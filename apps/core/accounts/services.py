"""Account authentication and role helpers (FUIP09, #85 FUSP07, #126 NFSP11)."""

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.core.api import APIError
from apps.core.models import Student, Teacher, UserAccount


ROLE_ALIASES = {
    "student": {"student", "دانشجو"},
    "professor": {"professor", "teacher", "advisor", "professor/advisor", "استاد", "مشاور"},
    "education_officer": {
        "education officer",
        "کارشناس آموزش",
        "کارمند آموزش",
        "مسئول آموزش",
    },
    "student_affairs_officer": {
        "student affairs officer",
        "student affairs",
        "کارشناس امور دانشجویی",
        "مسئول امور دانشجویی",
    },
    "scholarship_officer": {
        "scholarship officer",
        "کارشناس بورسیه",
        "مسئول بورسیه",
    },
    "admin": {"admin", "administrator", "مدیر", "مدیر سیستم", "مدیر سامانه"},
}


def _normalize_role(role_name):
    normalized = " ".join(
        role_name.strip().casefold().replace("_", " ").replace("-", " ").split()
    )
    for canonical, aliases in ROLE_ALIASES.items():
        if normalized == canonical.replace("_", " ") or normalized in aliases:
            return canonical
    return normalized.replace(" ", "_")


def _account_for_login(username):
    return (
        UserAccount.objects.select_for_update()
        .select_related("person")
        .filter(Q(username=username) | Q(person__username=username))
        .order_by("pk")
        .first()
    )


def authenticate_person(username, password, request=None):
    """Authenticate through Django's Person password hash, never UserAccount.password."""
    now = timezone.now()
    pending_error = None
    user = None

    with transaction.atomic():
        account = _account_for_login(username)

        if account and not account.is_active:
            pending_error = APIError("account_inactive", "This account is inactive.", 403)
        elif account and account.locked_until and account.locked_until > now:
            pending_error = APIError("account_locked", "Too many failed attempts.", 423)
        else:
            if account and account.locked_until:
                # A failure after the lock expires starts a fresh consecutive-failure window.
                account.failed_login_count = 0
                account.locked_until = None
                account.save(update_fields=["failed_login_count", "locked_until"])

            auth_username = account.person.username if account else username
            user = authenticate(request, username=auth_username, password=password)
            if user is not None and account is None and not user.is_superuser:
                # Non-admin API users need an active role account for lockout and RBAC.
                user = None

            if user is None or not user.is_active:
                if account:
                    account.failed_login_count += 1
                    threshold = getattr(settings, "AUTH_LOCKOUT_FAILURES", 5)
                    if account.failed_login_count >= threshold:
                        lock_seconds = getattr(settings, "AUTH_LOCKOUT_SECONDS", 900)
                        account.locked_until = now + timedelta(seconds=lock_seconds)
                        pending_error = APIError(
                            "account_locked", "Too many failed attempts.", 423
                        )
                    update_fields = ["failed_login_count"]
                    if account.locked_until:
                        update_fields.append("locked_until")
                    account.save(update_fields=update_fields)
                user = None
            elif account:
                account.failed_login_count = 0
                account.locked_until = None
                account.last_login_at = now
                account.last_activity_at = now
                account.save(
                    update_fields=[
                        "failed_login_count",
                        "locked_until",
                        "last_login_at",
                        "last_activity_at",
                    ]
                )

    # Raising outside atomic preserves the saved lockout state on the threshold attempt.
    if pending_error:
        raise pending_error
    return user


def role_codes_for(person):
    """Return canonical role codes attached to a Person."""
    if person.is_superuser:
        return {"admin"}

    codes = {
        _normalize_role(role_name)
        for role_name in UserAccount.objects.filter(
            person=person,
            is_active=True,
            role__is_active=True,
        ).values_list("role__role_name", flat=True)
    }
    if Student.objects.filter(person=person).exists():
        codes.add("student")
    if Teacher.objects.filter(person=person).exists():
        codes.add("professor")
    return codes


def user_has_any_role(person, roles):
    return bool(role_codes_for(person).intersection(roles))


def current_student(person, student_code=None):
    """Resolve only a Student record owned by the authenticated Person."""
    students = Student.objects.filter(person=person).select_related(
        "person", "field", "educational_level", "status"
    )
    if student_code:
        student = students.filter(student_code=student_code).first()
        if student is None:
            raise APIError("student_profile_not_found", "Student profile not found.", 404)
        return student

    records = list(students.order_by("student_code")[:2])
    if not records:
        raise APIError("student_profile_not_found", "Student profile not found.", 404)
    if len(records) > 1:
        raise APIError(
            "student_profile_ambiguous",
            "Provide the student_code for the profile to use.",
            400,
        )
    return records[0]

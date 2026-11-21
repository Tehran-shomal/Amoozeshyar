"""Account authentication and role helpers (FUIP09, #85 FUSP07, #126 NFSP11)."""

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone

from apps.core.api import APIError
from apps.core.models import Person, Student, Teacher, UserAccount


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


def _login_identity(username):
    """Resolve a Person username, role alias, or a student's student code.

    All aliases for one Person share the earliest active role account as their
    lockout record, so switching role aliases cannot reset consecutive failures.
    Person usernames take precedence when malformed legacy data collides across
    the two independently unique username columns.
    """
    username = username.strip()
    person = Person.objects.select_for_update().filter(username=username).first()
    identity_kind = "person" if person is not None else None
    if person is None:
        alias = UserAccount.objects.filter(username=username).only("person_id").first()
        if alias is not None:
            person = Person.objects.select_for_update().filter(pk=alias.person_id).first()
            identity_kind = "alias"

    if person is None:
        # The PDF asks for a student number. Normalize localized digits so
        # Persian and Arabic numerals resolve to the ASCII seeded code.
        digit_translation = str.maketrans(
            "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
            "01234567890123456789",
        )
        student_code = username.translate(digit_translation)
        student_person_id = (
            Student.objects.select_for_update()
            .filter(student_code=student_code)
            .values_list("person_id", flat=True)
            .first()
        )
        if student_person_id is not None:
            person = Person.objects.select_for_update().filter(pk=student_person_id).first()
            identity_kind = "student_code"

    if person is None:
        return None, None, None

    accounts = list(
        UserAccount.objects.select_for_update()
        .select_related("role")
        .filter(person=person)
        .order_by("pk")
    )
    selected_account = None
    if identity_kind == "alias":
        selected_account = next(
            (account for account in accounts if account.username == username), None
        )
    else:
        active_account = next(
            (
                account
                for account in accounts
                if account.is_active and account.role.is_active
            ),
            None,
        )
        # A superuser can authenticate as a Person even if legacy role rows
        # are inactive; exact inactive role aliases remain blocked above.
        selected_account = active_account or (
            accounts[0] if accounts and not person.is_superuser else None
        )

    lockout_account = next(
        (
            account
            for account in accounts
            if account.is_active and account.role.is_active
        ),
        None,
    )
    return person, selected_account, lockout_account


def authenticate_person(username, password, request=None):
    """Authenticate through Django's Person password hash, never UserAccount.password."""
    now = timezone.now()
    pending_error = None
    user = None

    with transaction.atomic():
        person, selected_account, lockout_account = _login_identity(username)
        person_lockout = (
            person
            if person is not None and person.is_superuser and lockout_account is None
            else None
        )
        locked_until = (
            lockout_account.locked_until
            if lockout_account is not None
            else person_lockout.locked_until if person_lockout is not None else None
        )

        if selected_account and (
            not selected_account.is_active or not selected_account.role.is_active
        ):
            pending_error = APIError("account_inactive", "This account is inactive.", 403)
        elif locked_until and locked_until > now:
            pending_error = APIError("account_locked", "Too many failed attempts.", 423)
        elif person and not person.is_superuser and lockout_account is None:
            user = None
        else:
            if lockout_account and lockout_account.locked_until:
                # A failure after the lock expires starts a fresh consecutive-failure window.
                lockout_account.failed_login_count = 0
                lockout_account.locked_until = None
                lockout_account.save(update_fields=["failed_login_count", "locked_until"])
            elif person_lockout and person_lockout.locked_until:
                person_lockout.failed_login_count = 0
                person_lockout.locked_until = None
                person_lockout.save(update_fields=["failed_login_count", "locked_until"])

            auth_username = person.username if person else username
            user = authenticate(request, username=auth_username, password=password)
            if user is not None and lockout_account is None and not user.is_superuser:
                # Non-admin API users need an active role account for lockout and RBAC.
                user = None

            if user is None or not user.is_active:
                if lockout_account:
                    lockout_account.failed_login_count += 1
                    threshold = getattr(settings, "AUTH_LOCKOUT_FAILURES", 5)
                    if lockout_account.failed_login_count >= threshold:
                        lock_seconds = getattr(settings, "AUTH_LOCKOUT_SECONDS", 900)
                        lockout_account.locked_until = now + timedelta(seconds=lock_seconds)
                        pending_error = APIError(
                            "account_locked", "Too many failed attempts.", 423
                        )
                    update_fields = ["failed_login_count"]
                    if lockout_account.locked_until:
                        update_fields.append("locked_until")
                    lockout_account.save(update_fields=update_fields)
                elif person_lockout:
                    person_lockout.failed_login_count += 1
                    threshold = getattr(settings, "AUTH_LOCKOUT_FAILURES", 5)
                    if person_lockout.failed_login_count >= threshold:
                        lock_seconds = getattr(settings, "AUTH_LOCKOUT_SECONDS", 900)
                        person_lockout.locked_until = now + timedelta(seconds=lock_seconds)
                        pending_error = APIError(
                            "account_locked", "Too many failed attempts.", 423
                        )
                    update_fields = ["failed_login_count"]
                    if person_lockout.locked_until:
                        update_fields.append("locked_until")
                    person_lockout.save(update_fields=update_fields)
                user = None
            elif lockout_account:
                lockout_account.failed_login_count = 0
                lockout_account.locked_until = None
                lockout_account.last_login_at = now
                lockout_account.last_activity_at = now
                lockout_account.save(
                    update_fields=[
                        "failed_login_count",
                        "locked_until",
                        "last_login_at",
                        "last_activity_at",
                    ]
                )
            elif person_lockout:
                person_lockout.failed_login_count = 0
                person_lockout.locked_until = None
                person_lockout.save(update_fields=["failed_login_count", "locked_until"])

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

"""Transactional course registration and drop rules (ADR-002/003, #132/#133)."""

from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone

from apps.core.api import APIError
from apps.core.models import Constant, CourseOffering, Enrollment, Grade, Prerequisite, Student


PASSING_GRADE = 10
INACTIVE_ENROLLMENT_CODES = ("dropped", "cancelled", "canceled")


class EnrollmentError(APIError):
    """A stable, client-readable enrollment-rule failure."""


def _active_enrollments(queryset):
    return queryset.filter(
        Q(status__isnull=True)
        | (
            ~Q(status__code__iexact="dropped")
            & ~Q(status__code__iexact="cancelled")
            & ~Q(status__code__iexact="canceled")
        )
    )


def _enrollment_status(code):
    status = Constant.objects.filter(
        category="enrollment_status", code__iexact=code
    ).order_by("pk").first()
    if status is None:
        raise EnrollmentError(
            "enrollment_status_unavailable",
            f"The {code} enrollment status has not been configured.",
            500,
        )
    return status


def _is_open(start, end, now):
    return start <= now <= end


def _has_passed_lesson(student, lesson):
    grades = Grade.objects.filter(
        enrollment__student=student,
        enrollment__offering__lesson=lesson,
        score__gte=PASSING_GRADE,
    )
    return grades.filter(
        Q(enrollment__status__isnull=True)
        | (
            ~Q(enrollment__status__code__iexact="dropped")
            & ~Q(enrollment__status__code__iexact="cancelled")
            & ~Q(enrollment__status__code__iexact="canceled")
        )
    ).exists()


def _validate_prerequisites(student, offering):
    relationships = Prerequisite.objects.filter(lesson=offering.lesson).select_related(
        "prerequisite_lesson", "prerequisite_type"
    )
    for relationship in relationships:
        relation_code = (
            relationship.prerequisite_type.code.casefold()
            if relationship.prerequisite_type
            else "prerequisite"
        )
        if relation_code in {"co_requisite", "corequisite", "co-requisite"}:
            enrolled_together = _active_enrollments(
                Enrollment.objects.filter(
                    student=student,
                    offering__term=offering.term,
                    offering__lesson=relationship.prerequisite_lesson,
                ).select_related("status")
            ).exists()
            if not enrolled_together and not _has_passed_lesson(
                student, relationship.prerequisite_lesson
            ):
                raise EnrollmentError(
                    "corequisite_not_met",
                    "Register for the co-requisite course in this term first.",
                )
        elif not _has_passed_lesson(student, relationship.prerequisite_lesson):
            raise EnrollmentError(
                "prerequisite_not_met",
                "A required prerequisite has not been passed.",
            )


def _validate_schedule(student, offering):
    current = _active_enrollments(
        Enrollment.objects.filter(
            student=student,
            offering__term=offering.term,
        ).exclude(offering=offering).select_related("status", "offering")
    )
    if offering.day_of_week_id is not None and current.filter(
        offering__day_of_week=offering.day_of_week,
        offering__start_time__lt=offering.end_time,
        offering__end_time__gt=offering.start_time,
    ).exists():
        raise EnrollmentError(
            "schedule_conflict", "The course overlaps another registered course."
        )

    if offering.exam_date and offering.exam_time:
        if current.filter(
            offering__exam_date=offering.exam_date,
            offering__exam_time=offering.exam_time,
        ).exists():
            raise EnrollmentError(
                "exam_conflict", "The course exam conflicts with another exam."
            )


def _validate_credit_limit(student, offering, current_term_enrollments):
    current_units = current_term_enrollments.aggregate(
        total=Sum("offering__lesson__theory_units")
        + Sum("offering__lesson__practical_units")
    )["total"] or 0
    requested_units = offering.lesson.theory_units + offering.lesson.practical_units
    if current_units + requested_units > student.max_allowed_units:
        raise EnrollmentError(
            "credit_limit_exceeded", "The course would exceed your allowed credit load."
        )


@transaction.atomic
def register_student(student, offering_id, now=None):
    """Register or reactivate one student in an offering after checking all rules."""
    now = now or timezone.now()
    try:
        offering = (
            CourseOffering.objects.select_for_update()
            .select_related("term", "lesson", "day_of_week")
            .get(pk=offering_id)
        )
        locked_student = Student.objects.select_for_update().get(pk=student.pk)
    except CourseOffering.DoesNotExist as error:
        raise EnrollmentError("offering_not_found", "Course offering not found.", 404) from error
    except Student.DoesNotExist as error:
        raise EnrollmentError("student_not_found", "Student record not found.", 404) from error

    existing = (
        Enrollment.objects.select_for_update()
        .filter(student=locked_student, offering=offering)
        .select_related("status")
        .first()
    )
    if existing and (
        existing.status is None
        or existing.status.code.casefold() not in INACTIVE_ENROLLMENT_CODES
    ):
        return existing

    if not offering.is_active:
        raise EnrollmentError("inactive_offering", "This course offering is inactive.")
    term = offering.term
    if not term.is_active:
        raise EnrollmentError("term_not_active", "This term is not active.")
    if not (
        _is_open(term.registration_start, term.registration_end, now)
        or _is_open(term.add_drop_start, term.add_drop_end, now)
    ):
        raise EnrollmentError(
            "registration_window_closed", "Registration is currently closed."
        )

    status_code = locked_student.status.code.casefold() if locked_student.status else None
    if status_code not in {None, "active"}:
        raise EnrollmentError("student_not_eligible", "The student is not active.")
    if locked_student.tuition_debt > 0:
        raise EnrollmentError("tuition_debt", "Outstanding tuition debt blocks registration.")

    _validate_prerequisites(locked_student, offering)

    current_term_enrollments = _active_enrollments(
        Enrollment.objects.filter(student=locked_student, offering__term=term)
        .exclude(offering=offering)
        .select_related("status", "offering__lesson")
    )
    _validate_schedule(locked_student, offering)
    _validate_credit_limit(locked_student, offering, current_term_enrollments)

    active_count = _active_enrollments(
        Enrollment.objects.filter(offering=offering).select_related("status")
    ).count()
    if active_count >= offering.capacity:
        raise EnrollmentError("offering_full", "This course offering has no available seats.")

    registered_status = _enrollment_status("registered")
    if existing:
        existing.status = registered_status
        existing.drop_date = None
        existing.save(update_fields=["status", "drop_date"])
        return existing
    return Enrollment.objects.create(
        student=locked_student,
        offering=offering,
        status=registered_status,
    )


@transaction.atomic
def drop_enrollment(student, enrollment_id, now=None):
    """Drop an owned enrollment during add/drop or emergency-drop windows."""
    now = now or timezone.now()
    try:
        enrollment = (
            Enrollment.objects.select_for_update()
            .select_related("status", "offering__term")
            .get(pk=enrollment_id)
        )
    except Enrollment.DoesNotExist as error:
        raise EnrollmentError("enrollment_not_found", "Enrollment not found.", 404) from error

    if enrollment.student_id != student.pk:
        raise EnrollmentError(
            "enrollment_not_owned", "This enrollment does not belong to the student.", 403
        )
    if enrollment.status and enrollment.status.code.casefold() in INACTIVE_ENROLLMENT_CODES:
        return enrollment

    term = enrollment.offering.term
    add_drop_open = _is_open(term.add_drop_start, term.add_drop_end, now)
    emergency_drop_open = _is_open(
        term.emergency_drop_start, term.emergency_drop_end, now
    )
    if not (add_drop_open or emergency_drop_open):
        raise EnrollmentError("drop_window_closed", "Course dropping is currently closed.")

    enrollment.status = _enrollment_status("dropped")
    enrollment.drop_date = timezone.localdate(now)
    enrollment.save(update_fields=["status", "drop_date"])
    return enrollment

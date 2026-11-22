from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time
from django.views.decorators.http import require_GET, require_POST

from apps.core.api import APIError, error_response, read_json
from apps.core.accounts.permissions import account_role_required
from apps.core.accounts.services import current_student, current_user_account
from apps.core.enrollment.services import active_enrollments
from apps.core.models import (
    Attendance,
    Constant,
    CourseOffering,
    Enrollment,
)


def _handle_error(error):
    return error_response(error.code, error.message, error.status_code)


def _attendance_payload(record):
    enrollment = record.enrollment
    offering = enrollment.offering

    return {
        "id": record.pk,
        "enrollment_id": enrollment.pk,
        "session_number": record.session_number,
        "session_date": record.session_date.isoformat(),
        "attendance_time": (
            record.attendance_time.isoformat()
            if record.attendance_time
            else None
        ),
        "status": (
            {
                "code": record.attendance_status.code,
                "label": record.attendance_status.label,
            }
            if record.attendance_status_id
            else None
        ),
        "description": record.description,
        "lesson": {
            "id": offering.lesson_id,
            "code": offering.lesson.lesson_code,
            "title": offering.lesson.title,
        },
        "student": {
            "id": enrollment.student_id,
            "student_code": enrollment.student.student_code,
            "full_name": enrollment.student.person.full_name,
        },
        "recorded_by": record.recorded_by_id,
        "created_at": record.created_at.isoformat(),
    }


def _owned_teacher_enrollment(request, enrollment_id):
    enrollment = (
        Enrollment.objects
        .select_related(
            "student__person",
            "offering__lesson",
            "offering__teacher__person",
            "status",
        )
        .filter(
            pk=enrollment_id,
            offering__teacher__person=request.user,
        )
        .first()
    )

    if enrollment is None:
        raise APIError(
            "enrollment_not_found",
            "Enrollment was not found for one of your course offerings.",
            404,
        )

    if not active_enrollments(
        Enrollment.objects.filter(pk=enrollment.pk)
    ).exists():
        raise APIError(
            "inactive_enrollment",
            "Attendance cannot be recorded for an inactive enrollment.",
        )

    return enrollment


@require_GET
@account_role_required("student")
def my_attendance_view(request):
    try:
        student = current_student(
            request.user,
            request.GET.get("student_code"),
        )

        records = (
            Attendance.objects
            .filter(enrollment__student=student)
            .select_related(
                "enrollment__student__person",
                "enrollment__offering__lesson",
                "attendance_status",
                "recorded_by",
            )
            .order_by(
                "-session_date",
                "-session_number",
            )[:300]
        )

        return JsonResponse({
            "count": len(records),
            "results": [_attendance_payload(item) for item in records],
        })

    except APIError as error:
        return _handle_error(error)


@require_GET
@account_role_required("professor")
def offering_attendance_view(request, offering_id):
    offering = (
        CourseOffering.objects
        .filter(
            pk=offering_id,
            teacher__person=request.user,
        )
        .select_related("lesson", "term")
        .first()
    )

    if offering is None:
        return error_response(
            "offering_not_found",
            "Course offering was not found.",
            404,
        )

    records = (
        Attendance.objects
        .filter(enrollment__offering=offering)
        .select_related(
            "enrollment__student__person",
            "enrollment__offering__lesson",
            "attendance_status",
            "recorded_by",
        )
        .order_by(
            "-session_date",
            "session_number",
            "enrollment__student__student_code",
        )[:500]
    )

    return JsonResponse({
        "offering_id": offering.pk,
        "lesson": offering.lesson.title,
        "count": len(records),
        "results": [_attendance_payload(item) for item in records],
    })


@require_POST
@account_role_required("professor")
def record_attendance_view(request, enrollment_id):
    try:
        payload = read_json(request)

        session_number = payload.get("session_number")

        if (
            isinstance(session_number, bool)
            or not isinstance(session_number, int)
            or session_number <= 0
        ):
            raise APIError(
                "invalid_session_number",
                "session_number must be a positive integer.",
            )

        raw_date = payload.get("session_date")
        if not isinstance(raw_date, str):
            raise APIError(
                "invalid_session_date",
                "session_date is required in YYYY-MM-DD format.",
            )

        session_date = parse_date(raw_date)
        if session_date is None:
            raise APIError(
                "invalid_session_date",
                "session_date must use YYYY-MM-DD format.",
            )

        raw_time = payload.get("attendance_time")
        if raw_time is None:
            attendance_time = timezone.localtime().time().replace(
                microsecond=0,
            )
        elif isinstance(raw_time, str):
            attendance_time = parse_time(raw_time)
            if attendance_time is None:
                raise APIError(
                    "invalid_attendance_time",
                    "attendance_time must use HH:MM or HH:MM:SS format.",
                )
        else:
            raise APIError(
                "invalid_attendance_time",
                "attendance_time must be a string.",
            )

        status_code = payload.get("attendance_status_code")
        if not isinstance(status_code, str) or not status_code.strip():
            raise APIError(
                "attendance_status_required",
                "attendance_status_code is required.",
            )

        attendance_status = Constant.objects.filter(
            category="attendance_status",
            code=status_code.strip(),
            is_active=True,
        ).first()

        if attendance_status is None:
            raise APIError(
                "invalid_attendance_status",
                "The requested attendance status is not active or does not exist.",
            )

        description = payload.get("description", "")
        if not isinstance(description, str):
            raise APIError(
                "invalid_description",
                "description must be a string.",
            )

        account = current_user_account(request)
        if account is None:
            raise APIError(
                "active_account_required",
                "An active user account is required.",
                403,
            )

        with transaction.atomic():
            enrollment = _owned_teacher_enrollment(
                request,
                enrollment_id,
            )

            # Serialize concurrent writes for the same enrollment/session.
            Enrollment.objects.select_for_update().get(
                pk=enrollment.pk,
            )

            record = (
                Attendance.objects
                .select_for_update()
                .filter(
                    enrollment=enrollment,
                    session_number=session_number,
                )
                .first()
            )

            created = record is None

            if created:
                record = Attendance(
                    enrollment=enrollment,
                    session_number=session_number,
                )

            record.session_date = session_date
            record.attendance_time = attendance_time
            record.attendance_status = attendance_status
            record.description = description.strip()
            record.recorded_by = account

            try:
                record.full_clean()
                record.save()
            except ValidationError as error:
                raise APIError(
                    "attendance_validation_error",
                    str(error),
                ) from error

            record = Attendance.objects.select_related(
                "enrollment__student__person",
                "enrollment__offering__lesson",
                "attendance_status",
                "recorded_by",
            ).get(pk=record.pk)

        return JsonResponse({
            "message": (
                "Attendance recorded successfully."
                if created
                else "Attendance updated successfully."
            ),
            "created": created,
            "attendance": _attendance_payload(record),
        }, status=201 if created else 200)

    except APIError as error:
        return _handle_error(error)
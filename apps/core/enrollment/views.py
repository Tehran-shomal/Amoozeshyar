"""Session-authenticated enrollment mutation endpoints."""

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.core.api import APIError, error_response
from apps.core.accounts.permissions import role_required
from apps.core.accounts.services import current_student
from apps.core.enrollment.services import drop_enrollment, register_student


def _enrollment_payload(enrollment):
    return {
        "id": enrollment.pk,
        "student_code": enrollment.student.student_code,
        "offering_id": enrollment.offering_id,
        "lesson_code": enrollment.offering.lesson.lesson_code,
        "lesson_title": enrollment.offering.lesson.title,
        "status": enrollment.status.code if enrollment.status else None,
        "enrollment_date": enrollment.enrollment_date.isoformat(),
        "drop_date": enrollment.drop_date.isoformat() if enrollment.drop_date else None,
    }


@require_POST
@role_required("student")
def register_view(request, offering_id):
    try:
        student = current_student(request.user)
        enrollment = register_student(student, offering_id)
    except APIError as error:
        return error_response(error.code, error.message, error.status_code)
    return JsonResponse({"enrollment": _enrollment_payload(enrollment)}, status=201)


@require_POST
@role_required("student")
def drop_view(request, enrollment_id):
    try:
        student = current_student(request.user)
        enrollment = drop_enrollment(student, enrollment_id)
    except APIError as error:
        return error_response(error.code, error.message, error.status_code)
    return JsonResponse({"enrollment": _enrollment_payload(enrollment)})

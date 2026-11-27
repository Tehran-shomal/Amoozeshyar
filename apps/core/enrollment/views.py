"""Session-authenticated enrollment mutation endpoints."""

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.core.api import APIError, error_response, read_json
from apps.core.accounts.permissions import role_required
from apps.core.accounts.services import current_student
from apps.core.enrollment.services import (
    drop_enrollment,
    register_student_with_outcome,
)


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


def _request_student(request):
    if not request.body:
        payload = {}
    elif request.content_type == "application/json":
        payload = read_json(request)
    elif request.content_type in {"application/x-www-form-urlencoded", "multipart/form-data"}:
        payload = request.POST.dict()
    else:
        raise APIError("invalid_json", "Request body must be valid JSON.")
    student_code = payload.get("student_code")
    if student_code is not None and (
        not isinstance(student_code, str) or not student_code.strip()
    ):
        raise APIError("invalid_student_code", "student_code must be a non-empty string.")
    return current_student(request.user, student_code.strip() if student_code else None)


@require_POST
@role_required("student")
def register_view(request, offering_id):
    try:
        student = _request_student(request)
        enrollment, created = register_student_with_outcome(student, offering_id)
    except APIError as error:
        return error_response(error.code, error.message, error.status_code)
    return JsonResponse(
        {"enrollment": _enrollment_payload(enrollment), "created": created},
        status=201 if created else 200,
    )


@require_POST
@role_required("student")
def drop_view(request, enrollment_id):
    try:
        student = _request_student(request)
        enrollment = drop_enrollment(student, enrollment_id, window="either")
    except APIError as error:
        return error_response(error.code, error.message, error.status_code)
    return JsonResponse({"enrollment": _enrollment_payload(enrollment)})


@require_POST
@role_required("student")
def emergency_drop_view(request, enrollment_id):
    try:
        student = _request_student(request)
        enrollment = drop_enrollment(student, enrollment_id, window="emergency-drop")
    except APIError as error:
        return error_response(error.code, error.message, error.status_code)
    return JsonResponse({"enrollment": _enrollment_payload(enrollment)})

from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.core.api import APIError, error_response, read_json
from apps.core.accounts.permissions import account_role_required
from apps.core.accounts.services import current_student
from apps.core.enrollment.services import active_enrollments
from apps.core.models import (
    Constant,
    Enrollment,
    Grade,
    GradeAppeal,
    TeacherSurvey,
)


def _handle_error(error):
    return error_response(error.code, error.message, error.status_code)





def _grade_payload(grade):
    enrollment = grade.enrollment
    offering = enrollment.offering

    return {
        "id": grade.pk,
        "score": str(grade.score) if grade.score is not None else None,
        "enrollment_id": enrollment.pk,
        "student": {
            "id": enrollment.student_id,
            "student_code": enrollment.student.student_code,
            "full_name": enrollment.student.person.full_name,
        },
        "lesson": {
            "id": offering.lesson_id,
            "code": offering.lesson.lesson_code,
            "title": offering.lesson.title,
        },
        "teacher": offering.teacher.person.full_name,
        "term_id": offering.term_id,
    }


def _appeal_payload(appeal):
    return {
        "id": appeal.pk,
        "enrollment_id": appeal.enrollment_id,
        "lesson": appeal.enrollment.offering.lesson.title,
        "reason": appeal.appeal_reason,
        "appeal_date": appeal.appeal_date.isoformat(),
        "status": (
            {
                "code": appeal.appeal_status.code,
                "label": appeal.appeal_status.label,
            }
            if appeal.appeal_status_id
            else None
        ),
    }


def _survey_payload(survey):
    return {
        "id": survey.pk,
        "enrollment_id": survey.enrollment_id,
        "overall_rating": survey.overall_rating,
        "teaching_quality": survey.teaching_quality,
        "behavior": survey.behavior,
        "comment": survey.comment,
        "submitted_at": survey.submitted_at.isoformat(),
    }


def _owned_teacher_enrollment(request, enrollment_id):
    enrollment = (
        Enrollment.objects
        .select_related(
            "student__person",
            "offering__lesson",
            "offering__teacher__person",
            "offering__term",
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
            "This enrollment is not active.",
            400,
        )

    return enrollment


def _owned_student_enrollment(request, enrollment_id, student_code=None):
    student = current_student(request.user, student_code)

    enrollment = (
        Enrollment.objects
        .select_related(
            "student",
            "offering__lesson",
            "offering__teacher__person",
            "offering__term",
            "status",
        )
        .filter(
            pk=enrollment_id,
            student=student,
        )
        .first()
    )

    if enrollment is None:
        raise APIError(
            "enrollment_not_found",
            "Enrollment was not found in your student record.",
            404,
        )

    if not active_enrollments(
        Enrollment.objects.filter(pk=enrollment.pk)
    ).exists():
        raise APIError(
            "inactive_enrollment",
            "This enrollment is not active.",
            400,
        )

    return enrollment


@require_GET
@account_role_required("student")
def my_grades_view(request):
    try:
        student = current_student(
            request.user,
            request.GET.get("student_code"),
        )

        grades = (
            Grade.objects
            .filter(enrollment__student=student)
            .select_related(
                "enrollment__student__person",
                "enrollment__offering__lesson",
                "enrollment__offering__teacher__person",
                "enrollment__offering__term",
            )
            .order_by(
                "-enrollment__offering__term_id",
                "enrollment__offering__lesson__lesson_code",
            )[:200]
        )

        return JsonResponse({
            "count": len(grades),
            "results": [_grade_payload(item) for item in grades],
        })

    except APIError as error:
        return _handle_error(error)


@require_GET
@account_role_required("professor")
def offering_grades_view(request, offering_id):
    from apps.core.models import CourseOffering

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

    enrollments = (
        active_enrollments(
            Enrollment.objects.filter(offering=offering)
        )
        .select_related("student__person")
        .order_by("student__student_code")[:200]
    )

    grade_map = {
        grade.enrollment_id: grade
        for grade in Grade.objects.filter(
            enrollment__in=enrollments
        )
    }

    results = []

    for enrollment in enrollments:
        grade = grade_map.get(enrollment.pk)

        results.append({
            "enrollment_id": enrollment.pk,
            "student": {
                "id": enrollment.student_id,
                "student_code": enrollment.student.student_code,
                "full_name": enrollment.student.person.full_name,
            },
            "grade": (
                _grade_payload(grade)
                if grade is not None
                else None
            ),
        })

    return JsonResponse({
        "offering_id": offering.pk,
        "lesson": offering.lesson.title,
        "count": len(results),
        "results": results,
    })


@require_http_methods(["PUT", "PATCH"])
@account_role_required("professor")
def set_grade_view(request, enrollment_id):
    try:
        payload = read_json(request)

        if "score" not in payload:
            raise APIError(
                "score_required",
                "The score field is required.",
            )

        raw_score = payload["score"]

        if isinstance(raw_score, bool):
            raise APIError("invalid_score", "Score must be a number.")

        try:
            score = Decimal(str(raw_score))
        except (InvalidOperation, TypeError, ValueError):
            raise APIError("invalid_score", "Score must be a valid number.")

        if not score.is_finite() or score < 0 or score > 20:
            raise APIError(
                "invalid_score",
                "Score must be between 0 and 20.",
            )

        with transaction.atomic():
            enrollment = _owned_teacher_enrollment(
                request,
                enrollment_id,
            )

            # Lock the enrollment to prevent concurrent duplicate grades.
            locked_enrollment = (
                Enrollment.objects
                .select_for_update()
                .get(pk=enrollment.pk)
            )

            grade = (
                Grade.objects
                .select_for_update()
                .filter(enrollment=locked_enrollment)
                .order_by("pk")
                .first()
            )

            if grade is None:
                grade = Grade(enrollment=locked_enrollment)

            grade.score = score.quantize(Decimal("0.01"))

            try:
                grade.full_clean()
                grade.save()
            except ValidationError as error:
                raise APIError(
                    "grade_validation_error",
                    str(error),
                ) from error

        return JsonResponse({
            "message": "Grade saved successfully.",
            "grade": _grade_payload(grade),
        })

    except APIError as error:
        return _handle_error(error)


@require_POST
@account_role_required("student")
def create_grade_appeal_view(request, enrollment_id):
    try:
        payload = read_json(request)
        reason = payload.get("appeal_reason")

        if not isinstance(reason, str) or not reason.strip():
            raise APIError(
                "appeal_reason_required",
                "A non-empty appeal_reason is required.",
            )

        with transaction.atomic():
            enrollment = _owned_student_enrollment(
                request,
                enrollment_id,
                payload.get("student_code"),
            )

            grade_exists = Grade.objects.filter(
                enrollment=enrollment,
                score__isnull=False,
            ).exists()

            if not grade_exists:
                raise APIError(
                    "grade_not_available",
                    "A grade must be published before submitting an appeal.",
                    400,
                )

            appeal_status = (
                Constant.objects.filter(
                    category="appeal_status",
                    code="submitted",
                    is_active=True,
                ).first()
                or Constant.objects.filter(
                    category="appeal_status",
                    code="pending",
                    is_active=True,
                ).first()
            )

            if appeal_status is None:
                raise APIError(
                    "appeal_status_unavailable",
                    "No active initial grade appeal status is configured.",
                    500,
                )

            appeal = GradeAppeal.objects.create(
                enrollment=enrollment,
                appeal_reason=reason.strip(),
                appeal_date=timezone.now(),
                appeal_status=appeal_status,
            )

            appeal = GradeAppeal.objects.select_related(
                "enrollment__offering__lesson",
                "appeal_status",
            ).get(pk=appeal.pk)

        return JsonResponse({
            "message": "Grade appeal submitted successfully.",
            "appeal": _appeal_payload(appeal),
        }, status=201)

    except APIError as error:
        return _handle_error(error)


@require_GET
@account_role_required("student")
def my_grade_appeals_view(request):
    try:
        student = current_student(
            request.user,
            request.GET.get("student_code"),
        )

        appeals = (
            GradeAppeal.objects
            .filter(enrollment__student=student)
            .select_related(
                "enrollment__offering__lesson",
                "appeal_status",
            )
            .order_by("-appeal_date")[:200]
        )

        return JsonResponse({
            "count": len(appeals),
            "results": [_appeal_payload(item) for item in appeals],
        })

    except APIError as error:
        return _handle_error(error)


@require_POST
@account_role_required("student")
def create_teacher_survey_view(request, enrollment_id):
    try:
        payload = read_json(request)

        def rating_value(field, required=False):
            value = payload.get(field)

            if value is None and not required:
                return None

            if isinstance(value, bool):
                raise APIError(
                    "invalid_rating",
                    f"{field} must be an integer between 1 and 5.",
                )

            try:
                parsed = int(value)
            except (TypeError, ValueError):
                raise APIError(
                    "invalid_rating",
                    f"{field} must be an integer between 1 and 5.",
                )

            if str(parsed) != str(value).strip() or not 1 <= parsed <= 5:
                raise APIError(
                    "invalid_rating",
                    f"{field} must be an integer between 1 and 5.",
                )

            return parsed

        overall_rating = rating_value("overall_rating", required=True)
        teaching_quality = rating_value("teaching_quality")
        behavior = rating_value("behavior")

        comment = payload.get("comment", "")
        if not isinstance(comment, str):
            raise APIError(
                "invalid_comment",
                "Comment must be a string.",
            )

        with transaction.atomic():
            enrollment = _owned_student_enrollment(
                request,
                enrollment_id,
                payload.get("student_code"),
            )

            # Lock the enrollment before checking for an existing survey.
            locked_enrollment = Enrollment.objects.select_for_update().get(
                pk=enrollment.pk,
            )

            if TeacherSurvey.objects.filter(
                enrollment=locked_enrollment,
            ).exists():
                raise APIError(
                    "survey_already_submitted",
                    "A survey has already been submitted for this course.",
                    409,
                )

            survey = TeacherSurvey(
                enrollment=locked_enrollment,
                overall_rating=overall_rating,
                teaching_quality=teaching_quality,
                behavior=behavior,
                comment=comment.strip(),
            )

            try:
                survey.full_clean()
                survey.save()
            except ValidationError as error:
                raise APIError(
                    "survey_validation_error",
                    str(error),
                ) from error

        return JsonResponse({
            "message": "Teacher survey submitted successfully.",
            "survey": _survey_payload(survey),
        }, status=201)

    except APIError as error:
        return _handle_error(error)


@require_GET
@account_role_required("student")
def my_teacher_surveys_view(request):
    try:
        student = current_student(
            request.user,
            request.GET.get("student_code"),
        )

        surveys = (
            TeacherSurvey.objects
            .filter(enrollment__student=student)
            .select_related("enrollment__offering__lesson")
            .order_by("-submitted_at")[:200]
        )

        return JsonResponse({
            "count": len(surveys),
            "results": [_survey_payload(item) for item in surveys],
        })

    except APIError as error:
        return _handle_error(error)
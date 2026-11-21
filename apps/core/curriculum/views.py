"""Role-aware JSON API views for curriculum management."""

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from apps.core.api import APIError, error_response, read_json
from apps.core.system_settings.reader import get_pagination_settings
from apps.core.accounts.permissions import role_required
from apps.core.models import Curriculum, Field, Lesson, Constant
from apps.core.curriculum.services import (
    curriculum_queryset_for_user,
    curriculum_payload,
)


def _integer_value(value, name, minimum=None):
    if isinstance(value, bool):
        raise APIError("invalid_field", f"{name} must be an integer.")

    try:
        result = int(value)
    except (TypeError, ValueError):
        raise APIError("invalid_field", f"{name} must be an integer.")

    if isinstance(value, float) and not value.is_integer():
        raise APIError("invalid_field", f"{name} must be an integer.")

    if isinstance(value, str) and str(result) != value.strip():
        raise APIError("invalid_field", f"{name} must be an integer.")

    if minimum is not None and result < minimum:
        raise APIError(
            "invalid_field",
            f"{name} must be greater than or equal to {minimum}.",
        )

    return result


def _boolean_value(value, name):
    if not isinstance(value, bool):
        raise APIError("invalid_field", f"{name} must be a boolean.")
    return value


def _validated_values(payload, instance=None, partial=False):
    allowed_fields = {
        "field_id",
        "lesson_id",
        "requirement_type_id",
        "recommended_term",
        "calculated_units",
        "is_active",
    }

    unknown_fields = set(payload) - allowed_fields
    if unknown_fields:
        raise APIError(
            "unknown_fields",
            f"Unknown fields: {', '.join(sorted(unknown_fields))}.",
        )

    values = {}

    required_fields = (
        "field_id",
        "lesson_id",
        "recommended_term",
        "calculated_units",
    )

    for name in required_fields:
        if not partial and name not in payload:
            raise APIError("missing_field", f"{name} is required.")

    if "field_id" in payload:
        field_id = _integer_value(payload["field_id"], "field_id", 1)
        field = Field.objects.filter(pk=field_id, is_active=True).first()

        if field is None:
            raise APIError("field_not_found", "Active field not found.", 404)

        values["field"] = field
    elif instance is not None:
        values["field"] = instance.field

    if "lesson_id" in payload:
        lesson_id = _integer_value(payload["lesson_id"], "lesson_id", 1)
        lesson = Lesson.objects.filter(pk=lesson_id, is_active=True).first()

        if lesson is None:
            raise APIError("lesson_not_found", "Active lesson not found.", 404)

        values["lesson"] = lesson
    elif instance is not None:
        values["lesson"] = instance.lesson

    if "requirement_type_id" in payload:
        raw_value = payload["requirement_type_id"]

        if raw_value is None:
            values["requirement_type"] = None
        else:
            constant_id = _integer_value(
                raw_value, "requirement_type_id", 1
            )
            requirement_type = Constant.objects.filter(
                pk=constant_id,
                category="requirement_type",
                is_active=True,
            ).first()

            if requirement_type is None:
                raise APIError(
                    "requirement_type_not_found",
                    "Active requirement type not found.",
                    404,
                )

            values["requirement_type"] = requirement_type

    elif instance is not None:
        values["requirement_type"] = instance.requirement_type
    else:
        values["requirement_type"] = None

    if "recommended_term" in payload:
        values["recommended_term"] = _integer_value(
            payload["recommended_term"], "recommended_term", 1
        )
    elif instance is not None:
        values["recommended_term"] = instance.recommended_term

    if "calculated_units" in payload:
        values["calculated_units"] = _integer_value(
            payload["calculated_units"], "calculated_units", 0
        )
    elif instance is not None:
        values["calculated_units"] = instance.calculated_units

    if "is_active" in payload:
        values["is_active"] = _boolean_value(
            payload["is_active"], "is_active"
        )
    elif instance is not None:
        values["is_active"] = instance.is_active
    else:
        values["is_active"] = True

    return values


def _save_curriculum(payload, instance=None, partial=False):
    values = _validated_values(
        payload,
        instance=instance,
        partial=partial,
    )

    try:
        with transaction.atomic():
            if instance is None:
                curriculum = Curriculum.objects.create(**values)
            else:
                for field, value in values.items():
                    setattr(instance, field, value)

                instance.save()
                curriculum = instance

    except IntegrityError as error:
        raise APIError(
            "duplicate_curriculum",
            "A curriculum record for this field and lesson already exists.",
            409,
        ) from error

    return curriculum


@require_GET
@role_required("student", "professor", "admin")
def curriculum_list_view(request):
    """List curriculum records accessible to the authenticated user."""

    try:
        queryset = curriculum_queryset_for_user(request.user)

        field_id = request.GET.get("field_id")
        department_id = request.GET.get("department_id")
        recommended_term = request.GET.get("recommended_term")
        active_value = request.GET.get("is_active")
        search = request.GET.get("search", "").strip()

        if field_id:
            queryset = queryset.filter(
                field_id=_integer_value(field_id, "field_id", 1)
            )

        if department_id:
            queryset = queryset.filter(
                field__department_id=_integer_value(
                    department_id, "department_id", 1
                )
            )

        if recommended_term:
            queryset = queryset.filter(
                recommended_term=_integer_value(
                    recommended_term, "recommended_term", 1
                )
            )

        if active_value is not None:
            if active_value.lower() not in ("true", "false"):
                raise APIError(
                    "invalid_is_active",
                    "is_active must be true or false.",
                )

            queryset = queryset.filter(
                is_active=(active_value.lower() == "true")
            )

        if search:
            queryset = queryset.filter(
                Q(lesson__title__icontains=search)
                | Q(lesson__lesson_code__icontains=search)
                | Q(field__field_name__icontains=search)
                | Q(field__field_code__icontains=search)
            )

        default_page_size, max_page_size = get_pagination_settings()

        page = _integer_value(request.GET.get("page", "1"), "page", 1)
        page_size = _integer_value(
            request.GET.get(
                "page_size",
                str(default_page_size),
            ),
            "page_size",
            1,
        )

        if page_size > max_page_size:
            raise APIError(
                "invalid_page_size",
                f"page_size cannot exceed {max_page_size}.",
            )

        total = queryset.count()
        start = (page - 1) * page_size
        records = queryset[start:start + page_size]

        return JsonResponse({
            "count": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "curriculums": [
                curriculum_payload(record)
                for record in records
            ],
        })

    except APIError as error:
        return error_response(
            error.code,
            error.message,
            error.status_code,
        )


@require_POST
@role_required("admin")
def curriculum_create_view(request):
    """Create a curriculum record. Admin only."""

    try:
        payload = read_json(request)
        curriculum = _save_curriculum(payload)

        return JsonResponse(
            {"curriculum": curriculum_payload(curriculum)},
            status=201,
        )

    except APIError as error:
        return error_response(
            error.code,
            error.message,
            error.status_code,
        )


@require_GET
@role_required("student", "professor", "admin")
def curriculum_detail_view(request, curriculum_id):
    """Return one accessible curriculum record."""

    curriculum = curriculum_queryset_for_user(request.user).filter(
        curriculum_id=curriculum_id
    ).first()

    if curriculum is None:
        return error_response(
            "curriculum_not_found",
            "Curriculum not found.",
            404,
        )

    return JsonResponse({
        "curriculum": curriculum_payload(curriculum)
    })


@require_http_methods(["PUT", "PATCH"])
@role_required("admin")
def curriculum_update_view(request, curriculum_id):
    """Update a curriculum record. Admin only."""

    instance = Curriculum.objects.filter(
        curriculum_id=curriculum_id
    ).first()

    if instance is None:
        return error_response(
            "curriculum_not_found",
            "Curriculum not found.",
            404,
        )

    try:
        payload = read_json(request)
        partial = request.method == "PATCH"

        curriculum = _save_curriculum(
            payload,
            instance=instance,
            partial=partial,
        )

        return JsonResponse({
            "curriculum": curriculum_payload(curriculum)
        })

    except APIError as error:
        return error_response(
            error.code,
            error.message,
            error.status_code,
        )


def _set_curriculum_status(curriculum_id, is_active):
    instance = Curriculum.objects.filter(
        curriculum_id=curriculum_id
    ).first()

    if instance is None:
        return None

    if instance.is_active != is_active:
        instance.is_active = is_active
        instance.save(update_fields=["is_active"])

    return instance


@require_POST
@role_required("admin")
def curriculum_activate_view(request, curriculum_id):
    """Activate a curriculum record. Admin only."""

    curriculum = _set_curriculum_status(curriculum_id, True)

    if curriculum is None:
        return error_response(
            "curriculum_not_found",
            "Curriculum not found.",
            404,
        )

    return JsonResponse({
        "message": "Curriculum activated successfully.",
        "curriculum": curriculum_payload(
            curriculum_queryset_for_user(request.user).get(
                curriculum_id=curriculum_id
            )
        ),
    })


@require_POST
@role_required("admin")
def curriculum_deactivate_view(request, curriculum_id):
    """Deactivate a curriculum record. Admin only."""

    curriculum = _set_curriculum_status(curriculum_id, False)

    if curriculum is None:
        return error_response(
            "curriculum_not_found",
            "Curriculum not found.",
            404,
        )

    return JsonResponse({
        "message": "Curriculum deactivated successfully.",
        "curriculum": curriculum_payload(
            curriculum_queryset_for_user(request.user).get(
                curriculum_id=curriculum_id
            )
        ),
    })

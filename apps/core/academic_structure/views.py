"""JSON API views for academic structure management."""

from functools import wraps

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from apps.core.api import APIError, error_response, read_json
from apps.core.system_settings.reader import get_pagination_settings
from apps.core.academic_structure.services import (
    resolve_academic_structure_access,
    academic_faculty_queryset,
    academic_department_queryset,
    academic_field_queryset,
    academic_lesson_queryset,
    academic_prerequisite_queryset,
)
from apps.core.models import (
    Faculty,
    Department,
    Field,
    Lesson,
    Prerequisite,
    Constant,
)


# =========================================================
# Shared helpers
# =========================================================

def academic_access_required(write=False):
    """
    Resolve the exact session role and access scope before executing a view.
    """

    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            try:
                request.academic_access = resolve_academic_structure_access(
                    request,
                    write=write,
                )
                return view(request, *args, **kwargs)

            except APIError as error:
                return error_response(
                    error.code,
                    error.message,
                    error.status_code,
                )

        return wrapped

    return decorator


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


def _required_string(payload, name, max_length, partial=False, instance=None):
    if name not in payload:
        if partial:
            return getattr(instance, name)
        raise APIError("missing_field", f"{name} is required.")

    value = payload[name]

    if not isinstance(value, str) or not value.strip():
        raise APIError("invalid_field", f"{name} must be a non-empty string.")

    value = value.strip()

    if len(value) > max_length:
        raise APIError(
            "invalid_field",
            f"{name} cannot exceed {max_length} characters.",
        )

    return value


def _active_value(payload, instance=None):
    if "is_active" in payload:
        return _boolean_value(payload["is_active"], "is_active")

    if instance is not None:
        return instance.is_active

    return True


def _pagination(request, queryset, key):
    default_page_size, max_page_size = get_pagination_settings()

    page = _integer_value(
        request.GET.get("page", "1"),
        "page",
        1,
    )

    page_size = _integer_value(
        request.GET.get("page_size", str(default_page_size)),
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

    return {
        "count": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "records": queryset[start:start + page_size],
    }


def _apply_common_filters(request, queryset, search_fields):
    search = request.GET.get("search", "").strip()

    if search:
        search_filter = Q()

        for field_name in search_fields:
            search_filter |= Q(**{f"{field_name}__icontains": search})

        queryset = queryset.filter(search_filter)

    active_value = request.GET.get("is_active")

    if active_value is not None:
        normalized = active_value.lower()

        if normalized not in {"true", "false"}:
            raise APIError(
                "invalid_is_active",
                "is_active must be true or false.",
            )

        queryset = queryset.filter(
            is_active=(normalized == "true")
        )

    return queryset


def _save_instance(model, values, instance=None):
    try:
        with transaction.atomic():
            if instance is None:
                return model.objects.create(**values)

            for field_name, value in values.items():
                setattr(instance, field_name, value)

            instance.save()
            return instance

    except IntegrityError as error:
        raise APIError(
            "duplicate_record",
            "A record with the same unique code or values already exists.",
            409,
        ) from error


def _set_status(queryset, object_id, is_active):
    instance = queryset.filter(pk=object_id).first()

    if instance is None:
        return None

    if instance.is_active != is_active:
        instance.is_active = is_active
        instance.save(update_fields=["is_active"])

    return instance


def _status_response(queryset, object_id, is_active, payload_function, label):
    instance = _set_status(queryset, object_id, is_active)

    if instance is None:
        return error_response(
            "record_not_found",
            f"{label} not found.",
            404,
        )

    return JsonResponse({
        "message": (
            f"{label} activated successfully."
            if is_active
            else f"{label} deactivated successfully."
        ),
        "record": payload_function(instance),
    })


# =========================================================
# Serializers
# =========================================================

def faculty_payload(faculty):
    return {
        "id": faculty.pk,
        "faculty_name": faculty.faculty_name,
        "faculty_code": faculty.faculty_code,
        "is_active": faculty.is_active,
        "created_at": faculty.created_at.isoformat(),
    }


def department_payload(department):
    return {
        "id": department.pk,
        "department_name": department.department_name,
        "department_code": department.department_code,
        "faculty": {
            "id": department.faculty_id,
            "name": department.faculty.faculty_name,
            "code": department.faculty.faculty_code,
        },
        "is_active": department.is_active,
        "created_at": department.created_at.isoformat(),
    }


def field_payload(field):
    department = field.department
    faculty = department.faculty

    return {
        "id": field.pk,
        "field_name": field.field_name,
        "field_code": field.field_code,
        "department": {
            "id": department.pk,
            "name": department.department_name,
            "code": department.department_code,
        },
        "faculty": {
            "id": faculty.pk,
            "name": faculty.faculty_name,
            "code": faculty.faculty_code,
        },
        "is_active": field.is_active,
        "created_at": field.created_at.isoformat(),
    }

def lesson_payload(lesson):
    department = lesson.department
    faculty = department.faculty

    return {
        "id": lesson.pk,
        "lesson_code": lesson.lesson_code,
        "title": lesson.title,
        "practical_units": lesson.practical_units,
        "theory_units": lesson.theory_units,
        "total_units": (
            lesson.practical_units + lesson.theory_units
        ),
        "lesson_type": (
            {
                "id": lesson.lesson_type_id,
                "code": lesson.lesson_type.code,
                "label": lesson.lesson_type.label,
            }
            if lesson.lesson_type_id
            else None
        ),
        "department": {
            "id": department.pk,
            "name": department.department_name,
            "code": department.department_code,
        },
        "faculty": {
            "id": faculty.pk,
            "name": faculty.faculty_name,
            "code": faculty.faculty_code,
        },
        "is_active": lesson.is_active,
        "created_at": lesson.created_at.isoformat(),
    }


def prerequisite_payload(prerequisite):
    lesson = prerequisite.lesson
    prerequisite_lesson = prerequisite.prerequisite_lesson

    return {
        "id": prerequisite.prereq_id,
        "lesson": {
            "id": lesson.pk,
            "lesson_code": lesson.lesson_code,
            "title": lesson.title,
        },
        "prerequisite_lesson": {
            "id": prerequisite_lesson.pk,
            "lesson_code": prerequisite_lesson.lesson_code,
            "title": prerequisite_lesson.title,
        },
        "prerequisite_type": (
            {
                "id": prerequisite.prerequisite_type_id,
                "code": prerequisite.prerequisite_type.code,
                "label": prerequisite.prerequisite_type.label,
            }
            if prerequisite.prerequisite_type_id
            else None
        ),
        "created_at": prerequisite.created_at.isoformat(),
    }
# =========================================================
# Faculty API
# =========================================================

@require_GET
@academic_access_required()
def faculty_list_view(request):
    try:
        queryset = academic_faculty_queryset(
            request,
            request.academic_access,
        )

        if request.academic_access["role"] in {"student", "professor"}:
            queryset = queryset.filter(is_active=True)

        queryset = _apply_common_filters(
            request,
            queryset,
            ["faculty_name", "faculty_code"],
        ).order_by("faculty_name")

        result = _pagination(request, queryset, "faculties")

        return JsonResponse({
            "count": result["count"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"],
            "faculties": [
                faculty_payload(item)
                for item in result["records"]
            ],
        })

    except APIError as error:
        return error_response(error.code, error.message, error.status_code)


@require_POST
@academic_access_required(write=True)
def faculty_create_view(request):
    try:
        if request.academic_access["role"] != "admin":
            raise APIError(
                "permission_denied",
                "Only administrators can create faculties.",
                403,
            )

        payload = read_json(request)

        allowed_fields = {"faculty_name", "faculty_code", "is_active"}
        unknown = set(payload) - allowed_fields

        if unknown:
            raise APIError(
                "unknown_fields",
                f"Unknown fields: {', '.join(sorted(unknown))}.",
            )

        values = {
            "faculty_name": _required_string(
                payload, "faculty_name", 150
            ),
            "faculty_code": _required_string(
                payload, "faculty_code", 20
            ),
            "is_active": _active_value(payload),
        }

        faculty = _save_instance(Faculty, values)

        return JsonResponse(
            {"faculty": faculty_payload(faculty)},
            status=201,
        )

    except APIError as error:
        return error_response(error.code, error.message, error.status_code)


@require_GET
@academic_access_required()
def faculty_detail_view(request, faculty_id):
    faculty = academic_faculty_queryset(
        request,
        request.academic_access,
    ).filter(pk=faculty_id).first()

    if faculty is None or (
        request.academic_access["role"] in {"student", "professor"}
        and not faculty.is_active
    ):
        return error_response("faculty_not_found", "Faculty not found.", 404)

    return JsonResponse({"faculty": faculty_payload(faculty)})


@require_http_methods(["PUT", "PATCH"])
@academic_access_required(write=True)
def faculty_update_view(request, faculty_id):
    try:
        role = request.academic_access["role"]

        if role not in {"admin", "faculty_manager"}:
            raise APIError("permission_denied", "Permission denied.", 403)

        instance = academic_faculty_queryset(
            request,
            request.academic_access,
        ).filter(pk=faculty_id).first()

        if instance is None:
            return error_response(
                "faculty_not_found",
                "Faculty not found.",
                404,
            )

        payload = read_json(request)
        partial = request.method == "PATCH"

        allowed_fields = {"faculty_name", "faculty_code", "is_active"}
        unknown = set(payload) - allowed_fields

        if unknown:
            raise APIError(
                "unknown_fields",
                f"Unknown fields: {', '.join(sorted(unknown))}.",
            )

        values = {
            "faculty_name": _required_string(
                payload, "faculty_name", 150, partial, instance
            ),
            "faculty_code": _required_string(
                payload, "faculty_code", 20, partial, instance
            ),
            "is_active": _active_value(payload, instance),
        }

        faculty = _save_instance(Faculty, values, instance)

        return JsonResponse({"faculty": faculty_payload(faculty)})

    except APIError as error:
        return error_response(error.code, error.message, error.status_code)


@require_POST
@academic_access_required(write=True)
def faculty_activate_view(request, faculty_id):
    role = request.academic_access["role"]

    if role not in {"admin", "faculty_manager"}:
        return error_response("permission_denied", "Permission denied.", 403)

    return _status_response(
        academic_faculty_queryset(request, request.academic_access),
        faculty_id,
        True,
        faculty_payload,
        "Faculty",
    )


@require_POST
@academic_access_required(write=True)
def faculty_deactivate_view(request, faculty_id):
    role = request.academic_access["role"]

    if role not in {"admin", "faculty_manager"}:
        return error_response("permission_denied", "Permission denied.", 403)

    return _status_response(
        academic_faculty_queryset(request, request.academic_access),
        faculty_id,
        False,
        faculty_payload,
        "Faculty",
    )


# =========================================================
# Department API
# =========================================================

@require_GET
@academic_access_required()
def department_list_view(request):
    try:
        queryset = academic_department_queryset(
            request,
            request.academic_access,
        )

        if request.academic_access["role"] in {"student", "professor"}:
            queryset = queryset.filter(is_active=True)

        faculty_id = request.GET.get("faculty_id")

        if faculty_id:
            queryset = queryset.filter(
                faculty_id=_integer_value(faculty_id, "faculty_id", 1)
            )

        queryset = _apply_common_filters(
            request,
            queryset,
            ["department_name", "department_code", "faculty__faculty_name"],
        ).order_by("department_name")

        result = _pagination(request, queryset, "departments")

        return JsonResponse({
            "count": result["count"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"],
            "departments": [
                department_payload(item)
                for item in result["records"]
            ],
        })

    except APIError as error:
        return error_response(error.code, error.message, error.status_code)


@require_POST
@academic_access_required(write=True)
def department_create_view(request):
    try:
        role = request.academic_access["role"]

        if role not in {"admin", "faculty_manager"}:
            raise APIError("permission_denied", "Permission denied.", 403)

        payload = read_json(request)

        allowed_fields = {
            "faculty_id",
            "department_name",
            "department_code",
            "is_active",
        }

        unknown = set(payload) - allowed_fields

        if unknown:
            raise APIError(
                "unknown_fields",
                f"Unknown fields: {', '.join(sorted(unknown))}.",
            )

        faculty_id = _integer_value(
            payload.get("faculty_id"),
            "faculty_id",
            1,
        )

        faculty = academic_faculty_queryset(
            request,
            request.academic_access,
        ).filter(pk=faculty_id, is_active=True).first()

        if faculty is None:
            raise APIError(
                "faculty_not_found",
                "Active faculty not found in your accessible scope.",
                404,
            )

        values = {
            "faculty": faculty,
            "department_name": _required_string(
                payload, "department_name", 150
            ),
            "department_code": _required_string(
                payload, "department_code", 20
            ),
            "is_active": _active_value(payload),
        }

        department = _save_instance(Department, values)

        return JsonResponse(
            {"department": department_payload(department)},
            status=201,
        )

    except APIError as error:
        return error_response(error.code, error.message, error.status_code)


@require_GET
@academic_access_required()
def department_detail_view(request, department_id):
    department = academic_department_queryset(
        request,
        request.academic_access,
    ).filter(pk=department_id).first()

    if department is None or (
        request.academic_access["role"] in {"student", "professor"}
        and not department.is_active
    ):
        return error_response(
            "department_not_found",
            "Department not found.",
            404,
        )

    return JsonResponse({"department": department_payload(department)})


@require_http_methods(["PUT", "PATCH"])
@academic_access_required(write=True)
def department_update_view(request, department_id):
    try:
        role = request.academic_access["role"]

        if role not in {"admin", "faculty_manager"}:
            raise APIError("permission_denied", "Permission denied.", 403)

        instance = academic_department_queryset(
            request,
            request.academic_access,
        ).filter(pk=department_id).first()

        if instance is None:
            return error_response(
                "department_not_found",
                "Department not found.",
                404,
            )

        payload = read_json(request)
        partial = request.method == "PATCH"

        allowed_fields = {
            "faculty_id",
            "department_name",
            "department_code",
            "is_active",
        }

        unknown = set(payload) - allowed_fields

        if unknown:
            raise APIError(
                "unknown_fields",
                f"Unknown fields: {', '.join(sorted(unknown))}.",
            )

        faculty = instance.faculty

        if "faculty_id" in payload:
            faculty_id = _integer_value(
                payload["faculty_id"],
                "faculty_id",
                1,
            )

            faculty = academic_faculty_queryset(
                request,
                request.academic_access,
            ).filter(pk=faculty_id, is_active=True).first()

            if faculty is None:
                raise APIError(
                    "faculty_not_found",
                    "Active faculty not found in your accessible scope.",
                    404,
                )

        values = {
            "faculty": faculty,
            "department_name": _required_string(
                payload, "department_name", 150, partial, instance
            ),
            "department_code": _required_string(
                payload, "department_code", 20, partial, instance
            ),
            "is_active": _active_value(payload, instance),
        }

        department = _save_instance(Department, values, instance)

        return JsonResponse({"department": department_payload(department)})

    except APIError as error:
        return error_response(error.code, error.message, error.status_code)


@require_POST
@academic_access_required(write=True)
def department_activate_view(request, department_id):
    role = request.academic_access["role"]

    if role not in {"admin", "faculty_manager"}:
        return error_response("permission_denied", "Permission denied.", 403)

    return _status_response(
        academic_department_queryset(request, request.academic_access),
        department_id,
        True,
        department_payload,
        "Department",
    )


@require_POST
@academic_access_required(write=True)
def department_deactivate_view(request, department_id):
    role = request.academic_access["role"]

    if role not in {"admin", "faculty_manager"}:
        return error_response("permission_denied", "Permission denied.", 403)

    return _status_response(
        academic_department_queryset(request, request.academic_access),
        department_id,
        False,
        department_payload,
        "Department",
    )


# =========================================================
# Field API
# =========================================================

@require_GET
@academic_access_required()
def field_list_view(request):
    try:
        queryset = academic_field_queryset(
            request,
            request.academic_access,
        )

        if request.academic_access["role"] in {"student", "professor"}:
            queryset = queryset.filter(is_active=True)

        department_id = request.GET.get("department_id")
        faculty_id = request.GET.get("faculty_id")

        if department_id:
            queryset = queryset.filter(
                department_id=_integer_value(
                    department_id, "department_id", 1
                )
            )

        if faculty_id:
            queryset = queryset.filter(
                department__faculty_id=_integer_value(
                    faculty_id, "faculty_id", 1
                )
            )

        queryset = _apply_common_filters(
            request,
            queryset,
            [
                "field_name",
                "field_code",
                "department__department_name",
                "department__faculty__faculty_name",
            ],
        ).order_by("field_name")

        result = _pagination(request, queryset, "fields")

        return JsonResponse({
            "count": result["count"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"],
            "fields": [
                field_payload(item)
                for item in result["records"]
            ],
        })

    except APIError as error:
        return error_response(error.code, error.message, error.status_code)


@require_POST
@academic_access_required(write=True)
def field_create_view(request):
    try:
        role = request.academic_access["role"]

        if role not in {"admin", "faculty_manager", "department_manager"}:
            raise APIError("permission_denied", "Permission denied.", 403)

        payload = read_json(request)

        allowed_fields = {
            "department_id",
            "field_name",
            "field_code",
            "is_active",
        }

        unknown = set(payload) - allowed_fields

        if unknown:
            raise APIError(
                "unknown_fields",
                f"Unknown fields: {', '.join(sorted(unknown))}.",
            )

        department_id = _integer_value(
            payload.get("department_id"),
            "department_id",
            1,
        )

        department = academic_department_queryset(
            request,
            request.academic_access,
        ).filter(pk=department_id, is_active=True).first()

        if department is None:
            raise APIError(
                "department_not_found",
                "Active department not found in your accessible scope.",
                404,
            )

        values = {
            "department": department,
            "field_name": _required_string(
                payload, "field_name", 150
            ),
            "field_code": _required_string(
                payload, "field_code", 20
            ),
            "is_active": _active_value(payload),
        }

        field = _save_instance(Field, values)

        return JsonResponse(
            {"field": field_payload(field)},
            status=201,
        )

    except APIError as error:
        return error_response(error.code, error.message, error.status_code)


@require_GET
@academic_access_required()
def field_detail_view(request, field_id):
    field = academic_field_queryset(
        request,
        request.academic_access,
    ).filter(pk=field_id).first()

    if field is None or (
        request.academic_access["role"] in {"student", "professor"}
        and not field.is_active
    ):
        return error_response("field_not_found", "Field not found.", 404)

    return JsonResponse({"field": field_payload(field)})


@require_http_methods(["PUT", "PATCH"])
@academic_access_required(write=True)
def field_update_view(request, field_id):
    try:
        role = request.academic_access["role"]

        if role not in {"admin", "faculty_manager", "department_manager"}:
            raise APIError("permission_denied", "Permission denied.", 403)

        instance = academic_field_queryset(
            request,
            request.academic_access,
        ).filter(pk=field_id).first()

        if instance is None:
            return error_response(
                "field_not_found",
                "Field not found.",
                404,
            )

        payload = read_json(request)
        partial = request.method == "PATCH"

        allowed_fields = {
            "department_id",
            "field_name",
            "field_code",
            "is_active",
        }

        unknown = set(payload) - allowed_fields

        if unknown:
            raise APIError(
                "unknown_fields",
                f"Unknown fields: {', '.join(sorted(unknown))}.",
            )

        department = instance.department

        if "department_id" in payload:
            department_id = _integer_value(
                payload["department_id"],
                "department_id",
                1,
            )

            department = academic_department_queryset(
                request,
                request.academic_access,
            ).filter(pk=department_id, is_active=True).first()

            if department is None:
                raise APIError(
                    "department_not_found",
                    "Active department not found in your accessible scope.",
                    404,
                )

        values = {
            "department": department,
            "field_name": _required_string(
                payload, "field_name", 150, partial, instance
            ),
            "field_code": _required_string(
                payload, "field_code", 20, partial, instance
            ),
            "is_active": _active_value(payload, instance),
        }

        field = _save_instance(Field, values, instance)

        return JsonResponse({"field": field_payload(field)})

    except APIError as error:
        return error_response(error.code, error.message, error.status_code)


@require_POST
@academic_access_required(write=True)
def field_activate_view(request, field_id):
    return _status_response(
        academic_field_queryset(request, request.academic_access),
        field_id,
        True,
        field_payload,
        "Field",
    )


@require_POST
@academic_access_required(write=True)
def field_deactivate_view(request, field_id):
    return _status_response(
        academic_field_queryset(request, request.academic_access),
        field_id,
        False,
        field_payload,
        "Field",
    )
# =========================================================
# Lesson API
# =========================================================


def _lesson_type_queryset():
    return Constant.objects.filter(
        category="lesson_type",
        is_active=True,
    )


def _resolve_lesson_type(value):
    if value is None:
        return None

    lesson_type_id = _integer_value(
        value,
        "lesson_type_id",
        1,
    )

    lesson_type = _lesson_type_queryset().filter(
        pk=lesson_type_id,
    ).first()

    if lesson_type is None:
        raise APIError(
            "lesson_type_not_found",
            "Active lesson type not found.",
            404,
        )

    return lesson_type


def _lesson_values(request, payload, instance=None):
    partial = request.method == "PATCH"

    department = (
        instance.department
        if instance is not None and partial
        else None
    )

    if "department_id" in payload:
        department_id = _integer_value(
            payload["department_id"],
            "department_id",
            1,
        )

        department = academic_department_queryset(
            request,
            request.academic_access,
        ).filter(
            pk=department_id,
            is_active=True,
        ).first()

        if department is None:
            raise APIError(
                "department_not_found",
                "Active department not found in your accessible scope.",
                404,
            )

    elif instance is None or not partial:
        raise APIError(
            "missing_field",
            "department_id is required.",
        )

    lesson_type = (
        instance.lesson_type
        if instance is not None and partial
        else None
    )

    if "lesson_type_id" in payload:
        lesson_type = _resolve_lesson_type(
            payload["lesson_type_id"]
        )

    lesson_code = _required_string(
        payload,
        "lesson_code",
        20,
        partial,
        instance,
    )

    title = _required_string(
        payload,
        "title",
        200,
        partial,
        instance,
    )

    practical_units = _integer_value(
        payload.get(
            "practical_units",
            instance.practical_units
            if instance is not None and partial
            else 0,
        ),
        "practical_units",
        0,
    )

    theory_units = _integer_value(
        payload.get(
            "theory_units",
            instance.theory_units
            if instance is not None and partial
            else 0,
        ),
        "theory_units",
        0,
    )

    if practical_units + theory_units <= 0:
        raise APIError(
            "invalid_units",
            "A lesson must have at least one practical or theory unit.",
        )

    return {
        "lesson_code": lesson_code,
        "title": title,
        "practical_units": practical_units,
        "theory_units": theory_units,
        "lesson_type": lesson_type,
        "department": department,
        "is_active": _active_value(payload, instance),
    }


@require_GET
@academic_access_required()
def lesson_list_view(request):
    try:
        queryset = academic_lesson_queryset(
            request,
            request.academic_access,
        )

        role = request.academic_access["role"]

        if role in {"student", "professor"}:
            queryset = queryset.filter(is_active=True)

        department_id = request.GET.get("department_id")
        faculty_id = request.GET.get("faculty_id")
        lesson_type_id = request.GET.get("lesson_type_id")

        if department_id:
            queryset = queryset.filter(
                department_id=_integer_value(
                    department_id,
                    "department_id",
                    1,
                )
            )

        if faculty_id:
            queryset = queryset.filter(
                department__faculty_id=_integer_value(
                    faculty_id,
                    "faculty_id",
                    1,
                )
            )

        if lesson_type_id:
            queryset = queryset.filter(
                lesson_type_id=_integer_value(
                    lesson_type_id,
                    "lesson_type_id",
                    1,
                )
            )

        queryset = _apply_common_filters(
            request,
            queryset,
            [
                "lesson_code",
                "title",
                "department__department_name",
                "department__faculty__faculty_name",
            ],
        ).order_by("title")

        result = _pagination(
            request,
            queryset,
            "lessons",
        )

        return JsonResponse({
            "count": result["count"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"],
            "lessons": [
                lesson_payload(item)
                for item in result["records"]
            ],
        })

    except APIError as error:
        return error_response(
            error.code,
            error.message,
            error.status_code,
        )


@require_POST
@academic_access_required(write=True)
def lesson_create_view(request):
    try:
        role = request.academic_access["role"]

        if role not in {
            "admin",
            "faculty_manager",
            "department_manager",
        }:
            raise APIError(
                "permission_denied",
                "Permission denied.",
                403,
            )

        payload = read_json(request)

        allowed_fields = {
            "lesson_code",
            "title",
            "practical_units",
            "theory_units",
            "lesson_type_id",
            "department_id",
            "is_active",
        }

        unknown = set(payload) - allowed_fields

        if unknown:
            raise APIError(
                "unknown_fields",
                f"Unknown fields: {', '.join(sorted(unknown))}.",
            )

        values = _lesson_values(
            request,
            payload,
        )

        lesson = _save_instance(
            Lesson,
            values,
        )

        return JsonResponse(
            {"lesson": lesson_payload(lesson)},
            status=201,
        )

    except APIError as error:
        return error_response(
            error.code,
            error.message,
            error.status_code,
        )


@require_GET
@academic_access_required()
def lesson_detail_view(request, lesson_id):
    queryset = academic_lesson_queryset(
        request,
        request.academic_access,
    )

    lesson = queryset.filter(pk=lesson_id).first()

    if lesson is None or (
        request.academic_access["role"] in {
            "student",
            "professor",
        }
        and not lesson.is_active
    ):
        return error_response(
            "lesson_not_found",
            "Lesson not found.",
            404,
        )

    return JsonResponse({
        "lesson": lesson_payload(lesson),
    })


@require_http_methods(["PUT", "PATCH"])
@academic_access_required(write=True)
def lesson_update_view(request, lesson_id):
    try:
        role = request.academic_access["role"]

        if role not in {
            "admin",
            "faculty_manager",
            "department_manager",
        }:
            raise APIError(
                "permission_denied",
                "Permission denied.",
                403,
            )

        instance = academic_lesson_queryset(
            request,
            request.academic_access,
        ).filter(pk=lesson_id).first()

        if instance is None:
            return error_response(
                "lesson_not_found",
                "Lesson not found.",
                404,
            )

        payload = read_json(request)

        allowed_fields = {
            "lesson_code",
            "title",
            "practical_units",
            "theory_units",
            "lesson_type_id",
            "department_id",
            "is_active",
        }

        unknown = set(payload) - allowed_fields

        if unknown:
            raise APIError(
                "unknown_fields",
                f"Unknown fields: {', '.join(sorted(unknown))}.",
            )

        values = _lesson_values(
            request,
            payload,
            instance,
        )

        lesson = _save_instance(
            Lesson,
            values,
            instance,
        )

        return JsonResponse({
            "lesson": lesson_payload(lesson),
        })

    except APIError as error:
        return error_response(
            error.code,
            error.message,
            error.status_code,
        )


@require_POST
@academic_access_required(write=True)
def lesson_activate_view(request, lesson_id):
    return _status_response(
        academic_lesson_queryset(
            request,
            request.academic_access,
        ),
        lesson_id,
        True,
        lesson_payload,
        "Lesson",
    )


@require_POST
@academic_access_required(write=True)
def lesson_deactivate_view(request, lesson_id):
    return _status_response(
        academic_lesson_queryset(
            request,
            request.academic_access,
        ),
        lesson_id,
        False,
        lesson_payload,
        "Lesson",
    )
# =========================================================
# Prerequisite API
# =========================================================


def _prerequisite_values(request, payload, instance=None):
    partial = request.method == "PATCH"

    lesson = instance.lesson if instance else None
    prerequisite_lesson = (
        instance.prerequisite_lesson
        if instance
        else None
    )

    accessible_lessons = academic_lesson_queryset(
        request,
        request.academic_access,
    )

    if "lesson_id" in payload:
        lesson_id = _integer_value(
            payload["lesson_id"],
            "lesson_id",
            1,
        )

        lesson = accessible_lessons.filter(
            pk=lesson_id,
            is_active=True,
        ).first()

        if lesson is None:
            raise APIError(
                "lesson_not_found",
                "Active lesson not found in your accessible scope.",
                404,
            )

    elif instance is None:
        raise APIError(
            "missing_field",
            "lesson_id is required.",
        )

    if "prerequisite_lesson_id" in payload:
        prerequisite_lesson_id = _integer_value(
            payload["prerequisite_lesson_id"],
            "prerequisite_lesson_id",
            1,
        )

        prerequisite_lesson = accessible_lessons.filter(
            pk=prerequisite_lesson_id,
            is_active=True,
        ).first()

        if prerequisite_lesson is None:
            raise APIError(
                "prerequisite_lesson_not_found",
                "Active prerequisite lesson not found in your accessible scope.",
                404,
            )

    elif instance is None:
        raise APIError(
            "missing_field",
            "prerequisite_lesson_id is required.",
        )

    if lesson.pk == prerequisite_lesson.pk:
        raise APIError(
            "invalid_prerequisite",
            "A lesson cannot be its own prerequisite.",
        )

    prerequisite_type = (
        instance.prerequisite_type
        if instance is not None
        else None
    )

    if "prerequisite_type_id" in payload:
        prerequisite_type_id = payload["prerequisite_type_id"]

        if prerequisite_type_id is None:
            prerequisite_type = None
        else:
            prerequisite_type_id = _integer_value(
                prerequisite_type_id,
                "prerequisite_type_id",
                1,
            )

            prerequisite_type = Constant.objects.filter(
                pk=prerequisite_type_id,
                category="prerequisite_type",
                is_active=True,
            ).first()

            if prerequisite_type is None:
                raise APIError(
                    "prerequisite_type_not_found",
                    "Active prerequisite type not found.",
                    404,
                )

    return {
        "lesson": lesson,
        "prerequisite_lesson": prerequisite_lesson,
        "prerequisite_type": prerequisite_type,
    }


@require_GET
@academic_access_required()
def prerequisite_list_view(request):
    try:
        queryset = academic_prerequisite_queryset(
            request,
            request.academic_access,
        )

        role = request.academic_access["role"]

        if role in {"student", "professor"}:
            queryset = queryset.filter(
                lesson__is_active=True,
                prerequisite_lesson__is_active=True,
            )

        lesson_id = request.GET.get("lesson_id")
        prerequisite_lesson_id = request.GET.get(
            "prerequisite_lesson_id"
        )

        if lesson_id:
            queryset = queryset.filter(
                lesson_id=_integer_value(
                    lesson_id,
                    "lesson_id",
                    1,
                )
            )

        if prerequisite_lesson_id:
            queryset = queryset.filter(
                prerequisite_lesson_id=_integer_value(
                    prerequisite_lesson_id,
                    "prerequisite_lesson_id",
                    1,
                )
            )

        search = request.GET.get("search", "").strip()

        if search:
            queryset = queryset.filter(
                Q(lesson__title__icontains=search)
                | Q(lesson__lesson_code__icontains=search)
                | Q(
                    prerequisite_lesson__title__icontains=search
                )
                | Q(
                    prerequisite_lesson__lesson_code__icontains=search
                )
            )

        queryset = queryset.order_by(
            "lesson__title",
            "prerequisite_lesson__title",
        )

        result = _pagination(
            request,
            queryset,
            "prerequisites",
        )

        return JsonResponse({
            "count": result["count"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"],
            "prerequisites": [
                prerequisite_payload(item)
                for item in result["records"]
            ],
        })

    except APIError as error:
        return error_response(
            error.code,
            error.message,
            error.status_code,
        )


@require_POST
@academic_access_required(write=True)
def prerequisite_create_view(request):
    try:
        role = request.academic_access["role"]

        if role not in {
            "admin",
            "faculty_manager",
            "department_manager",
        }:
            raise APIError(
                "permission_denied",
                "Permission denied.",
                403,
            )

        payload = read_json(request)

        allowed_fields = {
            "lesson_id",
            "prerequisite_lesson_id",
            "prerequisite_type_id",
        }

        unknown = set(payload) - allowed_fields

        if unknown:
            raise APIError(
                "unknown_fields",
                f"Unknown fields: {', '.join(sorted(unknown))}.",
            )

        values = _prerequisite_values(
            request,
            payload,
        )

        prerequisite = _save_instance(
            Prerequisite,
            values,
        )

        return JsonResponse(
            {
                "prerequisite": prerequisite_payload(
                    prerequisite
                )
            },
            status=201,
        )

    except APIError as error:
        return error_response(
            error.code,
            error.message,
            error.status_code,
        )


@require_GET
@academic_access_required()
def prerequisite_detail_view(request, prerequisite_id):
    prerequisite = academic_prerequisite_queryset(
        request,
        request.academic_access,
    ).filter(
        prereq_id=prerequisite_id,
    ).first()

    if prerequisite is None:
        return error_response(
            "prerequisite_not_found",
            "Prerequisite relationship not found.",
            404,
        )

    if request.academic_access["role"] in {
        "student",
        "professor",
    }:
        if (
            not prerequisite.lesson.is_active
            or not prerequisite.prerequisite_lesson.is_active
        ):
            return error_response(
                "prerequisite_not_found",
                "Prerequisite relationship not found.",
                404,
            )

    return JsonResponse({
        "prerequisite": prerequisite_payload(
            prerequisite
        )
    })


@require_http_methods(["PUT", "PATCH"])
@academic_access_required(write=True)
def prerequisite_update_view(request, prerequisite_id):
    try:
        role = request.academic_access["role"]

        if role not in {
            "admin",
            "faculty_manager",
            "department_manager",
        }:
            raise APIError(
                "permission_denied",
                "Permission denied.",
                403,
            )

        instance = academic_prerequisite_queryset(
            request,
            request.academic_access,
        ).filter(
            prereq_id=prerequisite_id,
        ).first()

        if instance is None:
            return error_response(
                "prerequisite_not_found",
                "Prerequisite relationship not found.",
                404,
            )

        payload = read_json(request)

        allowed_fields = {
            "lesson_id",
            "prerequisite_lesson_id",
            "prerequisite_type_id",
        }

        unknown = set(payload) - allowed_fields

        if unknown:
            raise APIError(
                "unknown_fields",
                f"Unknown fields: {', '.join(sorted(unknown))}.",
            )

        values = _prerequisite_values(
            request,
            payload,
            instance,
        )

        prerequisite = _save_instance(
            Prerequisite,
            values,
            instance,
        )

        return JsonResponse({
            "prerequisite": prerequisite_payload(
                prerequisite
            )
        })

    except APIError as error:
        return error_response(
            error.code,
            error.message,
            error.status_code,
        )


@require_http_methods(["DELETE"])
@academic_access_required(write=True)
def prerequisite_delete_view(request, prerequisite_id):
    role = request.academic_access["role"]

    if role not in {
        "admin",
        "faculty_manager",
        "department_manager",
    }:
        return error_response(
            "permission_denied",
            "Permission denied.",
            403,
        )

    prerequisite = academic_prerequisite_queryset(
        request,
        request.academic_access,
    ).filter(
        prereq_id=prerequisite_id,
    ).first()

    if prerequisite is None:
        return error_response(
            "prerequisite_not_found",
            "Prerequisite relationship not found.",
            404,
        )

    prerequisite.delete()

    return JsonResponse({
        "message": "Prerequisite relationship deleted successfully."
    })
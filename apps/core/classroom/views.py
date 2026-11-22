"""Admin API endpoints for classroom management."""

from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.views.decorators.http import (
    require_GET,
    require_POST,
    require_http_methods,
)

from apps.core.api import APIError, error_response, read_json
from apps.core.accounts.permissions import account_role_required
from apps.core.models import Classroom


def _classroom_payload(classroom):
    return {
        "id": classroom.pk,
        "building_name": classroom.building_name,
        "room_number": classroom.room_number,
        "capacity": classroom.capacity,
        "classroom_type": classroom.classroom_type,
    }


def _required_text(payload, field, instance=None, partial=False):
    if field not in payload:
        if partial:
            return getattr(instance, field)
        raise APIError(
            "missing_field",
            f"{field} is required.",
        )

    value = payload[field]

    if not isinstance(value, str) or not value.strip():
        raise APIError(
            "invalid_field",
            f"{field} must be a non-empty string.",
        )

    return value.strip()


def _capacity_value(payload, instance=None, partial=False):
    if "capacity" not in payload:
        if partial:
            return instance.capacity

        raise APIError(
            "missing_field",
            "capacity is required.",
        )

    value = payload["capacity"]

    if isinstance(value, bool):
        raise APIError(
            "invalid_capacity",
            "capacity must be a positive integer.",
        )

    try:
        capacity = int(value)
    except (TypeError, ValueError):
        raise APIError(
            "invalid_capacity",
            "capacity must be a positive integer.",
        )

    if str(capacity) != str(value).strip() or capacity <= 0:
        raise APIError(
            "invalid_capacity",
            "capacity must be a positive integer.",
        )

    return capacity


def _classroom_values(payload, instance=None, partial=False):
    return {
        "building_name": _required_text(
            payload, "building_name", instance, partial
        ),
        "room_number": _required_text(
            payload, "room_number", instance, partial
        ),
        "capacity": _capacity_value(
            payload, instance, partial
        ),
        "classroom_type": _required_text(
            payload, "classroom_type", instance, partial
        ),
    }


def _get_classroom_or_error(classroom_id):
    classroom = Classroom.objects.filter(pk=classroom_id).first()

    if classroom is None:
        raise APIError(
            "classroom_not_found",
            "Classroom not found.",
            404,
        )

    return classroom


# --------------------------------------------------
# List and search
# --------------------------------------------------

@require_GET
@account_role_required("admin")
def classroom_list_view(request):
    try:
        queryset = Classroom.objects.all().order_by(
            "building_name",
            "room_number",
        )

        search = request.GET.get("search", "").strip()

        if search:
            queryset = queryset.filter(
                Q(building_name__icontains=search)
                | Q(room_number__icontains=search)
                | Q(classroom_type__icontains=search)
            )

        page = request.GET.get("page", "1")
        page_size = request.GET.get("page_size", "20")

        try:
            page = int(page)
            page_size = int(page_size)
        except (TypeError, ValueError):
            raise APIError(
                "invalid_pagination",
                "page and page_size must be integers.",
            )

        if page < 1 or page_size < 1 or page_size > 100:
            raise APIError(
                "invalid_pagination",
                "page must be positive and page_size must be between 1 and 100.",
            )

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        return JsonResponse({
            "count": paginator.count,
            "page": page_obj.number,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
            "classrooms": [
                _classroom_payload(classroom)
                for classroom in page_obj.object_list
            ],
        })

    except APIError as error:
        return error_response(
            error.code,
            error.message,
            error.status_code,
        )


# --------------------------------------------------
# Create
# --------------------------------------------------

@require_POST
@account_role_required("admin")
def classroom_create_view(request):
    try:
        payload = read_json(request)
        values = _classroom_values(payload)

        classroom = Classroom.objects.create(**values)

        return JsonResponse(
            {
                "message": "Classroom created successfully.",
                "classroom": _classroom_payload(classroom),
            },
            status=201,
        )

    except APIError as error:
        return error_response(
            error.code,
            error.message,
            error.status_code,
        )


# --------------------------------------------------
# Detail
# --------------------------------------------------

@require_GET
@account_role_required("admin")
def classroom_detail_view(request, classroom_id):
    try:
        classroom = _get_classroom_or_error(classroom_id)

        return JsonResponse({
            "classroom": _classroom_payload(classroom),
        })

    except APIError as error:
        return error_response(
            error.code,
            error.message,
            error.status_code,
        )


# --------------------------------------------------
# Update
# --------------------------------------------------

@require_http_methods(["PUT", "PATCH"])
@account_role_required("admin")
def classroom_update_view(request, classroom_id):
    try:
        classroom = _get_classroom_or_error(classroom_id)
        payload = read_json(request)

        partial = request.method == "PATCH"

        values = _classroom_values(
            payload,
            instance=classroom,
            partial=partial,
        )

        for field, value in values.items():
            setattr(classroom, field, value)

        classroom.save(update_fields=list(values.keys()))

        return JsonResponse({
            "message": "Classroom updated successfully.",
            "classroom": _classroom_payload(classroom),
        })

    except APIError as error:
        return error_response(
            error.code,
            error.message,
            error.status_code,
        )


# --------------------------------------------------
# Delete
# --------------------------------------------------

@require_http_methods(["DELETE"])
@account_role_required("admin")
def classroom_delete_view(request, classroom_id):
    try:
        classroom = _get_classroom_or_error(classroom_id)

        try:
            classroom.delete()
        except ProtectedError:
            raise APIError(
                "classroom_in_use",
                "This classroom cannot be deleted because it is assigned to course offerings.",
                409,
            )

        return JsonResponse({
            "message": "Classroom deleted successfully.",
        })

    except APIError as error:
        return error_response(
            error.code,
            error.message,
            error.status_code,
        )
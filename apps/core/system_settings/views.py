"""Admin-only JSON API views for system settings."""

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import (
    require_GET,
    require_POST,
    require_http_methods,
)

from apps.core.api import APIError, error_response, read_json
from apps.core.accounts.permissions import role_required
from apps.core.models import Constant, SystemSetting
from apps.core.system_settings.services import (
    save_system_setting,
    system_settings_queryset,
    system_setting_payload,
    search_system_settings,
)


# --------------------------------------------------
# Query parameter validation
# --------------------------------------------------

def _integer_value(value, name, minimum=1):
    if isinstance(value, bool):
        raise APIError("invalid_field", f"{name} must be an integer.")

    try:
        result = int(value)
    except (TypeError, ValueError):
        raise APIError("invalid_field", f"{name} must be an integer.")

    if str(result) != str(value).strip():
        raise APIError("invalid_field", f"{name} must be an integer.")

    if result < minimum:
        raise APIError(
            "invalid_field",
            f"{name} must be greater than or equal to {minimum}.",
        )

    return result


def _get_setting_or_error(setting_id):
    setting = system_settings_queryset().filter(
        pk=setting_id
    ).first()

    if setting is None:
        raise APIError(
            "setting_not_found",
            "System setting not found.",
            404,
        )

    return setting


# --------------------------------------------------
# List and search
# --------------------------------------------------

@require_GET
@role_required("admin")
def system_setting_list_view(request):
    """List, search, filter, and paginate system settings."""

    try:
        queryset = system_settings_queryset()

        search = request.GET.get("search", "").strip()
        queryset = search_system_settings(queryset, search)

        data_type_id = request.GET.get("data_type_id")
        if data_type_id:
            parsed_id = _integer_value(data_type_id, "data_type_id")
            queryset = queryset.filter(data_type_id=parsed_id)

        data_type_code = request.GET.get("data_type")
        if data_type_code:
            queryset = queryset.filter(
                data_type__category="data_type",
                data_type__code__iexact=data_type_code.strip(),
            )

        page = _integer_value(
            request.GET.get("page", "1"),
            "page",
        )

        page_size = _integer_value(
            request.GET.get("page_size", "20"),
            "page_size",
        )

        if page_size > 100:
            raise APIError(
                "invalid_page_size",
                "page_size cannot exceed 100.",
            )

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        return JsonResponse({
            "count": paginator.count,
            "page": page_obj.number,
            "page_size": page_size,
            "total_pages": paginator.num_pages,
            "settings": [
                system_setting_payload(setting)
                for setting in page_obj.object_list
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
@role_required("admin")
def system_setting_create_view(request):
    """Create a new system setting."""

    try:
        payload = read_json(request)

        setting = save_system_setting(
            payload=payload,
            person=request.user,
        )

        return JsonResponse(
            {
                "message": "System setting created successfully.",
                "setting": system_setting_payload(setting),
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
@role_required("admin")
def system_setting_detail_view(request, setting_id):
    """Return details of one system setting."""

    try:
        setting = _get_setting_or_error(setting_id)

        return JsonResponse({
            "setting": system_setting_payload(setting),
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
@role_required("admin")
def system_setting_update_view(request, setting_id):
    """Update a system setting using PUT or PATCH."""

    try:
        setting = _get_setting_or_error(setting_id)
        payload = read_json(request)

        partial = request.method == "PATCH"

        updated_setting = save_system_setting(
            payload=payload,
            person=request.user,
            instance=setting,
            partial=partial,
        )

        return JsonResponse({
            "message": "System setting updated successfully.",
            "setting": system_setting_payload(updated_setting),
        })

    except APIError as error:
        return error_response(
            error.code,
            error.message,
            error.status_code,
        )

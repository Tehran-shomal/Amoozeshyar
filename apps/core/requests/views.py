"""Role-aware JSON review endpoint for existing request models."""

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.core.api import APIError, error_response, read_json
from apps.core.requests.services import REQUEST_MODELS, transition_request


@require_POST
def review_view(request, request_type, request_id):
    definition = REQUEST_MODELS.get(request_type)
    if definition is None:
        return error_response("request_type_not_found", "Request type not found.", 404)
    if not request.user.is_authenticated:
        return error_response(
            "authentication_required", "Authentication is required.", 401
        )

    try:
        payload = read_json(request)
        target_status = payload.get("target_status")
        if not isinstance(target_status, str) or not target_status.strip():
            raise APIError("missing_target_status", "A target_status is required.")
        instance = definition.model.objects.filter(pk=request_id).first()
        if instance is None:
            raise APIError("request_not_found", "Request not found.", 404)
        updated = transition_request(instance, target_status, reviewer=request.user)
    except APIError as error:
        return error_response(error.code, error.message, error.status_code)

    status = getattr(updated, definition.status_field)
    return JsonResponse(
        {
            "request": {
                "id": updated.pk,
                "type": request_type,
                "status": status.code if status else None,
            }
        }
    )

"""Role-aware JSON review endpoint for existing request models."""

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.core.api import APIError, error_response, read_json
from apps.core.requests.services import REQUEST_MODELS, transition_request
from apps.core.accounts.services import (
    current_user_account,
    USER_ACCOUNT_SESSION_KEY,
)
from apps.core.models import UserAccount
def _reviewer_account_for_request(request):
    account = current_user_account(request)
    if account is not None:
        return account

    # Backward compatibility for authenticated users with exactly
    # one active account and no account selected in the session.
    if request.session.get(USER_ACCOUNT_SESSION_KEY) is not None:
        return None

    accounts = list(
        UserAccount.objects
        .select_related("role", "person")
        .filter(
            person=request.user,
            is_active=True,
            role__is_active=True,
        )
        .order_by("pk")[:2]
    )

    return accounts[0] if len(accounts) == 1 else None
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
        reviewer_account = _reviewer_account_for_request(request)

        if reviewer_account is None:
            raise APIError(
                "permission_denied",
                "An active reviewer account is required.",
                403,
            )

        updated = transition_request(
            instance,
            target_status,
            reviewer=reviewer_account,
        )
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

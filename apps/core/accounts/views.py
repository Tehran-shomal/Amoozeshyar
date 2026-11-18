from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from apps.core.api import APIError, error_response, read_json
from apps.core.accounts.services import authenticate_person, role_codes_for


@require_GET
@ensure_csrf_cookie
def csrf_token_view(request):
    """Set the CSRF cookie and return a token for browser JSON requests."""
    return JsonResponse({"csrf_token": get_token(request)})


def _user_payload(user):
    return {
        "id": user.pk,
        "username": user.get_username(),
        "full_name": user.full_name,
        "roles": sorted(role_codes_for(user)),
    }


@require_POST
def login_view(request):
    try:
        payload = read_json(request)
        username = payload.get("username")
        password = payload.get("password")
        if not isinstance(username, str) or not username.strip():
            raise APIError("missing_credentials", "A username is required.")
        if not isinstance(password, str) or not password:
            raise APIError("missing_credentials", "A password is required.")

        user = authenticate_person(username.strip(), password, request=request)
        if user is None:
            return error_response(
                "invalid_credentials",
                "Username or password is incorrect.",
                401,
            )
    except APIError as error:
        return error_response(error.code, error.message, error.status_code)

    auth_login(request, user)
    return JsonResponse({"user": _user_payload(user)})


@require_POST
def logout_view(request):
    if not request.user.is_authenticated:
        return error_response(
            "authentication_required",
            "Authentication is required.",
            401,
        )
    auth_logout(request)
    return JsonResponse({"success": True})


@require_GET
def me_view(request):
    if not request.user.is_authenticated:
        return error_response(
            "authentication_required",
            "Authentication is required.",
            401,
        )
    return JsonResponse({"user": _user_payload(request.user)})

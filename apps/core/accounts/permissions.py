from functools import wraps

from apps.core.api import error_response
from apps.core.accounts.services import (
    current_account_role,
    user_has_any_role,
)


def role_required(*roles):
    """Restrict an API view to authenticated users with one of the roles."""
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return error_response(
                    "authentication_required",
                    "Authentication is required.",
                    401,
                )
            if not user_has_any_role(user, roles):
                return error_response(
                    "permission_denied",
                    "Permission denied.",
                    403,
                )
            return view(request, *args, **kwargs)

        return wrapped

    return decorator


def account_role_required(*roles):
    """
    Restrict an API view using the exact active UserAccount in the session.
    Unlike role_required, this does not aggregate roles across user accounts.
    """
    allowed_roles = set(roles)

    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return error_response(
                    "authentication_required",
                    "Authentication is required.",
                    401,
                )

            active_role = current_account_role(request)

            if active_role not in allowed_roles:
                return error_response(
                    "permission_denied",
                    "The active account does not have permission to perform this action.",
                    403,
                )

            return view(request, *args, **kwargs)

        return wrapped

    return decorator
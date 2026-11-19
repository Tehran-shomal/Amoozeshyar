"""Shared helpers for the Django-native JSON API."""

import json

from django.http import JsonResponse


class APIError(Exception):
    def __init__(self, code, message, status_code=400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def read_json(request):
    """Parse a JSON object from a request body."""
    try:
        payload = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise APIError("invalid_json", "Request body must be valid JSON.") from error

    if not isinstance(payload, dict):
        raise APIError("invalid_json", "Request body must be a JSON object.")
    return payload


def error_response(code, message, status=400):
    return JsonResponse(
        {"error": {"code": code, "message": message}},
        status=status,
    )

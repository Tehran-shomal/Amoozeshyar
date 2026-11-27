"""JSON boundary for database-backed student portal pages."""

from urllib.parse import urlsplit, urlunsplit

from django.core.exceptions import PermissionDenied
from django.db import OperationalError
from django.http import Http404, HttpResponseNotAllowed, JsonResponse, QueryDict
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
from django.views.decorators.http import require_http_methods

from apps.core.api import APIError, error_response, read_json
from .registry import PAGES
from .react_forms import serialize_form
from .react_payloads import serialize_page
from .views import PortalView

REACT_ACCEPT = "application/vnd.amoozeshyar.react+json"


def _template_for(slug):
    return "mobina/home.html" if slug == "home" else "core/section.html"


def _portal_redirect(slug, response_url):
    """Return successful page submissions to the UI route, not the API route."""
    query = urlsplit(response_url).query
    page_path = reverse("core:section", kwargs={"slug": slug})
    return urlunsplit(("", "", page_path, query, ""))


def _page_payload(slug, context, request):
    rendered = render_to_string(_template_for(slug), context, request=request)
    selected_term = context.get("selected_term")
    return {
        "page": slug,
        "html": rendered,
        "profile": context.get("api_profile", {}),
        "term": {
            "term_code": selected_term.term_code if selected_term else None,
            "display_label": context.get("term_display_code", ""),
        },
    }


def _form_post_data(payload):
    """Convert JSON scalar/list values to Django's normal form data shape."""
    form_data = QueryDict("", mutable=True)
    for key, value in payload.items():
        if not isinstance(key, str):
            raise APIError("invalid_form_payload", "Form field names must be strings.")
        values = value if isinstance(value, list) else [value]
        for item in values:
            if isinstance(item, (dict, list)):
                raise APIError("invalid_form_payload", "Form fields must contain scalar values.")
            form_data.appendlist(key, "" if item is None else str(item))
    return form_data


def _private_response(response):
    response["Cache-Control"] = "private, no-store"
    return response


@require_http_methods(["GET"])
def portal_ui_page_api(request, slug):
    """Return allowlisted JSON for React; never serialize a Django template."""
    if not request.user.is_authenticated:
        return _private_response(error_response(
            "authentication_required", "Authentication is required.", 401
        ))

    page_slug = None if slug == "home" else slug
    if slug != "home" and slug not in PAGES:
        return _private_response(error_response(
            "page_not_found", "Portal page not found.", 404
        ))

    try:
        context = PortalView().context(request, page_slug)
        return _private_response(JsonResponse(serialize_page(slug, context)))
    except APIError as error:
        response = error_response(error.code, error.message, error.status_code)
    except PermissionDenied:
        response = error_response("permission_denied", "Permission denied.", 403)
    except Http404:
        response = error_response(
            "page_data_not_found", "The requested page data was not found.", 404
        )
    except OperationalError:
        response = error_response("database_unavailable", "Database is unavailable.", 503)
    return _private_response(response)


@require_http_methods(["GET", "POST"])
def portal_page_api(request, slug):
    """Read or submit an existing portal page using its owning templates/forms."""
    if not request.user.is_authenticated:
        return error_response(
            "authentication_required", "Authentication is required.", 401
        )

    page_slug = None if slug == "home" else slug
    if slug != "home" and slug not in PAGES:
        return error_response("page_not_found", "Portal page not found.", 404)

    view = PortalView()
    try:
        if request.method == "GET":
            context = view.context(request, page_slug)
            return JsonResponse(_page_payload(slug, context, request))

        if slug == "home":
            return error_response(
                "method_not_allowed",
                "Dashboard does not accept form submissions.",
                405,
            )

        if request.content_type == "multipart/form-data":
            request._post = request.POST
            request._files = request.FILES
        else:
            request._post = _form_post_data(read_json(request))
            request._files = MultiValueDict()
        response = view.post(request, slug=page_slug)

        if 300 <= response.status_code < 400:
            return JsonResponse({"redirect": _portal_redirect(slug, response.url)})
        if response.status_code == 400:
            if REACT_ACCEPT in request.headers.get("Accept", ""):
                return JsonResponse({
                    "error": {
                        "code": "validation_error",
                        "message": "فرم را بررسی و خطاها را اصلاح کنید.",
                    },
                    "form": serialize_form(getattr(view, "submitted_form", None)),
                }, status=400)
            return JsonResponse({
                "error": {
                    "code": "validation_error",
                    "message": "فرم را بررسی و خطاها را اصلاح کنید.",
                },
                "html": response.content.decode(response.charset or "utf-8"),
            }, status=400)
        if isinstance(response, HttpResponseNotAllowed):
            return error_response(
                "method_not_allowed",
                "This page does not accept form submissions.",
                405,
            )
        return error_response(
            "page_submission_failed",
            "The form could not be submitted.",
            response.status_code,
        )
    except APIError as error:
        return error_response(error.code, error.message, error.status_code)
    except PermissionDenied:
        return error_response("permission_denied", "Permission denied.", 403)
    except Http404:
        return error_response("page_data_not_found", "The requested page data was not found.", 404)
    except OperationalError:
        return error_response("database_unavailable", "Database is unavailable.", 503)

"""Session-authenticated JSON API views for communications."""

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from apps.core.api import APIError, error_response, read_json
from apps.core.system_settings.reader import get_pagination_settings
from apps.core.communication.services import (
    communications_for_inbox,
    communications_for_outbox,
    get_communication_for_person,
    mark_communication_read,
    mark_communication_unread,
    send_communication,
)


def _authentication_error(request):
    """Return an authentication error for anonymous users."""
    if not request.user.is_authenticated:
        return error_response(
            "authentication_required",
            "Authentication is required.",
            401,
        )
    return None


def _account_payload(account):
    """Serialize an account without exposing its password."""
    return {
        "id": account.pk,
        "username": account.username,
        "person_id": account.person_id,
        "full_name": account.person.full_name,
        "role": account.role.role_name,
    }


def _communication_payload(communication):
    """Serialize a communication and its safe related information."""
    return {
        "id": communication.communication_id,
        "sender": _account_payload(communication.sender),
        "receiver": _account_payload(communication.receiver),
        "subject": communication.subject,
        "message_body": communication.message_body,
        "communication_type": (
            {
                "code": communication.communication_type.code,
                "label": communication.communication_type.label,
            }
            if communication.communication_type_id
            else None
        ),
        "status": (
            {
                "code": communication.status.code,
                "label": communication.status.label,
            }
            if communication.status_id
            else None
        ),
        "is_read": communication.is_read,
        "sent_at": communication.sent_at.isoformat(),
        "read_at": (
            communication.read_at.isoformat()
            if communication.read_at
            else None
        ),
    }


def _paginated_communications(queryset, request):
    """Apply search and pagination to a communication queryset."""
    search = request.GET.get("search", "").strip()

    if search:
        queryset = queryset.filter(
            Q(subject__icontains=search)
            | Q(message_body__icontains=search)
            | Q(sender__username__icontains=search)
            | Q(receiver__username__icontains=search)
            | Q(sender__person__first_name__icontains=search)
            | Q(sender__person__last_name__icontains=search)
            | Q(receiver__person__first_name__icontains=search)
            | Q(receiver__person__last_name__icontains=search)
        )

    default_page_size, max_page_size = get_pagination_settings()

    try:
        page = int(request.GET.get("page", "1"))
        page_size = int(
            request.GET.get("page_size", str(default_page_size))
        )
    except (TypeError, ValueError):
        raise APIError(
            "invalid_pagination",
            "page and page_size must be integers.",
        )

    if page < 1:
        raise APIError("invalid_page", "page must be greater than zero.")

    if page_size < 1 or page_size > max_page_size:
        raise APIError(
            "invalid_page_size",
            "page_size must be between 1 and 100.",
        )

    total_count = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size

    messages = queryset[start:end]

    return {
        "count": total_count,
        "page": page,
        "page_size": page_size,
        "total_pages": (total_count + page_size - 1) // page_size,
        "results": [
            _communication_payload(message)
            for message in messages
        ],
    }


@require_POST
def send_view(request):
    """Send a communication from one of the authenticated person's accounts."""
    auth_error = _authentication_error(request)
    if auth_error:
        return auth_error

    try:
        payload = read_json(request)

        communication = send_communication(
            person=request.user,
            receiver_account_id=payload.get("receiver_account_id"),
            sender_account_id=payload.get("sender_account_id"),
            subject=payload.get("subject"),
            message_body=payload.get("message_body"),
            communication_type_code=payload.get("communication_type_code"),
        )
    except APIError as error:
        return error_response(error.code, error.message, error.status_code)

    return JsonResponse(
        {"communication": _communication_payload(communication)},
        status=201,
    )


@require_GET
def inbox_view(request):
    """List messages received by the authenticated person."""
    auth_error = _authentication_error(request)
    if auth_error:
        return auth_error

    try:
        result = _paginated_communications(
            communications_for_inbox(request.user),
            request,
        )
    except APIError as error:
        return error_response(error.code, error.message, error.status_code)

    return JsonResponse({"inbox": result})


@require_GET
def outbox_view(request):
    """List messages sent by the authenticated person."""
    auth_error = _authentication_error(request)
    if auth_error:
        return auth_error

    try:
        result = _paginated_communications(
            communications_for_outbox(request.user),
            request,
        )
    except APIError as error:
        return error_response(error.code, error.message, error.status_code)

    return JsonResponse({"outbox": result})


@require_GET
def detail_view(request, communication_id):
    """Retrieve a communication visible to the authenticated person."""
    auth_error = _authentication_error(request)
    if auth_error:
        return auth_error

    try:
        communication = get_communication_for_person(
            request.user,
            communication_id,
        )
    except APIError as error:
        return error_response(error.code, error.message, error.status_code)

    return JsonResponse(
        {"communication": _communication_payload(communication)}
    )


@require_POST
def mark_read_view(request, communication_id):
    """Mark a received communication as read."""
    auth_error = _authentication_error(request)
    if auth_error:
        return auth_error

    try:
        communication = mark_communication_read(
            request.user,
            communication_id,
        )
    except APIError as error:
        return error_response(error.code, error.message, error.status_code)

    return JsonResponse(
        {"communication": _communication_payload(communication)}
    )


@require_POST
def mark_unread_view(request, communication_id):
    """Mark a received communication as unread."""
    auth_error = _authentication_error(request)
    if auth_error:
        return auth_error

    try:
        communication = mark_communication_unread(
            request.user,
            communication_id,
        )
    except APIError as error:
        return error_response(error.code, error.message, error.status_code)

    return JsonResponse(
        {"communication": _communication_payload(communication)}
    )

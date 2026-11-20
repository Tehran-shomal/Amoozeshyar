"""Business services for secure communication management."""

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.core.api import APIError
from apps.core.models import Communication, Constant, UserAccount


def active_accounts_for_person(person):
    """Return only active accounts with active roles owned by the person."""
    return (
        UserAccount.objects
        .filter(
            person=person,
            is_active=True,
            role__is_active=True,
        )
        .select_related("role", "person")
        .order_by("pk")
    )


def resolve_sender_account(person, sender_account_id=None):
    """Resolve a sender account without selecting an arbitrary account."""
    accounts = active_accounts_for_person(person)

    if sender_account_id is not None:
        if isinstance(sender_account_id, bool) or not isinstance(sender_account_id, int):
            raise APIError(
                "invalid_sender_account",
                "sender_account_id must be an integer.",
            )

        account = accounts.filter(pk=sender_account_id).first()
        if account is None:
            raise APIError(
                "sender_account_not_available",
                "The selected sender account is not available to this user.",
                403,
            )
        return account

    account_ids = list(accounts.values_list("pk", flat=True))

    if not account_ids:
        raise APIError(
            "sender_account_not_found",
            "No active sender account is available.",
            403,
        )

    if len(account_ids) > 1:
        raise APIError(
            "sender_account_required",
            "This user has multiple active accounts. Specify sender_account_id.",
        )

    return accounts.get(pk=account_ids[0])


def resolve_receiver_account(receiver_account_id):
    """Resolve an active receiver account with an active role."""
    if (
        isinstance(receiver_account_id, bool)
        or not isinstance(receiver_account_id, int)
    ):
        raise APIError(
            "invalid_receiver_account",
            "receiver_account_id must be an integer.",
        )

    account = (
        UserAccount.objects
        .select_related("person", "role")
        .filter(
            pk=receiver_account_id,
            is_active=True,
            role__is_active=True,
        )
        .first()
    )

    if account is None:
        raise APIError(
            "receiver_account_not_found",
            "The receiver account does not exist or is inactive.",
            404,
        )

    return account


def _active_constant(category, code, error_code):
    if not isinstance(code, str) or not code.strip():
        raise APIError(error_code, f"A valid {category} code is required.")

    constant = Constant.objects.filter(
        category=category,
        code=code.strip(),
        is_active=True,
    ).first()

    if constant is None:
        raise APIError(
            error_code,
            f"The selected {category} is invalid or inactive.",
        )

    return constant


@transaction.atomic
def send_communication(
    person,
    receiver_account_id,
    subject,
    message_body,
    sender_account_id=None,
    communication_type_code=None,
):
    """Create a communication using accounts owned by the authenticated person."""
    sender = resolve_sender_account(person, sender_account_id)
    receiver = resolve_receiver_account(receiver_account_id)

    if not isinstance(subject, str) or not subject.strip():
        raise APIError("invalid_subject", "subject must be a non-empty string.")

    subject = subject.strip()
    if len(subject) > 255:
        raise APIError("invalid_subject", "subject must not exceed 255 characters.")

    if not isinstance(message_body, str) or not message_body.strip():
        raise APIError(
            "invalid_message_body",
            "message_body must be a non-empty string.",
        )

    communication_type = None
    if communication_type_code is not None:
        communication_type = _active_constant(
            "communication_type",
            communication_type_code,
            "invalid_communication_type",
        )

    unread_status = Constant.objects.filter(
        category="communication_status",
        code="unread",
        is_active=True,
    ).first()

    return Communication.objects.create(
        sender=sender,
        receiver=receiver,
        subject=subject,
        message_body=message_body.strip(),
        communication_type=communication_type,
        status=unread_status,
    )


def communications_for_inbox(person):
    """Return messages received by any account belonging to the person."""
    return (
        Communication.objects
        .filter(receiver__person=person)
        .select_related(
            "sender__person",
            "sender__role",
            "receiver__person",
            "receiver__role",
            "communication_type",
            "status",
        )
        .order_by("-sent_at", "-communication_id")
    )


def communications_for_outbox(person):
    """Return messages sent by any account belonging to the person."""
    return (
        Communication.objects
        .filter(sender__person=person)
        .select_related(
            "sender__person",
            "sender__role",
            "receiver__person",
            "receiver__role",
            "communication_type",
            "status",
        )
        .order_by("-sent_at", "-communication_id")
    )


def get_communication_for_person(person, communication_id):
    """Return a message only if the person is its sender or receiver."""
    if (
        isinstance(communication_id, bool)
        or not isinstance(communication_id, int)
    ):
        raise APIError("invalid_communication_id", "Invalid communication ID.")

    communication = (
        Communication.objects
        .filter(communication_id=communication_id)
        .filter(
            Q(sender__person=person) | Q(receiver__person=person)
        )
        .select_related(
            "sender__person",
            "sender__role",
            "receiver__person",
            "receiver__role",
            "communication_type",
            "status",
        )
        .first()
    )

    if communication is None:
        raise APIError("communication_not_found", "Communication not found.", 404)

    return communication


@transaction.atomic
def mark_communication_read(person, communication_id):
    """Mark a received message as read; preserve the replied workflow status."""
    communication = get_communication_for_person(person, communication_id)

    if communication.receiver.person_id != person.pk:
        raise APIError(
            "permission_denied",
            "Only the receiver can change the read state.",
            403,
        )

    if not communication.is_read:
        communication.is_read = True
        communication.read_at = timezone.now()

        if communication.status_id and communication.status.code == "unread":
            read_status = Constant.objects.filter(
                category="communication_status",
                code="read",
                is_active=True,
            ).first()
            if read_status:
                communication.status = read_status

        communication.save(update_fields=["is_read", "read_at", "status"])

    return communication


@transaction.atomic
def mark_communication_unread(person, communication_id):
    """Mark a received message as unread; preserve the replied workflow status."""
    communication = get_communication_for_person(person, communication_id)

    if communication.receiver.person_id != person.pk:
        raise APIError(
            "permission_denied",
            "Only the receiver can change the read state.",
            403,
        )

    if communication.is_read:
        communication.is_read = False
        communication.read_at = None

        if communication.status_id and communication.status.code == "read":
            unread_status = Constant.objects.filter(
                category="communication_status",
                code="unread",
                is_active=True,
            ).first()
            if unread_status:
                communication.status = unread_status

        communication.save(update_fields=["is_read", "read_at", "status"])

    return communication

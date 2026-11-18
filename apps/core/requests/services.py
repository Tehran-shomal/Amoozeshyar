"""Reusable review transitions for request-like models (ADR-004)."""

from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from apps.core.api import APIError
from apps.core.accounts.services import user_has_any_role
from apps.core.models import (
    Constant,
    CreditTransferRequest,
    GradeAppeal,
    Internship,
    InternshipRequest,
    Proposal,
    RefundRequest,
    ScholarshipApplication,
    StudentServiceRequest,
    ThesisProgressReport,
    TransferRequest,
    UserAccount,
)


@dataclass(frozen=True)
class RequestDefinition:
    model: type
    status_field: str
    reviewer_roles: frozenset[str]


REQUEST_MODELS = {
    "student-service": RequestDefinition(
        StudentServiceRequest, "service_decision_state", frozenset({"education_officer", "admin"})
    ),
    "scholarship-application": RequestDefinition(
        ScholarshipApplication, "scholarship_status", frozenset({"scholarship_officer", "admin"})
    ),
    "proposal": RequestDefinition(
        Proposal, "proposal_status", frozenset({"professor", "education_officer", "admin"})
    ),
    "transfer": RequestDefinition(
        TransferRequest, "review_status", frozenset({"education_officer", "admin"})
    ),
    "credit-transfer": RequestDefinition(
        CreditTransferRequest, "status", frozenset({"education_officer", "admin"})
    ),
    "internship-request": RequestDefinition(
        InternshipRequest, "status", frozenset({"student_affairs_officer", "admin"})
    ),
    "internship": RequestDefinition(
        Internship, "status", frozenset({"student_affairs_officer", "admin"})
    ),
    "refund": RequestDefinition(
        RefundRequest, "refund_review_state", frozenset({"education_officer", "admin"})
    ),
    "grade-appeal": RequestDefinition(
        GradeAppeal, "appeal_status", frozenset({"education_officer", "professor", "admin"})
    ),
    "thesis-progress-report": RequestDefinition(
        ThesisProgressReport,
        "review_status",
        frozenset({"professor", "education_officer", "admin"}),
    ),
}

ALLOWED_TARGETS = frozenset({"in_review", "approved", "rejected"})


def _definition_for_instance(instance):
    for definition in REQUEST_MODELS.values():
        if isinstance(instance, definition.model):
            return definition
    raise APIError("unsupported_request_type", "This request type does not support review.", 404)


def _status_category(model, field_name):
    field = model._meta.get_field(field_name)
    choices = field.get_limit_choices_to()
    return choices.get("category")


@transaction.atomic
def transition_request(instance, target_status, reviewer=None):
    """Move a supported request from submission/review into a valid next state."""
    definition = _definition_for_instance(instance)
    if reviewer is None or not user_has_any_role(reviewer, definition.reviewer_roles):
        raise APIError("permission_denied", "Permission denied.", 403)

    if not isinstance(target_status, str):
        raise APIError("invalid_transition", "The requested status transition is invalid.")
    target_code = target_status.strip().casefold()
    if target_code not in ALLOWED_TARGETS:
        raise APIError("invalid_transition", "The requested status transition is invalid.")

    current = definition.model.objects.select_for_update().filter(pk=instance.pk).first()
    if current is None:
        raise APIError("request_not_found", "Request not found.", 404)

    status_field = definition.status_field
    current_status = getattr(current, status_field)
    current_code = current_status.code.casefold() if current_status else None

    if current_code == target_code:
        return current

    if current_code == "submitted":
        allowed_from_current = frozenset({"in_review"})
    # Legacy `pending` data represents submitted requests. Older admin flows
    # made decisions without an explicit in-review state, so those remain valid.
    elif current_code == "pending":
        allowed_from_current = ALLOWED_TARGETS
    elif current_code == "in_review":
        allowed_from_current = frozenset({"approved", "rejected"})
    else:
        allowed_from_current = frozenset()
    if target_code not in allowed_from_current:
        raise APIError("invalid_transition", "The requested status transition is invalid.")

    category = _status_category(definition.model, status_field)
    target = Constant.objects.filter(
        category=category,
        code__iexact=target_code,
        is_active=True,
    ).first()
    if target is None:
        raise APIError(
            "request_status_unavailable",
            f"The {target_code} status has not been configured for this request.",
            500,
        )

    setattr(current, status_field, target)
    update_fields = [status_field]
    if definition.model is Internship and target_code in {"approved", "rejected"}:
        reviewer_account = UserAccount.objects.filter(
            person=reviewer,
            is_active=True,
        ).order_by("pk").first()
        current.reviewed_by = reviewer_account
        current.reviewed_at = timezone.now()
        update_fields.extend(["reviewed_by", "reviewed_at"])
    current.save(update_fields=update_fields)
    return current

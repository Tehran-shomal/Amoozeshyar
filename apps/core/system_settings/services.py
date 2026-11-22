"""Business services for system settings API."""

from datetime import date
from decimal import Decimal, InvalidOperation

from django.db import IntegrityError, transaction
from django.db.models import Q

from apps.core.api import APIError
from apps.core.accounts.services import _normalize_role
from apps.core.models import Constant, SystemSetting, UserAccount


# --------------------------------------------------
# Queryset
# --------------------------------------------------

def system_settings_queryset():
    """Return system settings with related objects loaded."""

    return SystemSetting.objects.select_related(
        "data_type",
        "updated_by",
        "updated_by__role",
    ).order_by("setting_key")


# --------------------------------------------------
# Safe updater resolution
# --------------------------------------------------

def _admin_account_for_person(person):
    """
    Resolve the unique active admin UserAccount for a Person.

    Return None if no unique active admin account exists.
    Never select an arbitrary account.
    """

    if person is None or not person.is_authenticated:
        return None

    accounts = (
        UserAccount.objects.select_related("role")
        .filter(
            person=person,
            is_active=True,
            role__is_active=True,
        )
    )

    admin_accounts = [
        account
        for account in accounts
        if _normalize_role(account.role.role_name) == "admin"
    ]

    if len(admin_accounts) != 1:
        return None

    return admin_accounts[0]


# --------------------------------------------------
# Serialization
# --------------------------------------------------

def system_setting_payload(setting):
    """Serialize a setting without exposing sensitive account information."""

    data_type = setting.data_type
    updated_by = setting.updated_by

    return {
        "id": setting.setting_id,
        "setting_key": setting.setting_key,
        "setting_value": setting.setting_value,
        "data_type": (
            {
                "id": data_type.pk,
                "code": data_type.code,
                "label": data_type.label,
            }
            if data_type else None
        ),
        "description": setting.description,
        "updated_at": setting.updated_at.isoformat(),
        "updated_by": (
            {
                "id": updated_by.pk,
                "username": updated_by.username,
            }
            if updated_by else None
        ),
    }


# --------------------------------------------------
# Validation helpers
# --------------------------------------------------

def _integer_value(value, name, minimum=None):
    if isinstance(value, bool):
        raise APIError("invalid_field", f"{name} must be an integer.")

    if isinstance(value, int):
        result = value
    elif isinstance(value, str):
        raw = value.strip()

        try:
            result = int(raw)
        except ValueError:
            raise APIError("invalid_field", f"{name} must be an integer.")

        if str(result) != raw and not (
            raw.startswith("+") and raw[1:].isdigit()
        ):
            raise APIError("invalid_field", f"{name} must be an integer.")
    else:
        raise APIError("invalid_field", f"{name} must be an integer.")

    if minimum is not None and result < minimum:
        raise APIError(
            "invalid_field",
            f"{name} must be greater than or equal to {minimum}.",
        )

    return result


def _validate_setting_key(value):
    if not isinstance(value, str):
        raise APIError("invalid_field", "setting_key must be a string.")

    value = value.strip()

    if not value:
        raise APIError("invalid_field", "setting_key cannot be empty.")

    if len(value) > 100:
        raise APIError(
            "invalid_field",
            "setting_key cannot exceed 100 characters.",
        )

    return value


def _validate_setting_value(value):
    if not isinstance(value, str):
        raise APIError("invalid_field", "setting_value must be a string.")

    if len(value) > 255:
        raise APIError(
            "invalid_field",
            "setting_value cannot exceed 255 characters.",
        )

    return value


def _validate_description(value):
    if value is not None and not isinstance(value, str):
        raise APIError("invalid_field", "description must be a string or null.")

    return value


def _validate_typed_value(value, data_type):
    """Validate a string value according to its selected data type."""

    if data_type is None:
        return value

    code = data_type.code.strip().casefold()

    if code == "string":
        return value

    if code == "integer":
        try:
            parsed = int(value.strip())
        except (ValueError, AttributeError):
            raise APIError(
                "invalid_setting_value",
                "setting_value must contain a valid integer.",
            )

        if str(parsed) != value.strip() and not (
            value.strip().startswith("+")
            and value.strip()[1:].isdigit()
        ):
            raise APIError(
                "invalid_setting_value",
                "setting_value must contain a valid integer.",
            )

        return str(parsed)

    if code == "decimal":
        try:
            parsed = Decimal(value.strip())
        except (InvalidOperation, ValueError, AttributeError):
            raise APIError(
                "invalid_setting_value",
                "setting_value must contain a valid decimal number.",
            )

        if not parsed.is_finite():
            raise APIError(
                "invalid_setting_value",
                "setting_value must be a finite decimal number.",
            )

        return str(parsed)

    if code == "boolean":
        normalized = value.strip().casefold()

        if normalized in ("true", "false"):
            return normalized

        raise APIError(
            "invalid_setting_value",
            "Boolean setting_value must be true or false.",
        )

    if code == "date":
        normalized = value.strip()

        try:
            parsed = date.fromisoformat(normalized)
        except (ValueError, AttributeError):
            raise APIError(
                "invalid_setting_value",
                "Date setting_value must use YYYY-MM-DD format.",
            )

        if parsed.isoformat() != normalized:
            raise APIError(
                "invalid_setting_value",
                "Date setting_value must use YYYY-MM-DD format.",
            )

        return parsed.isoformat()

    raise APIError(
        "unsupported_data_type",
        f"Unsupported system setting data type: {data_type.code}.",
    )


# --------------------------------------------------
# Input validation
# --------------------------------------------------

def validated_setting_values(payload, instance=None, partial=False):
    """Validate input and return model field values."""

    allowed_fields = {
        "setting_key",
        "setting_value",
        "data_type_id",
        "description",
    }

    unknown_fields = set(payload) - allowed_fields

    if unknown_fields:
        raise APIError(
            "unknown_fields",
            f"Unknown fields: {', '.join(sorted(unknown_fields))}.",
        )

    required_fields = ("setting_key", "setting_value")

    if not partial:
        for field in required_fields:
            if field not in payload:
                raise APIError("missing_field", f"{field} is required.")

    values = {}

    if "setting_key" in payload:
        setting_key = _validate_setting_key(payload["setting_key"])

        duplicate = SystemSetting.objects.filter(
            setting_key=setting_key
        )

        if instance is not None:
            duplicate = duplicate.exclude(pk=instance.pk)

        if duplicate.exists():
            raise APIError(
                "duplicate_setting_key",
                "A system setting with this key already exists.",
                409,
            )

        values["setting_key"] = setting_key

    elif instance is not None:
        values["setting_key"] = instance.setting_key

    if "data_type_id" in payload:
        raw_data_type_id = payload["data_type_id"]

        if raw_data_type_id is None:
            data_type = None
        else:
            data_type_id = _integer_value(
                raw_data_type_id,
                "data_type_id",
                minimum=1,
            )

            data_type = Constant.objects.filter(
                pk=data_type_id,
                category="data_type",
                is_active=True,
            ).first()

            if data_type is None:
                raise APIError(
                    "data_type_not_found",
                    "Active data type not found.",
                    404,
                )

        values["data_type"] = data_type

    elif instance is not None:
        data_type = instance.data_type
        values["data_type"] = data_type
    else:
        data_type = None
        values["data_type"] = None

    if "setting_value" in payload:
        setting_value = _validate_setting_value(payload["setting_value"])
        values["setting_value"] = _validate_typed_value(
            setting_value,
            data_type,
        )

    elif instance is not None:
        values["setting_value"] = _validate_typed_value(
            instance.setting_value,
            data_type,
        )

    if "description" in payload:
        values["description"] = _validate_description(
            payload["description"]
        )
    elif instance is not None:
        values["description"] = instance.description
    else:
        values["description"] = None

    return values


# --------------------------------------------------
# Create and update
# --------------------------------------------------

def save_system_setting(payload, person, instance=None, partial=False):
    """Create or update a system setting atomically."""

    values = validated_setting_values(
        payload,
        instance=instance,
        partial=partial,
    )

    updater = _admin_account_for_person(person)

    try:
        with transaction.atomic():
            if instance is None:
                setting = SystemSetting.objects.create(
                    **values,
                    updated_by=updater,
                )
            else:
                for field, value in values.items():
                    setattr(instance, field, value)

                instance.updated_by = updater
                instance.save()
                setting = instance

    except IntegrityError as error:
        raise APIError(
            "duplicate_setting_key",
            "A system setting with this key already exists.",
            409,
        ) from error

    return system_settings_queryset().get(pk=setting.pk)


# --------------------------------------------------
# Search
# --------------------------------------------------

def search_system_settings(queryset, search=""):
    """Filter settings by key, value, or description."""

    search = search.strip()

    if not search:
        return queryset

    return queryset.filter(
        Q(setting_key__icontains=search)
        | Q(setting_value__icontains=search)
        | Q(description__icontains=search)
        | Q(data_type__code__icontains=search)
        | Q(data_type__label__icontains=search)
    )

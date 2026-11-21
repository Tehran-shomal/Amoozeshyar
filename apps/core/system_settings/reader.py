"""Safe, uncached access to persisted system settings."""

from datetime import date
from decimal import Decimal, InvalidOperation

from django.db import DatabaseError


DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def _convert_setting_value(value, data_type_code=None, cast=None):
    """Convert a stored string to its declared or explicitly requested type."""
    converter = cast

    if converter is None:
        code = (data_type_code or "string").strip().casefold()
        converter = {
            "integer": int,
            "decimal": Decimal,
            "string": str,
            "boolean": bool,
            "date": date,
        }.get(code)

    if converter is None:
        raise ValueError("Unsupported system setting data type.")

    if converter is bool:
        normalized = value.strip().casefold()

        if normalized == "true":
            return True
        if normalized == "false":
            return False

        raise ValueError("Invalid boolean system setting.")

    if converter is date:
        normalized = value.strip()
        parsed = date.fromisoformat(normalized)

        if parsed.isoformat() != normalized:
            raise ValueError("Invalid date system setting.")

        return parsed

    if converter is Decimal:
        parsed = Decimal(value.strip())

        if not parsed.is_finite():
            raise ValueError("Non-finite decimal system setting.")

        return parsed

    if converter is str:
        return value

    return converter(value.strip())


def get_system_setting(key, default=None, cast=None):
    """
    Return a typed setting value.

    If the setting is missing, malformed, or inaccessible, return default.
    The model import is intentionally local to avoid circular imports.
    No cache is used.
    """
    try:
        from apps.core.models import SystemSetting

        setting = (
            SystemSetting.objects
            .select_related("data_type")
            .filter(setting_key=key)
            .first()
        )

        if setting is None:
            return default

        data_type_code = (
            setting.data_type.code
            if setting.data_type_id
            else None
        )

        return _convert_setting_value(
            setting.setting_value,
            data_type_code,
            cast,
        )

    except (
        DatabaseError,
        InvalidOperation,
        TypeError,
        ValueError,
        OverflowError,
        AttributeError,
    ):
        return default


def get_pagination_settings():
    """Return validated default and maximum API page sizes."""
    default_size = get_system_setting(
        "default_page_size",
        default=DEFAULT_PAGE_SIZE,
        cast=int,
    )

    maximum_size = get_system_setting(
        "max_page_size",
        default=MAX_PAGE_SIZE,
        cast=int,
    )

    if (
        not isinstance(default_size, int)
        or isinstance(default_size, bool)
        or default_size < 1
    ):
        default_size = DEFAULT_PAGE_SIZE

    if (
        not isinstance(maximum_size, int)
        or isinstance(maximum_size, bool)
        or maximum_size < 1
    ):
        maximum_size = MAX_PAGE_SIZE

    if default_size > maximum_size:
        default_size = maximum_size

    return default_size, maximum_size

"""Allowlisted JSON representation of Django forms for the React portal."""

from datetime import date, datetime, time
from decimal import Decimal

from django import forms


def _scalar(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, (date, datetime, time)):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return [_scalar(item) for item in value]
    raise TypeError(f"Unsupported form value: {type(value).__name__}")


def _field_type(widget):
    if isinstance(widget, forms.CheckboxSelectMultiple):
        return "checkbox-group"
    if isinstance(widget, forms.RadioSelect):
        return "radio"
    if isinstance(widget, forms.SelectMultiple):
        return "select-multiple"
    if isinstance(widget, forms.Select):
        return "select"
    if isinstance(widget, forms.Textarea):
        return "textarea"
    if isinstance(widget, forms.CheckboxInput):
        return "checkbox"
    return getattr(widget, "input_type", "text")


def _choices(field):
    if not hasattr(field, "choices"):
        return []

    result = []
    for value, label in field.choices:
        if isinstance(label, (list, tuple)):
            for nested_value, nested_label in label:
                result.append({"value": str(nested_value), "label": str(nested_label)})
        else:
            result.append({"value": str(value), "label": str(label)})
    return result


def _field_value(field, value):
    if isinstance(field, forms.FileField):
        return getattr(value, "name", None) if value else None
    return _scalar(value)


def serialize_form(form):
    """Return only user-facing field metadata, values, errors, and choices."""
    if form is None:
        return None
    if not isinstance(form, forms.BaseForm):
        raise TypeError("Expected a Django form instance.")

    fields = []
    for name, field in form.fields.items():
        bound = form[name]
        attrs = field.widget.attrs
        fields.append({
            "name": name,
            "id": bound.id_for_label or "",
            "label": str(bound.label),
            "type": _field_type(field.widget),
            "required": bool(field.required),
            "disabled": bool(field.disabled),
            "multiple": bool(getattr(field.widget, "allow_multiple_selected", False)),
            "help_text": str(field.help_text) if field.help_text else "",
            "placeholder": str(attrs["placeholder"]) if attrs.get("placeholder") else "",
            "value": _field_value(field, bound.value()),
            "errors": [str(error) for error in bound.errors],
            "choices": _choices(field),
        })

    return {
        "fields": fields,
        "non_field_errors": [str(error) for error in form.non_field_errors()],
    }

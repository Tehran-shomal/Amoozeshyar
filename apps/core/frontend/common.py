"""ابزارهای مشترک نمایش؛ هیچ دادهٔ دانشجویی نمونه در این فایل وجود ندارد."""
from datetime import date, datetime
from decimal import Decimal
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.core import models as m
from apps.core.enrollment.services import INACTIVE_ENROLLMENT_CODES, active_enrollments


def display(value):
    if value is None or value == "":
        return "—"
    if isinstance(value, datetime):
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        return value.strftime("%Y-%m-%d %H:%M")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return f"{value:,.2f}"
    if isinstance(value, bool):
        return "بله" if value else "خیر"
    return str(value)


def term_code_display(term):
    """Keep the stored term key intact while showing the PDF's compact code."""
    if term is None:
        return "—"
    code = term.term_code
    return code[1:] if len(code) == 5 and code.startswith("1") else code


def table(title, columns, rows):
    return {"title": title, "columns": columns, "rows": [
        {"cells": [display(cell) for cell in row]} for row in rows
    ]}


def enrollment_rows(student, term=None):
    rows = m.Enrollment.objects.filter(student=student).select_related(
        "status", "offering__lesson", "offering__teacher__person", "offering__term",
        "offering__classroom", "offering__day_of_week"
    )
    return rows.filter(offering__term=term) if term else rows.none()


def active_enrollment_rows(student, term=None):
    """Apply the same inactive status rules used by the enrollment API."""
    return active_enrollments(enrollment_rows(student, term))


def enrollments_table(student, term, action=None, queryset=None):
    result = table("دروس ثبت‌نام‌شده", ["کد درس", "درس", "استاد", "واحد", "زمان", "وضعیت"], [])
    rows = queryset if queryset is not None else enrollment_rows(student, term)
    for row in rows:
        offer = row.offering
        item = {"cells": [offer.lesson.lesson_code, offer.lesson.title,
            offer.teacher.person.full_name, offer.lesson.theory_units + offer.lesson.practical_units,
            f"{offer.day_of_week or ''} {offer.start_time:%H:%M}–{offer.end_time:%H:%M}", display(row.status)]}
        if action and (not row.status or row.status.code.casefold() not in INACTIVE_ENROLLMENT_CODES):
            item.update(action=action, id=row.pk, action_label="حذف درس")
        result["rows"].append(item)
    result["has_actions"] = bool(action)
    return result


class OwnedModelForm(forms.ModelForm):
    """مالکیت و وضعیت از سرور تعیین می‌شوند، نه از فیلدهای ارسالی مرورگر."""
    owner_field = None
    status_field = None
    status_category = "review_status"

    def __init__(self, *args, student, person, term=None, **kwargs):
        self.student, self.person, self.term = student, person, term
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(attrs={"type": "date"})
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = "انتخاب کنید"
        if "enrollment" in self.fields:
            self.fields["enrollment"].queryset = enrollment_rows(student, term)

    def clean(self):
        data = super().clean()
        if self.owner_field:
            setattr(self.instance, self.owner_field, self.student)
        if self.status_field:
            # Constants must already exist in the backend/seed; never create them while rendering.
            status = m.Constant.objects.filter(category=self.status_category, code="pending", is_active=True).first()
            if not status:
                raise ValidationError("وضعیت اولیهٔ درخواست در سامانه تعریف نشده؛ با پشتیبانی تماس بگیرید.")
            setattr(self.instance, self.status_field, status)
        return data


def form_for(form_class, request, student, term):
    if student is None:
        return None
    return form_class(request.POST if request.method == "POST" else None,
                      student=student, person=request.user, term=term)

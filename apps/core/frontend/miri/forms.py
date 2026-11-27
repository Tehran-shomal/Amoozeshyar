"""Faculty communication and support forms owned by Miri."""

from django import forms
from django.db import transaction

from apps.core import models as m
from ..common import OwnedModelForm, active_enrollment_rows


RATING_CHOICES = tuple((value, str(value)) for value in range(1, 6))
EVALUATION_FORM_FIELDS = (
    ("overall_rating", "امتیاز کلی"),
    ("teaching_quality", "کیفیت تدریس"),
    ("behavior", "رفتار استاد"),
)
EVALUATION_CRITERIA = (
    ("teaching_quality", "کیفیت تدریس"),
    ("behavior", "رفتار استاد"),
)


class SurveyForm(OwnedModelForm):
    overall_rating = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=int,
        label="امتیاز کلی",
        widget=forms.RadioSelect(attrs={"class": "evaluation-rating-input"}),
    )
    teaching_quality = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=int,
        required=False,
        label="کیفیت تدریس",
        widget=forms.RadioSelect(attrs={"class": "evaluation-rating-input"}),
    )
    behavior = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=int,
        required=False,
        label="رفتار استاد",
        widget=forms.RadioSelect(attrs={"class": "evaluation-rating-input"}),
    )

    class Meta:
        model = m.TeacherSurvey
        fields = [
            "enrollment",
            "overall_rating",
            "teaching_quality",
            "behavior",
            "comment",
        ]
        labels = {"enrollment": "درس و استاد"}
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, selected_enrollment=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_enrollment = selected_enrollment
        self.fields["enrollment"].queryset = active_enrollment_rows(
            self.student, self.term
        ).exclude(
            teacher_surveys__isnull=False
        )
        if selected_enrollment is not None:
            self.fields["enrollment"].initial = selected_enrollment.pk
            self.fields["enrollment"].widget = forms.HiddenInput()
        self.fields["comment"].required = False

    def clean(self):
        data = super().clean()
        enrollment = data.get("enrollment")
        if enrollment and m.TeacherSurvey.objects.filter(enrollment=enrollment).exists():
            self.add_error("enrollment", "ارزشیابی این درس قبلاً ثبت شده است.")
        return data

    @transaction.atomic
    def save(self, commit=True):
        m.Enrollment.objects.select_for_update().get(pk=self.instance.enrollment_id)
        if m.TeacherSurvey.objects.filter(enrollment=self.instance.enrollment).exists():
            raise forms.ValidationError("ارزشیابی این درس قبلاً ثبت شده است.")
        return super().save(commit=commit)


class MessageForm(OwnedModelForm):
    class Meta:
        model = m.Communication
        fields = ["receiver", "subject", "message_body"]
        labels = {"receiver": "استاد دریافت‌کننده"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        teacher_ids = active_enrollment_rows(self.student, self.term).filter(
            offering__is_active=True
        ).values_list(
            "offering__teacher__person_id", flat=True
        ).distinct()
        self.fields["receiver"].queryset = m.UserAccount.objects.filter(
            person_id__in=teacher_ids, is_active=True, role__is_active=True
        ).select_related("person").order_by("person__last_name", "person__first_name", "pk")
        self.fields["receiver"].label_from_instance = lambda account: account.person.full_name

    def clean(self):
        data = super().clean()
        sender = m.UserAccount.objects.filter(
            person=self.person, is_active=True, role__is_active=True
        ).order_by("pk").first()
        if not sender:
            raise forms.ValidationError("حساب دانشجویی فعال برای ارسال پیام وجود ندارد.")
        self.instance.sender = sender
        return data


class SupportForm(OwnedModelForm):
    class Meta:
        model = m.Ticket
        fields = ["category", "subject", "content"]
        labels = {"content": "شرح و شناسهٔ مرتبط"}
        widgets = {"content": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = m.TicketCategory.objects.filter(is_active=True)

    def clean(self):
        data = super().clean()
        self.instance.creator = self.person
        return data

    def save(self, commit=True):
        self.instance.status = m.Constant.objects.filter(
            category="ticket_status", code="open", is_active=True
        ).first()
        return super().save(commit=commit)

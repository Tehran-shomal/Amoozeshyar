"""Request forms owned by Shahsavand and Omid in academic services."""

from django import forms
from django.db import transaction

from apps.core import models as m
from ..common import OwnedModelForm


class GuestRequestForm(OwnedModelForm):
    owner_field = "student"
    status_field = "review_status"

    class Meta:
        model = m.TransferRequest
        fields = ["destination_university"]


class GraduationReviewForm(OwnedModelForm):
    """Register a graduation review in the existing student-service model."""
    owner_field = "service_requester"
    status_field = "service_decision_state"

    class Meta:
        model = m.StudentServiceRequest
        fields = ["service_request_kind", "service_request_data"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service_request_kind"].queryset = m.Constant.objects.filter(
            category="service_request_type", code="certificate", is_active=True)

    def clean_service_request_data(self):
        details = self.cleaned_data.get("service_request_data", "").strip()
        return "درخواست بررسی فارغ‌التحصیلی" + (f"\n{details}" if details else "")


class SurveyForm(OwnedModelForm):
    class Meta:
        model = m.TeacherSurvey
        fields = ["enrollment", "overall_rating", "teaching_quality", "behavior", "comment"]
        labels = {"enrollment": "درس و استاد"}
        widgets = {name: forms.NumberInput(attrs={"min": 1, "max": 5})
                   for name in ["overall_rating", "teaching_quality", "behavior"]}

    def clean(self):
        data = super().clean()
        enrollment = data.get("enrollment")
        if enrollment and m.TeacherSurvey.objects.filter(enrollment=enrollment).exists():
            self.add_error("enrollment", "ارزشیابی این درس قبلاً ثبت شده است.")
        return data

    @transaction.atomic
    def save(self, commit=True):
        # Lock the owned enrollment so repeated submits cannot create duplicate surveys.
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
        teacher_ids = m.Enrollment.objects.filter(student=self.student).values_list(
            "offering__teacher__person_id", flat=True)
        self.fields["receiver"].queryset = m.UserAccount.objects.filter(
            person_id__in=teacher_ids, is_active=True, role__is_active=True)
        self.fields["receiver"].label_from_instance = lambda account: account.person.full_name

    def clean(self):
        data = super().clean()
        sender = m.UserAccount.objects.filter(
            person=self.person, is_active=True, role__is_active=True).order_by("pk").first()
        if not sender:
            raise forms.ValidationError("حساب دانشجویی فعال برای ارسال پیام وجود ندارد.")
        self.instance.sender = sender
        return data


class ServiceRequestForm(OwnedModelForm):
    owner_field = "service_requester"
    status_field = "service_decision_state"

    class Meta:
        model = m.StudentServiceRequest
        fields = ["service_request_kind", "service_request_data"]


class CertificateForm(ServiceRequestForm):
    """Use an existing certificate request type; never create a lookup value here."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service_request_kind"].queryset = m.Constant.objects.filter(
            category="service_request_type", code="certificate", is_active=True)


class SupportForm(OwnedModelForm):
    class Meta:
        model = m.Ticket
        fields = ["category", "subject", "content"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = m.TicketCategory.objects.filter(is_active=True)

    def clean(self):
        data = super().clean()
        self.instance.creator = self.person
        return data

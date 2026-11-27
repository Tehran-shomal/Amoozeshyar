"""Student request forms owned by Shahsvand."""

from django import forms

from apps.core import models as m
from ..common import OwnedModelForm


class InternshipForm(OwnedModelForm):
    owner_field = "student"
    status_field = "status"

    class Meta:
        model = m.Internship
        fields = ["request_type", "company_name", "intern_start_date", "duration_hours"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["request_type"].queryset = m.Constant.objects.filter(
            category="internship_request_type", is_active=True
        )
        self.fields["request_type"].required = True

    def clean_duration_hours(self):
        value = self.cleaned_data["duration_hours"]
        if value <= 0:
            raise forms.ValidationError("مدت کارآموزی باید بیشتر از صفر باشد.")
        return value


class GuestRequestForm(OwnedModelForm):
    owner_field = "student"
    status_field = "review_status"

    class Meta:
        model = m.TransferRequest
        fields = ["destination_university"]


class ServiceRequestForm(OwnedModelForm):
    owner_field = "service_requester"
    status_field = "service_decision_state"

    class Meta:
        model = m.StudentServiceRequest
        fields = ["service_request_kind", "service_request_data"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service_request_kind"].queryset = m.Constant.objects.filter(
            category="service_request_type", is_active=True
        )
        self.fields["service_request_kind"].required = True


class CertificateForm(ServiceRequestForm):
    """Restrict certificate requests to an explicitly configured active lookup."""

    def __init__(self, *args, allowed_codes=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service_request_kind"].queryset = m.Constant.objects.filter(
            category="service_request_type", code__in=allowed_codes, is_active=True
        )

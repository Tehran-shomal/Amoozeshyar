from django import forms
from apps.core import models as m
from ..common import OwnedModelForm


class InternshipForm(OwnedModelForm):
    owner_field = "student"
    status_field = "status"

    class Meta:
        model = m.Internship
        fields = ["request_type", "company_name", "intern_start_date", "duration_hours"]

    def clean_duration_hours(self):
        value = self.cleaned_data["duration_hours"]
        if value <= 0:
            raise forms.ValidationError("مدت کارآموزی باید بیشتر از صفر باشد.")
        return value


class SettingsForm(OwnedModelForm):
    class Meta:
        model = m.Person
        fields = ["email", "address", "is_notification_enabled", "preferred_language"]

    def __init__(self, *args, **kwargs):
        kwargs["instance"] = kwargs["person"]
        super().__init__(*args, **kwargs)

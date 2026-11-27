"""Account forms owned by Mobina."""

from django import forms

from apps.core import models as m
from ..common import OwnedModelForm


class SettingsForm(OwnedModelForm):
    class Meta:
        model = m.Person
        fields = ["email", "address", "is_notification_enabled", "preferred_language"]

    def __init__(self, *args, person, **kwargs):
        kwargs["instance"] = person
        super().__init__(*args, person=person, **kwargs)
        self.fields["email"].label = "رایانامه"
        self.fields["email"].widget.attrs.update({"autocomplete": "email", "dir": "ltr"})
        self.fields["address"].label = "نشانی پستی"
        self.fields["address"].widget.attrs.update({"autocomplete": "street-address"})
        self.fields["is_notification_enabled"].label = "ترجیح کلی دریافت اعلان‌ها"
        self.fields["preferred_language"].label = "زبان رابط کاربری"
        self.fields["preferred_language"].queryset = m.Constant.objects.filter(
            category="language"
        ).order_by("code")
        self.fields["preferred_language"].empty_label = "انتخاب زبان"
        self.fields["preferred_language"].widget = forms.RadioSelect()

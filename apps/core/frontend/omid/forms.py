"""Academic record forms owned by Omid."""

from django.utils import timezone

from apps.core import models as m
from ..common import OwnedModelForm


class GradeAppealForm(OwnedModelForm):
    status_field = "appeal_status"
    status_category = "appeal_status"

    class Meta:
        model = m.GradeAppeal
        fields = ["enrollment", "appeal_reason"]
        labels = {"enrollment": "درس", "appeal_reason": "دلیل اعتراض"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # An appeal is actionable only for an enrollment with a recorded grade.
        self.fields["enrollment"].queryset = self.fields["enrollment"].queryset.filter(
            grades__score__isnull=False
        ).distinct()

    def clean(self):
        data = super().clean()
        self.instance.appeal_date = timezone.now()
        return data

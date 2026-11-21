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

    def clean(self):
        data = super().clean()
        self.instance.appeal_date = timezone.now()
        return data

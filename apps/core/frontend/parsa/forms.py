from apps.core import models as m
from ..common import OwnedModelForm


class ScholarshipForm(OwnedModelForm):
    owner_field = "scholarship_applicant"
    status_field = "scholarship_status"

    class Meta:
        model = m.ScholarshipApplication
        fields = ["scholarship_type", "scholarship_reason"]
        labels = {"scholarship_type": "نوع تسهیلات", "scholarship_reason": "دلیل درخواست"}

from django.db import models


class ProposalStatusChoices(models.TextChoices):
    PENDING = "pending", "در انتظار بررسی"
    APPROVED = "approved", "تأیید شده"
    REJECTED = "rejected", "رد شده"


class CounselingStatusChoices(models.TextChoices):
    PENDING = "pending", "در انتظار برگزاری"
    COMPLETED = "completed", "برگزار شده"
    CANCELLED = "cancelled", "لغو شده"


class ScholarshipStatusChoices(models.TextChoices):
    PENDING = "pending", "در انتظار بررسی"
    APPROVED = "approved", "تأیید شده"
    REJECTED = "rejected", "رد شده"

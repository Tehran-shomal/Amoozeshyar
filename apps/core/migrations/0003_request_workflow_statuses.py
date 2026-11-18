from django.db import migrations


STATUS_VALUES = {
    "review_status": (
        ("submitted", "ثبت‌شده"),
        ("in_review", "در حال بررسی"),
        ("approved", "تأیید"),
        ("rejected", "رد"),
    ),
    "proposal_status": (
        ("submitted", "ثبت‌شده"),
        ("in_review", "در حال بررسی"),
        ("approved", "تأیید"),
        ("rejected", "رد"),
    ),
    "appeal_status": (
        ("submitted", "ثبت‌شده"),
        ("in_review", "در حال بررسی"),
        ("approved", "تأیید"),
        ("rejected", "رد"),
    ),
    "thesis_review_status": (
        ("submitted", "ثبت‌شده"),
        ("in_review", "در حال بررسی"),
        ("approved", "تأیید"),
        ("rejected", "رد"),
    ),
}


def add_request_workflow_statuses(apps, schema_editor):
    Constant = apps.get_model("core", "Constant")
    for category, values in STATUS_VALUES.items():
        for code, label in values:
            Constant.objects.get_or_create(
                category=category,
                code=code,
                defaults={"label": label, "is_active": True},
            )


class Migration(migrations.Migration):
    dependencies = [("core", "0002_enrollment_statuses")]

    operations = [
        migrations.RunPython(add_request_workflow_statuses, migrations.RunPython.noop)
    ]

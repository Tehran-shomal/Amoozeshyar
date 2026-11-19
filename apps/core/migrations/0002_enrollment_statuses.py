from django.db import migrations


STATUSES = (
    ("registered", "ثبت‌نام‌شده"),
    ("dropped", "حذف‌شده"),
)


def add_enrollment_statuses(apps, schema_editor):
    Constant = apps.get_model("core", "Constant")
    for code, label in STATUSES:
        Constant.objects.get_or_create(
            category="enrollment_status",
            code=code,
            defaults={"label": label, "is_active": True},
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]

    operations = [migrations.RunPython(add_enrollment_statuses, migrations.RunPython.noop)]

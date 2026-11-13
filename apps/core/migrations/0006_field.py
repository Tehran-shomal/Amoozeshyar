import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_faculty_department"),
    ]

    operations = [
        migrations.AddField(
            model_name="field",
            name="department",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="fields",
                to="core.department",
                verbose_name="گروه آموزشی",
            ),
        ),
        migrations.AddField(
            model_name="field",
            name="field_name",
            field=models.CharField(max_length=150, verbose_name="نام رشته"),
        ),
        migrations.AddField(
            model_name="field",
            name="field_code",
            field=models.CharField(max_length=20, verbose_name="کد رشته"),
        ),
        migrations.AddField(
            model_name="field",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="فعال"),
        ),
        migrations.AddField(
            model_name="field",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت"),
        ),
        migrations.AlterModelOptions(
            name="field",
            options={
                "ordering": ["field_name"],
                "verbose_name": "رشته تحصیلی",
                "verbose_name_plural": "رشته‌های تحصیلی",
            },
        ),
        migrations.AddConstraint(
            model_name="field",
            constraint=models.UniqueConstraint(
                fields=("department", "field_code"),
                name="unique_field_code_per_department",
            ),
        ),
    ]

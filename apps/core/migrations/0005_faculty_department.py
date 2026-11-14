import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_alter_role_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="Faculty",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("faculty_name", models.CharField(max_length=150, verbose_name="نام دانشکده")),
                (
                    "faculty_code",
                    models.CharField(max_length=20, unique=True, verbose_name="کد دانشکده"),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")),
            ],
            options={
                "verbose_name": "دانشکده",
                "verbose_name_plural": "دانشکده‌ها",
                "ordering": ["faculty_name"],
            },
        ),
        migrations.AddField(
            model_name="department",
            name="faculty",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="departments",
                to="core.faculty",
                verbose_name="دانشکده",
            ),
        ),
        migrations.AddField(
            model_name="department",
            name="department_name",
            field=models.CharField(max_length=150, verbose_name="نام گروه آموزشی"),
        ),
        migrations.AddField(
            model_name="department",
            name="department_code",
            field=models.CharField(max_length=20, verbose_name="کد گروه آموزشی"),
        ),
        migrations.AddField(
            model_name="department",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="فعال"),
        ),
        migrations.AddField(
            model_name="department",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت"),
        ),
        migrations.AlterModelOptions(
            name="department",
            options={
                "ordering": ["department_name"],
                "verbose_name": "گروه آموزشی",
                "verbose_name_plural": "گروه‌های آموزشی",
            },
        ),
        migrations.AddConstraint(
            model_name="department",
            constraint=models.UniqueConstraint(
                fields=("faculty", "department_code"),
                name="unique_department_code_per_faculty",
            ),
        ),
    ]

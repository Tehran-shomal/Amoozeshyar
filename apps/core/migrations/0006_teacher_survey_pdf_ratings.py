from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_person_failed_login_count_person_locked_until"),
    ]

    operations = [
        migrations.AddField(
            model_name="teachersurvey",
            name="content_mastery_rating",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="تسلط استاد بر محتوای درس"
            ),
        ),
        migrations.AddField(
            model_name="teachersurvey",
            name="explanation_clarity_rating",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="بیان روشن و قابل فهم مطالب"
            ),
        ),
        migrations.AddField(
            model_name="teachersurvey",
            name="class_organization_rating",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="نظم در برگزاری کلاس‌ها"
            ),
        ),
        migrations.AddField(
            model_name="teachersurvey",
            name="student_interaction_rating",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="پاسخ‌گویی و تعامل با دانشجو"
            ),
        ),
        migrations.AddField(
            model_name="teachersurvey",
            name="assessment_alignment_rating",
            field=models.PositiveSmallIntegerField(
                blank=True, null=True, verbose_name="تناسب تکالیف و شیوه ارزشیابی"
            ),
        ),
        migrations.AddConstraint(
            model_name="teachersurvey",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(content_mastery_rating__isnull=True)
                    | models.Q(content_mastery_rating__gte=1, content_mastery_rating__lte=5)
                ),
                name="ts_mastery_1_5",
            ),
        ),
        migrations.AddConstraint(
            model_name="teachersurvey",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(explanation_clarity_rating__isnull=True)
                    | models.Q(explanation_clarity_rating__gte=1, explanation_clarity_rating__lte=5)
                ),
                name="ts_clarity_1_5",
            ),
        ),
        migrations.AddConstraint(
            model_name="teachersurvey",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(class_organization_rating__isnull=True)
                    | models.Q(class_organization_rating__gte=1, class_organization_rating__lte=5)
                ),
                name="ts_organization_1_5",
            ),
        ),
        migrations.AddConstraint(
            model_name="teachersurvey",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(student_interaction_rating__isnull=True)
                    | models.Q(student_interaction_rating__gte=1, student_interaction_rating__lte=5)
                ),
                name="ts_interaction_1_5",
            ),
        ),
        migrations.AddConstraint(
            model_name="teachersurvey",
            constraint=models.CheckConstraint(
                condition=(
                    models.Q(assessment_alignment_rating__isnull=True)
                    | models.Q(assessment_alignment_rating__gte=1, assessment_alignment_rating__lte=5)
                ),
                name="ts_assessment_1_5",
            ),
        ),
    ]

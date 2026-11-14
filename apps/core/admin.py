
from django.contrib import admin
from .models import Exam, Classroom, GradeAppeal


# پنل مدیریت امتحانات
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "offering_id",
        "exam_date",
        "exam_type",
    )

    list_filter = (
        "exam_type",
        "exam_date",
    )

    search_fields = (
        "exam_type",
    )

    ordering = ("exam_date",)
    date_hierarchy = "exam_date"


# پنل مدیریت کلاس‌ها
@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "building_name",
        "room_number",
        "capacity",
        "classroom_type",
    )

    list_filter = (
        "classroom_type",
    )

    search_fields = (
        "building_name",
        "room_number",
        "classroom_type",
    )

    ordering = ("building_name", "room_number")


# پنل مدیریت اعتراض به نمره
@admin.register(GradeAppeal)
class GradeAppealAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "enrollment_id",
        "appeal_date",
        "appeal_status",
    )

    list_filter = (
        "appeal_status",
        "appeal_date",
    )

    search_fields = (
        "appeal_reason",
    )

    ordering = ("-appeal_date",)
    date_hierarchy = "appeal_date"

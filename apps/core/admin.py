import csv
from django.contrib import admin
from django.db.models import Count
from django.http import HttpResponse
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm

from .models import (
    CourseOffering,
    Department,
    Enrollment,
    Faculty,
    Field,
    Lesson,
    OnlineClass,
    Payment,
    Prerequisite,
    Role,
    Ticket,
    Person,
    Teacher,
    Student,
    Term,
    LessonGroups,
    ParkingPasses
)


# ----------------------------------------------------------------------
# مدیریت کلاس‌های آنلاین (OnlineClass)
# ----------------------------------------------------------------------
@admin.register(OnlineClass)
class OnlineClassAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "teacher",
        "offering",
        "start_at",
        "end_at",
        "duration",
        "is_ongoing",
    )

    list_filter = (
        "start_at",
        "end_at",
    )

    search_fields = ("title",)

    ordering = ("start_at",)

    readonly_fields = (
        "duration",
        "is_ongoing",
    )


# ----------------------------------------------------------------------
# مدیریت دانشکده‌ها
# ----------------------------------------------------------------------
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("faculty_code", "faculty_name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("faculty_code", "faculty_name")
    ordering = ("faculty_name",)
    list_per_page = 20


# ----------------------------------------------------------------------
# مدیریت دپارتمان‌ها
# ----------------------------------------------------------------------
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        "department_code",
        "department_name",
        "faculty",
        "is_active",
        "created_at",
    )
    list_filter = ("faculty", "is_active")
    search_fields = (
        "department_code",
        "department_name",
        "faculty__faculty_name",
    )
    list_select_related = ("faculty",)
    ordering = ("department_name",)
    list_per_page = 20


# ----------------------------------------------------------------------
# مدیریت رشته‌ها
# ----------------------------------------------------------------------
@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = (
        "field_code",
        "field_name",
        "department",
        "is_active",
        "created_at",
    )
    list_filter = ("department__faculty", "department", "is_active")
    search_fields = (
        "field_code",
        "field_name",
        "department__department_name",
        "department__faculty__faculty_name",
    )
    list_select_related = ("department", "department__faculty")
    ordering = ("field_name",)
    list_per_page = 20


# ----------------------------------------------------------------------
# مدیریت نقش‌ها
# ----------------------------------------------------------------------
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "role_name",
        "description",
        "created_at",
        "is_active",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("role_name", "description")
    ordering = ("role_name",)
    list_per_page = 10


# ----------------------------------------------------------------------
# مدیریت ثبت‌نام‌ها
# ----------------------------------------------------------------------
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "offering",
        "enrollment_type",
        "status",
        "enrollment_date",
        "drop_date",
    )
    list_filter = (
        "status",
        "enrollment_type",
        "enrollment_date",
    )
    search_fields = ("student__name",)
    list_select_related = ("student", "offering")
    list_per_page = 10


# ----------------------------------------------------------------------
# مدیریت پیش‌نیازها
# ----------------------------------------------------------------------
@admin.register(Prerequisite)
class PrerequisiteAdmin(admin.ModelAdmin):
    list_display = (
        "prereq_id",
        "lesson",
        "prerequisite_lesson",
        "prerequisite_type",
        "created_at",
    )
    list_filter = (
        "prerequisite_type__category",
        "prerequisite_type",
        "created_at",
    )
    search_fields = (
        "lesson__title",
        "lesson__lesson_code",
        "prerequisite_lesson__title",
        "prerequisite_lesson__lesson_code",
        "prerequisite_type__label",
    )
    list_select_related = (
        "lesson",
        "prerequisite_lesson",
        "prerequisite_type",
    )
    list_per_page = 10


# ----------------------------------------------------------------------
# مدیریت تیکت‌ها (Ticket)
# ----------------------------------------------------------------------
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "creator",
        "creator_role",
        "category",
        "status",
        "assigned_to",
        "is_assigned",
        "created_at",
    )

    list_filter = (
        "creator_role",
        "category",
        "status",
        "created_at",
    )

    search_fields = (
        "subject",
        "content",
        "creator__username",
        "creator__first_name",
        "creator__last_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "is_closed",
        "is_assigned",
    )

    ordering = ("-created_at",)


# ----------------------------------------------------------------------
# مدیریت درس‌ها
# ----------------------------------------------------------------------
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "lesson_code",
        "title",
        "lesson_type",
        "department",
        "practical_units",
        "theory_units",
        "is_active",
    )
    search_fields = ("lesson_code", "title")
    list_filter = ("is_active", "lesson_type", "department")
    ordering = ("title",)
    list_per_page = 25


# ----------------------------------------------------------------------
# مدیریت پرداخت‌ها
# ----------------------------------------------------------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_code",
        "student",
        "term",
        "amount",
        "payment_date",
        "status",
    )
    search_fields = ("tracking_code",)
    list_filter = ("status", "term")
    ordering = ("-created_at",)
    list_per_page = 25


# ----------------------------------------------------------------------
# مدیریت ارائه درس‌ها
# ----------------------------------------------------------------------
@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = (
        "lesson",
        "teacher",
        "term",
        "day_of_week",
        "start_time",
        "end_time",
        "capacity",
        "remaining_capacity",
        "is_active",
    )
    search_fields = ("lesson__lesson_code", "lesson__title")
    list_filter = ("day_of_week", "term", "is_active", "classroom")
    ordering = ("start_time",)
    list_per_page = 25


# ----------------------------------------------------------------------
# مدیریت اشخاص
# ----------------------------------------------------------------------
class PersonCreationForm(UserCreationForm):
    class Meta:
        model = Person
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "national_id",
            "birth_date",
            "birth_place",
        )


@admin.register(Person)
class PersonAdmin(UserAdmin):
    add_form = PersonCreationForm

    list_display = (
        "username",
        "full_name",
        "email",
        "national_id",
        "gender",
        "is_active",
        "is_staff",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "national_id",
    )

    list_filter = (
        "gender",
        "preferred_language",
        "is_active",
        "is_staff",
    )

    ordering = ("last_name", "first_name")

    readonly_fields = ("updated_at", "age", "full_name")

    fieldsets = (
        (
            "اطلاعات ورود",
            {
                "fields": ("username", "password"),
            },
        ),
        (
            "اطلاعات شخصی",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "national_id",
                    "birth_date",
                    "birth_place",
                    "gender",
                    "address",
                    "profile_image_path",
                    "preferred_language",
                    "is_notification_enabled",
                    "age",
                    "full_name",
                ),
            },
        ),
        (
            "دسترسی‌ها",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            "اطلاعات سیستمی",
            {
                "fields": ("last_login", "date_joined", "updated_at"),
            },
        ),
    )

    add_fieldsets = (
        (
            "ایجاد شخص جدید",
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                    "national_id",
                    "birth_date",
                    "birth_place",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


# ----------------------------------------------------------------------
# مدیریت اساتید
# ----------------------------------------------------------------------
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):

    list_display = (
        "teacher_code",
        "person",
        "department",
        "academic_rank",
        "hire_date",
        "years_of_service",
    )

    search_fields = (
        "teacher_code",
        "person__first_name",
        "person__last_name",
        "person__national_id",
    )

    list_filter = (
        "department",
        "academic_rank",
        "hire_date",
    )

    list_select_related = (
        "person",
        "department",
        "academic_rank",
    )

    ordering = ("teacher_code",)


# ----------------------------------------------------------------------
# مدیریت دانشجویان
# ----------------------------------------------------------------------
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        "student_code",
        "person",
        "field",
        "educational_level",
        "status",
        "total_gpa",
        "tuition_debt",
        "is_on_probation",
    )

    search_fields = (
        "student_code",
        "person__first_name",
        "person__last_name",
        "person__national_id",
    )

    list_filter = (
        "educational_level",
        "status",
        "admission_type",
        "field",
    )

    list_select_related = (
        "person",
        "field",
        "educational_level",
        "status",
        "admission_type",
    )

    ordering = ("student_code",)

    readonly_fields = (
        "is_on_probation",
        "can_register_courses",
        "max_allowed_units",
        "remaining_terms",
    )


# ----------------------------------------------------------------------
# مدیریت ترم
# ----------------------------------------------------------------------
@admin.register(Term)
class TermAdmin(admin.ModelAdmin):

    list_display = (
        "term_code",
        "semester",
        "academic_year",
        "start_date",
        "end_date",
        "is_active",
    )

    search_fields = (
        "term_code",
        "academic_year",
    )

    list_filter = (
        "semester",
        "academic_year",
        "is_active",
    )

    ordering = ("-start_date",)

    list_per_page = 20

    @admin.register(ParkingPasses)
    class ParkingPassesAdmin(admin.ModelAdmin):
        list_display = (
            "parking_pass_code",
            "expiration_date",
            "charge",
            "owner",
            "remaining_days"
        )

        search_fields = (
            "parking_pass_code",
            "owner",
            "expiration_date"
        )

        list_filter = (
            "expiration_date",
            "charge",
            "remaining_days"
        )

        ordering = ("remaining_days")

        list_per_page = 50

    @admin.register(LessonGroups)
    class LessonGroupsAdmin(admin.ModelAdmin):
        list_display = (
            "name",
            "created_at",
            "is_active",
            "members",
            "teacher"
        )

        search_fields = (
            "members",
            "name",
            "teacher"
        )

        list_filter = (
            "is_active",
            "created_at"
        )

        ordering = ("created_at")

        list_per_page = 50
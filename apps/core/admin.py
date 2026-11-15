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
    Curriculum,
    Communication,
    SystemSetting,
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
# مدیریت چارت درسی (Curriculum)  
# ----------------------------------------------------------------------
@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    # ستون‌هایی که در لیست اصلی نمایش داده می‌شوند
    list_display = (
        "curriculum_id",
        "field",
        "lesson",
        "requirement_type",
        "recommended_term",
        "calculated_units",
        "is_active",
    )
    
    # فیلترهای سمت راست صفحه (بر اساس رشته، دانشکده، نوع درس و ...)
    list_filter = (
        "is_active",
        "field__department__faculty",  # فیلتر بر اساس دانشکده
        "field__department",           # فیلتر بر اساس گروه آموزشی
        "field",                       # فیلتر بر اساس رشته
        "requirement_type",            # اجباری/اختیاری
        "recommended_term",            # ترم پیشنهادی
    )
    
    # فیلدهای قابل جستجو (با کد و نام درس و رشته)
    search_fields = (
        "field__field_name",
        "field__field_code",
        "lesson__title",
        "lesson__lesson_code",
    )
    
    # بهینه‌سازی دیتابیس برای جلوگیری از کندی (JOIN یکجا)
    list_select_related = ("field", "lesson", "requirement_type")
    
    # مرتب‌سازی پیش‌فرض
    ordering = ("field", "recommended_term")
    
    # تعداد آیتم در هر صفحه
    list_per_page = 25
    
    # تعداد ستون‌های قابل ویرایش مستقیم از لیست
    list_editable = ("is_active", "calculated_units", "recommended_term")
    
    # اکشن‌های گروهی (فعال/غیرفعال کردن دسته‌جمعی)
    actions = ["make_active", "make_inactive"]

    @admin.action(description="فعال کردن چارت‌های انتخاب شده")
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} چارت درسی با موفقیت فعال شدند.")

    @admin.action(description="غیرفعال کردن چارت‌های انتخاب شده")
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} چارت درسی با موفقیت غیرفعال شدند.")


# ----------------------------------------------------------------------
# مدیریت ارتباطات و مکاتبات (Communication)   
# ----------------------------------------------------------------------
@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = (
        "communication_id",
        "sender",
        "receiver",
        "subject",
        "communication_type",
        "status",
        "is_read_display",      # نمایش وضعیت خوانده شدن
        "sent_at",
    )
    
    # فیلترها
    list_filter = (
        "is_read",
        "communication_type",
        "status",
        "sent_at",
    )
    
    # جستجو بر اساس موضوع، متن پیام و نام فرستنده/گیرنده
    search_fields = (
        "subject",
        "message_body",
        "sender__username",
        "receiver__username",
    )
    
    list_select_related = ("sender", "receiver", "communication_type", "status")
    ordering = ("-sent_at",)
    list_per_page = 25
    
    # اضافه کردن نوار زمانی بالای صفحه (برای فیلتر سریع بر اساس تاریخ)
    date_hierarchy = "sent_at"
    
    # اکشن‌های گروهی برای مدیریت وضعیت خوانده شدن
    actions = ["mark_as_read", "mark_as_unread"]

    # نمایش وضعیت خوانده شدن به صورت آیکون (تیک سبز/ضربدر قرمز)
    @admin.display(description="خوانده شده؟", boolean=True)
    def is_read_display(self, obj):
        return obj.is_read

    @admin.action(description="علامت‌گذاری پیام‌های انتخاب شده به عنوان خوانده شده")
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} پیام خوانده شدند.")

    @admin.action(description="علامت‌گذاری پیام‌های انتخاب شده به عنوان خوانده نشده")
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} پیام به حالت خوانده نشده برگشتند.")


# ----------------------------------------------------------------------
# مدیریت تنظیمات پویای سیستم (SystemSetting)  
# ----------------------------------------------------------------------
@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = (
        "setting_id",
        "setting_key",
        "setting_value",
        "data_type",
        "updated_at",
        "updated_by",
    )
    
    list_filter = (
        "data_type",
        "updated_at",
    )
    
    search_fields = (
        "setting_key",
        "setting_value",
        "description",
    )
    
    list_select_related = ("data_type", "updated_by")
    ordering = ("setting_key",)
    list_per_page = 20
    
    # فیلدهایی که نباید قابل ویرایش باشند
    readonly_fields = ("updated_at", "updated_by")
    
    # تابع برای ثبت خودکار کاربری که تنظیمات رو تغییر داده
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
=======


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

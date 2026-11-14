import csv
from django.contrib import admin
from django.db.models import Count
from django.http import HttpResponse
from django.utils.html import format_html

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
)


# ----------------------------------------------------------------------
# مدیریت کلاس‌های آنلاین (OnlineClass)
# ----------------------------------------------------------------------
@admin.register(OnlineClass)
class OnlineClassAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course_offering",
        "platform",
        "class_link_button",
        "is_recorded",
        "is_active",
        "created_at",
    )
    list_filter = ("platform", "is_recorded", "is_active", "created_at")
    search_fields = (
        "course_offering__lesson__title",
        "course_offering__lesson__lesson_code",
        "meeting_id",
    )
    list_select_related = ("course_offering__lesson",)
    list_per_page = 20

    @admin.display(description="لینک ورود به کلاس")
    def class_link_button(self, obj):
        if obj.class_url:
            return format_html(
                '<a class="button" href="{}" target="_blank" style="background:#2563eb; color:#fff; padding:3px 8px; border-radius:4px; text-decoration:none;">ورود به کلاس</a>',
                obj.class_url,
            )
        return "-"


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
class TicketReplyInline(admin.StackedInline):
    model = Ticket
    fk_name = "parent"
    extra = 1
    fields = ("creator", "creator_role", "message", "status", "created_at")
    readonly_fields = ("created_at",)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk and form.instance.pk:
                instance.subject = f"Re: {form.instance.subject}"
                instance.category = form.instance.category
            instance.save()
        formset.save_m2m()


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    inlines = [TicketReplyInline]
    list_display = (
        "id",
        "subject",
        "creator",
        "category",
        "priority",
        "status_badge",
        "assigned_to",
        "replies_count",
        "created_at",
    )
    list_filter = ("status", "priority", "category", "created_at")
    search_fields = (
        "subject",
        "message",
        "creator__username",
        "assigned_to__username",
    )
    list_select_related = (
        "creator",
        "creator_role",
        "category",
        "priority",
        "status",
        "assigned_to",
    )
    list_per_page = 20
    actions = ["make_closed", "make_in_progress", "assign_to_me", "export_csv"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(parent__isnull=True).annotate(
            _replies_count=Count("replies")
        )

    @admin.display(description="تعداد پاسخ‌ها", ordering="_replies_count")
    def replies_count(self, obj):
        return getattr(obj, "_replies_count", 0)

    @admin.display(description="وضعیت", ordering="status")
    def status_badge(self, obj):
        if not obj.status:
            return "-"
        code = getattr(obj.status, "code", "").lower()
        color_map = {
            "open": "#0284c7",
            "in_progress": "#eab308",
            "closed": "#22c55e",
        }
        color = color_map.get(code, "#64748b")
        return format_html(
            '<span style="background:{}; color:#fff; padding:2px 8px; border-radius:10px; font-size:12px;">{}</span>',
            color,
            obj.status.label if hasattr(obj.status, "label") else obj.status,
        )

    @admin.action(description="تغییر وضعیت تیکت‌های انتخابی به بسته شده")
    def make_closed(self, request, queryset):
        from .models import Constant

        closed_status = Constant.objects.filter(
            category="ticket_status", code="closed"
        ).first()
        if closed_status:
            updated = queryset.update(status=closed_status)
            self.message_user(
                request, f"{updated} تیکت با موفقیت بسته شدند."
            )

    @admin.action(description="تغییر وضعیت تیکت‌های انتخابی به در حال بررسی")
    def make_in_progress(self, request, queryset):
        from .models import Constant

        in_progress_status = Constant.objects.filter(
            category="ticket_status", code="in_progress"
        ).first()
        if in_progress_status:
            updated = queryset.update(status=in_progress_status)
            self.message_user(
                request, f"{updated} تیکت در حال بررسی قرار گرفتند."
            )

    @admin.action(description="ارجاع تیکت‌های انتخابی به من")
    def assign_to_me(self, request, queryset):
        updated = queryset.update(assigned_to=request.user)
        self.message_user(
            request, f"{updated} تیکت به شما ارجاع داده شدند."
        )

    @admin.action(description="خروجی CSV از موارد انتخابی")
    def export_csv(self, request, queryset):
        response = HttpResponse(
            content_type="text/csv; charset=utf-8-sig"
        )
        response["Content-Disposition"] = 'attachment; filename="tickets.csv"'
        response.write("\ufeff".encode("utf8"))

        writer = csv.writer(response)
        writer.writerow(
            ["شناسه", "موضوع", "سازنده", "دسته بندی", "اولویت", "وضعیت", "تاریخ ایجاد"]
        )
        for ticket in queryset:
            writer.writerow(
                [
                    ticket.id,
                    ticket.subject,
                    str(ticket.creator) if ticket.creator else "",
                    str(ticket.category) if ticket.category else "",
                    str(ticket.priority) if ticket.priority else "",
                    str(ticket.status) if ticket.status else "",
                    ticket.created_at.strftime("%Y-%m-%d %H:%M")
                    if ticket.created_at
                    else "",
                ]
            )
        return response


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

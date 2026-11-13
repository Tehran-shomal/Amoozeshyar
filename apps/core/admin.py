from django.contrib import admin
from .models import OnlineClass, Ticket, Role, Enrollment, Prerequisite


admin.site.register(OnlineClass)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):

    list_display = (
        'role_name',
        'description',
        'created_at',
        'is_active',
    )

    list_filter = ('is_active', 'created_at')

    search_fields = ('role_name', 'description')

    ordering = ('role_name',)

    list_per_page = 10


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'offering',
        'enrollment_type',
        'status',
        'enrollment_date',
        'drop_date',
    )

    list_filter = (
        'status',
        'enrollment_type',
        'enrollment_date',
    )

    search_fields = ('student__name',)

    list_select_related = ('student', 'offering')

    list_per_page = 10


@admin.register(Prerequisite)
class PrerequisiteAdmin(admin.ModelAdmin):

    list_display = (
        'prereq_id',
        'lesson',
        'prerequisite_lesson',
        'prerequisite_type',
        'created_at',
    )

    list_filter = (
        'prerequisite_type__category',
        'prerequisite_type',
        'created_at',
    )

    search_fields = (
        'lesson__title',
        'lesson__lesson_code',
        'prerequisite_lesson__title',
        'prerequisite_lesson__lesson_code',
        'prerequisite_type__label',
    )

    list_select_related = (
        'lesson',
        'prerequisite_lesson',
        'prerequisite_type',
    )

    list_per_page = 10


class TicketReplyInline(admin.TabularInline):
    model = Ticket
    fk_name = "parent"
    extra = 1


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    inlines = [TicketReplyInline]
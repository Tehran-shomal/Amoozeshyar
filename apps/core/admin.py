
from django.contrib import admin
from .models import OnlineClass, Ticket, Lesson, Payment, CourseOffering


# ثبت کلاس آنلاین
admin.site.register(OnlineClass)


# مدیریت تیکت‌ها
class TicketReplyInline(admin.TabularInline):
    model = Ticket
    fk_name = "parent"
    extra = 1


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    inlines = [TicketReplyInline]


# مدیریت درس‌ها
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        'lesson_code',
        'title',
        'lesson_type',
        'department',
        'practical_units',
        'theory_units',
        'is_active',
    )
    search_fields = ('lesson_code', 'title')
    list_filter = ('is_active', 'lesson_type', 'department')
    ordering = ('title',)
    list_per_page = 25


# مدیریت پرداخت‌ها
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'tracking_code',
        'student',
        'term',
        'amount',
        'payment_date',
        'status',
    )
    search_fields = ('tracking_code',)
    list_filter = ('status', 'term')
    ordering = ('-created_at',)
    list_per_page = 25


# مدیریت ارائه درس‌ها
@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = (
        'lesson',
        'teacher',
        'term',
        'day_of_week',
        'start_time',
        'end_time',
        'capacity',
        'remaining_capacity',
        'is_active',
    )
    search_fields = ('lesson__lesson_code', 'lesson__title')
    list_filter = ('day_of_week', 'term', 'is_active', 'classroom')
    ordering = ('start_time',)
    list_per_page = 25

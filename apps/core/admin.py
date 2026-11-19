import csv

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
from django.http import HttpResponse
from django.utils.html import format_html

from .models import (
    Constant, Person, Teacher, Student, Lesson, Term, Payment, Exam,
    LessonGroups, ParkingPasses, Role, UserAccount, Faculty, Department,
    Field, Prerequisite, Classroom, CourseOffering, Enrollment, Grade,
    GradeAppeal, Attendance, TicketCategory, Ticket, OnlineClass,
    TuitionReceipt, RefundRequest, StudentServiceRequest,
    ScholarshipApplication, CounselingAppointment, Proposal, TransferRequest,
    GraduationAudit, EducationalChangeLog, Curriculum, Communication,
    SystemSetting, CreditTransferRequest, InternshipRequest,
    ThesisProgressReport, Notification, TeacherSurvey, Internship
)

# ==========================================
# تنظیمات کلی پنل ادمین
# ==========================================
admin.site.site_header = "پنل مدیریت آموزشیار"
admin.site.site_title = "مدیریت آموزشیار"
admin.site.index_title = "به سیستم مدیریت آموزشیار خوش آمدید"


# ==========================================
# ۱. شخص و کاربران
# ==========================================
class PersonCreationForm(UserCreationForm):
    class Meta:
        model = Person
        fields = ("username", "first_name", "last_name", "email", "national_id", "birth_date", "birth_place")


@admin.register(Person)
class PersonAdmin(UserAdmin):
    add_form = PersonCreationForm
    list_display = ('username', 'full_name', 'email', 'national_id', 'gender', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'national_id')
    list_filter = ('gender', 'preferred_language', 'is_active', 'is_staff')
    ordering = ('last_name', 'first_name')
    readonly_fields = ('updated_at', 'age', 'full_name')

    fieldsets = UserAdmin.fieldsets + (
        ('اطلاعات تکمیلی', {'fields': ('national_id', 'birth_date', 'birth_place', 'gender', 'address', 'age', 'full_name')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('اطلاعات تکمیلی', {'fields': ('national_id', 'birth_date', 'birth_place')}),
    )

    # اگر این کدها برای خروجی CSV (Action) است، باید داخل یک تابع تعریف شود:
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        fields = [field for field in meta.get_fields()]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}.csv'
        response.write("\ufeff")  # برای نمایش درست فارسی در Excel
        
        writer = csv.writer(response)
        writer.writerow([f.name for f in fields])
        
        for obj in queryset:
            writer.writerow([getattr(obj, f.attname, '') for f in fields])
            
        return response
    
    export_as_csv.short_description = "خروجی CSV"




@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_code', 'get_full_name', 'field', 'educational_level', 'status', 'total_gpa', 'is_on_probation_display')
    search_fields = ('student_code', 'person__first_name', 'person__last_name', 'person__national_id')
    list_filter = ('educational_level', 'status', 'field')
    list_select_related = ('person', 'field', 'educational_level', 'status')
    
    def get_full_name(self, obj):
        return obj.person.full_name
    get_full_name.short_description = 'نام و نام خانوادگی'

    @admin.display(description="مشروط؟", boolean=True)
    def is_on_probation_display(self, obj):
        return obj.is_on_probation


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_code', 'get_full_name', 'department', 'academic_rank', 'hire_date')
    search_fields = ('teacher_code', 'person__first_name', 'person__last_name')
    list_filter = ('department', 'academic_rank')
    list_select_related = ('person', 'department', 'academic_rank')
    
    def get_full_name(self, obj):
        return obj.person.full_name
    get_full_name.short_description = 'نام و نام خانوادگی'


admin.site.register(UserAccount)
admin.site.register(Role)


# ==========================================
# ۲. دروس، ترم‌ها و ارائه‌ها
# ==========================================
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('lesson_code', 'title', 'lesson_type', 'department', 'practical_units', 'theory_units', 'is_active')
    search_fields = ('lesson_code', 'title')
    list_filter = ('is_active', 'lesson_type', 'department')
    ordering = ('title',)
    list_per_page = 25


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('term_code', 'semester', 'academic_year', 'start_date', 'end_date', 'is_active')
    search_fields = ('term_code', 'academic_year')
    list_filter = ('is_active', 'semester')
    ordering = ('-start_date',)


@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'teacher', 'term', 'day_of_week', 'start_time', 'end_time', 'capacity', 'remaining_capacity_display', 'is_active')
    search_fields = ('lesson__lesson_code', 'lesson__title', 'teacher__person__last_name')
    list_filter = ('day_of_week', 'term', 'is_active', 'classroom')
    list_select_related = ('lesson', 'teacher__person', 'term', 'classroom', 'day_of_week')
    ordering = ('start_time',)
    list_per_page = 25

    @admin.display(description="ظرفیت باقی‌مانده")
    def remaining_capacity_display(self, obj):
        return obj.remaining_capacity


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('EnrollmentId', 'student', 'offering', 'status', 'enrollment_type', 'enrollment_date', 'drop_date')
    search_fields = ('student__person__first_name', 'student__person__last_name', 'student__student_code', 'offering__lesson__title')
    list_filter = ('status', 'enrollment_type', 'enrollment_date')
    list_select_related = ('student__person', 'offering__lesson', 'status', 'enrollment_type')
    list_per_page = 25


@admin.register(Prerequisite)
class PrerequisiteAdmin(admin.ModelAdmin):
    list_display = ('prereq_id', 'lesson', 'prerequisite_lesson', 'prerequisite_type', 'created_at')
    list_filter = ('prerequisite_type', 'created_at')
    search_fields = ('lesson__title', 'lesson__lesson_code', 'prerequisite_lesson__title')
    list_select_related = ('lesson', 'prerequisite_lesson', 'prerequisite_type')


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ('curriculum_id', 'field', 'lesson', 'requirement_type', 'recommended_term', 'calculated_units', 'is_active')
    list_filter = ('is_active', 'field__department__faculty', 'field__department', 'field', 'requirement_type', 'recommended_term')
    search_fields = ('field__field_name', 'field__field_code', 'lesson__title', 'lesson__lesson_code')
    list_select_related = ('field', 'lesson', 'requirement_type')
    ordering = ('field', 'recommended_term')
    list_editable = ('is_active', 'calculated_units', 'recommended_term')
    actions = ['make_active', 'make_inactive']

    @admin.action(description="فعال کردن چارت‌های انتخاب شده")
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} چارت درسی با موفقیت فعال شدند.")

    @admin.action(description="غیرفعال کردن چارت‌های انتخاب شده")
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} چارت درسی با موفقیت غیرفعال شدند.")


# ==========================================
# ۳. دانشکده، گروه و رشته
# ==========================================
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_code', 'faculty_name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('faculty_code', 'faculty_name')
    ordering = ('faculty_name',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('department_code', 'department_name', 'faculty', 'is_active', 'created_at')
    list_filter = ('faculty', 'is_active')
    search_fields = ('department_code', 'department_name', 'faculty__faculty_name')
    list_select_related = ('faculty',)
    ordering = ('department_name',)


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ('field_code', 'field_name', 'department', 'is_active', 'created_at')
    list_filter = ('department__faculty', 'department', 'is_active')
    search_fields = ('field_code', 'field_name', 'department__department_name')
    list_select_related = ('department', 'department__faculty')
    ordering = ('field_name',)


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('building_name', 'room_number', 'capacity', 'classroom_type')
    search_fields = ('building_name', 'room_number')


# ==========================================
# ۴. مالی و پرداخت
# ==========================================
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('tracking_code', 'student', 'term', 'amount', 'payment_date', 'status')
    search_fields = ('tracking_code', 'student__student_code')
    list_filter = ('status', 'term', 'payment_date')
    list_select_related = ('student__person', 'term', 'status')
    ordering = ('-created_at',)
    list_per_page = 25


@admin.register(TuitionReceipt)
class TuitionReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_serial_code', 'receipt_payment_link', 'receipt_issued_on')
    search_fields = ('receipt_serial_code',)
    list_select_related = ('receipt_payment_link',)


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ('refund_case_key', 'refund_payment_link', 'refund_value_requested', 'refund_review_state')
    list_filter = ('refund_review_state',)
    search_fields = ('refund_justification_text',)
    list_select_related = ('refund_payment_link', 'refund_review_state')


# ==========================================
# ۵. امتحانات، حضور و غیاب و نمرات
# ==========================================
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'offering', 'exam_date', 'exam_type')
    list_filter = ('exam_type', 'exam_date')
    search_fields = ('offering__lesson__title',)
    list_select_related = ('offering__lesson', 'exam_type')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrollment', 'score')
    search_fields = ('enrollment__student__person__first_name', 'enrollment__student__person__last_name')
    list_select_related = ('enrollment__student__person', 'enrollment__offering__lesson')


@admin.register(GradeAppeal)
class GradeAppealAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrollment', 'appeal_status', 'appeal_date')
    list_filter = ('appeal_status', 'appeal_date')
    search_fields = ('enrollment__student__person__first_name', 'enrollment__student__person__last_name')
    list_select_related = ('enrollment__student__person', 'appeal_status')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrollment', 'session_number', 'session_date', 'attendance_status')
    list_filter = ('attendance_status', 'session_date')
    search_fields = ('enrollment__student__person__first_name', 'enrollment__student__person__last_name')
    list_select_related = ('enrollment__student__person', 'attendance_status')


# ==========================================
# ۶. پشتیبانی و تیکت‌ها
# ==========================================
class TicketReplyInline(admin.StackedInline):
    model = Ticket
    fk_name = "parent"
    extra = 1
    fields = ("creator", "creator_role", "content", "status", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    inlines = [TicketReplyInline]
    list_display = ('id', 'subject', 'creator', 'category', 'status_badge', 'assigned_to', 'replies_count', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('subject', 'content', 'creator__username', 'assigned_to__username')
    list_select_related = ('creator', 'creator_role', 'category', 'status', 'assigned_to')
    list_per_page = 20
    actions = ['make_closed', 'make_in_progress', 'assign_to_me', 'export_csv']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(parent__isnull=True).annotate(_replies_count=Count('replies'))

    @admin.display(description="تعداد پاسخ‌ها", ordering="_replies_count")
    def replies_count(self, obj):
        return getattr(obj, "_replies_count", 0)

    @admin.display(description="وضعیت", ordering="status")
    def status_badge(self, obj):
        if not obj.status:
            return "-"
        code = getattr(obj.status, "code", "").lower()
        color_map = {'open': '#0284c7', 'in_progress': '#eab308', 'closed': '#22c55e'}
        color = color_map.get(code, "#64748b")
        return format_html(
            '<span style="background:{}; color:#fff; padding:2px 8px; border-radius:10px; font-size:12px;">{}</span>',
            color, obj.status.label
        )

    @admin.action(description="تغییر وضعیت به بسته شده")
    def make_closed(self, request, queryset):
        closed_status = Constant.objects.filter(category="ticket_status", code="closed").first()
        if closed_status:
            queryset.update(status=closed_status)
            self.message_user(request, f"{queryset.count()} تیکت بسته شدند.")

    @admin.action(description="تغییر وضعیت به در حال بررسی")
    def make_in_progress(self, request, queryset):
        in_progress_status = Constant.objects.filter(category="ticket_status", code="in_progress").first()
        if in_progress_status:
            queryset.update(status=in_progress_status)
            self.message_user(request, f"{queryset.count()} تیکت در حال بررسی قرار گرفتند.")

    @admin.action(description="ارجاع به من")
    def assign_to_me(self, request, queryset):
        queryset.update(assigned_to=request.user)
        self.message_user(request, f"{queryset.count()} تیکت به شما ارجاع داده شدند.")

    @admin.action(description="خروجی CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="tickets.csv"'
        response.write("\ufeff".encode("utf8"))
        writer = csv.writer(response)
        writer.writerow(["شناسه", "موضوع", "سازنده", "دسته", "وضعیت", "تاریخ ایجاد"])
        for ticket in queryset:
            writer.writerow([ticket.id, ticket.subject, str(ticket.creator), str(ticket.category), str(ticket.status), ticket.created_at.strftime("%Y-%m-%d %H:%M") if ticket.created_at else ""])
        return response


@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


# ==========================================
# ۷. سیستم، ارتباطات و اعلان‌ها
# ==========================================
@admin.register(Constant)
class ConstantAdmin(admin.ModelAdmin):
    list_display = ('constant_id', 'category', 'code', 'label', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('category', 'code', 'label')
    ordering = ('category', 'code')


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('setting_id', 'setting_key', 'setting_value', 'data_type', 'updated_at')
    list_filter = ('data_type',)
    search_fields = ('setting_key', 'setting_value')


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('communication_id', 'sender', 'receiver', 'subject', 'communication_type', 'status', 'is_read_display', 'sent_at')
    list_filter = ('is_read', 'communication_type', 'status')
    search_fields = ('subject', 'message_body')
    list_select_related = ('sender', 'receiver', 'communication_type', 'status')
    ordering = ('-sent_at',)
    date_hierarchy = 'sent_at'
    actions = ['mark_as_read', 'mark_as_unread']

    @admin.display(description="خوانده شده؟", boolean=True)
    def is_read_display(self, obj):
        return obj.is_read

    @admin.action(description="علامت‌گذاری به عنوان خوانده شده")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} پیام خوانده شدند.")

    @admin.action(description="علامت‌گذاری به عنوان خوانده نشده")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"{queryset.count()} پیام به حالت خوانده نشده برگشتند.")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('is_read', 'notification_type')
    search_fields = ('title', 'message')


# ==========================================
# ۸. درخواست‌ها و خدمات
# ==========================================
@admin.register(StudentServiceRequest)
class StudentServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('student_service_case_key', 'service_requester', 'service_request_kind', 'service_decision_state')
    list_filter = ('service_decision_state', 'service_request_kind')
    search_fields = ('service_request_data',)


@admin.register(ScholarshipApplication)
class ScholarshipApplicationAdmin(admin.ModelAdmin):
    list_display = ('scholarship_application_key', 'scholarship_applicant', 'scholarship_type', 'scholarship_status')
    list_filter = ('scholarship_status',)
    search_fields = ('scholarship_type',)


@admin.register(CounselingAppointment)
class CounselingAppointmentAdmin(admin.ModelAdmin):
    list_display = ('counseling_appointment_key', 'counseling_student_link', 'counseling_teacher_link', 'counseling_date', 'counseling_status')
    list_filter = ('counseling_status', 'counseling_date')


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('proposal_case_key', 'proposal_student_link', 'proposal_title', 'proposal_status')
    list_filter = ('proposal_status',)
    search_fields = ('proposal_title',)


@admin.register(TransferRequest)
class TransferRequestAdmin(admin.ModelAdmin):
    list_display = ('transfer_id', 'student', 'destination_university', 'review_status')
    list_filter = ('review_status',)
    search_fields = ('destination_university',)


@admin.register(GraduationAudit)
class GraduationAuditAdmin(admin.ModelAdmin):
    list_display = ('audit_id', 'student', 'curriculum', 'graduation_status', 'remaining_units_display', 'is_graduation_eligible')
    list_filter = ('graduation_status',)
    
    @admin.display(description="واحدهای باقی‌مانده")
    def remaining_units_display(self, obj):
        return obj.remaining_units


@admin.register(EducationalChangeLog)
class EducationalChangeLogAdmin(admin.ModelAdmin):
    list_display = ('log_id', 'student', 'change_type', 'changed_by', 'changed_at')
    list_filter = ('change_type', 'changed_at')
    search_fields = ('description',)


@admin.register(CreditTransferRequest)
class CreditTransferRequestAdmin(admin.ModelAdmin):
    list_display = ('transfer_request_id', 'student', 'source_university', 'status')
    list_filter = ('status',)


@admin.register(InternshipRequest)
class InternshipRequestAdmin(admin.ModelAdmin):
    list_display = ('internship_request_id', 'student', 'organization_name', 'start_date', 'status')
    list_filter = ('status',)


@admin.register(ThesisProgressReport)
class ThesisProgressReportAdmin(admin.ModelAdmin):
    list_display = ('report_id', 'student', 'teacher', 'review_status')
    list_filter = ('review_status',)


@admin.register(TeacherSurvey)
class TeacherSurveyAdmin(admin.ModelAdmin):
    list_display = ('id', 'enrollment', 'overall_rating', 'teaching_quality', 'behavior', 'submitted_at')
    list_filter = ('overall_rating', 'teaching_quality', 'behavior')


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'request_type', 'company_name', 'intern_start_date', 'duration_hours', 'status')
    list_filter = ('status', 'request_type')
    search_fields = ('company_name',)


@admin.register(OnlineClass)
class OnlineClassAdmin(admin.ModelAdmin):
    list_display = ('id', 'offering', 'teacher', 'title', 'start_at', 'end_at', 'meeting_link')
    list_filter = ('start_at',)
    search_fields = ('title',)


@admin.register(LessonGroups)
class LessonGroupsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'teacher', 'created_by', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(ParkingPasses)
class ParkingPassesAdmin(admin.ModelAdmin):
    list_display = ('id', 'parking_pass_code', 'owner', 'aquisition_date', 'expiration_date', 'remaining_days_display')
    search_fields = ('parking_pass_code', 'owner__username')

    @admin.display(description="روزهای باقی‌مانده")
    def remaining_days_display(self, obj):
        return obj.remaining_days
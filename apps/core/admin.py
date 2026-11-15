import csv

from django.contrib import admin
from django.http import HttpResponse
from django.contrib.auth.admin import UserAdmin

from .models import (
    Attendance,
    Classroom,
    Communication,
    Constant,
    CounselingAppointment,
    CourseOffering,
    CreditTransferRequest,
    Curriculum,
    Department,
    Enrollment,
    EducationalChangeLog,
    Exam,
    Faculty,
    Field,
    GradeAppeal,
    GraduationAudit,
    InternshipRequest,
    Internship,
    Lesson,
    LessonGroups,
    Notification,
    OnlineClass,
    ParkingPasses,
    Payment,
    Person,
    Prerequisite,
    Proposal,
    RefundRequest,
    Role,
    ScholarshipApplication,
    StudentServiceRequest,
    Student,
    SystemSetting,
    Teacher,
    Term,
    Ticket,
    TicketCategory,
    TeacherSurvey,
    ThesisProgressReport,
    TransferRequest,
    TuitionReceipt,
    UserAccount,
)


# ----------------------------------------------------------------------
# اکشن مشترک: خروجی CSV
# ----------------------------------------------------------------------
@admin.action(description="خروجی CSV از موارد انتخاب‌شده")
def export_csv(modeladmin, request, queryset):
    fields = modeladmin.model._meta.concrete_fields
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f'attachment; filename="{modeladmin.model._meta.model_name}.csv"'
    )
    response.write("\ufeff")  # برای نمایش درست فارسی در Excel
    writer = csv.writer(response)
    writer.writerow([f.name for f in fields])
    for obj in queryset:
        writer.writerow([getattr(obj, f.attname) for f in fields])
    return response


# ----------------------------------------------------------------------
# کاربران و نقش‌ها
# ----------------------------------------------------------------------
@admin.register(Person)
class PersonAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "first_name", "last_name", "email", "national_id")
    ordering = ("last_name",)
    actions = [export_csv]


@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ("username", "person", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("username", "person__first_name", "person__last_name")
    list_select_related = ("person", "role")
    readonly_fields = ("created_at",)
    actions = [export_csv]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("role_name", "description", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("role_name", "description")
    ordering = ("role_name",)
    readonly_fields = ("created_at",)
    actions = [export_csv]


# ----------------------------------------------------------------------
# ثابت‌ها و تنظیمات سیستم
# ----------------------------------------------------------------------
@admin.register(Constant)
class ConstantAdmin(admin.ModelAdmin):
    list_display = ("category", "code", "label", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("category", "code", "label")
    ordering = ("category", "code")
    readonly_fields = ("created_at",)
    actions = [export_csv]


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ("setting_key", "setting_value", "updated_by", "updated_at")
    list_filter = ("updated_at",)
    search_fields = ("setting_key", "setting_value", "description")
    list_select_related = ("updated_by",)
    readonly_fields = ("updated_at",)
    actions = [export_csv]


# ----------------------------------------------------------------------
# ساختار دانشگاه: دانشکده، گروه آموزشی، رشته
# ----------------------------------------------------------------------
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("faculty_name", "faculty_code", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("faculty_name", "faculty_code")
    ordering = ("faculty_name",)
    readonly_fields = ("created_at",)
    actions = [export_csv]


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("department_name", "department_code", "faculty", "is_active")
    list_filter = ("faculty", "is_active")
    search_fields = ("department_name", "department_code")
    list_select_related = ("faculty",)
    ordering = ("department_name",)
    readonly_fields = ("created_at",)
    actions = [export_csv]


@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    list_display = ("field_name", "field_code", "department", "is_active")
    list_filter = ("department", "is_active")
    search_fields = ("field_name", "field_code")
    list_select_related = ("department",)
    ordering = ("field_name",)
    readonly_fields = ("created_at",)
    actions = [export_csv]


# ----------------------------------------------------------------------
# اساتید و دانشجویان
# ----------------------------------------------------------------------
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("teacher_code", "person", "department", "academic_rank", "hire_date")
    list_filter = ("department", "academic_rank")
    search_fields = ("teacher_code", "person__first_name", "person__last_name")
    list_select_related = ("person", "department")
    ordering = ("teacher_code",)
    actions = [export_csv]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_code", "person", "field", "status", "total_gpa", "passed_units")
    list_filter = ("field", "status", "admission_type")
    search_fields = ("student_code", "person__first_name", "person__last_name")
    list_select_related = ("person", "field")
    ordering = ("student_code",)
    readonly_fields = ("total_gpa", "passed_units", "completed_terms")
    actions = [export_csv]


# ----------------------------------------------------------------------
# دروس، پیش‌نیاز، برنامه درسی
# ----------------------------------------------------------------------
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("lesson_code", "title", "department", "theory_units", "practical_units", "is_active")
    list_filter = ("department", "lesson_type", "is_active")
    search_fields = ("lesson_code", "title")
    list_select_related = ("department",)
    ordering = ("lesson_code",)
    readonly_fields = ("created_at",)
    actions = [export_csv]


@admin.register(Prerequisite)
class PrerequisiteAdmin(admin.ModelAdmin):
    list_display = ("lesson", "prerequisite_lesson", "prerequisite_type", "created_at")
    list_filter = ("prerequisite_type",)
    search_fields = ("lesson__title", "prerequisite_lesson__title")
    list_select_related = ("lesson", "prerequisite_lesson")
    readonly_fields = ("created_at",)
    actions = [export_csv]


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ("field", "lesson", "recommended_term", "calculated_units", "is_active")
    list_filter = ("field", "recommended_term", "is_active")
    search_fields = ("lesson__title", "lesson__lesson_code")
    list_select_related = ("field", "lesson")
    readonly_fields = ("created_at",)
    actions = [export_csv]


# ----------------------------------------------------------------------
# ترم، فضا و ارائه‌های درس
# ----------------------------------------------------------------------
@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("term_code", "academic_year", "semester", "start_date", "end_date", "is_active")
    list_filter = ("academic_year", "is_active")
    search_fields = ("term_code", "academic_year")
    ordering = ("-start_date",)
    actions = [export_csv]


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("building_name", "room_number", "capacity", "classroom_type")
    list_filter = ("classroom_type",)
    search_fields = ("building_name", "room_number")
    ordering = ("building_name", "room_number")
    actions = [export_csv]


@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ("lesson", "term", "teacher", "classroom", "day_of_week", "start_time", "capacity", "remaining_capacity")
    list_filter = ("term", "day_of_week", "is_active")
    search_fields = ("lesson__title", "lesson__lesson_code", "teacher__teacher_code")
    list_select_related = ("lesson", "term", "teacher", "classroom")
    ordering = ("term", "start_time")
    readonly_fields = ("created_at",)
    actions = [export_csv]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("offering", "exam_date", "exam_type")
    list_filter = ("exam_date", "exam_type")
    search_fields = ("offering__lesson__title",)
    list_select_related = ("offering",)
    actions = [export_csv]


@admin.register(OnlineClass)
class OnlineClassAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "offering", "start_at", "end_at", "duration", "is_ongoing")
    list_filter = ("start_at", "end_at")
    search_fields = ("title",)
    list_select_related = ("teacher", "offering")
    ordering = ("start_at",)
    readonly_fields = ("duration", "is_ongoing")
    actions = [export_csv]


@admin.register(LessonGroups)
class LessonGroupsAdmin(admin.ModelAdmin):
    list_display = ("name", "teacher", "created_by", "is_active", "created_at")
    list_filter = ("is_active", "teacher")
    search_fields = ("name",)
    list_select_related = ("teacher", "created_by")
    filter_horizontal = ("members",)
    readonly_fields = ("created_at",)
    actions = [export_csv]


# ----------------------------------------------------------------------
# ثبت‌نام، حضور و غیاب، اعتراض نمره، نظرسنجی
# ----------------------------------------------------------------------
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "offering", "status", "enrollment_type", "enrollment_date")
    list_filter = ("status", "enrollment_type", "enrollment_date")
    search_fields = ("student__student_code", "offering__lesson__title")
    list_select_related = ("student", "offering")
    ordering = ("-enrollment_date",)
    actions = [export_csv]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "session_number", "session_date", "attendance_status", "recorded_by")
    list_filter = ("session_date", "attendance_status")
    search_fields = ("enrollment__student__student_code", "description")
    list_select_related = ("enrollment", "recorded_by")
    readonly_fields = ("created_at",)
    actions = [export_csv]


@admin.register(GradeAppeal)
class GradeAppealAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "appeal_date", "appeal_status")
    list_filter = ("appeal_status", "appeal_date")
    search_fields = ("appeal_reason", "enrollment__student__student_code")
    list_select_related = ("enrollment",)
    actions = [export_csv]


@admin.register(TeacherSurvey)
class TeacherSurveyAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "overall_rating", "teaching_quality", "submitted_at")
    list_filter = ("overall_rating", "teaching_quality")
    search_fields = ("comment",)
    list_select_related = ("enrollment",)
    readonly_fields = ("created_at",)
    actions = [export_csv]


# ----------------------------------------------------------------------
# مالی: پرداخت، رسید، استرداد، پارکینگ
# ----------------------------------------------------------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("tracking_code", "student", "term", "amount", "payment_date", "status")
    list_filter = ("term", "status", "payment_date")
    search_fields = ("tracking_code", "student__student_code")
    list_select_related = ("student", "term")
    ordering = ("-payment_date",)
    readonly_fields = ("created_at",)
    actions = [export_csv]


@admin.register(TuitionReceipt)
class TuitionReceiptAdmin(admin.ModelAdmin):
    list_display = ("receipt_serial_code", "receipt_payment_link", "receipt_issued_on")
    list_filter = ("receipt_issued_on",)
    search_fields = ("receipt_serial_code",)
    list_select_related = ("receipt_payment_link",)
    actions = [export_csv]


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ("refund_payment_link", "refund_value_requested", "refund_review_state")
    list_filter = ("refund_review_state",)
    search_fields = ("refund_justification_text",)
    list_select_related = ("refund_payment_link",)
    actions = [export_csv]


@admin.register(ParkingPasses)
class ParkingPassesAdmin(admin.ModelAdmin):
    list_display = ("parking_pass_code", "owner", "aquisition_date", "expiration_date", "charge")
    list_filter = ("aquisition_date", "expiration_date")
    search_fields = ("parking_pass_code", "owner__username")
    list_select_related = ("owner",)
    actions = [export_csv]


# ----------------------------------------------------------------------
# درخواست‌ها و خدمات دانشجویی
# ----------------------------------------------------------------------
@admin.register(StudentServiceRequest)
class StudentServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("service_requester", "service_request_kind", "service_decision_state")
    list_filter = ("service_request_kind", "service_decision_state")
    search_fields = ("service_request_data",)
    list_select_related = ("service_requester",)
    actions = [export_csv]


@admin.register(ScholarshipApplication)
class ScholarshipApplicationAdmin(admin.ModelAdmin):
    list_display = ("scholarship_applicant", "scholarship_type", "scholarship_status", "scholarship_submitted_at")
    list_filter = ("scholarship_type", "scholarship_status")
    search_fields = ("scholarship_reason",)
    list_select_related = ("scholarship_applicant",)
    readonly_fields = ("scholarship_submitted_at",)
    actions = [export_csv]


@admin.register(CounselingAppointment)
class CounselingAppointmentAdmin(admin.ModelAdmin):
    list_display = ("counseling_student_link", "counseling_teacher_link", "counseling_date", "counseling_status")
    list_filter = ("counseling_status", "counseling_date")
    search_fields = ("counseling_topic",)
    list_select_related = ("counseling_student_link", "counseling_teacher_link")
    actions = [export_csv]


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ("proposal_title", "proposal_student_link", "proposal_status", "proposal_submitted_at")
    list_filter = ("proposal_status",)
    search_fields = ("proposal_title", "proposal_description")
    list_select_related = ("proposal_student_link",)
    readonly_fields = ("proposal_submitted_at",)
    actions = [export_csv]


@admin.register(TransferRequest)
class TransferRequestAdmin(admin.ModelAdmin):
    list_display = ("student", "destination_university", "review_status", "created_at")
    list_filter = ("review_status",)
    search_fields = ("destination_university", "student__student_code")
    list_select_related = ("student",)
    readonly_fields = ("created_at",)
    actions = [export_csv]


@admin.register(CreditTransferRequest)
class CreditTransferRequestAdmin(admin.ModelAdmin):
    list_display = ("student", "source_university", "status", "request_date")
    list_filter = ("status",)
    search_fields = ("source_university", "student__student_code")
    list_select_related = ("student",)
    readonly_fields = ("request_date",)
    actions = [export_csv]


@admin.register(InternshipRequest)
class InternshipRequestAdmin(admin.ModelAdmin):
    list_display = ("student", "organization_name", "start_date", "status")
    list_filter = ("status", "start_date")
    search_fields = ("organization_name", "student__student_code")
    list_select_related = ("student",)
    actions = [export_csv]


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ("student", "company_name", "intern_start_date", "duration_hours", "status", "reviewed_by")
    list_filter = ("status", "request_type")
    search_fields = ("company_name", "student__student_code")
    list_select_related = ("student", "reviewed_by")
    readonly_fields = ("created_at",)
    actions = [export_csv]


@admin.register(ThesisProgressReport)
class ThesisProgressReportAdmin(admin.ModelAdmin):
    list_display = ("student", "teacher", "review_status")
    list_filter = ("review_status",)
    search_fields = ("report_content", "student__student_code")
    list_select_related = ("student", "teacher")
    actions = [export_csv]


@admin.register(GraduationAudit)
class GraduationAuditAdmin(admin.ModelAdmin):
    list_display = ("student", "curriculum", "remaining_units", "graduation_status", "audit_date")
    list_filter = ("graduation_status", "audit_date")
    search_fields = ("student__student_code",)
    list_select_related = ("student", "curriculum")
    readonly_fields = ("audit_date",)
    actions = [export_csv]


@admin.register(EducationalChangeLog)
class EducationalChangeLogAdmin(admin.ModelAdmin):
    list_display = ("student", "change_type", "changed_by", "changed_at")
    list_filter = ("change_type", "changed_at")
    search_fields = ("description", "student__student_code")
    list_select_related = ("student", "changed_by")
    actions = [export_csv]


# ----------------------------------------------------------------------
# تیکت و ارتباطات
# ----------------------------------------------------------------------
@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    list_select_related = ("parent",)
    readonly_fields = ("created_at",)
    actions = [export_csv]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "creator", "category", "status", "assigned_to", "created_at")
    list_filter = ("category", "status", "created_at")
    search_fields = ("subject", "content")
    list_select_related = ("creator", "category", "assigned_to")
    readonly_fields = ("created_at", "updated_at")
    actions = [export_csv]


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ("subject", "sender", "receiver", "is_read", "sent_at")
    list_filter = ("is_read", "sent_at")
    search_fields = ("subject", "message_body")
    list_select_related = ("sender", "receiver")
    readonly_fields = ("sent_at",)
    actions = [export_csv]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "notification_type", "is_read", "sent_at")
    list_filter = ("notification_type", "is_read")
    search_fields = ("title", "message")
    list_select_related = ("user",)
    readonly_fields = ("created_at",)
    actions = [export_csv]

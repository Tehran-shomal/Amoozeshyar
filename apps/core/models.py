from django.db import models
from django.contrib.auth.models import AbstractUser


# شخص (جایگزین User پیش‌فرض جنگو)
class Person(AbstractUser):
    pass


# استاد
class Teacher(Person):
    pass


# دانشجو
class Student(Person):
    pass


# درس
class Lesson(models.Model):
    pass


# ترم
class Term(models.Model):
    pass


# پرداخت
class Payment(models.Model):
    pass


# امتحان
class Exam(models.Model):
    pass


# گروه کلاسی
class LessonGroups(models.Model):
    pass


# مجوزهای پارکینگ
class ParkingPasses(models.Model):
    pass


# نقش
class Role(models.Model):
    pass


# حساب کاربری
class UserAccount(models.Model):
    pass


# دانشکده
class Faculty(models.Model):
    pass


# گروه آموزشی
class Department(models.Model):
    pass


# رشته
class Field(models.Model):
    pass


# پیش‌نیاز/هم‌نیاز
class Prerequisite(models.Model):
    pass


# کلاس/مکان
class Classroom(models.Model):
    pass


# اعضای گروه کلاسی
class LessonGroupMember(models.Model):
    pass


# ارائه درس در ترم
class CourseOffering(models.Model):
    pass


# انتخاب واحد
class Enrollment(models.Model):
    pass


# نمره
class Grade(models.Model):
    pass


# اعتراض به نمره
class GradeAppeal(models.Model):
    pass


# حضور و غیاب
class Attendance(models.Model):
    pass


# تیکت
class Ticket(models.Model):
    creator_person_id = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='created_tickets')
    creator_role = models.CharField(max_length=20)
    category_id = models.ForeignKey('TicketCategory', on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=20)
    assigned_to_person_id = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# دسته بندی تیکت ها
class TicketCategory(models.Model):
    pass


# برگزاری کلاس مجازی
class OnlineClass(models.Model):
    teacher_id = models.ForeignKey('Teacher', on_delete=models.CASCADE)
    offering_id = models.ForeignKey('CourseOffering', on_delete=models.CASCADE)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    title = models.CharField(max_length=200)
    meeting_link = models.URLField()


# رسید شهریه
class TuitionReceipt(models.Model):

    tuition_receipt_key = models.AutoField(
        primary_key=True,
        db_column="TuitionReceiptKey"
    )
    receipt_serial_code = models.CharField(
        max_length=50,
        unique=True,
        db_column="ReceiptSerialCode"
    )
    receipt_payment_link = models.ForeignKey(
        "core.Payment",
        on_delete=models.PROTECT,
        related_name="tuition_receipts",
        db_column="ReceiptPaymentLinkId"
    )
    receipt_issued_on = models.DateTimeField(
        auto_now_add=True,
        db_column="ReceiptIssuedOn"
    )
    receipt_document_uri = models.CharField(
        max_length=500,
        blank=True,
        db_column="ReceiptDocumentUri"
    )

    class Meta:
        db_table = "TuitionReceipt"

    def __str__(self):
        return self.receipt_serial_code





# درخواست بازپرداخت وجه
class RefundRequest(models.Model):
    REFUND_STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("approved", "تأیید شده"),
        ("rejected", "رد شده"),
        ("paid", "بازپرداخت انجام شده"),
    ]

    refund_case_key = models.AutoField(
        primary_key=True,
        db_column="RefundCaseKey"
    )
    refund_payment_link = models.ForeignKey(
        "core.Payment",
        on_delete=models.PROTECT,
        related_name="refund_requests",
        db_column="RefundPaymentLinkId"
    )
    refund_value_requested = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        db_column="RefundValueRequested"
    )
    refund_justification_text = models.TextField(
        db_column="RefundJustificationText"
    )
    refund_review_state = models.CharField(
        max_length=20,
        choices=REFUND_STATUS_CHOICES,
        default="pending",
        db_column="RefundReviewState"
    )

    class Meta:
        db_table = "RefundRequest"

    def __str__(self):
        return f"درخواست بازپرداخت {self.refund_case_key}"





# اعلان
class Notification(models.Model):
    pass


# نظرسنجی از معلم
class TeacherSurvey(models.Model):
    pass


# کارآموزی
class Internship(models.Model):
    pass


# امانت کتابخانه
class LibraryLoan(models.Model):
    pass


# رویداد
class Event(models.Model):
    pass


# خوابگاه
class Dormitory(models.Model):
    pass


# کتاب
class Book(models.Model):
    pass


# درخواست خدمات دانشجویی
class StudentServiceRequest(models.Model):
    REQUEST_KIND_CHOICES = [
        ("installment", "تقسیط بدهی"),
        ("withdrawal", "انصراف از تحصیل"),
    ]

    REQUEST_STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("approved", "تأیید شده"),
        ("rejected", "رد شده"),
    ]

    student_service_case_key = models.AutoField(
        primary_key=True,
        db_column="StudentServiceCaseKey"
    )
    service_requester = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="service_requests",
        db_column="ServiceRequesterLinkId"
    )
    service_request_kind = models.CharField(
        max_length=20,
        choices=REQUEST_KIND_CHOICES,
        db_column="ServiceRequestKind"
    )
    service_request_data = models.TextField(
        blank=True,
        db_column="ServiceRequestData"
    )
    service_decision_state = models.CharField(
        max_length=20,
        choices=REQUEST_STATUS_CHOICES,
        default="pending",
        db_column="ServiceDecisionState"
    )

    class Meta:
        db_table = "StudentServiceRequest"

    def __str__(self):
        return (
            f"درخواست {self.student_service_case_key} - "
            f"{self.get_service_request_kind_display()}"
        )



# درخواست بورسیه
class ScholarshipApplication(models.Model):
    pass


# جلسات مشاوره
class CounselingAppointment(models.Model):
    pass


# پروپوزال
class Proposal(models.Model):
    pass

#درخواست مهمانی دروس
class TransferRequest(models.Model):

    REVIEW_STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("approved", "تأیید شده"),
        ("rejected", "رد شده"),
    ]

    transfer_id = models.AutoField(
        primary_key=True,
        db_column="TransferId",
        verbose_name="شناسه درخواست"
    )

    student = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="transfer_requests",
        db_column="StudentId",
        verbose_name="دانشجو"
    )

    destination_university = models.CharField(
        max_length=255,
        db_column="DestinationUniversity",
        verbose_name="نام دانشگاه مقصد"
    )

    review_status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS_CHOICES,
        default="pending",
        db_column="ReviewStatus",
        verbose_name="وضعیت بررسی"
    )

    course_compatibility_result = models.TextField(
        blank=True,
        default="",
        db_column="CourseCompatibilityResult",
        verbose_name="نتیجه بررسی دروس"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column="CreatedAt",
        verbose_name="تاریخ ثبت درخواست"
    )

    @property
    def is_approved(self):
        return self.review_status == "approved"

    class Meta:
        db_table = "TransferRequest"
        verbose_name = "درخواست مهمانی درس"
        verbose_name_plural = "درخواست‌های مهمانی دروس"
        ordering = ["-transfer_id"]

    def __str__(self):
        return (
            f"درخواست مهمانی {self.transfer_id} - "
            f"{self.student} - "
            f"{self.get_review_status_display()}"
        )

#بررسی شرایط فارغ تحصیلی
class GraduationAudit(models.Model):

    GRADUATION_STATUS_CHOICES = [
        ("eligible", "واجد شرایط"),
        ("not_eligible", "فاقد شرایط"),
        ("under_review", "در حال بررسی"),
    ]

    audit_id = models.AutoField(
        primary_key=True,
        db_column="AuditId",
        verbose_name="شناسه بررسی"
    )

    student = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="graduation_audits",
        db_column="StudentId",
        verbose_name="دانشجو"
    )

    curriculum = models.ForeignKey(
        "core.Curriculum",
        on_delete=models.PROTECT,
        related_name="graduation_audits",
        db_column="CurriculumId",
        verbose_name="چارت درسی"
    )

    remaining_units = models.PositiveIntegerField(
        default=0,
        db_column="RemainingUnits",
        verbose_name="تعداد واحد باقی‌مانده"
    )

    graduation_status = models.CharField(
        max_length=20,
        choices=GRADUATION_STATUS_CHOICES,
        default="under_review",
        db_column="GraduationStatus",
        verbose_name="وضعیت فارغ‌التحصیلی"
    )

    audit_date = models.DateTimeField(
        auto_now_add=True,
        db_column="AuditDate",
        verbose_name="تاریخ بررسی"
    )

    @property
    def is_graduation_eligible(self):
        return (
            self.remaining_units == 0
            and self.graduation_status == "eligible"
        )

    class Meta:
        db_table = "GraduationAudit"
        verbose_name = "بررسی فارغ‌التحصیلی"
        verbose_name_plural = "بررسی‌های فارغ‌التحصیلی"
        ordering = ["-audit_date"]

        constraints = [
            models.UniqueConstraint(
                fields=["student", "curriculum"],
                name="unique_student_curriculum_audit"
            )
        ]

    def __str__(self):
        return (
            f"بررسی فارغ‌التحصیلی {self.audit_id} - "
            f"{self.student} - "
            f"{self.get_graduation_status_display()}"
        )
    
#تاریخچه تغییرات اموزشی
class EducationalChangeLog(models.Model):

    CHANGE_TYPE_CHOICES = [
        ("grade_change", "تغییر نمره"),
        ("course_deletion", "حذف درس"),
        ("academic_status_change", "تغییر وضعیت تحصیلی"),
    ]

    log_id = models.AutoField(
        primary_key=True,
        db_column="LogId",
        verbose_name="شناسه تاریخچه"
    )

    student = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="educational_change_logs",
        db_column="StudentId",
        verbose_name="دانشجو"
    )

    change_type = models.CharField(
        max_length=30,
        choices=CHANGE_TYPE_CHOICES,
        db_column="ChangeType",
        verbose_name="نوع تغییر"
    )

    changed_by = models.ForeignKey(
        "core.UserAccount",
        on_delete=models.PROTECT,
        related_name="educational_change_logs",
        db_column="ChangedBy",
        verbose_name="کاربر ثبت‌کننده"
    )

    changed_at = models.DateTimeField(
        auto_now_add=True,
        db_column="ChangedAt",
        verbose_name="تاریخ و ساعت تغییر"
    )

    description = models.TextField(
        blank=True,
        default="",
        db_column="Description",
        verbose_name="توضیحات تغییر"
    )

    @property
    def change_type_label(self):
        return self.get_change_type_display()

    class Meta:
        db_table = "EducationalChangeLog"
        verbose_name = "تاریخچه تغییر آموزشی"
        verbose_name_plural = "تاریخچه تغییرات آموزشی"
        ordering = ["-changed_at"]

    def __str__(self):
        return (
            f"تغییر آموزشی {self.log_id} - "
            f"{self.student} - "
            f"{self.get_change_type_display()}"
        )
   
# ==========================================
# جدول Curriculum (چارت درسی)
# ==========================================
class Curriculum(models.Model):
    curriculum_id = models.AutoField(primary_key=True)
    field = models.ForeignKey('Field', on_delete=models.CASCADE, verbose_name="رشته تحصیلی")
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, verbose_name="درس")
    requirement_type = models.CharField(max_length=20, verbose_name="نوع درس در چارت")
    recommended_term = models.IntegerField(verbose_name="ترم پیشنهادی")
    calculated_units = models.IntegerField(verbose_name="تعداد واحد قابل محاسبه")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        db_table = 'Curriculum'
        verbose_name = "چارت درسی"
        verbose_name_plural = "چارت‌های درسی"


# ==========================================
# جدول Communication (ارتباطات و مکاتبات)
# ==========================================
class Communication(models.Model):
    communication_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey('UserAccount', on_delete=models.CASCADE, related_name='sent_messages', verbose_name="فرستنده")
    receiver = models.ForeignKey('UserAccount', on_delete=models.CASCADE, related_name='received_messages', verbose_name="گیرنده")
    subject = models.CharField(max_length=255, verbose_name="موضوع")
    message_body = models.TextField(verbose_name="متن پیام")
    communication_type = models.CharField(max_length=30, verbose_name="نوع مکاتبه")
    status = models.CharField(max_length=20, verbose_name="وضعیت")
    sent_at = models.DateTimeField(verbose_name="تاریخ ارسال")

    class Meta:
        db_table = 'Communication'
        verbose_name = "مکاتبه"
        verbose_name_plural = "مکاتبات"


# ==========================================
# جدول SystemSetting (تنظیمات پویای سیستم)
# ==========================================
class SystemSetting(models.Model):
    setting_id = models.AutoField(primary_key=True)
    setting_key = models.CharField(max_length=100, unique=True, verbose_name="کلید تنظیم")
    setting_value = models.CharField(max_length=255, verbose_name="مقدار تنظیم")
    data_type = models.CharField(max_length=20, verbose_name="نوع داده")
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")
    updated_by = models.ForeignKey('UserAccount', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="به‌روزرسانی‌کننده")

    class Meta:
        db_table = 'SystemSetting'
        verbose_name = "تنظیمات سیستم"
        verbose_name_plural = "تنظیمات سیستم"


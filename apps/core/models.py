from datetime import date

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone


# شخص (جایگزین User پیش‌فرض جنگو)
class Person(AbstractUser):

    GENDER_CHOICES = [
        ("F", "زن"),
        ("M", "مرد"),
    ]
    LANGUAGE_CHOICES = [
        ("fa", "فارسی"),
        ("en", "انگلیسی"),
    ]

    first_name = models.CharField("نام", max_length=100)
    last_name = models.CharField("نام خانوادگی", max_length=100)
    email = models.EmailField("ایمیل", max_length=254, unique=True)

    national_id = models.CharField(
        "کد ملی",
        max_length=10,
        unique=True,
        validators=[RegexValidator(r"^\d{10}$", "کد ملی باید دقیقاً ۱۰ رقم باشد.")],
    )
    birth_date = models.DateField("تاریخ تولد")
    gender = models.CharField("جنسیت", max_length=1, choices=GENDER_CHOICES)
    address = models.CharField("آدرس", max_length=200, blank=True)

    profile_image_path = models.CharField(
        "مسیر تصویر پروفایل",
        max_length=255,
        blank=True,
        help_text="برای صدور کارت دانشجویی دیجیتال",
    )
    preferred_language = models.CharField(
        "زبان ترجیحی",
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default="fa",
        help_text="پشتیبانی از فارسی و راست‌چین (NFUP01)",
    )
    is_notification_enabled = models.BooleanField(
        "دریافت اعلان فعال", default=True, help_text="FUOP05"
    )
    birth_place = models.CharField(
        "محل تولد", max_length=100, help_text="برای مدارک رسمی (04FUFP)"
    )
    updated_at = models.DateTimeField("تاریخ آخرین ویرایش", auto_now=True)

    REQUIRED_FIELDS = ["email", "national_id", "birth_date"]

    class Meta:
        db_table = "Person"
        verbose_name = "شخص"
        verbose_name_plural = "اشخاص"
        ordering = ["last_name", "first_name"]
        # جلوگیری از ثبت تکراری یک نفر (علاوه بر یکتا بودن کد ملی)
        unique_together = [
            ("first_name", "last_name", "birth_date", "birth_place"),
        ]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        """نام کامل (محاسباتی)"""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        """سن بر اساس تاریخ تولد (محاسباتی)"""
        today = date.today()
        had_birthday = (today.month, today.day) >= (
            self.birth_date.month,
            self.birth_date.day,
        )
        return today.year - self.birth_date.year - (0 if had_birthday else 1)


# استاد
class Teacher(models.Model):
    RANK_CHOICES = [
        ("instructor", "مربی"),
        ("assistant", "استادیار"),
        ("associate", "دانشیار"),
        ("professor", "استاد"),
    ]

    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        related_name="teacher",
        verbose_name="شخص",
    )
    teacher_code = models.CharField(
        "کد استاد", max_length=20, unique=True, help_text="مثال: T-1001"
    )
    department = models.ForeignKey(
        "Department",
        on_delete=models.PROTECT,
        related_name="teachers",
        verbose_name="گروه آموزشی",
    )
    academic_rank = models.CharField("مرتبه علمی", max_length=10, choices=RANK_CHOICES)
    hire_date = models.DateField("تاریخ استخدام")

    class Meta:
        db_table = "Teacher"
        verbose_name = "استاد"
        verbose_name_plural = "اساتید"
        ordering = ["teacher_code"]

    def __str__(self):
        return f"{self.teacher_code} - {self.person.full_name}"

    @property
    def years_of_service(self):
        """سابقه همکاری با دانشگاه به سال (محاسباتی)"""
        today = date.today()
        years = today.year - self.hire_date.year
        if (today.month, today.day) < (self.hire_date.month, self.hire_date.day):
            years -= 1
        return max(years, 0)


# دانشجو
class Student(models.Model):
    LEVEL_CHOICES = [
        ("associate", "کاردانی"),
        ("bachelor", "کارشناسی"),
        ("master", "ارشد"),
        ("phd", "دکتری"),
    ]
    STATUS_CHOICES = [
        ("active", "فعال"),
        ("leave", "مرخصی"),
        ("probation", "مشروط"),
        ("graduated", "فارغ‌التحصیل"),
        ("withdrawn", "انصراف"),
    ]

    MAX_TERMS = {"associate": 6, "bachelor": 8, "master": 4, "phd": 8}
    PROBATION_GPA = 12

    person = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="student_records",
        verbose_name="شخص",
    )
    student_code = models.CharField("شماره دانشجویی", max_length=20, unique=True)
    educational_level = models.CharField(
        "مقطع تحصیلی", max_length=10, choices=LEVEL_CHOICES
    )
    field = models.ForeignKey(
        "Field",
        on_delete=models.PROTECT,
        related_name="students",
        verbose_name="رشته تحصیلی",
    )
    application_date = models.DateField("تاریخ شروع تحصیل")
    status = models.CharField(
        "وضعیت تحصیلی", max_length=10, choices=STATUS_CHOICES, default="active"
    )
    admission_type = models.CharField(
        "نوع پذیرش", max_length=100, help_text="مثلا با آزمون، با معدل"
    )

    previous_term_gpa = models.DecimalField(
        "معدل ترم قبل",
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        help_text="کنترل حداقل و حداکثر واحد (FUFD04)؛ برای ترم اول خالی است",
    )
    total_gpa = models.DecimalField(
        "معدل کل",
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        help_text="نمایش وضعیت تحصیلی و مشروطی",
    )
    passed_units = models.PositiveIntegerField(
        "تعداد واحد گذرانده‌شده", default=0, help_text="حذف اضطراری (FUFP04)"
    )
    tuition_debt = models.DecimalField(
        "مبلغ بدهی شهریه",
        max_digits=12,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="مسدودسازی انتخاب واحد (FUFD05)؛ باید رمزنگاری شود (NFSP)",
    )
    completed_terms = models.PositiveSmallIntegerField(
        "تعداد ترم‌های گذرانده‌شده", default=0, help_text="هشدار سنوات (25FUOP)"
    )

    class Meta:
        db_table = "Student"
        verbose_name = "دانشجو"
        verbose_name_plural = "دانشجویان"
        ordering = ["student_code"]
        # یک شخص در یک مقطع نمی‌تواند دو پرونده دانشجویی داشته باشد
        unique_together = [("person", "educational_level")]

    def __str__(self):
        return f"{self.student_code} - {self.person.full_name}"

    @property
    def is_on_probation(self):
        """مشروط بودن (معدل کل کمتر از ۱۲)"""
        return self.total_gpa is not None and self.total_gpa < self.PROBATION_GPA

    @property
    def can_register_courses(self):
        """بدهی شهریه انتخاب واحد را مسدود می‌کند (FUFD05)"""
        return self.tuition_debt == 0

    @property
    def max_allowed_units(self):
        """سقف واحد مجاز بر اساس معدل ترم قبل (FUFD04) - ضوابط نمونه"""
        gpa = self.previous_term_gpa
        if gpa is None or gpa >= 17:
            return 24
        if gpa >= self.PROBATION_GPA:
            return 20
        return 14

    @property
    def remaining_terms(self):
        """ترم‌های باقی‌مانده تا سقف سنوات مقطع (25FUOP)"""
        return max(self.MAX_TERMS[self.educational_level] - self.completed_terms, 0)


# درس
class Lesson(models.Model):

    pass


# ترم
class Term(models.Model):
    SEMESTER_CHOICES = [
        ("mehr", "مهر"),
        ("bahman", "بهمن"),
        ("summer", "تابستان"),
    ]

    term_code = models.CharField("کد ترم", max_length=20, unique=True)
    semester = models.CharField("نیمسال", max_length=10, choices=SEMESTER_CHOICES)
    academic_year = models.CharField(
        "سال تحصیلی", max_length=9, help_text="مثال: 1405-1406"
    )
    start_date = models.DateField("تاریخ شروع ترم")
    end_date = models.DateField("تاریخ پایان ترم")
    registration_start = models.DateTimeField("شروع انتخاب واحد")
    registration_end = models.DateTimeField("پایان انتخاب واحد")
    add_drop_start = models.DateTimeField("شروع حذف و اضافه")
    add_drop_end = models.DateTimeField("پایان حذف و اضافه")
    emergency_drop_start = models.DateTimeField("شروع حذف اضطراری")
    emergency_drop_end = models.DateTimeField("پایان حذف اضطراری")
    is_active = models.BooleanField("فعال", default=False)

    class Meta:
        db_table = "Term"
        verbose_name = "ترم"
        verbose_name_plural = "ترم‌ها"
        ordering = ["-start_date"]
        # در هر سال تحصیلی هر نیمسال فقط یک بار تعریف می‌شود
        unique_together = [("semester", "academic_year")]

    def __str__(self):
        return f"{self.get_semester_display()} {self.academic_year}"

    def clean(self):
        """پایان هر بازه باید بعد از شروع آن باشد (FUID03)"""
        pairs = [
            (self.start_date, self.end_date, "تاریخ پایان ترم"),
            (self.registration_start, self.registration_end, "پایان انتخاب واحد"),
            (self.add_drop_start, self.add_drop_end, "پایان حذف و اضافه"),
            (self.emergency_drop_start, self.emergency_drop_end, "پایان حذف اضطراری"),
        ]
        for start, end, label in pairs:
            if start and end and end <= start:
                raise ValidationError(f"{label} باید بعد از شروع آن باشد.")

    @property
    def is_registration_open(self):
        return self.registration_start <= timezone.now() <= self.registration_end

    @property
    def is_add_drop_open(self):
        return self.add_drop_start <= timezone.now() <= self.add_drop_end

    @property
    def is_emergency_drop_open(self):
        return self.emergency_drop_start <= timezone.now() <= self.emergency_drop_end


# پرداخت
class Payment(models.Model):
    pass


# امتحان
class Exam(models.Model):
    offering = models.ForeignKey('CourseOffering', on_delete=models.CASCADE)
    exam_date = models.DateField()
    exam_type = models.CharField(
        max_length=20,
        choices=[
            ('midterm', 'میان‌ترم'),
            ('final', 'پایان‌ترم'),
            ('virtual', 'مجازی'),
        ],
    )


# گروه کلاسی
class LessonGroups(models.Model):
    pass


# مجوزهای پارکینگ
class ParkingPasses(models.Model):
    pass


# نقش
class Role(models.Model):
    
    # شناسه یکتا 
     role_id = models.AutoField(primary_key=True, verbose_name="شناسه نقش")
    
    # نام نقش (مثلاً: مدیر سیستم، استاد، دانشجو)
role_name = models.CharField(max_length=100, unique=True, verbose_name="نام نقش")
    
    # کد نقش (برای استفاده در سیستم؛ مثلاً ADMIN, TEACHER, STUDENT)
role_code = models.CharField(max_length=50, unique=True, verbose_name="کد نقش")
    
    # توضیحات (اختیاری)
description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    
    # وضعیت (آیا این نقش در حال حاضر فعال است؟)
is_active = models.BooleanField(default=True, verbose_name="وضعیت فعال بودن")
    
    # تاریخ ایجاد (به صورت خودکار زمان ثبت را ذخیره می‌کند)
created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")

def __str__(self):
        return self.role_name

class Meta:
        # برای اینکه در پنل ادمین اسمش به فارسی نمایش داده شود
        verbose_name = "نقش"
        verbose_name_plural = "نقش‌ها"
    


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
    
    # 1. درس اصلی که دانشجو می‌خواد برداره (مثلاً ریاضی ۲)
    lesson = models.ForeignKey(
        Lesson, 
        on_delete=models.CASCADE, 
        related_name='prerequisites', 
        verbose_name="درس اصلی"
    )
    
    # 2. درسی که باید از قبل پاس شده باشه (مثلاً ریاضی ۱)
    prerequisite_lesson = models.ForeignKey(
        Lesson, 
        on_delete=models.CASCADE, 
        related_name='is_prerequisite_for', 
        verbose_name="درس پیش‌نیاز"
    )
    
    # 3. آیا دانشجو باید حتماً نمره قبولی (حداقل ۱۰) آورده باشه؟ (پیش‌فرض بله)
    is_mandatory = models.BooleanField(default=True, verbose_name="اجباری بودن")

    def __str__(self):
        return f"{self.prerequisite_lesson} پیش‌نیاز برای {self.lesson}"

    class Meta:
        verbose_name = "پیش‌نیاز"
        verbose_name_plural = "پیش‌نیازها"
        # این خط خیلی مهمه: جلوی ثبت تکراری رو می‌گیره (مثلاً نمی‌شه دو بار گفت ریاضی ۱ پیش‌نیاز ریاضی ۲ است)
        unique_together = ('lesson', 'prerequisite_lesson')
    


# کلاس/مکان
class Classroom(models.Model):
    building_name = models.TextField()
    room_number = models.TextField()
    capacity = models.IntegerField()
    classroom_type = models.TextField()


# اعضای گروه کلاسی
class LessonGroupMember(models.Model):
    pass


# ارائه درس در ترم
class CourseOffering(models.Model):
    pass


# انتخاب واحد
class Enrollment(models.Model):
    
    # تعریف گزینه‌های ثابت برای وضعیت درس (برای اینکه دیتای اشتباه ثبت نشه)
    STATUS_CHOICES = (
        ('REGISTERED', 'در حال تحصیل (ثبت‌نام شده)'),
        ('PASSED', 'پاس شده'),
        ('FAILED', 'افتاده'),
        ('DROPPED', 'حذف شده'),
    )

    # 1. اتصال به جدول دانشجو
    student = models.ForeignKey(
        'Student', 
        on_delete=models.CASCADE, 
        related_name='enrollments', 
        verbose_name="دانشجو"
    )
    
    # 2. اتصال به جدول درس
    lesson = models.ForeignKey(
        Lesson, 
        on_delete=models.CASCADE, 
        related_name='enrollments', 
        verbose_name="درس"
    )
    
    # 3. ترم تحصیلی (مثلاً 14031 یا 14032)
    semester = models.CharField(max_length=20, verbose_name="ترم تحصیلی")
    
    # 4. نوع ثبت‌نام (از روی عکسی که فرستادی - مثلاً با آزمون، بدون آزمون)
    enrollment_type = models.CharField(max_length=50, verbose_name="نوع ثبت‌نام")
    
    # 5. وضعیت درس در آن ترم
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='REGISTERED', 
        verbose_name="وضعیت"
    )
    
    # 6. تاریخ ثبت‌نام (خودکار پر میشه)
    enrollment_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت‌نام")
    
    # 7. تاریخ حذف (اگر درس رو حذف کرد)
    drop_date = models.DateField(null=True, blank=True, verbose_name="تاریخ حذف")

    def __str__(self):
        return f"{self.student} - {self.lesson} ({self.semester})"

    class Meta:
        verbose_name = "انتخاب واحد"
        verbose_name_plural = "انتخاب واحدها"
        # نکته طلایی: یک دانشجو توی یک ترم نمی‌تونه یک درس رو دو بار انتخاب کنه!
        unique_together = ('student', 'lesson', 'semester')
    


# نمره
class Grade(models.Model):
    pass


# اعتراض به نمره
class GradeAppeal(models.Model):
    enrollment = models.ForeignKey('Enrollment', on_delete=models.CASCADE)
    appeal_reason = models.TextField()
    appeal_date = models.DateTimeField()
    appeal_status = models.CharField(
        max_length=30,
        choices=[
            ('pending', 'در انتظار بررسی'),
            ('approved', 'تأیید'),
            ('rejected', 'رد'),
        ],
    )


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
    db_column="CourseCompatibilityResult",
    verbose_name="نتیجه بررسی دروس"
)

class Meta:
    db_table = "TransferRequest"
    verbose_name = "درخواست مهمانی دروس"
    verbose_name_plural = "درخواست‌های مهمانی دروس"

def __str__(self):
    return (
        f"درخواست مهمانی {self.transfer_id} - "
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

class Meta:
    db_table = "GraduationAudit"
    verbose_name = "بررسی فارغ‌التحصیلی"
    verbose_name_plural = "بررسی‌های فارغ‌التحصیلی"

def __str__(self):
    return (
        f"بررسی فارغ‌التحصیلی {self.audit_id} - "
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

class Meta:
    db_table = "EducationalChangeLog"
    verbose_name = "تاریخچه تغییرات آموزشی"
    verbose_name_plural = "تاریخچه تغییرات آموزشی"
    ordering = ["-changed_at"]

def __str__(self):
    return (
        f"تغییر آموزشی {self.log_id} - "
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


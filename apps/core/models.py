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
    pass


# دسته بندی تیکت ها
class TicketCategory(models.Model):
    pass


# برگزاری کلاس مجازی
class OnlineClass(models.Model):
    pass


# رسید شهریه
class TuitionReceipt(models.Model):
    pass


# درخواست بازپرداخت وجه
class RefundRequest(models.Model):
    pass


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
    pass


# درخواست بورسیه
class ScholarshipApplication(models.Model):
    pass


# جلسات مشاوره
class CounselingAppointment(models.Model):
    pass


# پروپوزال
class Proposal(models.Model):
    pass

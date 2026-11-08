from datetime import date

from django.contrib.auth.models import AbstractUser
<<<<<<< HEAD
=======
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

from django.db.models.fields.related import _OnDeleteOptions
from .constants import TicketCreatorRoleChoices, TicketStatusChoices
from django.utils import timezone
from .constants import (
    AcademicRankChoices,
    AdmissionTypeChoices,
    EducationalLevelChoices,
    GenderChoices,
    SemesterChoices,
    StudentStatusChoices,
)
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e


# شخص (جایگزین User پیش‌فرض جنگو)
class Person(AbstractUser):
<<<<<<< HEAD
    pass


# استاد
class Teacher(Person):
    pass


# دانشجو
class Student(Person):
    pass
=======
    LANGUAGE_CHOICES = [
        ("fa", "فارسی"),
        ("en", "انگلیسی"),
    ]

    # بازتعریف برای اجباری شدن و verbose_name فارسی
    first_name = models.CharField(verbose_name="نام", max_length=100)
    last_name = models.CharField(verbose_name="نام خانوادگی", max_length=100)
    email = models.EmailField(verbose_name="ایمیل", max_length=254, unique=True)

    national_id = models.CharField(
        verbose_name="کد ملی",
        max_length=10,
        unique=True,
        validators=[RegexValidator(r"^\d{10}$", "کد ملی باید دقیقاً ۱۰ رقم باشد.")],
    )
    birth_date = models.DateField(verbose_name="تاریخ تولد")
    gender = models.CharField(
        verbose_name="جنسیت", max_length=6, choices=GenderChoices.choices
    )
    address = models.CharField(verbose_name="آدرس", max_length=200, blank=True)

    profile_image_path = models.CharField(
        verbose_name="مسیر تصویر پروفایل",
        max_length=255,
        blank=True,
        help_text="برای صدور کارت دانشجویی دیجیتال",
    )
    preferred_language = models.CharField(
        verbose_name="زبان ترجیحی",
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default="fa",
        help_text="پشتیبانی از فارسی و راست‌چین (NFUP01)",
    )
    is_notification_enabled = models.BooleanField(
        verbose_name="دریافت اعلان فعال", default=True, help_text="FUOP05"
    )
    birth_place = models.CharField(
        verbose_name="محل تولد", max_length=100, help_text="برای مدارک رسمی (04FUFP)"
    )
    updated_at = models.DateTimeField(verbose_name="تاریخ آخرین ویرایش", auto_now=True)

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

    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        related_name="teacher",
        verbose_name="شخص",
    )
    teacher_code = models.CharField(
        verbose_name="کد استاد", max_length=20, unique=True, help_text="مثال: T-1001"
    )
    department = models.ForeignKey(
        "Department",
        on_delete=models.PROTECT,
        related_name="teachers",
        verbose_name="گروه آموزشی",
    )
    academic_rank = models.CharField(
        verbose_name="مرتبه علمی", max_length=20, choices=AcademicRankChoices.choices
    )
    hire_date = models.DateField(verbose_name="تاریخ استخدام")

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
        id=models.BigAutoField(primary_key=True),
    )

    person = models.OneToOneField(
        Person, on_delete=models.CASCADE, related_name="student"
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

    student_code = models.CharField(max_length=20)

    educational_level = models.CharField(max_length=30)

    application_date = models.DateField(auto_now_add=True)
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e


# درس
class Lesson(models.Model):
<<<<<<< HEAD
=======

    lesson_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='کد درس'
    )

    title = models.CharField(
        max_length=200,
        verbose_name='عنوان درس'
    )

    practical_units = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='واحد عملی'
    )

    theory_units = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='واحد نظری'
    )

    lesson_type = models.CharField(
        max_length=20,
        choices=[
            ('general', 'عمومی'),
            ('basic', 'پایه'),
            ('specialized', 'تخصصی'),
            ('elective', 'اختیاری'),
        ],
        verbose_name='نوع درس'
    )

    department = models.ForeignKey(
        'Department',
        on_delete=models.PROTECT,
        related_name='lessons',
        verbose_name='گروه آموزشی'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت'
    )

    def __str__(self):
        return f'{self.lesson_code} - {self.title}'

    class Meta:
        verbose_name = 'درس'
        verbose_name_plural = 'دروس'

        ordering = ['title']

        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(practical_units__gt=0) |
                    models.Q(theory_units__gt=0)
                ),
                name='lesson_has_units'
            ),
        ]

# ترم
class Student(models.Model):

    MAX_TERMS = {
        EducationalLevelChoices.ASSOCIATE: 6,
        EducationalLevelChoices.BACHELOR: 8,
        EducationalLevelChoices.MASTER: 4,
        EducationalLevelChoices.PHD: 8,
    }
    PROBATION_GPA = 12
    HIGH_GPA = 17
    MAX_UNITS_HIGH_GPA = 24
    MAX_UNITS_NORMAL = 20
    MAX_UNITS_PROBATION = 14

    person = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="student_records",
        verbose_name="شخص",
    )
    student_code = models.CharField(
        verbose_name="شماره دانشجویی", max_length=20, unique=True
    )
    educational_level = models.CharField(
        verbose_name="مقطع تحصیلی",
        max_length=10,
        choices=EducationalLevelChoices.choices,
    )
    field = models.ForeignKey(
        "Field",
        on_delete=models.PROTECT,
        related_name="students",
        verbose_name="رشته تحصیلی",
    )
    application_date = models.DateField(verbose_name="تاریخ شروع تحصیل")
    status = models.CharField(
        verbose_name="وضعیت تحصیلی",
        max_length=10,
        choices=StudentStatusChoices.choices,
        default=StudentStatusChoices.ACTIVE,
    )
    admission_type = models.CharField(
        verbose_name="نوع پذیرش", max_length=20, choices=AdmissionTypeChoices.choices
    )

    previous_term_gpa = models.DecimalField(
        verbose_name="معدل ترم قبل",
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        help_text="کنترل حداقل و حداکثر واحد (FUFD04)؛ برای ترم اول خالی است",
    )
    total_gpa = models.DecimalField(
        verbose_name="معدل کل",
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        help_text="نمایش وضعیت تحصیلی و مشروطی",
    )
    passed_units = models.PositiveIntegerField(
        verbose_name="تعداد واحد گذرانده‌شده",
        default=0,
        help_text="حذف اضطراری (FUFP04)",
    )
    tuition_debt = models.DecimalField(
        verbose_name="مبلغ بدهی شهریه",
        max_digits=12,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="مسدودسازی انتخاب واحد (FUFD05)؛ باید رمزنگاری شود (NFSP)",
    )
    completed_terms = models.PositiveSmallIntegerField(
        verbose_name="تعداد ترم‌های گذرانده‌شده",
        default=0,
        help_text="هشدار سنوات (25FUOP)",
    )

    class Meta:
        db_table = "Student"
        verbose_name = "دانشجو"
        verbose_name_plural = "دانشجویان"
        ordering = ["student_code"]
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
        if gpa is None or gpa >= self.HIGH_GPA:
            return self.MAX_UNITS_HIGH_GPA
        if gpa >= self.PROBATION_GPA:
            return self.MAX_UNITS_NORMAL
        return self.MAX_UNITS_PROBATION

    @property
    def remaining_terms(self):
        """ترم‌های باقی‌مانده تا سقف سنوات مقطع (25FUOP)"""
        return max(self.MAX_TERMS[self.educational_level] - self.completed_terms, 0)


# درس
class Lesson(models.Model):
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e
    pass


# ترم
class Term(models.Model):
<<<<<<< HEAD
    pass
=======

    term_code = models.CharField(
        verbose_name="کد ترم",
        max_length=20,
        unique=True,
        null=False,
        blank=False,
        help_text="کد یکتای ترم، مثال: 14051",
    )
    semester = models.CharField(
        verbose_name="نیمسال",
        max_length=10,
        choices=SemesterChoices.choices,
        null=False,
        blank=False,
    )
    academic_year = models.CharField(
        verbose_name="سال تحصیلی",
        max_length=9,
        null=False,
        blank=False,
        validators=[
            RegexValidator(r"^\d{4}-\d{4}$", "فرمت سال تحصیلی باید مثل 1405-1406 باشد.")
        ],
        help_text="مثال: 1405-1406",
    )
    start_date = models.DateField(
        verbose_name="تاریخ شروع ترم",
        null=False,
        blank=False,
        help_text="تاریخ شروع کلاس‌های ترم",
    )
    end_date = models.DateField(
        verbose_name="تاریخ پایان ترم",
        null=False,
        blank=False,
        help_text="تاریخ پایان کلاس‌های ترم",
    )
    registration_start = models.DateTimeField(
        verbose_name="شروع انتخاب واحد",
        null=False,
        blank=False,
        help_text="بازه انتخاب واحد توسط مدیر تعریف می‌شود (FUID03)",
    )
    registration_end = models.DateTimeField(
        verbose_name="پایان انتخاب واحد",
        null=False,
        blank=False,
        help_text="FUID03",
    )
    add_drop_start = models.DateTimeField(
        verbose_name="شروع حذف و اضافه",
        null=False,
        blank=False,
        help_text="FUID03",
    )
    add_drop_end = models.DateTimeField(
        verbose_name="پایان حذف و اضافه",
        null=False,
        blank=False,
        help_text="FUID03",
    )
    emergency_drop_start = models.DateTimeField(
        verbose_name="شروع حذف اضطراری",
        null=False,
        blank=False,
        help_text="بعد از پایان حذف و اضافه شروع می‌شود (FUFP04)",
    )
    emergency_drop_end = models.DateTimeField(
        verbose_name="پایان حذف اضطراری",
        null=False,
        blank=False,
        help_text="FUFP04",
    )
    is_active = models.BooleanField(
        verbose_name="فعال",
        default=False,
        help_text="فقط یک ترم می‌تواند هم‌زمان فعال باشد",
    )

    class Meta:
        db_table = "Term"
        verbose_name = "ترم"
        verbose_name_plural = "ترم‌ها"
        ordering = ["-start_date"]
        unique_together = [("semester", "academic_year")]
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=models.Q(is_active=True),
                name="only_one_active_term",
            ),
        ]

    def __str__(self):
        return f"{self.get_semester_display()} {self.academic_year}"

    def clean(self):
        """پایان هر بازه باید بعد از شروع آن باشد و حذف اضطراری بعد از حذف و اضافه بیاید"""
        pairs = [
            (self.start_date, self.end_date, "تاریخ پایان ترم"),
            (self.registration_start, self.registration_end, "پایان انتخاب واحد"),
            (self.add_drop_start, self.add_drop_end, "پایان حذف و اضافه"),
            (self.emergency_drop_start, self.emergency_drop_end, "پایان حذف اضطراری"),
        ]
        for start, end, label in pairs:
            if start and end and end <= start:
                raise ValidationError(f"{label} باید بعد از شروع آن باشد.")
        if (
            self.emergency_drop_start
            and self.add_drop_end
            and self.emergency_drop_start < self.add_drop_end
        ):
            raise ValidationError("حذف اضطراری باید بعد از پایان حذف و اضافه شروع شود.")

    @property
    def is_registration_open(self):
        return self.registration_start <= timezone.now() <= self.registration_end

    @property
    def is_add_drop_open(self):
        return self.add_drop_start <= timezone.now() <= self.add_drop_end

    @property
    def is_emergency_drop_open(self):
        return self.emergency_drop_start <= timezone.now() <= self.emergency_drop_end
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e


# پرداخت

class Payment(models.Model):

    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('successful', 'موفق'),
        ('failed', 'ناموفق'),
        ('refunded', 'بازپرداخت شده'),
    ]

    term = models.ForeignKey(
        'Term',
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='نیمسال تحصیلی'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='مبلغ پرداخت'
    )

    payment_date = models.DateTimeField(
        verbose_name='تاریخ پرداخت'
    )

    tracking_code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='کد پیگیری'
    )

    student = models.ForeignKey(
        'Student',
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name='دانشجو'
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت پرداخت'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت'
    )

    def __str__(self):
        return f'{self.tracking_code} - {self.amount}'
    class Meta:

        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت‌ها'

        ordering = ['-created_at']

        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name='payment_amount_must_be_positive'
            ),
        ]



# امتحان
class Exam(models.Model):
<<<<<<< HEAD
    pass
=======
    offering = models.ForeignKey("CourseOffering", on_delete=models.CASCADE)
    exam_date = models.DateField()
    exam_type = models.CharField(
        max_length=20,
        choices=[
            ("midterm", "میان‌ترم"),
            ("final", "پایان‌ترم"),
            ("virtual", "مجازی"),
        ],
    )
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e


# گروه کلاسی
class LessonGroups(models.Model):
<<<<<<< HEAD
    pass


# مجوزهای پارکینگ
class ParkingPasses(models.Model):
    pass
=======
    id = models.BigIntegerField(primary_key=True)

    name = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    created_by = models.ForeignKey(
        Person, on_delete=models.CASCADE, related_name="lesson_groups"
    )

    members = models.ManyToManyField(Person, related_name="lesson_groups")

    teacher = models.ForeignKey(
        Teacher, on_delete=models.DO_NOTHING, related_name="lesson_groups"
    )

    is_active = models.BooleanField(default=True)


# مجوزهای پارکینگ
class ParkingPasses(models.Model):
    id = models.BigAutoField(primary_key=True)

    parking_pass_code = models.CharField(max_length=50)

    aquisition_date = models.DateField(auto_now_add=True)

    expiration_date = models.DateField

    charge = models.BigIntegerField

    owner = models.OneToOneField(
        Person, on_delete=models.CASCADE, related_name="parking_pass"
    )
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e


# نقش
class Role(models.Model):
<<<<<<< HEAD
    pass


# حساب کاربری
class UserAccount(models.Model):
    pass
=======

    # نام نقش
    role_name = models.CharField(
        max_length=100,
        verbose_name="عنوان نقش"
    )

    # توضیحات نقش
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="توضیح"
    )

    # تاریخ ایجاد نقش
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت"
    )

    # وضعیت فعال بودن نقش
    is_active = models.BooleanField(
        default=True,
        verbose_name="وضعیت فعال"
    )

    def __str__(self):
        return self.role_name

    class Meta:
        verbose_name = "نقش"
        verbose_name_plural = "نقش‌ها"
    


# حساب کاربری
class UserAccount(
    models.Model
):  # مدل حساب کاربری؛ Django از آن جدول پایگاه داده می‌سازد

    user_id = models.AutoField(
        primary_key=True,  # شناسهٔ اصلی و یکتای هر حساب؛ خودکار افزایش می‌یابد
        verbose_name="شناسه حساب کاربری",  # نام قابل‌نمایش فیلد در پنل مدیریت
    )

    person = models.ForeignKey(
        "Person",  # هر حساب به یک شخص از مدل Person متصل است
        on_delete=models.CASCADE,  # با حذف شخص، حساب او هم حذف می‌شود
        related_name="user_accounts",  # دسترسی از شخص به حساب‌هایش: person.user_accounts
        verbose_name="شخص",
    )

    role = models.ForeignKey(
        "Role",  # نقش این حساب را مشخص می‌کند؛ مثلاً دانشجو یا مدیر
        on_delete=models.PROTECT,  # تا وقتی حسابی از این نقش استفاده می‌کند، حذف نقش ممنوع است
        related_name="user_accounts",  # دسترسی از نقش به حساب‌های دارای آن نقش
        verbose_name="نقش",
    )

    username = models.CharField(
        max_length=150,  # حداکثر طول نام کاربری
        unique=True,  # هر نام کاربری باید یکتا باشد
        verbose_name="نام کاربری",
    )

    password = models.CharField(
        max_length=128, verbose_name="رمز عبور"  # طول فیلد ذخیرهٔ رمز هش‌شده
    )

    created_at = models.DateTimeField(
        auto_now_add=True,  # زمان ایجاد حساب را خودکار ذخیره می‌کند
        verbose_name="تاریخ ثبت",
    )

    is_active = models.BooleanField(
        default=True, verbose_name="فعال"  # حساب به‌صورت پیش‌فرض فعال است
    )

    failed_login_count = models.PositiveIntegerField(
        default=0,  # تعداد تلاش‌های ناموفق؛ عدد منفی نمی‌پذیرد
        verbose_name="تعداد تلاش ناموفق",
    )

    locked_until = models.DateTimeField(
        null=True,  # در دیتابیس می‌تواند خالی باشد
        blank=True,  # در فرم‌های Django هم اختیاری است
        verbose_name="قفل تا",
    )

    last_login_at = models.DateTimeField(
        null=True,  # ممکن است کاربر هنوز وارد نشده باشد
        blank=True,
        verbose_name="آخرین ورود",
    )

    last_activity_at = models.DateTimeField(
        null=True,  # ممکن است هنوز فعالیتی ثبت نشده باشد
        blank=True,
        verbose_name="آخرین فعالیت",
    )

    password_changed_at = models.DateTimeField(
        null=True,  # ممکن است زمان تغییر رمز هنوز ثبت نشده باشد
        blank=True,
        verbose_name="تاریخ تغییر رمز",
    )

    def __str__(self):
        return self.username  # هنگام نمایش حساب، نام کاربری را نشان می‌دهد
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e


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
<<<<<<< HEAD
    pass
=======

    # شناسه یکتای پیش‌نیاز
    prereq_id = models.AutoField(
        primary_key=True,
        db_column='PrereqID',
        verbose_name="شناسه پیش‌نیاز"
    )

    # درس اصلی
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='prerequisites',
        db_column='LessonID',
        verbose_name="درس اصلی"
    )

    # درس پیش‌نیاز یا هم‌نیاز
    prerequisite_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='is_prerequisite_for',
        db_column='PrereqLessonID',
        verbose_name="درس پیش‌نیاز یا هم‌نیاز"
    )

    # نوع رابطه
    prerequisite_type = models.CharField(
        max_length=50,
        choices=[
            ('prerequisite', 'پیش‌نیاز'),
            ('corequisite', 'هم‌نیاز'),
        ],
        db_column='Type',
        verbose_name="نوع رابطه"
    )

    # تاریخ ثبت
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='CreatedAt',
        verbose_name="تاریخ ثبت"
    )

    def __str__(self):
        return f"{self.prerequisite_lesson} - {self.lesson}"

    class Meta:
        verbose_name = "پیش‌نیاز و هم‌نیاز"
        verbose_name_plural = "پیش‌نیازها و هم‌نیازها"

        unique_together = (
            ('lesson', 'prerequisite_lesson'),
        )
    
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e


# کلاس/مکان
class Classroom(models.Model):
    pass


# اعضای گروه کلاسی
class LessonGroupMember(models.Model):
    pass


# ارائه درس در ترم
class CourseOffering(models.Model):

    DAY_CHOICES = [
        ('saturday', 'شنبه'),
        ('sunday', 'یکشنبه'),
        ('monday', 'دوشنبه'),
        ('tuesday', 'سه‌شنبه'),
        ('wednesday', 'چهارشنبه'),
        ('thursday', 'پنجشنبه'),
        ('friday', 'جمعه'),
    ]

    lesson = models.ForeignKey(
        'Lesson',
        on_delete=models.PROTECT,
        related_name='course_offerings',
        verbose_name='درس'
    )

    term = models.ForeignKey(
        'Term',
        on_delete=models.PROTECT,
        related_name='course_offerings',
        verbose_name='نیمسال تحصیلی'
    )

    teacher = models.ForeignKey(
        'Teacher',
        on_delete=models.PROTECT,
        related_name='course_offerings',
        verbose_name='استاد'
    )

    capacity = models.PositiveIntegerField(
        verbose_name='ظرفیت کلاس'
    )

    remaining_capacity = models.PositiveIntegerField(
        verbose_name='ظرفیت باقی‌مانده'
    )

    day_of_week = models.CharField(
        max_length=20,
        choices=DAY_CHOICES,
        verbose_name='روز هفته'
    )

    start_time = models.TimeField(
        verbose_name='ساعت شروع'
    )

    end_time = models.TimeField(
        verbose_name='ساعت پایان'
    )

    classroom = models.ForeignKey(
        'Classroom',
        on_delete=models.PROTECT,
        related_name='course_offerings',
        verbose_name='کلاس'
    )

    exam_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاریخ امتحان'
    )

    exam_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name='ساعت امتحان'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='وضعیت فعال بودن ارائه'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت'
    )

    @property
    def duration_minutes(self):
        start = (
            self.start_time.hour * 60
            + self.start_time.minute
        )

        end = (
            self.end_time.hour * 60
            + self.end_time.minute
        )

        return end - start

    def __str__(self):
        return self.lesson.title

    class Meta:
     
     verbose_name = 'ارائه درس'
    verbose_name_plural = 'ارائه‌های درس'
    ordering = ['start_time']

    unique_together = [
        ('teacher', 'day_of_week', 'start_time', 'term'),
    ]
    constraints = [
            models.CheckConstraint(
                condition=models.Q(capacity__gt=0),
                name='offering_capacity_positive'
            ),

            models.CheckConstraint(
                condition=models.Q(
                    remaining_capacity__lte=models.F('capacity')
                ),
                name='remaining_capacity_valid'
            ),

            models.CheckConstraint(
                condition=models.Q(
                    end_time__gt=models.F('start_time')
                ),
                name='offering_end_time_valid'
            ),

            models.CheckConstraint(
                condition=(
                    models.Q(
                        exam_date__isnull=True,
                        exam_time__isnull=True
                    ) |
                    models.Q(
                        exam_date__isnull=False,
                        exam_time__isnull=False
                    )
                ),
                name='exam_date_time_consistent'
            ),
        ]


# انتخاب واحد
class Enrollment(models.Model):
<<<<<<< HEAD
    pass
=======

    # وضعیت‌های ثبت‌نام
    STATUS_CHOICES = (

        ('REGISTERED', 'ثبت‌نام شده'),
        ('PASSED', 'پاس شده'),
        ('FAILED', 'افتاده'),
        ('DROPPED', 'حذف شده'),
)
    
    

    # نوع ثبت‌نام
    TYPE_CHOICES = (
        ('NORMAL', 'عادی'),
        ('GUEST', 'مهمان'),
    )

    # شناسه ثبت‌نام
    EnrollmentId = models.AutoField(
        primary_key=True,
        verbose_name="شناسه ثبت‌نام"
    )

    # ارتباط با دانشجو
    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="دانشجو"
    )

    # تاریخ ثبت‌نام
    enrollment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت‌نام"
    )

    # وضعیت ثبت‌نام
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='REGISTERED',
        verbose_name="وضعیت ثبت‌نام"
    )

    # نوع ثبت‌نام
    enrollment_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='NORMAL',
        verbose_name="نوع ثبت‌نام"
    )

    # تاریخ حذف
    drop_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="تاریخ حذف"
    )

    def __str__(self):
        return f"{self.student} - {self.get_status_display()}"

    class Meta:
        verbose_name = "انتخاب واحد"
        verbose_name_plural = "انتخاب واحدها"
        # نکته طلایی: یک دانشجو توی یک ترم نمی‌تونه یک درس رو دو بار انتخاب کنه!
        unique_together = ("student", "lesson", "semester")
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e


# نمره
class Grade(models.Model):
    pass


# اعتراض به نمره
class GradeAppeal(models.Model):
<<<<<<< HEAD
    pass


# حضور و غیاب
class Attendance(models.Model):
    pass
=======
    enrollment = models.ForeignKey("Enrollment", on_delete=models.CASCADE)
    appeal_reason = models.TextField()
    appeal_date = models.DateTimeField()
    appeal_status = models.CharField(
        max_length=30,
        choices=[
            ("pending", "در انتظار بررسی"),
            ("approved", "تأیید"),
            ("rejected", "رد"),
        ],
    )


# حضور و غیاب
class Attendance(models.Model):  # مدل ثبت اطلاعات حضور و غیاب

    enrollment = models.ForeignKey(  # ارتباط این رکورد با ثبت‌نام هنرجو
        "Enrollment",  # نام مدل ثبت‌نام
        on_delete=models.CASCADE,  # با حذف ثبت‌نام، رکورد حضور و غیاب هم حذف می‌شود
    )

    session_number = models.IntegerField()  # شمارهٔ جلسه

    session_date = models.DateField()  # تاریخ برگزاری جلسه

    attendance_status = models.CharField(max_length=50)  # وضعیت حضور، مثل حاضر یا غایب

    attendance_time = models.TimeField()  # ساعت حضور یا ثبت وضعیت

    description = models.TextField()  # توضیحات تکمیلی

    recorded_by = models.ForeignKey(  # ارتباط با حساب کاربری ثبت‌کننده
        "UserAccount",  # نام مدل حساب کاربری
        on_delete=models.CASCADE,  # با حذف حساب کاربری، این رکورد هم حذف می‌شود
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )  # زمان ایجاد رکورد که خودکار ثبت می‌شود
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e


# تیکت
class Ticket(models.Model):
<<<<<<< HEAD
    creator_person_id = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='created_tickets')
    creator_role = models.CharField(max_length=20)
    category_id = models.ForeignKey('TicketCategory', on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=20)
    assigned_to_person_id = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

=======
    creator = models.ForeignKey(
        "Person",
        on_delete=models.CASCADE,
        related_name="created_tickets",
        verbose_name="سازنده",
    )
    creator_role = models.CharField(
        max_length=20,
        choices=TicketCreatorRoleChoices.choices,
        verbose_name="نقش سازنده",
    )
    category = models.ForeignKey(
        "TicketCategory",
        on_delete=models.CASCADE,
        related_name="tickets",
        verbose_name="دسته‌بندی",
    )
    subject = models.CharField(max_length=200, verbose_name="موضوع")
    content = models.CharField(max_length=1000, verbose_name="متن تیکت")
    status = models.CharField(
        max_length=20,
        choices=TicketStatusChoices.choices,
        default=TicketStatusChoices.OPEN,
        verbose_name="وضعیت",
    )
    assigned_to = models.ForeignKey(
        "Person",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
        verbose_name="مسئول پاسخگویی",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="تاریخ آخرین به‌روزرسانی"
    )

    class Meta:
        verbose_name = "تیکت"
        verbose_name_plural = "تیکت‌ها"
        ordering = ["-created_at"]
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e

# دسته بندی تیکت ها
class TicketCategory(models.Model):
    pass



# برگزاری کلاس مجازی
class OnlineClass(models.Model):
<<<<<<< HEAD
    teacher_id = models.ForeignKey('Teacher', on_delete=models.CASCADE)
    offering_id = models.ForeignKey('CourseOffering', on_delete=models.CASCADE)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    title = models.CharField(max_length=200)
    meeting_link = models.URLField()

=======
    teacher = models.ForeignKey(
        "Teacher",
        on_delete=models.CASCADE,
        related_name="online_classes",
        verbose_name="استاد",
    )
    offering = models.ForeignKey(
        "CourseOffering",
        on_delete=models.CASCADE,
        related_name="online_classes",
        verbose_name="ارائه درس",
    )
    start_at = models.DateTimeField(verbose_name="تاریخ و ساعت شروع")
    end_at = models.DateTimeField(verbose_name="تاریخ و ساعت پایان")
    title = models.CharField(max_length=200, verbose_name="عنوان جلسه")
    meeting_link = models.URLField(verbose_name="لینک جلسه")

    class Meta:
        verbose_name = "کلاس مجازی"
        verbose_name_plural = "کلاس‌های مجازی"
        ordering = ["start_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_at__gt=models.F("start_at")),
                name="online_class_end_after_start",
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def duration(self):
        return self.end_at - self.start_at

    @property
    def is_ongoing(self):
        return self.start_at <= timezone.now() <= self.end_at
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e


# رسید شهریه
class TuitionReceipt(models.Model):

    tuition_receipt_key = models.AutoField(
        primary_key=True,
        db_column="TuitionReceiptKey",
        verbose_name="شناسه رسید شهریه"
    )

    receipt_serial_code = models.CharField(
        max_length=50,
        unique=True,
        null=False,
        blank=False,
        db_column="ReceiptSerialCode",
        verbose_name="شماره سریال رسید"
    )

    receipt_payment_link = models.ForeignKey(
        "core.Payment",
        on_delete=models.PROTECT,
        related_name="tuition_receipts",
        null=False,
        blank=False,
        db_column="ReceiptPaymentLinkId",
        verbose_name="پرداخت مربوط به رسید"
    )

    receipt_issued_on = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=True,
        db_column="ReceiptIssuedOn",
        verbose_name="تاریخ صدور رسید"
    )

    receipt_document_uri = models.CharField(
        max_length=500,
        null=False,
        blank=True,
        db_column="ReceiptDocumentUri",
        verbose_name="آدرس فایل رسید"
    )

    class Meta:
        db_table = "TuitionReceipt"
        verbose_name = "رسید پرداخت شهریه"
        verbose_name_plural = "رسیدهای پرداخت شهریه"
        ordering = ["-receipt_issued_on"]

    def __str__(self):
        return f"رسید شماره {self.receipt_serial_code}"




# درخواست بازپرداخت وجه
class RefundRequest(models.Model):

    refund_case_key = models.AutoField(
        primary_key=True,
        db_column="RefundCaseKey",
        verbose_name="شناسه درخواست استرداد"
    )

    refund_payment_link = models.ForeignKey(
        "core.Payment",
        on_delete=models.PROTECT,
        related_name="refund_requests",
        null=False,
        blank=False,
        db_column="RefundPaymentLinkId",
        verbose_name="پرداخت مربوط به درخواست"
    )

    refund_value_requested = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=False,
        blank=False,
        db_column="RefundValueRequested",
        verbose_name="مبلغ درخواستی بازپرداخت"
    )

    refund_justification_text = models.TextField(
        null=False,
        blank=False,
        db_column="RefundJustificationText",
        verbose_name="دلیل درخواست استرداد"
    )

    refund_review_state = models.CharField(
        max_length=20,
        choices=RequestReviewStatusChoices.choices,
        default=RequestReviewStatusChoices.PENDING,
        null=False,
        blank=False,
        db_column="RefundReviewState",
        verbose_name="وضعیت بررسی درخواست"
    )

    class Meta:
        db_table = "RefundRequest"
        verbose_name = "درخواست استرداد وجه"
        verbose_name_plural = "درخواست‌های استرداد وجه"
        ordering = ["-refund_case_key"]

        constraints = [
            models.CheckConstraint(
                condition=Q(refund_value_requested__gt=0),
                name="refund_value_must_be_positive"
            )
        ]

    def __str__(self):
        return f"درخواست استرداد شماره {self.refund_case_key}"


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
    
    student_service_case_key = models.AutoField(
        primary_key=True,
        db_column="StudentServiceCaseKey",
        verbose_name="شناسه درخواست خدمات دانشجویی"
    )

    service_requester = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="service_requests",
        null=False,
        blank=False,
        db_column="ServiceRequesterLinkId",
        verbose_name="دانشجوی درخواست‌دهنده"
    )

    service_request_kind = models.CharField(
        max_length=30,
        choices=ServiceRequestTypeChoices.choices,
        null=False,
        blank=False,
        db_column="ServiceRequestKind",
        verbose_name="نوع درخواست خدمات"
    )

    service_request_data = models.TextField(
        null=False,
        blank=True,
        db_column="ServiceRequestData",
        verbose_name="اطلاعات تکمیلی درخواست"
    )

    service_decision_state = models.CharField(
        max_length=20,
        choices=RequestReviewStatusChoices.choices,
        default=RequestReviewStatusChoices.PENDING,
        null=False,
        blank=False,
        db_column="ServiceDecisionState",
        verbose_name="وضعیت تصمیم‌گیری درخواست"
    )

    class Meta:
        db_table = "StudentServiceRequest"
        verbose_name = "درخواست خدمات دانشجویی"
        verbose_name_plural = "درخواست‌های خدمات دانشجویی"
        ordering = ["-student_service_case_key"]

    def __str__(self):
        return (
            f"درخواست شماره {self.student_service_case_key} - "
            f"{self.get_service_request_kind_display()}"
        )


# درخواست بورسیه
class ScholarshipApplication(models.Model):
<<<<<<< HEAD
    pass
=======
    SCHOLARSHIP_STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("approved", "تأیید شده"),
        ("rejected", "رد شده"),
    ]

    scholarship_application_key = models.AutoField(
        primary_key=True, db_column="ScholarshipApplicationKey"
    )

    scholarship_applicant = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="scholarship_applications",
        db_column="ScholarshipApplicantLinkId",
    )

    scholarship_type = models.CharField(max_length=50, db_column="ScholarshipType")

    scholarship_reason = models.TextField(db_column="ScholarshipReason")

    scholarship_status = models.CharField(
        max_length=20,
        choices=SCHOLARSHIP_STATUS_CHOICES,
        default="pending",
        db_column="ScholarshipStatus",
    )

    scholarship_submitted_at = models.DateTimeField(
        auto_now_add=True, db_column="ScholarshipSubmittedAt"
    )

    class Meta:
        db_table = "ScholarshipApplication"

    def __str__(self):
        return f"درخواست بورسیه {self.scholarship_application_key}"
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e


# جلسات مشاوره
class CounselingAppointment(models.Model):
    pass

<<<<<<< HEAD
=======
    counseling_appointment_key = models.AutoField(
        primary_key=True, db_column="CounselingAppointmentKey"
    )

    counseling_student_link = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="counseling_appointments",
        db_column="CounselingStudentLinkId",
    )

    counseling_teacher_link = models.ForeignKey(
        "core.Teacher",
        on_delete=models.PROTECT,
        related_name="counseling_appointments",
        db_column="CounselingTeacherLinkId",
    )

    counseling_date = models.DateTimeField(db_column="CounselingDate")

    counseling_topic = models.CharField(max_length=255, db_column="CounselingTopic")

    counseling_description = models.TextField(
        blank=True, db_column="CounselingDescription"
    )

    counseling_status = models.CharField(
        max_length=20,
        choices=COUNSELING_STATUS_CHOICES,
        default="pending",
        db_column="CounselingStatus",
    )

    class Meta:
        db_table = "CounselingAppointment"

    def __str__(self):
        return f"جلسه مشاوره {self.counseling_appointment_key}"
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e


# پروپوزال
class Proposal(models.Model):
    pass

<<<<<<< HEAD
#درخواست مهمانی دروس
=======
    proposal_case_key = models.AutoField(primary_key=True, db_column="ProposalCaseKey")

    proposal_student_link = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="proposals",
        db_column="ProposalStudentLinkId",
    )

    proposal_title = models.CharField(max_length=255, db_column="ProposalTitle")

    proposal_description = models.TextField(db_column="ProposalDescription")

    proposal_submitted_at = models.DateTimeField(
        auto_now_add=True, db_column="ProposalSubmittedAt"
    )

    proposal_status = models.CharField(
        max_length=20,
        choices=PROPOSAL_STATUS_CHOICES,
        default="pending",
        db_column="ProposalStatus",
    )

    class Meta:
        db_table = "Proposal"

    def __str__(self):
        return self.proposal_title


# درخواست مهمانی دروس
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e
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

<<<<<<< HEAD
#بررسی شرایط فارغ تحصیلی
=======

# بررسی شرایط فارغ‌التحصیلی
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e
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
<<<<<<< HEAD
        return (
            f"تغییر آموزشی {self.log_id} - "
            f"{self.student} - "
            f"{self.get_change_type_display()}"
        )
   
=======
        return f"تغییر آموزشی {self.log_id} - " f"{self.get_change_type_display()}"


>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e
# ==========================================
# جدول Curriculum (چارت درسی)
# ==========================================
class Curriculum(models.Model):
    curriculum_id = models.AutoField(primary_key=True)
    field = models.ForeignKey(
        "Field", on_delete=models.CASCADE, verbose_name="رشته تحصیلی"
    )
    lesson = models.ForeignKey("Lesson", on_delete=models.CASCADE, verbose_name="درس")
    requirement_type = models.CharField(max_length=20, verbose_name="نوع درس در چارت")
    recommended_term = models.IntegerField(verbose_name="ترم پیشنهادی")
    calculated_units = models.IntegerField(verbose_name="تعداد واحد قابل محاسبه")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        db_table = "Curriculum"
        verbose_name = "چارت درسی"
        verbose_name_plural = "چارت‌های درسی"


# ==========================================
# جدول Communication (ارتباطات و مکاتبات)
# ==========================================
class Communication(models.Model):
    communication_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(
        "UserAccount",
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name="فرستنده",
    )
    receiver = models.ForeignKey(
        "UserAccount",
        on_delete=models.CASCADE,
        related_name="received_messages",
        verbose_name="گیرنده",
    )
    subject = models.CharField(max_length=255, verbose_name="موضوع")
    message_body = models.TextField(verbose_name="متن پیام")
    communication_type = models.CharField(max_length=30, verbose_name="نوع مکاتبه")
    status = models.CharField(max_length=20, verbose_name="وضعیت")
    sent_at = models.DateTimeField(verbose_name="تاریخ ارسال")

    class Meta:
        db_table = "Communication"
        verbose_name = "مکاتبه"
        verbose_name_plural = "مکاتبات"


# ==========================================
# جدول SystemSetting (تنظیمات پویای سیستم)
# ==========================================
class SystemSetting(models.Model):
    setting_id = models.AutoField(primary_key=True)
    setting_key = models.CharField(
        max_length=100, unique=True, verbose_name="کلید تنظیم"
    )
    setting_value = models.CharField(max_length=255, verbose_name="مقدار تنظیم")
    data_type = models.CharField(max_length=20, verbose_name="نوع داده")
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")
    updated_by = models.ForeignKey(
        "UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="به‌روزرسانی‌کننده",
    )

    class Meta:
        db_table = "SystemSetting"
        verbose_name = "تنظیمات سیستم"
        verbose_name_plural = "تنظیمات سیستم"

<<<<<<< HEAD
=======

class CreditTransferRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("approved", "تأیید شده"),
        ("rejected", "رد شده"),
    ]

    transfer_request_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="credit_transfer_requests",
    )
    source_university = models.CharField(max_length=255)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    def __str__(self):
        return f"درخواست تطبیق واحد {self.transfer_request_id}"


class InternshipRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("approved", "تأیید شده"),
        ("rejected", "رد شده"),
    ]

    internship_request_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="internship_requests",
    )
    organization_name = models.CharField(max_length=255)
    start_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    def __str__(self):
        return f"درخواست کارآموزی {self.internship_request_id}"


class ThesisProgressReport(models.Model):
    REVIEW_STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("approved", "تأیید شده"),
        ("needs_revision", "نیازمند اصلاح"),
    ]

    report_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="thesis_progress_reports",
    )
    teacher = models.ForeignKey(
        "core.Teacher",
        on_delete=models.PROTECT,
        related_name="thesis_progress_reports",
    )
    report_content = models.TextField()
    review_status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS_CHOICES,
        default="pending",
    )

    def __str__(self):
        return f"گزارش پیشرفت پایان‌نامه {self.report_id}"
>>>>>>> 45ddee8ee0f0a8cd1485056100f6e163b493941e

from django.db import models
from datetime import date
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.utils import timezone

# ==========================================
# قوانین آموزشی (برای استفاده در @propertyها)
# ==========================================
class StudentAcademicRules:
    """
    کلاس قوانین آموزشی.
    این مقادیر در @propertyها استفاده می‌شوند تا افزونگی داده کاهش یابد.
    """
    # حداقل معدل برای مشروط نشدن
    PROBATION_GPA = 12.0
    
    # معدل بالا (برای سقف واحد بیشتر)
    HIGH_GPA = 17.0
    
    # سقف واحد مجاز بر اساس معدل
    MAX_UNITS_UNKNOWN_GPA = 14    # معدل نامشخص (ترم اول)
    MAX_UNITS_HIGH_GPA = 24       # معدل بالا (۱۷ به بالا)
    MAX_UNITS_NORMAL = 20         # معدل عادی (۱۲ تا ۱۷)
    MAX_UNITS_PROBATION = 14      # معدل مشروط (کمتر از ۱۲)
    
    # حداکثر تعداد ترم مجاز بر اساس مقطع
    MAX_TERMS = {
        "associate": 4,       # کاردانی: ۴ ترم
        "bachelor": 8,        # کارشناسی: ۸ ترم
        "master": 4,          # ارشد: ۴ ترم
        "phd": 8,             # دکتری: ۸ ترم
    }
# ==========================================
# جدول مقادیر ثابت (Constant)
# ==========================================
class Constant(models.Model):
    constant_id = models.AutoField(primary_key=True, verbose_name="شناسه ثابت")
    category = models.CharField(max_length=50, verbose_name="دسته‌بندی")
    code = models.CharField(max_length=50, verbose_name="کد")
    label = models.CharField(max_length=100, verbose_name="برچسب (نام نمایشی)")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        db_table = "Constant"
        verbose_name = "مقدار ثابت"
        verbose_name_plural = "مقادیر ثابت"
        ordering = ["category", "code"]
        unique_together = [("category", "code")]

    def __str__(self):
        return f"{self.category} - {self.label} ({self.code})"

    
# شخص (جایگزین User پیش‌فرض جنگو)
class Person(AbstractUser):
    first_name = models.CharField(verbose_name="نام", max_length=100, blank=False)
    last_name = models.CharField(
        verbose_name="نام خانوادگی", max_length=100, blank=False
    )
    email = models.EmailField(
        verbose_name="ایمیل", max_length=254, unique=True, blank=False
    )
    national_id = models.CharField(
        verbose_name="کد ملی",
        max_length=10,
        unique=True,
        blank=False,
        validators=[RegexValidator(r"^\d{10}$", "کد ملی باید دقیقاً ۱۰ رقم باشد.")],
    )
    birth_date = models.DateField(verbose_name="تاریخ تولد", blank=False)
    """
       gender = models.CharField(
        verbose_name="جنسیت",
        max_length=6,
        blank=False,
    )
    """
    gender = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="person_genders",
        verbose_name="جنسیت",
        limit_choices_to={"category": "gender"},
        null=True,
        blank=True,
    )    
    address = models.CharField(
        verbose_name="آدرس", max_length=200, blank=True, default=""
    )
    profile_image_path = models.CharField(
        verbose_name="مسیر تصویر پروفایل",
        max_length=255,
        blank=True,
        default="",
        help_text="برای صدور کارت دانشجویی دیجیتال",
    )
    """
    preferred_language = models.CharField(
            verbose_name="زبان ترجیحی",
            max_length=2,
            default='fa'
            blank=False,
            help_text="پشتیبانی از فارسی و راست‌چین (NFUP01)",
     )
    """
    preferred_language = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="person_languages",
        verbose_name="زبان ترجیحی",
        limit_choices_to={"category": "language"},
        null=True,
        blank=True,
        help_text="پشتیبانی از فارسی و راست‌چین (NFUP01)",
    )

    is_notification_enabled = models.BooleanField(
        verbose_name="دریافت اعلان فعال",
        default=True,
        help_text="FUOP05",
    )
    birth_place = models.CharField(
        verbose_name="محل تولد",
        max_length=100,
        blank=False,
        help_text="برای مدارک رسمی (04FUFP)",
    )
    updated_at = models.DateTimeField(verbose_name="تاریخ آخرین ویرایش", auto_now=True)

    REQUIRED_FIELDS = ["email", "national_id", "birth_date"]

    class Meta:
        db_table = "Person"
        verbose_name = "شخص"
        verbose_name_plural = "اشخاص"
        ordering = ["last_name", "first_name"]
        unique_together = [("first_name", "last_name", "birth_date", "birth_place")]

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        """نام کامل شخص؛ فیلدی محاسباتی و ذخیره‌نشده در دیتابیس."""
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        """سن شخص بر اساس تاریخ تولد."""
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
        verbose_name="کد استاد",
        max_length=20,
        unique=True,
        blank=False,
        help_text="مثال: T-1001",
    )
    department = models.ForeignKey(
        "Department",
        on_delete=models.PROTECT,
        related_name="teachers",
        verbose_name="گروه آموزشی",
    )
    """
    academic_rank = models.CharField(
        verbose_name="مرتبه علمی",
        max_length=20,
        blank=False,
    )
    """

    academic_rank = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="teacher_ranks",
        verbose_name="مرتبه علمی",
        limit_choices_to={"category": "academic_rank"},
        null=True,
        blank=True,
    )
    hire_date = models.DateField(verbose_name="تاریخ استخدام", blank=False)

    class Meta:
        db_table = "Teacher"
        verbose_name = "استاد"
        verbose_name_plural = "اساتید"
        ordering = ["teacher_code"]

    def __str__(self):
        return f"{self.teacher_code} - {self.person.full_name}"

    @property
    def years_of_service(self):
        """سابقه همکاری کامل استاد با دانشگاه بر حسب سال."""
        today = date.today()
        years = today.year - self.hire_date.year
        if (today.month, today.day) < (self.hire_date.month, self.hire_date.day):
            years -= 1
        return max(years, 0)


# دانشجو
class Student(models.Model):
    person = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="student_records",
        verbose_name="شخص",
    )
    student_code = models.CharField(
        verbose_name="شماره دانشجویی",
        max_length=20,
        unique=True,
        blank=False,
    )
    """
    educational_level = models.CharField(
        verbose_name="مقطع تحصیلی",
        max_length=10,
        blank=False,
    )
    """
    educational_level = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="student_levels",
        verbose_name="مقطع تحصیلی",
        limit_choices_to={"category": "educational_level"},
        null=True,
        blank=True,
    )
    field = models.ForeignKey(
        "Field",
        on_delete=models.PROTECT,
        related_name="students",
        verbose_name="رشته تحصیلی",
    )
    application_date = models.DateField(verbose_name="تاریخ شروع تحصیل", blank=False)
    """
    status = models.CharField(
        verbose_name="وضعیت تحصیلی",
        max_length=10,
        default='active'    
        blank=False,
    )
    """
    status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="student_statuses",
        verbose_name="وضعیت تحصیلی",
        limit_choices_to={"category": "student_status"},
        null=True,
        blank=True,
    )
    """
    admission_type = models.CharField(
        verbose_name="نوع پذیرش",
        max_length=20,
        blank=False,
    )
    """
    admission_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="student_admission_types",
        verbose_name="نوع پذیرش",
        limit_choices_to={"category": "admission_type"},
        null=True,
        blank=True,
    )
    previous_term_gpa = models.DecimalField(
        verbose_name="معدل ترم قبل",
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        help_text="مبنای تعیین سقف واحد (FUFD04)؛ برای ترم اول خالی است",
    )
    total_gpa = models.DecimalField(
        verbose_name="معدل کل",
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        help_text="برای نمایش وضعیت تحصیلی و مشروطی",
    )
    passed_units = models.PositiveIntegerField(
        verbose_name="تعداد واحد گذرانده‌شده",
        default=0,
        validators=[MinValueValidator(0)],
        help_text="اطلاعات آموزشی موردنیاز برای حذف اضطراری (FUFP04)",
    )
    tuition_debt = models.DecimalField(
        verbose_name="مبلغ بدهی شهریه",
        max_digits=12,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="مسدودسازی انتخاب واحد در صورت بدهی (FUFD05)",
    )
    completed_terms = models.PositiveSmallIntegerField(
        verbose_name="تعداد ترم‌های گذرانده‌شده",
        default=0,
        validators=[MinValueValidator(0)],
        help_text="برای محاسبه سنوات باقی‌مانده (25FUOP)",
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
        """مشروط بودن دانشجو بر اساس معدل کل کمتر از ۱۲."""
        if self.total_gpa is None:
            return False
        return self.total_gpa < StudentAcademicRules.PROBATION_GPA

    @property
    def can_register_courses(self):
        """در صورت نداشتن بدهی شهریه، از نظر مالی مجاز به انتخاب واحد است."""
        return self.tuition_debt == 0

    @property
    def max_allowed_units(self):
        """سقف واحد مجاز بر اساس معدل ترم قبل؛ اعداد طبق ضوابط نمونه پروژه‌اند."""
        rules = StudentAcademicRules
        gpa = self.previous_term_gpa
        if gpa is None:
            return rules.MAX_UNITS_UNKNOWN_GPA
        if gpa >= rules.HIGH_GPA:
            return rules.MAX_UNITS_HIGH_GPA
        if gpa >= rules.PROBATION_GPA:
            return rules.MAX_UNITS_NORMAL
        return rules.MAX_UNITS_PROBATION

    @property
    def remaining_terms(self):
        """تعداد ترم باقی‌مانده تا سقف سنوات مجاز مقطع."""
        max_terms = StudentAcademicRules.MAX_TERMS.get(self.educational_level)
        if max_terms is None:
            return 0
        return max(max_terms - self.completed_terms, 0)


# درس
class Lesson(models.Model):

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
    """
    lesson_type = models.CharField(
        max_length=20,
        verbose_name='نوع درس'
    )
    """

    lesson_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="lesson_types",
        verbose_name="نوع درس",
        limit_choices_to={"category": "lesson_type"},
        null=True,
        blank=True,
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
class Term(models.Model):

    term_code = models.CharField(
        verbose_name="کد ترم",
        max_length=20,
        unique=True,
        null=False,
        blank=False,
        help_text="کد یکتای ترم، مثال: 14051",
    )
    """
    semester = models.CharField(
        verbose_name="نیمسال",
        max_length=10,
        null=False,
        blank=False,
    )
    """
    semester = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="term_semesters",
        verbose_name="نیمسال",
        limit_choices_to={"category": "semester"},
        null=True,
        blank=True,
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
    offering = models.ForeignKey("CourseOffering", on_delete=models.CASCADE)
    exam_date = models.DateField()
    """
    exam_type = models.CharField(
        max_length=20
    )
    """
    exam_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="exam_types",
        verbose_name="نوع آزمون",
        limit_choices_to={"category": "exam_type"},
        null=True,
        blank=True,
    )

# گروه کلاسی
class LessonGroups(models.Model):
    id = models.BigIntegerField(primary_key = True, verbose_name = "آیدی")

    name = models.CharField(max_length = 50, blank = False, null = False, verbose_name = "نام گروه")

    created_at = models.DateTimeField(auto_now_add = True, verbose_name = "تاریخ ساخت")
    """
    created_by = models.ForeignKey(
        Person, 
        on_delete = models.CASCADE, 
        related_name = "lesson_groups", 
        verbose_name = "سازنده گروه"
    )

    members = models.ManyToManyField(
        Person, 
        related_name = "lesson_groups", 
        verbose_name = "اعضا"
    )
    """
    created_by = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="created_lesson_groups", verbose_name="سازنده گروه")
    members = models.ManyToManyField(Person, related_name="member_lesson_groups", verbose_name="اعضا")
    teacher = models.ForeignKey(
        Teacher, 
        on_delete = models.DO_NOTHING, 
        related_name = "lesson_groups", 
        verbose_name = "استاد"
    )

    is_active = models.BooleanField(default = True, verbose_name = "وضعیت")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "گروه کلاسی",
        verbose_name_plural = "گروه های کلاسی"


# مجوزهای پارکینگ
class ParkingPasses(models.Model):
    id = models.BigAutoField(primary_key = True, verbose_name = "آیدی")

    parking_pass_code = models.CharField(max_length = 50, unique = True, null = False, verbose_name = "کد مجوز پارکینگ")

    aquisition_date = models.DateField(auto_now_add=True, verbose_name = "تاریخ اخذ")

    expiration_date = models.DateField(null = False, blank = False, verbose_name = "تاریخ انقضا")

    charge = models.BigIntegerField(null = False, default = 0, blank = False, verbose_name = "شارژ")

    owner = models.OneToOneField(
        Person, 
        on_delete = models.CASCADE, 
        related_name = "parking_pass",
        verbose_name = "مالک"
    )

    @property
    def remaining_days(self):
        return (self.aquisition_date - self.expiration_date).days

    def __str__(self):
        return self.parking_pass_code

    class Meta:
        verbose_name = "مجوز پارکینگ",
        verbose_name_plural = "مجوزهای پارکینگ"

# نقش
class Role(models.Model):

    # نام نقش
    role_name = models.CharField(
        max_length=100,
        verbose_name="عنوان نقش"
    )

    # توضیحات نقش
    description = models.CharField(
        max_length=100,
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


# پیش‌نیاز/هم‌نیاز
class Prerequisite(models.Model):

    # شناسه یکتای پیش‌نیاز
    prereq_id = models.AutoField(
        primary_key=True,
        verbose_name="شناسه پیش‌نیاز"
    )

    # درس اصلی
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='prerequisites',
        verbose_name="درس اصلی"
    )

    # درس پیش‌نیاز یا هم‌نیاز
    prerequisite_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='is_prerequisite_for',
        verbose_name="درس پیش‌نیاز یا هم‌نیاز"
    )

    # نوع رابطه
    """
    prerequisite_type = models.CharField(
        max_length=50,
        verbose_name="نوع رابطه"
    )
    """
    prerequisite_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="prerequisite_types",
        verbose_name="نوع رابطه",
        limit_choices_to={"category": "prerequisite_type"},
        null=True,
        blank=True,
    )
    # تاریخ ثبت
    created_at = models.DateTimeField(
        auto_now_add=True,
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
    


# کلاس/مکان
class Classroom(models.Model):
    building_name = models.TextField()
    room_number = models.TextField()
    capacity = models.IntegerField()
    classroom_type = models.TextField()


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
    """
    day_of_week = models.CharField(
        max_length=20,
        verbose_name='روز هفته'
    )
    """
    day_of_week = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="offering_days",
        verbose_name="روز هفته",
        limit_choices_to={"category": "day_of_week"},
        null=True,
        blank=True,
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
    """
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
    """
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
    # ✅ ارتباط با ارائه درس (کلید خارجی - این فیلد قبلاً کم بود)
    offering = models.ForeignKey(
        'CourseOffering',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="ارائه درس"
    )
    # تاریخ ثبت‌نام
    enrollment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت‌نام"
    )

    # وضعیت ثبت‌نام
    status = models.CharField(
        max_length=20,
        default='REGISTERED',
        verbose_name="وضعیت ثبت‌نام"
    )

    # نوع ثبت‌نام
    enrollment_type = models.CharField(
        max_length=20,
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
        #unique_together = ("student", "lesson", "semester")
        unique_together = ("student", "enrollment_date")


# اعتراض به نمره
class GradeAppeal(models.Model):
    enrollment = models.ForeignKey("Enrollment", on_delete=models.CASCADE)
    appeal_reason = models.TextField()
    appeal_date = models.DateTimeField()
    """
    appeal_status = models.CharField(
        max_length=30
    )
    """
    appeal_status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="appeal_statuses",
        verbose_name="وضعیت اعتراض",
        limit_choices_to={"category": "appeal_status"},
        null=True,
        blank=True,
    )

# حضور و غیاب
class Attendance(models.Model):  # مدل ثبت اطلاعات حضور و غیاب

    enrollment = models.ForeignKey(  # ارتباط این رکورد با ثبت‌نام هنرجو
        "Enrollment",  # نام مدل ثبت‌نام
        on_delete=models.CASCADE,  # با حذف ثبت‌نام، رکورد حضور و غیاب هم حذف می‌شود
    )

    session_number = models.IntegerField()  # شمارهٔ جلسه

    session_date = models.DateField()  # تاریخ برگزاری جلسه
    """    
    attendance_status = models.CharField(max_length=50)  # وضعیت حضور، مثل حاضر یا غایب
    """
    attendance_status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="attendance_statuses",
        verbose_name="وضعیت حضور",
        limit_choices_to={"category": "attendance_status"},
        null=True,
        blank=True,
    )

    attendance_time = models.TimeField()  # ساعت حضور یا ثبت وضعیت

    description = models.TextField()  # توضیحات تکمیلی

    recorded_by = models.ForeignKey(  # ارتباط با حساب کاربری ثبت‌کننده
        "UserAccount",  # نام مدل حساب کاربری
        on_delete=models.CASCADE,  # با حذف حساب کاربری، این رکورد هم حذف می‌شود
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )  # زمان ایجاد رکورد که خودکار ثبت می‌شود

class TicketCategory(models.Model):
    category_id = models.AutoField(primary_key=True, verbose_name="شناسه دسته")
    name = models.CharField(max_length=100, unique=True, verbose_name="نام دسته")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_categories', verbose_name="دسته والد")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        db_table = 'TicketCategory'
        verbose_name = "دسته‌بندی تیکت"
        verbose_name_plural = "دسته‌بندی تیکت‌ها"

    def __str__(self):
        return self.name
# تیکت
class Ticket(models.Model):
    creator = models.ForeignKey(
        "Person",
        on_delete=models.CASCADE,
        related_name="created_tickets",
        verbose_name="سازنده",
    )
    """
    creator_role = models.CharField(
        max_length=20,
        verbose_name="نقش سازنده",
    )
    """
    creator_role = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="ticket_creator_roles",
        verbose_name="نقش سازنده",
        limit_choices_to={"category": "ticket_creator_role"},
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        "TicketCategory",
        on_delete=models.CASCADE,
        related_name="tickets",
        verbose_name="دسته‌بندی",
    )
    subject = models.CharField(max_length=200, verbose_name="موضوع")
    content = models.CharField(max_length=1000, verbose_name="متن تیکت")
    """
    status = models.CharField(
        max_length=20,
        default='open'
        verbose_name="وضعیت",
    )
    """
    parent = models.ForeignKey(
    "self",
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name="replies",
    verbose_name="تیکت اصلی",
)
    status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="ticket_statuses",
        verbose_name="وضعیت",
        limit_choices_to={"category": "ticket_status"},
        null=True,
        blank=True,
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

    def __str__(self):
        return self.subject
    """
    @property
    def is_closed(self):
        return self.status == TicketStatusChoices.CLOSED
    """

    @property
    def is_closed(self):
            return self.status.code == 'closed' if self.status else False
    @property
    def is_assigned(self):
        return self.assigned_to_id is not None


# برگزاری کلاس مجازی
class OnlineClass(models.Model):
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


# رسید شهریه
class TuitionReceipt(models.Model):

    tuition_receipt_key = models.AutoField(
        primary_key=True,
        verbose_name="شناسه رسید شهریه"
    )

    receipt_serial_code = models.CharField(
        max_length=50,
        unique=True,
        null=False,
        blank=False,
        verbose_name="شماره سریال رسید"
    )

    receipt_payment_link = models.ForeignKey(
        "core.Payment",
        on_delete=models.PROTECT,
        related_name="tuition_receipts",
        null=False,
        blank=False,
        verbose_name="پرداخت مربوط به رسید"
    )

    receipt_issued_on = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=True,
        verbose_name="تاریخ صدور رسید"
    )

    receipt_document_uri = models.CharField(
        max_length=500,
        null=False,
        blank=True,
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
        verbose_name="شناسه درخواست استرداد"
    )

    refund_payment_link = models.ForeignKey(
        "core.Payment",
        on_delete=models.PROTECT,
        related_name="refund_requests",
        null=False,
        blank=False,
        verbose_name="پرداخت مربوط به درخواست"
    )

    refund_value_requested = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=False,
        blank=False,
        verbose_name="مبلغ درخواستی بازپرداخت"
    )

    refund_justification_text = models.TextField(
        null=False,
        blank=False,
        verbose_name="دلیل درخواست استرداد"
    )
    """
    refund_review_state = models.CharField(
        max_length=20,
        default=RequestReviewStatusChoices.PENDING,
        null=False,
        blank=False,
        verbose_name="وضعیت بررسی درخواست"
    )
    """

    refund_review_state = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="refund_review_states",
        verbose_name="وضعیت بررسی درخواست",
        limit_choices_to={"category": "review_status"},
        null=True,
        blank=True,
    )
    class Meta:
        db_table = "RefundRequest"
        verbose_name = "درخواست استرداد وجه"
        verbose_name_plural = "درخواست‌های استرداد وجه"
        ordering = ["-refund_case_key"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(refund_value_requested__gt=0),
                name="refund_value_must_be_positive"
            )
        ]

    def __str__(self):
        return f"درخواست استرداد شماره {self.refund_case_key}"


# درخواست خدمات دانشجویی
class StudentServiceRequest(models.Model):
    
    student_service_case_key = models.AutoField(
        primary_key=True,
        verbose_name="شناسه درخواست خدمات دانشجویی"
    )

    service_requester = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="service_requests",
        null=False,
        blank=False,
        verbose_name="دانشجوی درخواست‌دهنده"
    )
    """
    service_request_kind = models.CharField(
        max_length=30,
        null=False,
        blank=False,
        verbose_name="نوع درخواست خدمات"
    )
    """
    service_request_kind = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="service_request_kinds",
        verbose_name="نوع درخواست خدمات",
        limit_choices_to={"category": "service_request_type"},
        null=True,
        blank=True,
    )
    service_request_data = models.TextField(
        null=False,
        blank=True,
        verbose_name="اطلاعات تکمیلی درخواست"
    )
    """
    service_decision_state = models.CharField(
        max_length=20,
        default='pending',
        null=False,
        blank=False,
        verbose_name="وضعیت تصمیم‌گیری درخواست"
    )
    """
    service_decision_state = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="service_decision_states",
        verbose_name="وضعیت تصمیم‌گیری درخواست",
        limit_choices_to={"category": "review_status"},
        null=True,
        blank=True,
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

    scholarship_application_key = models.AutoField(
        primary_key=True
    )

    scholarship_applicant = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="scholarship_applications",
    )

    scholarship_type = models.CharField(max_length=50)

    scholarship_reason = models.TextField()
    """
    scholarship_status = models.CharField(
        max_length=20,
        default='pending',
    )
    """
    scholarship_status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="scholarship_statuses",
        verbose_name="وضعیت درخواست",
        limit_choices_to={"category": "review_status"},
        null=True,
        blank=True,
    )
    scholarship_submitted_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "ScholarshipApplication"

    def __str__(self):
        return f"درخواست بورسیه {self.scholarship_application_key}"


# جلسات مشاوره
class CounselingAppointment(models.Model):

    counseling_appointment_key = models.AutoField(
        primary_key=True
    )

    counseling_student_link = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="counseling_appointments",
    )

    counseling_teacher_link = models.ForeignKey(
        "core.Teacher",
        on_delete=models.PROTECT,
        related_name="counseling_appointments",
    )

    counseling_date = models.DateTimeField()

    counseling_topic = models.CharField(max_length=255)

    counseling_description = models.TextField(
        blank=True
    )
    """
    counseling_status = models.CharField(
        max_length=20,
        default='pending',
    )
    """
    counseling_status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="counseling_statuses",
        verbose_name="وضعیت جلسه",
        limit_choices_to={"category": "counseling_status"},
        null=True,
        blank=True,
    )
    class Meta:
        db_table = "CounselingAppointment"

    def __str__(self):
        return f"جلسه مشاوره {self.counseling_appointment_key}"
    


# پروپوزال
class Proposal(models.Model):

    proposal_case_key = models.AutoField(primary_key=True)

    proposal_student_link = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="proposals",
    )

    proposal_title = models.CharField(max_length=255)

    proposal_description = models.TextField()

    proposal_submitted_at = models.DateTimeField(
        auto_now_add=True
    )
    """
    proposal_status = models.CharField(
        max_length=20,
        default='pending',
    )
    """
    proposal_status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="proposal_statuses",
        verbose_name="وضعیت پروپوزال",
        limit_choices_to={"category": "proposal_status"},
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "Proposal"

    def __str__(self):
        return self.proposal_title

class TransferRequest(models.Model):

    REVIEW_STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("approved", "تأیید شده"),
        ("rejected", "رد شده"),
    ]

    transfer_id = models.AutoField(
        primary_key=True,
        verbose_name="شناسه درخواست"
    )

    student = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="transfer_requests",
        verbose_name="دانشجو"
    )

    destination_university = models.CharField(
        max_length=255,
        verbose_name="نام دانشگاه مقصد"
    )
    """
    review_status = models.CharField(
        max_length=20,
        default="pending",
        verbose_name="وضعیت بررسی"
    )
    """
    review_status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="transfer_request_statuses",
        verbose_name="وضعیت بررسی",
        limit_choices_to={"category": "review_status"},
        null=True,
        blank=True,
    )

    course_compatibility_result = models.TextField(
        blank=True,
        default="",
        verbose_name="نتیجه بررسی دروس"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
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

class GraduationAudit(models.Model):

    GRADUATION_STATUS_CHOICES = [
        ("eligible", "واجد شرایط"),
        ("not_eligible", "فاقد شرایط"),
        ("under_review", "در حال بررسی"),
    ]

    audit_id = models.AutoField(
        primary_key=True,
        verbose_name="شناسه بررسی"
    )

    student = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="graduation_audits",
        verbose_name="دانشجو"
    )

    curriculum = models.ForeignKey(
        "core.Curriculum",
        on_delete=models.PROTECT,
        related_name="graduation_audits",
        verbose_name="چارت درسی"
    )

    remaining_units = models.PositiveIntegerField(
        default=0,
        verbose_name="تعداد واحد باقی‌مانده"
    )
    """
    graduation_status = models.CharField(
        max_length=20,
        default="under_review",
        verbose_name="وضعیت فارغ‌التحصیلی"
    )
    """
    graduation_status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="graduation_statuses",
        verbose_name="وضعیت فارغ‌التحصیلی",
        limit_choices_to={"category": "graduation_status"},
        null=True,
        blank=True,
    )

    audit_date = models.DateTimeField(
        auto_now_add=True,
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

        unique_together = [
            ("student", "curriculum")
        ]

    def __str__(self):
        return (
            f"بررسی فارغ‌التحصیلی {self.audit_id} - "
            f"{self.student} - "
            f"{self.get_graduation_status_display()}"
        )


class EducationalChangeLog(models.Model):

    CHANGE_TYPE_CHOICES = [
        ("grade_change", "تغییر نمره"),
        ("course_deletion", "حذف درس"),
        ("academic_status_change", "تغییر وضعیت تحصیلی"),
    ]

    log_id = models.AutoField(
        primary_key=True,
        verbose_name="شناسه تاریخچه"
    )

    student = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="educational_change_logs",
        verbose_name="دانشجو"
    )
    """
    change_type = models.CharField(
        max_length=30,
        verbose_name="نوع تغییر"
    )
    """
    change_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="change_types",
        verbose_name="نوع تغییر",
        limit_choices_to={"category": "change_type"},
        null=True,
        blank=True,
    )
    changed_by = models.ForeignKey(
        "core.UserAccount",
        on_delete=models.PROTECT,
        related_name="educational_change_logs",
        verbose_name="کاربر ثبت‌کننده"
    )

    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ و ساعت تغییر"
    )

    description = models.TextField(
        blank=True,
        default="",
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
    curriculum_id = models.AutoField(primary_key=True, verbose_name="شناسه چارت")
    field = models.ForeignKey("Field",on_delete=models.CASCADE,related_name="curriculums",verbose_name="رشته تحصیلی")
    lesson = models.ForeignKey("Lesson",on_delete=models.CASCADE,related_name="curriculums",verbose_name="درس")
    requirement_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="curriculum_requirements",
        verbose_name="نوع درس در چارت",
        limit_choices_to={"category": "requirement_type"},
        null=True,
        blank=True,
    )
    recommended_term = models.IntegerField(verbose_name="ترم پیشنهادی")
    calculated_units = models.IntegerField(verbose_name="تعداد واحد قابل محاسبه")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        db_table = "Curriculum"
        verbose_name = "چارت درسی"
        verbose_name_plural = "چارت‌های درسی"
        ordering = ["field", "recommended_term"]
        unique_together = [("field", "lesson")]

    def __str__(self):
        return f"{self.field.field_name} - ترم {self.recommended_term} - {self.lesson.title}"


# ==========================================
# جدول Communication (ارتباطات و مکاتبات)
# ==========================================
class Communication(models.Model):
    communication_id = models.AutoField(primary_key=True, verbose_name="شناسه مکاتبه")
    sender = models.ForeignKey("UserAccount",on_delete=models.CASCADE,related_name="sent_messages",verbose_name="فرستنده" )
    receiver = models.ForeignKey("UserAccount",on_delete=models.CASCADE,related_name="received_messages",verbose_name="گیرنده")
    subject = models.CharField(max_length=255, verbose_name="موضوع")
    message_body = models.TextField(verbose_name="متن پیام")
    communication_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="communication_types",
        verbose_name="نوع مکاتبه",
        limit_choices_to={"category": "communication_type"},
        null=True,
        blank=True,
    )
    status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="communication_statuses",
        verbose_name="وضعیت",
        limit_choices_to={"category": "communication_status"},
        null=True,
        blank=True,
    )
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ خوانده شدن")

    class Meta:
        db_table = "Communication"
        verbose_name = "مکاتبه"
        verbose_name_plural = "مکاتبات"
        ordering = ["-sent_at"]
       

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.subject}"

# ==========================================
# جدول SystemSetting (تنظیمات پویای سیستم)
# ==========================================
class SystemSetting(models.Model):
    setting_id = models.AutoField(primary_key=True, verbose_name="شناسه تنظیم")
    setting_key = models.CharField(max_length=100,unique=True,verbose_name="کلید تنظیم")
    setting_value = models.CharField(max_length=255, verbose_name="مقدار تنظیم")
    data_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="system_data_types",
        verbose_name="نوع داده",
        limit_choices_to={"category": "data_type"},
        null=True,
        blank=True,
    )
    description = models.TextField(null=True, blank=True, verbose_name="توضیحات")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین به‌روزرسانی")
    updated_by = models.ForeignKey("UserAccount",on_delete=models.SET_NULL,null=True,blank=True,verbose_name="به‌روزرسانی‌کننده")

    class Meta:
        db_table = "SystemSetting"
        verbose_name = "تنظیمات سیستم"
        verbose_name_plural = "تنظیمات سیستم"
        ordering = ["setting_key"]

    def __str__(self):
        return f"{self.setting_key} = {self.setting_value}"
    
class CreditTransferRequest(models.Model):
    transfer_request_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="credit_transfer_requests",
    )
    source_university = models.CharField(max_length=255)
    request_date = models.DateTimeField(auto_now_add=True)
    """
       status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    """
    status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="credit_transfer_statuses",
        verbose_name="وضعیت",
        limit_choices_to={"category": "review_status"},
        null=True,
        blank=True,
    )
    def __str__(self):
        return f"درخواست تطبیق واحد {self.transfer_request_id}"


class InternshipRequest(models.Model):
    internship_request_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="internship_requests",
    )
    organization_name = models.CharField(max_length=255)
    start_date = models.DateField()
    status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="internship_request_statuses",
        verbose_name="وضعیت",
        limit_choices_to={"category": "review_status"},
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"درخواست کارآموزی {self.internship_request_id}"


class ThesisProgressReport(models.Model):
    """
    REVIEW_STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("approved", "تأیید شده"),
        ("needs_revision", "نیازمند اصلاح"),
    ]
    """
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
    """
    review_status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS_CHOICES,
        default="pending",
    )
    """
    review_status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="thesis_review_statuses",
        verbose_name="وضعیت",
        limit_choices_to={"category": "thesis_review_status"},
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"گزارش پیشرفت پایان‌نامه {self.report_id}"

#نوتیفیکیشن 
class Notification(models.Model):
    """
    NOTIFICATION_TYPE_CHOICES = [
        ("GRADE", "نمره"),
        ("ANNOUNCEMENT", "اطلاعیه"),
        ("CLASS_CHANGE", "تغییر کلاس"),
        ("SYSTEM", "سیستمی"),
    ]
    """
    # notification_id=models.AutoField(primary_key=True,vebose_name="شناسه اعلان")
    user = models.ForeignKey(
        "UserAccount",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="کاربر دریافت‌کننده",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="عنوان اعلان",
    )
    message = models.TextField(
        verbose_name="متن اعلان",
    )
    related_exam = models.ForeignKey(
        "Exam",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name="امتحان مرتبط",
    )
    """
    notification_type = models.CharField(
        max_length=30,
        choices=NOTIFICATION_TYPE_CHOICES,
        verbose_name="نوع اعلان",
    )
    """
    notification_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="notification_types",
        verbose_name="نوع اعلان",
        limit_choices_to={"category": "notification_type"},
        null=True,
        blank=True,
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان ارسال",
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name="خوانده شده",
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان خوانده شدن",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان ایجاد رکورد",
    )

    class Meta:
        verbose_name = "اعلان"
        verbose_name_plural = "اعلان‌ها"

    def __str__(self):
        return f"{self.get_notification_type_display()}: {self.title}"

#نظرسنجی اساتید
class TeacherSurvey(models.Model):
    RATING_CHOICES = [
        (1, "۱"),
        (2, "۲"),
        (3, "۳"),
        (4, "۴"),
        (5, "۵"),
    ]    
    enrollment = models.ForeignKey(
        "Enrollment",
        on_delete=models.CASCADE,
        related_name="teacher_surveys",
        verbose_name="ثبت‌نام",
    )
    overall_rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        verbose_name="امتیاز کلی",
    )
    teaching_quality = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        verbose_name="کیفیت تدریس",
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان ثبت نظرسنجی",
    )
    behavior = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        verbose_name="رفتار استاد",
    )
    comment = models.TextField(
        blank=True,
        verbose_name="نظر دانشجو",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان ایجاد رکورد",
    )

    class Meta:
        verbose_name = "نظرسنجی استاد و درس"
        verbose_name_plural = "نظرسنجی‌های استاد و درس"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(overall_rating__gte=1, overall_rating__lte=5),
                name="ts_rating_1_5",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(teaching_quality__isnull=True)
                    | models.Q(teaching_quality__gte=1, teaching_quality__lte=5)
                ),
                name="ts_quality_1_5",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(behavior__isnull=True)
                    | models.Q(behavior__gte=1, behavior__lte=5)
                ),
                name="ts_behavior_1_5",
            ),
        ]

    def __str__(self):
        return f"نظرسنجی با امتیاز {self.overall_rating} از ۵"

#کاراموزی
class Internship(models.Model):
    student = models.ForeignKey(
        "Student",
        on_delete=models.CASCADE,
        related_name="internship_records",
        verbose_name="دانشجو",
    )
    """
    request_type = models.CharField(
        max_length=30,
        choices=REQUEST_TYPE_CHOICES,
        verbose_name="نوع درخواست",
    )
    """
    request_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="internship_request_types",
        verbose_name="نوع درخواست",
        limit_choices_to={"category": "internship_request_type"},
        null=True,
        blank=True,
    )
    company_name = models.CharField(
        max_length=255,
        verbose_name="نام شرکت یا سازمان",
    )
    intern_start_date = models.DateField(
        verbose_name="تاریخ شروع کارآموزی",
    )
    duration_hours = models.PositiveIntegerField(
        verbose_name="مدت کارآموزی به ساعت",
    )
    """
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        verbose_name="وضعیت درخواست",
    )
    """

    status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="internship_statuses",
        verbose_name="وضعیت درخواست",
        limit_choices_to={"category": "review_status"},
        null=True,
        blank=True,
    )
    reviewed_by = models.ForeignKey(
        "UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_internship_requests",
        verbose_name="بررسی‌کننده",
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="زمان بررسی",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان ایجاد درخواست",
    )

    class Meta:
        verbose_name = "درخواست کارآموزی"
        verbose_name_plural = "درخواست‌های کارآموزی"
       

    def __str__(self):
        return f"{self.get_request_type_display()} - {self.company_name}"


class Faculty(models.Model):
    faculty_name = models.CharField(max_length=150, verbose_name="نام دانشکده")
    faculty_code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="کد دانشکده",
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "دانشکده"
        verbose_name_plural = "دانشکده‌ها"
        ordering = ["faculty_name"]

    def __str__(self):
        return self.faculty_name


class Department(models.Model):
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.PROTECT,
        related_name="departments",
        verbose_name="دانشکده",
    )
    department_name = models.CharField(max_length=150, verbose_name="نام گروه آموزشی")
    department_code = models.CharField(max_length=20, verbose_name="کد گروه آموزشی")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "گروه آموزشی"
        verbose_name_plural = "گروه‌های آموزشی"
        ordering = ["department_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["faculty", "department_code"],
                name="unique_department_code_per_faculty",
            ),
        ]

    def __str__(self):
        return f"{self.department_name} ({self.faculty.faculty_name})"


class Field(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="fields",
        verbose_name="گروه آموزشی",
    )
    field_name = models.CharField(max_length=150, verbose_name="نام رشته")
    field_code = models.CharField(max_length=20, verbose_name="کد رشته")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "رشته تحصیلی"
        verbose_name_plural = "رشته‌های تحصیلی"
        ordering = ["field_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["department", "field_code"],
                name="unique_field_code_per_department",
            ),
        ]

    def __str__(self):
        return f"{self.field_name} ({self.department.department_name})"

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
    PROBATION_GPA = 12.0
    HIGH_GPA = 17.0
    MAX_UNITS_UNKNOWN_GPA = 14
    MAX_UNITS_HIGH_GPA = 24
    MAX_UNITS_NORMAL = 20
    MAX_UNITS_PROBATION = 14
    MAX_TERMS = {
        "associate": 4,
        "bachelor": 8,
        "master": 4,
        "phd": 8,
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
        #return f"{self.category} - {self.label} ({self.code})"
        return self.label


# ==========================================
# شخص (جایگزین User پیش‌فرض جنگو)
# ==========================================
class Person(AbstractUser):
    first_name = models.CharField(verbose_name="نام", max_length=100, blank=False)
    last_name = models.CharField(verbose_name="نام خانوادگی", max_length=100, blank=False)
    email = models.EmailField(verbose_name="ایمیل", max_length=254, unique=True, blank=False)
    national_id = models.CharField(
        verbose_name="کد ملی",
        max_length=10,
        unique=True,
        blank=False,
        validators=[RegexValidator(r"^\d{10}$", "کد ملی باید دقیقاً ۱۰ رقم باشد.")],
    )
    birth_date = models.DateField(verbose_name="تاریخ تولد", blank=False)
    gender = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="person_genders",
        verbose_name="جنسیت",
        limit_choices_to={"category": "gender"},
        null=True,
        blank=True,
    )
    address = models.CharField(verbose_name="آدرس", max_length=200, blank=True, default="")
    profile_image_path = models.CharField(
        verbose_name="مسیر تصویر پروفایل",
        max_length=255,
        blank=True,
        default="",
        help_text="برای صدور کارت دانشجویی دیجیتال",
    )
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
    failed_login_count = models.PositiveIntegerField(default=0, verbose_name="تعداد تلاش ناموفق ورود")
    locked_until = models.DateTimeField(null=True, blank=True, verbose_name="قفل ورود تا")
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
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        today = date.today()
        had_birthday = (today.month, today.day) >= (self.birth_date.month, self.birth_date.day)
        return today.year - self.birth_date.year - (0 if had_birthday else 1)


# ==========================================
# استاد
# ==========================================
class Teacher(models.Model):
    person = models.OneToOneField(Person, on_delete=models.CASCADE, related_name="teacher", verbose_name="شخص")
    teacher_code = models.CharField(verbose_name="کد استاد", max_length=20, unique=True, blank=False, help_text="مثال: T-1001")
    department = models.ForeignKey("Department", on_delete=models.PROTECT, related_name="teachers", verbose_name="گروه آموزشی")
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
        today = date.today()
        years = today.year - self.hire_date.year
        if (today.month, today.day) < (self.hire_date.month, self.hire_date.day):
            years -= 1
        return max(years, 0)


# ==========================================
# دانشجو
# ==========================================
class Student(models.Model):
    person = models.ForeignKey(Person, on_delete=models.PROTECT, related_name="student_records", verbose_name="شخص")
    student_code = models.CharField(verbose_name="شماره دانشجویی", max_length=20, unique=True, blank=False)
    educational_level = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="student_levels",
        verbose_name="مقطع تحصیلی",
        limit_choices_to={"category": "educational_level"},
        null=True,
        blank=True,
    )
    field = models.ForeignKey("Field", on_delete=models.PROTECT, related_name="students", verbose_name="رشته تحصیلی")
    application_date = models.DateField(verbose_name="تاریخ شروع تحصیل", blank=False)
    status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="student_statuses",
        verbose_name="وضعیت تحصیلی",
        limit_choices_to={"category": "student_status"},
        null=True,
        blank=True,
    )
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
        if self.total_gpa is None:
            return False
        return self.total_gpa < StudentAcademicRules.PROBATION_GPA

    @property
    def can_register_courses(self):
        return self.tuition_debt == 0

    @property
    def max_allowed_units(self):
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
        level_code = self.educational_level.code if self.educational_level else None
        max_terms = StudentAcademicRules.MAX_TERMS.get(level_code)
        if max_terms is None:
            return 0
        return max(max_terms - self.completed_terms, 0)


# ==========================================
# درس
# ==========================================
class Lesson(models.Model):
    lesson_code = models.CharField(max_length=20, unique=True, verbose_name='کد درس')
    title = models.CharField(max_length=200, verbose_name='عنوان درس')
    practical_units = models.PositiveSmallIntegerField(default=0, verbose_name='واحد عملی')
    theory_units = models.PositiveSmallIntegerField(default=0, verbose_name='واحد نظری')
    lesson_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="lesson_types",
        verbose_name="نوع درس",
        limit_choices_to={"category": "lesson_type"},
        null=True,
        blank=True,
    )
    department = models.ForeignKey('Department', on_delete=models.PROTECT, related_name='lessons', verbose_name='گروه آموزشی')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')

    def __str__(self):
        return f'{self.lesson_code} - {self.title}'

    class Meta:
        verbose_name = 'درس'
        verbose_name_plural = 'دروس'
        ordering = ['title']
        constraints = [
            models.CheckConstraint(
                condition=(models.Q(practical_units__gt=0) | models.Q(theory_units__gt=0)),
                name='lesson_has_units'
            ),
        ]


# ==========================================
# ترم
# ==========================================
class Term(models.Model):
    term_code = models.CharField(verbose_name="کد ترم", max_length=20, unique=True, null=False, blank=False, help_text="کد یکتای ترم، مثال: 14051")
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
        validators=[RegexValidator(r"^\d{4}-\d{4}$", "فرمت سال تحصیلی باید مثل 1405-1406 باشد.")],
        help_text="مثال: 1405-1406",
    )
    start_date = models.DateField(verbose_name="تاریخ شروع ترم", null=False, blank=False)
    end_date = models.DateField(verbose_name="تاریخ پایان ترم", null=False, blank=False)
    registration_start = models.DateTimeField(verbose_name="شروع انتخاب واحد", null=False, blank=False)
    registration_end = models.DateTimeField(verbose_name="پایان انتخاب واحد", null=False, blank=False)
    add_drop_start = models.DateTimeField(verbose_name="شروع حذف و اضافه", null=False, blank=False)
    add_drop_end = models.DateTimeField(verbose_name="پایان حذف و اضافه", null=False, blank=False)
    emergency_drop_start = models.DateTimeField(verbose_name="شروع حذف اضطراری", null=False, blank=False)
    emergency_drop_end = models.DateTimeField(verbose_name="پایان حذف اضطراری", null=False, blank=False)
    is_active = models.BooleanField(verbose_name="فعال", default=False, help_text="فقط یک ترم می‌تواند هم‌زمان فعال باشد")

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
        semester_label = self.semester.label if self.semester else "بدون نیمسال"
        return f"{semester_label} {self.academic_year}"

    def clean(self):
        super().clean()
        pairs = [
            (self.start_date, self.end_date, "تاریخ پایان ترم"),
            (self.registration_start, self.registration_end, "پایان انتخاب واحد"),
            (self.add_drop_start, self.add_drop_end, "پایان حذف و اضافه"),
            (self.emergency_drop_start, self.emergency_drop_end, "پایان حذف اضطراری"),
        ]
        for start, end, label in pairs:
            if start and end and end <= start:
                raise ValidationError(f"{label} باید بعد از شروع آن باشد.")
        if (self.emergency_drop_start and self.add_drop_end and self.emergency_drop_start < self.add_drop_end):
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


# ==========================================
# پرداخت
# ==========================================
class Payment(models.Model):
    term = models.ForeignKey('Term', on_delete=models.PROTECT, related_name='payments', verbose_name='نیمسال تحصیلی')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='مبلغ پرداخت')
    payment_date = models.DateTimeField(verbose_name='تاریخ پرداخت')
    tracking_code = models.CharField(max_length=100, unique=True, verbose_name='کد پیگیری')
    student = models.ForeignKey('Student', on_delete=models.PROTECT, related_name='payments', verbose_name='دانشجو')
    status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="payment_statuses",
        verbose_name="وضعیت پرداخت",
        limit_choices_to={"category": "payment_status"},
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')

    def __str__(self):
        return f'{self.tracking_code} - {self.amount}'

    class Meta:
        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت‌ها'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(condition=models.Q(amount__gt=0), name='payment_amount_must_be_positive'),
        ]


# ==========================================
# امتحان
# ==========================================
class Exam(models.Model):
    offering = models.ForeignKey("CourseOffering", on_delete=models.CASCADE)
    exam_date = models.DateField()
    exam_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="exam_types",
        verbose_name="نوع آزمون",
        limit_choices_to={"category": "exam_type"},
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"امتحان {self.offering.lesson.title} - {self.exam_date}"

    class Meta:
        verbose_name = "امتحان"
        verbose_name_plural = "امتحان‌ها"


# ==========================================
# گروه کلاسی
# ==========================================
class LessonGroups(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="آیدی")
    name = models.CharField(max_length=50, blank=False, null=False, verbose_name="نام گروه")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ساخت")
    created_by = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="created_lesson_groups", verbose_name="سازنده گروه")
    members = models.ManyToManyField(Person, related_name="member_lesson_groups", verbose_name="اعضا")
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, related_name="lesson_groups", verbose_name="استاد")
    is_active = models.BooleanField(default=True, verbose_name="وضعیت")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "گروه کلاسی"
        verbose_name_plural = "گروه های کلاسی"


# ==========================================
# مجوزهای پارکینگ
# ==========================================
class ParkingPasses(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name="آیدی")
    parking_pass_code = models.CharField(max_length=50, unique=True, null=False, verbose_name="کد مجوز پارکینگ")
    aquisition_date = models.DateField(auto_now_add=True, verbose_name="تاریخ اخذ")
    expiration_date = models.DateField(null=False, blank=False, verbose_name="تاریخ انقضا")
    charge = models.BigIntegerField(null=False, default=0, blank=False, verbose_name="شارژ")
    owner = models.OneToOneField(Person, on_delete=models.CASCADE, related_name="parking_pass", verbose_name="مالک")

    @property
    def remaining_days(self):
        return (self.expiration_date - date.today()).days

    def __str__(self):
        return self.parking_pass_code

    class Meta:
        verbose_name = "مجوز پارکینگ"
        verbose_name_plural = "مجوزهای پارکینگ"


# ==========================================
# نقش
# ==========================================
class Role(models.Model):
    role_name = models.CharField(max_length=100, verbose_name="عنوان نقش")
    description = models.CharField(max_length=100, blank=True, null=True, verbose_name="توضیح")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    is_active = models.BooleanField(default=True, verbose_name="وضعیت فعال")

    def __str__(self):
        return self.role_name

    class Meta:
        verbose_name = "نقش"
        verbose_name_plural = "نقش‌ها"


# ==========================================
# حساب کاربری
# ==========================================
class UserAccount(models.Model):
    person = models.ForeignKey("Person", on_delete=models.CASCADE, related_name="user_accounts", verbose_name="شخص")
    role = models.ForeignKey("Role", on_delete=models.PROTECT, related_name="user_accounts", verbose_name="نقش")
    username = models.CharField(max_length=150, unique=True, verbose_name="نام کاربری")
    password = models.CharField(max_length=128, verbose_name="رمز عبور")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    failed_login_count = models.PositiveIntegerField(default=0, verbose_name="تعداد تلاش ناموفق")
    locked_until = models.DateTimeField(null=True, blank=True, verbose_name="قفل تا")
    last_login_at = models.DateTimeField(null=True, blank=True, verbose_name="آخرین ورود")
    last_activity_at = models.DateTimeField(null=True, blank=True, verbose_name="آخرین فعالیت")
    password_changed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاریخ تغییر رمز")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "حساب کاربری"
        verbose_name_plural = "حساب‌های کاربری"



# ==========================================
# پیش‌نیاز/هم‌نیاز
# ==========================================
class Prerequisite(models.Model):
    prereq_id = models.AutoField(primary_key=True, verbose_name="شناسه پیش‌نیاز")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='prerequisites', verbose_name="درس اصلی")
    prerequisite_lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='is_prerequisite_for', verbose_name="درس پیش‌نیاز یا هم‌نیاز")
    prerequisite_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="prerequisite_types",
        verbose_name="نوع رابطه",
        limit_choices_to={"category": "prerequisite_type"},
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    def __str__(self):
        return f"{self.prerequisite_lesson} - {self.lesson}"

    class Meta:
        verbose_name = "پیش‌نیاز و هم‌نیاز"
        verbose_name_plural = "پیش‌نیازها و هم‌نیازها"
        unique_together = (('lesson', 'prerequisite_lesson'),)


# ==========================================
# کلاس/مکان
# ==========================================
class Classroom(models.Model):
    building_name = models.TextField(verbose_name="نام ساختمان")
    room_number = models.TextField(verbose_name="شماره اتاق")
    capacity = models.IntegerField(verbose_name="ظرفیت")
    classroom_type = models.TextField(verbose_name="نوع کلاس")

    class Meta:
        verbose_name = "کلاس"
        verbose_name_plural = "کلاس‌ها"

    def __str__(self):
        return f"{self.building_name} - {self.room_number}"


# ==========================================
# ارائه درس در ترم
# ==========================================
class CourseOffering(models.Model):
    lesson = models.ForeignKey('Lesson', on_delete=models.PROTECT, related_name='course_offerings', verbose_name='درس')
    term = models.ForeignKey('Term', on_delete=models.PROTECT, related_name='course_offerings', verbose_name='نیمسال تحصیلی')
    teacher = models.ForeignKey('Teacher', on_delete=models.PROTECT, related_name='course_offerings', verbose_name='استاد')
    capacity = models.PositiveIntegerField(verbose_name='ظرفیت کلاس')
    day_of_week = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="offering_days",
        verbose_name="روز هفته",
        limit_choices_to={"category": "day_of_week"},
        null=True,
        blank=True,
    )
    start_time = models.TimeField(verbose_name='ساعت شروع')
    end_time = models.TimeField(verbose_name='ساعت پایان')
    classroom = models.ForeignKey('Classroom', on_delete=models.PROTECT, related_name='course_offerings', verbose_name='کلاس')
    exam_date = models.DateField(null=True, blank=True, verbose_name='تاریخ امتحان')
    exam_time = models.TimeField(null=True, blank=True, verbose_name='ساعت امتحان')
    is_active = models.BooleanField(default=True, verbose_name='وضعیت فعال بودن ارائه')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')

    @property
    def duration_minutes(self):
        start = self.start_time.hour * 60 + self.start_time.minute
        end = self.end_time.hour * 60 + self.end_time.minute
        return end - start

    @property
    def remaining_capacity(self):
        active_status = models.Q(status__isnull=True) | (
            ~models.Q(status__code__iexact="dropped")
            & ~models.Q(status__code__iexact="cancelled")
            & ~models.Q(status__code__iexact="canceled")
        )
        registered_count = self.enrollments.filter(active_status).count()
        return max(self.capacity - registered_count, 0)

    def __str__(self):
        return self.lesson.title

    class Meta:
        verbose_name = 'ارائه درس'
        verbose_name_plural = 'ارائه‌های درس'
        ordering = ['start_time']
        unique_together = [('teacher', 'day_of_week', 'start_time', 'term')]
        constraints = [
            models.CheckConstraint(condition=models.Q(capacity__gt=0), name='offering_capacity_positive'),
            models.CheckConstraint(condition=models.Q(end_time__gt=models.F('start_time')), name='offering_end_time_valid'),
            models.CheckConstraint(
                condition=(
                    models.Q(exam_date__isnull=True, exam_time__isnull=True) |
                    models.Q(exam_date__isnull=False, exam_time__isnull=False)
                ),
                name='exam_date_time_consistent'
            ),
        ]


# ==========================================
# انتخاب واحد
# ==========================================
class Enrollment(models.Model):
    EnrollmentId = models.AutoField(primary_key=True, verbose_name="شناسه ثبت‌نام")
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='enrollments', verbose_name="دانشجو")
    offering = models.ForeignKey('CourseOffering', on_delete=models.CASCADE, related_name='enrollments', verbose_name="ارائه درس")
    enrollment_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت‌نام")
    status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="enrollment_statuses",
        verbose_name="وضعیت ثبت‌نام",
        limit_choices_to={"category": "enrollment_status"},
        null=True,
        blank=True,
    )
    enrollment_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="enrollment_types",
        verbose_name="نوع ثبت‌نام",
        limit_choices_to={"category": "enrollment_type"},
        null=True,
        blank=True,
    )
    drop_date = models.DateField(null=True, blank=True, verbose_name="تاریخ حذف")

    def __str__(self):
        return f"{self.student} - {self.status.label if self.status else 'نامشخص'}"

    class Meta:
        verbose_name = "انتخاب واحد"
        verbose_name_plural = "انتخاب واحدها"
        unique_together = ("student", "offering")


# ==========================================
# نمره
# ==========================================
class Grade(models.Model):
    enrollment = models.ForeignKey("Enrollment", on_delete=models.CASCADE, related_name="grades")
    score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="نمره")

    def __str__(self):
        return f"نمره {self.enrollment.student} - {self.enrollment.offering.lesson.title}"

    class Meta:
        verbose_name = "نمره"
        verbose_name_plural = "نمرات"


# ==========================================
# اعتراض به نمره
# ==========================================
class GradeAppeal(models.Model):
    enrollment = models.ForeignKey("Enrollment", on_delete=models.CASCADE)
    appeal_reason = models.TextField()
    appeal_date = models.DateTimeField()
    appeal_status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="appeal_statuses",
        verbose_name="وضعیت اعتراض",
        limit_choices_to={"category": "appeal_status"},
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"اعتراض {self.enrollment.student} - {self.appeal_status.label if self.appeal_status else 'در انتظار'}"

    class Meta:
        verbose_name = "اعتراض به نمره"
        verbose_name_plural = "اعتراض‌های نمره"


# ==========================================
# حضور و غیاب
# ==========================================
class Attendance(models.Model):
    enrollment = models.ForeignKey("Enrollment", on_delete=models.CASCADE)
    session_number = models.IntegerField(verbose_name="شماره جلسه")
    session_date = models.DateField(verbose_name="تاریخ جلسه")
    attendance_status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="attendance_statuses",
        verbose_name="وضعیت حضور",
        limit_choices_to={"category": "attendance_status"},
        null=True,
        blank=True,
    )
    attendance_time = models.TimeField(verbose_name="ساعت حضور")
    description = models.TextField(verbose_name="توضیحات")
    recorded_by = models.ForeignKey("UserAccount", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"حضور {self.enrollment.student} - جلسه {self.session_number}"

    class Meta:
        verbose_name = "حضور و غیاب"
        verbose_name_plural = "حضور و غیاب‌ها"

# ==========================================
# دسته‌بندی تیکت
# ==========================================
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


# ==========================================
# تیکت
# ==========================================
class Ticket(models.Model):
    creator = models.ForeignKey("Person", on_delete=models.CASCADE, related_name="created_tickets", verbose_name="سازنده")
    creator_role = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="ticket_creator_roles",
        verbose_name="نقش سازنده",
        limit_choices_to={"category": "ticket_creator_role"},
        null=True,
        blank=True,
    )
    category = models.ForeignKey("TicketCategory", on_delete=models.CASCADE, related_name="tickets", verbose_name="دسته‌بندی")
    subject = models.CharField(max_length=200, verbose_name="موضوع")
    content = models.CharField(max_length=1000, verbose_name="متن تیکت")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies", verbose_name="تیکت اصلی")
    status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="ticket_statuses",
        verbose_name="وضعیت",
        limit_choices_to={"category": "ticket_status"},
        null=True,
        blank=True,
    )
    assigned_to = models.ForeignKey("Person", on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets", verbose_name="مسئول پاسخگویی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ آخرین به‌روزرسانی")

    class Meta:
        verbose_name = "تیکت"
        verbose_name_plural = "تیکت‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return self.subject

    @property
    def is_closed(self):
        return self.status.code == 'closed' if self.status else False

    @property
    def is_assigned(self):
        return self.assigned_to_id is not None


# ==========================================
# برگزاری کلاس مجازی
# ==========================================
class OnlineClass(models.Model):
    teacher = models.ForeignKey("Teacher", on_delete=models.CASCADE, related_name="online_classes", verbose_name="استاد")
    offering = models.ForeignKey("CourseOffering", on_delete=models.CASCADE, related_name="online_classes", verbose_name="ارائه درس")
    start_at = models.DateTimeField(verbose_name="تاریخ و ساعت شروع")
    end_at = models.DateTimeField(verbose_name="تاریخ و ساعت پایان")
    title = models.CharField(max_length=200, verbose_name="عنوان جلسه")
    meeting_link = models.URLField(verbose_name="لینک جلسه")

    class Meta:
        verbose_name = "کلاس مجازی"
        verbose_name_plural = "کلاس‌های مجازی"
        ordering = ["start_at"]
        constraints = [
            models.CheckConstraint(condition=models.Q(end_at__gt=models.F("start_at")), name="online_class_end_after_start"),
        ]

    def __str__(self):
        return self.title

    @property
    def duration(self):
        if self.start_at is None or self.end_at is None:
            return None
        return self.end_at - self.start_at

    @property
    def is_ongoing(self):
        if self.start_at is None or self.end_at is None:
         return False
        return self.start_at <= timezone.now() <= self.end_at


# رسید شهریه
class TuitionReceipt(models.Model):
    tuition_receipt_key = models.AutoField(primary_key=True, verbose_name="شناسه رسید شهریه")
    receipt_serial_code = models.CharField(max_length=50, unique=True, null=False, blank=False, verbose_name="شماره سریال رسید")
    receipt_payment_link = models.ForeignKey("Payment", on_delete=models.PROTECT, related_name="tuition_receipts", null=False, blank=False, verbose_name="پرداخت مربوط به رسید")
    receipt_issued_on = models.DateTimeField(auto_now_add=True, null=False, blank=True, verbose_name="تاریخ صدور رسید")
    receipt_document_uri = models.CharField(max_length=500, null=False, blank=True, verbose_name="آدرس فایل رسید")

    class Meta:
        db_table = "TuitionReceipt"
        verbose_name = "رسید پرداخت شهریه"
        verbose_name_plural = "رسیدهای پرداخت شهریه"
        ordering = ["-receipt_issued_on"]

    def __str__(self):
        return f"رسید شماره {self.receipt_serial_code}"


# ==========================================
# درخواست بازپرداخت وجه
# ==========================================
class RefundRequest(models.Model):
    refund_case_key = models.AutoField(primary_key=True, verbose_name="شناسه درخواست استرداد")
    refund_payment_link = models.ForeignKey("Payment", on_delete=models.PROTECT, related_name="refund_requests", null=False, blank=False, verbose_name="پرداخت مربوط به درخواست")
    refund_value_requested = models.DecimalField(max_digits=15, decimal_places=2, null=False, blank=False, verbose_name="مبلغ درخواستی بازپرداخت")
    refund_justification_text = models.TextField(null=False, blank=False, verbose_name="دلیل درخواست استرداد")
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
            models.CheckConstraint(condition=models.Q(refund_value_requested__gt=0), name="refund_value_must_be_positive")
        ]

    def __str__(self):
        return f"درخواست استرداد شماره {self.refund_case_key}"


# ==========================================
# درخواست خدمات دانشجویی
# ==========================================
class StudentServiceRequest(models.Model):
    student_service_case_key = models.AutoField(primary_key=True, verbose_name="شناسه درخواست خدمات دانشجویی")
    service_requester = models.ForeignKey("Student", on_delete=models.PROTECT, related_name="service_requests", null=False, blank=False, verbose_name="دانشجوی درخواست‌دهنده")
    service_request_kind = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="service_request_kinds",
        verbose_name="نوع درخواست خدمات",
        limit_choices_to={"category": "service_request_type"},
        null=True,
        blank=True,
    )
    service_request_data = models.TextField(null=False, blank=True, verbose_name="اطلاعات تکمیلی درخواست")
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
        kind_label = self.service_request_kind.label if self.service_request_kind else "نامشخص"
        return f"درخواست شماره {self.student_service_case_key} - {kind_label}"


# ==========================================
# درخواست بورسیه
# ==========================================
class ScholarshipApplication(models.Model):
    scholarship_application_key = models.AutoField(primary_key=True)
    scholarship_applicant = models.ForeignKey("Student", on_delete=models.PROTECT, related_name="scholarship_applications")
    scholarship_type = models.CharField(max_length=50)
    scholarship_reason = models.TextField()
    scholarship_status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="scholarship_statuses",
        verbose_name="وضعیت درخواست",
        limit_choices_to={"category": "review_status"},
        null=True,
        blank=True,
    )
    scholarship_submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "درخواست بورسیه"
        verbose_name_plural = "درخواست‌های بورسیه"
        db_table = "ScholarshipApplication"
        verbose_name = "درخواست بورسیه"
        verbose_name_plural = "درخواست‌های بورسیه"

    def __str__(self):
        return f"درخواست بورسیه {self.scholarship_application_key}"


# ==========================================
# جلسات مشاوره
# ==========================================
class CounselingAppointment(models.Model):
    counseling_appointment_key = models.AutoField(primary_key=True)
    counseling_student_link = models.ForeignKey("Student", on_delete=models.PROTECT, related_name="counseling_appointments")
    counseling_teacher_link = models.ForeignKey("Teacher", on_delete=models.PROTECT, related_name="counseling_appointments")
    counseling_date = models.DateTimeField()
    counseling_topic = models.CharField(max_length=255)
    counseling_description = models.TextField(blank=True)
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
        verbose_name = "وقت مشاوره"
        verbose_name_plural = "وقت‌های مشاوره"
        db_table = "CounselingAppointment"
        verbose_name = "جلسه مشاوره"
        verbose_name_plural = "جلسات مشاوره"

    def __str__(self):
        return f"جلسه مشاوره {self.counseling_appointment_key}"


# ==========================================
# پروپوزال
# ==========================================
class Proposal(models.Model):
    proposal_case_key = models.AutoField(primary_key=True)
    proposal_student_link = models.ForeignKey("Student", on_delete=models.PROTECT, related_name="proposals")
    proposal_title = models.CharField(max_length=255)
    proposal_description = models.TextField()
    proposal_submitted_at = models.DateTimeField(auto_now_add=True)
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
        verbose_name = "پروپوزال"
        verbose_name_plural = "پروپوزال‌ها"
        db_table = "Proposal"
        verbose_name = "پروپوزال"
        verbose_name_plural = "پروپوزال‌ها"

    def __str__(self):
        return self.proposal_title


# ==========================================
# درخواست مهمانی
# ==========================================
class TransferRequest(models.Model):
    transfer_id = models.AutoField(primary_key=True, verbose_name="شناسه درخواست")
    student = models.ForeignKey("Student", on_delete=models.PROTECT, related_name="transfer_requests", verbose_name="دانشجو")
    destination_university = models.CharField(max_length=255, verbose_name="نام دانشگاه مقصد")
    review_status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="transfer_request_statuses",
        verbose_name="وضعیت بررسی",
        limit_choices_to={"category": "review_status"},
        null=True,
        blank=True,
    )
    course_compatibility_result = models.TextField(blank=True, default="", verbose_name="نتیجه بررسی دروس")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت درخواست")

    @property
    def is_approved(self):
        return self.review_status.code == "approved" if self.review_status else False

    class Meta:
        db_table = "TransferRequest"
        verbose_name = "درخواست مهمانی درس"
        verbose_name_plural = "درخواست‌های مهمانی دروس"
        ordering = ["-transfer_id"]

    def __str__(self):
        status_label = self.review_status.label if self.review_status else "نامشخص"
        return f"درخواست مهمانی {self.transfer_id} - {self.student} - {status_label}"


# ==========================================
# بررسی فارغ‌التحصیلی
# ==========================================
class GraduationAudit(models.Model):
    audit_id = models.AutoField(primary_key=True, verbose_name="شناسه بررسی")
    student = models.ForeignKey("Student", on_delete=models.PROTECT, related_name="graduation_audits", verbose_name="دانشجو")
    curriculum = models.ForeignKey("Curriculum", on_delete=models.PROTECT, related_name="graduation_audits", verbose_name="چارت درسی")
    graduation_status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="graduation_statuses",
        verbose_name="وضعیت فارغ‌التحصیلی",
        limit_choices_to={"category": "graduation_status"},
        null=True,
        blank=True,
    )
    audit_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ بررسی")

    @property
    def remaining_units(self):
        total_curriculum_units = Curriculum.objects.filter(
            field=self.curriculum.field,
            is_active=True
        ).aggregate(total=models.Sum('calculated_units'))['total'] or 0
        return max(total_curriculum_units - self.student.passed_units, 0)

    @property
    def is_graduation_eligible(self):
        return (
            self.remaining_units == 0
            and self.graduation_status and self.graduation_status.code == "eligible"
        )

    class Meta:
        db_table = "GraduationAudit"
        verbose_name = "بررسی فارغ‌التحصیلی"
        verbose_name_plural = "بررسی‌های فارغ‌التحصیلی"
        ordering = ["-audit_date"]
        unique_together = [("student", "curriculum")]

    def __str__(self):
        status_label = self.graduation_status.label if self.graduation_status else "نامشخص"
        return f"بررسی {self.audit_id} - {self.student} - {status_label}"


# ==========================================
# تاریخچه تغییرات آموزشی
# ==========================================
class EducationalChangeLog(models.Model):
    log_id = models.AutoField(primary_key=True, verbose_name="شناسه تاریخچه")
    student = models.ForeignKey("Student", on_delete=models.PROTECT, related_name="educational_change_logs", verbose_name="دانشجو")
    change_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="change_types",
        verbose_name="نوع تغییر",
        limit_choices_to={"category": "change_type"},
        null=True,
        blank=True,
    )
    changed_by = models.ForeignKey("UserAccount", on_delete=models.PROTECT, related_name="educational_change_logs", verbose_name="کاربر ثبت‌کننده")
    changed_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ و ساعت تغییر")
    description = models.TextField(blank=True, default="", verbose_name="توضیحات تغییر")

    @property
    def change_type_label(self):
        return self.change_type.label if self.change_type else "نامشخص"

    class Meta:
        db_table = "EducationalChangeLog"
        verbose_name = "تاریخچه تغییر آموزشی"
        verbose_name_plural = "تاریخچه تغییرات آموزشی"
        ordering = ["-changed_at"]

    def __str__(self):
        return f"تغییر {self.log_id} - {self.student} - {self.change_type_label}"


# ==========================================
# چارت درسی
# ==========================================
class Curriculum(models.Model):
    curriculum_id = models.AutoField(primary_key=True, verbose_name="شناسه چارت")
    field = models.ForeignKey("Field", on_delete=models.CASCADE, related_name="curriculums", verbose_name="رشته تحصیلی")
    lesson = models.ForeignKey("Lesson", on_delete=models.CASCADE, related_name="curriculums", verbose_name="درس")
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
# ارتباطات و مکاتبات
# ==========================================
class Communication(models.Model):
    communication_id = models.AutoField(primary_key=True, verbose_name="شناسه مکاتبه")
    sender = models.ForeignKey("UserAccount", on_delete=models.CASCADE, related_name="sent_messages", verbose_name="فرستنده")
    receiver = models.ForeignKey("UserAccount", on_delete=models.CASCADE, related_name="received_messages", verbose_name="گیرنده")
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
# تنظیمات پویای سیستم
# ==========================================
class SystemSetting(models.Model):
    setting_id = models.AutoField(primary_key=True, verbose_name="شناسه تنظیم")
    setting_key = models.CharField(max_length=100, unique=True, verbose_name="کلید تنظیم")
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
    updated_by = models.ForeignKey("UserAccount", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="به‌روزرسانی‌کننده")

    class Meta:
        db_table = "SystemSetting"
        verbose_name = "تنظیمات سیستم"
        verbose_name_plural = "تنظیمات سیستم"
        ordering = ["setting_key"]

    def __str__(self):
        
        return f"{self.setting_key} = {self.setting_value}"
        
# ==========================================
# درخواست تطبیق واحد
# ==========================================
class CreditTransferRequest(models.Model):
    transfer_request_id = models.AutoField(primary_key=True, verbose_name="شناسه درخواست")
    student = models.ForeignKey("Student", on_delete=models.PROTECT, related_name="credit_transfer_requests", verbose_name="دانشجو")
    source_university = models.CharField(max_length=255, verbose_name="دانشگاه مبدا")
    request_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ درخواست")
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

    class Meta:
        verbose_name = "درخواست تطبیق واحد"
        verbose_name_plural = "درخواست‌های تطبیق واحد"


# ==========================================
# درخواست کارآموزی (اولیه)
# ==========================================
class InternshipRequest(models.Model):
    internship_request_id = models.AutoField(primary_key=True, verbose_name="شناسه درخواست")
    student = models.ForeignKey("Student", on_delete=models.PROTECT, related_name="internship_requests", verbose_name="دانشجو")
    organization_name = models.CharField(max_length=255, verbose_name="نام سازمان")
    start_date = models.DateField(verbose_name="تاریخ شروع")
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

    class Meta:
        verbose_name = "درخواست کارآموزی"
        verbose_name_plural = "درخواست‌های کارآموزی"


# ==========================================
# گزارش پیشرفت پایان‌نامه
# ==========================================
class ThesisProgressReport(models.Model):
    report_id = models.AutoField(primary_key=True, verbose_name="شناسه گزارش")
    student = models.ForeignKey("Student", on_delete=models.PROTECT, related_name="thesis_progress_reports", verbose_name="دانشجو")
    teacher = models.ForeignKey("Teacher", on_delete=models.PROTECT, related_name="thesis_progress_reports", verbose_name="استاد")
    report_content = models.TextField(verbose_name="متن گزارش")
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

    class Meta:
        verbose_name = "گزارش پیشرفت پایان‌نامه"
        verbose_name_plural = "گزارش‌های پیشرفت پایان‌نامه"


# ==========================================
# نوتیفیکیشن
# ==========================================
class Notification(models.Model):
    user = models.ForeignKey("UserAccount", on_delete=models.CASCADE, related_name="notifications", verbose_name="کاربر دریافت‌کننده")
    title = models.CharField(max_length=255, verbose_name="عنوان اعلان")
    message = models.TextField(verbose_name="متن اعلان")
    related_exam = models.ForeignKey("Exam", on_delete=models.SET_NULL, null=True, blank=True, related_name="notifications", verbose_name="امتحان مرتبط")
    notification_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="notification_types",
        verbose_name="نوع اعلان",
        limit_choices_to={"category": "notification_type"},
        null=True,
        blank=True,
    )
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان ارسال")
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان خوانده شدن")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد رکورد")

    class Meta:
        verbose_name = "اعلان"
        verbose_name_plural = "اعلان‌ها"

    def __str__(self):
        type_label = self.notification_type.label if self.notification_type else "نامشخص"
        return f"{type_label}: {self.title}"


# ==========================================
# نظرسنجی اساتید
# ==========================================
class TeacherSurvey(models.Model):
    enrollment = models.ForeignKey("Enrollment", on_delete=models.CASCADE, related_name="teacher_surveys", verbose_name="ثبت‌نام")
    overall_rating = models.PositiveSmallIntegerField(verbose_name="امتیاز کلی")
    teaching_quality = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="کیفیت تدریس")
    behavior = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="رفتار استاد")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ثبت نظرسنجی")
    comment = models.TextField(blank=True, verbose_name="نظر دانشجو")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد رکورد")

    class Meta:
        verbose_name = "نظرسنجی استاد و درس"
        verbose_name_plural = "نظرسنجی‌های استاد و درس"
        constraints = [
            models.CheckConstraint(condition=models.Q(overall_rating__gte=1, overall_rating__lte=5), name="ts_rating_1_5"),
            models.CheckConstraint(
                condition=(models.Q(teaching_quality__isnull=True) | models.Q(teaching_quality__gte=1, teaching_quality__lte=5)),
                name="ts_quality_1_5",
            ),
            models.CheckConstraint(
                condition=(models.Q(behavior__isnull=True) | models.Q(behavior__gte=1, behavior__lte=5)),
                name="ts_behavior_1_5",
            ),
        ]

    def __str__(self):
        return f"نظرسنجی با امتیاز {self.overall_rating} از ۵"


# ==========================================
# کارآموزی (اصلی)
# ==========================================
class Internship(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE, related_name="internship_records", verbose_name="دانشجو")
    request_type = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="internship_request_types",
        verbose_name="نوع درخواست",
        limit_choices_to={"category": "internship_request_type"},
        null=True,
        blank=True,
    )
    company_name = models.CharField(max_length=255, verbose_name="نام شرکت یا سازمان")
    intern_start_date = models.DateField(verbose_name="تاریخ شروع کارآموزی")
    duration_hours = models.PositiveIntegerField(verbose_name="مدت کارآموزی به ساعت")
    status = models.ForeignKey(
        Constant,
        on_delete=models.PROTECT,
        related_name="internship_statuses",
        verbose_name="وضعیت درخواست",
        limit_choices_to={"category": "review_status"},
        null=True,
        blank=True,
    )
    reviewed_by = models.ForeignKey("UserAccount", on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_internship_requests", verbose_name="بررسی‌کننده")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان بررسی")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد درخواست")

    class Meta:
        verbose_name = "درخواست کارآموزی"
        verbose_name_plural = "درخواست‌های کارآموزی"

    def __str__(self):
        req_label = self.request_type.label if self.request_type else "نامشخص"
        return f"{req_label} - {self.company_name}"


# ==========================================
# دانشکده
# ==========================================
class Faculty(models.Model):
    faculty_name = models.CharField(max_length=150, verbose_name="نام دانشکده")
    faculty_code = models.CharField(max_length=20, unique=True, verbose_name="کد دانشکده")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "دانشکده"
        verbose_name_plural = "دانشکده‌ها"
        ordering = ["faculty_name"]

    def __str__(self):
        return self.faculty_name


# ==========================================
# گروه آموزشی
# ==========================================
class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT, related_name="departments", verbose_name="دانشکده")
    department_name = models.CharField(max_length=150, verbose_name="نام گروه آموزشی")
    department_code = models.CharField(max_length=20, verbose_name="کد گروه آموزشی")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "گروه آموزشی"
        verbose_name_plural = "گروه‌های آموزشی"
        ordering = ["department_name"]
        constraints = [
            models.UniqueConstraint(fields=["faculty", "department_code"], name="unique_department_code_per_faculty"),
        ]

    def __str__(self):
        return f"{self.department_name} ({self.faculty.faculty_name})"


# ==========================================
# رشته تحصیلی
# ==========================================
class Field(models.Model):
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="fields", verbose_name="گروه آموزشی")
    field_name = models.CharField(max_length=150, verbose_name="نام رشته")
    field_code = models.CharField(max_length=20, verbose_name="کد رشته")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "رشته تحصیلی"
        verbose_name_plural = "رشته‌های تحصیلی"
        ordering = ["field_name"]
        constraints = [
            models.UniqueConstraint(fields=["department", "field_code"], name="unique_field_code_per_department"),
        ]

    def __str__(self):
        return f"{self.field_name} ({self.department.department_name})"

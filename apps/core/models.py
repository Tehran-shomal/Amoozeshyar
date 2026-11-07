from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.fields.related import _OnDeleteOptions


# شخص (جایگزین User پیش‌فرض جنگو)
class Person(AbstractUser):
    gender = models.CharField(
        max_length=1,
        choices=[
            ("F", "Female"),
            ("M", "Male"),
        ],
    )
    address = models.TextField()
    email = models.EmailField(unique=True)
    father_name = models.CharField(max_length=100)
    birth_place = models.CharField(max_length=100)

    national_id = models.CharField(max_length = 15)


# استاد
class Teacher(models.Model):
    id = models.BigAutoField(primary_key=True)
    person = models.OneToOneField(
        Person, on_delete=models.CASCADE, related_name="teacher"
    )
    teacher_code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey("Department", on_delete=models.PROTECT)
    academic_rank = models.CharField(max_length=100)
    hire_date = models.DateField()


# دانشجو
class Student(models.Model):
    id = models.BigAutoField(primary_key = True)

    person = models.OneToOneField(
        Person, on_delete=models.CASCADE, related_name="student"
    )
    admission_type = models.CharField(max_length=100)
    previous_term_gpa = models.DecimalField(max_digits=4, decimal_places=2)
    total_gpa = models.DecimalField(max_digits=4, decimal_places=2)
    passed_units = models.IntegerField()
    tuition_debt = models.DecimalField(max_digits=12, decimal_places=2)

    student_code = models.CharField(max_length = 20)

    educational_level = models.CharField(max_length = 30)

    application_date = models.DateField(auto_now_add = True)

    # student_info = models.OneToOneField(
    #     Person,
    #     on_delete = models.CASCADE,
    #     related_name = "education_info"
    # )

    # field = models.ForeignKey(
    #     Field,
    #     on_delete = models.SET_DEFAULT,
    #     related_name = "students"
    # )



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
class Term(models.Model):
    id = models.BigAutoField(primary_key=True)
    term_code = models.CharField(max_length=20, unique=True)
    semester = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()
    add_drop_start = models.DateTimeField()
    add_drop_end = models.DateTimeField()
    emergency_drop_start = models.DateTimeField()
    emergency_drop_end = models.DateTimeField()
    is_active = models.BooleanField(default=False)


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
    id = models.BigIntegerField(primary_key = True)

    name = models.CharField(max_length = 50)

    created_at = models.DateTimeField(auto_now_add = True)

    created_by = models.ForeignKey(
        Person,
        on_delete = models.CASCADE,
        related_name = "lesson_groups"
    )

    members = models.ManyToManyField(
        Person,
        related_name = "lesson_groups"
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete = models.DO_NOTHING,
        related_name = "lesson_groups"
    )

    is_active = models.BooleanField(default = True)

# مجوزهای پارکینگ
class ParkingPasses(models.Model):
    id = models.BigAutoField(primary_key = True)

    parking_pass_code = models.CharField(max_length = 50)

    aquisition_date = models.DateField(auto_now_add = True)

    expiration_date = models.DateField

    charge = models.BigIntegerField

    owner = models.OneToOneField(
        Person,
        on_delete = models.CASCADE,
        related_name = "parking_pass"
    )


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
class UserAccount(models.Model):  # مدل حساب کاربری؛ Django از آن جدول پایگاه داده می‌سازد

    user_id = models.AutoField(
        primary_key=True,  # شناسهٔ اصلی و یکتای هر حساب؛ خودکار افزایش می‌یابد
        verbose_name='شناسه حساب کاربری'  # نام قابل‌نمایش فیلد در پنل مدیریت
    )

    person = models.ForeignKey(
        'Person',  # هر حساب به یک شخص از مدل Person متصل است
        on_delete=models.CASCADE,  # با حذف شخص، حساب او هم حذف می‌شود
        related_name='user_accounts',  # دسترسی از شخص به حساب‌هایش: person.user_accounts
        verbose_name='شخص'
    )

    role = models.ForeignKey(
        'Role',  # نقش این حساب را مشخص می‌کند؛ مثلاً دانشجو یا مدیر
        on_delete=models.PROTECT,  # تا وقتی حسابی از این نقش استفاده می‌کند، حذف نقش ممنوع است
        related_name='user_accounts',  # دسترسی از نقش به حساب‌های دارای آن نقش
        verbose_name='نقش'
    )

    username = models.CharField(
        max_length=150,  # حداکثر طول نام کاربری
        unique=True,  # هر نام کاربری باید یکتا باشد
        verbose_name='نام کاربری'
    )

    password = models.CharField(
        max_length=128,  # طول فیلد ذخیرهٔ رمز هش‌شده
        verbose_name='رمز عبور'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,  # زمان ایجاد حساب را خودکار ذخیره می‌کند
        verbose_name='تاریخ ثبت'
    )

    is_active = models.BooleanField(
        default=True,  # حساب به‌صورت پیش‌فرض فعال است
        verbose_name='فعال'
    )

    failed_login_count = models.PositiveIntegerField(
        default=0,  # تعداد تلاش‌های ناموفق؛ عدد منفی نمی‌پذیرد
        verbose_name='تعداد تلاش ناموفق'
    )

    locked_until = models.DateTimeField(
        null=True,  # در دیتابیس می‌تواند خالی باشد
        blank=True,  # در فرم‌های Django هم اختیاری است
        verbose_name='قفل تا'
    )

    last_login_at = models.DateTimeField(
        null=True,  # ممکن است کاربر هنوز وارد نشده باشد
        blank=True,
        verbose_name='آخرین ورود'
    )

    last_activity_at = models.DateTimeField(
        null=True,  # ممکن است هنوز فعالیتی ثبت نشده باشد
        blank=True,
        verbose_name='آخرین فعالیت'
    )

    password_changed_at = models.DateTimeField(
        null=True,  # ممکن است زمان تغییر رمز هنوز ثبت نشده باشد
        blank=True,
        verbose_name='تاریخ تغییر رمز'
    )

    def __str__(self):
        return self.username  # هنگام نمایش حساب، نام کاربری را نشان می‌دهد


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
class Attendance(models.Model):  # مدل ثبت اطلاعات حضور و غیاب

    enrollment = models.ForeignKey(  # ارتباط این رکورد با ثبت‌نام هنرجو
        'Enrollment',  # نام مدل ثبت‌نام
        on_delete=models.CASCADE  # با حذف ثبت‌نام، رکورد حضور و غیاب هم حذف می‌شود
    )

    session_number = models.IntegerField()  # شمارهٔ جلسه

    session_date = models.DateField()  # تاریخ برگزاری جلسه

    attendance_status = models.CharField(max_length=50)  # وضعیت حضور، مثل حاضر یا غایب

    attendance_time = models.TimeField()  # ساعت حضور یا ثبت وضعیت

    description = models.TextField()  # توضیحات تکمیلی

    recorded_by = models.ForeignKey(  # ارتباط با حساب کاربری ثبت‌کننده
        'UserAccount',  # نام مدل حساب کاربری
        on_delete=models.CASCADE  # با حذف حساب کاربری، این رکورد هم حذف می‌شود
    )

    created_at = models.DateTimeField(auto_now_add=True)  # زمان ایجاد رکورد که خودکار ثبت می‌شود


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
    SCHOLARSHIP_STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("approved", "تأیید شده"),
        ("rejected", "رد شده"),
    ]

    scholarship_application_key = models.AutoField(
        primary_key=True,
        db_column="ScholarshipApplicationKey"
    )

    scholarship_applicant = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="scholarship_applications",
        db_column="ScholarshipApplicantLinkId"
    )

    scholarship_type = models.CharField(
        max_length=50,
        db_column="ScholarshipType"
    )

    scholarship_reason = models.TextField(
        db_column="ScholarshipReason"
    )

    scholarship_status = models.CharField(
        max_length=20,
        choices=SCHOLARSHIP_STATUS_CHOICES,
        default="pending",
        db_column="ScholarshipStatus"
    )

    scholarship_submitted_at = models.DateTimeField(
        auto_now_add=True,
        db_column="ScholarshipSubmittedAt"
    )

    class Meta:
        db_table = "ScholarshipApplication"

    def __str__(self):
        return f"درخواست بورسیه {self.scholarship_application_key}"


# جلسات مشاوره
class CounselingAppointment(models.Model):
    COUNSELING_STATUS_CHOICES = [
        ("pending", "در انتظار برگزاری"),
        ("completed", "برگزار شده"),
        ("cancelled", "لغو شده"),
    ]

    counseling_appointment_key = models.AutoField(
        primary_key=True,
        db_column="CounselingAppointmentKey"
    )

    counseling_student_link = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="counseling_appointments",
        db_column="CounselingStudentLinkId"
    )

    counseling_teacher_link = models.ForeignKey(
        "core.Teacher",
        on_delete=models.PROTECT,
        related_name="counseling_appointments",
        db_column="CounselingTeacherLinkId"
    )

    counseling_date = models.DateTimeField(
        db_column="CounselingDate"
    )

    counseling_topic = models.CharField(
        max_length=255,
        db_column="CounselingTopic"
    )

    counseling_description = models.TextField(
        blank=True,
        db_column="CounselingDescription"
    )

    counseling_status = models.CharField(
        max_length=20,
        choices=COUNSELING_STATUS_CHOICES,
        default="pending",
        db_column="CounselingStatus"
    )

    class Meta:
        db_table = "CounselingAppointment"

    def __str__(self):
        return f"جلسه مشاوره {self.counseling_appointment_key}"

# پروپوزال
class Proposal(models.Model):
    PROPOSAL_STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("approved", "تأیید شده"),
        ("rejected", "رد شده"),
    ]

    proposal_case_key = models.AutoField(
        primary_key=True,
        db_column="ProposalCaseKey"
    )

    proposal_student_link = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="proposals",
        db_column="ProposalStudentLinkId"
    )

    proposal_title = models.CharField(
        max_length=255,
        db_column="ProposalTitle"
    )

    proposal_description = models.TextField(
        db_column="ProposalDescription"
    )

    proposal_submitted_at = models.DateTimeField(
        auto_now_add=True,
        db_column="ProposalSubmittedAt"
    )

    proposal_status = models.CharField(
        max_length=20,
        choices=PROPOSAL_STATUS_CHOICES,
        default="pending",
        db_column="ProposalStatus"
    )

    class Meta:
        db_table = "Proposal"

    def __str__(self):
        return self.proposal_title

# درخواست مهمانی دروس
class TransferRequest(models.Model):
    REVIEW_STATUS_CHOICES = [
        ("pending", "در انتظار بررسی"),
        ("approved", "تأیید شده"),
        ("rejected", "رد شده"),
    ]

    transfer_id = models.AutoField(
        primary_key=True,
        db_column="TransferId",
        verbose_name="شناسه درخواست",
    )

    student = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="transfer_requests",
        db_column="StudentId",
        verbose_name="دانشجو",
    )

    destination_university = models.CharField(
        max_length=255,
        db_column="DestinationUniversity",
        verbose_name="نام دانشگاه مقصد",
    )

    review_status = models.CharField(
        max_length=20,
        choices=REVIEW_STATUS_CHOICES,
        default="pending",
        db_column="ReviewStatus",
        verbose_name="وضعیت بررسی",
    )

    course_compatibility_result = models.TextField(
        blank=True,
        db_column="CourseCompatibilityResult",
        verbose_name="نتیجه بررسی دروس",
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

# بررسی شرایط فارغ‌التحصیلی
class GraduationAudit(models.Model):
    GRADUATION_STATUS_CHOICES = [
        ("eligible", "واجد شرایط"),
        ("not_eligible", "فاقد شرایط"),
        ("under_review", "در حال بررسی"),
    ]

    audit_id = models.AutoField(
        primary_key=True,
        db_column="AuditId",
        verbose_name="شناسه بررسی",
    )

    student = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="graduation_audits",
        db_column="StudentId",
        verbose_name="دانشجو",
    )

    curriculum = models.ForeignKey(
        "core.Curriculum",
        on_delete=models.PROTECT,
        related_name="graduation_audits",
        db_column="CurriculumId",
        verbose_name="چارت درسی",
    )

    remaining_units = models.PositiveIntegerField(
        default=0,
        db_column="RemainingUnits",
        verbose_name="تعداد واحد باقی‌مانده",
    )

    graduation_status = models.CharField(
        max_length=20,
        choices=GRADUATION_STATUS_CHOICES,
        default="under_review",
        db_column="GraduationStatus",
        verbose_name="وضعیت فارغ‌التحصیلی",
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


# تاریخچه تغییرات آموزشی
class EducationalChangeLog(models.Model):
    CHANGE_TYPE_CHOICES = [
        ("grade_change", "تغییر نمره"),
        ("course_deletion", "حذف درس"),
        ("academic_status_change", "تغییر وضعیت تحصیلی"),
    ]

    log_id = models.AutoField(
        primary_key=True,
        db_column="LogId",
        verbose_name="شناسه تاریخچه",
    )

    student = models.ForeignKey(
        "core.Student",
        on_delete=models.PROTECT,
        related_name="educational_change_logs",
        db_column="StudentId",
        verbose_name="دانشجو",
    )

    change_type = models.CharField(
        max_length=30,
        choices=CHANGE_TYPE_CHOICES,
        db_column="ChangeType",
        verbose_name="نوع تغییر",
    )

    changed_by = models.ForeignKey(
        "core.UserAccount",
        on_delete=models.PROTECT,
        related_name="educational_change_logs",
        db_column="ChangedBy",
        verbose_name="کاربر ثبت‌کننده",
    )

    changed_at = models.DateTimeField(
        auto_now_add=True,
        db_column="ChangedAt",
        verbose_name="تاریخ و ساعت تغییر",
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


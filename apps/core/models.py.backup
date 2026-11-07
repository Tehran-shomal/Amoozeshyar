from django.db import models

# ==========================================
class Person(models.Model):

    person_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50, verbose_name="نام")
    last_name = models.CharField(max_length=50, verbose_name="نام خانوادگی")
    national_id = models.CharField(max_length=10, unique=True, verbose_name="کد ملی")
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name="ایمیل")
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name="شماره تماس")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Teacher(models.Model):
    """FUAD01: ثبت استاد جدید - FUAD02: غیرفعال کردن استاد"""
    teacher_id = models.AutoField(primary_key=True)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, verbose_name="شخص")
    teacher_code = models.CharField(max_length=20, unique=True, verbose_name="کد استاد")
    department = models.CharField(max_length=100, verbose_name="گروه آموزشی")
    is_active = models.BooleanField(default=True, verbose_name="فعال (غیرفعال کردن بدون حذف فیزیکی)")
    hire_date = models.DateField(null=True, blank=True, verbose_name="تاریخ استخدام")

    def __str__(self):
        return self.teacher_code

class Student(models.Model):
    """FUAD03: ثبت دانشجو - FUAD04: ویرایش - FUAD05: غیرفعال کردن - FUAD06: جستجو"""
    student_id = models.AutoField(primary_key=True)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, verbose_name="شخص")
    student_code = models.CharField(max_length=20, unique=True, verbose_name="شماره دانشجویی")
    educational_level = models.CharField(max_length=30, verbose_name="مقطع تحصیلی")
    field_of_study = models.CharField(max_length=100, verbose_name="رشته تحصیلی")
    application_date = models.DateField(verbose_name="تاریخ شروع تحصیل")
    status = models.CharField(max_length=20, verbose_name="وضعیت تحصیلی")
    is_active = models.BooleanField(default=True, verbose_name="فعال (غیرفعال کردن بدون حذف فیزیکی)")

    def __str__(self):
        return self.student_code

# ==========================================

class Lesson(models.Model):

    lesson_id = models.AutoField(primary_key=True)
    lesson_code = models.CharField(max_length=20, unique=True, verbose_name="کد درس")
    title = models.CharField(max_length=150, verbose_name="عنوان درس")
    theory_units = models.IntegerField(default=0, verbose_name="واحد نظری")
    practical_units = models.IntegerField(default=0, verbose_name="واحد عملی")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.lesson_code} - {self.title}"


class Term(models.Model):

    term_id = models.AutoField(primary_key=True)
    term_code = models.CharField(max_length=20, unique=True, verbose_name="کد ترم")
    semester = models.CharField(max_length=10, verbose_name="نیمسال")
    academic_year = models.CharField(max_length=9, verbose_name="سال تحصیلی")
    is_active = models.BooleanField(default=False, verbose_name="ترم جاری")

    def __str__(self):
        return f"{self.academic_year} - {self.semester}"


class Classroom(models.Model):

    classroom_id = models.AutoField(primary_key=True)
    building_name = models.CharField(max_length=100, verbose_name="نام ساختمان")
    room_number = models.CharField(max_length=20, verbose_name="شماره اتاق")
    capacity = models.IntegerField(verbose_name="ظرفیت")

    def __str__(self):
        return f"{self.building_name} - اتاق {self.room_number}"


class CourseOffering(models.Model):
 
    offering_id = models.AutoField(primary_key=True)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, verbose_name="ترم")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="درس")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name="استاد")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, verbose_name="مکان کلاس")
    group_no = models.IntegerField(verbose_name="شماره گروه")
    capacity = models.IntegerField(verbose_name="ظرفیت")
    day_of_week = models.CharField(max_length=10, verbose_name="روز هفته")
    start_time = models.TimeField(verbose_name="ساعت شروع")
    end_time = models.TimeField(verbose_name="ساعت پایان")

    class Meta:
        db_table = 'CourseOffering'
        verbose_name = "ارائه درس"

        unique_together = ('term', 'lesson', 'group_no')

    def __str__(self):
        return f"{self.lesson.title} (گروه {self.group_no})"
# ==========================================

class Enrollment(models.Model):

    enrollment_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="دانشجو")
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, verbose_name="ارائه درس")
    enrollment_date = models.DateTimeField(auto_now_add=True)
    enrollment_status = models.CharField(max_length=20, default='تاییدشده')

    class Meta:
        unique_together = ('student', 'offering') 

    def __str__(self):
        return f"{self.student.student_code} -> {self.offering.lesson.title}"

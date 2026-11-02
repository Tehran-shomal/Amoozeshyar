from django.db import models

# ==========================================
# 1. Person & UserAccount & Role
# ==========================================

class GenderChoices(models.TextChoices):
    MALE = 'male', 'مرد'
    FEMALE = 'female', 'زن'

class RoleNameChoices(models.TextChoices):
    STUDENT = 'student', 'دانشجو'
    TEACHER = 'teacher', 'استاد'
    ADMIN = 'admin', 'مدیر سیستم'
    FINANCIAL = 'financial', 'کارشناس مالی'
    EDUCATIONAL_EXPERT = 'educational_expert', 'کارشناس آموزش'

# ==========================================
# 2. Faculty & Department & Field
# ==========================================

class EducationalLevelChoices(models.TextChoices):
    ASSOCIATE = 'associate', 'کاردانی'
    BACHELOR = 'bachelor', 'کارشناسی'
    MASTER = 'master', 'ارشد'
    PHD = 'phd', 'دکتری'

# ==========================================
# 3. Student & Teacher
# ==========================================

class StudentStatusChoices(models.TextChoices):
    ACTIVE = 'active', 'فعال'
    ON_LEAVE = 'on_leave', 'مرخصی'
    PROBATION = 'probation', 'مشروط'
    GRADUATED = 'graduated', 'فارغ‌التحصیل'
    WITHDRAWN = 'withdrawn', 'انصراف'

class AdmissionTypeChoices(models.TextChoices):
    WITH_EXAM = 'with_exam', 'با آزمون'
    WITHOUT_EXAM = 'without_exam', 'بدون آزمون'

class AcademicRankChoices(models.TextChoices):
    INSTRUCTOR = 'instructor', 'مربی'
    ASSISTANT_PROFESSOR = 'assistant_professor', 'استادیار'
    ASSOCIATE_PROFESSOR = 'associate_professor', 'دانشیار'
    PROFESSOR = 'professor', 'استاد'

# ==========================================
# 4. Lesson & Prerequisite & Classroom
# ==========================================

class LessonTypeChoices(models.TextChoices):
    SPECIALIZED = 'specialized', 'تخصصی'
    GENERAL = 'general', 'عمومی'
    BASIC = 'basic', 'پایه'
    ELECTIVE = 'elective', 'اختیاری'

class PrerequisiteTypeChoices(models.TextChoices):
    PREREQUISITE = 'prerequisite', 'پیش‌نیاز'
    CO_REQUISITE = 'co_requisite', 'هم‌نیاز'

class ClassroomTypeChoices(models.TextChoices):
    CLASS = 'class', 'کلاس معمولی'
    LAB = 'lab', 'آزمایشگاه'
    WORKSHOP = 'workshop', 'کارگاه'

# ==========================================
# 5. Term & CourseOffering
# ==========================================

class SemesterChoices(models.TextChoices):
    MEHR = 'mehr', 'مهر'
    BAHMAN = 'bahman', 'بهمن'
    SUMMER = 'summer', 'تابستان'

class DayOfWeekChoices(models.TextChoices):
    SATURDAY = 'saturday', 'شنبه'
    SUNDAY = 'sunday', 'یکشنبه'
    MONDAY = 'monday', 'دوشنبه'
    TUESDAY = 'tuesday', 'سه‌شنبه'
    WEDNESDAY = 'wednesday', 'چهارشنبه'
    THURSDAY = 'thursday', 'پنجشنبه'
    FRIDAY = 'friday', 'جمعه'

# ==========================================
# 6. Enrollment & Attendance & Exam
# ==========================================

class EnrollmentStatusChoices(models.TextChoices):
    PENDING = 'pending', 'در انتظار تایید'
    APPROVED = 'approved', 'تاییدشده'
    CANCELLED = 'cancelled', 'لغوشده'

class EnrollmentTypeChoices(models.TextChoices):
    NORMAL = 'normal', 'عادی'
    GUEST = 'guest', 'مهمان'

class AttendanceStatusChoices(models.TextChoices):
    PRESENT = 'present', 'حاضر'
    ABSENT = 'absent', 'غایب'
    LATE = 'late', 'تاخیر'

class ExamTypeChoices(models.TextChoices):
    MIDTERM = 'midterm', 'میان‌ترم'
    FINAL = 'final', 'پایان‌ترم'
    ONLINE = 'online', 'مجازی'

# ==========================================
# 7. Payment & GradeAppeal
# ==========================================

class PaymentStatusChoices(models.TextChoices):
    SUCCESS = 'success', 'موفق'
    FAILED = 'failed', 'ناموفق'
    PENDING = 'pending', 'در انتظار'
    REFUNDED = 'refunded', 'بازپرداخت'

class AppealStatusChoices(models.TextChoices):
    PENDING = 'pending', 'در انتظار بررسی'
    APPROVED = 'approved', 'تایید'
    REJECTED = 'rejected', 'رد'

# ==========================================
# 8. Tickets & Communication
# ==========================================

class TicketStatusChoices(models.TextChoices):
    OPEN = 'open', 'باز'
    IN_PROGRESS = 'in_progress', 'در حال بررسی'
    CLOSED = 'closed', 'بسته'

class TicketCreatorRoleChoices(models.TextChoices):
    STUDENT = 'student', 'دانشجو'
    TEACHER = 'teacher', 'استاد'
    STAFF = 'staff', 'کارمند'

class CommunicationStatusChoices(models.TextChoices):
    UNREAD = 'unread', 'خوانده نشده'
    READ = 'read', 'خوانده شده'
    REPLIED = 'replied', 'پاسخ داده شده'

class CommunicationTypeChoices(models.TextChoices):
    OFFICIAL = 'official', 'رسمی'
    INFORMAL = 'informal', 'غیررسمی'
    REQUEST = 'request', 'درخواست'
    ANNOUNCEMENT = 'announcement', 'اطلاعیه'

# ==========================================
# 9. SystemSetting & Curriculum & Notification
# ==========================================

class DataTypeChoices(models.TextChoices):
    INTEGER = 'integer', 'عدد صحیح'
    DECIMAL = 'decimal', 'عدد اعشار'
    STRING = 'string', 'رشته'
    BOOLEAN = 'boolean', 'مقدار منطقی'
    DATE = 'date', 'تاریخ'

class RequirementTypeChoices(models.TextChoices):
    MANDATORY = 'mandatory', 'اجباری'
    ELECTIVE = 'elective', 'اختیاری'
    BASIC = 'basic', 'پایه'

class NotificationTypeChoices(models.TextChoices):
    GRADE = 'grade', 'نمره'
    ANNOUNCEMENT = 'announcement', 'اطلاعیه'
    CLASS_CHANGE = 'class_change', 'تغییر کلاس'
    SYSTEM = 'system', 'سیستمی'

# ==========================================
# 10. Requests (Transfer, Refund, Services)
# ==========================================

class RequestReviewStatusChoices(models.TextChoices):
    PENDING = 'pending', 'در انتظار بررسی'
    APPROVED = 'approved', 'تایید'
    REJECTED = 'rejected', 'رد'
    ISSUED = 'issued', 'صادر شد'

class ServiceRequestTypeChoices(models.TextChoices):
    INSTALLMENT = 'installment', 'تقسیط بدهی'
    WITHDRAWAL = 'withdrawal', 'انصراف از تحصیل'
    EMPLOYMENT_CERTIFICATE = 'employment_certificate', 'گواهی اشتغال'
    INTERNSHIP_LETTER = 'internship_letter', 'نامه کارآموزی'

class InternshipRequestTypeChoices(models.TextChoices):
    INTERNSHIP_LETTER = 'internship_letter', 'نامه کارآموزی'
    INTRODUCTION_LETTER = 'introduction_letter', 'معرفی‌نامه'

# ==========================================
# 11. Academic Processes (Proposal, Thesis, Counseling)
# ==========================================

class ProposalStatusChoices(models.TextChoices):
    PENDING = 'pending', 'در انتظار بررسی'
    APPROVED = 'approved', 'تایید شده'
    REJECTED = 'rejected', 'رد شده'
    NEEDS_REVISION = 'needs_revision', 'نیازمند اصلاح'

class ThesisReviewStatusChoices(models.TextChoices):
    PENDING = 'pending', 'در انتظار بررسی'
    APPROVED = 'approved', 'تایید'
    NEEDS_REVISION = 'needs_revision', 'نیازمند اصلاح'

class CounselingStatusChoices(models.TextChoices):
    SCHEDULED = 'scheduled', 'برنامه‌ریزی شده'
    COMPLETED = 'completed', 'انجام شده'
    CANCELLED = 'cancelled', 'لغو شده'
    REJECTED = 'rejected', 'رد شده'

# ==========================================
# 12. Graduation, ChangeLog, Library, Parking, Dormitory
# ==========================================

class GraduationStatusChoices(models.TextChoices):
    ELIGIBLE = 'eligible', 'واجد شرایط'
    NOT_ELIGIBLE = 'not_eligible', 'فاقد شرایط'
    UNDER_REVIEW = 'under_review', 'در حال بررسی'

class ChangeTypeChoices(models.TextChoices):
    PROFILE_CHANGE = 'profile_change', 'تغییر مشخصات فردی'
    GRADE_CHANGE = 'grade_change', 'تغییر نمره'
    COURSE_DROP = 'course_drop', 'حذف درس'
    STATUS_CHANGE = 'status_change', 'تغییر وضعیت تحصیلی'

class LibraryLoanStatusChoices(models.TextChoices):
    BORROWED = 'borrowed', 'امانت'
    RETURNED = 'returned', 'بازگشته'
    OVERDUE = 'overdue', 'دیرکرد'

class ParkingPassStatusChoices(models.TextChoices):
    ACTIVE = 'active', 'فعال'
    EXPIRED = 'expired', 'منقضی'
    CANCELLED = 'cancelled', 'لغو شده'

class DormitoryTypeChoices(models.TextChoices):
    MALE = 'male', 'پسرانه'
    FEMALE = 'female', 'دخترانه'
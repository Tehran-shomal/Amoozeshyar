# ==========================================
# فایل مقادیر ثابت پروژه (نسخه واحد)
# ==========================================

class Constants:
   
    # ==========================================
    # ۱. جنسیت
    # ==========================================
    GENDER_MALE = 'male'
    GENDER_FEMALE = 'female'
    GENDER_CHOICES = (
        (GENDER_MALE, 'مرد'),
        (GENDER_FEMALE, 'زن'),
    )
    
    # ==========================================
    # ۲. نقش‌ها
    # ==========================================
    ROLE_STUDENT = 'student'
    ROLE_TEACHER = 'teacher'
    ROLE_ADMIN = 'admin'
    ROLE_FINANCIAL = 'financial'
    ROLE_EDUCATIONAL_EXPERT = 'educational_expert'
    ROLE_CHOICES = (
        (ROLE_STUDENT, 'دانشجو'),
        (ROLE_TEACHER, 'استاد'),
        (ROLE_ADMIN, 'مدیر سیستم'),
        (ROLE_FINANCIAL, 'کارشناس مالی'),
        (ROLE_EDUCATIONAL_EXPERT, 'کارشناس آموزش'),
    )
    
    # ==========================================
    # ۳. مقطع تحصیلی
    # ==========================================
    LEVEL_ASSOCIATE = 'associate'
    LEVEL_BACHELOR = 'bachelor'
    LEVEL_MASTER = 'master'
    LEVEL_PHD = 'phd'
    LEVEL_CHOICES = (
        (LEVEL_ASSOCIATE, 'کاردانی'),
        (LEVEL_BACHELOR, 'کارشناسی'),
        (LEVEL_MASTER, 'ارشد'),
        (LEVEL_PHD, 'دکتری'),
    )
    
    # ==========================================
    # ۴. وضعیت دانشجو
    # ==========================================
    STUDENT_ACTIVE = 'active'
    STUDENT_ON_LEAVE = 'on_leave'
    STUDENT_PROBATION = 'probation'
    STUDENT_GRADUATED = 'graduated'
    STUDENT_WITHDRAWN = 'withdrawn'
    STUDENT_STATUS_CHOICES = (
        (STUDENT_ACTIVE, 'فعال'),
        (STUDENT_ON_LEAVE, 'مرخصی'),
        (STUDENT_PROBATION, 'مشروط'),
        (STUDENT_GRADUATED, 'فارغ‌التحصیل'),
        (STUDENT_WITHDRAWN, 'انصراف'),
    )
    
    # ==========================================
    # ۵. نوع پذیرش
    # ==========================================
    ADMISSION_WITH_EXAM = 'with_exam'
    ADMISSION_WITHOUT_EXAM = 'without_exam'
    ADMISSION_TYPE_CHOICES = (
        (ADMISSION_WITH_EXAM, 'با آزمون'),
        (ADMISSION_WITHOUT_EXAM, 'بدون آزمون'),
    )
    
    # ==========================================
    # ۶. مرتبه علمی استاد
    # ==========================================
    RANK_INSTRUCTOR = 'instructor'
    RANK_ASSISTANT_PROFESSOR = 'assistant_professor'
    RANK_ASSOCIATE_PROFESSOR = 'associate_professor'
    RANK_PROFESSOR = 'professor'
    ACADEMIC_RANK_CHOICES = (
        (RANK_INSTRUCTOR, 'مربی'),
        (RANK_ASSISTANT_PROFESSOR, 'استادیار'),
        (RANK_ASSOCIATE_PROFESSOR, 'دانشیار'),
        (RANK_PROFESSOR, 'استاد'),
    )
    
    # ==========================================
    # ۷. نوع درس
    # ==========================================
    LESSON_SPECIALIZED = 'specialized'
    LESSON_GENERAL = 'general'
    LESSON_BASIC = 'basic'
    LESSON_ELECTIVE = 'elective'
    LESSON_TYPE_CHOICES = (
        (LESSON_SPECIALIZED, 'تخصصی'),
        (LESSON_GENERAL, 'عمومی'),
        (LESSON_BASIC, 'پایه'),
        (LESSON_ELECTIVE, 'اختیاری'),
    )
    
    # ==========================================
    # ۸. نوع پیش‌نیاز
    # ==========================================
    PREREQ_PREREQUISITE = 'prerequisite'
    PREREQ_CO_REQUISITE = 'co_requisite'
    PREREQUISITE_TYPE_CHOICES = (
        (PREREQ_PREREQUISITE, 'پیش‌نیاز'),
        (PREREQ_CO_REQUISITE, 'هم‌نیاز'),
    )
    
    # ==========================================
    # ۹. نوع کلاس
    # ==========================================
    CLASSROOM_CLASS = 'class'
    CLASSROOM_LAB = 'lab'
    CLASSROOM_WORKSHOP = 'workshop'
    CLASSROOM_TYPE_CHOICES = (
        (CLASSROOM_CLASS, 'کلاس معمولی'),
        (CLASSROOM_LAB, 'آزمایشگاه'),
        (CLASSROOM_WORKSHOP, 'کارگاه'),
    )
    
    # ==========================================
    # ۱۰. نیمسال
    # ==========================================
    SEMESTER_MEHR = 'mehr'
    SEMESTER_BAHMAN = 'bahman'
    SEMESTER_SUMMER = 'summer'
    SEMESTER_CHOICES = (
        (SEMESTER_MEHR, 'مهر'),
        (SEMESTER_BAHMAN, 'بهمن'),
        (SEMESTER_SUMMER, 'تابستان'),
    )
    
    # ==========================================
    # ۱۱. روز هفته
    # ==========================================
    DAY_SATURDAY = 'saturday'
    DAY_SUNDAY = 'sunday'
    DAY_MONDAY = 'monday'
    DAY_TUESDAY = 'tuesday'
    DAY_WEDNESDAY = 'wednesday'
    DAY_THURSDAY = 'thursday'
    DAY_FRIDAY = 'friday'
    DAY_OF_WEEK_CHOICES = (
        (DAY_SATURDAY, 'شنبه'),
        (DAY_SUNDAY, 'یکشنبه'),
        (DAY_MONDAY, 'دوشنبه'),
        (DAY_TUESDAY, 'سه‌شنبه'),
        (DAY_WEDNESDAY, 'چهارشنبه'),
        (DAY_THURSDAY, 'پنجشنبه'),
        (DAY_FRIDAY, 'جمعه'),
    )
    
    # ==========================================
    # ۱۲. وضعیت ثبت‌نام
    # ==========================================
    ENROLLMENT_PENDING = 'pending'
    ENROLLMENT_APPROVED = 'approved'
    ENROLLMENT_CANCELLED = 'cancelled'
    ENROLLMENT_STATUS_CHOICES = (
        (ENROLLMENT_PENDING, 'در انتظار تایید'),
        (ENROLLMENT_APPROVED, 'تاییدشده'),
        (ENROLLMENT_CANCELLED, 'لغوشده'),
    )
    
    # ==========================================
    # ۱۳. نوع ثبت‌نام
    # ==========================================
    ENROLLMENT_NORMAL = 'normal'
    ENROLLMENT_GUEST = 'guest'
    ENROLLMENT_TYPE_CHOICES = (
        (ENROLLMENT_NORMAL, 'عادی'),
        (ENROLLMENT_GUEST, 'مهمان'),
    )
    
    # ==========================================
    # ۱۴. وضعیت حضور
    # ==========================================
    ATTENDANCE_PRESENT = 'present'
    ATTENDANCE_ABSENT = 'absent'
    ATTENDANCE_LATE = 'late'
    ATTENDANCE_STATUS_CHOICES = (
        (ATTENDANCE_PRESENT, 'حاضر'),
        (ATTENDANCE_ABSENT, 'غایب'),
        (ATTENDANCE_LATE, 'تاخیر'),
    )
    
    # ==========================================
    # ۱۵. نوع آزمون
    # ==========================================
    EXAM_MIDTERM = 'midterm'
    EXAM_FINAL = 'final'
    EXAM_ONLINE = 'online'
    EXAM_TYPE_CHOICES = (
        (EXAM_MIDTERM, 'میان‌ترم'),
        (EXAM_FINAL, 'پایان‌ترم'),
        (EXAM_ONLINE, 'مجازی'),
    )
    
    # ==========================================
    # ۱۶. وضعیت پرداخت
    # ==========================================
    PAYMENT_SUCCESS = 'success'
    PAYMENT_FAILED = 'failed'
    PAYMENT_PENDING = 'pending'
    PAYMENT_REFUNDED = 'refunded'
    PAYMENT_STATUS_CHOICES = (
        (PAYMENT_SUCCESS, 'موفق'),
        (PAYMENT_FAILED, 'ناموفق'),
        (PAYMENT_PENDING, 'در انتظار'),
        (PAYMENT_REFUNDED, 'بازپرداخت'),
    )
    
    # ==========================================
    # ۱۷. وضعیت اعتراض
    # ==========================================
    APPEAL_PENDING = 'pending'
    APPEAL_APPROVED = 'approved'
    APPEAL_REJECTED = 'rejected'
    APPEAL_STATUS_CHOICES = (
        (APPEAL_PENDING, 'در انتظار بررسی'),
        (APPEAL_APPROVED, 'تایید'),
        (APPEAL_REJECTED, 'رد'),
    )
    
    # ==========================================
    # ۱۸. وضعیت تیکت
    # ==========================================
    TICKET_OPEN = 'open'
    TICKET_IN_PROGRESS = 'in_progress'
    TICKET_CLOSED = 'closed'
    TICKET_STATUS_CHOICES = (
        (TICKET_OPEN, 'باز'),
        (TICKET_IN_PROGRESS, 'در حال بررسی'),
        (TICKET_CLOSED, 'بسته'),
    )
    
    # ==========================================
    # ۱۹. نقش سازنده تیکت
    # ==========================================
    TICKET_CREATOR_STUDENT = 'student'
    TICKET_CREATOR_TEACHER = 'teacher'
    TICKET_CREATOR_STAFF = 'staff'
    TICKET_CREATOR_ROLE_CHOICES = (
        (TICKET_CREATOR_STUDENT, 'دانشجو'),
        (TICKET_CREATOR_TEACHER, 'استاد'),
        (TICKET_CREATOR_STAFF, 'کارمند'),
    )
    
    # ==========================================
    # ۲۰. وضعیت مکاتبه
    # ==========================================
    COMMUNICATION_UNREAD = 'unread'
    COMMUNICATION_READ = 'read'
    COMMUNICATION_REPLIED = 'replied'
    COMMUNICATION_STATUS_CHOICES = (
        (COMMUNICATION_UNREAD, 'خوانده نشده'),
        (COMMUNICATION_READ, 'خوانده شده'),
        (COMMUNICATION_REPLIED, 'پاسخ داده شده'),
    )
    
    # ==========================================
    # ۲۱. نوع مکاتبه
    # ==========================================
    COMMUNICATION_OFFICIAL = 'official'
    COMMUNICATION_INFORMAL = 'informal'
    COMMUNICATION_REQUEST = 'request'
    COMMUNICATION_ANNOUNCEMENT = 'announcement'
    COMMUNICATION_TYPE_CHOICES = (
        (COMMUNICATION_OFFICIAL, 'رسمی'),
        (COMMUNICATION_INFORMAL, 'غیررسمی'),
        (COMMUNICATION_REQUEST, 'درخواست'),
        (COMMUNICATION_ANNOUNCEMENT, 'اطلاعیه'),
    )
    
    # ==========================================
    # ۲۲. نوع داده تنظیمات
    # ==========================================
    DATA_TYPE_INTEGER = 'integer'
    DATA_TYPE_DECIMAL = 'decimal'
    DATA_TYPE_STRING = 'string'
    DATA_TYPE_BOOLEAN = 'boolean'
    DATA_TYPE_DATE = 'date'
    DATA_TYPE_CHOICES = (
        (DATA_TYPE_INTEGER, 'عدد صحیح'),
        (DATA_TYPE_DECIMAL, 'عدد اعشار'),
        (DATA_TYPE_STRING, 'رشته'),
        (DATA_TYPE_BOOLEAN, 'مقدار منطقی'),
        (DATA_TYPE_DATE, 'تاریخ'),
    )
    
    # ==========================================
    # ۲۳. نوع درس در چارت
    # ==========================================
    REQUIREMENT_MANDATORY = 'mandatory'
    REQUIREMENT_ELECTIVE = 'elective'
    REQUIREMENT_BASIC = 'basic'
    REQUIREMENT_TYPE_CHOICES = (
        (REQUIREMENT_MANDATORY, 'اجباری'),
        (REQUIREMENT_ELECTIVE, 'اختیاری'),
        (REQUIREMENT_BASIC, 'پایه'),
    )
    
    # ==========================================
    # ۲۴. نوع اعلان
    # ==========================================
    NOTIFICATION_GRADE = 'grade'
    NOTIFICATION_ANNOUNCEMENT = 'announcement'
    NOTIFICATION_CLASS_CHANGE = 'class_change'
    NOTIFICATION_SYSTEM = 'system'
    NOTIFICATION_TYPE_CHOICES = (
        (NOTIFICATION_GRADE, 'نمره'),
        (NOTIFICATION_ANNOUNCEMENT, 'اطلاعیه'),
        (NOTIFICATION_CLASS_CHANGE, 'تغییر کلاس'),
        (NOTIFICATION_SYSTEM, 'سیستمی'),
    )
    
    # ==========================================
    # ۲۵. وضعیت درخواست‌ها
    # ==========================================
    REQUEST_PENDING = 'pending'
    REQUEST_APPROVED = 'approved'
    REQUEST_REJECTED = 'rejected'
    REQUEST_ISSUED = 'issued'
    REQUEST_REVIEW_STATUS_CHOICES = (
        (REQUEST_PENDING, 'در انتظار بررسی'),
        (REQUEST_APPROVED, 'تایید'),
        (REQUEST_REJECTED, 'رد'),
        (REQUEST_ISSUED, 'صادر شد'),
    )
    
    # ==========================================
    # ۲۶. نوع درخواست خدمات
    # ==========================================
    SERVICE_INSTALLMENT = 'installment'
    SERVICE_WITHDRAWAL = 'withdrawal'
    SERVICE_EMPLOYMENT_CERT = 'employment_certificate'
    SERVICE_INTERNSHIP_LETTER = 'internship_letter'
    SERVICE_REQUEST_TYPE_CHOICES = (
        (SERVICE_INSTALLMENT, 'تقسیط بدهی'),
        (SERVICE_WITHDRAWAL, 'انصراف از تحصیل'),
        (SERVICE_EMPLOYMENT_CERT, 'گواهی اشتغال'),
        (SERVICE_INTERNSHIP_LETTER, 'نامه کارآموزی'),
    )
    
    # ==========================================
    # ۲۷. نوع درخواست کارآموزی
    # ==========================================
    INTERNSHIP_LETTER = 'internship_letter'
    INTRODUCTION_LETTER = 'introduction_letter'
    INTERNSHIP_REQUEST_TYPE_CHOICES = (
        (INTERNSHIP_LETTER, 'نامه کارآموزی'),
        (INTRODUCTION_LETTER, 'معرفی‌نامه'),
    )
    
    # ==========================================
    # ۲۸. وضعیت پروپوزال
    # ==========================================
    PROPOSAL_PENDING = 'pending'
    PROPOSAL_APPROVED = 'approved'
    PROPOSAL_REJECTED = 'rejected'
    PROPOSAL_NEEDS_REVISION = 'needs_revision'
    PROPOSAL_STATUS_CHOICES = (
        (PROPOSAL_PENDING, 'در انتظار بررسی'),
        (PROPOSAL_APPROVED, 'تایید شده'),
        (PROPOSAL_REJECTED, 'رد شده'),
        (PROPOSAL_NEEDS_REVISION, 'نیازمند اصلاح'),
    )
    
    # ==========================================
    # ۲۹. وضعیت پایان‌نامه
    # ==========================================
    THESIS_PENDING = 'pending'
    THESIS_APPROVED = 'approved'
    THESIS_NEEDS_REVISION = 'needs_revision'
    THESIS_REVIEW_STATUS_CHOICES = (
        (THESIS_PENDING, 'در انتظار بررسی'),
        (THESIS_APPROVED, 'تایید'),
        (THESIS_NEEDS_REVISION, 'نیازمند اصلاح'),
    )
    
    # ==========================================
    # ۳۰. وضعیت جلسه مشاوره
    # ==========================================
    COUNSELING_SCHEDULED = 'scheduled'
    COUNSELING_COMPLETED = 'completed'
    COUNSELING_CANCELLED = 'cancelled'
    COUNSELING_REJECTED = 'rejected'
    COUNSELING_STATUS_CHOICES = (
        (COUNSELING_SCHEDULED, 'برنامه‌ریزی شده'),
        (COUNSELING_COMPLETED, 'انجام شده'),
        (COUNSELING_CANCELLED, 'لغو شده'),
        (COUNSELING_REJECTED, 'رد شده'),
    )
    
    # ==========================================
    # ۳۱. وضعیت فارغ‌التحصیلی
    # ==========================================
    GRADUATION_ELIGIBLE = 'eligible'
    GRADUATION_NOT_ELIGIBLE = 'not_eligible'
    GRADUATION_UNDER_REVIEW = 'under_review'
    GRADUATION_STATUS_CHOICES = (
        (GRADUATION_ELIGIBLE, 'واجد شرایط'),
        (GRADUATION_NOT_ELIGIBLE, 'فاقد شرایط'),
        (GRADUATION_UNDER_REVIEW, 'در حال بررسی'),
    )
    
    # ==========================================
    # ۳۲. نوع تغییر آموزشی
    # ==========================================
    CHANGE_PROFILE = 'profile_change'
    CHANGE_GRADE = 'grade_change'
    CHANGE_COURSE_DROP = 'course_drop'
    CHANGE_STATUS = 'status_change'
    CHANGE_TYPE_CHOICES = (
        (CHANGE_PROFILE, 'تغییر مشخصات فردی'),
        (CHANGE_GRADE, 'تغییر نمره'),
        (CHANGE_COURSE_DROP, 'حذف درس'),
        (CHANGE_STATUS, 'تغییر وضعیت تحصیلی'),
    )
    
    # ==========================================
    # ۳۳. وضعیت امانت کتاب
    # ==========================================
    LOAN_BORROWED = 'borrowed'
    LOAN_RETURNED = 'returned'
    LOAN_OVERDUE = 'overdue'
    LIBRARY_LOAN_STATUS_CHOICES = (
        (LOAN_BORROWED, 'امانت'),
        (LOAN_RETURNED, 'بازگشته'),
        (LOAN_OVERDUE, 'دیرکرد'),
    )
    
    # ==========================================
    # ۳۴. وضعیت مجوز پارکینگ
    # ==========================================
    PARKING_ACTIVE = 'active'
    PARKING_EXPIRED = 'expired'
    PARKING_CANCELLED = 'cancelled'
    PARKING_PASS_STATUS_CHOICES = (
        (PARKING_ACTIVE, 'فعال'),
        (PARKING_EXPIRED, 'منقضی'),
        (PARKING_CANCELLED, 'لغو شده'),
    )
    
    # ==========================================
    # ۳۵. نوع خوابگاه
    # ==========================================
    DORMITORY_MALE = 'male'
    DORMITORY_FEMALE = 'female'
    DORMITORY_TYPE_CHOICES = (
        (DORMITORY_MALE, 'پسرانه'),
        (DORMITORY_FEMALE, 'دخترانه'),
    )
    
    # ==========================================
    # ۳۶. نوع شماره تماس
    # ==========================================
    CONTACT_MOBILE = 'mobile'
    CONTACT_HOME = 'home'
    CONTACT_WORK = 'work'
    CONTACT_WHATSAPP = 'whatsapp'
    CONTACT_TELEGRAM = 'telegram'
    CONTACT_OTHER = 'other'
    CONTACT_TYPE_CHOICES = (
        (CONTACT_MOBILE, 'موبایل'),
        (CONTACT_HOME, 'تلفن منزل'),
        (CONTACT_WORK, 'تلفن محل کار'),
        (CONTACT_WHATSAPP, 'واتساپ'),
        (CONTACT_TELEGRAM, 'تلگرام'),
        (CONTACT_OTHER, 'سایر'),
    )
    # ==========================================
    # زبان‌های پشتیبانی‌ شده
    # ==========================================
    LANGUAGE_PERSIAN = 'fa'
    LANGUAGE_ENGLISH = 'en'
    LANGUAGE_CHOICES = (
        (LANGUAGE_PERSIAN, 'فارسی'),
        (LANGUAGE_ENGLISH, 'English'),
    )
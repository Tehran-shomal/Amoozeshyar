from django.db import migrations


CONSTANTS = [
    # gender
    ("gender", "male", "مرد"),
    ("gender", "female", "زن"),

    # language
    ("language", "fa", "فارسی"),
    ("language", "en", "انگلیسی"),

    # academic_rank
    ("academic_rank", "instructor", "مربی"),
    ("academic_rank", "assistant_prof", "استادیار"),
    ("academic_rank", "associate_prof", "دانشیار"),
    ("academic_rank", "full_prof", "استاد"),

    # educational_level
    ("educational_level", "associate", "کاردانی"),
    ("educational_level", "bachelor", "کارشناسی"),
    ("educational_level", "master", "کارشناسی ارشد"),
    ("educational_level", "phd", "دکتری"),

    # student_status
    ("student_status", "active", "فعال"),
    ("student_status", "suspended", "مشروط"),
    ("student_status", "graduated", "فارغ‌التحصیل"),
    ("student_status", "withdrawn", "انصراف"),

    # admission_type
    ("admission_type", "national_exam", "کنکور سراسری"),
    ("admission_type", "quota", "سهمیه"),
    ("admission_type", "transfer", "انتقالی"),
    ("admission_type", "guest", "مهمان"),

    # lesson_type
    ("lesson_type", "theoretical", "نظری"),
    ("lesson_type", "practical", "عملی"),
    ("lesson_type", "combined", "نظری-عملی"),
    ("lesson_type", "workshop", "کارگاهی"),

    # semester
    ("semester", "first", "نیمسال اول"),
    ("semester", "second", "نیمسال دوم"),
    ("semester", "summer", "تابستان"),

    # exam_type
    ("exam_type", "midterm", "میان‌ترم"),
    ("exam_type", "final", "پایان‌ترم"),
    ("exam_type", "quiz", "کوییز"),
    ("exam_type", "makeup", "جبرانی"),

    # day_of_week
    ("day_of_week", "saturday", "شنبه"),
    ("day_of_week", "sunday", "یکشنبه"),
    ("day_of_week", "monday", "دوشنبه"),
    ("day_of_week", "tuesday", "سه‌شنبه"),
    ("day_of_week", "wednesday", "چهارشنبه"),
    ("day_of_week", "thursday", "پنجشنبه"),
    ("day_of_week", "friday", "جمعه"),

    # prerequisite_type
    ("prerequisite_type", "prerequisite", "پیش‌نیاز"),
    ("prerequisite_type", "corequisite", "هم‌نیاز"),

    # appeal_status
    ("appeal_status", "pending", "در انتظار بررسی"),
    ("appeal_status", "accepted", "پذیرفته شده"),
    ("appeal_status", "rejected", "رد شده"),

    # attendance_status
    ("attendance_status", "present", "حاضر"),
    ("attendance_status", "absent", "غایب"),
    ("attendance_status", "late", "تأخیر"),
    ("attendance_status", "excused", "موجه"),

    # ticket_creator_role
    ("ticket_creator_role", "student", "دانشجو"),
    ("ticket_creator_role", "teacher", "استاد"),
    ("ticket_creator_role", "staff", "کارمند"),
    ("ticket_creator_role", "admin", "مدیر"),

    # ticket_status
    ("ticket_status", "open", "باز"),
    ("ticket_status", "in_progress", "در حال بررسی"),
    ("ticket_status", "closed", "بسته"),

    # review_status (مشترک بین چند مدل)
    ("review_status", "pending", "در انتظار بررسی"),
    ("review_status", "approved", "تأیید شده"),
    ("review_status", "rejected", "رد شده"),

    # service_request_type
    ("service_request_type", "dormitory", "خوابگاه"),
    ("service_request_type", "loan", "وام"),
    ("service_request_type", "certificate", "گواهی"),
    ("service_request_type", "other", "سایر"),

    # counseling_status
    ("counseling_status", "pending", "در انتظار"),
    ("counseling_status", "confirmed", "تأیید شده"),
    ("counseling_status", "done", "انجام شده"),
    ("counseling_status", "canceled", "لغو شده"),

    # proposal_status
    ("proposal_status", "pending", "در انتظار بررسی"),
    ("proposal_status", "approved", "تأیید شده"),
    ("proposal_status", "rejected", "رد شده"),

    # graduation_status
    ("graduation_status", "eligible", "واجد شرایط"),
    ("graduation_status", "not_eligible", "فاقد شرایط"),
    ("graduation_status", "under_review", "در حال بررسی"),

    # change_type
    ("change_type", "grade_change", "تغییر نمره"),
    ("change_type", "course_deletion", "حذف درس"),
    ("change_type", "academic_status_change", "تغییر وضعیت تحصیلی"),

    # requirement_type
    ("requirement_type", "mandatory", "اجباری"),
    ("requirement_type", "elective", "اختیاری"),
    ("requirement_type", "basic", "پایه"),
    ("requirement_type", "specialized", "تخصصی"),

    # communication_type
    ("communication_type", "message", "پیام"),
    ("communication_type", "announcement", "اطلاعیه"),
    ("communication_type", "letter", "نامه"),

    # communication_status
    ("communication_status", "sent", "ارسال شده"),
    ("communication_status", "delivered", "تحویل شده"),
    ("communication_status", "read", "خوانده شده"),

    # data_type
    ("data_type", "int", "عدد صحیح"),
    ("data_type", "float", "عدد اعشاری"),
    ("data_type", "string", "متن"),
    ("data_type", "bool", "بولی"),

    # thesis_review_status
    ("thesis_review_status", "pending", "در انتظار بررسی"),
    ("thesis_review_status", "approved", "تأیید شده"),
    ("thesis_review_status", "needs_revision", "نیازمند اصلاح"),

    # notification_type
    ("notification_type", "grade", "نمره"),
    ("notification_type", "announcement", "اطلاعیه"),
    ("notification_type", "class_change", "تغییر کلاس"),
    ("notification_type", "system", "سیستمی"),

    # internship_request_type
    ("internship_request_type", "internship_letter", "نامه کارآموزی"),
    ("internship_request_type", "introduction_letter", "معرفی‌نامه"),
]


def seed_constants(apps, schema_editor):
    Constant = apps.get_model("core", "Constant")
    for category, code, label in CONSTANTS:
        Constant.objects.get_or_create(
            category=category,
            code=code,
            defaults={"label": label, "is_active": True},
        )


def unseed_constants(apps, schema_editor):
    Constant = apps.get_model("core", "Constant")
    for category, code, _ in CONSTANTS:
        Constant.objects.filter(category=category, code=code).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_constants, unseed_constants),
    ]
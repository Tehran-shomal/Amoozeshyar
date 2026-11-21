"""Page ownership for Shahsavand and Omid inside one academic-services group."""

SHAHSAVAND_PAGES = {
    "evaluation": {
        "title": "ارزشیابی اساتید",
        "subtitle": "",
        "group": "ارتباط و خدمات دانشجویی",
    },
    "evaluation-form": {
        "title": "فرم تکمیل ارزشیابی استاد",
        "subtitle": "ثبت بازخورد محرمانه برای بهبود کیفیت آموزش",
        "group": "ارتباط و خدمات دانشجویی",
    },
    "messages": {
        "title": "ارتباط با اساتید",
        "subtitle": "مشاهدهٔ ساعات پاسخ‌گویی و ارسال پیام آموزشی",
        "group": "ارتباط و خدمات دانشجویی",
    },
    "guest-request": {
        "title": "درخواست مهمانی",
        "subtitle": "ثبت درخواست مهمانی و پیگیری تأیید مبدأ و مقصد",
        "group": "درخواست‌ها و مجوزها",
    },
    "graduation": {
        "title": "درخواست فارغ‌التحصیلی",
        "subtitle": "بررسی شرایط و آغاز فرایند دانش‌آموختگی",
        "group": "درخواست‌ها و مجوزها",
    },
}

OMID_PAGES = {
    "academic-activities": {
        "title": "فعالیت‌های آموزشی",
        "subtitle": "",
        "group": "وضعیت تحصیلی و مالی",
        "template": "academic_services/academic_activities.html",
    },
    "transcript": {
        "title": "کارنامه دانشجویی",
        "subtitle": "",
        "group": "وضعیت تحصیلی و مالی",
        "template": "academic_services/transcript.html",
    },
    "attendance": {
        "title": "حضور و غیاب درس‌ها",
        "subtitle": "",
        "group": "برنامه آموزشی و امتحانات",
    },
    "exam-card": {
        "title": "کارت ورود به جلسه امتحان",
        "subtitle": "برنامهٔ امتحانات، شماره صندلی و شرایط دریافت کارت",
        "group": "برنامه آموزشی و امتحانات",
        "template": "academic_services/exam_card.html",
    },
    "requests": {
        "title": "درخواست‌های دانشجویی",
        "subtitle": "",
        "group": "درخواست‌ها و مجوزها",
    },
    "education-certificate": {
        "title": "درخواست صدور مدرک آموزشی",
        "subtitle": "",
        "group": "درخواست‌ها و مجوزها",
    },
    "graduation-certificate": {
        "title": "درخواست مدرک دانش‌آموختگی",
        "subtitle": "",
        "group": "درخواست‌ها و مجوزها",
    },
    "student-card": {
        "title": "کارت دانشجویی دیجیتال",
        "subtitle": "مشخصات هویتی و وضعیت اعتبار کارت دانشجویی",
        "group": "ارتباط و خدمات دانشجویی",
        "template": "academic_services/student_card.html",
    },
    "guide": {
        "title": "راهنمای سامانه",
        "subtitle": "راهنمای انجام فرایندهای آموزشی و خدمات دانشجویی",
        "group": "ارتباط و خدمات دانشجویی",
    },
    "support": {
        "title": "مرکز پشتیبانی",
        "subtitle": "ثبت و پیگیری درخواست پشتیبانی سامانه",
        "group": "ارتباط و خدمات دانشجویی",
    },
}

# Keep each contributor's route list visible for review and team handoff.
MEMBER_PAGE_DEFINITIONS = {
    "shahsavand": SHAHSAVAND_PAGES,
    "omid": OMID_PAGES,
}
MEMBER_PAGES = {
    member: tuple(definitions)
    for member, definitions in MEMBER_PAGE_DEFINITIONS.items()
}
PAGES = {
    slug: {**definition, "member": member}
    for member, definitions in MEMBER_PAGE_DEFINITIONS.items()
    for slug, definition in definitions.items()
}

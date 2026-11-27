"""Class and term schedule pages owned by Niousha, the frontend lead."""

PAGES = {
    "attendance": {
        "title": "حضور و غیاب درس‌ها",
        "subtitle": "جلسه‌ها و وضعیت حضور ثبت‌شده در نیمسال انتخاب‌شده",
        "group": "سیستم دروس دانشجو",
        "template": "niousha/attendance.html",
    },
    "exam-card": {
        "title": "کارت ورود به جلسه امتحان",
        "subtitle": "برنامهٔ امتحان‌های ثبت‌شده؛ شمارهٔ صندلی رسمی در دسترس نیست",
        "group": "سیستم دروس دانشجو",
        "template": "niousha/exam_card.html",
    },
    "calendar": {
        "title": "تقویم آموزشی ترم",
        "subtitle": "تقویم ماهانه و رویدادهای ثبت‌شدهٔ نیمسال",
        "group": "سیستم دروس دانشجو",
        "template": "niousha/calendar.html",
    },
    "schedule": {
        "title": "برنامه هفتگی کامل",
        "subtitle": "برنامهٔ درس‌های فعال پرونده در نیمسال انتخاب‌شده",
        "group": "سیستم دروس دانشجو",
        "template": "niousha/schedule.html",
    },
}

# The shared semester picker is maintained by the frontend lead.
COMPONENTS = ("term_picker",)

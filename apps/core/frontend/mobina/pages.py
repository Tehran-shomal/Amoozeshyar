"""Page metadata owned by Mobina: account access and shared student shell."""

PAGES = {
    "settings": {
        "title": "تنظیمات زبان و اعلان‌ها",
        "subtitle": "مدیریت اطلاعات تماس، زبان و اعلان‌های حساب کاربری",
        "group": "خدمات دانشجویی",
        "template": "mobina/settings.html",
    },
    "student-card": {
        "title": "کارت دانشجویی دیجیتال",
        "subtitle": "نمایش اطلاعات پرونده؛ این پیش‌نمایش کارت رسمی نیست.",
        "group": "خدمات دانشجویی",
        "template": "mobina/student_card.html",
    },
}

# Login and dashboard are module pages outside the /portal/<slug>/ route.
SPECIAL_PAGES = {
    "login": {"template": "mobina/login.html"},
    "dashboard": {"template": "mobina/home.html"},
}

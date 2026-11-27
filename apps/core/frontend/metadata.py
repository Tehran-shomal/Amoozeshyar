"""Shared product navigation and common interface copy; not team ownership."""

NAV_GROUPS = [
    {"title": "", "items": [{"label": "داشبورد", "slug": "", "icon": "⌂", "home": True}]},
    {
        "title": "سیستم دروس دانشجو",
        "items": [
            {"label": "انتخاب واحد", "slug": "enrollment", "icon": "▣"},
            {"label": "حذف و اضافه", "slug": "add-drop", "icon": "＋"},
            {"label": "حذف اضطراری", "slug": "emergency-drop", "icon": "−"},
            {"label": "مشاهده آخرین وضعیت ثبت نام", "slug": "registration-status", "icon": "✓"},
            {"label": "ارسال درخواست اعتراض به نمره", "slug": "grade-appeal", "icon": "↗"},
            {"label": "فعالیت های آموزشی دانشجو", "slug": "academic-activities", "icon": "▦"},
            {"label": "مشاهده کارنامه دانشجو", "slug": "transcript", "icon": "▤"},
            {"label": "چارت انتخاب واحد", "slug": "curriculum", "icon": "⌘"},
            {"label": "کارآموزی", "slug": "internship", "icon": "▱"},
            {"label": "حضور و غیاب دانشجو", "slug": "attendance", "icon": "◷"},
            {"label": "تقویم آموزشی ترم", "slug": "calendar", "icon": "▦"},
            {"label": "برنامه هفتگی کامل", "slug": "schedule", "icon": "▧"},
            {"label": "کارت ورود به جلسه امتحان", "slug": "exam-card", "icon": "▣"},
        ],
    },
    {
        "title": "خدمات مالی",
        "items": [
            {"label": "مدیریت پرداخت ها", "slug": "payments", "icon": "ریال"},
            {"label": "خدمات پرداخت امن", "slug": "secure-payment", "icon": "◇"},
            {"label": "درخواست یا پیگیری تسهیلات", "slug": "financial-aid", "icon": "٪"},
            {"label": "مدیریت مالی نیمسال های تحصیلی دانشجو", "slug": "tuition", "icon": "▤"},
        ],
    },
    {
        "title": "درخواست مجوز",
        "items": [
            {"label": "ارسال و پیگیری درخواست های دانشجو", "slug": "requests", "icon": "☷"},
            {"label": "ارسال و پیگیری درخواست صدور مدرک آموزشی دانشجو", "slug": "education-certificate", "icon": "▧"},
            {"label": "ارسال و پیگیری درخواست صدور مدرک دانش آموختگی", "slug": "graduation-certificate", "icon": "✧"},
            {"label": "درخواست مهمانی", "slug": "guest-request", "icon": "⇢"},
            {"label": "درخواست فارغ التحصیلی", "slug": "graduation", "icon": "✦"},
        ],
    },
    {
        "title": "خدمات دانشجویی",
        "items": [
            {"label": "کارت دانشجویی دیجیتال", "slug": "student-card", "icon": "▰"},
            {"label": "مرکز اعلان ها", "slug": "notifications", "icon": "♢"},
            {"label": "تنظیمات زبان و اعلان ها", "slug": "settings", "icon": "⚙"},
            {"label": "راهنمای سامانه", "slug": "guide", "icon": "؟"},
            {"label": "مرکز پشتیبانی", "slug": "support", "icon": "◎"},
        ],
    },
    {
        "title": "اساتید",
        "items": [
            {"label": "ارزشیابی اساتید", "slug": "evaluation", "icon": "★"},
            {"label": "ارتباط با اساتید", "slug": "messages", "icon": "✉"},
            {"label": "اطلاعیه های اساتید", "slug": "announcements", "icon": "◉"},
        ],
    },
]

SIDEBAR_FOOTER = [
    {"label": "خروج از سامانه", "slug": "", "icon": "⇥", "action": True},
]

LOGIN_COPY = {'university': 'دانشگاه آزاد اسلامی',
 'brand_title': 'آموزشیار؛',
 'brand_slogan': 'همراه مسیر موفقیت شما',
 'brand_description': 'سامانه یکپارچه خدمات آموزشی و دانشجویی',
 'brand_version': 'نسخه مفهومی بازطراحی رابط کاربری · دانشگاه آزاد اسلامی',
 'heading': 'خوش آمدید',
 'intro': 'برای ادامه، اطلاعات حساب دانشجویی خود را وارد کنید.',
 'username_label': 'نام کاربری / شماره دانشجویی',
 'username_placeholder': 'شماره دانشجویی خود را وارد کنید',
 'password_label': 'گذرواژه',
 'password_placeholder': 'گذرواژه خود را وارد کنید',
 'remember': 'مرا به خاطر بسپار',
 'recovery': 'بازیابی گذرواژه',
 'submit': 'ورود به سامانه',
 'warning': 'این نسخه صرفاً نمونه اولیه برای طراحی است. اطلاعات واقعی ورود خود را در این صفحه آزمایشی وارد کنید.',
 'prototype': '',
 'support': 'برای ورود به سامانه پشتیبانی، اینجا کلیک کنید.'}

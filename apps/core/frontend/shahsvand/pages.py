"""Student service request pages owned by Shahsvand."""

PAGES = {
    "internship": {
        "title": "کارآموزی",
        "subtitle": "ثبت محل کارآموزی و پیگیری وضعیت ثبت‌شده",
        "group": "سیستم دروس دانشجو",
        "template": "shahsvand/internship.html",
    },
    "guest-request": {
        "title": "درخواست مهمانی",
        "subtitle": "ثبت مقصد مهمانی و پیگیری وضعیت بررسی",
        "group": "درخواست مجوز",
        "template": "shahsvand/guest_request.html",
    },
    "graduation": {
        "title": "درخواست بررسی فارغ‌التحصیلی",
        "subtitle": "ثبت درخواست؛ ثبت به معنی تأیید رسمی نیست",
        "group": "درخواست مجوز",
        "template": "shahsvand/graduation.html",
    },
    "requests": {
        "title": "درخواست‌های دانشجویی",
        "subtitle": "ثبت و پیگیری درخواست‌های موجود در سامانه",
        "group": "درخواست مجوز",
    },
    "education-certificate": {
        "title": "درخواست گواهی آموزشی",
        "subtitle": "ثبت درخواست گواهی؛ صدور رسمی به سرویس دانشگاه وابسته است",
        "group": "درخواست مجوز",
    },
    "graduation-certificate": {
        "title": "درخواست گواهی دانش‌آموختگی",
        "subtitle": "ثبت درخواست؛ صدور رسمی در این سامانه متصل نیست",
        "group": "درخواست مجوز",
        "template": "shahsvand/graduation_certificate.html",
    },
}

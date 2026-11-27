# اطلاعیه‌های اساتید — صفحهٔ ۱۶

- مالک/route: Miri؛ shell `/portal/announcements/`؛ داده و POST از `/api/portal/pages/announcements/`؛ قالب اختصاصی `miri/announcements.html` و selector در `miri/selectors.py`.
- مرجع: [PDF صفحهٔ ۱۶](page-16-reference.png). سه کارت با عنوان، نویسنده، تاریخ، متن و کنترل مرتبط دیده می‌شود؛ نوار بالا نیمسال و شمار اعلان‌های خوانده‌نشده را خلاصه می‌کند.
- منبع واقعی: فقط `Communication`های دریافتی حساب جاری با `communication_type.code=announcement`؛ نویسنده از sender و تاریخ/متن از همان رکورد است. پیام‌های رسمی/درخواستی و رکوردهای حساب‌های دیگر در فهرست نمی‌آیند.
- رفتار: GET از API عمومی صفحه؛ POST با `communication_id` فقط اطلاعیهٔ نوع announcement متعلق به receiver حساب فعلی را خوانده‌شده می‌کند، `read_at` را ثبت و اگر Constant فعال `communication_status/read` موجود باشد status را هم تنظیم می‌کند. شناسهٔ قدیمی `notification_id` برای سازگاری ورودی پذیرفته می‌شود.
- مرز داده: Communication به درس/ترم FK ندارد؛ نیمسال انتخاب‌شده صرفاً context صفحه است، نه فیلتر اطلاعیه. دکمهٔ «بخش مرتبط» نیز در مدل link ندارد، بنابراین عمل در دسترس «خواندم» است و مسیر ساختگی نشان داده نمی‌شود.
- مجوز/خطا: session اجباری؛ cross-account یا نوع غیر announcement با 404 رد می‌شود؛ API از CSRF معمول POST استفاده می‌کند.
- شواهد: مرجع در `page-16-reference.png` ذخیره شد. GET ناشناس API در پورت ۸۰۰۱ با `401 application/json` برگشت؛ درخواست مجاز و capture جاری این نوبت هنوز انجام نشده، پس تطبیق بصری کامل تأیید نشده است.
- آزمون: `test_announcements_use_owned_announcement_communications_and_mark_read` اضافه شد؛ به درخواست کاربر اجرا نشده است.

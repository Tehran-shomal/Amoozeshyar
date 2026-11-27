# تقویم آموزشی ترم — صفحهٔ ۱۵

- مالک/route: Niousha؛ shell مسیر `/portal/calendar/` و داده از `GET /api/portal/pages/calendar/`؛ قالب اختصاصی `apps/core/frontend/niousha/templates/niousha/calendar.html` و selector در `niousha/selectors.py`.
- مرجع: [PDF صفحهٔ ۱۵](page-15-reference.png). چیدمان مرجع سه کارت خلاصه، تقویم ماهانهٔ شنبه‌محور، فهرست رویدادهای ماه و خلاصهٔ بازه‌های نیمسال دارد.
- پیاده‌سازی: grid واقعی ماه هجری شمسی، نشانگر روز جاری/دارای رویداد، رویدادهای ماه و پنل خلاصه؛ تاریخ‌ها از میلادی ذخیره‌شده به هجری شمسی تبدیل می‌شوند. CSS واکنش‌گرا در `static/core/portal.css` است.
- داده/API فقط‌خواندنی: تاریخ‌های شروع/پایان Term و پنجره‌های انتخاب واحد/حذف‌و‌اضافه/حذف اضطراری؛ امتحان‌های CourseOffering و جلسات Attendance فقط برای Enrollmentهای فعال همان دانشجو و نیمسال. API صفحهٔ مشترک، مالکیت Student جاری را در view حفظ می‌کند.
- مرز داده: مدل CalendarEvent، مناسبت عمومی و deadline شهریه در checkout نیست؛ رویداد نمونه از PDF ساخته نمی‌شود. تاریخ‌های فعلی clone برای term فعال `14051` در سال میلادی ۲۰۷۶ هستند و با دادهٔ نمونهٔ ۱۴۰۵ PDF تطبیق ندارند؛ تاریخ/رکورد DB تغییر نکرد.
- نوشتن/اعتبارسنجی: صفحه read-only است. term انتخاب‌نشده notice می‌دهد؛ بدون پرونده هم notice عمومی پروفایل نشان داده می‌شود.
- آزمون/وابستگی: regression `test_calendar_page_renders_month_grid_and_real_term_events` به `apps/core/test_frontend.py` افزوده شده؛ به درخواست کاربر اجرا نشده است. آزمون تبدیل تاریخ و suite در فاز بعد.
- شواهد: مرجع در `page-15-reference.png` ذخیره شده. GET ناشناس API در پورت ۸۰۰۱ با `401 application/json` برگشت؛ درخواست احرازشده و capture جاری برای این نوبت در دسترس نبود و هنوز ادعای تطبیق بصری کامل نمی‌شود.

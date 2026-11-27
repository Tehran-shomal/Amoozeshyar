# بازطراحی کامل صفحه‌ها و مالکیت هفت‌گانهٔ آموزشیار

## وضعیت و منابع معتبر

- این سند جایگزین تقسیم‌بندی پنج‌گانهٔ قبلی در کد فعال است؛ `MASTER EXECUTION PROMPT — AMOOZESHYAR` و بخش «NEW TEAM OWNERSHIP» آن مرجع مالکیت صفحه‌هاست.
- پیاده‌سازی در شاخهٔ ایزولهٔ `codex/full-system-audit` انجام می‌شود. دیتابیس اصلی، شاخهٔ `main` و checkout اصلی خارج از محدوده‌اند.
- فایل PDF مرجع در clone فعلی پیدا نشده است. تا زمانی که خود فایل در دسترس نباشد، شماره‌های صفحه و ظاهر PDF فقط مطابق اطلاعات ثبت‌شدهٔ پرامپت/مستندات قبلی هستند و تطبیق بصری تأییدشده محسوب نمی‌شوند.
- کاربر اجرای تست‌ها را به فاز بعد موکول کرده است؛ این فاز توسعه و مستندسازی است و نتیجهٔ تستی ادعا نمی‌کند.

## هدف

همهٔ مسیرهای فعلی پرتال، حالت‌های پنهان/گفت‌وگویی و عملیات قابل پشتیبانی را یکی‌یکی به مالک درست، صفحهٔ قابل استفاده و API/دادهٔ واقعی متصل کنیم؛ رفتار ناموجود یا متکی به سرویس بیرونی را صریحاً unavailable/unknown نگه داریم و موفقیت جعلی نسازیم.

## هفت مالک جدید

| مالک | محدوده | routeها و حالت‌های مرتبط |
|---|---|---|
| Mobina | ورود، داشبورد، چارچوب مشترک، تنظیمات حساب و کارت دیجیتال | `/login/`, `/`, `/portal/settings/`, `/portal/student-card/`؛ sidebar/header و shell مشترک |
| Shaghayegh | ثبت‌نام و تغییر دروس | `/portal/enrollment/`, `/portal/selected-courses/`, `/portal/add-drop/`, `/portal/emergency-drop/`, `/portal/registration-status/`؛ انتخاب گروه و تأییدهای ثبت/حذف |
| Parsa | امور مالی | `/portal/payments/`, `/portal/secure-payment/`, `/portal/financial-aid/`, `/portal/tuition/` |
| Omid | سوابق و پیشرفت آموزشی | `/portal/academic-activities/`, `/portal/transcript/`, `/portal/curriculum/`, `/portal/grade-appeal/` |
| Niousha | برنامه و کلاس‌ها، Frontend Lead | `/portal/schedule/`, `/portal/calendar/`, `/portal/attendance/`, `/portal/exam-card/`؛ مالک مؤلفهٔ مشترک انتخاب نیمسال |
| Shahsvand | درخواست‌های دانشجویی | `/portal/internship/`, `/portal/guest-request/`, `/portal/graduation/`, `/portal/requests/`, `/portal/education-certificate/`, `/portal/graduation-certificate/` |
| Miri | ارتباط با استاد و خدمات عمومی، Shared Lead | `/portal/evaluation/`, `/portal/evaluation-form/`, `/portal/messages/`, `/portal/announcements/`, `/portal/notifications/`, `/portal/guide/`, `/portal/support/` |

مالکیت تیمی از دسته‌بندی کاربردی منوی کناری مستقل است و `NAV_GROUPS` نباید به‌عنوان گروه مالکیت استفاده شود. خود منوی محصول باید با مرجع PDF تطبیق داشته باشد: «سیستم دروس دانشجو» (۱۳ مقصد)، «خدمات مالی» (۴)، «درخواست مجوز» (۵)، «خدمات دانشجویی» (۵) و «اساتید» (۳). ترتیب و عنوان مقصدها از برش‌های PDF صفحات ۴ تا ۸ گرفته می‌شود؛ URL و مالک backend با تغییر دسته‌بندی عوض نمی‌شوند.

## معماری و قراردادها

- Django monolith و endpointهای موجود حفظ می‌شوند؛ هر route از `GET/POST /api/portal/pages/<slug>/` با session و CSRF استفاده می‌کند. endpointهای دامنه‌ای ثبت‌نام، زمان‌بندی و حساب نیز بدون تغییر قرارداد باقی می‌مانند.
- `registry.py` تنها منبع تجمیع manifestهای هفت مالک است و در startup مالک تکراری، route جامانده یا route اضافه را رد می‌کند.
- هر مالک پوشهٔ مجزای `pages.py`, `selectors.py`, `forms.py`, `README.md` و asset/template مخصوص خودش دارد. ابزارهای بدون مالک در `frontend/common.py` یا قالب مشترک باقی می‌مانند.
- مدل‌ها و admin متمرکز می‌مانند؛ جابه‌جایی پوشهٔ مالکیت نباید schema یا داده را تغییر دهد.
- هر screen باید منبع داده، read API، write API یا دلیل نبود آن، validation، ownership/permission، خطا، حالت خالی/بارگذاری و URL را در ماتریس ثبت کند.
- برای پرداخت واقعی، صدور رسمی کارت/گواهی، اعلان خارجی، یا هر سرویس فاقد provider قرارداد معتبر ساخته نمی‌شود و موفقیت شبیه‌سازی نمی‌شود.
- صفحه‌های فاقد قانون تجاری مستند با مقدارها/قواعد ساختگی پر نمی‌شوند؛ وضعیت تصمیم در `BUSINESS_RULES.md` می‌ماند.

## معیار تکمیل صفحه

صفحه فقط وقتی complete است که مسیر و مالک درست، UI متصل به API، دادهٔ متعلق به دانشجوی جاری، عملیات/فرم معتبر یا دلیل روشنِ read-only، خطا و موفقیت قابل فهم، refresh داده پس از mutation، دسترس‌پذیری/RTL/responsive، و شواهد آزمون در فاز بعد موجود باشد. تا اجرای فاز تست، هیچ صفحه‌ای صرفاً با تغییر مالک یا افزودن مستند کامل اعلام نمی‌شود.

## مستندات خروجی

- `docs/TEAM_OWNERSHIP.md`: مرجع مالکیت و فهرست URLهای هر عضو.
- `docs/SCREEN_API_MATRIX.md` و `docs/API_CONTRACTS.md`: اتصال صفحه به داده، endpoint و قرارداد.
- `docs/screens/<slug>.md`: جزئیات هر route و حالت.
- `docs/presentation/01_Mobina.md` تا `07_Miri.md` و `MASTER_PRESENTATION.md`: ارائهٔ جداگانه با URL و فایل‌های مرتبط.
- `docs/PROGRESS.md`, `docs/NEXT_STEPS.md`, `docs/FINAL_REPORT.md`: وضعیت واقعی، ناتمام‌ها، مسیر اسناد و آزمون‌های موکول‌شده.

## موارد خارج از دامنهٔ این فاز

- اجرای suite تست یا مرورگر و تأیید نهایی؛ بنا به درخواست کاربر فاز بعد است.
- افزودن provider پرداخت/پیامک/ایمیل/صدور رسمی بدون credential و قرارداد حقیقی.
- بازسازی دقیق pixel-by-pixel صفحات PDF تا وقتی PDF در workspace موجود نیست.

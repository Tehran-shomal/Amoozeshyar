# کارآموزی

- مالک/route: Shahsvand؛ `/portal/internship/`; قالب اختصاصی `shahsvand/internship.html` در shell مشترک؛ `shahsvand.forms.InternshipForm`.
- مرجع: PDF صفحهٔ ۲۴ و نتیجهٔ ثبت در صفحهٔ ۳۸.
- هدف/کنترل: ثبت نوع درخواست، نام شرکت/سازمان، تاریخ شروع و مدت به ساعت؛ نمایش وضعیت درخواست‌های همان پرونده.
- داده/API: `GET|POST /api/portal/pages/internship/`؛ Internship، Student و Constant. مالک Student و status اولیهٔ pending از سرور؛ بعد از POST موفق، redirect دارای `request_id` نتیجهٔ رکورد ساخته‌شده را فقط در scope همان Student می‌خواند؛ review route `POST /api/requests/internship/<id>/review/`.
- اعتبارسنجی/مجوز: student/status pending از سرور؛ `request_type` اجباری و فقط از lookup فعال؛ duration_hours > 0؛ reviewer role در service برابر `student_affairs_officer` یا `admin` است.
- خطا/محدودیت: صفحه اکنون فرم دوستونه و تاریخچهٔ scoped دارد. نتیجهٔ صفحهٔ ۳۸ فقط ذخیرهٔ داخلی و status واقعی رکورد را گزارش می‌کند؛ ارسال به سامانهٔ دانشگاه/تأیید رسمی انجام نمی‌شود. مطابق schema فعلی، استاد ناظر، تلفن/نشانی محل، نام فعالیت و بارگذاری نامهٔ پذیرش در مدل `Internship` فیلد ندارند و در UI به‌عنوان قابلیت ثبت‌شده نمایش داده نمی‌شوند؛ lifecycle گزارش/تأیید نهایی نیز فقط بخشی از review موجود است.
- navigation: منوی برنامه آموزشی؛ رکوردهای خود student.
- آزمون/وابستگی: regressionهای `test_internship_page_uses_owned_form_and_scoped_request_history` و `test_internship_submission_shows_only_the_owned_persisted_result` در `apps/core/test_frontend.py` نوشته شده‌اند و اجرا نشده‌اند؛ تست‌های service در `apps/core/requests/test_services.py` وابستگی‌اند.
- وضعیت: مرجع PDF در `docs/screens/page-24-reference.png` بررسی و template صفحه اصلاح شد؛ capture جاری احرازشده نداریم، پس تطبیق بصری runtime تأیید نشده و توالی تصویری طبق plan روی صفحهٔ ۱۹ متوقف است.

# درخواست مهمانی

- مالک/route: Shahsvand؛ `/portal/guest-request/`; قالب اختصاصی `shahsvand/guest_request.html` در shell مشترک؛ `GuestRequestForm`.
- مرجع: PDF صفحهٔ ۲۵ و نتیجهٔ ثبت در صفحهٔ ۳۹.
- هدف/کنترل: ثبت دانشگاه مقصد و نمایش شناسه، مقصد، تاریخ ثبت و وضعیت درخواست‌های همان پرونده.
- داده/API: `GET|POST /api/portal/pages/guest-request/`; TransferRequest, Student, Constant. POST موفق با `request_id` redirect می‌کند و GET نتیجه را فقط از میان درخواست‌های متعلق به Student جاری می‌خواند.
- اعتبارسنجی/مجوز: owner `student` و وضعیت اولیه `review_status/pending` سمت سرور؛ فقط `destination_university` از client پذیرفته می‌شود.
- خطا/نامعلوم: فرم نامعتبر 400؛ مدل فقط مقصد، نتیجهٔ تطبیق دروس، وضعیت بررسی، تاریخ و دانشجو را ذخیره می‌کند. نتیجهٔ صفحهٔ ۳۹ فقط ثبت محلی را گزارش می‌کند؛ تأیید نهایی وابسته به review است و ارسال خودکار به دانشگاه مقصد وجود ندارد. مبدأ، نوع مهمانی، تماس، دلیل و مدارک PDF فیلد schema ندارند. مرحله‌های مجزای timeline، لغو/ویرایش و lifecycle رسمی از این داده‌ها قابل استنتاج نیستند و ساخته نشدند.
- navigation: منوی درخواست‌ها؛ بررسی بعدی از request-review API و نقش education_officer/admin طبق code، نه تأیید سیاست محصول.
- آزمون/وابستگی: regressionهای `test_guest_request_page_shows_real_destination_and_owned_status` و `test_guest_request_submission_shows_only_the_owned_persisted_result` در `apps/core/test_frontend.py` اضافه شده‌اند و اجرا نشده‌اند؛ `apps/core/requests/test_services.py`, `GuestRequestForm`, TransferRequest.
- وضعیت: مرجع PDF در `docs/screens/page-25-reference.png` بررسی و قالب فرم/تاریخچهٔ scoped اصلاح شد؛ capture جاری احرازشده نداریم، پس تطبیق runtime تأیید نشده و توالی تصویری طبق plan روی صفحهٔ ۱۹ متوقف است.

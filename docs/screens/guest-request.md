# درخواست مهمانی

- مالک/route: Shahsavand؛ `/portal/guest-request/`; shared `core/live_content.html`; `GuestRequestForm`.
- مرجع: PDF صفحهٔ ۲۵.
- هدف/کنترل: ثبت مقصد دانشگاه و نمایش درخواست‌های قبلی با تاریخ/وضعیت.
- داده/API: TransferRequest, Student, Constant؛ GET/POST API صفحه.
- اعتبارسنجی/مجوز: owner `student` و وضعیت اولیه `review_status/pending` سمت سرور؛ فقط `destination_university` از client پذیرفته می‌شود.
- خطا/نامعلوم: فرم نامعتبر 400؛ نقش مبدأ/مقصد، مدارک، لغو/ویرایش و lifecycle رسمی در source شرح نشده.
- navigation: منوی درخواست‌ها؛ بررسی بعدی از request-review API و نقش education_officer/admin طبق code، نه تأیید سیاست محصول.
- آزمون/وابستگی: `apps/core/test_frontend.py`, `apps/core/requests/test_services.py`; `GuestRequestForm`, TransferRequest.
- وضعیت: ثبت/پیگیری مدل موجود؛ گردش کامل مهمانی ثابت نشده؛ visual تازه باز.

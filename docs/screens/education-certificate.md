# درخواست مدرک آموزشی

- مالک/route: Omid؛ `/portal/education-certificate/`; shared `core/live_content.html`; `CertificateForm`.
- مرجع: PDF صفحهٔ ۷۲.
- هدف/کنترل: ارسال و پیگیری درخواست از مسیر StudentServiceRequest.
- داده/API: StudentServiceRequest و Constant فعال `service_request_type/certificate`; GET/POST API صفحه.
- اعتبارسنجی/مجوز: owner/status سروری؛ فقط نوع certificate و شرح موجود؛ `certificate` choice را از client arbitrary قبول نمی‌کند.
- خطا/محدودیت: فایل/قالب/امضای مدرک یا صدور PDF رسمی وجود ندارد؛ submit را نباید صدور موفق تعبیر کرد.
- navigation: گروه درخواست/مجوز؛ وضعیت تصمیم در جدول درخواست.
- آزمون/وابستگی: `apps/core/test_frontend.py`; CertificateForm و ServiceRequestForm.
- وضعیت: درخواست DB-backed؛ صدور/تحویل رسمی خارج از scope provider فعلی؛ screenshot تازه باز.

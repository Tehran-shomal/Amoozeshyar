# درخواست مدرک دانش‌آموختگی

- مالک/route: Omid؛ `/portal/graduation-certificate/`; shared `core/live_content.html`; `CertificateForm` مشترک.
- مرجع: PDF صفحهٔ ۷۳.
- هدف/کنترل: ثبت/پیگیری همان نوع certificate موجود.
- داده/API: StudentServiceRequest/Constant؛ GET و POST API صفحه؛ selector داده را به `service_request_kind.code="certificate"` فیلتر می‌کند.
- اعتبارسنجی/مجوز: student و pending status از backend؛ model فعلی تفکیک معنایی این route از education-certificate را نگه نمی‌دارد.
- خطا/محدودیت: صدور رسمی/فایل/امضای گواهی پیاده نشده؛ صفحه success issuance ادعا نمی‌کند.
- navigation: گروه درخواست‌ها؛ back به routeهای پرتال.
- آزمون/وابستگی: `apps/core/test_frontend.py`; Academic Services selector/forms.
- وضعیت: فرم پایه موجود؛ تفکیک lifecycle و سند رسمی نامعلوم؛ screenshot تازه باز.

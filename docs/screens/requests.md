# درخواست‌های دانشجویی

- مالک/route: Omid؛ `/portal/requests/`; shared `core/live_content.html`; `ServiceRequestForm`.
- مرجع: PDF صفحهٔ ۶۷.
- هدف/کنترل: ثبت نوع درخواست/توضیح و فهرست درخواست‌های خود دانشجو.
- داده/API: StudentServiceRequest و Constant؛ GET/POST API صفحه.
- اعتبارسنجی/مجوز: `service_requester` و `service_decision_state=pending` سمت سرور؛ فقط فیلدهای تعریف‌شدهٔ مدل؛ lookupهای موجود لازم‌اند.
- خطا/محدودیت: خطای فرم 400؛ هیچ پیوست، مبلغ یا workflow واحد برای همهٔ انواع در مدل وجود ندارد.
- navigation: گروه درخواست‌ها؛ staff review API فقط برای typeهای صریحاً پشتیبانی‌شده.
- آزمون/وابستگی: `apps/core/test_frontend.py`, `apps/core/requests/test_services.py`; ServiceRequestForm/selector.
- وضعیت: submit و read از مدل حاضر؛ معادل همهٔ فرم‌های مستقل PDF نیست؛ screenshot تازه باز.

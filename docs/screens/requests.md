# درخواست‌های دانشجویی

- مالک/route: Shahsvand؛ `/portal/requests/`; shared `core/live_content.html`; `shahsvand.forms.ServiceRequestForm`.
- مرجع: PDF صفحهٔ ۶۷ و نتیجهٔ ثبت در صفحهٔ ۴۴.
- هدف/کنترل: ثبت نوع درخواست/توضیح و فهرست درخواست‌های خود دانشجو؛ نبود پشتیبانی تماس/پیوست و ثبت محلی جلوی فرم اعلام می‌شود.
- داده/API: StudentServiceRequest و Constant؛ GET/POST API صفحه. پس از POST موفق، `request_id` به route بازمی‌گردد و نتیجه فقط رکورد متعلق به Student انتخابی را می‌خواند.
- اعتبارسنجی/مجوز: `service_request_kind` اجباری و از lookup فعال `service_request_type`؛ `service_requester` و `service_decision_state=pending` سمت سرور؛ فقط فیلدهای تعریف‌شدهٔ مدل.
- خطا/محدودیت: خطای فرم 400؛ نتیجهٔ صفحهٔ ۴۴ ثبت محلی و status واقعی را تأیید می‌کند اما ارسال به سامانهٔ دانشگاهی را ادعا نمی‌کند. مدل timestamp و phone ندارد؛ هیچ پیوست، مبلغ یا workflow واحد برای همهٔ انواع در مدل وجود ندارد.
- navigation: گروه درخواست‌ها؛ staff review API فقط برای typeهای صریحاً پشتیبانی‌شده.
- آزمون/وابستگی: رگرسیون اجباری‌بودن نوع در `apps/core/test_frontend.py` اضافه شد؛ اجرا برای فاز تست بعدی. همچنین `apps/core/requests/test_services.py`; ServiceRequestForm/selector.
- وضعیت: PDF صفحهٔ ۶۷ با type/data واقعی تطبیق شد؛ تماس/پیوست و ارسال بیرونی پشتیبانی نمی‌شوند و صریحاً گفته می‌شود. assertion جدید نوشته شد ولی اجرا نشده؛ capture جاری احرازشده نداریم.

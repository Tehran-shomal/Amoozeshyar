# درخواست بررسی فارغ‌التحصیلی

- مالک/route: Shahsavand؛ `/portal/graduation/`; shared `core/live_content.html`; `GraduationReviewForm`.
- مرجع: PDF صفحهٔ ۲۶.
- هدف/کنترل: نمایش GraduationAudit و ثبت درخواست بررسی شرایط.
- داده/API: GraduationAudit و StudentServiceRequest؛ GET/POST API صفحه؛ نوع درخواست به Constant فعال با code=`certificate` محدود است.
- اعتبارسنجی/مجوز: service_requester و pending status سمت سرور؛ متن با پیشوند «درخواست بررسی فارغ‌التحصیلی»؛ ورودی متن تکمیلی.
- خطا/محدودیت: ثبت به معنی تأیید فارغ‌التحصیلی نیست؛ ارزیابی رسمی/محاسبهٔ کمبود واحد یا صدور سند بیرونی صورت نمی‌گیرد.
- navigation: منوی درخواست‌ها؛ نتیجه در جدول GraduationAudit جدا از خود submission است.
- آزمون/وابستگی: `apps/core/test_frontend.py`, `apps/core/requests/test_services.py`; selector/form و مدل‌های مذکور.
- وضعیت: request persistence موجود؛ lifecycle/audit رسمی و screenshot تازه باز.

# چارت انتخاب واحد

- مالک/route: Mobina؛ `/portal/curriculum/`; shared template `core/live_content.html`; `mobina.selectors.build`.
- مرجع: PDF صفحهٔ ۲۳.
- هدف/کنترل: فهرست دروس چارت رشته با نوع الزام، ترم پیشنهادی و واحد.
- داده/API: Curriculum فیلترشده با `student.field` و `is_active`; Lesson و Constant؛ GET API صفحه.
- نوشتن/اعتبارسنجی: form یا mutation ندارد؛ دادهٔ جدید از جدول ساخته نمی‌شود.
- دسترسی/خطا: session؛ داده از field پروندهٔ متعلق؛ بدون پرونده پیام انتخاب profile؛ DB unavailable 503.
- navigation: گروه ثبت‌نام؛ لینک‌ها از sidebar مشترک.
- آزمون/وابستگی: `apps/core/test_frontend.py`; Mobina selector، Curriculum/Constant lookupها.
- وضعیت: فهرست DB-backed و render smoke حاضر؛ آزمون اختصاصی rule چارت یا همهٔ حالت‌های PDF و viewport تازه وجود ندارد.

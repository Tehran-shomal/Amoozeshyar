# حضور و غیاب درس‌ها

- مالک/route: Omid؛ `/portal/attendance/`; shared `core/live_content.html`; Omid selector.
- مرجع: PDF صفحهٔ ۱۴.
- هدف/کنترل: جدول درس، شماره/تاریخ جلسه، status و توضیحات.
- داده/API: Attendance به Enrollment/CourseOffering/Lesson/Constant؛ GET API صفحه.
- نوشتن/اعتبارسنجی: صفحهٔ دانشجو فقط read-only است؛ endpoint کارمندی برای ثبت حضور در namespace attendance mount نشده.
- مجوز/خطا: session و دادهٔ پروندهٔ جاری/term؛ foreign profile ممنوع؛ DB failure مشترک.
- navigation: منوی برنامه/امتحانات؛ term-picker.
- آزمون/وابستگی: `apps/core/test_frontend.py`; attendance selector؛ route namespace مستقل خالی.
- وضعیت: نمایش جدول موجود؛ ثبت حضور/اصلاح و مجوز staff غایب؛ اندازهٔ ردیف‌ها در PDF قبلاً متفاوت ثبت شده؛ screenshot تازه باز.

# کارنامه دانشجویی

- مالک/route: Omid؛ `/portal/transcript/`; `academic_services/transcript.html`; Omid selector.
- مرجع: PDF صفحهٔ ۶۲.
- هدف/کنترل: معدل کل/واحد گذرانده/وضعیت و gradeهای درس‌های term جاری مرتب‌شده با کد درس.
- داده/API: Student, Grade, Enrollment, CourseOffering, Lesson؛ GET API صفحه؛ write ندارد.
- اعتبارسنجی/مجوز: فقط دانشجوی جاری؛ term از query/active Term؛ نمره‌ای که DB ندارد ساخته نمی‌شود.
- خطا/empty: profile/term و DB error طبق قرارداد مشترک؛ نبود grade خالی نمایش داده می‌شود.
- navigation: activity dashboard/links؛ چاپ در PDF مستقل برای این route مستند نشده.
- آزمون/وابستگی: `apps/core/test_frontend.py`; selector تخصصی و Transcript template.
- وضعیت: خواندن DB-backed؛ رندر smoke، نه تست گستردهٔ grading lifecycle؛ screenshot تازه باز.

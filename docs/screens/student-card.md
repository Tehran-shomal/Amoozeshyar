# کارت دانشجویی دیجیتال

- مالک/route: Omid؛ `/portal/student-card/`; `academic_services/student_card.html`; Omid selector.
- مرجع: PDF صفحهٔ ۲۰.
- هدف/کنترل: نمایش و چاپ مشخصات واقعی پرونده در قالب کارت.
- داده/API: Person, Student, Field, Term؛ GET API صفحه؛ `printable=true` و چاپ مرورگر.
- اعتبارسنجی/مجوز: session و پروندهٔ متعلق؛ profile انتخابی؛ فیلد missing به‌عنوان missing می‌ماند.
- محدودیت/خطا: serial number، تاریخ اعتبار، QR یا credential رسمی در DB/service نیست و ساخته نمی‌شود.
- navigation: گروه خدمات دانشجویی؛ بازگشت به portal shell.
- آزمون/وابستگی: `apps/core/test_frontend.py` render test; `student_card.html`, selector.
- وضعیت: قالب مخصوص واقعی-data و print UI موجود؛ صدور کارت رسمی و screenshot تازه پس از تغییرها باز.

# کارآموزی

- مالک/route: Niousha/Pouya؛ `/portal/internship/`; shared `core/live_content.html`; `InternshipForm`.
- مرجع: PDF صفحهٔ ۲۴.
- هدف/کنترل: ثبت company، start date، duration، request type و نمایش رکوردهای student.
- داده/API: Internship, Student, Constant, UserAccount؛ GET/POST API صفحه؛ review route `POST /api/requests/internship/<id>/review/`.
- اعتبارسنجی/مجوز: student/status pending از سرور؛ duration_hours > 0؛ reviewer role در service برابر `student_affairs_officer` یا `admin` است.
- خطا/محدودیت: contact, mentor, document upload, report lifecycle در form فعلی نیست؛ review role need product validation.
- navigation: منوی برنامه آموزشی؛ رکوردهای خود student.
- آزمون/وابستگی: `apps/core/test_frontend.py`, `apps/core/requests/test_services.py`; InternshipForm/selector.
- وضعیت: ثبت و review generic از مدل موجود؛ workflow کامل کارآموزی ثابت نشده؛ screenshot viewport جدید باز.

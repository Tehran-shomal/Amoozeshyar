# دروس انتخاب‌شده

- مالک/route: Mobina؛ `/portal/selected-courses/`; template `mobina/selected_courses.html`; selector و `mobina/static/mobina/section.js`.
- مرجع: PDF صفحات ۹–۱۳، ۷۹–۸۸ و stateهای انتخاب گروه؛ صفحات ۱۰–۱۳ چندحالت داده‌ای را نشان می‌دهند که seed/fixture مستقل ندارند.
- هدف/کنترل: جدول enrollmentهای فعال، مجموع و سقف واحد، offerings موجود و action انتخاب/حذف.
- داده/API: Student, Enrollment, CourseOffering, Lesson, Teacher, Term؛ GET API صفحه + `GET /api/scheduling/offerings/?term=...`.
- نوشتن: ثبت با ID قطعی offering از `POST /api/enrollment/register/<id>/`; حذف جدول با `POST /api/enrollment/drop/<id>/`.
- اعتبارسنجی/مجوز: `student_code` فقط پروندهٔ خود؛ role student؛ همهٔ شروط آموزشی در backend؛ match مبهم گروه درس در client ثبت نمی‌شود.
- خطا: capacity/window/debt/prerequisite/schedule/credit و profile errors پیام‌دارند؛ empty offerings یک state صریح است.
- navigation: قبل از ثبت اطلاعات مرحلهٔ اول؛ افزودن درس با ثبت واقعی؛ جزئیات گروه/modal مطابق PDF کاملاً مستقل نیست.
- آزمون/وابستگی: `apps/core/enrollment/test_services.py`, `apps/core/test_frontend.py`, `static/core/tests/portal_api.test.cjs`, `static/core/tests/portal_bindings.test.cjs`.
- وضعیت: mutation DB-backed؛ modalهای درس/گروه و result states کامل نیستند؛ visual هفت viewport باز است.

# حذف و اضافه

- مالک/route: Shaghayegh؛ `/portal/add-drop/`; `shaghayegh/course_changes.html`, `shaghayegh.selectors.build`, `shaghayegh/static/shaghayegh/section.js`.
- مرجع: PDF صفحهٔ ۵۳، حالت‌های داده صفحات ۶۸–۷۱، انتخاب درس ۷۹–۸۸ و تأیید حذف عادی ۸۹–۹۲.
- هدف/کنترل: مشخصات پرونده/ترم، جدول enrollmentهای فعال و حذف با مودال؛ افزودن از لینک انتخاب واحد.
- داده/API: Student, Enrollment, CourseOffering, Lesson, Term؛ GET page + offerings scheduling؛ حذف با `POST /api/enrollment/drop/<id>/`; افزودن از صفحهٔ انتخاب درس.
- اعتبارسنجی/مجوز: session/student؛ مالکیت شناسه در backend؛ بازهٔ add/drop یا emergency؛ حذف غیرقابل تکرار امن.
- خطا/نتیجه: خطاهای مالکیت/بازه/DB با status؛ PDF success resultهای ۵۶–۵۹/۶۸–۷۱ route جدا ندارند.
- navigation: به enrollment برای افزودن؛ پس از موفقیت reload دادهٔ جاری.
- آزمون/وابستگی: `apps/core/enrollment/test_services.py`, `apps/core/test_frontend.py`, `static/core/tests/portal_bindings.test.cjs`.
- وضعیت: حذف واقعی؛ state تأیید موجود؛ result صفحه‌های مجزا و مجموعه‌داده‌های متنوع PDF باز؛ viewport تازه باز.

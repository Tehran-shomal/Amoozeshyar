# جزئیات گروه درس در مودال (PDF reference state)

- مرجع: PDF صفحات ۸۰–۸۳ و ۸۵–۸۸؛ stateهای جزئیات/گروه برای چند درس.
- صفحهٔ مرتبط/مالک: Mobina؛ `/portal/selected-courses/`.
- رفتار موجود: offerings API ساختار `CourseOffering` را می‌خواند، اما UI جاری مشخصات/گروه‌های درس را در dialog چندمرحله‌ای PDF نشان نمی‌دهد.
- ورودی/model: lesson code/title/teacher/day/time و offering id؛ انتخاب فقط زمانی ثبت می‌شود که client match یکتا پیدا کند.
- API/validation: `GET /api/scheduling/offerings/`; `POST /api/enrollment/register/<offering_id>/`; تمام eligibility checks در service.
- خطا/مجوز: match صفر/چندگانه به عدم ثبت می‌انجامد؛ session + role student + student ownership.
- آزمون: enrollment service و `static/core/tests/portal_bindings.test.cjs`; dialog state test ندارد.
- وضعیت: گروه/جزئیات مودال PDF بازنمایی‌نشده؛ data schema موجود به معنی UI کامل نیست.

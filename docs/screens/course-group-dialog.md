# جزئیات گروه درس در مودال (PDF reference state)

- مرجع: PDF صفحات ۸۰–۸۳ و ۸۵–۸۸؛ stateهای جزئیات/گروه برای چند درس.
- صفحهٔ مرتبط/مالک: Shaghayegh؛ `/portal/selected-courses/`.
- رفتار جاری: انتخاب درس از مودال فهرست، صفحهٔ جزئیات را با تمام `CourseOffering`های همان lesson code/title باز می‌کند. صفحات ۸۰–۸۳ و ۸۵–۸۸ stateهای انتخاب متفاوت‌اند؛ وضعیت انتخاب اولیه صرفاً انتخاب UI است و تا فشردن «افزودن درس» داده‌ای نمی‌نویسد.
- ورودی/model: کد/عنوان/واحد، استاد، روز، ساعت، ظرفیت باقی‌مانده، زمان امتحان و offering ID از API واقعی؛ زمان امتحان برای هر ارائه جداگانه است. فیلد group number در مدل نیست؛ شناسهٔ رسمی گروه جعل نمی‌شود.
- شهریه: `CourseOffering` تعرفه ندارد؛ مبلغ نمونهٔ PDF نمایش داده/محاسبه نمی‌شود و توضیح نبود تعرفه نشان داده می‌شود.
- API/validation: GET `/api/scheduling/offerings/`; POST `/api/enrollment/register/<offering_id>/`; ظرفیت، بدهی، بازه، مالکیت و قواعد موجود فقط در service/server اعتبارسنجی می‌شوند.
- آزمون: رگرسیون قالب و اتصال انتخاب به API در `apps/core/test_frontend.py` و `static/core/tests/portal_bindings.test.cjs` نوشته شده؛ اجرا نشده. Browser state و runtime capture نداریم.
- وضعیت: جزئیات API-driven پیاده شده؛ تطبیق دقیق screenshot و stateهای داده‌ای PDF-specific pending است.

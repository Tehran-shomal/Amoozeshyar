# داشبورد

- مالک/مسیر: Mobina؛ `GET /`; داده `GET /api/portal/pages/home/`; template `mobina/home.html`.
- مرجع: PDF صفحهٔ ۲.
- هدف/کنترل‌ها: خلاصهٔ پرونده و نیمسال، کلاس‌های فعال، اعلان‌های اخیر، وضعیت تحصیلی/مالی و quick actions.
- ورودی: query اختیاری `student_code` و `term`; کنترل انتخاب پرونده/نیمسال در پوستهٔ مشترک.
- داده: Student/Field/Enrollment/CourseOffering/Notification/Payment/Term؛ فقط student انتخاب‌شدهٔ متعلق به حساب و پنج اعلان اخیر حساب جاری.
- API: GET صفحه؛ dashboard خودش POST ندارد. لینک‌ها به routeهای متناظر می‌روند.
- اعتبارسنجی/مجوز: session اجباری؛ profile دیگران 403؛ بدون پرونده پیام انتخاب/نبود پرونده؛ مبلغ و پرداخت از DB واقعی.
- خطا: 401 session، 403 profile، 404 term، 503 DB؛ اعلان خالی/دادهٔ خالی state عادی است.
- مسیر: quick action به enrollment، transcript، tuition و requests؛ جست‌وجوی sidebar از پوسته.
- آزمون/وابستگی: `apps/core/test_frontend.py`; Mobina dashboard selector، common portal shell/API.
- وضعیت: دادهٔ DB-backed و render smoke دارد؛ screenshot فعلی در viewportهای هدف ثبت نشده، پس تطبیق نهایی بصری باز است.

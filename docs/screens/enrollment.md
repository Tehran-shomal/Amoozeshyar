# انتخاب واحد — مرحلهٔ اول

- مالک/route: Mobina؛ `/portal/enrollment/`; template `mobina/enrollment.html`، selector `mobina.selectors.build`.
- مرجع: PDF صفحهٔ ۵۲.
- هدف/کنترل: مرور اطلاعات دانشجو و آموزشی، هشدار بدهی ثبت‌شده، مرحله‌نما و رفتن به مرحلهٔ دروس.
- ورودی/data schema: `student_code`, `term`; Student, Person, Field, Constant, Term و سقف مجاز واحد.
- API: GET صفحه؛ فرم و mutation ندارد؛ لینک «ادامه» به `selected-courses` می‌رود.
- اعتبارسنجی/مجوز: session و پروندهٔ متعلق؛ term از رکورد موجود؛ service هنگام ثبت نهایی بدهی، پنجره و قواعد را دوباره اعتبارسنجی می‌کند.
- خطا/empty: نبود پرونده/ترم با پیام؛ profile دیگران 403 و term نامعتبر 404؛ DB unavailable 503.
- آزمون/وابستگی: `apps/core/test_frontend.py`, `apps/core/enrollment/test_services.py`; shell مشترک، selector Mobina.
- وضعیت: اطلاعات واقعی و مرحله‌نما موجود؛ نتیجهٔ ثبت مستقل جزو این مرحله نیست؛ viewport تازه باز است.

# انتخاب واحد — مرحلهٔ اول

- مالک/route: Shaghayegh؛ `/portal/enrollment/`; template `shaghayegh/enrollment.html`، selector `shaghayegh.selectors.build`.
- مرجع: PDF صفحهٔ ۵۲.
- هدف/کنترل: مرور اطلاعات دانشجو و آموزشی، هشدار بدهی ثبت‌شده، مرحله‌نما و رفتن به مرحلهٔ دروس.
- ورودی/data schema: `student_code`, `term`; Student, Person, Field, Constant, Term و سقف مجاز واحد.
- API: GET صفحه؛ فرم و mutation ندارد؛ لینک «ادامه» به `selected-courses` می‌رود.
- اعتبارسنجی/مجوز: session و پروندهٔ متعلق؛ term از رکورد موجود؛ service هنگام ثبت نهایی بدهی، پنجره و قواعد را دوباره اعتبارسنجی می‌کند.
- خطا/empty: نبود پرونده/ترم با پیام؛ profile دیگران 403 و term نامعتبر 404؛ DB unavailable 503.
- آزمون/وابستگی: regression `test_enrollment_stage_one_uses_owned_profile_and_live_term_without_inventing_minimum_units` دادهٔ پرونده/ترم، بدهی و ادامه را بررسی می‌کند اما اجرا نشده؛ shell مشترک، selector Shaghayegh.
- وضعیت: اطلاعات واقعی و مرحله‌نما موجود؛ نتیجهٔ ثبت مستقل جزو این مرحله نیست؛ capture جاری جدید نداریم. عدد حداقل واحد PDF در منبع قواعد/API تعریف نشده است.

# ارزشیابی اساتید — فهرست

- مالک/route: Miri؛ `/portal/evaluation/`؛ قالب اختصاصی `miri/evaluation.html` و `miri.selectors`.
- مرجع: PDF صفحات ۳۴ تا ۳۷ و ۷۴؛ صفحات ۳۴–۳۷ ترکیب‌های مختلف یک/چند survey تکمیل‌شده را برای چهار درس نمایش می‌دهند.
- هدف/کنترل: وضعیت هر Enrollment فعال همان Student و Term؛ برای موارد باز، لینک مستقیم و امن به فرم همان enrollment؛ موارد ثبت‌شده badge دارند و submit دوباره ندارند. هر معیار ۱ تا ۵ است. همهٔ چهار state با دادهٔ واقعی ساخته می‌شوند، نه چهار route ثابت.
- داده/API: `TeacherSurvey`, `Enrollment`, `CourseOffering`, `Teacher`, `Lesson`; GET از page API؛ ثبت فقط در `evaluation-form` انجام می‌شود.
- مجوز/اعتبارسنجی: query به پرونده و ترم جاری محدود؛ فرم مقصد دوباره مالکیت، active status و تکراری نبودن را بررسی می‌کند. TeacherSurvey به Enrollment دانشجو وصل است؛ بی‌نام/محرمانه‌بودن از این ساختار تضمین نمی‌شود.
- پیوند مرتبط: `/portal/evaluation-form/?student_code=…&term=…&enrollment=…`؛ شناسهٔ enrollment سمت سرور بازبینی می‌شود.
- آزمون: regression جدید ترکیب survey کامل/در انتظار و scope دانشجو به `apps/core/test_frontend.py` افزوده شد؛ اجرا طبق درخواست کاربر برای فاز بعد است.
- وضعیت: صفحهٔ ۷۴ با فهرست چهار درس/تکمیل و پیوند فرم تطبیق شد؛ PDF پاسخ‌ها را محرمانه می‌نامد اما schema، survey را به enrollment وصل می‌کند، پس UI تضمین محرمانگی نمی‌دهد. regression به‌روزرسانی شد ولی اجرا نشده؛ capture جاری احرازشده نداریم.

# فرم ارزشیابی استاد

- مالک/route: Shahsavand؛ `/portal/evaluation-form/`; shared `core/live_content.html`; همان selector/form صفحهٔ evaluation.
- مرجع: PDF صفحات ۱۷ و ۳۱؛ stateهای دوره‌های متفاوت ۳۲–۳۳ و crop مقیاس ۴۹.
- هدف/کنترل: انتخاب enrollment و امتیاز کلی/کیفیت تدریس/رفتار (۱ تا ۵) و نظر متنی.
- داده/API: TeacherSurvey و enrollmentهای همان Student و Term؛ GET + POST API صفحه.
- اعتبارسنجی/مجوز: `ModelChoiceField` سمت سرور فقط enrollmentهای مالک؛ امتیازهای ۱–۵؛ duplicate در فرم و transaction دوباره بررسی می‌شود.
- خطا: form invalid همراه HTML 400؛ اگر وضعیت submit همزمان duplicate شود، ValidationError ثبت را متوقف می‌کند.
- navigation: مسیر فرعی از فهرست ارزشیابی؛ صفحهٔ مستقل چندتا انتخاب/گام برای stateهای PDF پیاده نشده.
- آزمون/وابستگی: `apps/core/test_frontend.py`; `academic_services/forms.py`, `TeacherSurvey`.
- وضعیت: persistence واقعی؛ تعداد stateهای PDF/حالت موفقیت بصری کامل نیست؛ viewport تازه باز.

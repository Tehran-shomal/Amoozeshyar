# ارزشیابی اساتید — فهرست

- مالک/route: Shahsavand؛ `/portal/evaluation/`; shared `core/live_content.html`; academic services selector.
- مرجع: PDF صفحات ۳۴–۳۷ و ۷۴؛ فهرست و stateهای تکمیل متفاوت در دادهٔ فعلی همگی قابل بازتولید نیستند.
- هدف/کنترل: فهرست نظرسنجی‌های ثبت‌شده برای enrollmentهای همان دانشجو و نیمسال؛ فرم shared.
- داده/API: TeacherSurvey, Enrollment, CourseOffering, Teacher, Lesson؛ GET و POST API صفحه.
- اعتبارسنجی: enrollment محدود به پرونده/term؛ ratingها ۱–۵؛ duplicate survey برای enrollment رد می‌شود.
- مجوز/خطا: session + پروندهٔ متعلق؛ فرم status/reviewer ندارد؛ خطای form با 400/HTML.
- navigation: لینک صفحهٔ فرم `evaluation-form` در صورت ارائهٔ UI؛ این slug منویی hidden است.
- آزمون/وابستگی: `apps/core/test_frontend.py`; `SurveyForm`, TeacherSurvey constraint/transaction.
- وضعیت: فهرست و ارسال فرم در selector حاضر؛ statusهای PDF مستقل و screenshot تازه باز.

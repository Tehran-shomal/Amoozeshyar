# فعالیت‌های آموزشی

- مالک/route: Omid؛ `/portal/academic-activities/`; `academic_services/academic_activities.html`; Omid selector.
- مرجع: PDF صفحهٔ ۶۱.
- هدف/کنترل: خلاصهٔ enrollment فعال/واحدها/وضعیت، تغییرهای اخیر و لینک‌های خدمات آموزشی.
- داده/API: Enrollment, CourseOffering, Lesson, EducationalChangeLog, Student, Term؛ GET API صفحه.
- نوشتن/اعتبارسنجی: read-only؛ هر mutation از route صفحهٔ مربوطه انجام می‌شود.
- مجوز/خطا: پروندهٔ جاری/term؛ query تغییرها فیلتر به student جاری و تا ۸ مورد اخیر؛ empty state مجاز.
- navigation: schedule, attendance, exam-card, calendar, transcript.
- آزمون/وابستگی: `apps/core/test_frontend.py`; selector و template تخصصی، common session shell.
- وضعیت: selector اختصاصی و render test؛ screenshot پس از تغییرهای فعلی و viewport کامل هنوز ثبت نشده.

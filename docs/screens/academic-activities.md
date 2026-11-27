# فعالیت‌های آموزشی

- مالک/route: Omid؛ `/portal/academic-activities/`; `omid/academic_activities.html`; `omid.selectors`.
- مرجع: PDF صفحهٔ ۶۱.
- هدف/کنترل: خلاصهٔ enrollment فعال/واحدها/وضعیت، حداکثر ۸ تغییر اخیر و چهار لینک برنامه، حضور و غیاب، کارت امتحان و تقویم؛ مطابق چیدمان کارت‌های صفحهٔ PDF ۶۱.
- داده/API: Enrollment, CourseOffering, Lesson, EducationalChangeLog, Student, Term؛ GET API صفحه.
- نوشتن/اعتبارسنجی: read-only؛ هر mutation از route صفحهٔ مربوطه انجام می‌شود.
- مجوز/خطا: enrollmentها به Student/Term جاری و تاریخچه به Student جاری محدود است؛ جدول تاریخچه حداکثر ۸ مورد اخیر را می‌آورد و empty state دارد. `EducationalChangeLog` فیلد term ندارد؛ بنابراین تاریخچهٔ تغییرها بین نیمسال‌ها قابل تفکیک نیست و نباید به‌عنوان رویدادهای فقط نیمسال جاری تعبیر شود.
- navigation: schedule, attendance, exam-card, calendar, transcript.
- آزمون/وابستگی: `apps/core/test_frontend.py`; selector و template تخصصی، common session shell.
- وضعیت: مرجع صفحه در `page-61-reference.png` است؛ selector/template چهار کارت و تاریخچهٔ واقعی را می‌سازند. رگرسیون scope تاریخچه و مقصد لینک‌ها اضافه شد ولی اجرا نشده؛ capture جاری احرازشده و مقایسهٔ viewport ثبت نشده است.

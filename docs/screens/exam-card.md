# کارت ورود به جلسه

- مالک/route: Omid؛ `/portal/exam-card/`; `academic_services/exam_card.html`; Omid selector.
- مرجع: PDF صفحهٔ ۲۱.
- هدف/کنترل: نمایش امتحان enrollmentهای فعال به ترتیب تاریخ/ساعت/کد؛ blockerها و چاپ مرورگر.
- داده/API: Enrollment, CourseOffering, Lesson, Classroom, TeacherSurvey و بدهی Student؛ GET API صفحه.
- قواعد موجود: blocker برای بدهی مثبت، ارزشیابی تکمیل‌نشده، یا نبود exam_date؛ این‌ها فقط دادهٔ فعلی‌اند.
- اعتبارسنجی/مجوز: session + student جاری؛ `printable` UI؛ no official issuance/write.
- خطا/محدودیت: شمارهٔ صندلی، QR، serial و مجوز رسمی در مدل نیست؛ کارت رسمی ساخته/تأیید نمی‌شود.
- navigation: منوی امتحانات؛ print button مرورگر.
- آزمون/وابستگی: `apps/core/test_frontend.py`; exam-card selector/template و Enrollment/Exam.
- وضعیت: قالب/selector و render test موجود؛ نتیجهٔ رسمی و screenshot بعد از آخرین تغییرات باز.

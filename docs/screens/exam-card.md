# کارت ورود به جلسه

- مالک/route: Niousha؛ `/portal/exam-card/`; `niousha/exam_card.html`; `niousha.selectors`.
- مرجع: [PDF صفحهٔ ۲۱](page-21-reference.png).
- هدف/کنترل: نمایش امتحان enrollmentهای فعال به ترتیب تاریخ/ساعت/کد، موانع واقعی پرونده و راهنمای حضور در جلسه.
- داده/API: Enrollment, CourseOffering, Lesson, Classroom, TeacherSurvey و `Student.tuition_debt`؛ GET `/api/portal/pages/exam-card/`.
- قواعد موجود: blocker برای بدهی مثبت (با مبلغ واقعی پرونده و واحد ریال)، ارزشیابی تکمیل‌نشده، یا نبود `exam_date`؛ صندلی و کارت رسمی ساخته نمی‌شوند.
- اعتبارسنجی/مجوز: session + student جاری؛ `printable` UI؛ no official issuance/write.
- خطا/محدودیت: شمارهٔ صندلی، QR، serial و مجوز رسمی در مدل نیست؛ کارت رسمی ساخته/تأیید نمی‌شود.
- navigation: منوی امتحانات؛ کنترل صدور کارت رسمی غیرفعال می‌ماند و پیوندهای پرداخت/ارزشیابی موجودند.
- آزمون/وابستگی: `apps/core/test_frontend.py::test_student_and_exam_cards_use_page_specific_real_data_templates` و `test_exam_card_debt_blocker_shows_the_persisted_amount_in_rials`; تست جدید در فاز فعلی اجرا نشده.
- وضعیت: PDF reference و source/API بررسی شدند؛ راهنمای حضور ۳۰ دقیقه پیش از آزمون با PDF هم‌راستا شد. capture جاری احرازشده نداریم؛ کارت و صندلی رسمی وابسته به provider/دادهٔ موجود نیستند.

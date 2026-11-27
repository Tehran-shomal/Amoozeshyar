# میری — ارتباط با استاد و خدمات عمومی (Shared Lead)

مالک `/portal/evaluation/`, `/portal/evaluation-form/`, `/portal/messages/`, `/portal/announcements/`, `/portal/notifications/`, `/portal/guide/`, `/portal/support/` است. نقش Shared Lead هماهنگی API، جریان‌های میان‌صفحه‌ای و آمادگی مستندات است؛ معماری همچنان یک Django monolith است.

- `pages.py`: manifest هفت route؛ `evaluation-form` از منوی اصلی پنهان است و از فهرست ارزشیابی با enrollment مشخص باز می‌شود.
- `selectors.py`: queryهای پیام، اعلان، ارزشیابی و تیکت را به حساب/پرونده محدود می‌کند؛ فهرست ارزشیابی وضعیت واقعی enrollmentهای فعال را می‌سازد و اطلاعیه‌های استاد فقط از Communicationهای type=`announcement` دریافت‌شده می‌آیند.
- `forms.py`: ارزشیابی پنج‌معیاره، پیام استاد، ایجاد Ticket.
- `templates/miri/messages.html`: استادهای ثبت‌نام فعال همان نیمسال، ارسال پیام و تاریخچهٔ مکاتبات حساب جاری؛ thread و تحویل بیرونی در مدل نیست.
- `templates/miri/evaluation.html` و `evaluation_form.html`: وضعیت درس‌ها، فرم پنج معیار و نتیجهٔ read-only.
- `TeacherSurvey` پنج فیلد مستقل دارد؛ migration `0006_teacher_survey_pdf_ratings` باید در مرحلهٔ مجاز migration اجرا شود. رکوردهای قدیمی بدون امتیازهای پنج‌گانه حفظ و read-only می‌مانند.
- `templates/miri/notifications.html`: مرکز اعلان‌ها با شمارش/فیلتر براساس typeهای واقعی همان حساب؛ POST فقط همان Notification را mark-read می‌کند و query فیلتر را نگه می‌دارد.
- `templates/miri/announcements.html`: کارت‌های مکاتبهٔ نوع announcement؛ POST فقط communication دریافتی حساب را mark-read می‌کند.
- `templates/miri/guide.html`: چهار کارت FAQ و CTA مطابق صفحهٔ ۲۸ PDF؛ مقصدها routeهای واقعی‌اند. اختلاف API حذف اضطراری دربارهٔ حداقل واحد آشکار است؛ قواعد رسمی جدید جعل نشده‌اند.
- `templates/miri/support.html`: فرم category/subject/content و جدول تیکت‌های root حساب جاری؛ آخرین پاسخ از reply واقعی Ticket می‌آید. پیوست به‌دلیل نبود فیلد مدل و پشتیبانی multipart در API، ادعا/ذخیره نمی‌شود.
- [ارائهٔ میری](../../../../docs/presentation/07_Miri.md) · [قراردادها](../../../../docs/API_CONTRACTS.md) · [ماتریس صفحه‌ها](../../../../docs/SCREEN_API_MATRIX.md).

انتشار اطلاعیه، ارسال خارجی، Q&A پویا و lifecycle کامل رسیدگی Ticket در این scope نیست؛ success ساختگی ندارند.

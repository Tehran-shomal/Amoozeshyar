# کارت دانشجویی دیجیتال

- مالک/route: Mobina؛ `/portal/student-card/`; `mobina/student_card.html`; `mobina.selectors`.
- مرجع: [PDF صفحهٔ ۲۰](page-20-reference.png).
- هدف/کنترل: نمایش مشخصات واقعی پرونده در قالب کارت و ارائهٔ پیوندهای اصلاح اطلاعات/پشتیبانی؛ در markup فعلی دکمهٔ چاپ وجود ندارد.
- داده/API: `Person`, `Student`, `Field`, `Term`; GET `/api/portal/pages/student-card/`؛ فقط اطلاعات پروندهٔ انتخاب‌شدهٔ متعلق به حساب جاری.
- اعتبارسنجی/مجوز: session و پروندهٔ متعلق؛ profile انتخابی؛ فیلد missing به‌عنوان missing می‌ماند.
- محدودیت/خطا: serial number، تاریخ اعتبار، QR یا credential رسمی در DB/service نیست و ساخته نمی‌شود.
- navigation: گروه خدمات دانشجویی؛ بازگشت به portal shell.
- آزمون/وابستگی: `apps/core/test_frontend.py::test_student_and_exam_cards_use_page_specific_real_data_templates`؛ در فاز فعلی اجرا نشده؛ `student_card.html`, selector.
- وضعیت: مرجع PDF در مخزن ثبت و سورس template/CSS/API بررسی شد؛ کد API برای GET ناشناس `401` می‌دهد. capture تازهٔ احرازشده موجود نیست و تطبیق بصری هنوز باز است.

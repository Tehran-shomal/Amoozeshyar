# ارتباط با استادان

- مالک/route: Miri؛ `/portal/messages/`; قالب اختصاصی `miri/messages.html` در shell مشترک؛ `miri.forms.MessageForm` و selector میری.
- مرجع: PDF صفحهٔ ۲۷ و نتیجهٔ ارسال در صفحهٔ ۴۰.
- هدف/کنترل: فهرست استادهای درس‌های فعال نیمسال انتخاب‌شده، composer گیرنده/موضوع/متن و هشت مکاتبهٔ اخیر حساب.
- داده/API: `GET|POST /api/portal/pages/messages/`; Communication, UserAccount, Person, Enrollment, CourseOffering, Teacher.
- اعتبارسنجی/مجوز: گیرنده فقط UserAccount فعال با Role فعال برای استادِ Enrollment فعال همان Student و همان Term است؛ enrollment حذف‌شده، درس غیرفعال و استادِ ترم دیگر قابل انتخاب نیست. sender از UserAccount فعال Person جاری و سرور تعیین می‌شود.
- خطا/محدودیت: فرم/DB errors مشترک؛ صفحهٔ ۴۰ نتیجهٔ ثبت واقعی Communication فرستاده‌شده توسط حساب جاری را نمایش می‌دهد، اما اتصال حساب واقعی استاد و تحویل بیرونی را تأیید نمی‌کند. مدل thread ID ندارد، پس «مکاتبات اخیر» فهرست رکوردهاست نه تجمیع مکالمه؛ SMS/email و read/delivery workflow به‌عنوان ارسال‌شده ادعا نمی‌شوند.
- navigation: گروه «اساتید»؛ history بر اساس sender/receiver حساب جاری.
- آزمون/وابستگی: regression `test_message_recipients_and_submission_results_are_account_scoped` در `apps/core/test_frontend.py` نوشته شده اما طبق درخواست اجرا نشده؛ `miri/forms.py`, selector, Communication/Enrollment/Offering.
- وضعیت: مرجع PDF در `docs/screens/page-27-reference.png` بررسی و UI/API scope سخت‌گیرانه‌تر شد؛ capture جاری احرازشده نداریم و توالی تصویری طبق plan روی صفحهٔ ۱۹ متوقف است.

# مرکز اعلان‌ها

- مالک/route: Miri؛ `/portal/notifications/`; قالب اختصاصی `miri/notifications.html` و `miri.selectors`.
- مرجع: [PDF صفحهٔ ۱۸](page-18-reference.png)؛ crop کلید تنظیم اعلان در صفحهٔ ۵۰ به تنظیمات مربوط است.
- ظاهر/تعامل: نوار فیلتر تعداددار، کارت‌های اعلان، دکمهٔ مشاهده برای اعلان خوانده‌نشده و لینک واقعی تنظیمات اعلان‌ها.
- داده/API: `Notification`, `UserAccount`, `Constant(notification_type)`؛ GET از `GET /api/portal/pages/notifications/` و فیلتر اختیاری `?notification_type=<code>`؛ POST با `notification_id` همان رکورد را read می‌کند.
- مالکیت: تمام queryها و updateها به `user__person=request.user` محدودند؛ نوع و شمار فیلترها فقط از اعلان‌های متعلق به همان حساب محاسبه می‌شوند؛ شناسهٔ حساب دیگر `404` است؛ query فیلتر پس از mark-read حفظ می‌شود.
- اختلاف منبع با PDF: lookup فعلی فقط `grade`, `announcement`, `class_change`, `system` دارد؛ دسته‌های PDF («آموزشی/مالی/درخواست‌ها») در مدل یا lookup رسمی تعریف نشده‌اند. UI برچسب و دستهٔ واقعی lookup را نشان می‌دهد و نوع مالی/درخواست یا اعلان جدید نمی‌سازد.
- محدودیت داده: Notification عنوان/متن/نوع/وضعیت/زمان دارد، ولی deep-link مقصد، کلاس delivery، pagination یا delivery-provider ندارد؛ CTA «مشاهده» فعلاً یعنی mark-read، نه رفتن به صفحهٔ دیگری.
- راستی‌آزمایی: regression source افزوده شده ولی بنا به درخواست اجرا نشده؛ API ناشناس `401`؛ capture جاری احرازشده و تعداد/typeهای حساب محلی هنوز ثبت نشده است. هیچ notification یا lookupای seed/ویرایش نشده.

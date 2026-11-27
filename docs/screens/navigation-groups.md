# گروه‌بندی نهایی منوی محصول

این فهرست بر اساس برش‌های PDF صفحات ۴ تا ۸ تهیه شده است. گروه‌های منو برای کاربر محصول‌اند؛ مالکیت فنی در [TEAM_OWNERSHIP.md](../TEAM_OWNERSHIP.md) جداست و تغییر منو، URL یا مالک API را عوض نمی‌کند.

| صفحهٔ مرجع | عنوان گروه | تعداد | مقصدها به ترتیب PDF |
|---:|---|---:|---|
| ۴ | سیستم دروس دانشجو | ۱۳ | `enrollment`, `add-drop`, `emergency-drop`, `registration-status`, `grade-appeal`, `academic-activities`, `transcript`, `curriculum`, `internship`, `attendance`, `calendar`, `schedule`, `exam-card` |
| ۵ | خدمات مالی | ۴ | `payments`, `secure-payment`, `financial-aid`, `tuition` |
| ۶ | درخواست مجوز | ۵ | `requests`, `education-certificate`, `graduation-certificate`, `guest-request`, `graduation` |
| ۷ | خدمات دانشجویی | ۵ | `student-card`, `notifications`, `settings`, `guide`, `support` |
| ۸ | اساتید | ۳ | `evaluation`, `messages`, `announcements` |

مجموع ۳۰ مقصد قابل‌نمایش است؛ `selected-courses` و `evaluation-form` همچنان routeهای پنهانِ workflow والدند. تنظیمات فقط در گروه خدمات دانشجویی قرار دارد و footer تنها خروج را نگه می‌دارد.

## ظاهر مشترک

هر گروه دو کپسول هم‌عنوان دارد: کپسول چپ نمایشی است و پیکان «‹» دارد؛ کپسول راست `<summary>` واقعی برای باز و بسته کردن گروه است و پیکان رو به پایین دارد. آیتم‌ها متن ساده و راست‌چین‌اند؛ کارت پس‌زمینه و هایلایت دائمی ردیف فعال حذف شده‌اند. این ظاهر در `static/core/portal.css` و markup در `apps/core/templates/core/portal_base.html` است.

## شواهد صفحه‌به‌صفحه

- صفحهٔ ۴: [مرجع](page-04-reference.png) · [capture جاری](page-04-current.png)
- صفحهٔ ۵: [مرجع](page-05-reference.png) · [capture جاری](page-05-current.png)
- صفحهٔ ۶: [مرجع](page-06-reference.png) · [capture جاری](page-06-current.png)
- صفحهٔ ۷: [مرجع](page-07-reference.png) · [capture جاری](page-07-current.png) · [بررسی گروه و API](student-services-menu.md)
- صفحهٔ ۸: [مرجع](page-08-reference.png) · [capture جاری](page-08-current.png) · [بررسی گروه و API](faculty-services-menu.md)

جزئیات هر API و نتیجهٔ بررسی در [PDF_PAGE_MAPPING.md](../PDF_PAGE_MAPPING.md) ثبت می‌شود. suite خودکار طبق درخواست کاربر در فاز بعد اجرا خواهد شد.

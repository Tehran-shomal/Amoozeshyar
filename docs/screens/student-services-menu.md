# خدمات دانشجویی — صفحهٔ ۷ PDF

- مرجع: [برش صفحهٔ ۷](page-07-reference.png)، ۵۳۲×۲۷۸.
- capture جاری: [برش از sidebar واقعی](page-07-current.png)، از route احراز‌شدهٔ `/portal/student-card/`.
- گروه PDF پنج مقصد دارد و عنوان آن «خدمات دانشجویی» است؛ فهرست به همان ترتیب در منوی جاری قرار گرفته است. قبل از اصلاح، سه لینک استادان نیز در همان گروه هشت‌تایی دیده می‌شدند؛ اکنون به گروه مستقل «اساتید» منتقل شده‌اند.

| مقصد | مالک route | route | API خواندن |
|---|---|---|---|
| کارت دانشجویی دیجیتال | Mobina | `/portal/student-card/` | `GET /api/portal/pages/student-card/` |
| مرکز اعلان‌ها | Miri | `/portal/notifications/` | `GET /api/portal/pages/notifications/` |
| تنظیمات زبان و اعلان‌ها | Mobina | `/portal/settings/` | `GET /api/portal/pages/settings/` |
| راهنمای سامانه | Miri | `/portal/guide/` | `GET /api/portal/pages/guide/` |
| مرکز پشتیبانی | Miri | `/portal/support/` | `GET /api/portal/pages/support/` |

درخواست GET احراز‌شده برای هر پنج route و API پیش‌تر `200` داده است. کارت دانشجویی پیش‌نمایش اطلاعات واقعی است نه کارت رسمی؛ اعلان‌ها و تیکت‌ها به حساب جاری محدودند؛ تنظیمات فقط فیلدهای مدل موجود را ذخیره می‌کند؛ راهنما routeهای واقعی را لینک می‌دهد. هیچ POST در این مرور اجرا نشد. جزئیات داده/فرم در پرونده‌های [student-card](student-card.md)، [notifications](notifications.md)، [settings](settings.md)، [guide](guide.md) و [support](support.md) است.

پوسته و سبک مشترک در [navigation.md](navigation.md) آمده است. آزمون خودکار برای فاز بعد محفوظ است.

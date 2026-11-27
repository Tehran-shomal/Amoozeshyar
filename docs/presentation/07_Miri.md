# ارائهٔ ۰۷ — میری: ارتباط با استاد و خدمات عمومی

### 1. معرفی بخش

ارتباط آموزشی، ارزشیابی، اعلان، راهنمای سامانه و پشتیبانی. Miri Shared Lead است: هماهنگی یکپارچگی بخش‌ها، APIها و مستندات؛ نه ایجاد معماری مستقل.

### 2. مسئولیت عضو

صفحات Master: ۱۶–۱۸، ۲۷–۲۹ و ۳۱–۳۷. PDF در clone حاضر نیست؛ شماره‌ها برای تطبیق تصویری قطعی نیستند.

### 3. صفحه‌ها و URLها

| صفحه | URL | API | وضعیت |
|---|---|---|---|
| ارزشیابی | `/portal/evaluation/` | GET صفحه | وضعیت هر درس از TeacherSurvey؛ فرم فقط برای درس‌های باز |
| فرم ارزشیابی | `/portal/evaluation-form/` | GET/POST صفحه | امتیاز کلی اجباری و دو معیار موجود اختیاری (۱–۵)، نظر اختیاری، ثبت نهایی read-only؛ پنج معیار PDF در schema نیست |
| پیام به استاد | `/portal/messages/` | GET/POST صفحه | گیرنده به استادهای مربوط محدود |
| اطلاعیه | `/portal/announcements/` | GET/POST صفحه | Communication نوع announcement؛ receiver-scoped mark-read؛ بدون FK درس/ترم |
| اعلان | `/portal/notifications/` | GET/POST صفحه | فیلتر شمارشی بر اساس type واقعی؛ Notification متعلق به حساب جاری؛ mark-read |
| راهنما | `/portal/guide/` | GET صفحه | راهنمای عملی با لینک routeها؛ Q&A رسمی پویا نیست |
| پشتیبانی | `/portal/support/` | GET/POST صفحه | ایجاد و فهرست Ticket حساب |

### 4. جریان UI

`live_portal.js` صفحه را load می‌کند، فرم را JSON می‌کند و validation HTML را با همان shell جایگزین می‌کند. اعلان با شناسهٔ فرم POST می‌شود. پیام و تیکت در DB ذخیره می‌شوند؛ تحویل بیرونی یا lifecycle کامل تیکت ادعا نمی‌شود.

### 5. API و داده

API صفحه: `GET|POST /api/portal/pages/<slug>/`. فرم ارزشیابی فقط فیلدهای موجود `overall_rating`, `teaching_quality`, `behavior` را در TeacherSurvey/Enrollment ثبت می‌کند؛ پیام و اطلاعیه از Communication و UserAccount، اعلان از Notification همان حساب با فیلترهای type موجود، support از Ticket creator همان حساب خوانده می‌شود. CSRF برای mutation الزامی است. Communication اطلاعیه در schema به term/course وصل نیست.

نمونهٔ علامت‌گذاری اعلان خود کاربر به‌عنوان خوانده‌شده (شناسه نمایشی):

```http
POST /api/portal/pages/notifications/
Content-Type: application/json
X-CSRFToken: <csrf-token>

{"notification_id":42}
```

پاسخ موفق HTTP 200: `{"redirect":"/portal/notifications/"}`؛ اعلان متعلق به شخص دیگر تغییر نمی‌کند. برای فرم پیام و تیکت، payloadهای واقعی هر صفحه در جدول `API_CONTRACTS.md` آمده‌اند.

### 6. مجوز و validation

فرم ارزشیابی فقط enrollment فعال همان دانشجو/ترم را می‌پذیرد؛ امتیاز کلی اجباری و دو فیلد قدیمی اختیاری‌اند؛ duplicate رد می‌شود و بعد از ثبت ویرایش ندارد. migration schema در این شاخه اضافه نمی‌شود؛ پنج معیار PDF با ستون‌های موجود قابل ذخیره نیستند. گیرندهٔ پیام از استادهای مرتبط است. Notification و Communication اطلاعیه فقط توسط صاحب/گیرندهٔ حساب mark-read می‌شوند. Ticket creator از session می‌آید و category باید فعال باشد.

### 7. فایل‌های فنی

- `apps/core/frontend/miri/{pages.py,selectors.py,forms.py}`
- `apps/core/frontend/miri/templates/miri/notifications.html`
- `apps/core/frontend/miri/templates/miri/guide.html`
- API: `apps/core/frontend/{api.py,api_urls.py}`؛ مشترک: `static/core/{portal_api.js,live_portal.js}`
- [Screens](../screens/evaluation.md), [messages](../screens/messages.md), [notifications](../screens/notifications.md), [guide](../screens/guide.md), [support](../screens/support.md)

### 8. Shared Lead و وابستگی‌ها

Miri مسئول مرور traceability API و هماهنگی جریان بین مالک‌هاست. اعتبار session و انتخاب term در shell مشترک حفظ می‌شود. ارسال SMS/email، انتشار اطلاعیه از پنل کارمند و پشتیبانی خارجی در این checkout provider ندارند.

### 9. تست و QA

اجرای suite و مرورگر طبق درخواست به فاز بعد موکول است. تست‌ها باید شامل owner check، ارسال duplicate survey، notification متعلق به دیگران، receiver نامعتبر، و POST بدون CSRF باشند.

### 10. سناریوی ارائه

۱) survey را برای enrollment قابل انتخاب باز کنید. ۲) پیام به استاد را نشان دهید. ۳) اعلان را mark-read کنید. ۴) تیکت ایجادشده را از همان حساب پیگیری کنید. ۵) محدودیت‌های ارسال خارجی و پاسخ staff را شفاف بگویید.

مستندات API و صفحه‌ها: [API_CONTRACTS](../API_CONTRACTS.md), [SCREEN_API_MATRIX](../SCREEN_API_MATRIX.md), [TEAM_OWNERSHIP](../TEAM_OWNERSHIP.md).

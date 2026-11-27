# ارائهٔ ۰۳ — پارسا: امور مالی

### 1. معرفی بخش

نمایش بدهی ثبت‌شده، سوابق تراکنش، خلاصهٔ شهریه و درخواست تسهیلات. هدف، نمایش وضعیت واقعی بدون ایجاد تراکنش نمایشی است.

### 2. مسئولیت عضو

مالک صفحه‌های مالی؛ در Master به صفحهٔ ۳۰ و صفحات ۶۴–۶۶ اشاره شده است. PDF در clone پیدا نشد؛ شماره‌ها نیازمند تطبیق بعدی‌اند.

### 3. صفحه‌ها و URLها

| صفحه | URL | API | وضعیت |
|---|---|---|---|
| سوابق پرداخت | `/portal/payments/` | GET صفحه | Payment متعلق به Student/Term، read-only |
| پرداخت امن | `/portal/secure-payment/` | GET صفحه | درگاه متصل نیست؛ اقدام پرداخت disabled/unavailable |
| تسهیلات | `/portal/financial-aid/` | GET/POST صفحه | ScholarshipApplication واقعی |
| شهریه نیمسال‌ها | `/portal/tuition/` | GET صفحه | جمع پرداخت‌های successful و debt ذخیره‌شده |

### 4. جریان UI

صفحه مالی از API با context دانشجو و ترم بارگیری می‌شود. پرداخت امن فقط وضعیت عدم اتصال را توضیح می‌دهد؛ درخواست تسهیلات به فرم واقعی متصل است و پس از ثبت از همان پایگاه داده خوانده می‌شود.

### 5. API و داده

تمام routeها `GET /api/portal/pages/<slug>/` دارند؛ تسهیلات همچنین `POST /api/portal/pages/financial-aid/` دارد. selector روی `Payment.student` و `Payment.term` محدود است و پرداخت موفق را بر اساس status lookup موجود جمع می‌زند.

نمونهٔ ثبت درخواست تسهیلات (مقادیر قراردادی):

```http
POST /api/portal/pages/financial-aid/?student_code=S10001&term=TERM-1
Content-Type: application/json
X-CSRFToken: <csrf-token>

{"scholarship_type":"وام","scholarship_reason":"شرح نمونه"}
```

پاسخ موفق HTTP 200: `{"redirect":"/portal/financial-aid/?student_code=S10001&term=TERM-1"}`. پرداخت آنلاین این قرارداد را ندارد و عمداً هیچ response موفقی برای درگاه نمونه‌سازی نشده است. «گزارش مغایرت» فقط به تیکت عمومی پشتیبانی می‌رود و به tracking code یا چرخهٔ مستقل بازپرداخت متصل نیست.

### 6. اعتبارسنجی و مرز امنیت

فرم تسهیلات owner و status را از سرور می‌گیرد. API پرداخت واقعی، callback درگاه، برگشت وجه متصل یا ثبت تراکنش ندارد؛ بنابراین POST پرداخت ارائه نمی‌شود. هیچ شماره کارت، مبلغ موفق یا gateway response نمونه ساخته نمی‌شود.

### 7. فایل‌های فنی

- `apps/core/frontend/parsa/{pages.py,selectors.py,forms.py}`
- `apps/core/frontend/parsa/templates/parsa/finance.html`
- `apps/core/models.py`: Payment, ScholarshipApplication, Term, Student
- [Screens](../screens/payments.md), [safe payment](../screens/secure-payment.md), [aid](../screens/financial-aid.md), [tuition](../screens/tuition.md)

### 8. وابستگی‌ها

خلاصه مالی داشبورد Mobina از همین رکوردهای ORM می‌خواند؛ term picker مشترک دامنهٔ Paymentهای قابل‌نمایش را تعیین می‌کند. سرویس درگاه dependency بیرونی محسوب می‌شود و هنوز credential/provider قراردادش در محیط نیست.

### 9. تست و QA

تست‌ها برای فاز بعد باقی مانده‌اند. آن فاز باید فقط با DB تست سناریوی empty, successful, failed, another-student access و تسهیلات را بررسی کند. درگاه تا ارائهٔ sandbox/contract همچنان unavailable ثبت شود.

### 10. سناریوی ارائه

۱) سوابق را باز کنید و نشان دهید هر ردیف از Payment آمده. ۲) ترم را تغییر دهید. ۳) صفحهٔ امن را باز و محدودیت درگاه را بخوانید. ۴) فرم تسهیلات را در DB تست ثبت و نتیجه را refresh کنید؛ آن را با پرداخت اشتباه نگیرید.

آدرس‌ها: [TEAM_OWNERSHIP](../TEAM_OWNERSHIP.md)؛ API: [API_CONTRACTS](../API_CONTRACTS.md).

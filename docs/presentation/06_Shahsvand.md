# ارائهٔ گروه شاهسوند — ارزشیابی و درخواست‌های بین‌دانشگاهی

### 1. معرفی بخش

ارتباط دانشجو با استاد، فرم ارزشیابی و چند درخواست موجود در مدل‌های دانشجویی.

### 2. مسئولیت عضو

در manifest فعلی، شاهسوند (با spelling `Shahsavand`) مالک پنج route زیرمجموعهٔ `academic_services` است. پیوست مسئولیت‌های وسیع‌تری شامل کارآموزی، درخواست عمومی و گواهی را به این عضو نسبت می‌دهد؛ در کد فعلی این‌ها در Neyousha/Pouya یا Omid هستند. این اختلاف برای ارائه شفاف می‌ماند.

### 3. صفحات پیاده‌سازی‌شده

| صفحه | PDF | URL | وضعیت واقعی |
|---|---:|---|---|
| فرم ارزشیابی | 17, 31 | `/portal/evaluation-form/` | route و SurveyForm موجود؛ slug از منو پنهان |
| فهرست ارزشیابی و stateها | 34–37, 49 | `/portal/evaluation/` | route موجود؛ چند crop PDF dataset مستقل ندارند |
| ارتباط با استاد | 27 | `/portal/messages/` | CommunicationForm موجود؛ گیرنده محدود به استاد درس‌های خود |
| درخواست مهمانی | 25 | `/portal/guest-request/` | TransferRequestForm موجود |
| بررسی فراغت از تحصیل | 26 | `/portal/graduation/` | درخواست بررسی موجود؛ تأیید رسمی نیست |
| کارآموزی/درخواست/مدرک | 24, 67, 72–73 | مسیرهای مربوطه | routeهای واقعی اما در manifest Neyousha/Pouya یا Omid هستند |

### 4. طراحی و عملکرد

فرم ارزشیابی به Enrollment متعلق متصل است و برای یک ثبت‌نام تکرار نمی‌شود. پیام به استاد از فهرست استادان ثبت‌نام‌های متعلق به دانشجو انتخاب می‌شود. درخواست مهمانی مقصد را ذخیره می‌کند؛ درخواست فراغت از مدل درخواست موجود استفاده می‌کند و پاسخ آن مدرک تأییدشده نیست.

### 5. APIهای مرتبط

- `GET|POST /api/portal/pages/evaluation/` و `evaluation-form/`
- `GET|POST /api/portal/pages/messages/`
- `GET|POST /api/portal/pages/guest-request/`
- `GET|POST /api/portal/pages/graduation/`

نمونهٔ قراردادی: `POST /api/portal/pages/messages/`، session و CSRF لازم؛ JSON scalarهای فرم (`receiver`, `subject`, `message_body`)؛ موفقیت 200 با redirect صفحه، خطای فرم 400 و خطای مالکیت/دسترسی 403. پاسخ پیام به معنی ارسال بیرونی SMS/email نیست.

### 6. سناریوی عملکرد

GET صفحه → selector/form متعلق → resolve Student از session → فرم validate → owner/status از server → save در ORM → redirect و refresh. برای survey، transaction و قفل Enrollment از duplicate submit جلوگیری می‌کند.

### 7. ارتباط با سایر بخش‌ها

messages/evaluation به Enrollment و Teacher وابسته‌اند؛ guest request به Student و مقصد؛ graduation به مدل عمومی StudentServiceRequest و constantهای از پیش seedشده. Miri در پیوست shared lead است و نقش مالک داده را جایگزین شاهسوند نمی‌کند.

### 8. ساختار فنی

- `apps/core/frontend/academic_services/pages.py`, `selectors.py`, `forms.py`
- `apps/core/frontend/academic_services/README.md` و `MEMBER_PAGES`
- `apps/core/frontend/common.py` برای `OwnedModelForm`
- مدل‌های `TeacherSurvey`, `Communication`, `TransferRequest`, `StudentServiceRequest`, `Enrollment` در `apps/core/models.py`.

### 9. تست‌ها

`apps/core/test_frontend.py` تست POST درخواست و تحمیل owner/status از سمت سرور را دارد؛ API/فرم‌های صفحه در render smoke بررسی می‌شوند. suite کامل آخرین بار ۱۰۱ Python و ۱۴ Node را بدون شکست گذراند؛ آزمون‌های دیگر در [TEST_REPORT.md](../TEST_REPORT.md) فهرست شده‌اند.

### 10. راهنمای ارائه به استاد

1. صفحهٔ evaluation را باز و ارتباط گزینه با enrollment متعلق را نشان دهید.
2. از ارسال دوبارهٔ همان survey جلوگیری را توضیح دهید.
3. فرم messages را باز و محدودیت receiver را در `MessageForm` نشان دهید.
4. guest/graduation را به‌عنوان «درخواست ثبت‌شده» معرفی کنید، نه انتقال/فراغت تأییدشده.
5. تفاوت مسئولیت‌های پیوست با manifest فعلی را صریح بیان کنید.

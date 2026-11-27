# ارائهٔ ۰۶ — شاهسوند: درخواست‌های دانشجویی

### 1. معرفی بخش

ثبت و پیگیری خدماتی که دانشجو برای پروندهٔ خود درخواست می‌کند؛ ثبت درخواست با پذیرش یا صدور نتیجهٔ رسمی فرق دارد.

### 2. مسئولیت عضو

کارآموزی، مهمانی، درخواست عمومی، فارغ‌التحصیلی و گواهی‌ها. صفحات اشاره‌شده در Master: ۲۴–۲۶، ۶۷ و ۷۲؛ منبع PDF در clone موجود نیست.

### 3. صفحه‌ها و URLها

| صفحه | URL | API | وضعیت |
|---|---|---|---|
| کارآموزی | `/portal/internship/` | GET/POST صفحه | ثبت Internship و فهرست وضعیت |
| مهمانی | `/portal/guest-request/` | GET/POST صفحه | TransferRequest |
| فارغ‌التحصیلی | `/portal/graduation/` | GET صفحه | GraduationAudit خواندنی؛ نوع درخواست معتبر موجود نیست |
| درخواست عمومی | `/portal/requests/` | GET/POST صفحه | StudentServiceRequest |
| گواهی آموزشی | `/portal/education-certificate/` | GET/POST صفحه | فقط با lookup `employment_certificate` فعال؛ صدور رسمی ندارد |
| گواهی دانش‌آموختگی | `/portal/graduation-certificate/` | GET صفحه | unavailable؛ lookup و provider صدور موجود نیست |

### 4. جریان UI

صفحه‌های دارای workflow تعریف‌شده رکوردها را می‌خوانند و فرم را با validation server ذخیره می‌کنند. برای graduation و graduation-certificate نوع درخواست مناسب در seed/lookup موجود نیست؛ نوع نامرتبط به‌جای آن استفاده نمی‌شود و POST غیرفعال است.

### 5. API و داده

API صفحه `GET|POST /api/portal/pages/<slug>/`، با session/CSRF. مدل‌ها: Internship، TransferRequest، StudentServiceRequest و GraduationAudit. payload فیلدهای فرم مطابق Django form metadata است؛ جزئیات در ماتریس/قرارداد API.

نمونهٔ ثبت درخواست مهمانی (مقدارها نمایشی‌اند):

```http
POST /api/portal/pages/guest-request/?student_code=S10001&term=TERM-1
Content-Type: application/json
X-CSRFToken: <csrf-token>

{"destination_university":"دانشگاه مقصد نمونه"}
```

پاسخ موفق HTTP 200: `{"redirect":"/portal/guest-request/?student_code=S10001&term=TERM-1"}`؛ این پاسخ فقط ایجاد درخواست DB را تأیید می‌کند، نه تأیید اداری یا پذیرش مقصد.

### 6. مجوز و validation

owner و status اولیه از server تعیین می‌شوند؛ نوع کارآموزی از lookup فعال و duration باید مثبت باشد؛ rows با Student جاری فیلتر می‌شوند. وضعیت review نهایی فقط از رکورد DB می‌آید. write فارغ‌التحصیلی تا وجود lookup معتبر unavailable می‌ماند.

### 7. فایل‌های فنی

- `apps/core/frontend/shahsvand/{pages.py,selectors.py,forms.py}`
- فرم‌ها: `InternshipForm`, `GuestRequestForm`, `ServiceRequestForm`, `CertificateForm`
- `apps/core/models.py` مدل‌ها و lookupها؛ shared API: `apps/core/frontend/api.py`
- [Screens](../screens/internship.md), [guest request](../screens/guest-request.md), [graduation](../screens/graduation.md), [requests](../screens/requests.md), [certificates](../screens/education-certificate.md)

### 8. وابستگی‌ها

Term و session در shell مشترک‌اند؛ وضعیت درخواست به lookup و رسیدگی staff موجود وابسته است. کارت دانشجویی مبینا مسیر درخواست اصلاح اطلاعات را لینک می‌کند؛ صدور گواهی external است.

### 9. تست و QA

تست‌ها در فاز بعد اجرا می‌شوند. ownership، نوع lookup غیرفعال/ناموجود، submit دوباره و عدم افشای پروندهٔ دانشجوی دیگر باید آنجا پوشش داده شوند.

### 10. سناریوی ارائه

۱) کارآموزی را باز کنید و validation مدت را نشان دهید. ۲) درخواست مهمانی را ثبت کنید. ۳) صفحهٔ عمومی و گواهی را مقایسه کنید. ۴) مشخص کنید ثبت، فقط ایجاد درخواست است و به‌تنهایی تأیید یا صدور مدرک نیست.

فهرست URLها: [TEAM_OWNERSHIP](../TEAM_OWNERSHIP.md)؛ قرارداد: [API_CONTRACTS](../API_CONTRACTS.md).

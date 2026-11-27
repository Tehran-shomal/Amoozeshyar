# ارائهٔ ۰۴ — امید: سوابق و پیشرفت آموزشی

### 1. معرفی بخش

صفحه‌های خواندن وضعیت آموزشی و ثبت درخواست اعتراض به نمره. داده‌ها باید از پرونده و نیمسال انتخاب‌شده بیایند.

### 2. مسئولیت عضو

کارنامه، نمره‌ها، ریزنمرات، چارت، فعالیت‌ها، وضعیت تحصیلی و اعتراض نمره. صفحات اشاره‌شده در Master: ۲۳ و ۶۰–۶۳؛ PDF محلی موجود نیست و این mapping تأیید تصویری ندارد.

### 3. صفحه‌ها و URLها

| صفحه | URL | API | وضعیت |
|---|---|---|---|
| فعالیت آموزشی | `/portal/academic-activities/` | GET صفحه | Enrollment و logهای موجود |
| کارنامه | `/portal/transcript/` | GET صفحه | Gradeهای ذخیره‌شده در term |
| چارت | `/portal/curriculum/` | GET صفحه | Curriculum فعال رشته |
| اعتراض نمره | `/portal/grade-appeal/` | GET/POST صفحه | فرم واقعی فقط روی Enrollment دارای Grade غیرخالی و متعلق به Student/Term |

### 4. جریان UI

کاربر ترم را در shell انتخاب می‌کند؛ کارنامه و فعالیت همان scope را می‌خوانند. اعتراض فقط با درس موجود و دلیل واردشده ثبت می‌شود. صفحهٔ فعالیت به برنامه/تقویم/حضور راه می‌دهد اما دادهٔ مشترک را جعل نمی‌کند.

### 5. API و داده

`GET /api/portal/pages/<slug>/` برای هر صفحه. اعتراض با `POST /api/portal/pages/grade-appeal/` ثبت می‌شود؛ `GradeAppealForm` enrollmentهای پرونده/ترم جاری را به گزینه‌های دارای نمرهٔ واقعی محدود می‌کند، و تاریخ/status را سرور تعیین می‌کند. schema کامل در `API_CONTRACTS.md`.

نمونهٔ قراردادی (شناسه‌ها نمایشی‌اند):

```http
POST /api/portal/pages/grade-appeal/?student_code=S10001&term=TERM-1
Content-Type: application/json
X-CSRFToken: <csrf-token>

{"enrollment":31,"appeal_reason":"لطفاً نمره بررسی شود"}
```

پاسخ موفق HTTP 200: `{"redirect":"/portal/grade-appeal/?student_code=S10001&term=TERM-1"}`؛ نمرهٔ گمشده/شناسهٔ خارج از پرونده به‌صورت validation error رد می‌شود.

### 6. اعتبارسنجی و محدودیت

selectorهای Grade و Enrollment با Student و Term محدود می‌شوند. نمره فقط از Grade موجود نمایش داده می‌شود. مهلت، فرایند بررسی و اختیار تصمیم نهایی اعتراض بدون فایل نیازمندی رسمی unknown است؛ ثبت فرم نتیجهٔ اعتراض را تأیید نمی‌کند.

### 7. فایل‌های فنی

- `apps/core/frontend/omid/{pages.py,selectors.py,forms.py}`
- `templates/omid/{academic_activities.html,transcript.html}`
- `apps/core/models.py`: Grade, Enrollment, Curriculum, EducationalChangeLog, GradeAppeal
- [Screens](../screens/academic-activities.md), [transcript](../screens/transcript.md), [curriculum](../screens/curriculum.md), [appeal](../screens/grade-appeal.md)

### 8. وابستگی‌ها

چارت به Field/lesson/constant، کارنامه به enrollment/offer/grade، و صفحهٔ فعالیت به log نیاز دارد. Niousha مالک برنامه و حضور است؛ Omid فقط linkهای cross-page را ارائه می‌کند.

### 9. تست و QA

به درخواست کاربر suite در مرحلهٔ بعد اجرا می‌شود. تست‌های بعدی باید خالی بودن نمره، term صحیح، دسترسی به Student دیگر و submit نامعتبر/تکراری appeal را بررسی کنند.

### 10. سناریوی ارائه

۱) کارنامهٔ ترم را نشان دهید. ۲) از آن به فعالیت‌ها بروید. ۳) چارت رشته را باز کنید. ۴) فرم اعتراض را بررسی و در test DB ذخیره کنید. ۵) روشن کنید status «در انتظار» به معنی پذیرش اعتراض نیست.

آدرس همهٔ صفحه‌ها: [TEAM_OWNERSHIP](../TEAM_OWNERSHIP.md)؛ قوانین: [BUSINESS_RULES](../BUSINESS_RULES.md).

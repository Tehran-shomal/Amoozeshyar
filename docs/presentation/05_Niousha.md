# ارائهٔ ۰۵ — نیوشا: برنامه و کلاس‌ها، Frontend Lead

### 1. معرفی بخش

نمایش برنامهٔ هفتگی، تقویم ترم، حضور و غیاب و برنامهٔ امتحان‌ها. نیوشا Frontend Lead است و هماهنگی consistency و responsive همهٔ گروه‌ها را بررسی می‌کند.

### 2. مسئولیت عضو

routeهای برنامه/کلاس و term picker مشترک. صفحات ذکرشده در Master: ۱۴–۱۵ و ۲۱–۲۲؛ فایل PDF مرجع در clone حاضر نیست و بازبینی بصری به بعد منتقل می‌شود.

### 3. صفحه‌ها و URLها

| صفحه | URL | API | وضعیت |
|---|---|---|---|
| برنامه هفتگی | `/portal/schedule/` | GET صفحه | شبکهٔ روز×ساعت از Enrollment/Offering فعال؛ جمع واحد و جلسه و بررسی overlap؛ چاپ مرورگر |
| تقویم ترم | `/portal/calendar/` | GET صفحه | تاریخ‌های ذخیره‌شده Term |
| حضور و غیاب | `/portal/attendance/` | GET صفحه | فقط Attendance موجود؛ no staff write |
| کارت امتحان | `/portal/exam-card/` | GET صفحه | برنامهٔ ثبت‌شده؛ صندلی/صدور رسمی ناموجود |
| انتخاب نیمسال | در header هر صفحه | `GET /api/scheduling/active-term/` | component مشترک |

### 4. جریان رابط

انتخاب ترم query صفحه را تغییر می‌دهد؛ schedule/attendance/exam-card همان term را می‌خوانند. چاپ از مرورگر است و خروجی backend جداگانه ندارد. صفحهٔ calendar فقط بازه‌هایی را نشان می‌دهد که Term در DB دارد.

### 5. API و داده

هر route از `GET /api/portal/pages/<slug>/` استفاده می‌کند. shared active-term endpoint برای نشان‌دادن ترم فعال است؛ صفحه بر اساس `term` انتخابی load می‌شود. داده از Enrollment، CourseOffering، Attendance و Term است.

نمونهٔ GET (بدنهٔ `html` خلاصه شده و مقدار term نمایشی است):

```http
GET /api/portal/pages/schedule/?student_code=S10001&term=TERM-1
Accept: application/json
Cookie: sessionid=<session>
```

پاسخ HTTP 200 با شکل `{"page":"schedule","html":"<section>…</section>","profile":{"student_code":"S10001"},"term":{"term_code":"TERM-1","display_label":"1405"}}`. این گروه API نوشتن حضور یا ساخت کارت رسمی ارائه نمی‌کند.

### 6. امنیت و محدودیت

queryها برای Student متعلق به حساب هستند. شمارهٔ صندلی، کارت امتحان رسمی، attendance marking توسط staff و تقویم رویداد مستقل در مدل/provider جاری نیستند. دکمهٔ چاپ، مدرک رسمی تولید نمی‌کند.

### 7. فایل‌های فنی

- `apps/core/frontend/niousha/{pages.py,selectors.py}` و `COMPONENTS`
- `apps/core/frontend/niousha/templates/niousha/exam_card.html`
- shell: `apps/core/templates/core/portal_base.html`; picker logic: `static/core/live_portal.js`
- [Screens](../screens/schedule.md), [calendar](../screens/calendar.md), [attendance](../screens/attendance.md), [exam-card](../screens/exam-card.md), [term picker](../screens/term-picker.md)

### 8. مسئولیت lead و cross-team

layout مرکزی و CSS مشترک در `static/core/` است. Lead به معنی تغییر مالکیت routeهای دیگر نیست؛ وظیفه، مرور سازگاری UI و گزارش موردهای ناهماهنگ است. Miri هماهنگ‌کنندهٔ API/docs مشترک است.

### 9. تست و QA

تست/browser در فاز بعد است. viewportهای 1920×1080 تا 390×844 و focus/RTL/table overflow باید آنجا بررسی شوند. تا آن زمان responsive complete علامت نمی‌خورد.

### 10. سناریوی ارائه

۱) ترم فعال را از header نشان دهید. ۲) schedule و چاپ را باز کنید. ۳) حضورهای ثبت‌شده و حالت empty را نشان دهید. ۴) کارت امتحان را باز و محدودیت seat number را توضیح دهید. ۵) به تقویم term بروید.

مالکیت و API: [TEAM_OWNERSHIP](../TEAM_OWNERSHIP.md)، [contracts](../API_CONTRACTS.md).

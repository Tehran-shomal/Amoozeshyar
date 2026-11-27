# اساتید — صفحهٔ ۸ PDF

- مرجع: [برش صفحهٔ ۸](page-08-reference.png)، ۵۳۲×۱۷۸.
- capture جاری: [برش از sidebar واقعی](page-08-current.png)، از route احراز‌شدهٔ `/portal/evaluation/`.
- PDF سه مقصد «ارزشیابی اساتید»، «ارتباط با اساتید» و «اطلاعیه‌های اساتید» را در گروه «اساتید» نشان می‌دهد. این‌ها اکنون سه لینک گروه‌اند؛ پنج مقصد خدمات دانشجویی در گروه جدا هستند.

| مقصد | route | API | رفتار کد |
|---|---|---|---|
| ارزشیابی اساتید | `/portal/evaluation/` | `GET /api/portal/pages/evaluation/`؛ فرم در `evaluation-form` | enrollmentهای حساب جاری؛ تکرار ثبت سمت سرور رد می‌شود |
| ارتباط با اساتید | `/portal/messages/` | `GET /api/portal/pages/messages/` | گفتگوهای حساب جاری؛ ارسال فقط به استاد مرتبط و فعال |
| اطلاعیه‌های اساتید | `/portal/announcements/` | `GET /api/portal/pages/announcements/` | اطلاعیه‌های قابل‌مشاهده برای حساب جاری؛ تغییر read-state با POST |

مالک هر سه صفحه Miri است. GET احراز‌شدهٔ route/API هر سه مقصد `200` داده است؛ POST اجرا نشده است. `evaluation-form` همچنان route پنهانِ مقصد اول است و لینک منوی مستقل ندارد. جزئیات در پرونده‌های [evaluation](evaluation.md)، [messages](messages.md) و [announcements](announcements.md) ثبت شده است.

پوستهٔ دوکپسولی در [navigation.md](navigation.md) توصیف شده؛ suite خودکار طبق درخواست برای فاز بعد محفوظ است.

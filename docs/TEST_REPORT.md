# گزارش آزمون — baseline ممیزی کامل سامانه

تاریخ: ۲۰۷۶-۰۵-۰۷ — branch: `codex/full-system-audit` — base: `dbe34c558df41517fe262a13e4af90eb75d2937e`

## محیط ایزوله

- دستورهای Django از `C:\Users\repair\Documents\یونی\.venv\Scripts\python.exe` با Django `5.2.18` اجرا شدند، اما working directory برابر clone ایزولهٔ branch بود.
- `SECRET_KEY`, `DEBUG`, و `ALLOWED_HOSTS` فقط برای process تست تنظیم شدند؛ `.env` یا secret جدیدی در مخزن ساخته نشد.
- تست‌ها دیتابیس تستی SQLite ساختند و در پایان حذف کردند. دیتابیس اصلی مخزن مبدأ دست‌نخورده ماند.
- نسخهٔ Node: `v24.19.0`.

## نتایج واقعی

| بررسی | نتیجه |
|---|---|
| `python manage.py test` | PASS — ۱۰۰ تست، ۰ شکست، ۱۳۶٫۱۳۲ ثانیه |
| `python manage.py check` | PASS — `System check identified no issues (0 silenced).` |
| `python manage.py makemigrations --check --dry-run` | PASS — `No changes detected` |
| `node --test static/core/tests/*.test.cjs` | PASS — ۱۳ تست، ۰ شکست، حدود ۰٫۲۹ ثانیه |

در اجرای کامل Django دقیقاً ۲۰ `RuntimeWarning` دربارهٔ datetimeهای naive با `USE_TZ=True` دیده شد: ۶ مورد فیلدهای بازهٔ ثبت‌نام/حذف‌و‌اضافه/حذف‌اضطراری `Term`، یک `Payment.payment_date`، سه `CounselingAppointment.counseling_date` و ۱۰ مورد `OnlineClass.start_at/end_at`. این‌ها خطای تست نبودند؛ باید هنگام تکمیل seed و قواعد تاریخ بررسی شوند.

## پوشش و موارد اجرا‌نشده

- تست‌های موجود account، scheduling، enrollment، request review، architecture و frontend در مجموع ۱۰۰ مورد را پوشش دادند.
- تست‌های JS موجود client API، ثبت‌نام/حذف، و مالکیت صفحه را پوشش دادند.
- screenshot تازه از branch فعلی در viewportهای `1920×1080`, `1536×864`, `1366×768`, `1280×720`, `1024×768`, `768×1024`, `390×844` هنوز گرفته نشده است؛ پس visual acceptance نهایی انجام نشده.
- baseline، صحت APIهای ثبت‌شده و فرم‌های موجود را نشان می‌دهد؛ نبود route در namespaceهای خالی یا رفتار رسمیِ سرویس بیرونی را پوشش نمی‌دهد.

## تکرار فرمان‌ها

در clone ایزوله، با interpreter دارای Django 5.2.18:

```powershell
python manage.py test
python manage.py check
python manage.py makemigrations --check --dry-run
node --test static/core/tests/*.test.cjs
```

# پیشرفت بازسازی و ممیزی

آخرین به‌روزرسانی: ۲۰۷۶-۰۵-۰۷

| فاز | وضعیت | شاهد / مانده |
|---|---|---|
| ۰ — ایزوله‌سازی Git و ایمنی | کامل | branch `codex/full-system-audit` در clone مستقل؛ source و دیتابیس اصلی دست‌نخورده |
| ۱ — کشف و ممیزی مخزن | کامل | inventory، route namespaceها، محدودیت‌های داده و baseline تازهٔ ۱۰۰ Python + ۱۳ Node؛ warningها شمرده و دسته‌بندی شدند |
| ۲ — تحلیل PDF | در حال تکمیل | تصاویر ۱–۹۶ مرور و جدول canonical ساخته شد؛ screen docs ایجاد شدند؛ route coverage در حال کنترل؛ screenshot branch فعلی باز است |
| ۳ — مدل و قرارداد API | کامل | قراردادهای endpoint، ۳۲ صفحه، قواعد implementation و تصمیم‌ها در چهار سند ثبت شدند |
| ۴ — layout، ورود و داشبورد | قبلاً پیاده؛ بازبینی مجدد لازم | تست‌های موجود سبزند؛ viewport/visual smoke این branch باقی است |
| ۵ — ثبت‌نام و گردش آموزشی | پیادهٔ بخشی و تست‌شده | ثبت/حذف و دادهٔ صفحات؛ نتیجه‌های مستقل PDF و قواعد تأییدنشده باز هستند |
| ۶ — مالی و سوابق | پیادهٔ بخشی | نمایش پرداخت و تسهیلات موجود؛ درگاه و چند مدل مالی غایب‌اند |
| ۷ — زمان‌بندی و درخواست‌ها | پیادهٔ بخشی | read API زمان‌بندی و review API درخواست موجود؛ routeهای دامنه‌ای و submissionهای فاقد schema باز هستند |
| ۸ — ارتباط و خدمات عمومی | پیادهٔ بخشی | فرم‌ها/selectorهای موجود؛ provider بیرونی و برخی workflowها مشخص نیستند |
| ۹ — یکپارچگی API | پیادهٔ بخشی | page API و client تست‌شده؛ APIهای دامنه‌ای مستقل متعدد وجود ندارند |
| ۱۰ — responsive و visual consistency | باز | CSS/viewport وجود دارد؛ screenshot هفت viewport هنوز ثبت نشده |
| ۱۱ — تست و bug fixing | baseline کامل | ۱۰۰ Python و ۱۳ Node تست پاس؛ بعد از تغییرها باید تکرار شوند |
| ۱۲ — مستندات و ارائه | در حال انجام | این checkpoint اولیه ساخته شد؛ mapping، screens و بستهٔ ۸ ارائه باقی است |
| ۱۳ — regression نهایی | باز | پس از پیاده‌سازی/مستندات |
| ۱۴ — Git و deliverables نهایی | باز | commitها و وضعیت نهایی هنوز ثبت نشده‌اند |

## آخرین checkpoint

- Base: `dbe34c558df41517fe262a13e4af90eb75d2937e`
- branch: `codex/full-system-audit`
- آخرین commit: `05b98eb900aa8214cc494a86991107e65428f237`؛ فایل‌های checkpoint اولیه: spec/plan و `INITIAL_AUDIT.md`, `TEST_REPORT.md`, `PROGRESS.md`, `NEXT_STEPS.md`.
- تست baseline تازه: ۱۰۰ Python + ۱۳ Node، همه پاس؛ Django check و migration check پاس؛ ۲۰ warning timezone از fixtureها در `TEST_REPORT.md` ثبت شد.
- هیچ migration یا دستکاری دیتابیس واقعی انجام نشده.
- مانع اجرایی: فایل رفتاری مرجع SDD موجود نیست؛ قوانین نامعلوم باید در گزارش جدا بمانند. TLS زمان سیستم مانع نصب dependency از PyPI شد؛ از venv موجود فقط برای اجرای تست استفاده شد.

## گام بعدی

گام بعد: شمارش screen docs و پوشش ۹۶ شمارهٔ PDF را کنترل و Task 2 را commit کن؛ سپس Task 3 را با مستندهای صفحه/حالت commit کن. پس از آن browser visual smoke و رفع فقط defectهای بازتولیدشده با TDD.

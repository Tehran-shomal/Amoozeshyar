# پیشرفت بازسازی و ممیزی

آخرین به‌روزرسانی: ۲۰۷۶-۰۵-۰۷

| فاز | وضعیت | شاهد / مانده |
|---|---|---|
| ۰ — ایزوله‌سازی Git و ایمنی | کامل | branch `codex/full-system-audit` در clone مستقل؛ source و دیتابیس اصلی دست‌نخورده |
| ۱ — کشف و ممیزی مخزن | کامل | inventory، route namespaceها، محدودیت‌های داده و baseline تازهٔ ۱۰۰ Python + ۱۳ Node؛ warningها شمرده و دسته‌بندی شدند |
| ۲ — تحلیل PDF | کاملِ مستندات | نگاشت ۹۶/۹۶؛ ۳۲/۳۲ screen docs و stateهای PDF موجود؛ link/route coverage پاس؛ screenshot branch فعلی جداگانه باز است |
| ۳ — مدل و قرارداد API | کامل | قراردادهای endpoint، ۳۲ صفحه، قواعد implementation و تصمیم‌ها در چهار سند ثبت شدند |
| ۴ — layout، ورود و داشبورد | قبلاً پیاده؛ بازبینی مجدد لازم | تست‌های موجود سبزند؛ viewport/visual smoke این branch باقی است |
| ۵ — ثبت‌نام و گردش آموزشی | پیادهٔ بخشی و تست‌شده | ثبت/حذف و دادهٔ صفحات؛ نتیجه‌های مستقل PDF و قواعد تأییدنشده باز هستند |
| ۶ — مالی و سوابق | پیادهٔ بخشی | نمایش پرداخت و تسهیلات موجود؛ درگاه و چند مدل مالی غایب‌اند |
| ۷ — زمان‌بندی و درخواست‌ها | پیادهٔ بخشی | read API زمان‌بندی و review API درخواست موجود؛ routeهای دامنه‌ای و submissionهای فاقد schema باز هستند |
| ۸ — ارتباط و خدمات عمومی | پیادهٔ بخشی | فرم‌ها/selectorهای موجود؛ provider بیرونی و برخی workflowها مشخص نیستند |
| ۹ — یکپارچگی API | پیادهٔ بخشی | page API و client تست‌شده؛ APIهای دامنه‌ای مستقل متعدد وجود ندارند |
| ۱۰ — responsive و visual consistency | باز | CSS/viewport وجود دارد؛ screenshot هفت viewport هنوز ثبت نشده |
| ۱۱ — تست و bug fixing | baseline کامل | ۱۰۰ Python و ۱۳ Node تست پاس؛ بعد از تغییرها باید تکرار شوند |
| ۱۲ — مستندات و ارائه | در حال انجام | دو checkpoint audit/API ساخته شد؛ mapping و screen docs آمادهٔ commit؛ بستهٔ ۸ ارائه باقی است |
| ۱۳ — regression نهایی | باز | پس از پیاده‌سازی/مستندات |
| ۱۴ — Git و deliverables نهایی | باز | commitها و وضعیت نهایی هنوز ثبت نشده‌اند |

## آخرین checkpoint

- Base: `dbe34c558df41517fe262a13e4af90eb75d2937e`
- branch: `codex/full-system-audit`
- آخرین commit: `db6dae31652865f6789a9f19073552563e11e679`؛ شامل قراردادهای API، ماتریس، قواعد و تصمیم‌ها؛ checkpoint اولیه در commit قبلی است.
- تست baseline تازه: ۱۰۰ Python + ۱۳ Node، همه پاس؛ Django check و migration check پاس؛ ۲۰ warning timezone از fixtureها در `TEST_REPORT.md` ثبت شد.
- هیچ migration یا دستکاری دیتابیس واقعی انجام نشده.
- مانع اجرایی: فایل رفتاری مرجع SDD موجود نیست؛ قوانین نامعلوم باید در گزارش جدا بمانند. TLS زمان سیستم مانع نصب dependency از PyPI شد؛ از venv موجود فقط برای اجرای تست استفاده شد.

## گام بعدی

گام بعد: checkpoint نگاشت/صفحه‌ها را commit کن؛ سپس browser visual smoke هفت viewport، رفع defectهای بازتولیدشده با TDD و در پایان presentation pack و regression.

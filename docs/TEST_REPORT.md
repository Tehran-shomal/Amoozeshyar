# گزارش آزمون و بازبینی مرورگر

تاریخ: ۲۰۷۶-۰۵-۰۷ — branch: `codex/full-system-audit` — base: `dbe34c558df41517fe262a13e4af90eb75d2937e`

## محیط ایزوله

- working directory همهٔ فرمان‌ها clone مستقل `Amoozeshyar-audit-clone-3` بود؛ interpreter دارای Django `5.2.18` از venv موجود استفاده شد. source checkout و دیتابیس آن تغییر نکردند.
- تست Django دیتابیس موقت SQLite ساخت و در پایان حذف کرد. مرورگر روی runserver همین clone و SQLite seedشدهٔ clone بود. رکورد حساب QA موقت پس از سناریوی مرورگر پاک شد.
- secretهای process فقط برای اجرای محلی تنظیم شدند؛ secret یا credential جدید در مخزن ثبت نشد.
- Node `v24.19.0`. Browser smoke با Microsoft Edge/CDP محلی انجام شد؛ Playwright یا dependency جدید نصب نشد.

## اجرای واقعی تست‌ها

| بررسی | baseline | آخرین اجرا روی تغییرهای این branch |
|---|---:|---:|
| `manage.py test` | ۱۰۰ پاس | **۱۰۱ پاس، ۰ شکست، ۱۴۲٫۴۹۱ ثانیه** |
| `manage.py check` | پاک | **PASS — هیچ issue شناسایی نشد** |
| `makemigrations --check --dry-run` | بدون تغییر | **PASS — No changes detected** |
| `node --test static/core/tests/*.test.cjs` | ۱۳ پاس | **۱۴ پاس، ۰ شکست، ۰٫۲۰۴ ثانیه** |
| تست focused پوستهٔ مالی | — | PASS؛ `payments`, `secure-payment`, `tuition` هرکدام یک shell دارند |
| تست focused قاب جست‌وجوی responsive | RED سپس GREEN | PASS؛ قاب wrapper باقی، border input داخلی صفر |
| `git diff --check` | — | PASS پس از مستندسازی نهایی |

در اجرای کامل Django دقیقاً ۲۰ `RuntimeWarning` دربارهٔ datetimeهای naive با `USE_TZ=True` ثبت شد: ۶ فیلد بازهٔ `Term`، یک `Payment.payment_date`، سه `CounselingAppointment.counseling_date` و ۱۰ فیلد `OnlineClass.start_at/end_at`. این‌ها شکست تست نبودند؛ زمان seed بدون منبع timezone معتبر تغییر داده نشد.

## browser integration smoke

سناریوها با Edge محلی و فقط دادهٔ clone انجام شدند؛ حساب QA موقت پس از خروج حذف شد.

| سناریو | وضعیت و شاهد |
|---|---|
| ورود | PASS؛ فرم واقعی login، API login، session و انتقال به dashboard |
| داشبورد | PASS؛ shell و محتوای DB-backed بارگذاری شدند |
| انتخاب نیمسال | PASS؛ انتخاب `14052` در dialog، query URL از `14051` تغییر کرد |
| مسیر انتخاب درس | PASS؛ link «ادامه» از `/portal/enrollment/` به `/portal/selected-courses/` رفت |
| خواندن ارائه‌ها | PASS؛ `GET /api/scheduling/offerings/?term=14051` پاسخ 200 و دو offering seed را برگرداند |
| منع دسترسی به پروفایل دیگر | PASS؛ `GET /api/portal/pages/payments/?student_code=4011001` برای حساب QA پاسخ 403 `permission_denied` داد |
| خروج | PASS؛ فرم واقعی logout session را بست و به `/login/` برگشت |
| ثبت/حذف واقعی در مرورگر | NOT RUN؛ seed فعلی برای term فعال خارج از بازهٔ ثبت‌نام است و term دیگر offering ندارد. داده/بازهٔ مصنوعی برای دورزدن این محدودیت ساخته نشد. مسیرهای معتبر register/drop و persistence در `apps/core/enrollment/test_services.py` آزموده می‌شوند. |
| خواندن مالی | PASS؛ صفحهٔ payment shell واحد دارد؛ provider بانکی اجرا/شبیه‌سازی نشد |

## viewport و مقایسهٔ بصری

هفت viewport در Edge بررسی شدند. در هیچ‌کدام `document` یا `body` horizontal overflow نداشت؛ جدول‌های عریض در wrapper خودشان scroll می‌شوند. در desktop اختلاف `scrollWidth` و `innerWidth` فقط با عرض scrollbar عمودی سازگار بود، نه overflow افقی.

| Viewport | صفحهٔ captureشده | نتیجه |
|---|---|---|
| 1920×1080 | داشبورد | shell/کارت‌ها دیده شدند؛ بدون horizontal overflow |
| 1536×864 | دروس انتخاب‌شده | جدول در wrapper؛ بدون document overflow |
| 1366×768 | حذف و اضافه | modal/جدول در layout اصلی؛ بدون document overflow |
| 1280×720 | سوابق پرداخت | پس از fix فقط یک shell؛ بدون document overflow |
| 1024×768 | تقویم | بدون document overflow |
| 768×1024 | حضور و غیاب | قاب search دوتایی بازتولید و رفع شد؛ input border=`0px`, wrapper border=`1px`, input داخل wrapper |
| 390×844 | دروس انتخاب‌شده | بدون document overflow؛ جدول فقط در wrapper افقی scroll می‌شود |

مقایسهٔ نماینده با PDF برای صفحه‌های ۲، ۹، ۵۳ و ۶۳ انجام شد. هویت رنگی و shell راست‌به‌چپ قابل‌تشخیص است، ولی چیدمان و داده‌ها pixel-identical نیستند: dashboard فعلی ترکیب کارت‌ها/خلاصهٔ متفاوت دارد، جمع‌بندی پایین صفحهٔ انتخاب واحد PDF در UI موجود نیست، و صفحهٔ مالی فقط دادهٔ seed موجود را نشان می‌دهد. بنابراین وضعیت visual **جزئی و representative** است، نه پذیرش ۹۶ صفحه.

هفت capture viewport پس از آخرین اصلاح CSS دوباره گرفته شده‌اند؛ تصویرها در temp همین نشست‌اند و commit نشده‌اند:

- مجموعهٔ نهایی viewport: `C:\Users\repair\AppData\Local\Temp\2\amoozeshyar-final-visual-tdizJY`

## تغییرات و موارد باز

- `apps/core/frontend/parsa/templates/parsa/finance.html` اکنون fragment است، نه shell دوم؛ regression test برای سه route مالی اضافه شد.
- قانون border تکراری input در `static/core/responsive.css` حذف شد؛ Node regression test با RED/GREEN و computed style مرورگر تأیید شد.
- تست render عمومی صفحات همهٔ edge caseهای هر ۳۲ فرم را پوشش نمی‌دهد؛ تست مرورگر برای هر صفحه یا registration write اجرا نشده است.
- APIهای مستقل staff در ۱۴ namespace خالی، درگاه پرداخت، صدور رسمی کارت/مدرک، lifecycle کامل Ticket، تقویم event-based و Q&A راهنما همچنان gap هستند.
- منبع رفتاری `نیازمندی_های_آموزشیار.md` در repo نیست؛ قواعد تجاری ناشناخته در [BUSINESS_RULES.md](BUSINESS_RULES.md) و [NEXT_STEPS.md](NEXT_STEPS.md) باز مانده‌اند.

## فرمان‌های تکرار

```powershell
python manage.py test
python manage.py check
python manage.py makemigrations --check --dry-run
node --test static/core/tests/*.test.cjs
git diff --check
```

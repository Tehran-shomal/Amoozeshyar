# بررسی ادامهٔ مهاجرت React — ۲۰۲۶-۱۱-۲۶

## اصلاح بازبینی پیش از PR — ۲۰۲۶-۱۱-۲۷

- serializer تاریخ اکنون `date` و `datetime` را جداگانه مدیریت می‌کند؛ فرم‌های نامعتبر همان نمونهٔ bindشده و خطاهای save را به React برمی‌گردانند.
- endpoint قدیمی حذف درس پنجرهٔ عادی یا اضطراری را می‌پذیرد؛ endpoint اختصاصی emergency فقط پنجرهٔ اضطراری را قبول می‌کند.
- migration جدید امتیازهای پنج‌گانه حذف شد تا شرط «بدون تغییر schema» رعایت شود. فرم فقط `overall_rating`, `teaching_quality`, `behavior` موجود را ذخیره می‌کند؛ تفاوت پنج معیار PDF با schema باز است.
- Regressionهای مربوطه اضافه/به‌روز شدند اما اجرا نشدند؛ اجرای suite طبق درخواست برای QA بعدی deferred است.

این بخش فقط شواهد ایستا و build مهاجرت React را ثبت می‌کند؛ تست‌های خودکار عمداً اجرا نشده‌اند و وضعیت آن‌ها به PASS تغییر نمی‌کند.

- پیش‌فرض runtime: ورود و ۳۳ route پورتال به پوستهٔ React می‌روند؛ `?legacy=1` مسیر قالب‌های Django را برای سازگاری نگه می‌دارد.
- نگاشت ایستا: ۳۳ slug رجیستری به route و dispatch React متصل‌اند؛ crosswalk جداگانهٔ ۹۶ ردیفی در `PDF_PAGE_MAPPING.md` مسیر/state و کامپوننت را مشخص می‌کند.
- `npm run typecheck --prefix frontend-react`: **PASS**.
- `npm run build --prefix frontend-react`: **PASS**؛ ۵۸ ماژول، `app.js` برابر ۳۶۰٫۷۵ kB (gzip: ۹۶٫۸۸ kB) و `style.css` برابر ۰٫۶۴ kB (gzip: ۰٫۳۴ kB).
- `py_compile` برای viewها، serializer، فرم‌ها، API و registry: **PASS**؛ `manage.py check --verbosity 0`: **PASS، بدون issue**.
- `manage.py findstatic` هر دو asset یعنی `core/react-build/app.js` و `style.css` را پیدا کرد: **PASS**.
- مقایسهٔ منبع: ۳۲ slug رجیستری به‌علاوهٔ `home`، دقیقاً با ۳۳ route و dispatch React برابر است؛ crosswalk PDF شامل ۹۶ ردیف پیوستهٔ ۱ تا ۹۶ است.
- بررسی `dangerouslySetInnerHTML|innerHTML` در `frontend-react/src`: هیچ sinkی پیدا نشد. `git diff --check` و `git diff --cached --check`: **PASS**؛ مورد whitespace خطادار گزارش نشد (Git فقط دربارهٔ تبدیل معمول LF به CRLF هشدار داد).
- `manage.py test` و هر suite خودکار: **NOT RUN — به درخواست کاربر برای فاز QA بعدی موکول شد**.
- پذیرش بصری احرازشده: **NOT DONE**؛ cursor ترتیبی PDF روی صفحهٔ ۹ است. build یا route coverage، جای capture و تطبیق بصری نیست.

# گزارش آزمون و بازبینی مرورگر

## بازبینی runtime فقط‌خواندنی — ۲۰۲۶-۱۱-۲۵

- سرور clone با Django روی `127.0.0.1:8000` اجرا شد و از DB SQLite داخل همین clone استفاده می‌کند.
- `GET /login/` → `200`؛ `GET /api/portal/pages/selected-courses/` و `GET /api/scheduling/offerings/` بدون نشست → `401`.
- `GET /portal/selected-courses/` بدون نشست → `302` به ورود؛ فایل `responsive.css` → `200` و شامل override عنوان sidebar، عرض دکمه‌های 160/180px و کارت‌های تخت صفحهٔ ۹ است. این تأیید تحویل asset است، نه تأیید بصری UI.
- این فقط smoke read-only است، نه اجرای test suite؛ هیچ POST، login ناموفق، تغییر رمز یا تغییر داده انجام نشد. capture احرازشدهٔ صفحهٔ ۹ همچنان pending است.

> **گزارش تاریخی:** نتایج اجرای تست زیر مربوط به قبل از تغییر اخیر مالکیت هفت‌گانه و جابه‌جایی selector/form/templateهاست؛ آن‌ها را PASS نسخهٔ فعلی تلقی نکن. برای نسخهٔ جاری، مرور تصویری ترتیبی تا صفحهٔ ۱۴ و GETهای read-only صفحات ۹ و ۱۴ ثبت شده‌اند. source صفحات ۱۵–۱۹ پیش رفته، اما capture جاری/API مجاز در دسترس نیست. صفحهٔ ۱۷ پنج معیار مستقل دارد و migration جدید اجرا نشده؛ صفحهٔ ۱۸ typeهای واقعی را فیلتر می‌کند؛ صفحهٔ ۱۹ فقط فیلدهای موجود Person را ذخیره می‌کند و کانال‌های بدون provider را وعده نمی‌دهد. suite، mutationها و browser/workflow QA کامل طبق درخواست کاربر برای فاز بعد هستند.

تغییرهای جدید تستی نیز تا اجرای فاز بعد **NOT RUN** هستند؛ از جمله `test_guide_contains_actionable_instructions_and_real_page_links`، رگرسیون اجباری‌بودن نوع درخواست در کارآموزی/خدمات/گواهی، `test_selected_courses_matches_pdf_columns_and_hides_offerings_until_requested`، `test_attendance_page_summarizes_sessions_by_active_course`، `test_calendar_page_renders_month_grid_and_real_term_events`، `test_announcements_use_owned_announcement_communications_and_mark_read`، `test_evaluation_form_uses_existing_survey_fields_and_persists_response`، `test_react_validation_response_keeps_form_errors_from_failed_save`، `test_evaluation_form_does_not_accept_another_students_enrollment`، `test_date_payload_formatter_accepts_plain_date_values`، `test_notifications_filter_by_owned_type_and_mark_only_owned_records_read`، `test_settings_page_renders_only_profile_backed_preferences`، `test_settings_post_updates_only_the_logged_in_person` و تغییر سناریوی seeded فارغ‌التحصیلی.

ادامهٔ ممیزی صفحات ۶۰–۶۱: assertions هشدار مهلت/پیوست صفحهٔ اعتراض نمره به تست موجود افزوده شد؛ regression فعالیت‌های آموزشی نیز scope تاریخچه به Student جاری و چهار مقصد لینک را پوشش می‌دهد. هر دو **NOT RUN** هستند؛ هیچ تستی در این ادامه اجرا نشده است.

صفحهٔ ۶۲: `test_transcript_shows_current_enrollments_without_inventing_split_grades` افزوده شد؛ درس‌های دارای/فاقد نمره، جمع واحد، مالکیت، نبود میان‌ترم/پایان‌ترم ساختگی و لینک‌های PDF را بررسی می‌کند. **NOT RUN**.

صفحهٔ ۶۳: تست مالکیت پرداخت اکنون یک پرداخت موفق و یک ناموفق می‌سازد و جمع موفق، وضعیت failed و نبود شرح در schema را بررسی می‌کند. **NOT RUN**.

صفحهٔ ۶۴: `test_payment_page_does_not_fake_a_gateway` حالا مبلغ بدهی/پرداخت‌کننده، دکمهٔ disabled، لینک سوابق و نبود فیلد کارت یا Payment جدید را مطالبه می‌کند. **NOT RUN**.

صفحهٔ ۶۵: آزمون نتیجهٔ ScholarshipApplication نبود فیلد amount/IBAN/attachment و پیام محدودیت/عدم تأیید را بررسی می‌کند. صفحهٔ ۶۶: `test_tuition_summary_uses_successful_payments_and_real_debt_only` تفکیک failed، بدهی واقعی، فقدان ریزتعرفه و لینک‌ها را پوشش می‌دهد. هر دو **NOT RUN**.

صفحهٔ ۶۷: `test_request_submission_assigns_owner_and_pending_on_server` وجود هشدار نبود شمارهٔ تماس/پیوست و ثبت محلی را هم بررسی می‌کند. **NOT RUN**.

صفحات ۶۸–۷۱: `test_add_drop_page_exposes_real_add_and_drop_actions_together` اکنون وجود ستون وضعیت و status واقعی Enrollment را هم مطالبه می‌کند. دادهٔ PDF-specific چندردیفی در clone seed نشده؛ regression **NOT RUN**.

صفحهٔ ۷۲: regression گواهی آموزشی محدودیت مخاطب/نسخه/تحویل را مطالبه می‌کند. صفحهٔ ۷۳: `test_graduation_certificate_page_uses_real_checks_without_fake_issuance` دادهٔ چارت/پرونده، لینک‌ها و نبود صدور ساختگی را بررسی می‌کند. هر دو **NOT RUN**.

صفحهٔ ۷۴: `test_evaluation_list_builds_completed_and_pending_rows_from_owned_surveys` اکنون بازهٔ rating ۱–۵ و پیوند survey به enrollment/نبود تضمین anonymity را هم مطالبه می‌کند. **NOT RUN**.

صفحات ۷۵–۷۸: `test_emergency_drop_result_shows_only_the_owned_dropped_enrollment` مالکیت/نیمسال و نبود نشت نتیجه را مطالبه می‌کند؛ **NOT RUN**. صفحات ۷۹–۸۸: `test_selected_courses_matches_pdf_columns_and_hides_offerings_until_requested` مودال/گروه‌بندی و نبود group number یا تعرفهٔ جعلی را مطالبه می‌کند؛ Node binding test نیز event offerings و ثبت offering انتخابی را بررسی می‌کند؛ هر دو **NOT RUN**. صفحات ۸۹–۹۶: assertions حذف عادی/اضطراری می‌گویند API بازپرداخت را محاسبه/ثبت نمی‌کند؛ **NOT RUN**.

تکمیل یادداشت NOT RUN: regressionهای جدید `test_internship_submission_shows_only_the_owned_persisted_result`, `test_guest_request_submission_shows_only_the_owned_persisted_result` و سناریوی نتیجه در `test_message_recipients_and_submission_results_are_account_scoped` نیز نوشته شده‌اند؛ اجرا نشده‌اند.

ادامهٔ صفحات ۴۱–۴۶: assertions نتیجهٔ تنظیمات/اعتراض/تسهیلات/درخواست/گواهی به تست‌های موجود افزوده شدند؛ تست تیکت `test_support_submission_uses_the_active_open_status` نیز redirect شناسه‌دار، نتیجهٔ واقعی، نبود پیوست و عدم افشای تیکت حساب دیگر را پوشش می‌دهد. همه **NOT RUN** هستند و نتیجهٔ تاریخی تست‌ها گواه این تغییرها نیست.

صفحات ۴۹–۵۴: آزمون ارزشیابی به فیلدهای فعلی schema محدود شد؛ تست تنظیمات فارسی/English افزوده شد؛ آزمون مرحلهٔ اول ثبت‌نام، سازگاری endpoint قدیمی drop با هر دو پنجره و endpoint اختصاصی emergency-only نیز نوشته شد. آزمون‌های service/API/JS/template این checkpoint همگی **NOT RUN** هستند.

صفحهٔ ۵۵: `test_registration_status_summarizes_persisted_stages_without_claiming_final_approval` برای تعداد enrollment، بدهی پرونده، لینک مالی و نبود ادعای approval اضافه شد؛ **NOT RUN**.

صفحات ۵۶–۵۹: `test_add_drop_registration_result_is_scoped_to_an_owned_active_enrollment` اضافه شد و تست ثبت تکراری، `created=true/false` در پاسخ API را کنترل می‌کند؛ هر دو **NOT RUN** هستند.

بازبینی read-only صفحهٔ ۱۴: `GET /api/portal/pages/attendance/` برابر `200`؛ درخواست ناشناس `401` و `student_code` پروندهٔ دیگر `403`. clone یک enrollment فعال/یک attendance ثبت‌شده دارد. capture مرجع/جاری ۱۴۴۰×۹۰۰ و جاری ۳۹۰×۸۴۴ در `docs/screens/attendance.md` لینک شده‌اند. POST و suite اجرا نشدند.

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

مقایسهٔ نماینده با PDF برای صفحه‌های ۲، ۹، ۱۴، ۵۳ و ۶۳ انجام شد. هویت رنگی و shell راست‌به‌چپ قابل‌تشخیص است، ولی چیدمان و داده‌ها pixel-identical نیستند: dashboard فعلی ترکیب کارت‌ها/خلاصهٔ متفاوت دارد؛ در صفحهٔ انتخاب واحد مبالغ شهریه به‌دلیل نبود تعرفه خالی‌اند و state صفحات ۱۰–۱۳ در DB نیست؛ صفحهٔ حضور و غیاب layout تجمیعی دارد اما دادهٔ clone یک enrollment/یک attendance است؛ صفحهٔ مالی فقط دادهٔ seed موجود را نشان می‌دهد. در viewport موبایل صفحهٔ ۱۴، document width برابر viewport ماند و جدول داخل wrapper خود پیمایش شد. بنابراین وضعیت visual **جزئی و representative** است، نه پذیرش ۹۶ صفحه.

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

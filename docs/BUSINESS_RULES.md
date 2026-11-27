# فهرست قواعد و درجهٔ اطمینان

«تأییدشده در کد/آزمون» در این سند یعنی رفتار حاضر و قابل‌ردیابی در checkout؛ لزوماً تأیید مالک محصول یا آیین‌نامهٔ دانشگاه نیست. موردهای استنباط‌شده از PDF/دادهٔ نمونه، به‌عنوان قاعدهٔ قطعی محصول معرفی نمی‌شوند.

## رفتار پیاده و آزمون‌شده

| موضوع | رفتار فعلی | شواهد |
|---|---|---|
| مالکیت پروفایل | فقط Studentهایی resolve می‌شوند که `Student.person == request.user`؛ `student_code` متعلق به حساب دیگر یا ناموجود رد می‌شود. اگر چند پرونده باشد انتخاب صریح لازم است. | `accounts.services.current_student`; `test_frontend.py`; enrollment tests |
| دادهٔ صفحه | profile و term از query انتخاب‌شده/نیمسال فعال می‌آیند؛ selectorهای دانشجو به دانشجوی جاری محدودند. اعلان به Person جاری محدود است. | `frontend/views.py`; selectorهای تیمی؛ frontend tests |
| session/CSRF | session جنگو؛ نوشتن با CSRF؛ ورود با رمز hashشدهٔ `Person`؛ `UserAccount.password` منبع احراز نیست. | accounts service/tests؛ API client tests |
| قفل ورود | تنظیم پیش‌فرض پنج شکست متوالی، قفل ۹۰۰ ثانیه؛ پس از قفل/ورود موفق شمارنده reset می‌شود. | settings/accounts service/tests |
| ثبت درس | transaction و row lock؛ offering فعال، term فعال، پنجرهٔ registration یا add/drop باز، وضعیت مجاز و بدهی صفر لازم است؛ ظرفیت، پیش‌نیاز/هم‌نیاز، تداخل ساعت و سقف واحد بررسی می‌شود. | `enrollment/services.py`, `enrollment/test_services.py` |
| تکرار ثبت درس | ثبت فعال تکراری idempotent است؛ enrollment حذف‌شده می‌تواند دوباره فعال شود؛ پاسخ API 200 برای رکورد از قبل موجود/فعال‌شده و 201 برای رکورد تازه. | service/API tests |
| حذف درس | فقط enrollment متعلق به دانشجوی انتخابی؛ یکی از بازه‌های add/drop یا emergency-drop باید باز باشد؛ حذف تکراری idempotent است. | enrollment service/tests |
| فرم صفحه | هر فرم `OwnedModelForm` که `owner_field` یا `status_field` تعریف کند مالک/وضعیت را سمت سرور تعیین می‌کند؛ status اولیه باید Constant فعال `pending` داشته باشد؛ فیلد `enrollment` به پرونده/ترم جاری محدود می‌شود. | `frontend/common.py`, form definitions, frontend tests |
| اعتراض نمره | فقط Enrollment متعلق به Student/Term جاری که حداقل یک Grade با score غیرخالی دارد در فرم قابل انتخاب است؛ مهلت اعتراض یا جلوگیری از اعتراض تکراری از روی کد به‌عنوان قانون دانشگاه استنباط نمی‌شود. | `frontend/omid/forms.py`, `frontend/common.py`; آزمون نسخهٔ جدید در فاز بعد |
| نوع درخواست کارآموزی و خدمات | نوع درخواست اجباری است و باید از Constant فعال همان category باشد (`internship_request_type` یا `service_request_type`)؛ گواهی آموزشی فقط `employment_certificate` فعال را می‌پذیرد؛ وضعیت درخواست سمت سرور تعیین می‌شود. | `frontend/shahsvand/forms.py`, `frontend/common.py`; رگرسیون نوشته شد و اجرای آزمون برای فاز بعد |
| ارزشیابی استاد | پنج معیار PDF هرکدام الزامی و محدود ۱ تا ۵؛ فقط Enrollment فعالِ Student/Term جاری؛ enrollment ارزیابی‌شده read-only است و تکرار در تراکنش رد می‌شود. `overall_rating` میانگین پنج مقدار و به صحیح گرد می‌شود؛ legacy `teaching_quality`/`behavior` تغییر یا حدس‌زده نمی‌شوند. | `apps/core/frontend/miri/forms.py`, `selectors.py`, `TeacherSurvey`; migration `0006_teacher_survey_pdf_ratings` اضافه شده ولی اجرا نشده؛ regression اجرا نشده |
| جمع‌بندی حضور و غیاب | تعداد حاضر/غایب/تأخیر فقط از Attendanceهای ثبت‌شده برای enrollment فعال در پرونده و ترم انتخابی محاسبه می‌شود؛ حد مجاز غیبت یا وضعیت نزدیک‌شدن به آن محاسبه نمی‌شود. | `apps/core/frontend/niousha/selectors.py`; رگرسیون صفحه نوشته شده، اجرا نشده؛ مقررات غیبت در منبع رسمی حاضر نیست |
| گواهی/فارغ‌التحصیلی | seed فقط `employment_certificate` را برای گواهی آموزشی تعریف می‌کند؛ نوع مستقل graduation یا graduation-certificate در lookup نیست. نوع نامرتبط جایگزین نمی‌شود و write آن صفحه‌ها غیرفعال است. | `apps/core/management/commands/seed.py`, `shahsvand/forms.py`, `shahsvand/selectors.py` |
| پیام به استاد | فهرست گیرنده‌ها به حساب‌های فعال استادانی که دانشجو در کلاسشان enrollment دارد محدود است؛ sender از حساب فعال Person تعیین می‌شود. | `MessageForm` |
| اعلان | mark-read فقط با Notification ID متعلق به کاربر جاری ممکن است. | `frontend/views.py`, `test_frontend.py` |
| اطلاعیهٔ استاد | فهرست announcementها فقط از Communicationهای دارای `communication_type=announcement` و receiver حساب جاری خوانده می‌شود؛ mark-read، `is_read/read_at` و status فعال read را برای همان گیرنده ثبت می‌کند. | `miri/selectors.py`, `frontend/views.py`; مدل Communication course/term relation ندارد. |
| پرداخت | فقط رکوردهای `successful` در جمع موفق مالی لحاظ می‌شوند؛ selector دانشجو و نیمسال انتخابی را رعایت می‌کند. | `parsa/selectors.py`, financial render tests |
| درگاه/صدور | درگاه پرداخت و صدور رسمی کارت/مدرک وجود ندارند؛ صفحهٔ پرداخت امن صریحاً غیرقابل‌پرداخت است؛ serial/card/provider success جعل نمی‌شود. | Parsa selector, `portal-pdf-comparison.md`, tests |

## فرض/تصمیم فنی ثبت‌شده، نه آیین‌نامهٔ تأییدشده

| قاعده | پیاده‌سازی | چرا نیاز به تأیید دارد |
|---|---|---|
| نمرهٔ قبولی prerequisite | `PASSING_GRADE = 10` از ۲۰ | کد و ADR آن را به‌عنوان فرض ثبت می‌کنند؛ سند مقررات رسمی در checkout نیست. |
| سقف واحد مشروط | حداکثر ۱۴ واحد یا `Student.max_allowed_units`، هرکدام کمتر است. | منبع مرجع آموزشی و استثناهای مجاز در دسترس نیست. |
| تداخل امتحان | تنها امتحان با تاریخ و ساعت دقیقاً برابر، متداخل شمرده می‌شود؛ مدت/بازهٔ امتحان مدل نشده است. | زمان پایان/قاعدهٔ فاصلهٔ بین امتحان‌ها موجود نیست. |
| transition درخواست | از submitted به in_review؛ از in_review به approved/rejected؛ دادهٔ legacy pending مسیر گسترده‌تری دارد. | منبع وضعیت‌های واقعی و نقش‌های staff محصولی تأیید نشده؛ migration وضعیت‌ها صرفاً implementation را تثبیت می‌کند. |
| تعداد تلاش و session | ۵ شکست/۹۰۰ ثانیه و idle session ۹۰۰ ثانیه تنظیم پیش‌فرض‌اند. | نیاز سیاست امنیتی deployment باید تأیید شود. |
| تاریخ naive در seed/test | Django آن را در حضور `USE_TZ=True` warning می‌دهد؛ timezone کاری Asia/Tehran است، اما warning رفع نشده است. | تبدیل fixture نباید بدون شناخت معنای زمان داده انجام شود. |
| تقویم آموزشی | برای نمایش، تاریخ میلادی ذخیره‌شده به هجری شمسی تبدیل می‌شود؛ رویدادهای شخصی فقط از Term، امتحان درس فعال و Attendance همان پرونده/ترم می‌آیند. | مدل event عمومی/تعطیلات/مهلت شهریه وجود ندارد؛ افزودن یا حدس این رویدادها گمراه‌کننده است. دادهٔ seed ترم فعال 14051 در clone سال میلادی 2076 است و با تاریخ نمونهٔ PDF 1405 همخوان نیست. |

## نامشخص یا خارج از پیاده‌سازی

- اعلان حساب: `Person.is_notification_enabled` در فرم تنظیمات ذخیره می‌شود، اما سرویس/selector اعلان آن را اعمال نمی‌کند؛ مدل ترجیح مجزای چهار دسته/کانال و provider SMS/email نیز وجود ندارد. مقدار این فیلد به‌تنهایی اثبات ارسال یا خاموش‌بودن اعلان‌های جاری نیست.
- فایل مرجع رفتاری `نیازمندی_های_آموزشیار.md` که SSOT به آن ارجاع می‌دهد در checkout موجود نیست؛ ۱۵۲ شناسهٔ SDD رفتار، نقش و payload کامل را تعیین نمی‌کند.
- موارد منع بدهی/موفقیت عملیات، نتیجه‌های جداگانهٔ PDF، انتخاب چند درس و داده‌های گوناگون PDF، شناسهٔ صندلی، شماره/اعتبار رسمی کارت و خروجی گواهی معتبر در همهٔ صفحه‌ها پیاده نشده‌اند.
- تأییدکننده/امضاکنندهٔ واقعی برای هر نوع درخواست، SLA، امکان ویرایش/لغو، پیوست، audit trail، pagination، retention و سیاست حریم خصوصی پیام‌ها در منبع موجود روشن نیست.
- پرداخت آنلاین، refund واقعی، SMS/email، queue/background job، سرویس SIS بیرونی، dorm/meal، tuition installment/loan، و APIهای staff برای ۱۴ namespace خالی پیکربندی نشده‌اند.
- گزارش مغایرت مالی فقط به فرم عمومی پشتیبانی هدایت می‌کند؛ رکورد dispute، اتصال به tracking code و lifecycle بررسی/بازپرداخت در مدل/API موجود نیست.
- فرمت/تقویم نهایی تاریخ در UI و timezone هر event نیاز به منبع معتبر دارد؛ نباید با fixtureهای تاریخ ۲۰۲۶ قاعدهٔ تقویمی جدید استنباط کرد.
- حد غیبت مجاز هر درس، نحوهٔ محاسبهٔ غیبت موجه و آستانهٔ هشدار از PDF یا مدل موجود قابل تأیید نیست؛ صفحهٔ حضور و غیاب فقط سوابق ثبت‌شده را جمع می‌زند و وضعیت اخطار عددی را حدس نمی‌زند.

## شواهد تست قبلی و فاز جاری

پیش از تغییر مالکیت هفت‌گانه، checkout با `manage.py test` و Node tests اجرا شده بود؛ آن نتیجه مربوط به نسخهٔ قبلی است. کد فعلی پس از جابه‌جایی page/form هنوز تست نشده است، چون کاربر فاز تست را به بعد موکول کرده. این سند نتیجهٔ فعلی را PASS اعلام نمی‌کند؛ گزارش تاریخی در [TEST_REPORT.md](TEST_REPORT.md) و unknownهای قواعد در همین سند هستند.

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
| ارزشیابی | امتیازها محدود ۱ تا ۵؛ enrollment متعلق به دانشجو/ترم؛ ثبت تکراری برای همان enrollment رد می‌شود. | `academic_services/forms.py`, `test_frontend.py` |
| پیام به استاد | فهرست گیرنده‌ها به حساب‌های فعال استادانی که دانشجو در کلاسشان enrollment دارد محدود است؛ sender از حساب فعال Person تعیین می‌شود. | `MessageForm` |
| اعلان | mark-read فقط با Notification ID متعلق به کاربر جاری ممکن است. | `frontend/views.py`, `test_frontend.py` |
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

## نامشخص یا خارج از پیاده‌سازی

- فایل مرجع رفتاری `نیازمندی_های_آموزشیار.md` که SSOT به آن ارجاع می‌دهد در checkout موجود نیست؛ ۱۵۲ شناسهٔ SDD رفتار، نقش و payload کامل را تعیین نمی‌کند.
- موارد منع بدهی/موفقیت عملیات، نتیجه‌های جداگانهٔ PDF، انتخاب چند درس و داده‌های گوناگون PDF، شناسهٔ صندلی، شماره/اعتبار رسمی کارت و خروجی گواهی معتبر در همهٔ صفحه‌ها پیاده نشده‌اند.
- تأییدکننده/امضاکنندهٔ واقعی برای هر نوع درخواست، SLA، امکان ویرایش/لغو، پیوست، audit trail، pagination، retention و سیاست حریم خصوصی پیام‌ها در منبع موجود روشن نیست.
- پرداخت آنلاین، refund واقعی، SMS/email، queue/background job، سرویس SIS بیرونی، dorm/meal، tuition installment/loan، و APIهای staff برای ۱۴ namespace خالی پیکربندی نشده‌اند.
- فرمت/تقویم نهایی تاریخ در UI و timezone هر event نیاز به منبع معتبر دارد؛ نباید با fixtureهای تاریخ ۲۰۲۶ قاعدهٔ تقویمی جدید استنباط کرد.

## آزمون‌های پایه

رفتار baseline با `manage.py test` (۱۰۰ test) و Node client tests (۱۳ test) پاس است. این آزمون‌ها فقط رفتار مشخص‌شده در test caseها را تأیید می‌کنند و به‌جای مقررات محصول یا قرارداد سرویس بیرونی نیستند؛ جزئیات در [TEST_REPORT.md](TEST_REPORT.md) است.

# نگاشت canonical صفحات Amoozeshyar.pdf

منبع: `Amoozeshyar.pdf`، ۹۶ صفحه. هر شمارهٔ PDF دقیقاً یک ردیف دارد؛ حالت‌های crop، منو، modal و نتیجه به route والد یا «بازنمایی‌نشده» نگاشت شده‌اند. «مقایسهٔ قبلی» به screenshotهای تاریخی ۱۴۴۰×۹۰۰ اشاره می‌کند، نه capture تازه از branch ممیزی. بنابراین هیچ statusی به معنی تطبیق پیکسلی یا پذیرش responsive فعلی نیست.

وضعیت‌ها: **route موجود**، **جزء مشترک**، **state بخشی**، **بازنمایی‌نشده**. شرح implementation هر route در [docs/screens](screens/README.md) و API در [API_CONTRACTS.md](API_CONTRACTS.md) است.

| PDF | route/جزء و موضوع تصویر | وضعیت در checkout و شاهد |
|---:|---|---|
| 1 | ورود `/login/` | route موجود؛ مقایسهٔ قبلی ثبت شده، capture تازه باز است. |
| 2 | داشبورد `/` | route موجود؛ دادهٔ DB-backed؛ capture تازه باز است. |
| 3 | انتخاب نیمسال | جزء مشترک header؛ component، route مستقل ندارد. |
| 4 | گروه منوی ثبت‌نام/انتخاب واحد | metadata/sidebar مشترک؛ مقایسهٔ برش PDF قبلی است. |
| 5 | گروه منوی وضعیت مالی | metadata/sidebar مشترک؛ مقایسهٔ برش PDF قبلی است. |
| 6 | گروه منوی درخواست‌ها/مجوزها | metadata/sidebar مشترک؛ مقایسهٔ برش PDF قبلی است. |
| 7 | گروه منوی خدمات دانشجویی | metadata/sidebar مشترک؛ مقایسهٔ برش PDF قبلی است. |
| 8 | گروه منوی استادان | metadata/sidebar مشترک؛ تطبیق یک‌به‌یک برش با sidebar کامل تأیید نشده. |
| 9 | دروس انتخاب‌شده | `/portal/selected-courses/`؛ route موجود، وضعیت‌های جزئی کامل نیست. |
| 10 | state دروس انتخاب‌شده/تعداد متفاوت | route والد موجود؛ دادهٔ تصویری خاص این صفحه بازنمایی‌نشده. |
| 11 | state دروس انتخاب‌شده/جدول متفاوت | route والد موجود؛ fixture معادل این state تأیید نشده. |
| 12 | state دروس انتخاب‌شده/جمع واحد متفاوت | route والد موجود؛ state داده‌ای مستقل بازنمایی‌نشده. |
| 13 | state دروس انتخاب‌شده/جمع مالی | route والد موجود؛ محاسبهٔ PDF-specific بدون منبع داده اضافه نشده. |
| 14 | حضور و غیاب `/portal/attendance/` | route موجود؛ جدول DB-backed، مقایسهٔ قبلی؛ write کارمندی ندارد. |
| 15 | تقویم آموزشی `/portal/calendar/` | route موجود، ولی selector فقط تاریخ‌های Term را می‌دهد؛ grid/event PDF ناقص. |
| 16 | اطلاعیه استادان `/portal/announcements/` | route موجود؛ selector مشترک Notification؛ مقایسهٔ قبلی. |
| 17 | فرم ارزشیابی `/portal/evaluation-form/` | route موجود؛ form همان survey؛ مقایسهٔ قبلی. |
| 18 | مرکز اعلان‌ها `/portal/notifications/` | route موجود؛ list و mark-read؛ مقایسهٔ قبلی. |
| 19 | تنظیمات `/portal/settings/` | route موجود؛ ذخیرهٔ Person؛ مقایسهٔ قبلی. |
| 20 | کارت دانشجویی `/portal/student-card/` | قالب اختصاصی و render test؛ سریال/اعتبار رسمی ساخته نمی‌شود؛ capture تازه باز. |
| 21 | کارت امتحان `/portal/exam-card/` | قالب اختصاصی و render test؛ شمارهٔ صندلی/صدور رسمی وجود ندارد؛ capture تازه باز. |
| 22 | برنامه هفتگی `/portal/schedule/` | route موجود و print مرورگر؛ مقایسهٔ قبلی. |
| 23 | چارت درسی `/portal/curriculum/` | route موجود و data-backed؛ مقایسهٔ قبلی. |
| 24 | کارآموزی `/portal/internship/` | route و فرم DB-backed؛ مقایسهٔ قبلی؛ lifecycle کامل نامعلوم. |
| 25 | درخواست مهمانی `/portal/guest-request/` | route/form موجود؛ مقایسهٔ قبلی. |
| 26 | فراغت از تحصیل `/portal/graduation/` | route/form request موجود؛ تأیید رسمی نیست؛ مقایسهٔ قبلی. |
| 27 | ارتباط با استاد `/portal/messages/` | route/form Communication موجود؛ مقایسهٔ قبلی. |
| 28 | راهنمای سامانه `/portal/guide/` | route shell موجود، محتوای Q&A در selector موجود نیست؛ gap باز. |
| 29 | مرکز پشتیبانی `/portal/support/` | route/form Ticket موجود؛ lifecycle پشتیبانی کامل نیست؛ مقایسهٔ قبلی. |
| 30 | منع عملیات به علت بدهی | state مستقل بازنمایی‌نشده؛ بدهی API ثبت‌نام را رد می‌کند، ولی route/result مخصوص این PDF نیست. |
| 31 | فرم ارزشیابی استاد | همان `/portal/evaluation-form/`؛ route موجود. |
| 32 | ارزشیابی برای درس دیگر | form route مشترک؛ dataset/state جداگانهٔ این PDF بازنمایی‌نشده. |
| 33 | ارزشیابی برای درس دیگر | form route مشترک؛ dataset/state جداگانه بازنمایی‌نشده. |
| 34 | فهرست ارزشیابی `/portal/evaluation/` | route موجود؛ حالت داده‌ای PDF به fixture مستقل نگاشت نشده. |
| 35 | state دوم فهرست ارزشیابی | route والد موجود؛ نتیجهٔ مستقل بازنمایی‌نشده. |
| 36 | state سوم فهرست ارزشیابی | route والد موجود؛ نتیجهٔ مستقل بازنمایی‌نشده. |
| 37 | state چهارم فهرست ارزشیابی | route والد موجود؛ نتیجهٔ مستقل بازنمایی‌نشده. |
| 38 | نتیجهٔ عملیات | route نتیجه وجود ندارد؛ API عملیات فقط payload/status بازمی‌گرداند و browser reload می‌کند. |
| 39 | نتیجهٔ عملیات | state مستقل PDF بازنمایی‌نشده. |
| 40 | نتیجهٔ عملیات | state مستقل PDF بازنمایی‌نشده. |
| 41 | نتیجهٔ عملیات | state مستقل PDF بازنمایی‌نشده. |
| 42 | نتیجهٔ عملیات | state مستقل PDF بازنمایی‌نشده. |
| 43 | نتیجهٔ عملیات | state مستقل PDF بازنمایی‌نشده. |
| 44 | نتیجهٔ عملیات | state مستقل PDF بازنمایی‌نشده. |
| 45 | نتیجهٔ عملیات | state مستقل PDF بازنمایی‌نشده. |
| 46 | نتیجهٔ عملیات | state مستقل PDF بازنمایی‌نشده. |
| 47 | نتیجهٔ عملیات | state مستقل PDF بازنمایی‌نشده. |
| 48 | نتیجهٔ عملیات | state مستقل PDF بازنمایی‌نشده. |
| 49 | مقیاس پاسخ ارزشیابی | کنترل‌های ۱–۵ در route فرم هستند؛ crop مستقل/طراحی دقیق پیاده و ثبت نشده. |
| 50 | toggle اعلان | فیلد در `/portal/settings/` است؛ crop مستقل وجود ندارد. |
| 51 | انتخاب زبان | فیلد در `/portal/settings/` است؛ crop مستقل وجود ندارد. |
| 52 | شروع انتخاب واحد `/portal/enrollment/` | route و دادهٔ پرونده/term موجود؛ render test؛ screenshot تازه باز. |
| 53 | حذف و اضافه `/portal/add-drop/` | route و حذف واقعی موجود؛ success state مستقل PDF نیست. |
| 54 | حذف اضطراری `/portal/emergency-drop/` | route موجود؛ همان service حذف و بررسی هرکدام از دو window. |
| 55 | آخرین وضعیت ثبت‌نام `/portal/registration-status/` | route موجود؛ render smoke؛ visual review قبلی ناتمام. |
| 56 | نتیجهٔ موفق حذف/اضافه | result URL/view مستقل ندارد؛ state بازنمایی‌نشده. |
| 57 | نتیجهٔ موفق حذف/اضافه | state بازنمایی‌نشده؛ دادهٔ مستقل ساخته نشده. |
| 58 | نتیجهٔ موفق حذف/اضافه | state بازنمایی‌نشده؛ دادهٔ مستقل ساخته نشده. |
| 59 | نتیجهٔ موفق حذف/اضافه | state بازنمایی‌نشده؛ دادهٔ مستقل ساخته نشده. |
| 60 | اعتراض نمره `/portal/grade-appeal/` | route/form موجود؛ قواعد مهلت/مدرک در source نیست؛ visual review قبلی ناتمام. |
| 61 | فعالیت آموزشی `/portal/academic-activities/` | selector/template اختصاصی و render test؛ screenshot تازه باز. |
| 62 | کارنامه `/portal/transcript/` | route موجود؛ نمره‌های DB؛ visual review قبلی ناتمام. |
| 63 | پرداخت‌ها `/portal/payments/` | template/selector مالی موجود؛ موفق‌ها از failed جدا؛ screenshot تازه باز. |
| 64 | پرداخت امن `/portal/secure-payment/` | route موجود؛ نبود gateway صریح؛ تراکنش/موفقیت شبیه‌سازی نمی‌شود. |
| 65 | تسهیلات `/portal/financial-aid/` | فرم مدل موجود؛ مبلغ/حساب/پیوست PDF در schema نیست. |
| 66 | شهریه `/portal/tuition/` | aggregate پرداخت‌های موفق موجود؛ line item نوع شهریه مدل نشده. |
| 67 | درخواست‌ها `/portal/requests/` | route/form عمومی موجود؛ معادل تمام workflowهای PDF نیست. |
| 68 | state حذف‌و‌اضافه با دادهٔ دیگر | route والد موجود؛ data set PDF-specific بازنمایی‌نشده. |
| 69 | state حذف‌و‌اضافه با دادهٔ دیگر | route والد موجود؛ data set PDF-specific بازنمایی‌نشده. |
| 70 | state حذف‌و‌اضافه با دادهٔ دیگر | route والد موجود؛ data set PDF-specific بازنمایی‌نشده. |
| 71 | state حذف‌و‌اضافه با دادهٔ دیگر | route والد موجود؛ data set PDF-specific بازنمایی‌نشده. |
| 72 | مدرک آموزشی `/portal/education-certificate/` | form request موجود؛ صدور/تحویل رسمی نیست. |
| 73 | مدرک دانش‌آموختگی `/portal/graduation-certificate/` | همان schema certificate؛ تفکیک semantic در DB وجود ندارد. |
| 74 | فهرست ارزشیابی `/portal/evaluation/` | route موجود؛ حالت داده‌ای مستقل با صفحهٔ ۳۴ یکی است. |
| 75 | نتیجهٔ حذف اضطراری | result route مستقل ندارد؛ state بازنمایی‌نشده. |
| 76 | نتیجهٔ حذف اضطراری | state بازنمایی‌نشده؛ تنها API/service status موجود است. |
| 77 | نتیجهٔ حذف اضطراری | state بازنمایی‌نشده؛ دادهٔ مستقل ساخته نشده. |
| 78 | نتیجهٔ حذف اضطراری | state بازنمایی‌نشده؛ دادهٔ مستقل ساخته نشده. |
| 79 | فهرست درس در مودال انتخاب | modal مستقل در UI جاری نیست؛ offerings در جدول `selected-courses` آمده‌اند. |
| 80 | جزئیات گروه/درس | modal و data state مستقل پیاده نیست؛ route والد `selected-courses`. |
| 81 | جزئیات گروه/درس | state گروه PDF بازنمایی‌نشده. |
| 82 | جزئیات گروه/درس | state گروه PDF بازنمایی‌نشده. |
| 83 | جزئیات گروه/درس | state گروه PDF بازنمایی‌نشده. |
| 84 | فهرست درس در مودال انتخاب | همان page 79؛ modal مستقل پیاده نیست. |
| 85 | جزئیات گروه/درس | state گروه PDF بازنمایی‌نشده. |
| 86 | جزئیات گروه/درس | state گروه PDF بازنمایی‌نشده. |
| 87 | جزئیات گروه/درس | state گروه PDF بازنمایی‌نشده. |
| 88 | جزئیات گروه/درس | state گروه PDF بازنمایی‌نشده. |
| 89 | تأیید حذف عادی | modal واقعی داخل `/portal/add-drop/`; ظاهر چهار variation نیاز به visual check تازه دارد. |
| 90 | تأیید حذف عادی | همان component/route؛ API فقط پس از confirm فراخوانی می‌شود. |
| 91 | تأیید حذف عادی | همان component؛ تفاوت داده از ردیف enrollment جاری. |
| 92 | تأیید حذف عادی | همان component؛ screenshot viewport فعلی موجود نیست. |
| 93 | تأیید حذف اضطراری | modal واقعی داخل `/portal/emergency-drop/`; service همان endpoint مشترک را می‌زند. |
| 94 | تأیید حذف اضطراری | همان component؛ نوع حذف در payload از هم جدا نشده. |
| 95 | تأیید حذف اضطراری | state/رنگ/متن variation نیاز به capture فعلی دارد. |
| 96 | تأیید حذف اضطراری | همان component؛ result مستقل بعد از confirm پیاده نیست. |

## اختلاف inventory تصویر و محدودیت بازبینی

سند قبلی `docs/portal-pdf-comparison.md` ۵۸ حالت رابط ثبت‌شده را گزارش می‌کند و پوشهٔ موقت ۷۵ screenshot دارد؛ تعریف این دو شمارش یکسان نیست. ۹۶ تصویر مرجع PDF در contact sheet مرور شدند، اما screenshot تازهٔ checkout فعلی در viewportهای `1920×1080`, `1536×864`, `1366×768`, `1280×720`, `1024×768`, `768×1024`, `390×844` در این checkpoint ثبت نشده است. پس وضعیت responsive/visual برای همهٔ صفحات «تأیید نهایی» نیست.

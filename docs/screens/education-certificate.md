# درخواست مدرک آموزشی

- مالک/route: Shahsvand؛ `/portal/education-certificate/`; shared `core/live_content.html`; `shahsvand.forms.CertificateForm`.
- مرجع: PDF صفحهٔ ۷۲ و نتیجهٔ ثبت درخواست در صفحهٔ ۴۵.
- هدف/کنترل: ارسال و پیگیری درخواست از مسیر StudentServiceRequest؛ UI نشان می‌دهد مخاطب/نسخه/روش تحویل در schema نیست و این workflow صدور مدرک نیست.
- داده/API: StudentServiceRequest و Constant فعال `service_request_type/employment_certificate`; GET/POST API صفحه فقط در صورت وجود lookup فعال؛ redirect موفق دارای `request_id` است و نتیجه را از رکورد همان Student می‌خواند.
- اعتبارسنجی/مجوز: owner/status سروری؛ `service_request_kind` اجباری و فقط type فعال `employment_certificate` از server قابل انتخاب است.
- خطا/محدودیت: صفحهٔ ۴۵ ثبت درخواست را تأیید می‌کند، نه صدور مدرک. مخاطب، تعداد نسخه و روش تحویل در schema نیستند؛ فایل/قالب/امضای مدرک یا صدور PDF رسمی وجود ندارد؛ برای مدرک معتبر باید به سامانهٔ رسمی مراجعه کرد.
- navigation: گروه درخواست/مجوز؛ وضعیت تصمیم در جدول درخواست.
- آزمون/وابستگی: `test_request_types_are_required_and_certificate_request_is_not_issuance` در `apps/core/test_frontend.py` validation و نتیجهٔ غیررسمی را پوشش می‌دهد؛ نوشته شده و اجرا نشده. CertificateForm و ServiceRequestForm.
- وضعیت: PDF صفحهٔ ۷۲ با lookup فعال و فرم محدود واقعی تطبیق شد؛ مخاطب/تعداد نسخه/تحویل و صدور رسمی gap هستند و جلوی فرم آشکارند. regression به‌روزرسانی شده ولی اجرا نشده؛ capture جاری احرازشده نداریم.

# ارتباط با استادان

- مالک/route: Shahsavand؛ `/portal/messages/`; shared `core/live_content.html`; `MessageForm`.
- مرجع: PDF صفحهٔ ۲۷.
- هدف/کنترل: فهرست مکاتبات و فرم انتخاب استاد، موضوع و متن پیام.
- داده/API: Communication, UserAccount, Person, Enrollment؛ GET/POST API صفحه.
- اعتبارسنجی/مجوز: گیرنده فقط account فعال استادانِ مرتبط با enrollmentهای دانشجو؛ sender از UserAccount فعال خود Person؛ session و ownership.
- خطا/محدودیت: فرم/DB errors مشترک؛ ارسال واقعی SMS/email یا تحویل خارجی وجود ندارد؛ رکورد Communication صرفاً DB message است.
- navigation: sidebar خدمات دانشجویی؛ history بر اساس sender/receiver حساب جاری.
- آزمون/وابستگی: `apps/core/test_frontend.py`; `academic_services/forms.py`, model Communication.
- وضعیت: نوشتن DB-backed؛ read/unread یا status workflow در UI غایب؛ screenshot تازه باز.

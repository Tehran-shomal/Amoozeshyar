# خلاصهٔ مالی نیمسال‌ها

- مالک/route: Parsa؛ `/portal/tuition/`; `parsa/finance.html`; Parsa selector.
- مرجع: PDF صفحهٔ ۶۶.
- هدف/کنترل: خلاصهٔ پرداخت موفق و بدهی پرونده؛ جمع پرداخت‌های موفق هر term؛ لینک به پرداخت مانده و سوابق تراکنش.
- داده/API: Payment, Term, Student, Constant؛ GET API صفحه؛ `tuition_rows` همهٔ termها را جمع می‌کند حتی وقتی یک term برای summary انتخاب شده باشد.
- نوشتن/اعتبارسنجی: read-only؛ payment ایجاد/تسویه نمی‌کند.
- دسترسی/خطا: session و Student جاری؛ مقدار missing صفر/— با قرارداد صفحه؛ DB error مشترک. تعرفهٔ شهریهٔ ثابت/متغیر و breakdown بدهی مدل نشده و به‌صورت هشدار روشن است؛ مبالغ موجود مثل بقیهٔ portal به ریال نمایش داده می‌شوند و تبدیل واحد از PDF تومان حدس زده نمی‌شود.
- navigation: payments/secure-payment؛ term picker برای summary مشترک است.
- آزمون/وابستگی: `apps/core/test_frontend.py`; Parsa selector، ORM aggregate.
- وضعیت: مرجع صفحهٔ ۶۶ با summary و ledger مقایسه شد؛ داده فقط بدهی پرونده و جمع پرداخت موفق را پشتیبانی می‌کند، نه تعرفه/اقلام. لینک‌ها به صفحات موجود وصل شدند؛ regression نوشته، اجرا نشده؛ capture جاری احرازشده نداریم.

# خلاصهٔ مالی نیمسال‌ها

- مالک/route: Parsa؛ `/portal/tuition/`; `parsa/finance.html`; Parsa selector.
- مرجع: PDF صفحهٔ ۶۶.
- هدف/کنترل: جمع پرداخت‌های successful بر حسب term و بدهی ثبت‌شده در پرونده.
- داده/API: Payment, Term, Student, Constant؛ GET API صفحه؛ `tuition_rows` همهٔ termها را جمع می‌کند حتی وقتی یک term برای summary انتخاب شده باشد.
- نوشتن/اعتبارسنجی: read-only؛ payment ایجاد/تسویه نمی‌کند.
- دسترسی/خطا: session و Student جاری؛ مقدار missing صفر/— با قرارداد صفحه؛ DB error مشترک.
- navigation: payments/secure-payment؛ term picker برای summary مشترک است.
- آزمون/وابستگی: `apps/core/test_frontend.py`; Parsa selector، ORM aggregate.
- وضعیت: گزارش aggregate بر دادهٔ موجود؛ دسته‌بندی tuition/line items PDF در مدل وجود ندارد؛ screenshot تازه باز.

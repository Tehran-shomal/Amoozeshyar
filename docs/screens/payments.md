# سوابق پرداخت

- مالک/route: Parsa؛ `/portal/payments/`; `parsa/finance.html`; Parsa selector.
- مرجع: PDF صفحهٔ ۶۳.
- هدف/کنترل: خلاصهٔ پرداخت موفق/بدهی، جدول تراکنش‌های ثبت‌شده و statusها.
- داده/API: Payment, Term, Student, Constant؛ GET API صفحه؛ paymentهای student انتخابی، term انتخابی (یا همه اگر term null).
- نوشتن/اعتبارسنجی: read-only؛ هیچ تراکنشی از UI ساخته نمی‌شود.
- مجوز/خطا: session و student-scoped؛ failed transaction در جمع successful لحاظ نمی‌شود؛ DB errors مشترک.
- navigation: secure-payment برای توضیح بدهی، support برای گزارش مغایرت؛ این لینک‌ها خودشان gateway نیستند.
- آزمون/وابستگی: `apps/core/test_frontend.py`؛ `parsa/selectors.py`, finance template و Payment.
- وضعیت: read واقعی؛ gateway/تسویه/رسید بیرونی نیست؛ screenshot پس از تغییرها و viewport QA باز.

# سوابق پرداخت

- مالک/route: Parsa؛ `/portal/payments/`; `parsa/finance.html`; Parsa selector.
- مرجع: PDF صفحهٔ ۶۳.
- هدف/کنترل: خلاصهٔ پرداخت موفق/بدهی و جدول شناسه، شرح، تاریخ، مبلغ و وضعیت برای تراکنش‌های همان پرونده/نیمسال.
- داده/API: Payment, Term, Student, Constant؛ GET API صفحه؛ paymentهای student انتخابی، term انتخابی (یا همه اگر term null).
- نوشتن/اعتبارسنجی: read-only؛ هیچ تراکنشی از UI ساخته نمی‌شود.
- مجوز/خطا: session و student-scoped؛ failed transaction در جمع successful لحاظ نمی‌شود؛ DB errors مشترک. `Payment` فیلد شرح ندارد، پس ستون PDF با متن ثابت و شفاف «شرح در مدل پرداخت ثبت نشده» پر می‌شود؛ term از عنوان جدول/خلاصه مشخص است.
- navigation: secure-payment برای توضیح بدهی، support برای گزارش مغایرت؛ لینک پشتیبانی فقط تیکت عمومی است و PaymentDispute/ارتباط ticket با tracking code مدل نشده.
- آزمون/وابستگی: `apps/core/test_frontend.py`؛ `parsa/selectors.py`, finance template و Payment.
- وضعیت: ستون‌های جدول با مرجع PDF تطبیق داده شد؛ جمع موفق از failed جداست و آزمون مالکیت/مبلغ/شرح به‌روزرسانی شد ولی اجرا نشده. capture جاری احرازشده و viewport QA موجود نیست؛ gateway/تسویه/رسید بیرونی هم وجود ندارد.

# پرداخت امن

- مالک/route: Parsa؛ `/portal/secure-payment/`; `parsa/finance.html`; Parsa selector.
- مرجع: PDF صفحهٔ ۶۴؛ منع عملیات به‌علت بدهی در صفحهٔ ۳۰ state جداگانه و پیاده‌نشده است.
- هدف/کنترل: نمایش مانده و توضیح صریح نبود درگاه؛ لینک به سوابق پرداخت/تسهیلات.
- داده/API: Student و Payment برای summary؛ GET API صفحه؛ نوشتن ندارد.
- اعتبارسنجی/مجوز: session و student جاری؛ پرداخت در این route شروع نمی‌شود.
- خطا/محدودیت: no gateway/provider؛ فرم کارت، کسر مبلغ، token، تراکنش یا موفقیت ساختگی وجود ندارد؛ page 30 denial flow مستقل ندارد.
- navigation: `payments`, `financial-aid`؛ بازگشت از shell.
- آزمون/وابستگی: `apps/core/test_frontend.py`; Parsa selector/finance template.
- وضعیت: محدودیت امن و واقعی نشان داده می‌شود؛ پرداخت آنلاین «پیاده‌شده» نیست؛ viewport تازه باز.

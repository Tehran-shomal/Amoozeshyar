# پرداخت امن

- مالک/route: Parsa؛ `/portal/secure-payment/`; `parsa/finance.html`; Parsa selector.
- مرجع: PDF صفحهٔ ۶۴؛ منع عملیات به‌علت بدهی در صفحهٔ ۳۰ state جداگانه و پیاده‌نشده است.
- هدف/کنترل: پیش‌نمایش read-only مبلغ مانده، شرح کلی پرونده، پرداخت‌کننده و وضعیت درگاه؛ ادامه پرداخت تا اتصال gateway غیرفعال و سوابق پرداخت در دسترس است.
- داده/API: Student و Payment برای summary؛ GET API صفحه؛ نوشتن ندارد.
- اعتبارسنجی/مجوز: session و student جاری؛ پرداخت در این route شروع نمی‌شود.
- خطا/محدودیت: no gateway/provider؛ هیچ شماره کارت، bank account، token، تراکنش یا موفقیتی ساخته/گرفته نمی‌شود؛ شرح فقط متن کلی است چون Payment model پرداختی در انتظار ندارد؛ مبلغ بدهی از Student است و به نیمسال خاص نسبت داده نمی‌شود؛ page 30 denial flow مستقل ندارد.
- navigation: `payments`؛ بازگشت از shell. مسیر تسهیلات در منوی خودش باقی است.
- آزمون/وابستگی: `apps/core/test_frontend.py`; Parsa selector/finance template.
- وضعیت: چیدمان مرجع با preview واقعی پرونده بازسازی شد؛ کنترل ادامه disabled است و API write ندارد. regression با بدهی/پرداخت صفر و عدم وجود input بانکی نوشته شد، اجرا نشده؛ capture جاری احرازشده در دسترس نیست.

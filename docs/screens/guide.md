# راهنمای سامانه

- مالک/route: Omid؛ `/portal/guide/`; `core/live_content.html`; selector فعلی به fallback notice می‌رسد.
- مرجع: PDF صفحهٔ ۲۸.
- هدف/کنترل مرجع: کارت‌های سؤال‌وپاسخ راهنمایی؛ اما در کد فعلی راهنمای محتوایی، accordion یا navigation راهنما پیدا نشد.
- داده/API: متن ثابت notice در selector؛ GET API صفحه؛ مدل یا فرم guide ندارد.
- اعتبارسنجی/مجوز: session لازم؛ PortalView آن را برای حساب بدون Student نیز render می‌کند.
- خطا/navigation: خطای API مشترک؛ sidebar و linkهای عمومی پرتال.
- آزمون/وابستگی: `apps/core/test_frontend.py` smoke؛ Omid selector و shared live-content.
- وضعیت: gap بازتولیدشدنی نسبت به PDF؛ متن رسمی راهنما/رویه‌ها در منابع موجود نیست، بنابراین محتوا حدس زده نشده و این صفحه کامل نیست.

# ناوبری و پوستهٔ پرتال

- مالک: metadata/registry مشترک پنج گروه؛ `apps/core/frontend/metadata.py`, `registry.py`, `portal_base.html`, `static/core/live_portal.js`.
- مرجع: PDF صفحات ۴–۸ (برش گروه منو؛ تطبیق یک‌به‌یک با sidebar کامل قطعی نیست).
- هدف/کنترل‌ها: گروه‌بندی ۳۲ صفحه، جست‌وجوی لینک‌ها، باز/بسته‌کردن sidebar در موبایل، breadcrumb/وضعیت صفحه و خروج.
- داده/API: menu static از registry؛ صفحهٔ فعال از path؛ logout با `POST /api/accounts/logout/` و CSRF؛ shell داده را از API صفحه می‌گیرد.
- ورودی/اعتبارسنجی: slug فقط وقتی در `PAGES` ثبت و یکتا باشد resolve می‌شود؛ `selected-courses` و `evaluation-form` از navigation اصلی hidden هستند.
- مجوز/خطا: همهٔ portal routes session می‌خواهند؛ API unauthenticated JSON 401؛ link به route نامعتبر 404.
- مسیر: لینک‌های منو/quick actions بین routeهای ثبت‌شده؛ logout session را پاک و به login هدایت می‌کند.
- آزمون/وابستگی: `apps/core/test_architecture.py`, `apps/core/test_frontend.py`, `static/core/tests/portal_bindings.test.cjs`; registry و API client.
- وضعیت: navigation، search و mobile toggle پیاده‌اند؛ pixel/keyboard audit کامل در ۷ viewport هنوز انجام نشده.

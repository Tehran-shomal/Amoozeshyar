# ناوبری و پوستهٔ پرتال

- مالک: پوسته/منوی محصول مشترک؛ مالکیت routeها در هفت ماژول `apps/core/frontend/registry.py` است. دسته‌بندی `NAV_GROUPS` کاربرد محصولی دارد و مرجع مالکیت تیمی نیست.
- مرجع: cropهای منوی PDF در صفحات ۴ تا ۸؛ نگاشت کامل گروه‌ها در [navigation-groups.md](navigation-groups.md) و [PDF_PAGE_MAPPING.md](../PDF_PAGE_MAPPING.md).
- دادهٔ گروه در `apps/core/frontend/metadata.py`; ساختار در `apps/core/templates/core/portal_base.html`; ظاهر/بازوبسته‌شدن در `static/core/portal.css` و `static/core/live_portal.js` است. sidebar از API فهرست نمی‌گیرد؛ مقصدها به API همان صفحه متصل‌اند.
- گروه‌های فعال مطابق PDF: «سیستم دروس دانشجو» (۱۳ مقصد)، «خدمات مالی» (۴)، «درخواست مجوز» (۵)، «خدمات دانشجویی» (۵) و «اساتید» (۳). این تغییر فقط جایگاه و عنوان منو را عوض می‌کند؛ route و owner هر صفحه ثابت می‌ماند.
- هر گروه دو کپسول عنوان هم‌نام دارد؛ کپسول راست با `<summary>` باز/بسته می‌شود، کپسول چپ صرفاً نمایشی و `aria-hidden` است. لینک‌های داخل گروه plain و بدون کارت/هایلایت ردیف فعال‌اند تا با نمونهٔ PDF هم‌خوان شوند. تنظیمات فقط یک‌بار در گروه خدمات دانشجویی آمده و از footer حذف شده است.
- نمونهٔ احراز‌شده: `/portal/enrollment/` و `GET /api/portal/pages/enrollment/`. مسیرها و APIهای نمونه با session پاسخ `200`؛ route ناشناس `302` به ورود و API ناشناس `401` می‌دهد. API صفحه مشترک است؛ slug ثبت‌نشده `404` می‌دهد.
- `selected-courses` و `evaluation-form` از منوی اصلی پنهان‌اند، ولی group metadata آن‌ها برای بازشدن گروه والد نگه داشته می‌شود. خروج با `POST /api/accounts/logout/` و CSRF انجام می‌شود.
- آزمون خودکار `apps/core/test_architecture.py`, `apps/core/test_frontend.py`, `static/core/tests/portal_bindings.test.cjs` طبق خواستهٔ کاربر به فاز بعد موکول است؛ تطبیق viewport و حالت keyboard نیز هنوز باز است.
- وضعیت: صفحات منوی ۴ تا ۸ بازبینی شدند و دسته‌بندی/ظاهر مشترک مطابق مرجع اصلاح شد؛ تطبیق پیکسلی و ارزیابی همهٔ viewportها ادعا نمی‌شود.

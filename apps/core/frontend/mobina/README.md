# مبینا — ورود و چارچوب مشترک

مالک ورود `/login/`، داشبورد `/`، تنظیمات حساب `/portal/settings/` و کارت دیجیتال `/portal/student-card/` است. انتخاب واحد و چارت طبق تقسیم جدید به Shaghayegh و Omid تعلق دارند.

- `pages.py`: تنظیمات و کارت دیجیتال؛ `SPECIAL_PAGES`: login/dashboard.
- `selectors.py` و `forms.py`: تنظیمات Person حساب جاری و نمایش پیش‌نمایش کارت Student؛ زبان از lookup موجود انتخاب می‌شود.
- `templates/mobina/settings.html`: صفحهٔ PDF ۱۹. فقط فیلدهای ذخیره‌شوندهٔ فعلی حساب را می‌فرستد؛ شمارهٔ موبایل و تنظیم تفکیکی SMS/email در schema/provider حاضر نیستند و به‌صورت محدودیت نشان داده می‌شوند.
- `static/mobina/login.js`: اتصال فرم ورود به Accounts API.
- `templates/mobina/`: home، login و student card.
- داشبورد: `GET /api/portal/pages/home/`; تنظیمات: GET/POST `/api/portal/pages/settings/`; کارت: GET `/api/portal/pages/student-card/`; session: `/api/accounts/`.
- [ارائهٔ مبینا](../../../../docs/presentation/01_Mobina.md) · [ماتریس صفحه/API](../../../../docs/SCREEN_API_MATRIX.md).

کارت نمایش‌داده‌شده صرفاً پیش‌نمایش است؛ serial/صدور رسمی ساخته نمی‌شود. پوستهٔ مشترک در `apps/core/templates/core/` و `static/core/` نگهداری می‌شود.

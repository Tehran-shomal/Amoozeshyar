# درخواست مجوز — صفحهٔ ۶ PDF

- مرجع PDF: [page 06](page-06-reference.png)، ۵۳۲×۲۷۸.
- وضعیت جاری: [برش واقعی از route احراز‌شده](page-06-current.png)، همان viewport؛ HTML گروه از `GET /portal/requests/` استخراج شده است.
- PDF و منوی اصلاح‌شده هر دو عنوان «درخواست مجوز» و پنج مقصد یکسان دارند. پوسته اکنون دو کپسول هم‌نام دارد؛ control راست باز/بسته می‌کند و فهرست plain زیر آن نمایش داده می‌شود. مالکیت شاهسوند مستقل از این گروه محصولی باقی می‌ماند.

## Route، مالکیت و API

هر پنج لینک در `apps/core/frontend/metadata.py` به یک route واقعی می‌رسند. همه در `apps/core/frontend/shahsvand/pages.py` مالکیت شاهسوند دارند:

| slug | route | API GET | رفتار خواندن/نوشتن در source |
|---|---|---|---|
| `requests` | `/portal/requests/` | `/api/portal/pages/requests/` | فهرست درخواست‌های دانشجو و فرم عمومی نوع درخواست فعال |
| `education-certificate` | `/portal/education-certificate/` | `/api/portal/pages/education-certificate/` | فقط lookup فعال `employment_certificate`؛ اگر موجود نباشد فرم ارسال حذف می‌شود |
| `graduation-certificate` | `/portal/graduation-certificate/` | `/api/portal/pages/graduation-certificate/` | به‌علت نبود نوع معتبر/فرایند رسمی، اطلاع‌رسانی و جدول خالی؛ write جایگزین جعل نمی‌شود |
| `guest-request` | `/portal/guest-request/` | `/api/portal/pages/guest-request/` | فرم و تاریخچهٔ درخواست همان دانشجو؛ وضعیت سمت سرور |
| `graduation` | `/portal/graduation/` | `/api/portal/pages/graduation/` | خواندن audit موجود؛ نوع معتبر ثبت درخواست تعریف نشده و این صفحه write نمی‌کند |

`GET` هر پنج route و API در TestClient احراز‌شده پاسخ `200` داد و payload هر API کلیدهای `page`, `html`, `profile`, `term` داشت. نشست موقت signed-cookie بود و signal به‌روزرسانی last-login در زمان force-login قطع شد. `POST` اجرا نشد؛ `forms.py`, `selectors.py` و مرز generic `portal_page_api` بازبینی شدند. در API عمومی، احراز هویت لازم است؛ anonymous GET برای endpointهای صفحه `401` می‌دهد.

## تصمیم مشترک ظاهر

گروه/قالب منوی مشترک پس از مرور صفحات ۴ تا ۸ اصلاح شد؛ جزئیات گروه نهایی در [navigation-groups.md](navigation-groups.md) است. آزمون خودکار بنا به درخواست کاربر اجرا نشده است.

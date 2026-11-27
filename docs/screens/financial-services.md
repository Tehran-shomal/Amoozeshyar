# امور مالی و منوی صفحهٔ ۵

- مرجع: [برش صفحهٔ ۵ PDF](page-05-reference.png)، ۵۳۲×۲۲۸ پیکسل.
- جاری: [گروه واقعی از HTML احراز‌شدهٔ `/portal/payments/`](page-05-current.png)، در viewport برابر ۵۳۲×۲۲۸؛ از route جاری جدا شد، نه از mock.
- PDF یک گروه محصولی با عنوان «خدمات مالی» و چهار مقصد نشان می‌دهد: مدیریت پرداخت‌ها، پرداخت امن، پیگیری تسهیلات و مدیریت مالی نیمسال‌ها.
- گروه فعلی پس از اصلاح `apps/core/frontend/metadata.py` دقیقاً «خدمات مالی» با چهار مقصد PDF است؛ مقصدهای آموزشی از این گروه خارج شده‌اند. دو کپسول عنوان و لینک‌های ساده نیز در پوسته پیاده شده‌اند.
- مالک workflowهای مالی در `apps/core/frontend/registry.py` و manifest `apps/core/frontend/parsa/pages.py` پارساست؛ این مالکیت تیمی با دسته‌بندی محصولی sidebar یکی نیست.

## مسیر و API

| مقصد | route | API | رفتار |
|---|---|---|---|
| سوابق پرداخت | `/portal/payments/` | `GET /api/portal/pages/payments/` | پرداخت‌های پروندهٔ انتخاب‌شده و نیمسال؛ جمع موفق‌ها جدا از تراکنش ناموفق |
| پرداخت امن | `/portal/secure-payment/` | `GET /api/portal/pages/secure-payment/` | ماندهٔ ثبت‌شده و اعلام نبود درگاه؛ پرداختی ثبت یا کسر نمی‌شود |
| تسهیلات | `/portal/financial-aid/` | GET/POST همان API | فرم `ScholarshipForm`؛ پرونده و وضعیت ثبت از سمت سرور کنترل می‌شود |
| مالی نیمسال‌ها | `/portal/tuition/` | `GET /api/portal/pages/tuition/` | مجموع پرداخت‌های موفق به تفکیک نیمسال |

`apps/core/frontend/parsa/selectors.py` پرداخت‌ها را به `Student` انتخاب‌شده محدود می‌کند؛ ردیف‌های سوابق پرداخت با فیلتر پرونده و term خوانده می‌شوند. جمع فقط status با کد `successful` را لحاظ می‌کند. فرم تسهیلات از `OwnedModelForm` استفاده می‌کند. API صفحه در `apps/core/frontend/api.py` پیش از خواندن session را لازم می‌داند.

## شاهد و موارد باز

- نشست TestClient با signed-cookie session و `update_last_login` جداشده فقط برای GET ساخته شد؛ `ALLOWED_HOSTS` در همان پردازش تشخیصی تنظیم شد چون clone `.env` ندارد. route احراز‌شده و APIهای `payments`, `secure-payment`, `financial-aid`, `tuition` همگی `200` دادند؛ هر API payload دارای `page`, `html`, `profile`, `term` داشت. هیچ POST یا تغییر رکوردی انجام نشد.
- روی سرور محلی، درخواست ناشناس به `/api/portal/pages/payments/` پاسخ `401 authentication_required` داد و route مرورگر `/portal/payments/` به ورود `302` داد.
- پس از مرور صفحات ۶ تا ۸، عنوان/اعضای گروه مشترک تغییر کرد؛ مالکیت پارسا در manifest و APIها ثابت ماند. نتیجهٔ نهایی گروه‌ها در [navigation-groups.md](navigation-groups.md) ثبت شده است.
- آزمون خودکار طبق خواستهٔ کاربر اجرا نشده است؛ APIها در GET احراز‌شده و ناشناس read-only بررسی شده‌اند.

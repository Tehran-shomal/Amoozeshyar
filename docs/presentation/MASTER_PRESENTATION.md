# ارائهٔ یکپارچهٔ آموزشیار — نسخهٔ مالکیت هفت‌گانه

## وضعیت ارائه

این بسته، تفکیک هفت‌گانهٔ جدید را در کد و مستندات فعال می‌کند. تست و QA نهایی بنا به درخواست کاربر به فاز بعد موکول شده؛ پس این سند ادعای «آمادهٔ تحویل نهایی» ندارد. PDF مرجع ۹۶ صفحه‌ای در clone پیدا نشد؛ mapping صفحه‌ها موجود است، اما بازبینی تصویری باید پس از دسترسی به فایل انجام شود.

## معماری

```text
Browser / RTL
  ├─ GET /, /portal/<slug>/ -> shell
  ├─ GET /api/portal/pages/<slug>/ -> owner selector -> ORM -> page HTML JSON
  ├─ POST same page API + CSRF -> Django form -> validation/ownership -> DB
  └─ enrollment/scheduling/accounts APIs -> domain services
```

مدل‌ها و admin همچنان مرکزی‌اند: `apps/core/models.py`, `apps/core/admin.py`. هفت manifest در `apps/core/frontend/registry.py` ثبت می‌شوند؛ مسیرهای URL عمومی تغییر نکرده‌اند. `NAV_GROUPS` دسته‌بندی کاربردی منوست و هیچ‌گاه به معنی مالک تیمی نیست.

## تقسیم مسئولیت‌ها و مستندات جداگانه

| عضو | دامنه و URLها | پوشهٔ کد | سند ارائه |
|---|---|---|---|
| Mobina | ورود `/login/`، داشبورد `/`، تنظیمات و کارت | `apps/core/frontend/mobina/` | [01_Mobina.md](01_Mobina.md) |
| Shaghayegh | انتخاب/تغییر درس، وضعیت ثبت‌نام | `apps/core/frontend/shaghayegh/` | [02_Shaghayegh.md](02_Shaghayegh.md) |
| Parsa | پرداخت، تسهیلات، شهریه | `apps/core/frontend/parsa/` | [03_Parsa.md](03_Parsa.md) |
| Omid | فعالیت، کارنامه، چارت، اعتراض نمره | `apps/core/frontend/omid/` | [04_Omid.md](04_Omid.md) |
| Niousha | برنامه، تقویم، حضور، کارت امتحان؛ Frontend Lead | `apps/core/frontend/niousha/` | [05_Niousha.md](05_Niousha.md) |
| Shahsvand | کارآموزی، مهمانی، درخواست و گواهی | `apps/core/frontend/shahsvand/` | [06_Shahsvand.md](06_Shahsvand.md) |
| Miri | استاد، پیام، اعلان، راهنما، پشتیبانی؛ Shared Lead | `apps/core/frontend/miri/` | [07_Miri.md](07_Miri.md) |

فهرست تمام ۳۲ route و endpointهایشان در [TEAM_OWNERSHIP.md](../TEAM_OWNERSHIP.md) و [SCREEN_API_MATRIX.md](../SCREEN_API_MATRIX.md) است. screen docs مستقل در [docs/screens](../screens/README.md) و قراردادهای دقیق در [API_CONTRACTS.md](../API_CONTRACTS.md) قرار دارند.

## سناریوی ارائهٔ تیمی

۱. ورود و session؛ ۲. dashboard و انتخاب term؛ ۳. نمایش ارائه‌ها و workflow انتخاب واحد در محیط تست؛ ۴. مشاهدهٔ کارنامه/برنامه؛ ۵. مشاهدهٔ سوابق مالی بدون پرداخت جعلی؛ ۶. ثبت یک درخواست و پیگیری وضعیت ذخیره‌شده؛ ۷. پیام/اعلان و محدودیت provider؛ ۸. خروج.

ثبت یا حذف درس در دیتابیس محلی فقط بعد از ساخت test DB و term/offering مجاز انجام شود. DB اصلی و دادهٔ کاربر برای demo نباید تغییر کنند.

## محدودیت‌ها و فاز بعد

- test suite، Django checks، browser run و viewportهای موبایل/دسکتاپ در فاز بعد اجرا می‌شوند.
- قرارداد provider پرداخت، صدور رسمی کارت/گواهی و ارسال SMS/email در workspace موجود نیست؛ این عملیات unavailable هستند.
- مرجع قوانین رسمی `نیازمندی_های_آموزشیار.md` و PDF در این clone نیستند؛ رفتار نامعلوم نباید حدس زده شود.
- معیار complete هر صفحه شامل UI، API، persistence، permission، validation/error، refresh و test evidence است. هیچ صفحه‌ای تا ارائهٔ آن شواهد کامل خوانده نشود.

## محل مستندات

- مرجع تیم و URL هر عضو: `docs/TEAM_OWNERSHIP.md`
- ماتریس تمام صفحه/API: `docs/SCREEN_API_MATRIX.md`
- قرارداد endpointها: `docs/API_CONTRACTS.md`
- mapping ۹۶ صفحه: `docs/PDF_PAGE_MAPPING.md`
- screen-by-screen: `docs/screens/<slug>.md`
- هفت ارائهٔ فردی: `docs/presentation/01_Mobina.md` تا `07_Miri.md`
- وضعیت و ادامه: `docs/PROGRESS.md`, `docs/NEXT_STEPS.md`, `docs/FINAL_REPORT.md`

# ارائهٔ گروه پارسا — امور مالی

### 1. معرفی بخش

نمایش بدهی پرونده، خلاصهٔ نیمسال، سوابق پرداخت و درخواست تسهیلات با دادهٔ واقعی موجود. درگاه بانکی در checkout پیکربندی نشده است.

### 2. مسئولیت عضو

گروه Parsa در manifest واقعی چهار صفحهٔ `payments`, `secure-payment`, `financial-aid`, `tuition` را دارد. PDF صفحهٔ ۳۰ را به state منع عملیات بدهی اختصاص می‌دهد؛ آن state route مستقل نیست. موفقیت پرداخت یا بازگشت از provider نباید جعل شود.

### 3. صفحات پیاده‌سازی‌شده

| صفحه/حالت | PDF | URL | وضعیت |
|---|---:|---|---|
| منع عملیات به علت بدهی | 30 | state در گردش ثبت‌نام، نه route مالی | مستقل بازنمایی نشده؛ service ثبت‌نام بدهی را رد می‌کند |
| سوابق پرداخت | 63 | `/portal/payments/` | خواندن تراکنش‌های پرونده/نیمسال |
| پرداخت امن | 64 | `/portal/secure-payment/` | نبود gateway صریح است؛ mutation ندارد |
| تسهیلات | 65 | `/portal/financial-aid/` | ثبت درخواست نوع/دلیل در مدل موجود؛ مبلغ و پیوست مدل نشده |
| شهریه | 66 | `/portal/tuition/` | جمع‌زدن پرداخت‌های موفق؛ تفکیک line item شهریه موجود نیست |

### 4. طراحی و عملکرد

خلاصه و جدول از selector مالی ساخته می‌شوند و به Student جاری و Term انتخابی محدودند. صفحات مالی از یک template fragment در section shell استفاده می‌کنند. باگ ارث‌بری shell تکراری در همین template با تست regression رفع شد؛ routeهای مالی اکنون تنها یک `portal-shell` دارند.

### 5. APIهای مرتبط

| مسیر | روش | ورودی/خروجی |
|---|---|---|
| `/api/portal/pages/payments/` | GET | `page`, `profile`, `term`, HTML؛ فقط پروندهٔ مالک |
| `/api/portal/pages/secure-payment/` | GET | پیام نبود gateway؛ تراکنش نمی‌سازد |
| `/api/portal/pages/financial-aid/` | GET/POST | فیلدهای واقعی فرم `scholarship_type`, `scholarship_reason`؛ وضعیت از سرور |
| `/api/portal/pages/tuition/` | GET | summary و تجمیع پرداخت‌های موفق |

نمونهٔ خواندن: `GET /api/portal/pages/payments/` با session؛ 200 و `{"page":"payments","html":"…","profile":{"student_code":"…"},"term":{"term_code":"…","display_label":"…"}}`. درخواست POST به صفحهٔ پرداخت امن وجود ندارد و success provider تولید نمی‌شود.

### 6. سناریوی عملکرد

session → page API → Parsa selector → queryهای Payment/Student/Term → render → جدول/خلاصه. فرم تسهیلات از `OwnedModelForm` مالک و status را سروری تنظیم می‌کند؛ پرداخت واقعی خارج از مرز سامانه است و برای آن مسیر fake ساخته نشده.

### 7. ارتباط با سایر بخش‌ها

از Student و Term مشترک استفاده می‌کند؛ بدهی روی service enrollment اثر دارد. Paymentها با انتخاب نیمسال فیلتر می‌شوند. درگاه، حساب بانکی، ریزاقساط و workflow بررسی کارمند در مدل/API فعلی مشخص نیستند.

### 8. ساختار فنی

- `apps/core/frontend/parsa/pages.py`, `selectors.py`, `forms.py`
- `apps/core/frontend/parsa/templates/parsa/finance.html`
- `apps/core/models.py`: `Payment`, `Student`, `ScholarshipApplication`, `Term`, `Constant`
- `apps/core/test_frontend.py`: تست shell واحد، privacy، و عدم جعل درگاه.

### 9. تست‌ها

تست focused `test_finance_pages_render_inside_one_portal_shell` برای سه route مالی اجرا و پاس شد. در آخرین اجرای کامل موجود: ۱۰۱ تست Python و ۱۴ تست Node پاس؛ `manage.py check` و migration check نیز پاک بودند. ۲۰ RuntimeWarning datetime naive از seed در [TEST_REPORT.md](../TEST_REPORT.md) ثبت شده است.

### 10. راهنمای ارائه به استاد

1. `payments` و `tuition` را در نیمسال انتخابی باز کنید.
2. در کد selector، فیلتر پرونده و تجمیع مبلغ را نشان دهید.
3. `secure-payment` را باز کنید و پیام نبود gateway را نمایش دهید.
4. مدل `ScholarshipApplication` را با فیلدهای واقعی مقایسه کنید.
5. توضیح دهید چرا بدون قرارداد بانکی، پرداخت موفق ساختگی نمایش داده نمی‌شود.

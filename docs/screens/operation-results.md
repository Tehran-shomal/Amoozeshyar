# نتیجه‌ها و منع عملیات (PDF-only reference states)

- مرجع: PDF صفحهٔ ۳۰ (منع به علت بدهی)، ۳۸–۴۸ (نتایج عملیات)، ۵۶–۵۹ (نتایج حذف/اضافه)، ۷۵–۷۸ (نتایج حذف اضطراری).
- route/owner: برای اکثر stateها route مستقلی وجود ندارد؛ ثبت‌نام و حذف به endpointهای enrollment و صفحهٔ جاری برمی‌گردند.
- رفتار موجود: خطاهای mutation به کد/message JSON و پیام UI تبدیل می‌شوند؛ success معمولاً صفحه را reload می‌کند. هیچ operation-result record/URL مستقل ساخته نمی‌شود.
- داده/API: `POST /api/enrollment/register/<id>/`, `POST /api/enrollment/drop/<id>/`; enrollment/term/student متعلق.
- اعتبارسنجی/مجوز: rule checks در service؛ بدهی مانع ثبت‌نام است؛ حذف مجاز به بازه‌های تعریف‌شده.
- محدودیت: PDF برای چند پاسخ موفق/منع، layout و متن مشخص دارد؛ stateهای مستقل و مجموعه‌دادهٔ متنوع current fixture وجود ندارد. متن نتیجه را از روی ظاهر حدس نمی‌زنیم.
- آزمون: `apps/core/enrollment/test_services.py`, `static/core/tests/portal_api.test.cjs`, `portal_bindings.test.cjs`.
- وضعیت: API نتیجهٔ rule را دارد، ولی صفحه/route مستقل نتیجهٔ PDF بازنمایی‌نشده است.

# مرکز پشتیبانی

- مالک/route: Omid؛ `/portal/support/`; shared `core/live_content.html`; `SupportForm`.
- مرجع: PDF صفحهٔ ۲۹.
- هدف/کنترل: ساخت تیکت و نمایش تیکت‌های اخیر حساب جاری.
- داده/API: Ticket, TicketCategory, Person, Constant؛ GET/POST API صفحه؛ query تیکت‌ها بر اساس `creator=request.user`.
- اعتبارسنجی/مجوز: category فعال؛ creator از session، نه request؛ فیلدهای category/subject/content مطابق model.
- خطا/محدودیت: category نامعتبر form error؛ assignment، پاسخ agent، SLA و status lifecycle در این فرم/API ارائه نشده‌اند.
- navigation: گروه ارتباط و خدمات؛ پیگیری با لیست تیکت‌های خود حساب.
- آزمون/وابستگی: `apps/core/test_frontend.py`; SupportForm، Ticket/TicketCategory.
- وضعیت: ثبت و خواندن ticket model موجود؛ چرخهٔ کامل پشتیبانی/مجوز agent ناقص؛ screenshot تازه باز.

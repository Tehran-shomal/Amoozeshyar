# فهرست انتخاب درس در مودال (PDF reference state)

- مرجع: PDF صفحات ۷۹ و ۸۴؛ این‌ها state تصویری‌اند، نه route مستقل.
- صفحهٔ مرتبط/مالک: Mobina؛ `/portal/selected-courses/` و `selected-courses.md`.
- رفتار موجود: offeringها در جدول صفحه از `GET /api/scheduling/offerings/?term=...` می‌آیند؛ client دکمهٔ انتخاب را در همان ردیف نشان می‌دهد.
- اختلاف: در template/JS جاری modal انتخاب درس با state/overlay مجزا وجود ندارد؛ در نتیجه ابعاد/close/focus رفتار modal PDF بازنمایی نشده است.
- داده/validation/permission: قرارداد Offering و ثبت در [API_CONTRACTS.md](../API_CONTRACTS.md)؛ enrollment با شناسهٔ قطعی ثبت و در backend اعتبارسنجی می‌شود.
- آزمون: `apps/core/enrollment/test_services.py`, `static/core/tests/portal_bindings.test.cjs`؛ modal مستقلاً تست نشده است.
- وضعیت: PDF state بازنمایی‌نشده؛ به‌عنوان قابلیت کامل علامت نخورده.

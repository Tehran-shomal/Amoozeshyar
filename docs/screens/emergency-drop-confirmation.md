# تأیید حذف اضطراری (PDF reference state)

- مرجع: PDF صفحات ۹۳–۹۶.
- صفحهٔ مرتبط/مالک: Shaghayegh؛ `/portal/emergency-drop/`; همان modal و JS حذف عادی.
- رفتار موجود: نام/کد/واحد از ردیف enrollment؛ confirm همان `POST /api/enrollment/drop/<id>/` را صدا می‌زند.
- اختلاف: request payload نوع حذف را نمی‌فرستد؛ server از Term بررسی می‌کند که یکی از دو بازهٔ add/drop یا emergency باز باشد. سیاست مجزا هنوز نیست.
- اعتبارسنجی/خطا: ownership و time window backend؛ خطا در status مشترک؛ موفقیت reload.
- آزمون: `apps/core/enrollment/test_services.py`; هر چهار variation PDF و focus/viewport بصری باید جداگانه بررسی شوند.
- وضعیت: confirmation interaction موجود؛ تفاوت policy/resultهای مستقل PDF ناقص است.

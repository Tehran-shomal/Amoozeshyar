# اطلاعیه‌های استادان

- مالک/route: Niousha/Pouya؛ `/portal/announcements/`; `neyousha_pouya/notifications.html`; selector مشترک notifications.
- مرجع: PDF صفحهٔ ۱۶.
- هدف/کنترل: کارت‌های Notification دیده‌شده در صفحهٔ اطلاعیه.
- داده/API: Notification با `user__person=request.user`؛ GET API صفحه.
- نوشتن: فقط `notification_id` خود کاربر برای mark-read؛ ایجاد/انتشار اطلاعیه از این screen ممکن نیست.
- اعتبارسنجی/مجوز: session و owner filter؛ cross-user id رد می‌شود؛ CSRF برای write.
- خطا/محدودیت: مدل فعلی با selector مشترک نوع استاد/اطلاعیه را برای این route جدا فیلتر نمی‌کند؛ رفتار نوع‌بندی PDF کامل اثبات نشده.
- navigation: مرکز اعلان‌ها و menu خدمات؛ no notification provider.
- آزمون/وابستگی: `apps/core/test_frontend.py`; Notification selector/template.
- وضعیت: data-backed list با route موجود؛ تمایز domain/announcement state و screenshot تازه باز است.

# مرکز اعلان‌ها

- مالک/route: Niousha/Pouya؛ `/portal/notifications/`; `neyousha_pouya/notifications.html`; shared selector.
- مرجع: PDF صفحهٔ ۱۸؛ notification toggle crop صفحهٔ ۵۰ در settings است.
- هدف/کنترل: فهرست اعلان‌های حساب جاری با وضعیت/فیلتر UI؛ بازکردن/خوانده‌شدن.
- داده/API: Notification و UserAccount/Person؛ GET API صفحه؛ POST API صفحه با `notification_id` mark-read می‌کند.
- اعتبارسنجی/مجوز: `user__person=request.user` هم در query و هم update؛ اعلان کاربر دیگر 404؛ CSRF برای POST.
- خطا/محدودیت: اعلان خارجی push/email/SMS ساخته نمی‌شود؛ pagination/delivery lifecycle در code مشخص نیست.
- navigation: announcements و settings؛ POST موفق به همان page redirect می‌کند.
- آزمون/وابستگی: `apps/core/test_frontend.py`; `Notification` model, shared API/JS.
- وضعیت: listing و mark-read موجود؛ delivery provider غایب؛ screenshot تازه باز.

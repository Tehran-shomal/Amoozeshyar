# حذف اضطراری

- مالک/route: Shaghayegh؛ `/portal/emergency-drop/`; از همان template/selector و JS صفحهٔ حذف و اضافه.
- مرجع: PDF صفحهٔ ۵۴؛ تغییرات فهرست در صفحات ۷۵–۷۸؛ تأیید حذف در صفحات ۹۳–۹۶.
- هدف/کنترل: جدول enrollment فعال، action حذف اضطراری و مودال تأیید.
- داده/API: Student, Enrollment, CourseOffering, Term؛ GET page و `POST /api/enrollment/emergency-drop/<id>/`; این endpoint مستقل از `POST /api/enrollment/drop/<id>/` است.
- قاعدهٔ اصلاح‌شده: `emergency-drop` فقط بازهٔ `Term.emergency_drop_start/end` را می‌پذیرد؛ add/drop فقط بازهٔ معمولی را می‌پذیرد. سرویس عمومی برای مصرف‌کننده‌های داخلی همچنان حالت either دارد، اما این دو HTTP workflow جدا هستند.
- اعتبارسنجی/مجوز: session/student و مالکیت Enrollment؛ زمان از Term واقعی؛ idempotent برای enrollment غیرفعال.
- خطا/نتیجه: خارج بازه در endpoint اضطراری `emergency_drop_window_closed` و در endpoint عادی `drop_window_closed`. صفحات ۷۵–۷۸ همچنان stateهای فهرست همین صفحه با ردیف‌های متفاوت‌اند، نه routeهای نتیجه. بعد از عملیات موفق، `dropped_enrollment_id` فقط برای enrollment حذف‌شدهٔ همان Student/Term resolve می‌شود و نتیجهٔ scoped نشان داده می‌شود.
- محدودیت مالی: حذف وضعیت ثبت‌نام را عوض می‌کند؛ API بازپرداخت را محاسبه/ثبت نمی‌کند و خود حذف اضطراری درخواست استرداد وجه ایجاد نمی‌کند.
- navigation: پس از تأیید، نتیجهٔ scoped در همین route می‌آید؛ شروع دوبارهٔ سناریو و لینک‌های sidebar در دسترس‌اند.
- آزمون/وابستگی: regression تفکیک دو window در `apps/core/enrollment/test_services.py`, endpoint و مالکیت نتیجه در `apps/core/test_frontend.py` و path/redirect در `static/core/tests/portal_api.test.cjs` و `portal_bindings.test.cjs` نوشته شده‌اند اما اجرا نشده‌اند.
- وضعیت: حذف واقعی و dialog؛ صفحه به endpoint مخصوص emergency وصل است. مرجع صفحات بررسی شد؛ capture جاری ترتیبی به‌دلیل توقف visual روی صفحهٔ ۱۹ نداریم.

# چارت انتخاب واحد

- مالک/route: Omid؛ `/portal/curriculum/`; قالب اختصاصی `omid/curriculum.html` با shell مشترک `core/section.html`؛ `omid.selectors.build`.
- مرجع: PDF صفحهٔ ۲۳.
- هدف/کنترل: چهار شاخص واحد مصوب/گذرانده/جاری/باقی‌مانده، جدول مسیر دروس، پیش‌نیازهای تعریف‌شده و پیوند به انتخاب واحد و کارآموزی.
- داده/API: `GET /api/portal/pages/curriculum/`؛ Curriculum فعال رشتهٔ پرونده، Lesson/Constant، Prerequisite، Enrollmentهای فعال همان دانشجو و Gradeهای قبولی (حد `PASSING_GRADE` سرویس ثبت‌نام). وضعیت هر درس فقط از Enrollment/Grade همان دانشجو محاسبه می‌شود؛ واحدهای خلاصه از ردیف‌های چارت محاسبه می‌شوند.
- محدودیت schema: مدل Curriculum ستون مستقل گروه آموزشی ندارد؛ ستون «گروه» از `requirement_type` چارت پر می‌شود. پیش‌نیاز تعریف‌نشده با «—» نشان داده می‌شود. «باقی‌مانده» وضعیت نمایشی است و مجوز انتخاب واحد را جایگزین نمی‌کند.
- نوشتن/اعتبارسنجی: form یا mutation ندارد؛ دادهٔ جدید از جدول ساخته نمی‌شود.
- دسترسی/خطا: session؛ داده از field پروندهٔ متعلق؛ بدون پرونده پیام انتخاب profile؛ DB unavailable 503.
- navigation: گروه ثبت‌نام؛ لینک‌ها از sidebar مشترک.
- آزمون/وابستگی: regression `test_curriculum_page_shows_chart_progress_and_real_course_state` در `apps/core/test_frontend.py` نوشته شده و بنا به درخواست برای فاز تست اجرا نشده است؛ Omid selector و مدل‌های Curriculum/Prerequisite/Enrollment/Grade.
- وضعیت: مرجع PDF در `docs/screens/page-23-reference.png` موجود و منبع/API صفحه اصلاح شد؛ capture جاری احرازشده نداریم، بنابراین تطبیق بصری runtime تأیید نشده و توالی تصویری طبق plan هنوز روی صفحهٔ ۱۹ متوقف است.

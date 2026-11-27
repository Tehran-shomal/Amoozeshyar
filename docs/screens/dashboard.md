# داشبورد

- مالک/مسیر: Mobina؛ `GET /`; داده `GET /api/portal/pages/home/`; template `mobina/home.html`.
- مرجع: PDF صفحهٔ ۲.
- هدف/کنترل‌ها: خلاصهٔ پرونده و نیمسال، کلاس‌های فعال، اعلان‌های اخیر، وضعیت تحصیلی/مالی و quick actions.
- ورودی: query اختیاری `student_code` و `term`; کنترل انتخاب پرونده/نیمسال در پوستهٔ مشترک.
- داده: Student/Field/Enrollment/CourseOffering/Notification/Payment/Term؛ فقط student انتخاب‌شدهٔ متعلق به حساب و پنج اعلان اخیر حساب جاری.
- API: GET صفحه؛ dashboard خودش POST ندارد. لینک‌ها به routeهای متناظر می‌روند.
- اعتبارسنجی/مجوز: session اجباری؛ profile دیگران 403؛ بدون پرونده پیام انتخاب/نبود پرونده؛ مبلغ و پرداخت از DB واقعی.
- خطا: 401 session، 403 profile، 404 term، 503 DB؛ اعلان خالی/دادهٔ خالی state عادی است.
- مسیر: quick action به enrollment، transcript، tuition و requests؛ جست‌وجوی sidebar از پوسته.
- آزمون/وابستگی: `apps/core/test_frontend.py`; Mobina dashboard selector، common portal shell/API.
- بازبینی PDF شمارهٔ ۲: template، selector، view و قرارداد API بررسی شدند. `GET /api/portal/pages/home/` بدون نشست ۴۰۱ و با نشست محلی ۲۰۰ داد؛ login و API خواندنی بودند و رکورد کسب‌وکاری تغییر نکرد. مجوز پروفایل از `Student.objects.filter(person=request.user)` می‌آید و کد پروندهٔ متعلق به حساب دیگر رد می‌شود.
- مقایسهٔ دیداری در ۱۴۴۰×۹۰۰ با مرجع ۱۰۸۰×۶۷۵: عرض/جای hero، میان‌برها، سه کارت ردیف اول و دو کارت ردیف دوم با مقیاس ۴/۳ هم‌تراز شدند. نبود grid ردیف خلاصه و بلندی کارت‌های پایین اصلاح شد؛ جمع‌وجورشدن ردیف‌های مالی و حلقهٔ معدل در `static/core/responsive.css` است. محتوای seed طبیعتاً با متن/دادهٔ نمونهٔ PDF یکسان نیست؛ گروه‌های sidebar نیز عمداً از تقسیم‌بندی مالکیت جدید پیروی می‌کنند.
- capture محلی خارج از مخزن: `%TEMP%\amoozeshyar-dashboard-page02-final.png` (HTML همان template از پاسخ API احراز‌شده رندر شد؛ JavaScript برای capture حذف شد). کلون روی `http://127.0.0.1:8001` اجرا شد؛ پورت ۸۰۰۰ متعلق به checkout دیگری بود و دست‌نخورده ماند.
- وضعیت: بازبینی ظاهری و code/API review صفحهٔ ۲ انجام شد. `manage.py check` پاک است؛ تست خودکار طبق درخواست برای فاز بعد محفوظ مانده است.

# درخواست بررسی فارغ‌التحصیلی

- مالک/route: Shahsvand؛ `/portal/graduation/`; قالب اختصاصی `shahsvand/graduation.html` در shell مشترک؛ GET از GraduationAudit. نوع درخواست معتبر در lookup موجود نیست؛ POST جدید غیرفعال است.
- مرجع: PDF صفحهٔ ۲۶.
- هدف/کنترل: نمایش خلاصهٔ واقعیت‌های موجود پرونده، نتیجهٔ آخرین audit و تاریخچهٔ auditهای آموزشی؛ لینک به چارت و مالی.
- داده/API: `GET /api/portal/pages/graduation/`; GraduationAudit فقط برای Student جاری، Student GPA/واحد گذرانده/بدهی ثبت‌شده. شرط واجد شرایط بودن از property موجود `GraduationAudit.is_graduation_eligible` خوانده می‌شود.
- اعتبارسنجی/مجوز: دادهٔ audit فقط برای Student جاری نمایش داده می‌شود؛ هیچ POST تا وجود نوع معتبر در lookup ارائه نمی‌شود.
- خطا/محدودیت: فرم قبلی به نوع `certificate` نامرتبط تکیه داشت؛ حذف شد. آستانهٔ رسمی GPA، اتصال تسویهٔ کتابخانه و lifecycle چندمرحله‌ای در schema/provider فعلی نیست؛ عدد GPA/بدهی به‌تنهایی شرط نهایی تلقی نمی‌شود. CTA ثبت نهایی غیرفعال است؛ POST API پاسخ 405 می‌دهد.
- navigation: منوی درخواست‌ها؛ نتیجه در جدول GraduationAudit جدا از خود submission است.
- آزمون/وابستگی: regression `test_graduation_page_reports_only_recorded_audit_and_profile_facts` در `apps/core/test_frontend.py` نوشته شده اما اجرا نشده؛ selector و مدل GraduationAudit.
- وضعیت: مرجع PDF در `docs/screens/page-26-reference.png` بررسی و صفحه به چک‌لیست داده‌محور/تاریخچهٔ owner-scoped تبدیل شد؛ capture جاری احرازشده نداریم، پس تطبیق runtime تأیید نشده و توالی تصویری طبق plan روی صفحهٔ ۱۹ متوقف است.

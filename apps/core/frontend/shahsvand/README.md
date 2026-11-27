# شاهسوند — درخواست‌های دانشجویی

مالک `/portal/internship/`, `/portal/guest-request/`, `/portal/graduation/`, `/portal/requests/`, `/portal/education-certificate/`, `/portal/graduation-certificate/` است. فرم‌ها از API هم‌مبدأ `/api/portal/pages/<slug>/` خوانده و با POST همان endpoint ثبت می‌شوند.

- `pages.py`: routeها، metadata و انتخاب قالب‌های اختصاصی کارآموزی، درخواست مهمانی و نمایش audit فارغ‌التحصیلی.
- `selectors.py`: فهرست را بر اساس Student جاری محدود می‌کند.
- `forms.py`: مالک و وضعیت را سرور تعیین می‌کند؛ internship/request type و certificate type فقط از lookupهای فعال و موجود می‌آیند.
- `templates/shahsvand/`: `internship.html` و `guest_request.html` فیلدهای قابل ذخیره و تاریخچهٔ همان دانشجو را نشان می‌دهند؛ `graduation.html` فقط facts/audit ثبت‌شده را نمایش می‌دهد و درخواست رسمی را نمی‌سازد.
- [ارائهٔ شاهسوند](../../../../docs/presentation/06_Shahsvand.md) · [مستند routeها](../../../../docs/TEAM_OWNERSHIP.md).
- screenها: [درخواست عمومی](../../../../docs/screens/requests.md)، [کارآموزی](../../../../docs/screens/internship.md)، [مهمانی](../../../../docs/screens/guest-request.md)، [فارغ‌التحصیلی](../../../../docs/screens/graduation.md)، [گواهی](../../../../docs/screens/education-certificate.md).

ثبت درخواست، تأیید یا صدور رسمی نیست. وضعیت‌های ثبت‌نشده و قوانین فاقد منبع رسمی، حدس زده نمی‌شوند.

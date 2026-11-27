# نیوشا — برنامه و کلاس‌ها (Frontend Lead)

مالک `/portal/schedule/`, `/portal/calendar/`, `/portal/attendance/`, `/portal/exam-card/` و مؤلفهٔ مشترک انتخاب نیمسال است. صفحه‌ها از `GET /api/portal/pages/<slug>/` می‌خوانند؛ برای این routeها write کارمندی در UI وجود ندارد.

- `pages.py`: manifest و `COMPONENTS = ("term_picker",)`.
- `selectors.py`: schedule/attendance/exams فقط از Enrollment و Term واقعی پرونده استفاده می‌کند؛ `niousha/schedule.html` برنامه را به‌شکل شبکهٔ هفتگی و خلاصهٔ واحد/جلسه/تداخل نمایش می‌دهد.
- `templates/niousha/exam_card.html`: چاپ اطلاعات موجود، با اعلام صریح seat number ناموجود.
- پوستهٔ مشترک: `apps/core/templates/core/portal_base.html`; picker: `static/core/live_portal.js`; ترم فعال: `GET /api/scheduling/active-term/`.
- [ارائهٔ نیوشا](../../../../docs/presentation/05_Niousha.md) · [ماتریس API](../../../../docs/SCREEN_API_MATRIX.md).

Frontend Lead مسئول هماهنگی و بررسی responsive همهٔ گروه‌هاست؛ این نقش مالکیت routeهای سایر اعضا را جابه‌جا نمی‌کند. کارت رسمی یا حضور کارمندی جعل نمی‌شود.

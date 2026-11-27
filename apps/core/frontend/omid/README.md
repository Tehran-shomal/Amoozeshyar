# امید — سوابق و پیشرفت آموزشی

مالک `/portal/academic-activities/`, `/portal/transcript/`, `/portal/curriculum/`, `/portal/grade-appeal/` است. همه از `GET /api/portal/pages/<slug>/` استفاده می‌کنند؛ اعتراض نمره با `POST` همان API ثبت می‌شود.

- `pages.py`: manifest مالکیت و قالب‌ها.
- `selectors.py`: Enrollment، Grade، Curriculum، Prerequisite و GradeAppeal را به پرونده/رشته/ترم لازم محدود می‌کند؛ پیشرفت چارت بر اساس نمرهٔ قبولی و انتخاب‌واحد فعال همان دانشجو محاسبه می‌شود.
- `forms.py`: فرم اعتراض؛ انتخاب enrollment از `OwnedModelForm` و تاریخ/status از سرور.
- `templates/omid/`: قالب‌های کارنامه، فعالیت آموزشی و چارت انتخاب واحد.
- [ارائهٔ امید](../../../../docs/presentation/04_Omid.md) · [ماتریس route/API](../../../../docs/SCREEN_API_MATRIX.md).

چارت، کارنامه و فعالیت read-only هستند. نمرهٔ غایب ساخته نمی‌شود و قانون رسمی اعتراض که منبع ندارد unknown می‌ماند.

# پویا و نیوشا (لید فرانت)

## Page ownership

- `internship` - کارآموزی
- `notifications` - مرکز اعلان‌ها
- `announcements` - اطلاعیه‌های اساتید
- `calendar` - تقویم آموزشی ترم
- `schedule` - برنامه هفتگی کامل
- `settings` - تنظیمات زبان و اعلان‌ها

Shared component: `term_picker` in the portal header. This is the frontend lead module.

`pages.py` declares owned slugs and page-specific assets; `selectors.py` reads the records for those pages.
`forms.py` contains this group's forms, with ownership and validation enforced on the server.

The header's semester picker is the shared component owned by the lead group; its choices come from saved `Term` rows. The schedule and term calendar use the selected term. Internship forms are student-scoped, and notifications are scoped to the signed-in account. `notifications.html` provides the unread/read presentation and its existing POST action.

Page-specific files:

- `templates/neyousha_pouya/notifications.html`

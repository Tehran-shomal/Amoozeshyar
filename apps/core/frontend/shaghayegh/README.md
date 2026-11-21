# شقایق

## Page ownership

- `add-drop` - حذف و اضافه
- `emergency-drop` - حذف اضطراری
- `registration-status` - وضعیت ثبت‌نام
- `grade-appeal` - درخواست‌های اعتراض به نمره

`pages.py` declares owned slugs and page-specific assets; `selectors.py` reads the records for those pages.
`forms.py` contains this group's forms, with ownership and validation enforced on the server.

`add-drop` and `emergency-drop` share `templates/shaghayegh/course_changes.html`. Each action is attached to a real active `Enrollment` ID and confirmed in the in-page dialog before the existing drop API is called. The registration status and grade-appeal pages use the shared table/form renderer.

Page-specific files:

- `static/shaghayegh/section.js`

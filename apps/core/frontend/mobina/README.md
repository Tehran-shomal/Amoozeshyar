# مبینا

## Page ownership

- `enrollment` - انتخاب واحد
- `selected-courses` - دروس انتخاب‌شده
- `curriculum` - چارت انتخاب واحد

Special pages: `login` (`templates/mobina/login.html`) and `dashboard` (`templates/mobina/home.html`).

`pages.py` declares owned slugs and page-specific assets. The browser reads database-backed page content from `/api/portal/pages/<slug>/`; available course offerings are loaded from `/api/scheduling/offerings/?term=<term_code>`. Current registrations and dashboard summaries are returned by the page API using this group's student-scoped selectors. Enrollment actions send real record IDs to the existing enrollment API.

Page-specific files:

- `static/mobina/section.js`
- `templates/mobina/home.html`
- `templates/mobina/login.html`

The enrollment flow uses two steps: `enrollment.html` checks the student's saved profile and term, and `selected_courses.html` shows current registrations and eligible offerings. The offerings list is inserted from the scheduling API; both stages use empty states when their records are absent, and no sample courses are created.

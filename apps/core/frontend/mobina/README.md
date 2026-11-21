# مبینا

## Page ownership

- `enrollment` - انتخاب واحد
- `selected-courses` - دروس انتخاب‌شده
- `curriculum` - چارت انتخاب واحد

Special pages: `login` (`templates/mobina/login.html`) and `dashboard` (`templates/mobina/home.html`).

`pages.py` declares owned slugs and page-specific assets; `selectors.py` reads the signed-in student's record, the selected term, available offerings, registrations, notifications, and payment summary. Enrollment actions send the real course-offering ID to the existing API.

Page-specific files:

- `static/mobina/section.js`
- `templates/mobina/home.html`
- `templates/mobina/login.html`

The enrollment flow uses two steps: `enrollment.html` checks the student's saved profile and term, and `selected_courses.html` shows current registrations and eligible offerings. Both stages use empty states when their records are absent; the selector does not create sample courses.

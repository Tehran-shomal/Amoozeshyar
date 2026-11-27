# شقایق — ثبت‌نام و تغییر دروس

## Page ownership

- `enrollment` — `/portal/enrollment/`
- `selected-courses` — `/portal/selected-courses/`
- `add-drop` — `/portal/add-drop/`
- `emergency-drop` — `/portal/emergency-drop/`
- `registration-status` — `/portal/registration-status/`

Page data uses `GET /api/portal/pages/<slug>/`; offerings use `GET /api/scheduling/offerings/?term=<term_code>`. Register/drop call `POST /api/enrollment/register/<offering_id>/`, `/api/enrollment/drop/<enrollment_id>/`, and `/api/enrollment/emergency-drop/<enrollment_id>/`. The backend validates ownership, eligibility, capacity, and the workflow-specific configured window.

`add-drop` and `emergency-drop` share `templates/shaghayegh/course_changes.html`. A deletion is attached to an active `Enrollment` ID and confirmed in the in-page dialog. The add-drop page also loads offerings from the scheduling API and registers through the existing enrollment API, so add and drop are both available on the PDF-matched route; emergency-drop remains drop-only. The two-step enrollment templates also live here. Grade appeal is owned by Omid.

`selected-courses` renders the PDF page-30 debt blocker only after the real enrollment API returns `tuition_debt`; amount/max come from the selected Student. No minimum-unit rule or live payment gateway is present, so neither is simulated.

Page-specific files:

- `static/shaghayegh/section.js`

For exact payloads, screen URLs, permissions, and limitations see [TEAM_OWNERSHIP](../../../../docs/TEAM_OWNERSHIP.md), [API_CONTRACTS](../../../../docs/API_CONTRACTS.md), and [presentation](../../../../docs/presentation/02_Shaghayegh.md).

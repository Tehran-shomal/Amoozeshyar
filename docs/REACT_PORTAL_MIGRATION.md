# React Portal Migration Status

Last updated: 2026-11-26

## Runtime and API boundary

- React is now the default at `/login/`, `/`, and all registered `/portal/<slug>/` routes. Add `?legacy=1` to explicitly use the Django-template compatibility path; `?react=1` remains accepted as a compatibility flag but is no longer required.
- Authenticated page data is read from `GET /api/portal/ui/pages/<slug>/`. Django continues to enforce session authentication, selected-profile ownership, term selection, selectors, validation, CSRF, and persistence.
- Page actions use the existing `POST /api/portal/pages/<slug>/` endpoint. React does not render HTML from that endpoint and page text is rendered as text, not injected markup.
- The default React login still posts to Django's existing authentication service; after success it returns to React by default and preserves the explicit `legacy=1` escape hatch when that path was chosen.
- Session-expired/API errors use a React system-error view with explicit 401/403/database-unavailable messaging and retry; the hidden CSRF input in the React shell is also available as a cookie fallback. The server-rendered login and portal remain available with `?legacy=1`.
- Page-specific model data is mapped field-by-field in `apps/core/frontend/react_payloads.py`; model instances and querysets are not recursively serialized.
- `SCREEN_API_MATRIX.md` remains the route/ownership/API reference; this document adds the React component mapping and migration acceptance state.

## React-rendered pages in the current default experience

| Existing route | React component | Data and actions |
|---|---|---|
| `/` (`home`) | `DashboardPage` | Dashboard selector data: student summary, classes, notices, finance, academics, quick links. Read-only. |
| `/portal/student-card/` | `StudentCardPage` | Selected student identity/status/date and selected term; links to existing requests/support routes; browser print. |
| `/portal/announcements/` | `AnnouncementsPage` | Receiver-scoped announcements; POST `communication_id` marks only the current user's announcement read. |
| `/portal/notifications/` | `NotificationsPage` | Current-user notifications and actual notification-type counts; preserves `notification_type`, `student_code`, `term`, and compatibility flags; POST `notification_id` marks read. |
| `/portal/settings/` | `SettingsPage` | Account-owned `SettingsForm`; field errors and submitted values return from Django; notification/SMS/email limitations remain disclosed. |
| `/portal/guide/` | `GuidePage` | Existing safe topic cards and internal links; read-only. |
| `/portal/messages/` | `MessagesPage` | Active-term teacher choices and account-scoped message history; POST `receiver`, `subject`, `message_body` remains local-only, not external delivery. |
| `/portal/support/` | `SupportPage` | Account-owned support tickets/replies; POST `category`, `subject`, `content`; no attachment support is claimed. |
| `/portal/academic-activities/` | `AcademicPage` | Selected-term enrollment summary, persisted student change history, and existing route links. |
| `/portal/transcript/` | `AcademicPage` | Selected-term active enrollments and persisted grades; browser print; no fabricated term GPA. |
| `/portal/curriculum/` | `AcademicPage` | Student-field curriculum and progress computed by existing selectors; route links preserved. |
| `/portal/enrollment/` | `EnrollmentPage` | Current student/term preflight information; stage-one route and server-controlled continuation preserved. |
| `/portal/selected-courses/` | `SelectedCoursesPage` + `OfferingPicker` | Active registrations; offerings from scheduling GET; registration via existing enrollment POST and server result route. Tuition remains undisclosed when no tariff exists. |
| `/portal/add-drop/` | `CourseChangesPage` + `OfferingPicker` | Active registration rows; course registration/drop APIs, confirmation dialogs, and scoped result refresh. No refund is claimed. |
| `/portal/emergency-drop/` | `CourseChangesPage` | Owned active registration rows; emergency-drop API and window validation remain authoritative; no refund is claimed. |
| `/portal/registration-status/` | `RegistrationStatusPage` | Existing four-stage summary from the student record; final approval/settlement is not invented. |
| `/portal/attendance/` | `AttendancePage` | Scoped active enrollments and attendance totals; read-only, teacher contact remains on the existing messages route. |
| `/portal/calendar/` | `CalendarPage` | Selected-term dates, active-course exams, and attendance sessions; Persian calendar display, read-only. |
| `/portal/exam-card/` | `ExamCardPage` | Explicit student and active-enrollment exam fields; missing seat number/card issuance remain disclosed and unavailable. |
| `/portal/schedule/` | `SchedulePage` | Active selected-term courses, weekly time grid, conflict summary, and browser print; read-only. |
| `/portal/evaluation/` | `EvaluationPage` | Scoped active-term course/survey status; route parameters retained when opening a course form. |
| `/portal/evaluation-form/` | `EvaluationFormPage` | Existing five required ratings plus optional comment; Django validation/submit remains authoritative and no post-submit edits are offered. Anonymity is not promised. |
| `/portal/grade-appeal/` | `GradeAppealPage` | Existing grade-bearing enrollment choices, request form, status/result table; deadline and attachment limitations remain disclosed. |
| `/portal/internship/` | `StudentServicePage` | Existing internship fields and owner-scoped history/result; external university submission and approval are not claimed. |
| `/portal/guest-request/` | `StudentServicePage` | Destination-only transfer form and scoped request history; missing PDF fields remain disclosed. |
| `/portal/financial-aid/` | `StudentServicePage` | Existing scholarship type/reason form, local status/result; no award or payment is implied. |
| `/portal/requests/` | `StudentServicePage` | Existing local service-request form and owner-scoped history; contact, attachment, and university forwarding remain unavailable. |
| `/portal/education-certificate/` | `StudentServicePage` | Configured employment-certificate request only; if its lookup is absent, submission remains disabled. |
| `/portal/graduation/` | `StudentServicePage` | Recorded checks and audit history; formal eligibility is not newly calculated. |
| `/portal/graduation-certificate/` | `StudentServicePage` | Explicit student/curriculum/audit summary; official clearance and document issuance remain unavailable. |
| `/portal/payments/` | `FinancePage` | Payment rows and failed-payment notice scoped to the selected student and term; read-only. |
| `/portal/secure-payment/` | `FinancePage` | Current student's debt and payment preview; payment remains disabled because no gateway is connected. |
| `/portal/tuition/` | `FinancePage` | Successful payments grouped by term and current-student debt summary; read-only. |
| `/login/` | `LoginPage` | Existing server-side login POST and authentication behavior; no React-side credential handling. `?legacy=1` selects the compatibility login. |

The announcement/notification read actions remain server-authoritative and return through the existing page route. The payload contains only the fields used by these views; it does not include sender/receiver objects or unrelated model columns.

## Route coverage and remaining acceptance

All 33 current entries in `apps/core/frontend/registry.py` have a corresponding React route and explicit `PageRenderer` dispatch; a source inventory found no missing or extra slugs. `PageRenderer` now fails closed for an unmapped slug rather than showing the generic renderer. Every page-data key read by the page components has a corresponding common/page allowlist or explicit adapter output.

Course registration dialogs keep keyboard focus inside the active dialog, support Escape/backdrop cancellation when no mutation is in flight, and restore focus to the opener or safe close control. All 33 registered routes now default to React; `?legacy=1` remains an explicit compatibility escape hatch. Visual equivalence has not been accepted. Do not infer PDF parity or business-rule acceptance from route coverage or build success.

## Verification state

- React TypeScript check: passed for the current source.
- Vite production build: passed; the latest continuation build emitted `app.js` and `style.css` under `static/core/react-build/` and resolved them through Django static-file lookup (module count and output sizes are recorded in the current verification section of `docs/TEST_REPORT.md`).
- Python syntax check: passed for the view, form, API, and explicit payload serializer modules.
- Django system check: passed; registered route-to-renderer source inventory is checked separately from test suites.
- Login, shell, and error-state source checks: default login returns to the React dashboard; `?legacy=1` survives successful login and the compatibility shell preserves profile/term query values. CSRF, profile, term, and compatibility query handling remains present in the shared shell.
- The read endpoint and write endpoint are separate: `ui-page` serves JSON GETs; `page` handles existing POST actions.
- Automated test suites and authenticated visual parity review remain deferred to the user's later QA phase. The PDF visual cursor remains at page 9; no visual approval is implied by a successful build.

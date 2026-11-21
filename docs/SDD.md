# SDD — Amoozeshyar (Software Design Document) v2.1

Source: `نیازمندی_های_آموزشیار.md` (152 approved requirements). Requirement text stays in the source file; this document references codes only. Rows are numbered (#) because some codes repeat (e.g. NFRP01) or differ only by case (fuop02/FUOP02); cite `#` + code when ambiguous.

## 1. Scope
A university education portal for students, professors, education staff, student-affairs staff, scholarship/thesis officers and system admins. Only capabilities present in the requirements are in scope; nothing else is to be invented.

## 2. Architecture overview
Django monolith.
- `apps/core/models.py` — ALL models. `apps/core/admin.py` — admin panel.
- Each feature is a sub-app under `apps/core/<feature>/` with its own `views.py` and `urls.py` when it exposes behavior. Add templates, forms, or serializers only when a user-facing flow requires them. Register every feature in `INSTALLED_APPS` and root urls.
- Sub-apps:
- `apps/core/enrollment/` — Course registration, drop/add, schedules (18 reqs)
- `apps/core/tuition/` — Tuition, payments, loans, refunds (10 reqs)
- `apps/core/grading/` — Grades, GPA, probation (12 reqs)
- `apps/core/requests/` — Administrative requests and student records (17 reqs)
- `apps/core/scheduling/` — Terms, windows, class offerings (7 reqs)
- `apps/core/attendance/` — Attendance (3 reqs)
- `apps/core/classroom/` — Class content, announcements, reviews (6 reqs)
- `apps/core/tickets/` — Support tickets (1 reqs)
- `apps/core/online_exam/` — Online exams/meetings (2 reqs)
- `apps/core/people/` — Student/professor management (4 reqs)
- `apps/core/student_services/` — Meals, dormitory, other services (3 reqs)
- `apps/core/notifications/` — News and notifications (2 reqs)
- `apps/core/thesis/` — Thesis/proposal workflow (11 reqs)
- `apps/core/accounts/` — Authentication, sessions, roles (3 reqs)
- `apps/core/counseling/` — Advisor/counseling sessions (6 reqs)
- `apps/core/reports/` — Reports (PDF/Excel) (1 reqs)
- `apps/core/internship/` — Internship (5 reqs)
- `apps/core/scholarships/` — Scholarships (6 reqs)

The feature assignment is an existing traceability decision. Review it against the original behavioral text when that source is restored.

The backend foundation exposes same-origin JSON endpoints under `/api/<feature>/`. Browser clients bootstrap CSRF with `/api/accounts/csrf/`; state-changing routes use Django sessions and CSRF middleware. The route and payload contract is maintained in `SSOT.md` §4.

## 3. Design by requirement group
- Input (ورودی) → forms/endpoints with validation. Output (خروجی) → read views. Operation (عملیات) → state-changing services. Data (داده), accuracy (دقت) → model constraints and validation.
- Dependent requirements ("وابسته", column Ref) are implemented inside the same sub-app as the referenced main requirement, after it.
- Request-style workflows (admin requests, scholarship, proposal, counseling, credit transfer, leave, withdrawal, major change, graduation) are intended to follow student submission → `submitted` → `in_review` → `approved`/`rejected` → status view. Existing models have a review transition service; submission and student status views await the original behavior source.
- Registration rules (prerequisite, conflict, capacity, windows, credit limit) live in a service layer in `enrollment/services.py`; register and drop run in a DB transaction (#132, #133).

## 4. Non-functional design (see ADR)
Cross-cutting items (rows with type غیرعملیاتی, plus a few functional-code rows classed there) map to: security (encryption, TLS, session timeout, lockout, role-based access, session invalidation on password change), performance (≤2–3 s responses, 1000 concurrent users, caching, background jobs for non-urgent work), reliability (99% availability in registration/grading, daily backup, transactions, idempotent submissions, graceful degradation of SMS etc., error logging), usability (Persian, RTL, Jalali calendar, responsive, accessibility, clear errors), maintainability (technical docs).

## Implementation readiness (2026-11-18)

- The source `نیازمندی_های_آموزشیار.md` is referenced as the authority for behavior but is absent from the repository and searched workspace.
- This SDD contains 152 identifiers and metadata rows, not the full behavioral language. Do not infer domain rules solely from those codes.
- Backend work in this checkout is limited to contracts stated explicitly in SSOT/ADR and rules supported by existing models. Assumptions and unimplemented areas are recorded in ADR.md and PROJECT_STRUCTURE.md.
- A Persian/RTL server-rendered student portal is implemented. Login and logout use the existing account/session flow, page data is read for the authenticated student's selected profile, and course registration/drop actions use the existing APIs. Remaining feature/API gaps are listed in `PROJECT_STRUCTURE.md`.

## 5. Traceability (all 152 requirements)

The traceability tables are split by domain under [`docs/sdd/traceability/`](sdd/traceability/). Row numbers, codes, and table data are preserved verbatim so this overview stays navigable.

These tables identify requirement ownership and priority; they do not contain each requirement's behavioral text. Use the original requirements file when available, and cite `#` plus code when identifiers repeat or differ only by case.

| Domain | Area | Table | Rows |
|---|---|---|---:|
| enrollment | Course registration, drop/add, schedules | [traceability/enrollment.md](sdd/traceability/enrollment.md) | 18 |
| tuition | Tuition, payments, loans, refunds | [traceability/tuition.md](sdd/traceability/tuition.md) | 10 |
| grading | Grades, GPA, probation | [traceability/grading.md](sdd/traceability/grading.md) | 12 |
| requests | Administrative requests and student records | [traceability/requests.md](sdd/traceability/requests.md) | 17 |
| scheduling | Terms, windows, class offerings | [traceability/scheduling.md](sdd/traceability/scheduling.md) | 7 |
| attendance | Attendance | [traceability/attendance.md](sdd/traceability/attendance.md) | 3 |
| classroom | Class content, announcements, reviews | [traceability/classroom.md](sdd/traceability/classroom.md) | 6 |
| tickets | Support tickets | [traceability/tickets.md](sdd/traceability/tickets.md) | 1 |
| online_exam | Online exams/meetings | [traceability/online-exam.md](sdd/traceability/online-exam.md) | 2 |
| people | Student/professor management | [traceability/people.md](sdd/traceability/people.md) | 4 |
| student_services | Meals, dormitory, other services | [traceability/student-services.md](sdd/traceability/student-services.md) | 3 |
| notifications | News and notifications | [traceability/notifications.md](sdd/traceability/notifications.md) | 2 |
| thesis | Thesis/proposal workflow | [traceability/thesis.md](sdd/traceability/thesis.md) | 11 |
| accounts | Authentication, sessions, roles | [traceability/accounts.md](sdd/traceability/accounts.md) | 3 |
| counseling | Advisor/counseling sessions | [traceability/counseling.md](sdd/traceability/counseling.md) | 6 |
| reports | Reports (PDF/Excel) | [traceability/reports.md](sdd/traceability/reports.md) | 1 |
| internship | Internship | [traceability/internship.md](sdd/traceability/internship.md) | 5 |
| scholarships | Scholarships | [traceability/scholarships.md](sdd/traceability/scholarships.md) | 6 |
| nfr | Cross-cutting non-functional requirements | [traceability/nfr.md](sdd/traceability/nfr.md) | 35 |

## 6. Open points
- Contradictory/ambiguous items to confirm with the owner: #145 (separate server per university unit) vs monolith; #135 says AES for passwords while NFSP01 says encrypted storage (passwords are normally hashed, not AES-encrypted); duplicate codes noted above.

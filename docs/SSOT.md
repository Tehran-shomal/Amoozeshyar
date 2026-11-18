# SSOT — Amoozeshyar (Single Source of Truth) v2.0

Rule: this file defines names and contracts. If another document or code disagrees, this wins, unless the requirements file `نیازمندی_های_آموزشیار.md` says otherwise.

## 1. Sources
1. `نیازمندی_های_آموزشیار.md` — requirements (152). Authoritative for behaviour.
2. This file — structure and naming.
3. `ADR.md` — rationale for decisions.
4. `PROJECT_STRUCTURE.md` — the real current layout, produced by the agent (see `AGENT_INSTRUCTIONS.md`).

## 2. Project layout
```
apps/
  core/
    models.py        # the only place models are defined
    admin.py         # admin panel for all models
    <feature>/       # views, urls, templates, forms, services, tests
```
Features (registered sub-apps):
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

## 3. Conventions
- Requirement code is the key; write it in docstrings/tests, e.g. `# FUFP01`. When a code repeats, add the # from SDD.
- Dependent requirement lives in the same sub-app as its Ref code.
- Backend URLs: `/api/<feature>/...`; route names are namespaced by feature.
- Roles: student, professor/advisor, education officer, student-affairs officer, scholarship officer, admin (role-based access: FUOP16).
- Dates shown in Jalali; stored in UTC/Gregorian. UI Persian, RTL.
- Request workflow status enum: `submitted`, `in_review`, `approved`, `rejected`. Add `cancelled` only when the relevant behavior requirement allows it. Existing `pending` records are legacy submitted requests.
- Registration/drop operations are atomic transactions.
- DateTimeField values are timezone-aware and stored in UTC; user-facing dates remain Gregorian in the API until a Jalali presentation layer is specified.

## 4. Backend contracts implemented in this checkout
- JSON API errors use `{"error":{"code":"...","message":"..."}}`.
- Browser clients call `GET /api/accounts/csrf/` first, retain the `csrftoken` cookie, send its value in `X-CSRFToken` on unsafe requests, and retain the session cookie after login. Use same-origin requests; cross-origin credentials are not configured.
- Login uses the Django `Person` password hash. `UserAccount.password` is not an authentication source.
- Session idle lifetime is 900 seconds, refreshed on requests. Login lockout is five consecutive failures for 900 seconds; both values are configurable in Django settings.
- Enrollment mutation routes require a session and the student role; they resolve the acting user's own Student record.
- Request-review transitions require a session and a role mapped to the request type. Only existing request models are registered; request submission and student status-list endpoints are not implemented by this backend foundation.

### API surface

| Method and path | Access and contract |
|---|---|
| `GET /api/accounts/csrf/` | Public; sets the CSRF cookie and returns `{"csrf_token":"..."}`. |
| `POST /api/accounts/login/` | CSRF-protected; accepts `username` and `password`; starts a session and returns the safe user summary. |
| `POST /api/accounts/logout/` | Authenticated session; ends the session. |
| `GET /api/accounts/me/` | Authenticated session; returns the safe user summary. |
| `GET /api/scheduling/active-term/` | Public read; returns the active term and registration-window flags, or `null`. |
| `GET /api/scheduling/offerings/` | Public read; returns active offerings for the active term. |
| `POST /api/enrollment/register/<offering_id>/` | Student session; no body; returns the resulting enrollment. |
| `POST /api/enrollment/drop/<enrollment_id>/` | Owning student session; no body; returns the resulting enrollment. |
| `POST /api/requests/<request_type>/<request_id>/review/` | Reviewer session; accepts `target_status` (`in_review`, `approved`, or `rejected`). Registered request types: `student-service`, `scholarship-application`, `proposal`, `transfer`, `credit-transfer`, `internship-request`, `internship`, `refund`, `grade-appeal`, `thesis-progress-report`. |

## 5. Entities and model coverage
The current inventory of models is in `PROJECT_STRUCTURE.md`; all current model classes remain in `apps/core/models.py` and admin registrations remain in `apps/core/admin.py`. Reuse those entities before adding a model.

The following SSOT concepts are not represented by a dedicated current model: `WaitlistEntry`, `EnrollmentWindow`, `TuitionAccount`, `Installment`, `Loan`, generic `AdminRequest`, profile-correction/leave/withdrawal/major-change/graduation requests, `Scholarship`, meal reservation, dorm request, and `AuditLog`/`ErrorLog`. The original behavior requirements are needed before designing these schemas. Existing related models such as `StudentServiceRequest`, `RefundRequest`, `CreditTransferRequest`, `ScholarshipApplication`, `Proposal`, and `InternshipRequest` must be checked before adding alternatives.

## 6. Traceability
The full code-to-module index is in `SDD.md` §5; the 19 domain tables are split under `docs/sdd/traceability/`. They preserve all 152 row identifiers but do not replace the missing behavioral requirement source.

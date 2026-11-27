# Amoozeshyar Project Structure

This document began as a snapshot of the master baseline (1896c3c) and is updated as the project changes. It describes the current checkout, then compares it with docs/SSOT.md, docs/SDD.md, and docs/ADR.md.

## Repository layout

    Amoozeshyar/
    ├── apps/
    │   └── core/
    │       ├── management/commands/  seed.py, seed_data.py
    │       ├── migrations/           0001_initial.py–0005_person_failed_login_count_person_locked_until.py
    │       ├── templates/core/       database_unavailable.html, live_content.html, portal_base.html, section.html
    │       ├── frontend/             shared helpers and seven team-owned page modules
    │       ├── admin.py
    │       ├── apps.py
    │       ├── models.py
    │       ├── tests.py
    │       ├── urls.py
    │       └── views.py
    ├── config/                       Django settings, root URLs, ASGI, WSGI
    ├── README.md                     setup, API, verification, and scope guide
    ├── docs/                         AGENT_INSTRUCTIONS.md, SSOT.md, ADR.md, SDD.md
    │   └── sdd/traceability/         19 split tables, all 152 rows preserved
    ├── media/                        empty except .gitkeep
    ├── static/                       shared static root
    │   └── core/                     portal.css, responsive.css, portal_api.js, live_portal.js, tests/
    ├── templates/                    base.html
    ├── .env.example
    ├── manage.py
    ├── requirements.txt
    └── seed_data.py                  root-level data generator

The backend baseline had no frontend bundles or static assets and no feature sub-apps, API framework, serializers, or shared service modules. Task 1 added the 18 SSOT feature packages; Tasks 2–4 added account, scheduling, enrollment, and existing-model request-review APIs/services. The current checkout includes the PDF-aligned, server-rendered portal, connected to the current account, enrollment, scheduling, and request services. `apps/core/models.py.backup` is a tracked older model draft; it is not imported by Django.

The registered feature packages are apps/core/enrollment, tuition, grading, requests, scheduling, attendance, classroom, tickets, online_exam, people, student_services, notifications, thesis, accounts, counseling, reports, internship, and scholarships. Each has __init__.py, apps.py, and urls.py. Accounts, enrollment, scheduling, and requests also have service/view modules and automated tests; the other feature packages are route namespaces for now.

## Django configuration and routing

- Django version pinned in requirements.txt: 5.2.18. Other direct dependencies: django-environ, asgiref, sqlparse, and typing_extensions.
- INSTALLED_APPS contains Django admin/auth/contenttypes/sessions/messages/staticfiles, apps.core, and the 18 feature AppConfigs listed in docs/SSOT.md.
- AUTH_USER_MODEL is core.Person.
- Database engine is SQLite at db.sqlite3.
- USE_TZ is True; TIME_ZONE is Asia/Tehran and language is fa-ir. Migration 0004 converts retained naive datetimes only when `LEGACY_DATETIME_TIME_ZONE` is explicitly set; otherwise it aborts before changing rows. The ignored working database contains legacy seed rows and remains untouched; 0004 was checked on a temporary copy.
- Root URLs: /admin/ is Django admin, / includes apps.core.urls, and /api/<feature>/ includes each registered feature URLConf.
- Browser routes: / renders the signed-in student's dashboard, /login/ authenticates a student account, and named paths under /portal/ render pages owned by the team modules. The session login/logout and course register/drop actions use existing account and enrollment APIs. Each page reads its current records through the corresponding team selector; absent records produce an empty state.
- Implemented routes: GET /api/accounts/csrf/, POST /api/accounts/login/, POST /api/accounts/logout/, GET /api/accounts/me/, GET /api/scheduling/active-term/, GET /api/scheduling/offerings/, POST /api/enrollment/register/<offering_id>/, POST /api/enrollment/drop/<enrollment_id>/, and POST /api/requests/<request_type>/<request_id>/review/.
- Middleware is Django's security, session, common, CSRF, authentication, messages, and clickjacking middleware. No project-specific middleware is present.
- Session cookies expire after 900 seconds and are refreshed per request; production cookies are marked Secure when DEBUG is False. Account lockout is configured for five failed attempts and 900 seconds.
- `Person.username` takes precedence over a colliding `UserAccount.username`; failed-login lockout is shared across aliases on the earliest active role account, with `Person` fields covering superusers without an active role account.
- Enrollment mutations accept an optional `student_code` body field when one Person owns multiple Student records. Probation and legacy `suspended` status impose a 14-unit cap, further limited by `Student.max_allowed_units`; repeated registration returns HTTP 200.
- Media and static roots are configured. `templates/base.html` provides the shared Persian/RTL document shell; `apps/core/templates/core/portal_base.html` provides the portal shell and semester picker. Shared assets live in `static/core/`; team scripts live beside their owner modules and are registered only where they exist.

## Models and relations

All 43 current model classes are defined in apps/core/models.py; there are no feature-local model files. Relation targets are shown after ->. Person also inherits Django AbstractUser fields and its groups and permissions many-to-many relations.

| Model | Fields and relations |
|---|---|
| Constant | constant_id, category, code, label, is_active, created_at |
| Person | AbstractUser fields; first_name, last_name, email, national_id, birth_date, gender -> Constant, address, profile_image_path, preferred_language -> Constant, is_notification_enabled, birth_place, failed_login_count, locked_until, updated_at |
| Teacher | person -> Person, teacher_code, department -> Department, academic_rank -> Constant, hire_date |
| Student | person -> Person, student_code, educational_level -> Constant, field -> Field, application_date, status -> Constant, admission_type -> Constant, previous_term_gpa, total_gpa, passed_units, tuition_debt, completed_terms |
| Lesson | lesson_code, title, practical_units, theory_units, lesson_type -> Constant, department -> Department, is_active, created_at |
| Term | term_code, semester -> Constant, academic_year, start_date, end_date, registration_start/end, add_drop_start/end, emergency_drop_start/end, is_active |
| Payment | term -> Term, amount, payment_date, tracking_code, student -> Student, status -> Constant, created_at |
| Exam | offering -> CourseOffering, exam_date, exam_type -> Constant |
| LessonGroups | id, name, created_at, created_by -> Person, members -> M2M Person, teacher -> Teacher, is_active |
| ParkingPasses | id, parking_pass_code, aquisition_date, expiration_date, charge, owner -> Person |
| Role | role_name, description, created_at, is_active |
| UserAccount | person -> Person, role -> Role, username, password, created_at, is_active, failed_login_count, locked_until, last_login_at, last_activity_at, password_changed_at |
| Prerequisite | prereq_id, lesson -> Lesson, prerequisite_lesson -> Lesson, prerequisite_type -> Constant, created_at |
| Classroom | building_name, room_number, capacity, classroom_type |
| CourseOffering | lesson -> Lesson, term -> Term, teacher -> Teacher, capacity, day_of_week -> Constant, start_time, end_time, classroom -> Classroom, exam_date, exam_time, is_active, created_at |
| Enrollment | EnrollmentId, student -> Student, offering -> CourseOffering, enrollment_date, status -> Constant, enrollment_type -> Constant, drop_date |
| Grade | enrollment -> Enrollment, score |
| GradeAppeal | enrollment -> Enrollment, appeal_reason, appeal_date, appeal_status -> Constant |
| Attendance | enrollment -> Enrollment, session_number, session_date, attendance_status -> Constant, attendance_time, description, recorded_by -> UserAccount, created_at |
| TicketCategory | category_id, name, parent -> TicketCategory, is_active, created_at |
| Ticket | creator -> Person, creator_role -> Constant, category -> TicketCategory, subject, content, parent -> Ticket, status -> Constant, assigned_to -> Person, created_at, updated_at |
| OnlineClass | teacher -> Teacher, offering -> CourseOffering, start_at, end_at, title, meeting_link |
| TuitionReceipt | tuition_receipt_key, receipt_serial_code, receipt_payment_link -> Payment, receipt_issued_on, receipt_document_uri |
| RefundRequest | refund_case_key, refund_payment_link -> Payment, refund_value_requested, refund_justification_text, refund_review_state -> Constant |
| StudentServiceRequest | student_service_case_key, service_requester -> Student, service_request_kind -> Constant, service_request_data, service_decision_state -> Constant |
| ScholarshipApplication | scholarship_application_key, scholarship_applicant -> Student, scholarship_type, scholarship_reason, scholarship_status -> Constant, scholarship_submitted_at |
| CounselingAppointment | counseling_appointment_key, counseling_student_link -> Student, counseling_teacher_link -> Teacher, counseling_date, counseling_topic, counseling_description, counseling_status -> Constant |
| Proposal | proposal_case_key, proposal_student_link -> Student, proposal_title, proposal_description, proposal_submitted_at, proposal_status -> Constant |
| TransferRequest | transfer_id, student -> Student, destination_university, review_status -> Constant, course_compatibility_result, created_at |
| GraduationAudit | audit_id, student -> Student, curriculum -> Curriculum, graduation_status -> Constant, audit_date |
| EducationalChangeLog | log_id, student -> Student, change_type -> Constant, changed_by -> UserAccount, changed_at, description |
| Curriculum | curriculum_id, field -> Field, lesson -> Lesson, requirement_type -> Constant, recommended_term, calculated_units, is_active, created_at |
| Communication | communication_id, sender -> UserAccount, receiver -> UserAccount, subject, message_body, communication_type -> Constant, status -> Constant, sent_at, is_read, read_at |
| SystemSetting | setting_id, setting_key, setting_value, data_type -> Constant, description, updated_at, updated_by -> UserAccount |
| CreditTransferRequest | transfer_request_id, student -> Student, source_university, request_date, status -> Constant |
| InternshipRequest | internship_request_id, student -> Student, organization_name, start_date, status -> Constant |
| ThesisProgressReport | report_id, student -> Student, teacher -> Teacher, report_content, review_status -> Constant |
| Notification | user -> UserAccount, title, message, related_exam -> Exam, notification_type -> Constant, sent_at, is_read, read_at, created_at |
| TeacherSurvey | enrollment -> Enrollment, overall_rating, teaching_quality, behavior, submitted_at, comment, created_at |
| Internship | student -> Student, request_type -> Constant, company_name, intern_start_date, duration_hours, status -> Constant, reviewed_by -> UserAccount, reviewed_at, created_at |
| Faculty | faculty_name, faculty_code, is_active, created_at |
| Department | faculty -> Faculty, department_name, department_code, is_active, created_at |
| Field | department -> Department, field_name, field_code, is_active, created_at |

The models include validation/constraints for positive payment/refund amounts and offering capacity, lesson units, offering/online-class time order, one active term, unique student/offering enrollment, and survey ratings. Some models also expose computed properties; see StudentAcademicRules below.

## Admin registrations

All 43 models are registered in apps/core/admin.py. The admin customizes Person, Student, Teacher, Lesson, Term, CourseOffering, Enrollment, Prerequisite, Curriculum, Faculty, Department, Field, Classroom, Payment, TuitionReceipt, RefundRequest, Exam, Grade, GradeAppeal, Attendance, Ticket, TicketCategory, Constant, SystemSetting, Communication, Notification, StudentServiceRequest, ScholarshipApplication, CounselingAppointment, Proposal, TransferRequest, GraduationAudit, EducationalChangeLog, CreditTransferRequest, InternshipRequest, ThesisProgressReport, TeacherSurvey, Internship, OnlineClass, LessonGroups, and ParkingPasses. Person exposes the service-managed login lockout fields as read-only; Role and UserAccount use default admin registration.

## Views, templates, utilities, and conventions

- Core views: HomeView, LoginPreviewView, and PortalSectionView in `apps/core/frontend/views.py`, re-exported by `apps/core/views.py`. Feature JSON views are in accounts, enrollment, scheduling, and requests.
- Templates: `templates/base.html` is the shared document shell; `apps/core/templates/core/portal_base.html` is the shared portal shell; `core/live_content.html` renders common data/forms; `core/section.html` provides page headings and breadcrumbs. Mobina owns login and dashboard templates; the lead team owns the custom notification renderer. Generic content wrappers and empty per-team CSS files are not kept.
- Static assets: `static/core/portal.css` and `responsive.css` provide the shared RTL design; `portal_api.js` and `live_portal.js` provide shared API and interface behavior. Mobina and Shaghayegh own the registration/drop scripts. Node suites live in `static/core/tests/`.
- Shared/domain utilities: StudentAcademicRules; computed properties on Person, Teacher, Student, Term, CourseOffering, ParkingPasses, Ticket, OnlineClass, TransferRequest, GraduationAudit, and EducationalChangeLog; apps/core/api.py provides JSON object parsing and stable JSON errors; accounts services authenticate Person and resolve roles/current student records; enrollment services enforce transactional register/drop rules; scheduling services provide active-term/offering reads; request services register existing request models and validate review transitions. Account and enrollment mutations use session/role checks; review roles are selected by request type.
- Management commands: seed creates deterministic Persian development data and refuses to run unless DEBUG=True; seed_data generates sample rows for models. There is also a root seed_data.py.
- Tests: `apps/core/test_frontend.py` covers team page ownership, rendering, data isolation, and live request flows. `apps/core/test_architecture.py` covers feature registration, URL mounting, legacy datetime compatibility, JSON parsing, and JSON error responses. Account, enrollment, scheduling, and request tests cover their APIs. Browser API and team bindings are covered by the Node suites under `static/core/tests/`.
- Migrations: 0001_initial.py defines the baseline model schema; 0002_enrollment_statuses.py seeds registered/dropped enrollment statuses; 0003_request_workflow_statuses.py seeds workflow statuses; 0004_legacy_datetime_utc.py converts retained naive datetime values using the explicitly configured source timezone; 0005_person_failed_login_count_person_locked_until.py adds persistent lockout state for superusers without a role account.
- Existing style: Django models and admin use Persian verbose labels, English identifiers, a custom Person user, and Constant(category, code, label) lookup values. No repository-wide formatter or linter configuration is present.

## Gaps against SSOT, SDD, and ADR

- docs/SSOT.md and docs/SDD.md describe 18 feature sub-apps and 152 requirements. The feature app namespaces now exist; model definitions and admin registrations remain centralized under apps.core.
- The SDD maps requirement codes to features but does not include the original behavioral text. The referenced نیازمندی_های_آموزشیار.md is absent from the repository and searched project workspace, so traceability rows cannot establish all 152 behaviors. SDD §5 now links 19 smaller domain tables under docs/sdd/traceability/; row numbers and identifiers were preserved.
- Feature model coverage is partial. Existing entities include enrollment, scheduling, grades, attendance, payments/refunds, tickets, online classes, people, service and scholarship applications, counseling, thesis proposals/reports, internships, notifications, and educational history. Missing entities explicitly listed in SSOT include WaitlistEntry, TuitionAccount, Installment, Loan, generic AdminRequest, profile correction/leave/withdrawal/major change/graduation requests, Scholarship, MealReservation, DormRequest, AuditLog, and ErrorLog.
- Account, enrollment, scheduling, and existing-model request review APIs/services are implemented. Request submission/status-list endpoints, tuition, grading, and remaining domains are not implemented. Automated architecture, account, enrollment, scheduling, and request tests exist.
- Frontend ownership is split across seven current code groups defined by `docs/TEAM_OWNERSHIP.md`; `NAV_GROUPS` remains the product navigation and is not a team grouping. Each owner manifest in `apps/core/frontend/<owner>/pages.py` owns its routes; selectors/forms/templates stay with that owner where specialized. Historical five-group design notes are superseded by the 2076-05-07 seven-owner design.
- ADR-002/003 specify registration services, atomic register/drop, capacity locking, prerequisite/conflict/credit-limit/window checks. The enrollment service now applies those rules; exact-time exam collisions are used because the current model has no exam duration.
- ADR-005 and SSOT call for role-based access, session timeout/lockout, and hashed passwords. The account API authenticates Person through Django's hashers and requires non-superusers to have an active UserAccount; it does not use the separate UserAccount.password field. Session expiry, 5-attempt/15-minute lockout, and role checks are implemented. TLS, sensitive-field encryption, password-change session invalidation, and production cookie setup remain deployment/security work.
- `manage.py check --deploy` reports `security.W004` (HSTS is not configured) and `security.W008` (SSL redirect is not enabled). Configure these at deployment after confirming the HTTPS/reverse-proxy topology.
- Enrollment allows active and probation students; the legacy `suspended` code from the root seed is treated as probation. Probation status caps the load at 14 units, further limited by `Student.max_allowed_units`. On-leave students cannot enroll. It assumes 10/20 is a passing grade and treats exams at the same date and exact time as conflicts because the model has no duration. The latter rules are tested and documented in ADR-002 pending the original requirements source.
- Request reviews use request-type role mappings, accept `pending` as a legacy state, and do not expose `cancelled`; verify these choices against the missing behavioral requirements.
- The local SQLite database is ignored and not included in the change; it contains legacy seed rows and was left untouched. Migration 0004 was exercised on a temporary copy with and without an explicit source timezone. ADR mentions TLS, background work, caching, backups, and availability; deployment and integration behavior remains unconfigured.
- The project uses SQLite, so database-level row-lock behavior required by ADR-003 is not available in production-equivalent form.
- SDD says SDD.md; this is the file present in the checkout (the user referred to it as SSD.md).

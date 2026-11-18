# Backend Foundation Implementation Plan

> For agentic workers: use superpowers:executing-plans and implement each task in order. Steps use checkbox syntax.

**Goal:** Build a tested, headless backend foundation on the existing Django project for accounts, enrollment, scheduling, and request review.

**Architecture:** Keep the current monolith, centralized models/admin, and Django session authentication. Add the SSOT feature packages, expose a small Django-native JSON API, and place business rules in feature service modules.

**Tech Stack:** Python, Django 5.2.18, Django auth/sessions/JsonResponse, Django TestCase; no new dependencies.

**Spec:** docs/superpowers/specs/2026-11-18-backend-foundation-design.md

## Global Constraints

- Keep all models in apps/core/models.py and all admin registrations in apps/core/admin.py.
- Do not rename, move, or delete existing models, fields, or files.
- Create feature apps under apps/core/<feature>/ and register them in INSTALLED_APPS and root URLs.
- Add no third-party dependencies.
- Preserve Django CSRF middleware and use the configured Person model for authentication.
- Cite requirement codes in service docstrings/tests; disambiguate repeated codes with SDD row numbers.
- Do not invent models or domain rules for which the requirements text is missing.

## Review Focus

- Five consecutive failed logins lock an account for 15 minutes; valid credentials after lock expiry work. Test in Task 2.
- A valid registration is idempotent and cannot exceed an offering's remaining capacity. Test in Task 3.
- A student cannot register without prerequisites, with a debt, beyond the credit limit, or during a closed window. Test in Task 3.
- Weekly and exam conflicts are rejected without creating an enrollment. Test in Task 3.
- Review transitions reject invalid source/target states, missing constants, and unauthorized roles. Test in Task 4.

---

### Task 1: Feature app structure and JSON helpers

**Files:**
- Create: apps/core/<feature>/__init__.py and apps.py for all 18 SSOT feature names
- Create: apps/core/<feature>/urls.py for all 18 SSOT feature names
- Create: apps/core/api.py
- Create: apps/core/test_architecture.py
- Modify: config/settings.py
- Modify: config/urls.py
- Modify: PROJECT_STRUCTURE.md

**Interfaces:**
- Produces app labels and URL namespaces for enrollment, tuition, grading, requests, scheduling, attendance, classroom, tickets, online_exam, people, student_services, notifications, thesis, accounts, counseling, reports, internship, and scholarships.
- Produces api.read_json(request) -> dict and api.error_response(code, message, status) -> JsonResponse.

- [ ] Step 1: Write test_expected_feature_apps_are_registered_and_mounted in apps/core/test_architecture.py. Assert every feature label is in apps.get_app_configs() and every /api/<feature>/ prefix exists in the root URL resolver.
- [ ] Step 2: Run .venv/Scripts/python.exe manage.py test apps.core.test_architecture. Expected: FAIL because feature apps and routes are missing.
- [ ] Step 3: Create the 18 feature packages, register AppConfigs, and include their URLConfs under /api/<feature>/ in config/urls.py. Keep unfinished feature URL patterns empty.
- [ ] Step 4: Write tests for read_json accepting a JSON object and returning a stable 400 error for malformed JSON or non-object JSON.
- [ ] Step 5: Implement the shared JSON parsing and error response helpers in apps/core/api.py.
- [ ] Step 6: Run .venv/Scripts/python.exe manage.py test apps.core.test_architecture. Expected: PASS.
- [ ] Step 7: Run .venv/Scripts/python.exe manage.py check. Expected: no system-check issues.
- [ ] Step 8: Update PROJECT_STRUCTURE.md with the feature app and route inventory; commit this task.

### Task 2: Account API and session security

**Files:**
- Create: apps/core/accounts/services.py
- Create: apps/core/accounts/permissions.py
- Create: apps/core/accounts/views.py
- Create: apps/core/accounts/test_services.py
- Modify: apps/core/accounts/urls.py
- Modify: config/settings.py
- Modify: apps/core/management/commands/seed.py

**Interfaces:**
- Produces authenticate_person(username, password, request) -> Person | None.
- Produces role_codes_for(person) -> set[str], user_has_any_role(person, roles) -> bool, and current_student(person, student_code=None) -> Student.
- Produces POST /api/accounts/login/, POST /api/accounts/logout/, and GET /api/accounts/me/.

- [ ] Step 1: Write tests for successful login, invalid credentials, fifth-failure lockout, locked account rejection, lock expiry, current-user output, and role mapping. Cite FUIP09, #85 FUSP07, #126 NFSP11, #129 FUOP16, and #140 NFSP13.
- [ ] Step 2: Run .venv/Scripts/python.exe manage.py test apps.core.accounts.test_services. Expected: FAIL because the account service and routes are missing.
- [ ] Step 3: Implement login using Django authenticate/login against Person, update UserAccount counters without reading UserAccount.password, and return stable JSON errors.
- [ ] Step 4: Implement logout, current-user output, role normalization, and ownership-safe student resolution.
- [ ] Step 5: Set a 900-second session age and save sessions on every request; add configurable five-failure/900-second lockout constants.
- [ ] Step 6: Change the seed command to use timezone-aware datetimes with USE_TZ enabled.
- [ ] Step 7: Run .venv/Scripts/python.exe manage.py test apps.core.accounts.test_services. Expected: PASS.
- [ ] Step 8: Run .venv/Scripts/python.exe manage.py check. Expected: no system-check issues; commit this task.

### Task 3: Scheduling reads and enrollment operations

**Files:**
- Create: apps/core/scheduling/services.py
- Create: apps/core/scheduling/views.py
- Create: apps/core/scheduling/test_services.py
- Modify: apps/core/scheduling/urls.py
- Create: apps/core/enrollment/services.py
- Create: apps/core/enrollment/views.py
- Create: apps/core/enrollment/test_services.py
- Modify: apps/core/enrollment/urls.py
- Create: apps/core/migrations/0002_enrollment_statuses.py
- Modify: apps/core/management/commands/seed.py
- Modify: apps/core/models.py
- Modify: config/settings.py

**Interfaces:**
- Produces EnrollmentError(code, message), register_student(student, offering_id, now=None) -> Enrollment, and drop_enrollment(student, enrollment_id, now=None) -> Enrollment.
- Produces GET /api/scheduling/active-term/, GET /api/scheduling/offerings/, POST /api/enrollment/register/<offering_id>/, and POST /api/enrollment/drop/<enrollment_id>/.

- [ ] Step 1: Write service tests for closed windows, debt, prerequisite/co-requisite, weekly conflict, exam conflict, credit limit, inactive offerings, capacity, idempotent registration, dropped-record reactivation, and valid/invalid drop windows. Cite ADR #132/#133 NFRP01/NFRP02 and enrollment codes from SDD.
- [ ] Step 2: Run .venv/Scripts/python.exe manage.py test apps.core.enrollment.test_services. Expected: FAIL because services are missing.
- [ ] Step 3: Implement service validation using existing Term, StudentAcademicRules, Prerequisite, Grade, CourseOffering, Enrollment, and Constant models. Use atomic transactions and row locks for offering/student.
- [ ] Step 4: Add migration and seed values for registered/dropped enrollment status constants; correct remaining_capacity to treat lowercase dropped records consistently.
- [ ] Step 5: Add scheduling read services and JSON views for active term and active offerings.
- [ ] Step 6: Add authenticated enrollment register/drop views that resolve the acting student's own Student record and translate EnrollmentError to JSON.
- [ ] Step 7: Enable USE_TZ and update date/time test fixtures and seed data to use aware datetimes.
- [ ] Step 8: Run .venv/Scripts/python.exe manage.py test apps.core.enrollment.test_services apps.core.scheduling.test_services. Expected: PASS.
- [ ] Step 9: Run .venv/Scripts/python.exe manage.py makemigrations --check --dry-run and manage.py check. Expected: no model drift and no system-check issues; commit this task.

### Task 4: Request review workflow

**Files:**
- Create: apps/core/requests/services.py
- Create: apps/core/requests/views.py
- Create: apps/core/requests/test_services.py
- Modify: apps/core/requests/urls.py
- Create: apps/core/migrations/0003_request_workflow_statuses.py
- Modify: apps/core/management/commands/seed.py

**Interfaces:**
- Produces REQUEST_MODELS, transition_request(instance, target_status, reviewer=None) -> instance, and POST /api/requests/<request_type>/<pk>/review/.
- Supports existing StudentServiceRequest, ScholarshipApplication, Proposal, TransferRequest, CreditTransferRequest, InternshipRequest, Internship, RefundRequest, GradeAppeal, and ThesisProgressReport records.

- [ ] Step 1: Write tests for submitted -> in_review -> approved/rejected, legacy pending transitions, invalid transitions, missing status constants, and role-denied/role-allowed reviews. Cite ADR-004 and the relevant SDD feature codes.
- [ ] Step 2: Run .venv/Scripts/python.exe manage.py test apps.core.requests.test_services. Expected: FAIL because the review service is missing.
- [ ] Step 3: Add only missing workflow Constant values via an idempotent data migration and keep the development seed aligned.
- [ ] Step 4: Implement the model/status-field registry and atomic transition validation; retain existing model-specific status categories.
- [ ] Step 5: Add the role-checked JSON review view and route.
- [ ] Step 6: Run .venv/Scripts/python.exe manage.py test apps.core.requests.test_services. Expected: PASS; commit this task.

### Task 5: Documentation and final verification

**Files:**
- Modify: PROJECT_STRUCTURE.md
- Modify: docs/SDD.md
- Modify: docs/SSOT.md
- Modify: docs/ADR.md

- [ ] Step 1: Update the structure inventory to reflect implemented packages, routes, utilities, tests, and migrations.
- [ ] Step 2: Add an SDD implementation-readiness note stating that the referenced behavioral requirements file is missing and the traceability table does not specify all behaviors.
- [ ] Step 3: Record the API/session, lockout, pass-threshold, and UTC decisions in the relevant architecture documents.
- [ ] Step 4: Run .venv/Scripts/python.exe manage.py test, manage.py check, manage.py makemigrations --check --dry-run, and manage.py check --deploy; report any deploy-only warnings separately.
- [ ] Step 5: Review git diff and status, confirm no frontend assets or dependencies were added, and commit the documentation task.

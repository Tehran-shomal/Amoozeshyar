# Backend Foundation Design

## Intent

Prepare the Django backend so a frontend can be built against real, tested behavior while keeping the current data model and admin usable. This is a backend-only milestone; no page layouts, static assets, or frontend bundles are included.

## Current state and evidence

- The project is a Django 5.2 monolith. All 43 current models are in apps/core/models.py and all are registered in apps/core/admin.py.
- Only the home route is implemented. There are no feature apps, services, forms, API endpoints, or automated tests.
- Baseline verification: manage.py check passes; makemigrations --check --dry-run reports no changes; manage.py test discovers 0 tests.
- docs/SSOT.md and docs/SDD.md describe 18 feature apps and 152 requirement codes. The referenced behavior source, نیازمندی_های_آموزشیار.md, is missing, so these codes cannot establish every domain rule.
- ADR-002/003 are explicit about enrollment service rules and atomic register/drop operations. ADR-005 and SSOT explicitly require hashed passwords, role checks, and a 15-minute idle timeout.

## Goals

1. Register the 18 feature sub-apps under apps/core/<feature>/, keep all models in apps/core/models.py and all admin code in apps/core/admin.py, and mount each feature URL namespace.
2. Add a Django-native, session-authenticated JSON boundary that does not require a new dependency and keeps CSRF protection enabled.
3. Implement account login/logout/current-user behavior using Django's Person credentials, role checks through existing UserAccount/Role data, failed-login lockout, and the documented 15-minute idle timeout.
4. Implement the enrollment rules that are explicit in ADR-002/003 and SSOT: registration windows, debt, prerequisites/co-requisites, weekly/exam conflicts, credit limits, capacity, idempotency, and transactional drops.
5. Add a reusable review transition service for request-like models that already exist, and expose an authorized review endpoint.
6. Add tests before implementation for each behavior and update the project inventory and design docs.

## Non-goals

- Implementing frontend pages, templates, CSS, or JavaScript.
- Adding third-party dependencies or a REST framework.
- Adding database entities or fields whose shape is not present in SSOT or the missing requirements source.
- Claiming all 152 requirements are implemented from a table that contains codes but not their behavioral text.
- Implementing payment-gateway, SMS, background-queue, PDF/Excel, backup, or multi-university deployment integrations without their contracts or dependencies.

## Constraints

- All models remain in apps/core/models.py and admin registrations remain in apps/core/admin.py.
- Existing model names, fields, and files are preserved.
- Feature packages follow the names in docs/SSOT.md and are registered in INSTALLED_APPS and the root URL configuration.
- No new dependencies.
- Requirement codes are cited in service docstrings/tests, including row numbers where a code is duplicated.
- Persian remains the configured language and Asia/Tehran remains the display timezone.

## Approaches considered

1. Add Django REST Framework. It offers serializers and permission abstractions, but it adds a dependency that AGENT_INSTRUCTIONS.md disallows without approval.
2. Use Django's built-in views, JsonResponse, auth/session middleware, and CSRF. This follows the existing dependency set and is sufficient for the small API surface in this milestone. Chosen.
3. Put all behavior in apps/core/views.py. This is the smallest diff but conflicts with SSOT/ADR's feature modules and makes backend work hard to test in isolation. Rejected.

## Design decisions

- Feature apps are packages below apps/core. Existing model and admin locations do not change.
- API routes use /api/<feature>/... and JSON error objects with stable error codes. Session auth and the existing CSRF middleware apply to unsafe requests.
- Accounts authenticate the existing Person user through Django's configured auth backend. UserAccount.password is not used for login because it is a separate plain CharField with no model-level hashing guarantee.
- The ADR calls for lockout but does not set its threshold or duration. This implementation uses five consecutive failures and a 15-minute lock, with tests and an explicit setting so the call can be changed.
- SESSION_COOKIE_AGE is 900 seconds and sessions are saved on every request so the 15-minute expiry slides with activity.
- Enrollment is implemented as a service, not embedded in views. It locks the offering and student rows, and a repeated registration returns the existing active enrollment. Dropped records are reactivated to respect the existing unique student/offering constraint.
- A passing grade is treated as 10/20 when deciding whether a prerequisite was completed. No pass threshold exists in the available documents; 10 is an implementation assumption based on the existing 0–20 grade scale and is isolated as a named constant.
- Existing lookup constants are preserved. A data migration adds only the status codes required by the new transitions; the development seed is kept consistent.
- Request reviews use the existing model status foreign keys and a registry of supported models. Each transition checks its current state, target status category, and reviewer role.
- UTC storage is enabled to meet SSOT. TIME_ZONE remains Asia/Tehran for local presentation. The local SQLite database is ignored and not part of the change.
- Apps whose functional requirement text is unavailable get the documented package/URL boundary only; no domain behavior is invented for them in this milestone.

## Risks and follow-up

- The original 152-item requirements file is needed to complete the other domain services and to resolve duplicate/ambiguous requirement codes.
- SQLite ignores select_for_update; transaction and row-lock behavior must also be exercised against the production database engine before relying on the 1000-user concurrency target.
- Existing UserAccount.password values remain untouched; the login path deliberately uses Person.password through Django's hashers.
- Financial/grade encryption, TLS termination, background jobs, caching, backups, and report formats remain deployment/integration work.

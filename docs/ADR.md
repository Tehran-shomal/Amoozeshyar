# Amoozeshyar — Architecture Decision Records

## ADR-001 Django monolith with feature sub-apps

**Status:** accepted.

**Decision:** Keep one Django deployment. Feature code lives in `apps/core/<feature>/`; all models remain in `apps/core/models.py` and admin registrations in `apps/core/admin.py`.

**Consequence:** Transactions can cross feature boundaries, but feature apps share the central model file. The SDD row #145 / NFPP10 request for a separate server per university unit conflicts with this architecture and remains unresolved.

## ADR-002 Service layer for business rules

**Decision:** Put enrollment rules in `apps/core/enrollment/services.py` and call them from views. This covers registration windows, student eligibility, debt, prerequisites/co-requisites, schedule/exam conflicts, credit limits, capacity, and drop windows.

**Legacy status note:** The root `seed_data.py` originally used `student_status.suspended` with the Persian label for probation. Enrollment treats that legacy code as probation with the same 14-unit cap, and the seed now emits `probation` consistently.

**Assumptions pending the original requirements source:** A passing grade is 10/20. Since `CourseOffering` has no exam duration, an exam conflict means the same date and start time. Both assumptions are isolated and tested; revisit them when `نیازمندی_های_آموزشیار.md` is available.

## ADR-003 Atomic registration and drop

**Decision:** Wrap register/drop in `transaction.atomic`; lock the offering and student rows before making capacity-sensitive decisions. This addresses SDD #132/#133 (NFRP01/NFRP02) at the application layer.

**Operational limitation:** The current development database is SQLite, which does not enforce `select_for_update()`. Verify concurrency behavior on the intended production database before relying on the 1000-user target.

## ADR-004 Generic request-review workflow

**Decision:** Reuse status foreign keys on existing request-like models through a registry in `apps/core/requests/services.py`. The review endpoint supports `submitted → in_review → approved|rejected`; legacy `pending` records may enter review or receive a direct decision to preserve older admin workflows. Reviewer roles are selected by request type.

**Scope:** This backend foundation adds review transitions only for existing models. It does not invent missing request schemas or implement submission forms/status-list pages. `cancelled` is not enabled because the available source does not identify which request types permit cancellation. Revisit the role mapping and state transitions when the original requirements are available.

## ADR-005 Security

**Decision:** Use Django password hashers for `Person.password`; never authenticate from the separate `UserAccount.password` field. A session is refreshed with requests and expires after 900 seconds of inactivity. Lock a Person's shared login identity after five consecutive failures for 900 seconds, regardless of which active role alias was used. The counter is stored on the earliest active role account; superusers without an active role account use the lockout fields on `Person`, even when legacy inactive role rows exist. Explicitly using an inactive role alias remains blocked. `Person.username` takes precedence over a colliding `UserAccount.username` alias because the existing unique constraints are local to each table. Both lockout values are explicit settings because the ADR/source did not give exact values. Enforce role checks on enrollment mutations and request reviews.

**Follow-up:** TLS termination, encryption at rest for financial/grade data, session invalidation on password change, and production cookie settings remain deployment/security work. `manage.py check --deploy` currently warns that HSTS (`security.W004`) and SSL redirect (`security.W008`) are not configured; set them when the production HTTPS/reverse-proxy topology is known. The requirement that names AES for passwords conflicts with safe password storage by reversible encryption; hashing is retained as the security decision pending owner review.

## ADR-006 Performance and background work

**Decision:** Cache read-heavy, low-change pages and defer non-urgent work to a task queue. Target response times are those in SDD #134/#138. Cache and queue technology must match the eventual deployment; neither integration is added to this backend-only milestone.

## ADR-007 Resilience

**Decision:** Provide daily automated database backups, idempotent submissions, graceful degradation for SMS/side services, and error logging/admin alerts for critical failures (NFSP02, NFPP17, NFXP02, NFRP03).

**Status:** These integrations are not implemented. The current models do not include the SSOT `AuditLog`/`ErrorLog` entities, and backup/queue/SMS providers are unspecified.

## ADR-008 Localization and time

**Decision:** Keep Persian and RTL presentation with Asia/Tehran as Django’s local timezone. Enable `USE_TZ=True` so new `DateTimeField` values are timezone-aware and stored in UTC. The backend returns ISO/Gregorian dates; Jalali formatting belongs to the future presentation layer.

**Migration gate:** The master baseline uses `USE_TZ=False`, and the timezone of retained naive timestamps is unknown. Migration `0004` converts existing `DateTimeField` values only when `LEGACY_DATETIME_TIME_ZONE` explicitly names their source timezone; if any such rows exist and the setting is absent, migration stops before changing data. It excludes status constants created by branch migrations so their new UTC timestamps are not converted twice. The migration is intentionally irreversible; restore a pre-migration database backup to roll back. The ignored working SQLite database contains legacy seed rows and was not modified; migration behavior was checked on a temporary copy. Confirm an existing database's actual timestamp convention before setting this value on deployment.

## ADR-009 Backend API boundary

**Decision:** Use Django views, `JsonResponse`, sessions, and existing CSRF middleware rather than adding a REST framework or other dependency. Feature endpoints are under `/api/<feature>/`; errors have a stable JSON `{error: {code, message}}` shape. No frontend pages or assets are included until the frontend is ready.

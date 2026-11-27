# React Portal Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Replace every student-facing portal page with React while preserving Django routes, authentication, API ownership, business behavior, and current visual design.

**Architecture:** A Vite-built React/TypeScript client is served from Django static files. Django remains the auth, routing, selector, validation, permission, and persistence boundary; a new allowlisted JSON view-model serves React while the existing HTML API remains compatible during migration.

**Tech Stack:** Django 5.2, React, TypeScript, Vite, existing portal CSS, same-origin Django APIs and CSRF.

**Spec:** `docs/superpowers/specs/2026-11-26-react-portal-migration-design.md`

## Global Constraints

- Preserve current page URLs, query parameters, auth, permissions, data scope, API writes, and Django business rules.
- Preserve page layout/styles; this is a rendering migration, not a redesign.
- JSON view-models must be authenticated and explicitly allowlisted; do not serialize arbitrary model/queryset data.
- Keep old templates until all corresponding React pages and data contracts are present.
- Django admin is out of scope; the student-facing login and portal are in scope.
- Automated test execution is deferred to the user's later QA phase; do not claim tests pass. Build and syntax checks are allowed.
- Preserve all pre-existing staged, unstaged, and untracked audit work. Do not reset, stash, overwrite, or broadly stage it.
- Keep the visual audit at its current page until a fresh authenticated capture is available; component migration alone is not visual verification.

## Review Focus

- Session expires between shell render and page-data fetch: show the existing login/reauth state and never render stale student data.
- A user switches `student_code` or `term`: every React page and API request must retain the same selected profile/term scoping.
- Server form validation fails: show field/non-field errors and preserve user-entered values without treating the write as successful.
- Forms include model-choice, checkbox, multi-value, and empty choices: preserve Django validation and exact field semantics.
- Data may contain HTML-like text, null values, Persian digits, or dates: render as text, preserve current formatting, and never inject untrusted HTML.

---

### Task 1: Add the React/Vite build without changing runtime routes

**Files:**
- Create: `frontend-react/package.json`, `frontend-react/package-lock.json`, `frontend-react/tsconfig.json`, `frontend-react/vite.config.ts`, `frontend-react/index.html`, `frontend-react/src/app.css`
- Create: `frontend-react/src/main.tsx`, `frontend-react/src/types.ts`
- Modify: `.gitignore`
- Create: `static/core/react-build/` output (generated, not hand-edited)

**Interfaces:**
- Produces a stable Django-static entry at `/static/core/react-build/app.js` and stylesheet at `/static/core/react-build/style.css`.
- `PortalBootstrap` contains `page: string`, `apiUrl: string`, `loginUrl: string`, and `csrfToken: string`.

- [ ] Create a Vite React/TypeScript package with pinned compatible versions and scripts `dev`, `build`, and `typecheck`; keep dependencies local to `frontend-react/`.
- [ ] Configure Vite output names and public base so Django can serve the bundle without a Node server in production.
- [ ] Add a minimal typed React root that mounts only when `#portal-react-root` exists; preserve `dir="rtl"` and do not add page redesign styles.
- [ ] Add only generated dependency/build directories to `.gitignore`; do not ignore React source or lockfile.
- [ ] Verify `npm run typecheck` and `npm run build` complete and emit the declared JS/CSS entry files.

### Task 2: Add explicit React page-data and form contracts

**Files:**
- Create: `apps/core/frontend/react_payloads.py`
- Modify: `apps/core/frontend/api.py`, `apps/core/frontend/api_urls.py`
- Create: `apps/core/frontend/react_forms.py`
- Create: `frontend-react/src/api/client.ts`, `frontend-react/src/api/types.ts`, `frontend-react/src/forms/types.ts`
- Modify: `docs/API_CONTRACTS.md`

**Interfaces:**
- New authenticated read endpoint: `GET /api/portal/ui/pages/<slug>/`; returns `{schema_version, page, title, subtitle, owner, profile, term, shell, data, form, omitted_fields}`.
- `serialize_page(slug: str, context: dict) -> dict` returns only JSON primitives/arrays/objects and allowlisted page keys.
- `serialize_form(form) -> {fields: FieldSchema[], nonFieldErrors: string[]}`; each field includes name, label, type, required, helpText, value, errors, and safe choices.
- `PortalApi.getPage(url: string) -> Promise<PagePayload>` and `PortalApi.submitPage(url: string, payload: Record<string, unknown>) -> Promise<SubmitResult>` use same-origin credentials and CSRF; React writes identify themselves with `Accept: application/vnd.amoozeshyar.react+json`.
- Existing `/api/portal/pages/<slug>/` HTML response remains available during migration.

- [x] Define the versioned JSON schema and reject/omit unknown context keys rather than recursively dumping models.
- [x] Implement explicit serializers for the current shared structures (`facts`, `tables`, operation results, form fields, and page metadata).
- [x] Add per-owner/page adapters for values that are not already display-safe primitives; scope all reads through the existing `PortalView.context`.
- [x] Make JSON POST validation responses return safe field errors, non-field errors, and submitted values; preserve status codes, redirects, and old HTML response when the request does not ask for the React representation.
- [x] Implement the typed React API client with `credentials: "same-origin"`, CSRF, JSON error mapping, and login redirect on 401.
- [x] Document endpoint shapes, auth rules, page-specific reads/writes, and legacy compatibility.
- [x] Verify Python import/compile and TypeScript/Vite build; do not run automated test suites.

### Task 3: Move login and shared portal shell to React

**Files:**
- Create: `apps/core/templates/core/react_shell.html`
- Modify: `apps/core/templates/mobina/login.html`, `apps/core/templates/core/database_unavailable.html`, `apps/core/frontend/views.py`, `apps/core/frontend/metadata.py`
- Create: `frontend-react/src/app/App.tsx`, `frontend-react/src/app/routes.ts`, `frontend-react/src/components/PortalShell.tsx`, `frontend-react/src/components/Sidebar.tsx`, `frontend-react/src/components/Topbar.tsx`, `frontend-react/src/components/TermPicker.tsx`, `frontend-react/src/pages/LoginPage.tsx`, `frontend-react/src/pages/SystemErrorPage.tsx`
- Modify: `frontend-react/src/main.tsx`

**Interfaces:**
- Django bootstrap globals are typed as `window.portalBootstrap: PortalBootstrap`.
- `PortalBootstrap.apiUrl` is the authenticated JSON page-data GET; `PortalBootstrap.submitUrl` is the existing page-form/action endpoint. React reads and writes must not share the GET-only URL.
- `resolvePage(pathname: string) -> {slug: string, login: boolean}` maps existing Django URLs without changing them.
- Shared shell consumes `PagePayload` metadata and preserves navigation, profile/term query strings, menu state, logout CSRF, and existing CSS class names.

- [x] Add a React shell template that loads the Vite build, supplies only escaped bootstrap JSON/CSRF data, and contains the React root.
- [x] Render existing portal routes through that shell without changing route authorization or URL names; retain an explicit legacy fallback while page coverage is incomplete.
- [x] Port login markup and error states to React while keeping the existing server-side POST/authentication and no-JavaScript fallback behavior.
- [x] Port sidebar, search, mobile menu, profile picker, term dialog, status notices, and logout using current metadata and CSS classes.
- [x] Verify route/path resolution and static bundle response locally; preserve current search/query parameters.

### Task 4: Port common page renderers and straightforward pages

**Files:**
- Create: `frontend-react/src/components/PageHeading.tsx`, `PageRenderer.tsx`, `FactList.tsx`, `DataTable.tsx`, `DynamicForm.tsx`, `OperationResult.tsx`, `EmptyState.tsx`
- Create: `frontend-react/src/pages/mobina/DashboardPage.tsx`, `SettingsPage.tsx`, `StudentCardPage.tsx`
- Create: `frontend-react/src/pages/miri/AnnouncementsPage.tsx`, `NotificationsPage.tsx`, `GuidePage.tsx`, `SupportPage.tsx`, `MessagesPage.tsx`
- Create: `frontend-react/src/pages/parsa/FinancePage.tsx`, `frontend-react/src/pages/omid/AcademicPage.tsx`
- Modify: payload adapters and route map from Tasks 2–3

**Interfaces:**
- `PageRenderer({payload}: {payload: PagePayload}) -> JSX.Element` dispatches to a registered component or generic safe renderer.
- `DynamicForm({schema, onSubmit}: {schema: FormSchema, onSubmit: SubmitHandler})` submits field names/values to Django and renders returned errors.

- [x] Port the generic facts/tables/forms/result states and preserve existing text, column order, action hooks, print behavior, and empty states.
- [x] Port dashboard, account settings, student card, announcements/notifications, messages, guide/support, financial pages, and academic summary pages from their current templates.
- [x] Keep dynamic content rendered as React text; do not use `dangerouslySetInnerHTML` for page data.
- [x] Verify each migrated page's mapping to its current read/write API and registered route in `docs/SCREEN_API_MATRIX.md`.
- [x] Build the client and inspect emitted bundle names; automated test execution remains deferred.

### Task 5: Port specialized academic workflows and modals

**Files:**
- Create: `frontend-react/src/pages/shaghayegh/EnrollmentPage.tsx`, `SelectedCoursesPage.tsx`, `CourseChangesPage.tsx`, `RegistrationStatusPage.tsx`
- Create: `frontend-react/src/pages/niousha/SchedulePage.tsx`, `CalendarPage.tsx`, `AttendancePage.tsx`, `ExamCardPage.tsx`
- Create: `frontend-react/src/pages/omid/CurriculumPage.tsx`, `TranscriptPage.tsx`, `AcademicActivitiesPage.tsx`, `GradeAppealPage.tsx`
- Create: `frontend-react/src/pages/miri/EvaluationPage.tsx`, `EvaluationFormPage.tsx`
- Modify: `frontend-react/src/api/client.ts`, explicit payload adapters, current shared CSS only where required for parity

**Interfaces:**
- Enrollment action calls retain current endpoints: registration, ordinary drop, and emergency drop; server remains authoritative.
- Course-selection and drop-confirmation dialogs use local React state with accessible open/close/focus behavior and server-driven choices/results. The evaluation form remains on its existing route because its current template and PDF reference are a separate screen.
- All page components consume the same `PagePayload` envelope and preserve `student_code`, `term`, enrollment, and filter query parameters.

- [x] Port enrollment, selected course list, course-change/drop flows, registration status, tuition warning, and course/group dialogs.
- [x] Port schedule, calendar, attendance, exam card, curriculum, transcript, academic activities, evaluation list, and evaluation form.
- [x] Keep endpoint methods, request fields, eligibility checks, ownership, error codes, disabled actions, and unavailable-data notices unchanged.
- [x] Verify all relevant route/API pairs against `docs/SCREEN_API_MATRIX.md` and update component mappings.
- [x] Build and run syntax checks only; defer automated tests and visual acceptance as requested.

### Task 6: Port remaining services and complete every registered route

**Files:**
- Create: `frontend-react/src/pages/shahsvand/InternshipPage.tsx`, `GuestRequestPage.tsx`, `GraduationPage.tsx`, `GraduationCertificatePage.tsx`, `RequestsPage.tsx`, `EducationCertificatePage.tsx`
- Create: remaining shared or owner components for any slugs found in `apps/core/frontend/registry.py` not yet mapped
- Modify: `frontend-react/src/app/routes.ts`, all corresponding page payload adapters

**Interfaces:**
- Every slug from `apps/core/frontend/registry.py` and special route `home` maps to exactly one React component.
- A `legacyTemplate` flag is allowed only for routes not yet migrated and must be removed before this task is complete.

- [x] Port internship, guest request, graduation, certificates, student services requests, and every remaining registered route.
- [x] Compare the React route inventory against the Django registry and fail closed on an unmapped slug; do not show generic demo data for missing components.
- [x] Ensure every POST remains handled by the existing Django service/form and every successful result is displayed from the API response.
- [x] Document each component's route, owner, payload, read API, write API, and known schema limitations.
- [x] Build the complete client and inspect all emitted static assets.

### Task 7: Switch the portal fully to React and reconcile documentation

**Files:**
- Modify: `apps/core/frontend/views.py`, `apps/core/templates/core/section.html`, `apps/core/templates/core/portal_base.html`, `apps/core/templates/core/live_content.html`, `apps/core/frontend/api.py`
- Modify: `docs/PDF_PAGE_MAPPING.md`, `docs/SCREEN_API_MATRIX.md`, `docs/PROGRESS.md`, `docs/TEST_REPORT.md`, `docs/screens/README.md`
- Retire only after route inventory: unused legacy page templates/scripts in `apps/core/frontend/*/templates/` and `static/core/live_portal.js`

**Interfaces:**
- All authenticated portal routes resolve to React and the JSON view-model endpoint.
- The old HTML API may remain as a documented compatibility response; React never renders or inserts its HTML.
- `?legacy=1` fallback may remain only as a short-term operator escape hatch and must be documented, not presented as React coverage.

- [x] Switch default portal rendering to the React shell after all route slugs have React components and payload adapters.
- [x] Remove only code/templates proven unused by the route and static-reference inventory; preserve Django forms, selectors, ownership registry, and APIs.
- [x] Update all 96 PDF mapping rows to identify React component and shared state/route mapping without changing the existing visual-verification statuses.
- [x] Record that automated suites and the sequential authenticated visual audit are still pending; do not mark pages visually accepted from build success alone.
- [x] Run `npm run build`, Python compile checks, `git diff --check`, and a source grep proving all registry slugs are mapped and React does not inject API HTML. Do not run automated test suites.

Task 7 inventory result: all 28 HTML files under `apps/core/frontend/**/templates/` are mapped through the 32 registered pages, the legacy login/dashboard, or an included partial; `static/core/live_portal.js` remains referenced by `templates/base.html` on the `?legacy=1` path. No safely orphaned template/script was identified, so nothing was deleted.

### Task 8: Perform authenticated visual parity after the React cutover

**Files:**
- Update: `docs/screens/page-NN-current.png`, `docs/screens/<page>.md`, `docs/PDF_PAGE_MAPPING.md`, `docs/PROGRESS.md`
- Modify: React components/styles only for evidenced parity defects

**Interfaces:**
- Each capture is associated with a valid authenticated session, viewport, PDF reference, route, and component version.
- The sequential visual cursor resumes at PDF page 9; a React conversion is not itself a capture or approval.

- [ ] Capture and compare page 9 in the authenticated local app, correct only evidence-backed mismatches, and document route/API state.
- [ ] Continue one PDF page/state at a time through page 96, preserving the required sequence and current data/auth constraints.
- [ ] Keep test suites deferred until the user starts the separate QA phase.

## Execution choice

Execute natively in the current checkout. There is no subagent tool available in this session, and creating a clean worktree would omit the many uncommitted user-owned audit changes; preserve the current working tree and do not switch branches or manipulate its existing changes.

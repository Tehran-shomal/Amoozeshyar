# Portal API and PDF Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Connect the existing Django session and course APIs to the PDF-based portal while preserving its visible data and matching its reference screens.

**Architecture:** Add a small dependency-free browser API client with testable request and matching helpers. Wire login, logout, offering lookup, registration, and guarded drop actions through existing endpoints; keep PDF fixtures as the displayed source. Compare the rendered routes and modal states against the 96-page PDF and correct only observed presentation differences.

**Tech Stack:** Django 5.2 templates, vanilla JavaScript, CSS, Node 24 built-in test runner, Django test runner, Microsoft Edge headless screenshots.

**Spec:** `docs/superpowers/specs/2026-11-19-portal-api-pdf-alignment-design.md`

## Global Constraints

- Use existing same-origin Django endpoints only; do not add endpoints, dependencies, migrations, or seed data.
- Preserve every visible PDF fixture value and copy; modify presentation only to match the PDF reference.
- Send `X-CSRFToken` for unsafe requests and use same-origin session cookies.
- Send a registration request only for one uniquely matched offering; never infer an offering ID from list order.
- Do not send a drop request for a PDF fixture row without a real enrollment ID.
- Do not run migrations or seed the local database; `core.0004` has an unresolved legacy timestamp source timezone.
- Update `PROJECT_STRUCTURE.md` after file changes. Do not commit while the shared worktree contains earlier uncommitted user changes.

## Review Focus

- Persian and Arabic-Indic digits in lesson codes map to ASCII without changing displayed text; pin with `testNormalizeDigitsAndMatchCode`.
- Duplicate or mismatched offerings never trigger a registration request; pin with `testMatchRequiresUniqueGroupOffering`.
- Missing CSRF token, expired session, or rejected credentials produce a readable status and no false success; pin with `testUnsafeRequestsBootstrapCsrfAndSurfaceApiErrors` and the login browser smoke check.
- A fixture row without an enrollment ID never triggers `POST /drop/`; pin with `testDropRejectsMissingEnrollmentIdWithoutFetching`.
- Empty/failed offering responses leave PDF fixture content intact; pin the no-write path with `testNoOfferingDoesNotRegister`, assert the fixture values in the Django template contract, and verify the rendered screen by screenshot.

---

### Task 1: Testable same-origin API client

**Files:**
- Create: `static/core/portal_api.js`
- Create: `static/core/tests/portal_api.test.cjs`
- Modify: `templates/base.html`

**Interfaces:**
- `createPortalApi({ fetchImpl, cookieReader })` returns `csrfToken()`, `login(credentials)`, `me()`, `logout()`, `activeTerm()`, `offerings()`, `register(offeringId, payload)`, and `drop(enrollmentId, payload)`.
- `normalizeDigits(value)` converts Persian and Arabic-Indic numerals to ASCII for comparisons only.
- `matchOffering({ lessonCode, groupTitle, schedule }, offerings)` returns the sole matching offering or `null`; it requires matching lesson code, teacher, weekday, and start/end times.
- `registerMatchedOffering(api, selection, offerings, payload)` calls `api.register()` only for one match; it returns `null` without a write when there is no unique match.
- `drop()` rejects an absent/non-positive enrollment ID before issuing any request.

- [x] **Step 1: Write Node tests for API request behavior and matching helpers**

  Include `testUnsafeRequestsBootstrapCsrfAndSurfaceApiErrors` and assertions for same-origin credentials, digit normalization, exact unique group matching, ambiguous/no match, no offering/no write, and missing drop ID.

- [x] **Step 2: Run the Node tests and confirm they fail because the client does not exist**

  Run: `node --test static/core/tests/portal_api.test.cjs`
  Expected: FAIL because `portal_api.js` and its exported helpers are absent.

- [x] **Step 3: Implement the client and load it before `portal.js`**

  Make unsafe requests fetch `/api/accounts/csrf/` as needed, preserve same-origin cookies, send `X-CSRFToken`, parse the documented `{error:{code,message}}` shape, and expose the exact interfaces above to both the browser and CommonJS tests.

- [x] **Step 4: Run the Node tests and confirm they pass**

  Run: `node --test static/core/tests/portal_api.test.cjs`
  Expected: all API helper tests PASS.

### Task 2: Login, session check, and logout controls

**Files:**
- Modify: `apps/core/templates/core/login.html`
- Modify: `apps/core/templates/core/portal_base.html`
- Modify: `static/core/portal.js`
- Modify: `apps/core/tests.py`

**Interfaces:**
- Login submits `{ username, password }` with `PortalApi.login()` and navigates to the existing dashboard only after success.
- `GET /api/accounts/me/` checks the active browser session without replacing PDF display data.
- The existing sidebar exit link invokes `PortalApi.logout()` and returns to the existing login preview.
- Errors use a pre-rendered `aria-live="polite"` status node; no status text is visible before an error occurs.

- [x] **Step 1: Add failing Django template contract tests**

  Add `PortalTemplateContractTests` for named username/password fields, a real submit control, a status node, and a logout action hook while preserving existing visible labels.

- [x] **Step 2: Run the targeted Django tests and confirm the contract fails**

  Run: `\.venv\Scripts\python.exe manage.py test apps.core.tests.PortalTemplateContractTests`
  Expected: FAIL because the current login controls are demo-only and logout links to the preview.

- [x] **Step 3: Wire the templates and browser handlers**

  Keep the current visible labels and layout. Intercept login/logout actions, call the API client, check `/me/` after login, translate known API error codes to concise Persian feedback, and redirect only on confirmed success.

- [x] **Step 4: Run the targeted Django tests and confirm they pass**

  Run: `\.venv\Scripts\python.exe manage.py test apps.core.tests.PortalTemplateContractTests`
  Expected: all template contract tests PASS.

- [x] **Step 5: Smoke-check login and logout browser behavior**

  Use Edge with mocked API responses to confirm success redirects, invalid credentials show the live status, and logout is a POST with CSRF. Do not use the local database or real credentials.

### Task 3: Safe course lookup, registration, and drop guard

**Files:**
- Modify: `apps/core/templates/core/section.html`
- Modify: `static/core/portal.js`
- Modify: `static/core/portal.css` only if a newly revealed status needs styling
- Modify: `static/core/tests.py`
- Extend: `static/core/tests/portal_api.test.cjs`

**Interfaces:**
- Course cards expose their PDF lesson code; each radio choice exposes its teacher label and schedule as data attributes without changing visible copy.
- Opening the existing course modal fetches active term and offerings once. The fixtures remain the visible list and values.
- Confirming add calls `register(offering.id)` only when `matchOffering()` returns exactly one offering; otherwise no write request is sent and a live status explains the unavailable match.
- Drop confirmation calls `drop(id)` only when the row has a real positive enrollment ID. Current fixture rows have no such ID and therefore never send a drop request.

- [x] **Step 1: Add failing tests for ambiguous/no offering and missing drop ID**

  Extend the Node suite with the review-focus cases; add Django assertions that course codes/groups are exposed as data hooks while their fixture text remains unchanged.

- [x] **Step 2: Run Node and targeted Django tests and confirm the new assertions fail**

  Run: `node --test static/core/tests/portal_api.test.cjs`
  Expected: FAIL on missing/ambiguous match behavior.

  Run: `\.venv\Scripts\python.exe manage.py test apps.core.tests.PortalTemplateContractTests`
  Expected: FAIL because course controls lack the API mapping hooks.

- [x] **Step 3: Connect only uniquely matched course actions**

  Add the data hooks and handlers. Fetch scheduling data without replacing fixture values, report API errors in the live region, and leave fixture drop controls local when no enrollment ID exists.

- [x] **Step 4: Run the Node and Django contract suites and confirm they pass**

  Run: `node --test static/core/tests/portal_api.test.cjs`
  Expected: all tests PASS, including no request for absent/ambiguous IDs.

  Run: `\.venv\Scripts\python.exe manage.py test apps.core.tests.PortalTemplateContractTests`
  Expected: all template contract tests PASS and fixture labels unchanged.

### Task 4: PDF screen-by-screen comparison

**Files:**
- Modify: `static/core/portal.css` and/or the relevant templates only where a measured mismatch exists.
- Create: `docs/portal-pdf-comparison.md`

**Interfaces:**
- The report maps PDF page/state to the matching route or modal state and records `match` or the concrete mismatch.
- Screenshots use the same viewport, device scale, and browser zoom for PDF pages and browser routes.

- [x] **Step 1: Capture the PDF reference states and the current UI states**

  Use the existing PDF at `C:\Users\repair\Downloads\Amoozeshyar.pdf`; capture each applicable route and modal at a common viewport. Keep screenshot artifacts in `%TEMP%`.

- [ ] **Step 2: Record mismatches before changing presentation**

  Map all 96 PDF pages to a route/state or mark the page as unrepresented. Compare every represented route and modal state, including all course-selection and drop-confirmation states; record every non-match and unrepresented page in `docs/portal-pdf-comparison.md`.

- [x] **Step 3: Correct only presentation mismatches**

  Match PDF geometry, typography, color, spacing, and modal backdrop. Do not change visible text, numbers, ordering, or fixture values.

- [x] **Step 4: Recapture and update the comparison report**

  Run the same capture procedure and mark only visually verified states as `match`; leave any unverified or blocked state explicitly identified.

### Task 5: Project documentation and final verification

**Files:**
- Modify: `PROJECT_STRUCTURE.md`
- Modify: `docs/portal-pdf-comparison.md`

- [x] **Step 1: Update the current project map**

  Describe the new static API client, its tests, and the login/course template hooks without changing unrelated entries.

- [x] **Step 2: Run Django checks and API-focused tests**

  Run: `\.venv\Scripts\python.exe manage.py check`
  Expected: `System check identified no issues (0 silenced).`

  Run: `\.venv\Scripts\python.exe manage.py test apps.core.accounts.test_services.AccountAPITests apps.core.enrollment.test_services.EnrollmentAPITests apps.core.tests.PortalTemplateContractTests`
  Expected: all selected Django tests PASS on Django's isolated test database.

- [x] **Step 3: Run frontend helper tests and read-only migration status**

  Run: `node --test static/core/tests/portal_api.test.cjs`
  Expected: all tests PASS.

  Run: `\.venv\Scripts\python.exe manage.py migrate --check --plan`
  Expected: reports pending local migrations without applying them; record this as a runtime prerequisite.

- [ ] **Step 4: Review the final diff and comparison report**

  Confirm no API write can occur without a unique offering/enrollment ID, no fixture value changed, and no unrelated user change was overwritten. Report exact page/state coverage and any remaining mismatch; do not claim blanket 100% if any state is unverified.

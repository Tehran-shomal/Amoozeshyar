# API-Driven Portal Data Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every database-backed portal page read and submit its data through same-origin APIs, while keeping the existing Django templates and PDF-matched layout.

**Architecture:** Add an authenticated portal page JSON API that renders the owning page template from the existing selectors and forms, then have the browser load and submit that page through this API. Keep existing accounts, scheduling, and enrollment APIs as the authoritative endpoints for their applicable actions; do not call reviewer-only APIs from student pages.

**Tech Stack:** Django 5, session authentication, JSON APIs, existing Django templates, vanilla JavaScript.

**Spec:** `docs/superpowers/specs/2026-11-21-api-driven-portal-data-design.md`

## Global Constraints

- Preserve the existing PDF-matched page structure, Persian content, and five owner modules.
- All database-backed page data must arrive after page load through an authenticated same-origin JSON API.
- Reuse existing selectors and forms; do not add seed records, migrations, or invented domain data.
- Keep CSRF, profile ownership, and existing API role checks intact.
- Only call APIs that are appropriate to a student session; the reviewer-only request review endpoint is excluded.

## Review Focus

- Unauthenticated page API requests must return JSON 401 instead of login HTML (Task 1).
- A foreign student code must remain denied on page reads and form submissions (Task 1).
- Invalid form submissions must return the bound form and original field values through JSON (Task 1 and Task 2).
- Term-filtered course offerings must preserve the active-term default and reject unknown terms (Task 3).
- Replacing a page shell must not lose actions, search, logout, profile selection, or semester selection handlers (Task 4).

### Task 1: Authenticated page data API

**Files:**
- Create: `apps/core/frontend/api.py`
- Create: `apps/core/frontend/api_urls.py`
- Modify: `config/urls.py`
- Test: `apps/core/test_frontend.py`

**Interfaces:**
- Produces `GET /api/portal/pages/<slug>/` JSON `{html, page, profile, term}` and `POST` JSON `{redirect}` or `{error, html}`.
- Uses `PortalView.context(request, slug)` and existing templates/forms; `home` maps to the dashboard.
- POST JSON form fields normalize into `QueryDict` before existing Django validation runs.

- [x] Add API tests for authenticated page GET, unauthenticated JSON 401, unknown page 404, foreign profile denial, valid form redirect, and invalid form values/errors.
- [x] Run the focused frontend API tests and confirm they fail on missing route/contract.
- [x] Implement API view, JSON error mapping, page-template rendering, and URL registration.
- [x] Run focused frontend API tests and `python manage.py check`.

### Task 2: Data-free initial shell and page API client

**Files:**
- Modify: `apps/core/frontend/views.py`
- Modify: `apps/core/templates/core/portal_base.html`
- Modify: `static/core/portal_api.js`
- Modify: `static/core/live_portal.js`
- Test: `static/core/tests/portal_api.test.cjs`

**Interfaces:**
- Initial `/` and `/portal/<slug>/` render static navigation/UI metadata and a loading state without querying student, term, or page records.
- `PortalApi.portalPage(url)` loads JSON; `PortalApi.submitPage(url, payload)` submits JSON; thrown errors retain the server response in `error.payload`.
- `live_portal.js` replaces `.portal-shell` from the trusted same-origin API response and uses delegated handlers that survive replacement.

- [x] Add client tests for page GET/POST URLs, JSON body, and preservation of API error payload.
- [x] Run focused Node tests and confirm they fail for missing page methods/error payload.
- [x] Implement shell-only context and the page API loader/form submit delegation.
- [x] Run Node tests, Django checks, and verify initial shell context has no database selectors.

### Task 3: Existing scheduling and enrollment APIs

**Files:**
- Modify: `apps/core/scheduling/views.py`
- Modify: `apps/core/frontend/mobina/selectors.py`
- Modify: `apps/core/frontend/mobina/templates/mobina/selected_courses.html`
- Modify: `static/core/portal_api.js`
- Modify: `static/core/live_portal.js`
- Modify: `apps/core/frontend/mobina/static/mobina/section.js`
- Modify: `apps/core/frontend/shaghayegh/static/shaghayegh/section.js`
- Test: `apps/core/scheduling/test_services.py`
- Test: `static/core/tests/portal_api.test.cjs`

**Interfaces:**
- `GET /api/scheduling/offerings/?term=<term_code>` filters by the requested valid term; omitted term keeps `get_active_term()` behavior.
- `PortalApi.offerings(termCode)` sends the optional term query parameter.
- Available-course rows render only from the offerings API; selection/removal use existing enrollment APIs.
- `GET /api/scheduling/active-term/` populates the current active-term state in the existing term picker without overwriting a user's historical term selection.

- [x] Add focused coverage for term-specific offerings and default active-term offerings.
- [x] Run focused scheduling and client tests and confirm the term-filter contract fails before implementation.
- [x] Implement API term filtering, dynamic offerings rendering, active-term loading, and delegated register/drop handlers.
- [x] Run focused checks and inspect generated course rows for safe text rendering and correct offering IDs.

### Task 4: Documentation and integration verification

**Files:**
- Modify: `apps/core/frontend/mobina/README.md`
- Modify: `apps/core/frontend/shaghayegh/README.md`
- Modify: `apps/core/frontend/parsa/README.md`
- Modify: `apps/core/frontend/academic_services/README.md`
- Modify: `apps/core/frontend/neyousha_pouya/README.md`
- Modify: `docs/superpowers/specs/2026-11-21-api-driven-portal-data-design.md`

- [x] Document the data flow, available API map, form contract, and reviewer-only API exclusion.
- [x] Run frontend API tests, scheduling tests, `python manage.py check`, JavaScript syntax checks, and `git diff --check`.
- [x] Review changed files for unintended seed, migration, database, or PDF-layout changes.

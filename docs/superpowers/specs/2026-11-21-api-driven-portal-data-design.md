# API-Driven Portal Data Design

## Intent

The student portal must obtain every database-backed page value through same-origin HTTP APIs. The user-facing reason is to make the frontend consume backend contracts consistently instead of reading models directly while rendering the page. Preserve the existing Persian PDF layouts and the five owner modules.

## Current state

- `PortalView.context()` queries profiles, terms, and feature selectors before rendering each page.
- `PortalApi` already supports accounts, scheduling, and enrollment endpoints. The active-term and offerings methods are not currently called by page code.
- Student request and service forms post to Django page routes. Most feature apps have no domain API route; the requests review endpoint is role-protected and is for reviewers.

## Goals

- Load dashboard and section content, profile choices, term choices, notifications, and record rows through a JSON API request after the static portal shell loads.
- Submit portal forms through a same-origin JSON API and return validation errors through the same page-data contract.
- Use existing accounts, scheduling, and enrollment APIs in the browser where their contracts apply.
- Preserve student ownership checks, selected profile/term, form validation, current page structure, and empty states.
- Keep navigation labels, page titles, helper copy, and design tokens as source-controlled UI metadata; these are presentation copy, not business data.

## Non-goals

- Do not call reviewer-only request APIs from the student UI or weaken their role checks.
- Do not invent domain APIs for feature apps whose backend service is not implemented.
- Do not add demo rows, change the database, seed data, or migrations.
- Do not rewrite the portal as a new SPA framework.

## Approaches considered

1. **Keep ORM-backed server rendering.** Lowest change and preserves the current pages, but it does not meet the user's requirement that browser page data arrive through APIs.
2. **Add a server-driven portal page API (chosen).** The browser fetches a JSON response for each page; it includes the trusted full page render and the profile/term metadata needed by the shell. The browser extracts `.portal-shell`. Form submissions use the same API and return a refreshed page or validation errors. This preserves the PDF layouts and keeps selectors/forms in their owner modules while making the HTTP API the frontend's data boundary.
3. **Build a fully client-rendered SPA with domain serializers for every model.** This gives a normalized REST-style JSON model but duplicates rendering logic across many pages and risks visual regressions. There are not yet domain APIs for most page areas, so this expands the work far beyond the requested integration.

## API contract

- `GET /api/portal/pages/<slug>/` returns JSON with the rendered page document, current profile metadata, and selected-term metadata. `home` maps to the dashboard selector. Optional `student_code` and `term` query parameters retain existing selection behavior.
- The browser extracts and replaces `.portal-shell` from the same-origin API response. This is a server-driven JSON API boundary: existing Django templates render the layout, and database-backed markup is delivered only in the API response. It avoids maintaining a second client-side implementation of the PDF layouts.
- `POST /api/portal/pages/<slug>/` accepts JSON made from existing form fields. The API normalizes it to a `QueryDict` and binds the existing Django form. Success returns JSON with a redirect back to the portal shell; validation failure returns HTTP 400 with JSON error details and the rendered shell containing bound-form errors. The API client preserves the error payload so the form handler can replace the shell.
- The HTML GET for `/` and `/portal/<slug>/` renders a data-free loading shell and performs no page selectors. Database-backed profile, term, dashboard, page, form-choice, and record markup is rendered by the page API.
- Existing accounts API calls used by the browser: `GET /api/accounts/csrf/`, `POST /api/accounts/login/`, `GET /api/accounts/me/`, and `POST /api/accounts/logout/`.
- Existing scheduling API calls used by the browser: `GET /api/scheduling/active-term/` and `GET /api/scheduling/offerings/?term=<term_code>` for the available-course list.
- Existing `POST /api/enrollment/register/<offering_id>/` and `POST /api/enrollment/drop/<enrollment_id>/` remain authoritative for course actions.
- `GET /api/scheduling/active-term/` sets active-term state in the portal header without replacing a historical term selected by the user. The offerings endpoint keeps its active-term default when no term is supplied and returns JSON 404 for an unknown code.
- The reviewer-only `POST /api/requests/<type>/<id>/review/` stays outside the student UI. Other feature URL modules currently declare no domain API routes; the portal page API provides their student-facing read and form boundary until domain endpoints exist.

## Security and data behavior

- Require an authenticated session for portal page APIs; return JSON 401 errors instead of redirect HTML.
- Resolve profiles only from `Student.objects.filter(person=request.user)`; reject foreign `student_code` values.
- Reuse existing selectors and Django forms for validation and ownership. Do not serialize model fields wholesale.
- Escape page data with Django templates before placing the trusted shell in JSON. The client inserts only this same-origin server-rendered fragment.
- Preserve CSRF on every POST and the existing enrollment service checks.
- Page shell GETs contain no database-backed portal rows; those arrive in the page API response.

## Acceptance checks

- Network requests show a portal-page API GET for the dashboard and every section; the initial page response contains no database-backed profile, term, or page values.
- Every existing page still renders its current template and empty/error state from database-backed context returned by the API.
- Valid and invalid form submissions return through the page API without losing the selected profile or term; invalid forms preserve bound values and field errors.
- Login, logout, enrollment, drop, active-term, and offerings requests retain their existing authentication/CSRF behavior.
- A second user's profile code cannot be requested through the page API.
- `manage.py check`, migration dry-run, JavaScript syntax check, and existing frontend checks pass; no data migrations or seed changes are introduced.

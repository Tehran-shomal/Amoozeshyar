# React Portal Migration Design

## Intent

Move the existing student-facing portal UI to React without redesigning its pages or changing its business behavior. Preserve the current Django backend, database, authentication, permission checks, page URLs, navigation groups, data ownership, and API write rules. The PDF-to-portal audit remains a separate, ordered effort; this migration must not claim a page visually verified merely because it now renders in React.

## Goals

- Replace the rendered portal shell, login screen, dashboard, and every registered portal page with React components.
- Keep Django as the route/authentication boundary and source of truth for selectors, validation, permissions, and persistence.
- Preserve current page URLs and query parameters (`student_code`, `term`, filters, and workflow IDs).
- Keep the existing CSS and page geometry; port markup and behavior, not redesign them.
- Use explicit, authenticated JSON view-models for React. Serialize only fields needed by each page; never expose arbitrary model objects or querysets.
- Keep the existing write endpoints and server-side form validation. Return structured validation errors to React while preserving legacy response behavior for existing clients during migration.
- Keep the PDF page mapping and document React component/API ownership for all 96 reference screens, including multiple states that share one route/component.
- Keep login, logout, CSRF, profile ownership, term selection, and permission checks server-controlled.

## Non-goals and anti-goals

- No database/model/schema migration, business-rule rewrite, auth bypass, or role/permission change.
- No visual redesign, changed navigation taxonomy, changed URL scheme, or fabricated fixture data.
- No rewrite of Django admin; “all frontend” here means the student-facing portal and its login, not Django's staff administration site.
- Do not remove the current Django templates until every route has a React equivalent and the replacement is documented. The Python modules under `apps/core/frontend/` remain backend selectors/forms/page registry, not React source.
- Automated test execution is deferred to the user's later QA phase. Build/syntax checks may be used during implementation; test suites must not be represented as passing.

## Current state and constraints

- The portal is a Django application with owner-scoped Python page modules and 28 HTML templates (including login, dashboard, and a shared partial).
- `PortalView` preserves Django routes and authentication; current API `GET /api/portal/pages/<slug>/` returns rendered HTML, and POST delegates to the same Django forms and selectors.
- The current browser client uses `static/core/live_portal.js` and `static/core/portal_api.js`; enrollment has a dedicated owner script.
- No React/Vite/Node manifest exists in this repo. Node/npm are available on this machine; use a local Vite build whose output is served by Django static files.
- The checkout is already dirty with user-owned audit work. Preserve it; do not revert, stash, overwrite, or broadly stage those changes. Work on the existing audit branch/worktree and keep migration edits identifiable.
- The current browser session for authenticated page-9 visual verification was unavailable. React migration may proceed from source/contracts, but must leave the visual audit cursor at page 9 until a valid authenticated capture is available.

## Approaches considered

1. React islands inside the current Django templates. Lowest initial risk, but leaves most of the requested frontend in Django and duplicates rendering responsibilities. Rejected as the final architecture.
2. React owns the complete portal UI; Django keeps routes, auth, selectors/forms, APIs, and database. A Vite-built React/TypeScript client renders each existing route from explicit JSON page data, while Django remains the security/business boundary. This best satisfies “all frontend in React without fundamental changes” and is selected.
3. A standalone SPA plus backend rewrite. This would change routing, auth boundaries, and API/business logic unnecessarily and has the highest regression/security risk. Rejected.

## Design decisions

- Add React/TypeScript source in a distinct root folder (for example `frontend-react/`) so it does not collide with Django's `apps/core/frontend/` Python package.
- Use Vite to emit stable, Django-served static assets. Keep deployment/local startup under the existing Django workflow; document the required frontend build step and a developer HMR command.
- Preserve normal browser URLs and navigation semantics. Django serves one lightweight React bootstrap shell for authenticated portal routes; React selects the component from the current pathname. Links may remain ordinary anchors so route reload and Django auth behavior stay unchanged.
- Add an authenticated page-data endpoint/representation for React rather than using server-rendered HTML as React content. Keep the current HTML API response available during transition. The React response is an explicit allowlisted view-model built from the current owner selectors.
- Forms are described to React with safe metadata (name, label, type, required, help text, choices, current value, and errors). Django remains the validator and persistence authority. React submissions include CSRF and the existing profile/term context; redirects and field errors are returned as JSON for the React client.
- Build the React shell and shared components first, then migrate route components by existing ownership/page manifests. Start with login/shared shell and generic facts/forms/tables; migrate specialized dashboard, enrollment/course modals, finance, calendar/attendance, and request workflows without changing their backend behavior.
- Maintain a route-to-component/API map alongside the PDF page map. Multiple PDF states sharing a route stay documented as states of the same React component; missing data/state is not fabricated.
- Keep old templates as fallback until each route's React component and data contract are in place. Remove or retire legacy rendering only in a final cleanup after a route inventory confirms full coverage.

## Acceptance criteria

- Every route in the current frontend registry, plus login and dashboard, is rendered by a React component; the Django admin remains outside scope.
- React renders real structured data, not HTML returned by Django templates.
- Existing visible labels, layout, URLs, navigation groups, query parameters, empty/error states, CSRF, server validation, ownership, and write behavior remain intact.
- No React payload contains unrestricted model serialization; each payload is authenticated, profile-scoped, and allowlisted.
- Every page and its PDF-state mappings identify the React component and the API/read/write contract in documentation.
- Legacy templates remain available until equivalent React coverage is confirmed; no route silently falls back to fabricated/demo content.
- Build/syntax verification is reported separately from the deferred automated QA phase. No claim of all-96-page visual approval is made without fresh authenticated captures.

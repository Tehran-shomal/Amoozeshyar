# Frontend Team Page Ownership Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put portal pages in five clear code groups while keeping Shahsavand and Omid's page assignments distinct inside the shared academic-services module, identify Pouya and Niousha as frontend leads, match key reference screens, remove placeholder assets, and push from the repository's default branch.

**Architecture:** Each code group declares its portal slugs in `pages.py`; the shared registry merges those declarations and rejects missing or duplicate ownership. The academic-services README and `MEMBER_PAGES` keep Shahsavand's and Omid's assignments separate. Common data/form markup remains in `core/live_content.html`; group templates and assets exist only where the reference requires page-specific markup or behavior.

**Tech Stack:** Django templates and selectors, Python, Node.js tests, Git.

**Spec:** `docs/superpowers/specs/2026-11-20-portal-frontend-feature-modules-design.md`

## Global Constraints

- Keep the five navigation categories separate from five code ownership groups.
- Preserve each named owner's exact page list, even where two owners share one code group.
- Preserve existing page slugs, server-side records, API paths, and database state.
- Do not add demo data, empty files, placeholder templates, or placeholder stylesheets.
- Use `origin/master` as the base because the GitHub repository's default branch is `master`; there is no `main` branch.
- Commit and push only the frontend deliverable and its required project wiring/documentation.

## Review Focus

- A route appears in exactly one team's manifest and still renders: test every slug through the frontend test suite.
- Group folders do not contain redundant shared-template or stylesheet stubs: assert the shared renderer is used and inspect tracked files.
- The lead label and semester-picker ownership remain explicit: assert in the architecture test.
- The feature branch is based on the fetched default branch and contains only the scoped commit: inspect `git diff origin/master...HEAD` before pushing.

---

### Task 1: Pin page ownership and lead in tests

**Files:**
- Modify: `apps/core/test_frontend.py`
- Modify: `static/core/tests/portal_bindings.test.cjs`

- [x] Add a failing test requiring every group module to declare unique route slugs covering `PAGES`, and assert the lead label is `پویا و نیوشا (لید فرانت)`.
- [x] Add a failing Node assertion that redundant shared content templates and placeholder `section.css` files are absent.
- [x] Run the focused Python and Node tests; both failed for the expected missing manifests/assets.

### Task 2: Move page declarations into the five code groups

**Files:**
- Create: `apps/core/frontend/<group>/pages.py` for each of the five code groups.
- Modify: `apps/core/frontend/<team>/__init__.py`
- Modify: `apps/core/frontend/registry.py`
- Modify: `apps/core/frontend/metadata.py`

- [x] Move each route's title, subtitle, and navigation group metadata beside its owning team; retain only navigation, footer, and login copy in shared metadata.
- [x] Put login and dashboard under Mobina, and the term-picker component under the Pouya/Niousha lead module.
- [x] Merge module definitions in the central registry; raise a configuration error for duplicate or unassigned routes.
- [x] Run the focused ownership test and confirm it passes.

### Task 3: Keep only real templates and assets

**Files:**
- Modify: `apps/core/frontend/views.py`
- Modify: `apps/core/frontend/neyousha_pouya/templates/neyousha_pouya/content.html`
- Delete: duplicated group `content.html` wrappers and unused per-group `section.css` stubs.
- Modify: `config/settings.py`
- Modify: `templates/base.html`

- [x] Use the shared renderer for data/table/form pages; retain the actual custom notification template and owner-specific API scripts.
- [x] Stop registering missing/empty per-team template and static directories.
- [x] Run the ownership and static-binding checks.

### Task 4: Match key screens and consolidate to five code groups

**Files:**
- Create: `apps/core/frontend/academic_services/` with separate Shahsavand/Omid page lists and a group README.
- Create: owner-group templates for student card, exam card, enrollment, add/drop, academic activities, and finance pages.
- Modify: `apps/core/test_frontend.py`, `static/core/tests/portal_bindings.test.cjs`, `config/settings.py`, and the relevant selectors/templates/navigation.
- Remove: the standalone `omid` and `shahsavand` code-group folders after moving their live files.

- [x] Add failing tests for exactly five group modules, distinct member ownership, page-specific screen markup, and opening only the active navigation group.
- [x] Run focused Python and Node tests and observe the expected failures.
- [x] Add page-specific, database-backed templates for the mismatched screens; keep actions on existing APIs/routes and omit values not present in the database.
- [x] Compare the updated page structure and CSS against the supplied 1440×900 PDF references (20, 21, 52, 53, 54, 61, and 63); record that a fresh browser screenshot pass was not generated.
- [x] Add short comments and owner-by-owner READMEs for the five code groups.

### Task 5: Document, verify, and publish

**Files:**
- Modify: `PROJECT_STRUCTURE.md`
- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-11-20-portal-frontend-feature-modules-design.md`

- [x] Document the exact page ownership, five navigation groups, and five code modules.
- [x] Run frontend, account, scheduling, enrollment, and request tests; run `manage.py check` and migration dry-run.
- [ ] Review the staged file list and diff; commit with `refactor: define frontend pages by team`.
- [ ] Push `feature/frontend-team-structure` to `origin` and verify the published branch head.

# Amoozeshyar Full-System Audit and Reconstruction Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify the 96-page PDF portal end to end, close only evidence-backed gaps, and produce the required implementation, API, screen, team, and verification records.

**Architecture:** Preserve the Django monolith, centralized model/admin files, five frontend owner modules, and same-origin session/CSRF page API. Reuse existing models/forms/services; where the PDF or repository does not specify business behavior, record the gap and keep the action safe instead of inventing a rule.

**Tech Stack:** Django 5.2.18, Python 3.12, SQLite for isolated development/tests, existing server-rendered templates, and vanilla JavaScript.

**Spec:** `docs/superpowers/specs/2076-05-07-full-system-reconstruction.md`

## Global Constraints

- Use only branch `codex/full-system-audit`; never push, merge, or rewrite shared history.
- Preserve the existing source checkout, its untracked `.superpowers/`, and the original database.
- Use the PDF as the UI/state reference; do not invent absent data or backend rules.
- Keep all models in `apps/core/models.py`, all admin registrations in `apps/core/admin.py`, and avoid new dependencies.
- Keep same-origin session authentication, CSRF protection, request-role checks, and selected-student ownership checks.
- Run migrations and tests only against the isolated clone/test database.
- Treat an unavailable payment gateway, official card/certificate issuance, and other external integrations as unavailable—not successful simulations.
- Mark a screen complete only when appearance, navigation, API, persistence, validation, permissions, errors, tests, and documentation are evidenced.

## Review Focus

- A request for another student's profile must never disclose or mutate that student's records (API and page-form ownership tests).
- Anonymous API access must return JSON `401`, not a login-page redirect or HTML (accounts, scheduling, and portal-page tests).
- Missing/invalid lookup constants and malformed form payloads must fail safely without creating data (request/form validation tests).
- Payment, official-card, certificate, and operation-result states must not claim an external action succeeded without a real provider/record (finance and page-render tests).
- RTL navigation, tables, forms, dialogs, and focus must remain usable at 1920×1080, 1536×864, 1366×768, 1280×720, 1024×768, 768×1024, and 390×844 (browser visual regression review).

---

### Task 1: Evidence-based baseline and audit checkpoint

**Files:**
- Create: `docs/INITIAL_AUDIT.md`
- Create: `docs/PROGRESS.md`
- Create: `docs/NEXT_STEPS.md`
- Create: `docs/TEST_REPORT.md`
- Modify: `PROJECT_STRUCTURE.md` only where the current audit finds factual drift

**Interfaces:**
- Consumes: current branch base `dbe34c558df41517fe262a13e4af90eb75d2937e`, current repository docs/code, 96 PDF reference images, and baseline verification output.
- Produces: a timestamped, evidence-only inventory of current stack, routes, data safety, test state, known gaps, and continuation checkpoint.

- [x] Record branch/base/remote, clean-clone status, original working-tree preservation, database isolation, and the 96-page source.
- [x] Record the baseline `manage.py test`, `check`, migration-check, and JS results, including the exact observed timezone-warning count and categories.
- [x] List completed, partial, absent, and blocked product areas; do not infer untested behavior from page appearance.
- [x] Verify the audit against `config/settings.py`, `config/urls.py`, `PROJECT_STRUCTURE.md`, and existing tests.
- [x] Commit the audit checkpoint after document consistency checks pass.

### Task 2: API contracts, screen/API matrix, and business-rule decisions

**Files:**
- Create: `docs/API_CONTRACTS.md`
- Create: `docs/SCREEN_API_MATRIX.md`
- Create: `docs/BUSINESS_RULES.md`
- Create: `docs/DECISIONS.md`

**Interfaces:**
- Consumes: Django URL/view/service/form implementations and the 32 registered portal page slugs plus login, dashboard, and shared term picker.
- Produces: exact method/path/auth/CSRF/payload/status/error contracts and an explicit confirmed-vs-assumed-vs-unknown rule catalog.

- [x] Map every implemented endpoint to its view/service and tests.
- [x] Map all portal screens to owner, template, selector/models, read API, write API, validation, and permissions.
- [x] Mark feature namespaces with empty URLs and forms lacking an authoritative workflow as gaps.
- [x] Verify each documented claim against code and tests; correct conflicts in the docs, not by guessing new behavior.
- [x] Commit after endpoint and screen coverage checks pass.

### Task 3: Complete 96-page PDF mapping and screen-level records

**Files:**
- Create: `docs/PDF_PAGE_MAPPING.md`
- Create: `docs/screens/README.md`
- Create: `docs/screens/README.md`, `login.md`, `dashboard.md`, `term-picker.md`, `navigation.md`, one `<slug>.md` for each of the 32 entries in `apps/core/frontend/registry.py`, and five PDF-state docs: `course-selection-dialog.md`, `course-group-dialog.md`, `drop-confirmation.md`, `emergency-drop-confirmation.md`, and `operation-results.md`.
- Modify: `docs/portal-pdf-comparison.md` only to link to the canonical mapping if needed

**Interfaces:**
- Consumes: PDF reference pages 1–96 and the Task 2 screen/API matrix.
- Produces: one explicit mapping for each PDF page and one technical record per real route/component, including represented/unrepresented modal and result states.

- [ ] Cover PDF pages 1 through 96 with no missing page number.
- [ ] For every real screen document reference, owner, URL, purpose, inputs, read/write API, data schema, controls, validation, errors, navigation, rules, tests, and dependencies.
- [ ] Reuse the existing route for repeated PDF states where appropriate; mark independent result states as unrepresented when no safe backend behavior exists.
- [ ] Commit after page-number and route-coverage checks pass.

### Task 4: Screen-backed implementation gap closure

**Files:**
- Modify only the exact feature files exposed by Tasks 1–3 (models remain centralized; templates/scripts stay with their owner).
- Add focused tests beside the owning feature before each behavior change.

**Interfaces:**
- Consumes: Tasks 1–3 evidence and existing model/service contracts.
- Produces: only test-backed fixes for reproducible user-facing defects; no new schema or external integration without source evidence.

- [ ] For each confirmed defect, write a failing focused test first, run it to observe the failure, then implement the smallest safe fix.
- [ ] Cover valid flow, invalid input, empty state, denied role/profile, and persistence for every touched workflow.
- [ ] Do not treat unavailable provider-dependent actions as implemented; record them in `docs/NEXT_STEPS.md`.
- [ ] Run focused tests, system checks, and migration checks before committing each coherent fix.

### Task 5: Responsive, accessibility, and browser integration verification

**Files:**
- Modify: `static/core/portal.css`, `static/core/responsive.css`, or owned templates/scripts only when a reproduced defect requires it
- Test: `apps/core/test_frontend.py` and existing browser-client tests where the runtime is available
- Create/update: `docs/TEST_REPORT.md`

**Interfaces:**
- Consumes: existing login/dashboard/page API and the seven target viewport sizes in the spec.
- Produces: reproducible browser evidence for navigation, form submission, error states, responsive layout, table overflow, and keyboard focus.

- [ ] Exercise login, dashboard, representative read/write screens, profile/term switching, logout, and a denied request.
- [ ] Inspect the seven required viewport sizes and compare representative screens with their PDF references.
- [ ] If browser automation/runtime is unavailable, report that limitation and do not claim visual completion.
- [ ] Run applicable Python and JavaScript suites and commit only after the actual outputs are recorded.

### Task 6: Team presentation pack and final regression

**Files:**
- Create: `docs/presentation/01_Mobina.md` through `07_Miri.md`
- Create: `docs/presentation/MASTER_PRESENTATION.md`
- Create: `docs/FINAL_REPORT.md`
- Update: `docs/PROGRESS.md`, `docs/NEXT_STEPS.md`, `docs/TEST_REPORT.md`

**Interfaces:**
- Consumes: completed screen docs, API matrix/contracts, verified test output, actual ownership manifests, and branch history.
- Produces: seven Persian member presentations, one team presentation, final limitations, next steps, and a Git/verification handoff.

- [ ] Include the ten required sections in every member document and cite only real screens, APIs, files, models, and test output.
- [ ] Cross-check all required deliverables, screen files, links, and page numbers.
- [ ] Run the full Python suite, Django system check, migration check, applicable JS tests, and `git diff --check`.
- [ ] Record the final commit list and clean/dirty Git status; do not push, merge, or open a PR.

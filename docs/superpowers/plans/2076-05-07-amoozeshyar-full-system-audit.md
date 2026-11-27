# Amoozeshyar Full-System Audit and Reconstruction Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Verify the 96-page PDF portal end to end, close only evidence-backed gaps, and produce the required implementation, API, screen, team, and verification records.

**Architecture:** Preserve the Django monolith, centralized model/admin files, seven new frontend owner modules (see `2076-05-07-seven-team-full-pages-plan.md`), and same-origin session/CSRF page API. Reuse existing models/forms/services; where the PDF or repository does not specify business behavior, record the gap and keep the action safe instead of inventing a rule.

**Tech Stack:** Django 5.2.18, Python 3.12, SQLite for isolated development/tests, existing server-rendered templates, and vanilla JavaScript.

**Spec:** `docs/superpowers/specs/2076-05-07-full-system-reconstruction.md`

## Global Constraints

- Use only branch `codex/full-system-audit`; never push, merge, or rewrite shared history.
- Preserve the existing source checkout, its untracked `.superpowers/`, and the original database.
- Use the PDF as the UI/state reference; do not invent absent data or backend rules.
- Continuation audit: the source PDF is available at `C:\Users\repair\Downloads\Amoozeshyar.pdf`; reference PNGs 1–96 are stored in `docs/screens/`. Review current site appearance and page/API code in strict page order, recording evidence in `docs/PDF_PAGE_MAPPING.md` and `docs/screens/`.
- A page is not visually complete without a fresh capture of its current runtime state. If authentication blocks that capture, record the exact status and do not advance the visual sequence by using stale screenshots or bypassing authorization.
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

- [x] Cover PDF pages 1 through 96 with no missing page number.
- [x] For every real screen document reference, owner, URL, purpose, inputs, read/write API, data schema, controls, validation, errors, navigation, rules, tests, and dependencies; shared invariants are linked to the API contract and matrix.
- [x] Reuse the existing route for repeated PDF states where appropriate; mark independent result states as unrepresented when no safe backend behavior exists.
- [x] Commit after page-number and route-coverage checks pass.

### Task 4: Screen-backed implementation gap closure

**Files:**
- Modify only the exact feature files exposed by Tasks 1–3 (models remain centralized; templates/scripts stay with their owner).
- Add focused tests beside the owning feature before each behavior change.

**Interfaces:**
- Consumes: Tasks 1–3 evidence and existing model/service contracts.
- Produces: only test-backed fixes for reproducible user-facing defects; no new schema or external integration without source evidence.

- [x] For each confirmed defect, write a failing focused test first, run it to observe the failure, then implement the smallest safe fix (finance shell and responsive search border).
- [x] No business workflow changed; focused rendering/CSS tests cover the touched behavior, and the existing suite covers persistence, invalid input, empty states, and profile permissions.
- [x] Do not treat unavailable provider-dependent actions as implemented; record them in `docs/NEXT_STEPS.md`.
- [x] Run focused tests, system checks, and migration checks before committing each coherent fix.

### Task 5: Responsive, accessibility, and browser integration verification

**Files:**
- Modify: `static/core/portal.css`, `static/core/responsive.css`, or owned templates/scripts only when a reproduced defect requires it
- Test: `apps/core/test_frontend.py` and existing browser-client tests where the runtime is available
- Create/update: `docs/TEST_REPORT.md`

**Interfaces:**
- Consumes: existing login/dashboard/page API and the seven target viewport sizes in the spec.
- Produces: reproducible browser evidence for navigation, form submission, error states, responsive layout, table overflow, and keyboard focus.

- [x] Browser smoke: login, dashboard, read pages/API, term switching, continuation navigation, denied profile, and logout.
- [ ] Browser write workflow: not run because the seeded active term has a closed registration window and the other term has no offerings; service persistence tests pass without fabricating a course/term.
- [x] Inspect all seven viewport sizes and compare representative screens with PDF pages 2, 9, 53, and 63; document visual differences and partial scope.
- [x] Edge/CDP runtime was available; Playwright was not installed and no dependency was added.
- [x] Full Python/JavaScript suites, Django check, and migration check reran after the final report edits: Python 101/101, Node 14/14, both Django checks clean.

### Task 6: Team presentation pack and final regression

**Files:**
- Create: `docs/presentation/01_Mobina.md` through `07_Miri.md`
- Create: `docs/presentation/MASTER_PRESENTATION.md`
- Create: `docs/FINAL_REPORT.md`
- Update: `docs/PROGRESS.md`, `docs/NEXT_STEPS.md`, `docs/TEST_REPORT.md`

**Interfaces:**
- Consumes: completed screen docs, API matrix/contracts, verified test output, actual ownership manifests, and branch history.
- Produces: seven Persian member presentations, one team presentation, final limitations, next steps, and a Git/verification handoff.

- [x] Include the ten required sections in every member document and cite only real screens, APIs, files, models, and test output.
- [x] Cross-check all required deliverables, screen files, links, and page numbers: seven member docs, master, 32/32 route docs, 96/96 PDF pages, 106 Markdown files and zero broken local links.
- [x] Run the full Python suite, Django system check, migration check, applicable JS tests, and `git diff --check` after the final report is authored.
- [x] Record the final commit list and clean Git status after the local documentation checkpoint; do not push, merge, or open a PR.

## Active continuation — 2026-11-25

- Source/API review has continued through PDF page 41. Pages 23–29 have page-specific templates, page 30 has an API-triggered debt blocker, pages 31–33 use the existing evaluation form/API, pages 34–37 use its real survey state list, pages 38–40 show persisted owner-scoped internship/guest/message results, and page 41 confirms saved settings from the current Person record; no external submission or delivery is claimed. Regression coverage is written but no test suite has been run because the user deferred tests. Page 28 records emergency-drop minimum-unit and registration-block-reason gaps; page 29 records ticket attachment and portal-reply workflow gaps; page 30 records the absent minimum-unit rule and payment gateway; pages 31–33 lack a class-group field in schema.
- Pages 23–41 are documented in `docs/screens/curriculum.md`, `internship.md`, `guest-request.md`, `graduation.md`, `messages.md`, `guide.md`, `support.md`, `operation-results.md`, `evaluation-form.md`, and `evaluation.md`; their route/API mapping and limitations are recorded in `docs/PDF_PAGE_MAPPING.md` and `docs/SCREEN_API_MATRIX.md`.
- PDF reference PNGs 27–96 were rendered at 96 DPI using a temporary PyMuPDF install outside the project; no runtime/project dependency was added.
- The visual sequence remains blocked at page 19: there is no current authorized portal capture for that page. Reviewing later source and PDF references does not count as completing the visual sequence.
- Read-only verification: Django `check` passed with a one-off local `SECRET_KEY`; `git diff --check` exited 0 (Git emitted existing CRLF normalization warnings). No migration, test suite, production DB mutation, staging, or commit was performed in this continuation.
- Latest checkpoint: source/API review through PDF page 42. Results 38–42 now bind to saved Internship, TransferRequest, Communication, Person settings, and GradeAppeal data respectively. Regression coverage was added, but tests remain NOT RUN by the user's instruction; runtime visual sequence is still blocked at page 19.
- Updated checkpoint: source/API review through PDF page 44; pages 43 and 44 now expose owned saved ScholarshipApplication and StudentServiceRequest results. No test suite run; visual sequence remains blocked at page 19.
- Updated checkpoint: source/API review through PDF page 48. Page 46 now renders an owner-scoped saved Ticket result (attachment unsupported); page 47 remains unavailable without a payment gateway; page 48 does not fabricate formal certificate issuance. Regression added but tests remain NOT RUN; sequential runtime visual review remains blocked at page 19.
- Updated checkpoint: source/API review through PDF page 54. Pages 49–52 cover actual survey ratings, settings limitations/language lookup, and enrollment stage one; page 53 now supports both register/drop from its matching route, and page 54 uses an emergency-window-only endpoint. New regressions remain NOT RUN; visual sequence remains blocked at page 19.
- Updated checkpoint: source/API review through PDF page 55. Registration status now summarizes persisted student/enrollment/debt facts while marking approval as unknown because there is no approval model. Regression remains NOT RUN; visual sequence remains blocked at page 19.
- Updated checkpoint: source/API review through PDF page 59. New course registration now reports `created`, sends a fresh success to the add/drop route, and renders only the owned active Enrollment result; repeated registrations are not claimed as new successes. Tests remain NOT RUN; visual sequence remains blocked at page 19.
- Updated checkpoint: source/API review through PDF page 61. Page 60 now states that the grade-appeal endpoint does not enforce the permitted window and cannot attach files; page 61's current-term enrollment summary and four real route links were checked, and the change history is accurately noted as student-wide because its model has no term FK. Regression assertions were added but not run; the authorized visual sequence is still blocked at page 19.
- Updated checkpoint: source/API review through PDF page 62. Transcript now lists every active enrollment, including courses with no recorded score, with units/status and actual score; grade-component and term-GPA gaps are explicit, and appeal/chart links match the reference actions. Regression was added but not run; visual sequence remains blocked at page 19.
- Updated checkpoint: source/API review through PDF page 63. Payments now follow the PDF table columns, while the absent Payment description field is disclosed instead of invented; successful totals exclude failed rows. Regression updated but not run; visual sequence remains blocked at page 19.
- Updated checkpoint: source/API review through PDF page 64. Secure-payment now presents only current Student debt/payer information, states its description is generic, disables continuation without a gateway, and links to real history; no card data or Payment write is introduced. Regression updated but not run; visual sequence remains blocked at page 19.
- Updated checkpoint: source/API review through PDF page 65. Financial-aid form still submits only existing type/reason fields and now declares absent amount/IBAN/attachment and no approval/payment. Regression assertions written, not run; visual sequence remains blocked at page 19.
- Updated checkpoint: source/API review through PDF page 66. Tuition adds a clear missing fixed/variable tariff warning and links to secure-payment/history; sums remain successful payments and stored debt, with no guessed conversion from PDF toman. Regression written, not run; visual sequence remains blocked at page 19.
- Updated checkpoint: source/API review through PDF page 67. Student requests now declare the missing contact/attachment fields and local-only submission while preserving active-type validation, server ownership/status, and scoped results. Regression updated but not run; visual sequence remains blocked at page 19.
- Updated checkpoint: source/API review through PDF page 71. Pages 68–71 share add/drop; the current Enrollment table now includes its real status while keeping API-backed drop action and no fabricated tariff; PDF-specific course-count variants remain unavailable. Regression updated but not run; visual sequence remains blocked at page 19.
- Updated checkpoint: source/API review through PDF page 73. Education-certificate warns that recipient/copy/delivery fields are absent; graduation-certificate now has a dedicated read-only profile/chart/audit/workflow page and links but still no request type or issuing provider. Regression added/updated but not run; visual sequence remains blocked at page 19.
- Updated checkpoint: source/API review through PDF page 74. Evaluation list state remains data-driven and owner/term-scoped; the page now states ratings are 1–5 and that the survey is linked to the student enrollment, so the PDF's anonymity/confidentiality claim is not repeated. Regression updated but not run; visual sequence remains blocked at page 19.
- Updated checkpoint: source/API review through PDF page 96. Pages 75–78 are emergency-drop list variants, not result routes; the post-drop result is now scoped to the owned dropped Enrollment. Pages 79–88 now use a real-offering-driven selection/group modal and register the chosen offering; unsupported group numbers/tariffs remain undisplayed. Pages 89–96 use distinct normal/emergency endpoints and disclose that deletion does not calculate/refund tuition. Python/Node regressions were written or updated but remain NOT RUN; the runtime visual sequence is still blocked at page 19.
- Continuation checkpoint 2026-11-25: rechecked the stored page 9 reference/current desktop and mobile captures. Fixed the confirmed half-width sidebar group title on the selected-courses route and added a static regression assertion; no test suite was run. A fresh authorized runtime capture is unavailable, so the CSS change is pending visual confirmation.

# Amoozeshyar Full-System Reconstruction — Execution Spec

## Sources and authority

- Primary visual reference: the user-provided `Amoozeshyar.pdf` (96 pages).
- Execution requirements: the user-provided “MASTER EXECUTION PROMPT — AMOOZESHYAR”.
- Existing contracts and code organization: `docs/SSOT.md`, `docs/SDD.md`, `docs/ADR.md`, `docs/AGENT_INSTRUCTIONS.md`, and the current source.
- The referenced behavioral requirements file `نیازمندی_های_آموزشیار.md` is absent. The PDF establishes visible screens and interaction states, but does not establish every validation rule, permission, or backend transition.

## Goal

Audit and complete the existing Django student portal against the PDF, connect only evidenced workflows to persisted records, verify the integration, and leave technical, screen-level, and team-presentation documentation that accurately distinguishes implemented, partial, unavailable, and unknown behavior.

## Architecture and compatibility constraints

- Keep the existing Django monolith and use the replacement seven frontend ownership groups in `2076-05-07-seven-team-full-pages-design.md`; the prior five-group structure is superseded.
- Keep model declarations in `apps/core/models.py` and admin registrations in `apps/core/admin.py` unless an explicit project decision supersedes that rule.
- Preserve the same-origin session/CSRF API boundary and student/profile ownership checks.
- Do not add dependencies, sample transactions, invented grades, fabricated identifiers, or fake external-service success.
- Do not run destructive migrations or commands against the original project database. Use isolated tests and a separate development database only.
- Persian/RTL and the PDF page/state structure are required. Validate the requested desktop, tablet, and mobile viewports.
- Work only on `codex/full-system-audit`; do not push, merge, or open a PR.

## Acceptance criteria

1. Every one of the 96 PDF pages is accounted for with an explicit screen/state and implementation status.
2. Every current route has its owner, data source, API read/write path, validation, permissions, errors, and test evidence documented; unknowns stay marked unknown.
3. Existing tests, Django checks, and migration checks are run and reported with actual results.
4. Existing student data remains profile-scoped; payments, card issuance, certificates, and other external/official actions are never simulated as successful.
5. The required audit, contract, screen, business-rule, progress, final-report, and eight presentation documents are present.
6. No capability is called complete unless its UI, API, persistence, permissions, errors, and tests have evidence.

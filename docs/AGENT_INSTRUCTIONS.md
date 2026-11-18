# Agent Instructions

You are working in an existing Django project. Follow these steps in order.

1. Read the whole project first: settings, root urls, `apps/`, `apps/core/models.py`, `apps/core/admin.py`, every sub-app under `apps/core/`, templates, static, tests, requirements/manage files. Do not skip files.
2. Write `PROJECT_STRUCTURE.md` at the repo root describing the CURRENT state: directory tree, registered apps (INSTALLED_APPS), url includes, every model with fields/relations, admin registrations, per-sub-app views/templates/urls, shared utilities, conventions. Describe only what exists; mark unknowns as "unknown".
3. Read `SSOT.md`, `SDD.md`, `ADR.md`. Compare against `PROJECT_STRUCTURE.md` and list gaps (missing features/models) in a "Gaps" section of that file.
4. Do not deviate from the structure:
   - All models only in `apps/core/models.py`; admin only in `apps/core/admin.py`.
   - Each feature is a separate sub-app `apps/core/<feature>/` with its own views, urls, templates; register it in INSTALLED_APPS and root urls.
   - Do not rename, move or delete existing files, models or fields; no new top-level layout; no new dependencies without asking.
   - Reuse existing models/utilities before creating new ones.
5. Reference requirement codes (e.g. FUFP01) in code comments/tests. When a code is ambiguous, ask.
6. If anything conflicts with this structure or the docs, stop and ask instead of improvising.
7. After each change, update `PROJECT_STRUCTURE.md`, run migrations check and tests.

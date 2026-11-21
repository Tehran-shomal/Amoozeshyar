# Login and Dashboard Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restore student login on port 8000 and align the dashboard semester and financial cards with the user's PDF reference.

**Architecture:** Keep Django sessions and existing models/APIs. Use a backup, the approved Tehran timezone migration, and root `seed_data.py`; render the term picker and financial summary from current database records.

**Tech Stack:** Django 5.2, SQLite, Django templates, shared portal CSS/JavaScript.

**Spec:** `docs/superpowers/specs/2026-11-20-login-and-dashboard-alignment-design.md`

## Global Constraints

- Preserve a validated backup of `db.sqlite3` before migration or flush.
- Set `LEGACY_DATETIME_TIME_ZONE=Asia/Tehran` when applying pending migrations.
- After clearing existing rows, use only `seed_data.py` to repopulate application data.
- Keep login/session/API routes unchanged and do not hard-code dashboard records.

## Review Focus

- A failed migration must not be followed by a database flush; the backup remains restorable.
- The original term code remains the submitted query value even when the PDF display shortens it.
- Missing payment rows render an empty state instead of a fabricated payment status.
- Local HTTP session cookies must be configurable without weakening production defaults.
- The profile and finance side column must collapse cleanly on tablet and mobile layouts.

---

### Task 1: Back up, migrate, and seed the local database

**Files:**
- Database: `db.sqlite3`
- Backup: timestamped sibling file, created without overwriting an existing backup

- [x] Create a consistent SQLite backup using the SQLite backup API.
- [x] Verify the backup with SQLite `integrity_check` and confirm original record counts.
- [x] Run `manage.py migrate --noinput` with `LEGACY_DATETIME_TIME_ZONE=Asia/Tehran`.
- [x] Run `manage.py flush --noinput` only after migrations succeed, honoring the seed-only instruction.
- [x] Run root `seed_data.py` with UTF-8 console output.
- [x] Confirm migrations are current, student accounts exist, and `S-2001` / `password123` authenticates.

### Task 2: Match the semester control to the PDF

**Files:**
- Modify: `apps/core/frontend/views.py`
- Modify: `apps/core/templates/core/portal_base.html`
- Modify: `static/core/live_portal.js`
- Modify: `static/core/portal.css`

- [x] Build semester display options from existing `Term` rows while retaining the full `term_code` for requests.
- [x] Render the compact PDF-style active semester label and “انتخاب نیمسال” control.
- [x] Add an accessible dialog that lists actual terms and preserves the selected student profile on submit.
- [x] Add responsive styling and dialog open/close behavior with comments.

### Task 3: Move financial summary beside the profile card

**Files:**
- Modify: `apps/core/frontend/mobina/selectors.py`
- Modify: `apps/core/frontend/mobina/templates/mobina/home.html`
- Modify: `static/core/portal.css`

- [x] Build summary values from `Student.tuition_debt` and selected-term `Payment` rows.
- [x] Place profile and financial panels in one side column; keep classes and notices in the main column.
- [x] Keep the academic panel and make the layout responsive.

### Task 4: Keep local HTTP authentication configurable

**Files:**
- Modify: `config/settings.py`
- Modify local-only `.env` cookie settings if required; do not display or alter unrelated secrets.

- [x] Read `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` from environment values, defaulting to the current `not DEBUG` behavior.
- [x] Set local development values for the existing HTTP server without weakening secure defaults elsewhere.

### Task 5: Verify the result

- [x] Run `manage.py check` and inspect `migrate --check` output.
- [x] Perform a real HTTP login on port 8000, then request `/api/accounts/me/` using the same session.
- [x] Inspect the rendered dashboard at desktop and narrow viewport sizes.
- [x] Confirm the original backup remains readable and report its path.

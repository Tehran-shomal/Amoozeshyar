# Login and Dashboard Alignment Design

## Intent

Restore the local student login on port 8000, use the existing `seed_data.py` as the only source of application records, and align the dashboard term control with page 2 of `Amoozeshyar.pdf`. Move the financial status into the profile side column so it fills the empty dashboard area.

## Chosen approach

Back up the current SQLite database, apply the pending migrations with `LEGACY_DATETIME_TIME_ZONE=Asia/Tehran`, clear existing application rows as previously requested, then run only `seed_data.py`. The main database stays the one used by port 8000. Secure-cookie settings remain secure by default and become configurable for local HTTP through environment values.

Replace the header dropdown with the compact term label and “انتخاب نیمسال” control shown in the PDF. Its accessible dialog lists terms from the database and applies the selected term using the existing query parameter. Keep the complete term code for queries while presenting the PDF's shortened code when it matches the seeded `14051` pattern.

Place the student's financial summary directly below the student profile card. Read debt from `Student.tuition_debt` and selected-term payment status from the student's `Payment` rows; show an empty state when the database has no matching record.

## Constraints

- Preserve a validated SQLite backup before changing the original database.
- `Asia/Tehran` is the confirmed source timezone for legacy timestamps.
- After reset, application records come only from root `seed_data.py`.
- Do not hard-code student, payment, or semester records in templates.
- Keep current URL routes, session authentication, and APIs.
- Dashboard remains responsive and uses the existing feature-module structure.

## Other approaches considered

- A separate database on another port avoids touching the current database but leaves the ordinary port 8000 broken; the user has now approved the timezone and requested login data.
- Migrating and seeding without clearing rows would leave the previously unwanted superuser and non-seed records; clearing after backup honors the earlier seed-only instruction.

## Acceptance

- The database records all current migrations and contains seeded students, terms, and payment data only.
- A seeded student can log in and retain a session over local HTTP.
- The topbar shows the current semester in the PDF's compact format, and its selector changes the selected term.
- The dashboard shows financial status beneath the profile card, using database values.
- The page fits desktop and narrow screens without the finance card falling below an unintended blank column.

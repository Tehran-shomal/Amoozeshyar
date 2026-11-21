# Live frontend implementation

User authorized direct implementation without questions, six owner modules, and responsive full-width pages. Temporary template data is permitted but must be disclosed.

Architecture: Django templates and authenticated ORM selectors; existing session APIs for login and enrollment; validated, ownership-scoped ModelForms for models without submission APIs. No schema migration or seed execution. Database records are authoritative, including subsequent user submissions; no artificial seed provenance registry.

- [x] Create six modules (mobina, shaghayegh, shahsavan, parsa, neyousha_pouya, omid), shared shell and explicit route registry.
- [x] Replace fixture-backed views with current-student selectors and empty states; support profile/term selection.
- [x] Connect enrollment IDs to existing APIs; implement validated submission forms with server-assigned ownership and statuses.
- [x] Move login/dashboard and module templates/assets into owner folders, retain shared visual theme; fix full viewport responsiveness.
- [x] Verify all routes, ownership isolation, form submissions, API failures and responsive CSS. Document missing external gateway and data added.

Completion: 85 Django tests pass. Root `seed_data.py` ran only in the disposable test database. No application fixture rows or live database changes were made. Online payment is unavailable because the project registers no gateway or payment submission API.

Review focus: anonymous access, foreign student IDs, multiple profiles, no seed rows, missing initial status constants, duplicate submissions, selected term, and narrow screens. Existing local DB must not be migrated or seeded.

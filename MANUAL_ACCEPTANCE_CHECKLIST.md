# Manual acceptance checklist

The Docker/PostgreSQL API portions were validated on August 27, 2026. Automated
frontend tests cover authentication, permissions, catalog forms, inventory draft
saves/submission, dashboard, products, and alerts. The in-app browser had no
available session, so visual browser-only items remain unchecked and must be run
before a public demo.

- [x] Manager login succeeds; invalid login shows a safe error; logout clears access.
- [ ] Refreshing an authenticated page preserves the cookie session; an expired session redirects once. *(automated protection tests pass; browser refresh not run)*
- [x] Employee navigation omits Add Product and Users and manager URLs show a forbidden state.
- [x] Dashboard renders zero values, submitted sessions, low-stock rows, and retry states correctly.
- [ ] Product search, every filter, query-string persistence, pagination, and mobile cards work. *(automated rendering/filter controls pass; full browser pass not run)*
- [x] An uncounted product says Uncounted and has no low-stock/reorder value.
- [x] Product create/edit validates thresholds and displays duplicate-SKU conflicts.
- [x] Category/vendor create, edit, activate, deactivate, search, and pagination work through the live API.
- [x] User create/edit and authorization work through the live API.
- [ ] Employee starts a draft, saves/replaces/removes quantities, refreshes, and sees saved state. *(live API and automated saves pass; browser refresh not run)*
- [x] A failed item save leaves the entered value visible and reports the failure.
- [x] Another employee cannot edit the draft; a manager can; submitted counts are read-only.
- [x] Empty-count submission is rejected; nonempty submission updates product history and dashboard.
- [x] Low-stock results preserve backend urgency order; filter/render behavior is automated. *(clipboard remains browser-manual)*
- [ ] Keyboard focus, labels, dialogs, menus, 44px controls, and phone layouts are usable.
- [ ] Browser storage contains no JWT; authenticated requests use cookies. *(source and HTTP cookie flow pass; browser storage inspection not run)*

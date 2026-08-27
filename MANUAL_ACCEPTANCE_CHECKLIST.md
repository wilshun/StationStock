# Manual acceptance checklist

Playwright is intentionally not configured because this environment cannot
reliably launch the PostgreSQL-backed stack. Run this checklist against seeded
Docker services before a portfolio demo.

- [ ] Manager login succeeds; invalid login shows a safe error; logout clears access.
- [ ] Refreshing an authenticated page preserves the cookie session; an expired session redirects once.
- [ ] Employee navigation omits Add Product and Users and manager URLs show a forbidden state.
- [ ] Dashboard renders zero values, submitted sessions, low-stock rows, and retry states correctly.
- [ ] Product search, every filter, query-string persistence, pagination, and mobile cards work.
- [ ] An uncounted product says Uncounted and has no low-stock/reorder value.
- [ ] Product create/edit validates thresholds and displays duplicate-SKU conflicts.
- [ ] Category/vendor create, edit, activate, deactivate, search, and pagination work.
- [ ] User create/edit works; self-demotion/deactivation errors are displayed.
- [ ] Employee starts a draft, saves/replaces/removes quantities, refreshes, and sees saved state.
- [ ] A failed item save leaves the entered value visible and reports the failure.
- [ ] Another employee cannot edit the draft; a manager can; submitted counts are read-only.
- [ ] Empty-count submission is rejected; nonempty submission updates product history and dashboard.
- [ ] Low-stock category/vendor filters preserve backend urgency order and copy returned data only.
- [ ] Keyboard focus, labels, dialogs, menus, 44px controls, and phone layouts are usable.
- [ ] Browser storage contains no JWT; authenticated network requests include cookies.

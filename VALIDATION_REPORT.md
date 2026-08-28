# StationStock Core MVP validation report

Validated on August 27, 2026 in Windows with Docker Desktop.

## Environment

- Docker Engine: 29.7.2, build `a7dcaa6`
- Docker Compose: v5.4.0
- PostgreSQL: 17.11 (Debian 17.11-1.pgdg13+2)
- Alembic head/current revision: `0de475186ebf`
- PostgreSQL, FastAPI, and Next.js reached healthy Compose states

## Database and seed validation

All three migrations applied to real PostgreSQL. Offline upgrade and downgrade
SQL generation succeeded and exactly one Alembic head exists. PostgreSQL
inspection confirmed the application tables, UUID keys, foreign keys, check and
unique constraints, enum types, inventory-item uniqueness, and the
`uq_users_email_lower` case-insensitive email index.

The live connectivity probe returned `SELECT 1`. Initial demo seeding created six
categories, three vendors, 21 products, and two submitted counts. A second seed
created zero records. Both development accounts passed the real password/login
path.

## Live integration results

- Manager/employee login, `/auth/me`, logout, invalid/unknown/inactive login, and post-logout rejection passed.
- The JWT cookie is HTTP-only, API-scoped, SameSite=Lax, and absent from response JSON.
- Credentialed CORS returned the exact frontend origin and credentials permission.
- User, category, vendor, and product manager CRUD/duplicate behavior passed; employee administration returned 403.
- Password hashes were never serialized; uncounted inventory remained null.
- Draft upsert/replacement/removal, official-inventory isolation, owner/manager rules,
  validation failures, submission, official quantity update, and submitted immutability passed.
- Low-stock results excluded uncounted records, preserved urgency ordering, calculated reorder quantities, and matched the dashboard preview.
- Dashboard recent submissions were newest first.

Validation records were deactivated afterward. The named volume was preserved.

## Automated validation

- Backend: 42 passed, 1 host-connectivity test skipped; an equivalent live container probe passed.
- Frontend: 17 tests passed across 11 files.
- ESLint and strict TypeScript: passed.
- Next.js production build: passed; 14 routes generated.
- npm audit: zero vulnerabilities.
- OpenAPI: 19 paths generated; required frontend endpoints present.
- Compose: valid; all services healthy.
- Alembic upgrade/downgrade SQL generation: passed.

## Browser/manual status

The frontend, API documentation, and health endpoint returned HTTP 200. The
in-app browser runtime had no available browser session, so visual acceptance,
console/network inspection, browser-storage inspection, and responsive overflow
checks were not performed. They remain unchecked in the manual checklist.

## Warnings and limitations

- The backend tests report a Starlette/httpx deprecation warning.
- Host-side psycopg access to published `localhost:5432` was rejected on this
  machine, although container networking and live schema validation passed. The
  validated migration command therefore uses `docker compose run --rm backend`.
- Docker initially warned that user-level `.docker/config.json` was unreadable in
  the restricted shell; Compose operations still completed.
- npm emits deprecation/funding/install-script notices during image construction;
  its audit reports zero vulnerabilities.
- Core quantities are whole numbers, catalog selectors load at most 100 active
  options, and browser E2E automation is not configured.
- Extended MVP capabilities remain intentionally out of scope.

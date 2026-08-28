# StationStock

Inventory and restocking management system for a gas station convenience store.

StationStock now includes a responsive Next.js 16 frontend (React 19, strict
TypeScript, Tailwind CSS, shadcn/ui, React Hook Form, and Zod) backed by FastAPI,
SQLAlchemy, Alembic, and PostgreSQL 17. Use Node.js 24 LTS for frontend work.

## Frontend setup

From the repository root:

```powershell
Copy-Item frontend/.env.example frontend/.env.local
Set-Location frontend
npm install
npm run dev
```

The browser application runs at `http://localhost:3000` and expects the API at
`http://localhost:8000/api/v1`. The API must be configured with
`ALLOWED_FRONTEND_ORIGIN=http://localhost:3000`; requests include the HTTP-only
authentication cookie automatically.

Frontend quality commands:

```sh
npm run lint
npm run typecheck
npm test
npm run build
```

Main routes are `/login`, `/dashboard`, `/products`, `/products/new`,
`/products/{id}`, `/products/{id}/edit`, `/categories`, `/vendors`, `/users`,
`/inventory-counts`, `/inventory-counts/new`, `/inventory-counts/{id}`, and
`/alerts/low-stock`. Catalog mutations and user administration are manager-only.
Both roles may create counts; employees may edit only drafts they started.

## Full application with Docker Compose

Start PostgreSQL, apply migrations, and launch the backend and frontend:

```sh
docker compose up --build
```

View health and container status with `docker compose ps`, and stop the stack
without removing database data with `docker compose down`. The named
`stationstock_postgres_data` volume persists PostgreSQL state. Seed demo data
after the backend becomes healthy:

```sh
docker compose exec backend python -m app.scripts.seed_demo_data
```

Then sign in at `http://localhost:3000` with the development credentials below.
See `DEMO_GUIDE.md` for a five-minute walkthrough and
`MANUAL_ACCEPTANCE_CHECKLIST.md` for browser checks.

Known Core MVP limitations: inventory is based on whole-number quantities;
catalog selectors load the first 100 active records; there is no expiration,
purchase-order, delivery, barcode, offline, or automatic retry functionality.
Screenshots: _add portfolio screenshots here after running the seeded stack._

## Goal

Help employees track stock, identify low inventory, monitor expiration dates, and verify vendor deliveries.

## Local PostgreSQL setup

The local development database runs PostgreSQL 17 through Docker Compose. Install
Docker Desktop (or Docker Engine with the Compose plugin) before continuing.

Create the backend environment file from the checked-in example:

```powershell
Copy-Item backend/.env.example backend/.env
```

On macOS or Linux, use:

```sh
cp backend/.env.example backend/.env
```

The development connection uses:

- Database: `stationstock`
- Username: `stationstock`
- Password: `stationstock_dev`
- Host port: `5432`

These credentials are intended for local development only.

### Database commands

Run these commands from the repository root.

Start PostgreSQL in the background:

```sh
docker compose up -d postgres
```

Apply migrations through the backend image (the validated Docker workflow):

```sh
docker compose run --rm backend alembic -c alembic.ini upgrade head
```

View container and health status:

```sh
docker compose ps
```

Stop PostgreSQL without deleting its stored data:

```sh
docker compose down
```

After activating the backend virtual environment, apply all Alembic migrations:

```sh
alembic -c backend/alembic.ini upgrade head
```

Run the live database connectivity test:

```sh
python -m pytest backend/tests/test_database.py -v
```

The `stationstock_postgres_data` named volume preserves PostgreSQL data when the
container is stopped or recreated. To intentionally remove the local database and
all of its data, run `docker compose down --volumes`.

## Authentication

StationStock uses a short-lived JWT access token stored in an HTTP-only cookie.
The browser cannot read the token through JavaScript, and the API reloads the user
from the database on every authenticated request so deleted or inactive accounts
lose access immediately. Manager authorization is enforced by reusable backend
dependencies rather than by frontend behavior.

The authentication endpoints are:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`

Configure authentication in `backend/.env`:

| Variable | Development example | Purpose |
| --- | --- | --- |
| `AUTH_SECRET_KEY` | `development-only-change-me-use-32-bytes` | Signs access tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access-token and cookie lifetime |
| `AUTH_COOKIE_NAME` | `stationstock_access_token` | Authentication cookie name |
| `AUTH_COOKIE_SECURE` | `false` | Allows local HTTP cookies |
| `AUTH_COOKIE_SAMESITE` | `lax` | Cross-site cookie protection |
| `ALLOWED_FRONTEND_ORIGIN` | `http://localhost:3000` | Credentialed browser origin |

Production refuses the documented development secret and always enables secure
cookies. Use a strong, randomly generated `AUTH_SECRET_KEY` in every deployed
environment. Never use the example secret, database password, or seed credentials
in production.

## Development users

Apply migrations and seed the full Core MVP demo dataset:

```sh
alembic -c backend/alembic.ini upgrade head
python -m app.scripts.seed_demo_data
```

The demo seed command is explicit and idempotent. It preserves existing records,
creates missing development users, six categories, three vendors, 21 products,
and two submitted count sessions. The resulting catalog includes low-stock,
adequately stocked, and uncounted products. It does not run at application startup.

To create only the two accounts, run `python -m app.scripts.seed_users`.

Development-only credentials:

| Role | Email | Password |
| --- | --- | --- |
| Manager | `manager@stationstock.local` | `StationStockDev!2026` |
| Employee | `employee@stationstock.local` | `StationStockDev!2026` |

All seeded accounts, credentials, vendors, catalog records, and count sessions
are for development only.

## Core MVP API

Interactive OpenAPI documentation is available at `http://localhost:8000/docs`
while the backend is running. Except for health and login, endpoints require the
authentication cookie returned by `POST /api/v1/auth/login`.

| Area | Endpoints | Read access | Write access |
| --- | --- | --- | --- |
| Users | `/api/v1/users` | Manager | Manager |
| Categories | `/api/v1/categories` | Employee or manager | Manager |
| Vendors | `/api/v1/vendors` | Employee or manager | Manager |
| Products | `/api/v1/products` | Employee or manager | Manager |
| Product history | `/api/v1/products/{id}/count-history` | Employee or manager | None |
| Inventory counts | `/api/v1/inventory-counts` | Employee or manager | Draft owner or manager |
| Low-stock alerts | `/api/v1/alerts/low-stock` | Employee or manager | None |
| Dashboard | `/api/v1/dashboard/summary` | Employee or manager | None |

Categories, vendors, products, and users are deactivated rather than deleted.
Inventory counts expose draft creation, note editing, item upsert/removal, and
submission endpoints. A submitted count is permanently read-only.

### Pagination and filters

List endpoints accept `page` (default `1`) and `page_size` (default `20`, maximum
`100`) and return:

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0,
  "pages": 0
}
```

Catalog lists support text search and active-state filters. Products additionally
support category, preferred vendor, counted/uncounted, and low-stock filters.
Inventory-count lists support status, starter, and created-date filters. Low-stock
alerts support category and preferred-vendor filters.

### Inventory rules

- Latest quantity comes only from the newest submitted count item.
- Draft counts never affect official inventory.
- A product without a submitted item is uncounted; its quantity, low-stock state,
  and reorder recommendation are `null`, never silently zero.
- A counted product is low stock when `latest_quantity < minimum_quantity`.
- Recommended reorder quantity is
  `max(target_quantity - latest_quantity, 0)`.
- Alerts are ordered by largest shortage to target, then SKU.
- Employees may edit only drafts they started; managers may edit any draft.
- Submission requires at least one item and atomically records submitted status,
  timestamp, and submitting user.

## Running and testing the backend

After activating the backend virtual environment, start the API from the
repository root:

```sh
uvicorn app.main:app --app-dir backend --reload
```

Run all backend tests:

```sh
python -m pytest backend/tests
```

Run only authentication and authorization tests:

```sh
python -m pytest backend/tests/test_auth.py backend/tests/test_passwords.py
```

Run Core API and workflow tests:

```sh
python -m pytest backend/tests/test_users_api.py \
  backend/tests/test_categories_api.py \
  backend/tests/test_vendors_api.py \
  backend/tests/test_products_api.py \
  backend/tests/test_inventory_counts_api.py \
  backend/tests/test_alerts_dashboard_api.py
```

With the API running, log in manually and store the returned cookie:

```sh
curl -i -c stationstock-cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"email":"manager@stationstock.local","password":"StationStockDev!2026"}' \
  http://localhost:8000/api/v1/auth/login
```

Use the stored cookie to request the current user:

```sh
curl -b stationstock-cookies.txt http://localhost:8000/api/v1/auth/me
```

Docker is required for live PostgreSQL migration, connectivity, seed, and API
validation. The unit and HTTP behavior tests can run without Docker, but SQLite
test databases do not replace final PostgreSQL runtime validation.

## Extended MVP roadmap

Expiration tracking, purchase orders, vendor deliveries, and related reporting
are intentionally outside the validated Core MVP and have no placeholder UI.

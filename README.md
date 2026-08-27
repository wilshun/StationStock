# StationStock

Inventory and restocking management system for a gas station convenience store.

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
| `AUTH_SECRET_KEY` | `development-only-change-me` | Signs access tokens |
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

Apply migrations before creating the development accounts:

```sh
alembic -c backend/alembic.ini upgrade head
python -m app.scripts.seed_users
```

The seed command is explicit and idempotent: it creates missing accounts and
leaves existing accounts unchanged. It does not run during application startup.

Development-only credentials:

| Role | Email | Password |
| --- | --- | --- |
| Manager | `manager@stationstock.local` | `StationStockDev!2026` |
| Employee | `employee@stationstock.local` | `StationStockDev!2026` |

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

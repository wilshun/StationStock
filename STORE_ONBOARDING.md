# Lake Hopatcong Store Onboarding

This guide is for the BP store at 747 State Route 15 S, Lake Hopatcong, NJ 07849. The production database must be new and must never be shared with the development demo database.

1. Have the deployment administrator create `.env.production` from `.env.production.example`, replace every placeholder, and start the production stack.
2. Apply migrations with `docker compose --env-file .env.production -f docker-compose.prod.yml run --rm backend alembic -c alembic.ini upgrade head`.
3. Create the first manager interactively: `docker compose --env-file .env.production -f docker-compose.prod.yml run --rm backend python -m app.scripts.create_manager --name "Manager Name" --email "manager@example.com"`. The password is requested without appearing in shell history.
4. Sign in and create each employee under Users. Give manager access only to people who administer accounts and catalog data.
5. Add real Categories, then Vendors, then Products. Never run either demo seed command in production; the application blocks them when `ENVIRONMENT=production`.
6. Choose a stable, unique SKU printed on the package or based on the store's existing register code. Do not reuse an SKU for a different item.
7. Set minimum quantity to the point where replenishment should start. Set target quantity to the desired full shelf/back-stock amount; target must be at least minimum.
8. Ask an employee to start the first inventory count, enter each on-hand quantity, review it, and submit it. Submitted counts become the inventory record and cannot be edited.

Before opening access to staff, test one employee login, one product update, one count, logout, backup, and restore rehearsal on a separate empty database.

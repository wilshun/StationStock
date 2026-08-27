# StationStock five-minute demo

## Before the demo

Run `docker compose up --build`, then
`docker compose exec backend python -m app.scripts.seed_demo_data`. Open
`http://localhost:3000`. These credentials and all seeded records are local
development data only.

## Walkthrough

1. Frame the problem (30 seconds): convenience-store teams need a quick shared
   count process and an accurate, explainable reorder list.
2. Sign in as `manager@stationstock.local` / `StationStockDev!2026`. Point out
   that authentication is an HTTP-only cookie, not a token in browser storage.
3. On Dashboard, show active catalog totals, uncounted products, recent submitted
   sessions, and the real priority-restock preview.
4. Open Products. Search by SKU, apply counted/low-stock filters, and open a
   product. Show that uncounted is distinct from zero and history is auditable.
5. Open Low stock. Explain backend ordering and the calculated reorder quantity;
   copy the reorder summary without creating a purchase order.
6. Log out and sign in as `employee@stationstock.local` with the same development
   password. Note that Users, Add Product, and administrative edit controls vanish.
7. Start an inventory count, add notes, search for products, enter quantities,
   and show the saved-item progress. Refresh to demonstrate the backend-owned draft.
8. Review and submit. Point out the confirmation and read-only submitted state.
9. Return as the manager and show the submitted session on Dashboard and the
   updated official quantities/alerts.
10. Close with the architecture: responsive Next.js UI, credentialed typed API
    client, FastAPI authorization, transactional SQLAlchemy inventory logic, and
    PostgreSQL/Alembic persistence. Expiration, orders, and deliveries intentionally
    remain future Extended MVP work.

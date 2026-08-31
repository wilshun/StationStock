# StationStock architecture

## Frontend architecture

The App Router frontend is a client-rendered authenticated application shell.
Small reusable hooks call a central typed fetch client; local component state is
used for filters and in-progress forms rather than adding a global state library.
This keeps invalidation explicit after mutations and avoids a cache layer that is
not yet justified by the Core MVP's scale. Searchable product filters are stored
in the URL so links and refreshes preserve context.

The root auth provider calls `/auth/me` before protected content renders. Login
and logout go through the backend, while the JWT remains exclusively in an
HTTP-only cookie. Every API request uses `credentials: include`. A 401 broadcasts
one session-expired event, clears the in-memory user, and redirects to login;
there is no token refresh loop or browser storage. Protected routes prevent data
flashes, manager guards protect administrative pages, and role-aware navigation
hides actions that the backend would reject. Backend authorization remains the
security boundary—the UI is only a usability layer.

Inventory-count pages keep unsaved input locally and upsert each quantity to the
backend on an explicit Save action. Successful responses replace the local draft
snapshot; failed saves leave the typed value visible. Submission requires a
confirmation and replaces the page state with the backend's immutable submitted
representation. Official inventory is never calculated in the browser.

API `null` inventory values are rendered as **Uncounted**, never coerced to zero.
Low-stock order and reorder quantities are consumed directly from backend
responses, preserving a single source of business truth.

## Request flow and module boundaries

Requests enter FastAPI through `app.main`, pass CORS and authentication middleware,
and are dispatched by the versioned routers under `app.api.routes`. Routes validate
input with explicit Pydantic schemas, enforce authorization dependencies, and
coordinate database transactions. SQLAlchemy models define persistence only;
reusable inventory and submission rules live under `app.services`.

The intended dependency direction is:

```text
HTTP route -> Pydantic schema -> service/query -> SQLAlchemy model -> PostgreSQL
                  |                    |
                  +---- response ------+
```

Routes never serialize arbitrary model dictionaries. Response schemas explicitly
select safe fields, preventing password hashes from reaching API responses.

## Authentication and authorization

Login verifies an Argon2 password hash and returns a short-lived HS256 JWT in an
HTTP-only, SameSite-protected cookie. Protected requests decode the token, load the
user from the database, and reject missing or inactive accounts. This database
check means deactivation takes effect even when an older token has not expired.

`CurrentUser` protects employee-or-manager operations. `ManagerUser` protects user
administration and catalog mutations. Inventory draft mutations additionally check
that the current user started the draft unless the user is a manager.

## Database relationships

- A category has many products.
- A vendor can be the preferred vendor for many products.
- A user starts inventory counts and may submit inventory counts.
- An inventory count owns many items.
- Each item references exactly one product.
- `(inventory_count_id, product_id)` is unique, so a product appears at most once
  in a session.

UUIDs are used for every primary and foreign key. Historical foreign keys use
restrictive deletion behavior. Product/vendor/category/user APIs therefore expose
deactivation, not hard deletion. Deleting a draft count internally can cascade to
its items, but the public API does not expose count deletion.

## Inventory-count transaction flow

New sessions start in `draft` and record the starting user. Item writes use an
upsert-like operation keyed by count and product. Only active products can be added.
Draft validation and item changes commit independently while the session is open.

Submission uses the shared `submit_inventory_count` service. It verifies the count
is still a draft and contains at least one item, then sets status, submitting user,
and a UTC submission timestamp in one database transaction. Any exception rolls
the transaction back. Submitted rows are immutable through every API mutation.

## Latest inventory query

`latest_inventory_subquery` joins items only to submitted count sessions and ranks
them per product by `submitted_at` descending. The first ranked row is the official
latest quantity. Drafts are excluded before any product, alert, or dashboard logic
can consume the query.

If no submitted row exists, quantity and count timestamp are `null`. This is an
explicit uncounted state. Treating it as zero would incorrectly create low-stock
alerts and reorder suggestions for products that have never been measured.

## Low-stock and reorder calculations

For a counted product:

```text
is_low_stock = latest_quantity < minimum_quantity
recommended_reorder_quantity = max(target_quantity - latest_quantity, 0)
```

For an uncounted product both values are `null`. Alerts include only known
quantities below minimum and prioritize the largest shortage to target. SKU and ID
provide stable secondary ordering.

## Dashboard aggregation

The dashboard uses aggregate SQL queries for active products, categories, vendors,
submitted sessions, low-stock products, and uncounted products. Recent submitted
sessions include submitter and item count. The low-stock preview reuses the same
ranked inventory query and ordering as the full alerts endpoint, avoiding divergent
business rules and obvious per-product query loops.

## Development data

`python -m app.scripts.seed_demo_data` explicitly creates missing development
accounts and demo catalog data. Natural keys (email, category name, vendor name,
SKU, and fixed count notes) make the command repeatable. Existing matching records
are preserved rather than overwritten. Demo count submission uses the same service
as the production endpoint.

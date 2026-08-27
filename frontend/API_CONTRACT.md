# Frontend API Contract

The browser uses `NEXT_PUBLIC_API_BASE_URL` (default
`http://localhost:8000/api/v1`) and sends `credentials: "include"` on every
request. Authentication is an HTTP-only cookie; no token is exposed to or stored
by frontend JavaScript.

All list endpoints return `{ items, page, page_size, total, pages }`. Backend
errors use `{ "detail": string }`; FastAPI validation errors use a `detail` array.
The exact TypeScript representations of every response live in
`src/lib/api/types.ts` and mirror the generated FastAPI OpenAPI schema.

Core paths: `/auth`, `/users`, `/categories`, `/vendors`, `/products`,
`/inventory-counts`, `/alerts/low-stock`, and `/dashboard/summary`.

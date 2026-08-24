# StationStock Project Plan

## 1. Project Overview

StationStock is a web-based inventory and replenishment platform for a real gas station convenience store in Lake Hopatcong, New Jersey. It will replace informal shelf checks, memory-based ordering, and disconnected paper counts with a simple shared system for products, stock counts, expiration dates, purchase orders, and vendor deliveries.

The application will be designed for daily use by store employees and managers on phones, tablets, and desktop computers. Delivery is divided into a **Core MVP** and an **Extended MVP**. The Core MVP will establish the smallest usable inventory and replenishment system; the Extended MVP will add expiration, purchasing, and delivery controls after the core workflows are stable.

### Planned technology stack

- Frontend: Next.js, TypeScript, Tailwind CSS, and shadcn/ui
- Backend: FastAPI and Python
- Data layer: PostgreSQL, SQLAlchemy, and Alembic
- Testing: Pytest plus appropriate frontend test tools
- Local development and packaging: Docker
- Future hosting: AWS

### Guiding principles

- Keep common store tasks short and understandable.
- Make important exceptions visible: low stock, expiring products, and delivery discrepancies.
- Preserve an auditable history instead of silently replacing operational records.
- Use simple, explainable calculations that managers can verify.
- Keep both MVP stages achievable for one student developer by completing and validating the Core MVP before starting the Extended MVP.

## 2. Business Background

The store sells convenience products with different sales rates, shelf lives, package sizes, suppliers, and reorder needs. Inventory is currently managed through visual shelf inspection and manual counting. Purchasing and delivery verification depend heavily on staff attention and experience, without a dedicated system that connects products, counts, orders, and deliveries.

This creates avoidable operational uncertainty. A shelf can appear adequately stocked while back-room inventory is low, an expiration date can be overlooked, or a vendor delivery can be accepted without a consistent comparison against what was ordered. StationStock will provide one operational source of truth for these activities.

## 3. Current Problems

- Restocking decisions rely on visual estimates and employee memory.
- Inventory counts are manual and may be inconsistent or difficult to review later.
- Low-stock products may not be recognized until a shelf is empty.
- Expiration dates are not consistently recorded or surfaced before products expire.
- Expected vendor quantities are not systematically compared with delivered quantities.
- Missing, damaged, excess, or incorrect delivery items can be overlooked.
- Managers lack a consolidated view of inventory risks and outstanding work.
- There is limited historical information for understanding when a count, order, or delivery occurred and who recorded it.
- Product, category, vendor, and stocking information is not maintained in one structured system.

## 4. Project Purpose

StationStock will make routine inventory work more consistent and less dependent on individual memory. It will organize product data, capture physical counts, calculate replenishment needs, track expiration risks, manage purchase orders, and document delivery discrepancies.

The platform is intended to support human decisions rather than automate purchasing. A manager remains responsible for reviewing recommendations, approving order quantities, and resolving vendor issues.

## 5. Business Value and Expected ROI

### Expected value

- Fewer lost sales from products being out of stock.
- Lower waste from products expiring unnoticed.
- Less employee and manager time spent reconstructing inventory information.
- More consistent ordering based on recorded counts and target levels.
- Stronger evidence when reporting shortages or damage to vendors.
- Better accountability through dated records and user attribution.
- Faster prioritization through dashboard alerts and filtered worklists.

### ROI approach

The project should measure value before claiming a fixed financial return. Baseline data should be gathered during the Core MVP pilot and compared with results after adoption; Extended MVP measures can be added when those workflows launch.

Recommended measures include:

- Estimated retail value of stockouts per month
- Cost value of expired products discarded per month
- Time required to complete a count
- Number and value of delivery discrepancies documented
- Percentage of active products at or above minimum stock
- Percentage of expiring items acted on before expiration

A simple monthly benefit estimate can be calculated as:

`avoided stockout margin + avoided expiration cost + labor time saved + recovered vendor discrepancy value - monthly operating cost`

Development time is primarily an educational investment, but hosting, maintenance, training, and data-entry effort must still be considered. Exact ROI targets should be established only after baseline data is available.

## 6. Target Users

### Managers

Managers maintain reference data, review inventory risks, decide what to reorder, create purchase orders, and investigate delivery discrepancies. They need broader permissions and summary views.

### Employees

Employees perform operational tasks such as entering counts, recording expiration dates, and receiving deliveries. Their interface should minimize typing and avoid exposing administrative actions.

Both MVP stages assume a small, single-store team. Multi-location organizations, vendor portals, and customer-facing access are outside the initial scope.

## 7. Manager Role

Managers can:

- Create, edit, activate, and deactivate products.
- Create and edit categories and vendors.
- Set minimum and target stock levels.
- Review inventory counts and count history.
- Review low-stock alerts.
- Adjust recommended order quantities before ordering.
- View dashboard summaries and operational history.
- Manage user roles and deactivate accounts, subject to implementation scope.

In the Extended MVP, managers can also:

- Review expiring-soon and expired-product alerts.
- Create, edit, submit, and close purchase orders.
- Review expected versus delivered quantities.
- Review and resolve delivery discrepancies.

Destructive deletion of records with history should be avoided. Products, vendors, and users should normally be deactivated instead.

## 8. Employee Role

Employees can:

- Sign in and sign out.
- View active products needed for assigned workflows.
- Search and filter products.
- Create and submit inventory counts.
- Review their submitted counts and available count history.
- View actionable low-stock alerts.

In the Extended MVP, employees can also:

- Record expiration dates and quantities for tracked product batches.
- View expiring-soon and expired-product alerts.
- Receive an existing purchase order.
- Record delivered, missing, damaged, and incorrect quantities or notes.

Employees cannot manage users, change role assignments, alter system-wide stocking rules, or approve administrative reference-data changes unless explicitly granted manager access.

## 9. Main User Workflows

### 9.1 Sign in

**Stage: Core MVP**

1. The user enters credentials.
2. The system validates the account and establishes an authenticated session.
3. The user is directed to a role-appropriate dashboard.
4. Unauthorized routes and actions remain inaccessible.

### 9.2 Perform an inventory count

**Stage: Core MVP**

1. The employee opens a new count session.
2. The employee optionally filters by category, location area, or product search.
3. The system displays active products in a touch-friendly list.
4. The employee enters the physical quantity for each relevant product.
5. The interface shows progress and preserves entered values during navigation.
6. The employee reviews and submits the count.
7. Submitted values become the latest known inventory and remain in count history.
8. The system recalculates low-stock status and reorder recommendations.

### 9.3 Review and act on low stock

**Stage: Core MVP**

1. A manager opens the low-stock list.
2. The system shows the latest quantity, minimum level, target level, and recommended reorder quantity.
3. The manager filters or searches the list and reviews the recommendation.
4. The manager uses the recommendation to guide the store's existing ordering process.
5. After the Extended MVP is available, selected recommendations can be converted into a draft purchase order.

### 9.4 Track expiration dates

**Stage: Extended MVP**

1. An employee selects a product and records an expiration date and associated quantity.
2. The system calculates whether the record is expired or within the configured warning window.
3. Employees can update quantities as units are sold, removed, or discarded.
4. Managers review expiring-soon and expired lists and record an action or resolution.

### 9.5 Create a purchase order

**Stage: Extended MVP**

1. A manager creates a draft for one vendor.
2. Products and expected quantities are added manually or from reorder recommendations.
3. The manager reviews totals and notes, then marks the order as submitted.
4. The system stores the order date, expected delivery date, status, items, and creator.

### 9.6 Receive and reconcile a delivery

**Stage: Extended MVP**

1. An employee opens the submitted purchase order.
2. The employee enters delivered and damaged quantities for each line.
3. The system calculates missing quantities and highlights unexpected results.
4. Incorrect products or other issues are documented in delivery notes.
5. The employee submits the delivery record.
6. The manager reviews unresolved discrepancies and closes or resolves them.

## 10. Detailed MVP Scope

The work is intentionally split into two sequential stages. **Core MVP is the first release and must be usable on its own. Extended MVP begins only after the Core MVP is stable and accepted.**

### Core MVP

The Core MVP includes only:

- Authentication
- Manager and employee roles
- Product management
- Category management
- Vendor management
- Manual inventory counts
- Minimum and target stock levels
- Low-stock alerts
- Reorder quantity recommendations
- Basic dashboard

#### Authentication and authorization

- Secure login and logout
- Employee and manager roles
- Route- and action-level authorization
- Account activation/deactivation
- Authenticated user attribution on operational records

#### Catalog management

- Product creation, editing, viewing, search, filtering, and deactivation
- Category creation, editing, and assignment
- Vendor creation, editing, contact details, and activation status
- Product-to-vendor association, including an optional preferred vendor
- Minimum and target stock levels per product
- Basic product fields such as SKU/internal code, name, unit description, and notes

#### Inventory counting and replenishment

- Manual count sessions with multiple count lines
- Draft and submitted count states
- Latest known quantity derived from the latest submitted count line
- Count history with date, user, and values
- Low-stock status when latest quantity is below the minimum stock level
- Automatic reorder recommendation
- Manager review of recommended quantities before using the store's existing ordering process

For the Core MVP, the default calculation is:

`recommended reorder quantity = max(target stock level - latest known quantity, 0)`

In the Extended MVP, open purchase-order quantities may be incorporated, changing the calculation to:

`max(target stock level - latest known quantity - open incoming quantity, 0)`

The Core MVP must use the first calculation. The second version may replace it only when Extended MVP open-order handling is implemented reliably; the active rule must be displayed to users and tested.

#### Basic dashboard

- Count of low-stock products
- Short prioritized low-stock list linking to product details or a filtered worklist
- Recent inventory-count activity
- Clear links to start a count and review products
- Empty, loading, validation, and error states

### Extended MVP

The Extended MVP adds the following after the Core MVP is stable:

- Expiration tracking
- Purchase orders and purchase-order items
- Delivery reconciliation
- Missing and damaged item tracking
- Delivery discrepancy alerts and resolution
- Extended dashboard summaries for expiration, purchasing, and deliveries

#### Expiration tracking

- Product-level indication of whether expiration tracking is required
- Expiration records containing product, date, and quantity
- Configurable or documented default warning window
- Expiring-soon and expired status calculation
- Alerts and filtered lists
- Resolution status or quantity adjustment when products are sold, removed, or discarded

#### Purchasing and delivery

- Purchase orders linked to one vendor
- Purchase-order line items with expected quantities
- Draft, submitted, partially received, received, cancelled, and closed statuses as needed
- One or more delivery records associated with an order if partial deliveries are supported
- Delivered, damaged, and missing quantity capture by order line
- Expected-versus-delivered comparison
- Notes for incorrect or unexpected items
- Automatically generated discrepancy flags
- Manager review and resolution of discrepancies

#### Extended dashboard and discovery

- The Core MVP low-stock summary plus counts of expiring-soon records, expired records, open purchase orders, and unresolved delivery discrepancies
- Short prioritized lists linking to detailed views
- Search and relevant filters on products, counts, expiration records, purchase orders, and deliveries
- Empty, loading, validation, and error states

### Explicit MVP boundary

Both MVP stages support one store and manual data entry. The Core MVP does not include expiration records, purchase orders, deliveries, missing or damaged item tracking, or delivery discrepancies. The Extended MVP adds those capabilities but still does not automatically place vendor orders, infer sales from a POS system, or maintain real-time perpetual inventory from sales transactions.

## 11. Functional Requirements

Requirements are grouped by delivery stage. FR-001 through FR-016 and the Core MVP dashboard requirements are required for the first release. Expiration, purchasing, delivery, and discrepancy requirements belong to the Extended MVP.

### Core MVP requirements

#### Accounts and permissions

- FR-001: Users must authenticate before accessing business data.
- FR-002: The system must distinguish employee and manager permissions.
- FR-003: The backend must enforce permissions independently of frontend visibility.
- FR-004: The system must record the responsible user and timestamp for important operations.

#### Products, categories, and vendors

- FR-005: Managers must be able to create, view, edit, and deactivate products.
- FR-006: Managers must be able to maintain categories and assign products to them.
- FR-007: Managers must be able to maintain vendor records and associate products with vendors.
- FR-008: Managers must be able to define valid minimum and target levels, with target level greater than or equal to minimum level.
- FR-009: Users must be able to search products and filter by category, vendor, status, and alert state where relevant.

#### Inventory counts

- FR-010: Authorized users must be able to create a count session and enter nonnegative quantities.
- FR-011: A submitted count must retain its lines, author, and submission time.
- FR-012: Users must be able to view count history according to their permissions.
- FR-013: The system must identify the latest submitted quantity for each counted product.
- FR-014: The system must flag products below their minimum stock level.
- FR-015: The system must calculate a nonnegative reorder recommendation from the documented rule.
- FR-016: Draft counts must not change the latest official inventory quantity.

#### Basic dashboard

- FR-017: The dashboard must summarize low-stock products and recent inventory-count activity.
- FR-018: Basic dashboard items must link to relevant Core MVP pages or filtered lists.
- FR-019: Dashboard data must respect the signed-in user's permissions.

### Extended MVP requirements

#### Expiration records

- FR-020: Users must be able to record an expiration date and nonnegative quantity for an expiration-tracked product.
- FR-021: The system must distinguish future, expiring-soon, expired, and resolved expiration records.
- FR-022: Users must be able to filter expiration records by date range, product, category, and status.

#### Purchase orders and deliveries

- FR-023: Managers must be able to create a purchase order for one active vendor.
- FR-024: An order must contain at least one item before submission.
- FR-025: Each order item must store an expected quantity greater than zero.
- FR-026: Authorized users must be able to record deliveries against a submitted order.
- FR-027: The system must compare cumulative delivered quantities with expected quantities.
- FR-028: The system must capture damaged quantities separately.
- FR-029: The system must calculate or clearly track missing quantities.
- FR-030: The system must allow notes for incorrect items and other discrepancies.
- FR-031: The system must flag unresolved missing, damaged, excess, or incorrect deliveries.
- FR-032: Managers must be able to mark a discrepancy resolved with a note and timestamp.

#### Extended dashboard

- FR-033: The dashboard must extend the Core MVP summary with actionable expiration, order, and delivery states.
- FR-034: Extended dashboard items must link to filtered detail views.

## 12. Non-Functional Requirements

- NFR-001 Usability: Common tasks must use clear language, large touch targets, and minimal required typing.
- NFR-002 Responsiveness: All workflows in both MVP stages must work at phone, tablet, and desktop widths.
- NFR-003 Performance: Normal list and dashboard requests should generally complete within two seconds under expected single-store usage, excluding network disruptions.
- NFR-004 Reliability: Submitted operational records must use database transactions and must not be partially saved.
- NFR-005 Data integrity: Quantities, statuses, relationships, and stocking thresholds must be validated in both API and database layers where practical.
- NFR-006 Accessibility: Forms must have labels, keyboard support, visible focus, useful error messages, and adequate contrast, targeting WCAG 2.1 AA practices.
- NFR-007 Maintainability: The codebase must separate user interface, API, business rules, and persistence concerns and include migrations and tests.
- NFR-008 Observability: Production errors and important server events must be logged without exposing secrets or credentials.
- NFR-009 Recoverability: Production data must be backed up, and database restoration must be documented and tested before live reliance.
- NFR-010 Compatibility: The application should support current major mobile and desktop browsers used by the store.
- NFR-011 Time handling: Timestamps must be stored consistently, preferably in UTC, and displayed in the store's local time zone.
- NFR-012 Scope: Design decisions should favor reliable, sequential Core and Extended MVP releases for one store over premature multi-store complexity.

## 13. Database Entities and Relationships

### Core MVP entities

#### User

- `id`
- `email` or username
- password hash
- display name
- role: employee or manager
- active status
- created and updated timestamps

#### Category

- `id`
- unique name
- description
- active status

One category has many products; each product belongs to one category in both MVP stages.

#### Vendor

- `id`
- unique name
- contact name, phone, email, and notes
- active status

A vendor supplies many products in the Core MVP. In the Extended MVP, a vendor also has many purchase orders.

#### Product

- `id`
- unique SKU or internal code
- name and description
- unit description
- category ID
- preferred vendor ID, nullable
- minimum stock level
- target stock level
- expiration tracking flag, added or activated for the Extended MVP
- active status
- timestamps

Products and vendors may be many-to-many through `ProductVendor` if multiple suppliers must be retained. To control Core MVP complexity, a preferred-vendor field can be used first while keeping the schema extensible.

#### ProductVendor

- product ID
- vendor ID
- vendor product code, optional
- preferred flag
- notes

#### InventoryCount

- `id`
- status: draft or submitted
- started by user ID
- submitted by user ID, nullable
- started and submitted timestamps
- notes

An inventory count has many inventory count items.

#### InventoryCountItem

- `id`
- inventory count ID
- product ID
- counted quantity
- optional note

A uniqueness constraint should prevent duplicate product lines within one count.

### Extended MVP entities

#### ExpirationRecord

- `id`
- product ID
- expiration date
- quantity
- status or resolved flag
- recorded by user ID
- resolved by user ID, nullable
- resolution note and timestamps

A product can have multiple expiration records because different batches may expire on different dates.

#### PurchaseOrder

- `id`
- human-readable order number
- vendor ID
- status
- order date
- expected delivery date, nullable
- created by user ID
- submitted and closed timestamps
- notes

A vendor has many purchase orders; an order has many purchase-order items and delivery records.

#### PurchaseOrderItem

- `id`
- purchase order ID
- product ID
- expected quantity
- optional unit cost
- notes

Products on an order should be valid for the selected vendor, or the manager must explicitly confirm an exception.

#### Delivery

- `id`
- purchase order ID
- received by user ID
- delivery date and recorded timestamp
- vendor document/reference number, optional
- status
- notes

#### DeliveryItem

- `id`
- delivery ID
- purchase-order item ID
- delivered quantity
- damaged quantity
- incorrect-item flag or note
- notes

Missing quantity should normally be derived from expected quantity minus cumulative acceptable delivered quantity, bounded at zero. Storing a snapshot is acceptable only if reconciliation logic keeps it consistent.

#### DeliveryDiscrepancy

- `id`
- delivery ID and/or delivery-item ID
- type: missing, damaged, excess, incorrect, or other
- quantity, nullable
- status: open or resolved
- description
- resolved by user ID, resolution note, and resolved timestamp

### Relationship summary

#### Core MVP relationships

- Category 1-to-many Product
- Product many-to-many Vendor through ProductVendor, or Product many-to-1 preferred Vendor in the reduced MVP
- User 1-to-many InventoryCount
- InventoryCount 1-to-many InventoryCountItem; Product 1-to-many InventoryCountItem

#### Extended MVP relationships

- Product 1-to-many ExpirationRecord
- User 1-to-many ExpirationRecord, Delivery, and resolution actions
- Vendor 1-to-many PurchaseOrder
- PurchaseOrder 1-to-many PurchaseOrderItem
- PurchaseOrder 1-to-many Delivery
- Delivery 1-to-many DeliveryItem
- PurchaseOrderItem 1-to-many DeliveryItem to support partial deliveries
- Delivery or DeliveryItem 1-to-many DeliveryDiscrepancy

## 14. REST API Endpoint Plan

All endpoints should use a versioned prefix such as `/api/v1`, validate request and response schemas, paginate list endpoints, enforce authorization, and return consistent error structures. Core MVP endpoints are implemented first; Extended MVP endpoints are added only in the second stage.

### Core MVP endpoints

#### Authentication and users

- `POST /auth/login` - authenticate and establish or return a session/token
- `POST /auth/logout` - end the current session
- `GET /auth/me` - return the current user's identity and role
- `GET /users` - list users; manager only
- `POST /users` - create a user; manager only
- `PATCH /users/{user_id}` - update role or active state; manager only

#### Categories

- `GET /categories` - list/search categories
- `POST /categories` - create a category; manager only
- `GET /categories/{category_id}` - retrieve a category
- `PATCH /categories/{category_id}` - edit or deactivate; manager only

#### Vendors

- `GET /vendors` - list/search vendors
- `POST /vendors` - create a vendor; manager only
- `GET /vendors/{vendor_id}` - retrieve vendor details
- `PATCH /vendors/{vendor_id}` - edit or deactivate; manager only
- `GET /vendors/{vendor_id}/products` - list supplied products

#### Products

- `GET /products` - paginated search and filters
- `POST /products` - create a product; manager only
- `GET /products/{product_id}` - retrieve product and current status
- `PATCH /products/{product_id}` - edit or deactivate; manager only
- `GET /products/{product_id}/count-history` - retrieve count history
- `GET /products/low-stock` - list low-stock products and recommendations

#### Inventory counts

- `GET /inventory-counts` - list count sessions
- `POST /inventory-counts` - start a draft count
- `GET /inventory-counts/{count_id}` - retrieve count and lines
- `PATCH /inventory-counts/{count_id}` - update draft metadata
- `PUT /inventory-counts/{count_id}/items/{product_id}` - add or replace a draft quantity
- `DELETE /inventory-counts/{count_id}/items/{product_id}` - remove a draft line
- `POST /inventory-counts/{count_id}/submit` - validate and submit atomically

#### Basic dashboard

- `GET /dashboard/summary` - return low-stock and recent count summaries
- `GET /dashboard/activity` - return recent Core MVP activity, limited and paginated

### Extended MVP endpoints

#### Expiration records

- `GET /expiration-records` - list and filter expiration records
- `POST /expiration-records` - create a record
- `GET /expiration-records/{record_id}` - retrieve a record
- `PATCH /expiration-records/{record_id}` - correct or update an active record
- `POST /expiration-records/{record_id}/resolve` - record resolution
- `GET /expiration-records/alerts` - list expiring-soon and expired records

#### Purchase orders

- `GET /purchase-orders` - list and filter orders
- `POST /purchase-orders` - create a draft; manager only
- `GET /purchase-orders/{order_id}` - retrieve an order with lines and receipt summary
- `PATCH /purchase-orders/{order_id}` - edit draft/header fields; manager only
- `POST /purchase-orders/{order_id}/items` - add a draft line; manager only
- `PATCH /purchase-orders/{order_id}/items/{item_id}` - edit a line; manager only
- `DELETE /purchase-orders/{order_id}/items/{item_id}` - remove a draft line; manager only
- `POST /purchase-orders/{order_id}/submit` - submit an order; manager only
- `POST /purchase-orders/{order_id}/cancel` - cancel an eligible order; manager only
- `POST /purchase-orders/{order_id}/close` - close a reconciled order; manager only

#### Deliveries and discrepancies

- `GET /deliveries` - list and filter deliveries
- `POST /purchase-orders/{order_id}/deliveries` - record a delivery
- `GET /deliveries/{delivery_id}` - retrieve receipt details and comparison
- `PATCH /deliveries/{delivery_id}` - edit while allowed
- `POST /deliveries/{delivery_id}/submit` - finalize receipt and generate discrepancies
- `GET /delivery-discrepancies` - list and filter discrepancies
- `POST /delivery-discrepancies/{discrepancy_id}/resolve` - resolve with notes; manager only

#### Extended dashboard

- `GET /dashboard/summary` - extend the Core response with expiration, order, delivery, and discrepancy counts
- `GET /dashboard/activity` - extend recent activity with Extended MVP events

Exact endpoint shapes may be consolidated during implementation to avoid unnecessary CRUD complexity, but business actions such as submit, close, cancel, and resolve should remain explicit.

## 15. Frontend Page and Route Plan

The route names below are conceptual Next.js routes and may use route groups for layouts and access control.

### Core MVP routes

- `/login` - sign-in form
- `/dashboard` - role-aware summaries and actionable lists
- `/products` - product search, filters, stock state, and manager actions
- `/products/new` - manager product creation
- `/products/[id]` - product details, thresholds, vendors, and count history
- `/products/[id]/edit` - manager product editing
- `/categories` - manager category administration
- `/vendors` - vendor list and search
- `/vendors/new` - manager vendor creation
- `/vendors/[id]` - vendor details and products
- `/inventory-counts` - count history and start-count action
- `/inventory-counts/new` - fast count workflow
- `/inventory-counts/[id]` - count detail or draft continuation
- `/alerts/low-stock` - low-stock products and reorder recommendations
- `/users` - manager account and role administration

### Extended MVP routes

- `/expirations` - expiration search and filters
- `/expirations/new` - fast expiration entry
- `/alerts/expiring` - expiring-soon and expired worklist
- `/purchase-orders` - order list and status filters
- `/purchase-orders/new` - manager order creation
- `/purchase-orders/[id]` - order items, status, deliveries, and comparison
- `/purchase-orders/[id]/receive` - delivery receiving workflow
- `/deliveries/[id]` - delivery record and discrepancies
- `/discrepancies` - manager discrepancy review queue

Navigation should expose only relevant destinations for the signed-in role, while direct route access remains protected by server-side authorization.

## 16. Mobile Usability Requirements

- Use a mobile-first layout with no required horizontal page scrolling.
- Use touch targets of approximately 44 by 44 CSS pixels or larger.
- Keep primary actions reachable and visually consistent.
- Use numeric keyboards for quantity fields where supported.
- Allow rapid movement between count fields without reopening each product.
- Keep product name, unit, current entry, and validation state visible together.
- Provide category filters and search at the top of long count lists.
- Preserve draft entries across route navigation, refreshes, or short connection interruptions where feasible.
- Avoid dense desktop tables on narrow screens; use cards or responsive rows.
- Confirm high-impact submissions, but do not interrupt every routine line entry with a dialog.
- Display progress during counts, such as completed products versus total shown.
- Clearly distinguish saved drafts from submitted records.
- Test on representative phone, tablet, and desktop viewport sizes and with real touch interaction.
- Keep Core MVP count workflows and Extended MVP receiving workflows usable on typical store Wi-Fi; show retryable errors without discarding entered data.

## 17. Security Considerations

- Hash passwords with a modern adaptive password-hashing algorithm; never store plaintext passwords.
- Prefer secure, HTTP-only, same-site cookies for browser authentication when architecture permits.
- Require HTTPS in deployed environments.
- Enforce role permissions in FastAPI for every protected operation.
- Protect cookie-authenticated state-changing requests against CSRF.
- Validate and normalize all inputs with explicit schemas.
- Use SQLAlchemy parameterization and avoid dynamic raw SQL.
- Apply least-privilege database credentials and separate development and production secrets.
- Store secrets in environment-specific secret management, not source control.
- Rate-limit or otherwise protect login attempts and avoid revealing whether an account exists.
- Use safe error responses that do not expose stack traces or sensitive data.
- Record security-relevant and operational actions with user and timestamp information.
- Avoid hard deletion of records needed for count, order, and delivery history.
- Define session expiration and account deactivation behavior.
- Back up production data and restrict backup access.
- Keep frameworks and dependencies patched and scan them periodically.
- Do not store unnecessary payment, payroll, customer, or other sensitive information.

## 18. Testing Strategy

### Backend unit tests

Core MVP coverage:

- Reorder quantity calculations and boundary cases
- Low-stock determination
- Role and permission policies
- Inventory-count state transitions

Extended MVP coverage:

- Expiring-soon and expired date classification
- Expected, delivered, damaged, excess, and missing quantity calculations
- State-transition rules for orders, deliveries, and discrepancies

### API integration tests

Core MVP coverage:

- Authentication success, failure, logout, and inactive accounts
- Employee versus manager access to each protected action
- Product, category, and vendor validation
- Draft and submitted inventory-count behavior
- Search, filters, sorting, and pagination for Core MVP lists
- Transaction rollback on invalid Core MVP submissions

Extended MVP coverage:

- Purchase-order lifecycle and invalid transitions
- Partial and complete delivery reconciliation
- Expiration-record behavior and alerts
- Search, filtering, pagination, and transaction rollback for Extended MVP modules

Integration tests should run against PostgreSQL, not only a substitute database, so database constraints and behavior match production.

### Frontend tests

Core MVP coverage:

- Form validation and error display
- Search and filter behavior
- Count-entry workflow and draft preservation
- Reorder recommendation presentation and manager adjustment
- Responsive navigation and role-dependent controls

Extended MVP coverage:

- Expiration entry and alert presentation
- Purchase-order workflows
- Delivery-entry calculations and discrepancy warnings

### End-to-end tests

At minimum, automate these critical paths by stage:

#### Core MVP end-to-end paths

1. Manager signs in, creates catalog data, and sets stock levels.
2. Employee submits a count that causes a low-stock alert.
3. Manager reviews the recommendation and basic dashboard.

#### Extended MVP end-to-end paths

1. Manager creates and submits an order from a recommendation.
2. Employee records an incomplete or damaged delivery.
3. Manager reviews and resolves the discrepancy.
4. Employee records an expiration date and the dashboard surfaces the alert.

### Manual acceptance and usability testing

- Conduct short tests with actual store employees on a phone or tablet.
- Measure completion time and errors for counts and delivery receiving.
- Verify labels and terminology match how the store speaks about products and deliveries.
- Test weak-network and interrupted-entry scenarios.
- Perform an accessibility pass using keyboard navigation, screen-reader spot checks, and automated checks.

## 19. Deployment Strategy

### Local development

- Use Docker Compose for PostgreSQL and, where useful, the frontend and backend services.
- Keep configuration in documented environment variables with safe example values.
- Run Alembic migrations as an explicit setup step.
- Provide repeatable seed data for development and demonstrations.

### Pre-production

- Maintain a staging environment with separate credentials and data.
- Run migrations and automated tests before deployment.
- Test responsive workflows on actual store devices.
- Validate backup and restore procedures before production adoption.

### AWS production direction

A simple managed architecture should be preferred:

- Frontend: a suitable AWS web-hosting service or container deployment
- FastAPI: Amazon ECS Express Mode, or another AWS compute service selected during deployment based on current availability, cost, and operational complexity
- PostgreSQL: Amazon RDS for PostgreSQL
- Static assets: S3/CloudFront only if required
- Secrets: AWS Secrets Manager or Systems Manager Parameter Store
- Logs and monitoring: CloudWatch
- TLS and DNS: AWS Certificate Manager and Route 53 if a custom domain is used

The final AWS compute service and supporting services should be selected during deployment based on current pricing, availability, free-tier eligibility, operational complexity, and expected traffic. Infrastructure-as-code is desirable after the first stable deployment but should not delay either MVP stage.

### Release process

1. Back up production data.
2. Build immutable application artifacts.
3. Run automated tests and security checks.
4. Apply reviewed database migrations.
5. Deploy backend and frontend.
6. Run stage-appropriate smoke tests: login, dashboard, and counts for Core MVP; add expiration, orders, and deliveries for Extended MVP.
7. Monitor errors and retain a documented rollback procedure.

## 20. Development Phases

### Phase 0: Discovery and workflow validation

- Observe a real shelf count and delivery check.
- Confirm product terminology, units, categories, vendors, and user roles.
- Record baseline operating measures for ROI evaluation.
- Sketch mobile-first count and receiving workflows.
- Finalize separate Core MVP and Extended MVP acceptance criteria and data-retention rules.

### Phase 1: Core MVP foundation

- Establish frontend, backend, database, Docker, linting, formatting, and test structure.
- Create initial database models and Alembic migrations.
- Add health checks, configuration management, and basic CI.

### Phase 2: Core MVP authentication and reference data

- Implement login, logout, current-user lookup, and role enforcement.
- Implement users, products, categories, vendors, and stock-level settings.
- Build responsive catalog pages with search and filters.

### Phase 3: Core MVP inventory counts, recommendations, and dashboard

- Implement count sessions, count lines, submission, and history.
- Implement latest-count logic, low-stock rules, and reorder calculations.
- Implement the basic dashboard with low-stock and recent-count summaries.
- Optimize the phone/tablet counting interface.

### Phase 4: Core MVP hardening and pilot

- Complete Core MVP unit, integration, end-to-end, security, accessibility, and usability testing.
- Load representative product and vendor data.
- Train a small pilot group and run the Core MVP alongside the existing process.
- Fix high-impact issues and verify backup/restore procedures.
- Obtain Core MVP acceptance before beginning Extended MVP development.

### Phase 5: Extended MVP expiration tracking

- Implement expiration entry, status calculation, filters, alerts, and resolution.
- Validate the process with products that commonly expire.

### Phase 6: Extended MVP purchase orders and deliveries

- Implement order drafting, submission, status transitions, and line items.
- Implement delivery receiving, partial-delivery handling, and discrepancy calculation.
- Implement manager discrepancy review and resolution.

### Phase 7: Extended MVP dashboard and operational polish

- Extend dashboard summaries and prioritized lists with expiration, order, delivery, and discrepancy information.
- Complete cross-module search, filtering, empty states, and error recovery.
- Improve accessibility and responsive behavior.

### Phase 8: Extended MVP hardening and pilot

- Complete Extended MVP unit, integration, end-to-end, security, and usability testing.
- Train the pilot group on the new expiration, ordering, and delivery workflows.
- Run the Extended MVP alongside the existing purchasing and delivery process.
- Fix high-impact issues and verify backup/restore procedures.

### Phase 9: Production launch and evaluation

- Deploy the accepted Core MVP first, then deploy the Extended MVP when its acceptance criteria are met.
- Monitor usage, errors, data quality, and performance.
- Compare post-launch measures with the baseline.
- Prioritize post-Extended-MVP work using observed store needs rather than assumptions.

For a solo developer, phases should be delivered as small vertical slices. The Core MVP must become usable and accepted before any Extended MVP expiration, purchasing, or delivery features are implemented.

## 21. Features Postponed Until After the Extended MVP

The following are explicitly outside both the Core MVP and Extended MVP:

- Payroll
- Employee scheduling
- Fuel pricing
- POS integration
- Cash reconciliation
- AI forecasting
- Barcode hardware integration
- Accounting integration

Other reasonable post-Extended-MVP candidates include:

- Multi-store support and inventory transfers
- Automated purchase-order transmission to vendors
- Vendor self-service access
- Email, SMS, or push notifications
- Sales-based perpetual inventory
- Demand forecasting and seasonality
- Barcode scanning after hardware and workflow evaluation
- Product images and document/photo attachments
- Vendor pricing history and advanced cost analytics
- Lot numbers and formal recall workflows
- Offline-first synchronization
- Advanced reports and export templates
- Fine-grained custom roles beyond employee and manager

Post-Extended-MVP items should not influence the initial design enough to delay or complicate the core store workflows.

## 22. Risks and Limitations

### Data accuracy risk

Manual input can contain mistakes. Use validation, clear units, confirmation summaries, and history, but recognize that the system is only as accurate as submitted counts and delivery records.

### Adoption risk

Employees may return to visual checks if entry is slow. Test the count interface with real users, minimize taps, and make the dashboard immediately useful.

### Stale inventory limitation

Without POS integration, quantities are snapshots from physical counts rather than real-time stock. The UI must show the date and time of the latest count so recommendations are not mistaken for live inventory.

### Expiration granularity risk

Expiration tracking requires batch-level quantity entry and ongoing adjustment. This may be burdensome for every product, so it should be enabled only for products where the value justifies the effort.

### Reorder calculation limitation

Target-minus-current is intentionally simple and does not account for sales velocity, lead-time variation, promotions, seasonality, case-pack constraints, or minimum vendor orders. Managers must review recommendations.

### Delivery interpretation risk

Partial deliveries, substitutions, overages, credits, and damaged goods can complicate reconciliation. Before Extended MVP implementation, the project should define its quantity formulas and status transitions and provide explanatory notes.

### Scope and schedule risk

The combined Core and Extended MVP stages cross several business domains. A solo developer should enforce the stage boundary, use vertical milestones, defer nonessential customization, and avoid building generic enterprise abstractions.

### Security and privacy risk

Authentication, authorization, secret handling, and dependency maintenance require deliberate work even though the system holds limited personal data. Security cannot be deferred until deployment.

### Connectivity and device risk

Store Wi-Fi or mobile connectivity may be unreliable, and device sizes vary. The Core MVP may not provide full offline operation, but it must protect draft input and make network errors recoverable; the same standard applies to Extended MVP workflows.

### Operational dependency risk

Once the store relies on the platform, downtime or data loss can disrupt ordering. Managed hosting, monitoring, backups, restore testing, and a temporary manual fallback process are necessary.

### Single-store limitation

Both MVP stages assume one location and one shared inventory context. Adding locations later will require explicit location ownership on many entities and should not be implied by the initial data model.

## 23. Definition of Project Success

The project uses separate success gates. The Core MVP must be deployed or pilot-ready, trusted by the store team, and useful for routine inventory and replenishment decisions before the Extended MVP begins. The Extended MVP succeeds when expiration, purchasing, and delivery controls add measurable operational value without weakening Core MVP usability.

### Core MVP completion criteria

- Employees and managers can securely sign in with correct role restrictions.
- Managers can maintain products, categories, vendors, and stock thresholds.
- Employees can complete and submit a practical inventory count on a phone or tablet.
- Count history clearly identifies quantities, users, and timestamps.
- Low-stock products and explainable reorder quantities are calculated correctly.
- The basic dashboard shows low-stock and recent-count information and links to relevant Core MVP workflows.
- Search and filtering work across Core MVP operational lists where needed.
- Critical Core MVP automated tests pass, production backups exist, and restore instructions are verified.

### Extended MVP completion criteria

- Expiration records produce useful expiring-soon and expired alerts.
- Managers can create purchase orders with expected quantities.
- Employees can record deliveries, damage, missing quantities, and incorrect items.
- The system flags delivery discrepancies and supports manager resolution.
- Extended dashboard summaries link users to actionable expiration, order, delivery, and discrepancy views.
- Search and filtering work across Extended MVP operational lists where needed.
- Critical Extended MVP automated tests pass without regressing Core MVP workflows.
- No explicitly excluded feature is required to complete the core workflows.

### Operational success indicators

Initial targets should be confirmed after baseline measurement. The Core MVP pilot should aim for:

- At least 90% of scheduled inventory counts completed in StationStock.
- Typical focused count sessions completed within an agreed time established during discovery.
- At least 90% of active stocked products having valid minimum and target levels.

After the Extended MVP launches, the pilot should also aim for:

- All recorded submitted purchase orders reconciled against a delivery or explicitly cancelled.
- All material delivery discrepancies documented and visible until resolved.
- A measurable reduction in observed stockout incidents and expired-product waste over a representative comparison period.
- Positive usability feedback from the manager and participating employees, with no unresolved critical workflow blockers.

Success does not require eliminating all stockouts, waste, or human judgment. The Core MVP must provide a reliable inventory-counting and replenishment process; the Extended MVP must build on it with practical expiration and delivery controls.

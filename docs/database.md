# NEXUS — Database Design

**Project:** NEXUS — Autonomous Enterprise AI Platform  
**Document:** Database Design  
**Version:** 0.1.0  
**Status:** Initial Draft

## 1. Purpose

This document defines the initial relational data model for the fictional business environment used by NEXUS.

The database will support business analytics and will eventually provide data for machine learning, AI-assisted investigation, and controlled workflow automation.

PostgreSQL is the planned primary relational database.

## 2. Initial Business Scenario

NEXUS will initially work with a fictional retail company that sells products to customers across multiple regions.

The company maintains information about:

- Customers
- Products
- Orders
- Order items
- Support tickets
- Invoices

The first business question we intend to support is:

"Why did sales revenue decline in Mumbai last month?"

The data model must allow the system to compare revenue across periods and regions and investigate changes in order volume and product performance.

## 3. Entity Relationships

The initial conceptual relationships are:

```text
CUSTOMERS
    |
    | 1:N
    v
  ORDERS
    |
    | 1:N
    v
ORDER_ITEMS
    ^
    | N:1
    |
 PRODUCTS
```

Additional business entities will be introduced later:

```text
CUSTOMERS
    |
    ├── SUPPORT_TICKETS
    |
    └── INVOICES
```

A customer can place multiple orders. An order can contain multiple order items, and a product can appear in multiple order items.

## 4. Initial Entities

### 4.1 Customers

Table: `customers`

| Column | PostgreSQL type | Purpose |
|---|---|---|
| id | BIGINT | Primary key |
| customer_code | VARCHAR(50) | Unique business identifier |
| name | VARCHAR(150) | Customer name |
| email | VARCHAR(255) | Customer email |
| created_at | TIMESTAMPTZ | Record creation time |

Constraints:

- `id` is the primary key.
- `customer_code` is unique and not null.
- `name` is not null.
- `email` should be unique when the business rules require it.

### 4.2 Products

Table: `products`

| Column | PostgreSQL type | Purpose |
|---|---|---|
| id | BIGINT | Primary key |
| sku | VARCHAR(80) | Unique product identifier |
| name | VARCHAR(200) | Product name |
| category | VARCHAR(100) | Product category |
| current_price | NUMERIC(12,2) | Current selling price |
| is_active | BOOLEAN | Whether the product is active |
| created_at | TIMESTAMPTZ | Record creation time |

Constraints:

- `id` is the primary key.
- `sku` is unique and not null.
- `current_price` must not be negative.

### 4.3 Orders

Table: `orders`

| Column | PostgreSQL type | Purpose |
|---|---|---|
| id | BIGINT | Primary key |
| order_number | VARCHAR(50) | Unique business identifier |
| customer_id | BIGINT | Foreign key to customers |
| order_date | TIMESTAMPTZ | Order timestamp |
| region | VARCHAR(100) | Business region associated with the order |
| status | VARCHAR(30) | Order status |
| created_at | TIMESTAMPTZ | Record creation time |

Constraints:

- `id` is the primary key.
- `order_number` is unique and not null.
- `customer_id` references `customers.id`.
- `order_date` is not null.
- `status` must be one of the supported order statuses.

The order's region is recorded with the order so historical regional reporting does not automatically change when a customer's current address changes.

### 4.4 Order Items

Table: `order_items`

| Column | PostgreSQL type | Purpose |
|---|---|---|
| id | BIGINT | Primary key |
| order_id | BIGINT | Foreign key to orders |
| product_id | BIGINT | Foreign key to products |
| quantity | INTEGER | Number of units |
| unit_price_at_purchase | NUMERIC(12,2) | Price per unit at purchase |
| discount_amount | NUMERIC(12,2) | Discount applied to the line |
| created_at | TIMESTAMPTZ | Record creation time |

Constraints:

- `id` is the primary key.
- `order_id` references `orders.id`.
- `product_id` references `products.id`.
- `quantity` must be greater than zero.
- `unit_price_at_purchase` must not be negative.
- `discount_amount` must not be negative.
- The discount must not exceed the line's gross amount.

The purchase price is stored separately from the product's current price because product prices may change over time.

## 5. Revenue Calculation

For the initial analytics use case:

**Line revenue:**

`quantity × unit_price_at_purchase − discount_amount`

**Order revenue:**

The sum of the line revenues for the order.

**Regional revenue:**

The sum of eligible order-line revenue grouped by the order's region and selected time period.

The business must define how cancellations, refunds, taxes, shipping charges, and returns affect revenue reporting before those cases are implemented.

We will derive revenue from order items rather than storing a duplicate `sales` table in the initial model.

This reduces the risk of inconsistent totals.

## 6. Future Entities

These entities are planned but are not required for the first database implementation.

### Support Tickets

Potential fields:

- `id`
- `customer_id`
- `subject`
- `description`
- `status`
- `priority`
- `created_at`
- `resolved_at`

### Invoices

Potential fields:

- `id`
- `invoice_number`
- `customer_id`
- `order_id`
- `issue_date`
- `due_date`
- `status`
- `total_amount`

The final schemas will depend on the workflows we choose to implement.

## 7. Data Integrity

The database should enforce integrity through:

- Primary keys.
- Foreign keys.
- Unique constraints.
- Not-null constraints.
- Appropriate check constraints.
- Transactions for operations that must succeed or fail together.

Application validation and database constraints serve complementary purposes.

## 8. Indexing Strategy

We will introduce indexes based on query patterns and measured performance.

Initial candidates include:

- `orders(order_date)`
- `orders(region, order_date)`
- `orders(customer_id)`
- `order_items(order_id)`
- `order_items(product_id)`

Primary keys and unique constraints will provide their associated indexes where PostgreSQL creates them.

Additional indexes will be justified by query plans and observed performance rather than added indiscriminately.

## 9. Data Quality

The fictional dataset should include realistic scenarios:

- Different order volumes across regions.
- Products with different prices and categories.
- Seasonal revenue changes.
- Cancelled orders.
- Customers with multiple orders.
- Products with declining sales.

The dataset must support testing both expected behavior and edge cases.

No generated dataset should be presented as real company data.

## 10. Initial Implementation Scope

The first database implementation will focus on:

1. Customers.
2. Products.
3. Orders.
4. Order items.
5. Database migrations and constraints.
6. A small, reproducible fictional dataset.
7. Tests for relationships and revenue calculations.

Support tickets, invoices, and other entities will be added when required by a selected workflow.

## 11. Open Decisions

The following decisions require further specification:

- Exact order status values.
- Revenue treatment for cancellations and refunds.
- Currency handling.
- Whether customer email addresses must be unique.
- Historical region and address rules.
- Organization and tenant isolation requirements.
- Data retention and deletion policies.

These decisions must be resolved before the corresponding production functionality is implemented.

## 12. Current Status

The database model is a proposed design. No database tables or migrations have been implemented yet.

The schema will be revised as we define the first working analytics use case.
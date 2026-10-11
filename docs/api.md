# NEXUS — API Design

**Status:** Proposed  
**Version:** 1.0  
**Base path:** `/api/v1`

## 1. Purpose

This document defines how clients communicate with the NEXUS backend. It establishes API conventions, initial endpoints, request and response formats, error handling, validation, and security expectations.

These endpoints are planned, not yet implemented.

## 2. API Principles

- Use REST conventions for business resources.
- Version public endpoints using `/api/v1`.
- Exchange data in JSON format.
- Use consistent naming and error responses.
- Validate incoming data at the API boundary.
- Keep business logic in application services, not route handlers.
- Never expose credentials, secrets, or internal stack traces.
- Document changes to API behavior.

## 3. Base URL

Local development:

`http://localhost:8000`

Versioned API prefix:

`/api/v1`

Example:

`http://localhost:8000/api/v1/health`

## 4. Initial Endpoints

### 4.1 Health Check

**Method:** `GET`

**Path:** `/api/v1/health`

**Purpose:** Check whether the API service is responding.

Example response:

```json
{
  "status": "ok",
  "service": "nexus-api",
  "version": "0.1.0"
}
```

The initial health check confirms application availability. Database and external dependency checks can be introduced separately.

### 4.2 Customers

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/customers` | List customers |
| GET | `/api/v1/customers/{customer_id}` | Retrieve one customer |
| POST | `/api/v1/customers` | Create a customer |

Planned customer fields:

- `id`
- `customer_code`
- `name`
- `email`
- `created_at`

Example creation request:

```json
{
  "customer_code": "CUST-001",
  "name": "Aarav Sharma",
  "email": "aarav@example.com"
}
```

Example response:

```json
{
  "id": 1,
  "customer_code": "CUST-001",
  "name": "Aarav Sharma",
  "email": "aarav@example.com",
  "created_at": "2026-10-12T10:00:00Z"
}
```

The example values are illustrative, not real customer data.

### 4.3 Products

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/products` | List products |
| GET | `/api/v1/products/{product_id}` | Retrieve one product |
| POST | `/api/v1/products` | Create a product |

Planned product fields:

- `id`
- `sku`
- `name`
- `category`
- `current_price`
- `is_active`
- `created_at`

### 4.4 Orders

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/v1/orders` | List orders |
| GET | `/api/v1/orders/{order_id}` | Retrieve an order and its items |
| POST | `/api/v1/orders` | Create an order |

An order may include:

- `id`
- `order_number`
- `customer_id`
- `order_date`
- `region`
- `status`
- `items`

Each item references a product and contains its quantity, purchase price, and discount amount.

Order creation must validate the customer, products, quantities, and prices. The order and its items must be persisted consistently in a database transaction.

## 5. List Endpoint Conventions

List endpoints should support pagination as the data grows.

Proposed query parameters:

- `limit`: maximum number of records to return.
- `offset`: number of records to skip.

Example:

`GET /api/v1/customers?limit=20&offset=0`

Example response:

```json
{
  "items": [],
  "limit": 20,
  "offset": 0,
  "total": 0
}
```

Filtering, sorting, and search parameters will be specified when individual endpoint requirements are implemented.

## 6. HTTP Status Codes

| Status | Meaning |
|---|---|
| `200 OK` | Request succeeded |
| `201 Created` | Resource created successfully |
| `204 No Content` | Request succeeded without a response body |
| `400 Bad Request` | Request is malformed or invalid |
| `401 Unauthorized` | Authentication is required or invalid |
| `403 Forbidden` | Caller lacks permission |
| `404 Not Found` | Resource does not exist |
| `409 Conflict` | Request conflicts with existing data |
| `422 Unprocessable Entity` | Request data fails validation |
| `429 Too Many Requests` | Rate limit exceeded |
| `500 Internal Server Error` | Unexpected server failure |

The exact status code for validation errors will follow the chosen framework's conventions consistently.

## 7. Error Response Format

Errors should use a consistent JSON structure.

Example:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested customer was not found.",
    "details": []
  }
}
```

Rules:

- `code` is a stable, machine-readable identifier.
- `message` is a safe, human-readable explanation.
- `details` may contain field-level validation information.
- Internal stack traces, database credentials, and secrets must never appear in responses.

## 8. Validation Rules

- Required fields must be present.
- Email addresses must use a valid format.
- Customer codes and product SKUs must follow defined uniqueness rules.
- Prices and discounts must be non-negative.
- Quantities must be positive integers.
- Referenced customers and products must exist.
- Order items must satisfy business rules before persistence.
- Unknown or unsupported input fields must be handled consistently.

## 9. Security

Before exposing the API beyond local development, NEXUS must implement appropriate authentication and authorization.

Security requirements:

- Store secrets in environment variables or an approved secrets manager.
- Never commit `.env` files or credentials.
- Validate all incoming data.
- Apply authorization checks to protected resources.
- Avoid exposing sensitive customer information unnecessarily.
- Add request-size limits and rate limiting where appropriate.
- Log security-relevant events without logging passwords, tokens, or other secrets.

Authentication and multi-tenant authorization details remain design decisions to resolve before production use.

## 10. API Testing

Planned tests include:

- Successful health-check response.
- Successful customer and product creation.
- Retrieval of existing resources.
- `404` behavior for missing resources.
- Validation failures for invalid input.
- Duplicate customer codes and product SKUs.
- Order creation with valid and invalid references.
- Transaction behavior when order creation fails.
- Authentication and authorization checks when implemented.

Tests should cover successful requests, invalid input, edge cases, and failure paths.

## 11. Implementation Boundaries

API route handlers should remain thin:

1. Parse and validate the request.
2. Call the appropriate application service.
3. Return the result using the documented response format.

Business rules belong in application or domain logic. Database access belongs in the persistence layer.

The API must not directly contain model training, LLM prompting, RAG retrieval, or agent execution logic. Those capabilities will be exposed through separately designed application services and endpoints as the platform evolves.

## 12. Current Status

This document describes the proposed API contract. No endpoint should be considered implemented until its code and tests exist.

Initial implementation order:

1. Health check.
2. Database connection and persistence foundation.
3. Customer endpoints.
4. Product endpoints.
5. Order endpoints.
6. Automated API tests.

AI, ML, document retrieval, and agent-related endpoints will be designed after the initial backend foundation is working.

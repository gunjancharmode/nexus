# ADR-001: Start with a Modular Monolith

- **Status:** Accepted
- **Date:** 2026-10-12
- **Decision owners:** NEXUS project

## 1. Context

NEXUS is an enterprise AI platform intended to evolve to support business analytics, machine learning, knowledge retrieval, LLM integration, controlled tool execution, and workflow automation.

The project is being developed incrementally by a single developer who is learning and implementing the system while building a job-ready portfolio.

Starting with a distributed architecture would introduce additional deployment, communication, debugging, and operational complexity before the system has demonstrated a need for it.

## 2. Decision

NEXUS will begin as a modular monolith.

The initial backend will run as one application with clearly separated modules and responsibilities.

Modules will communicate through explicit interfaces and application-level dependencies rather than unnecessary network calls between separate services.

## 3. Alternatives Considered

### Option A: Modular Monolith

One deployable application with internal module boundaries.

Advantages:
- Simpler local development.
- Easier debugging and testing.
- Fewer infrastructure requirements.
- Straightforward transactions and application-level coordination.
- Supports clear boundaries between business capabilities.

Disadvantages:
- Requires discipline to prevent tightly coupled modules.
- Independent scaling of individual modules is limited.
- Poor module boundaries can make later separation harder.

### Option B: Microservices from the Beginning

Multiple independently deployed services communicating over network interfaces.

Advantages:
- Independent deployment and scaling.
- Clear service-level ownership when multiple teams are involved.
- Isolation of some operational failures.

Disadvantages:
- Additional deployment and infrastructure complexity.
- Network communication and distributed failure handling.
- More difficult local development and integration testing.
- Unnecessary overhead before service boundaries are understood.

## 4. Rationale

The modular monolith provides the simplest architecture that supports the current requirements while preserving room for future evolution.

It allows NEXUS to establish reliable software-engineering practices before introducing distributed-system complexity.

## 5. Consequences

### Positive Consequences

- Faster initial development.
- Fewer infrastructure dependencies.
- Easier end-to-end debugging.
- Clear internal module boundaries can be tested.
- The project can evolve incrementally.

### Negative Consequences

- Modules must be prevented from depending excessively on internal implementation details of other modules.
- Resource-intensive workloads may eventually compete with API requests.
- Separating a module later will require careful interface and data-boundary design.

## 6. Conditions for Reconsideration

A module may be separated into an independent process or service if evidence demonstrates a meaningful need, such as:

- Independent scaling requirements.
- Long-running workloads that interfere with API responsiveness.
- Different deployment or resource requirements.
- Strong isolation requirements.
- A clear operational or organizational benefit.

The decision must be supported by requirements or measurements rather than technology preference alone.

## 7. Implementation Notes

The initial backend will use clear internal boundaries for API handling, application services, domain logic, repositories, and configuration.

The project will not introduce microservices, message brokers, or orchestration infrastructure solely to make the architecture appear more advanced.

## 8. References

- `docs/requirements.md`
- `docs/architecture.md`

## 9. Review History

- Version 0.1: Initial decision for the NEXUS project.
# Feature Specification: Silver Transforms (Conformed Delta Tables)

**Feature Branch**: `[003-silver-transforms]`  
**Created**: 2026-05-08  
**Status**: Draft  
**Input**: User description: "Implement next step after Bronze: Silver transforms following Spec Kit."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Produce typed, conformed Silver tables from Bronze (Priority: P1)

As a data engineer, I want to transform Bronze tables into Silver tables with consistent types and minimal business rules so downstream marts are stable and easier to query.

**Why this priority**: Silver is the conformed layer that reduces repeated cleaning/typing and sets up Gold modeling.

**Independent Test**: Run Silver for `dt=2026-01-01` and confirm Silver tables exist and have expected columns/types.

**Acceptance Scenarios**:

1. **Given** Bronze tables exist for `dt=2026-01-01`, **When** I run Silver transforms for `dt=2026-01-01`, **Then** the Silver tables are created/updated: orders, order_lines, inventory_snapshot, fulfilment_events.
2. **Given** a completed Silver run for `dt=2026-01-01`, **When** I rerun Silver for the same date, **Then** the output is idempotent (no duplicates for that partition/day).
3. **Given** Silver orders and fulfilment tables, **When** I query delivery KPIs, **Then** derived fields exist to support later Gold (e.g., `delivery_minutes`, `delivered_on_time_flag`).

---

### User Story 2 - Enforce basic referential sanity within the day (Priority: P2)

As a data engineer, I want to ensure basic integrity rules are applied (or at least measurable) in Silver so data issues are caught early.

**Why this priority**: Prevents low-quality data from silently propagating.

**Independent Test**: Query counts of orphan order lines (lines without orders) and confirm they are filtered or isolated per policy.

**Acceptance Scenarios**:

1. **Given** Bronze orders and order_lines for `dt`, **When** Silver is produced, **Then** Silver order_lines only contains lines with a matching Silver order for that `dt` (no orphans).

---

### Edge Cases

- Duplicate orders in Bronze for the same `order_id` and `dt`
- Late/malformed timestamps in fulfilment events

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST read from Bronze Delta tables (by UC table or Delta path) and write Silver Delta tables.
- **FR-002**: System MUST be parameterized by `dt`.
- **FR-003**: System MUST standardize types for key fields (timestamps, ints).
- **FR-004**: System MUST be idempotent per `dt`.
- **FR-005**: System MUST apply a clear orphan policy for order_lines.

### Key Entities *(include if feature involves data)*

- **SilverOrder**: typed `order_ts`, `promised_delivery_ts`, standard keys
- **SilverOrderLine**: typed `line_number`, `quantity`, standard keys
- **SilverInventorySnapshot**: typed quantities
- **SilverFulfilmentEvent**: typed timestamps and derived delivery duration

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Silver run completes for 1 day with no manual data fixes.
- **SC-002**: Orphan order_lines count is 0 in Silver for the day.
- **SC-003**: Rerunning Silver does not change row counts for the same `dt` (stable/idempotent).

## Assumptions

- Unity Catalog is available; tables are registered under `retail_lakehouse.bronze.*`.
- Silver storage will use a new UC schema `retail_lakehouse.silver` with a volume-backed location.


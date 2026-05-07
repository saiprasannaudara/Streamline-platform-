# Feature Specification: Synthetic Retail Data Generator

**Feature Branch**: `[001-synthetic-data-generator]`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Start the project following Spec Kit; generate synthetic (non-proprietary) retail data for lakehouse ingestion."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate a reproducible “daily drop” dataset (Priority: P1)

As a data engineer, I want to generate reproducible synthetic retail datasets locally so I can develop and test lakehouse ingestion pipelines without using proprietary data.

**Why this priority**: It unlocks the rest of the project (Bronze ingestion, Silver/Gold transforms, DQ gates).

**Independent Test**: Run the generator for 2 days and verify expected folders/files exist and are non-empty.

**Acceptance Scenarios**:

1. **Given** a clean workspace, **When** I run `python -m retail_lakehouse.generate --days 2 --start-date 2026-01-01`, **Then** the generator creates `data/landing/` with the expected dataset folders and daily partitions.
2. **Given** the same arguments and seed, **When** I run the generator twice, **Then** outputs are reproducible (same record counts per file for a given day).

---

### User Story 2 - Keep data safe for public sharing (Priority: P2)

As a project owner, I want to ensure generated data contains no real personal data and is safe to share publicly.

**Why this priority**: This is a portfolio project and must stay within ethical/confidentiality boundaries.

**Independent Test**: Inspect the generated datasets for the absence of direct identifiers (email, phone, full address).

**Acceptance Scenarios**:

1. **Given** generated customer data, **When** I inspect customer fields, **Then** there are no direct identifiers (no email/phone/full address).

---

### Edge Cases

- What happens when `--days 0` is passed?
- What happens when the output directory already contains generated data?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST generate static dimension datasets: stores, products, customers.
- **FR-002**: The system MUST generate daily partitioned fact datasets for orders and operational events.
- **FR-003**: The system MUST support reproducible generation via a seed.
- **FR-004**: The system MUST write output under `data/landing/` by default.
- **FR-005**: The system MUST be runnable locally via a CLI entry point.

### Key Entities *(include if feature involves data)*

- **Store**: `store_id`, region, type, opened date
- **Product**: `product_id`, category, unit price/cost, active flag
- **Customer**: `customer_id`, tier, signup date, home region (no direct identifiers)
- **Order**: `order_id`, timestamp, channel, store, customer, promised delivery
- **OrderLine**: `order_id`, line number, product, quantity
- **InventorySnapshot**: snapshot date, store, product, on-hand quantity
- **FulfilmentEvent**: order lifecycle timestamps and on-time flag

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Generator produces at least 2 days of data in under 60 seconds on a typical laptop.
- **SC-002**: Output folder structure matches the documented quickstart and remains stable.
- **SC-003**: No direct personal identifiers are present in generated datasets.

## Assumptions

- Python is available locally and dependencies can be installed via `pip`.
- Generated data volume is “dev-friendly” (not intended for large-scale performance benchmarking).


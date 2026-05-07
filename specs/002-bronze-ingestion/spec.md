# Feature Specification: Bronze Ingestion (Databricks Lakehouse)

**Feature Branch**: `[002-bronze-ingestion]`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Next step after synthetic generator: implement Bronze ingestion on Databricks following Spec Kit."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ingest landing data into Bronze Delta tables (Priority: P1)

As a data engineer, I want to ingest the generated landing datasets into Bronze Delta tables so downstream Silver/Gold transformations can be built on reliable, queryable data.

**Why this priority**: Bronze is the foundation of the medallion architecture and unlocks all subsequent features.

**Independent Test**: Run the Bronze workflow for 1 day and confirm Bronze tables exist and contain records with ingestion metadata.

**Acceptance Scenarios**:

1. **Given** landing data exists under the configured landing path, **When** I run the Bronze workflow for a date `dt=2026-01-01`, **Then** Bronze tables are created/updated for orders, order_lines, inventory_snapshot, fulfilment_events.
2. **Given** a completed Bronze run for `dt=2026-01-01`, **When** I rerun the same Bronze workflow for the same date, **Then** the result is idempotent (no duplicate rows for that partition/day).
3. **Given** a Bronze run, **When** I query Bronze tables, **Then** each row includes ingestion metadata fields (at minimum: `ingestion_ts`, `source_path`, `load_id`, `dt`).

---

### User Story 2 - Support schema evolution safely (Priority: P2)

As a data engineer, I want the Bronze ingestion to handle minor schema changes safely so the pipeline doesn’t break unexpectedly.

**Why this priority**: Real pipelines encounter schema drift; Bronze should be resilient but controlled.

**Independent Test**: Add an extra column to one landing dataset and confirm the ingestion either captures it or routes it to quarantine per policy.

**Acceptance Scenarios**:

1. **Given** a new nullable column appears in the landing orders feed, **When** I run Bronze ingestion, **Then** the pipeline continues successfully and the new column is available (or is recorded as drift according to the chosen policy).

---

### Edge Cases

- Landing path missing for a given `dt` (should be a clean failure with a clear error).
- Partial landing data (orders exist but fulfilment events missing) — define expected behavior.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST ingest landing datasets into Delta Lake Bronze tables in Databricks.
- **FR-002**: System MUST be parameterized by `dt` (business date) and environment (dev/test).
- **FR-003**: System MUST write ingestion metadata fields to Bronze.
- **FR-004**: System MUST be idempotent for a given `dt` (reruns do not duplicate data).
- **FR-005**: System SHOULD use a consistent naming convention for Bronze tables and paths.

### Key Entities *(include if feature involves data)*

- **BronzeOrder**: raw order record + metadata
- **BronzeOrderLine**: raw line record + metadata
- **BronzeInventorySnapshot**: raw snapshot record + metadata
- **BronzeFulfilmentEvent**: raw event record + metadata

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Bronze ingestion for 1 day completes with no manual intervention.
- **SC-002**: Rerunning Bronze for the same `dt` results in no duplicates.
- **SC-003**: Ingestion metadata is present and queryable for operational debugging.

## Assumptions

- A Databricks workspace is available (Community/Trial is acceptable for portfolio).
- Landing data is accessible to Databricks (local upload to DBFS, or ADLS Gen2 path).
- Unity Catalog may or may not be available; the feature must work without UC (catalog optional).


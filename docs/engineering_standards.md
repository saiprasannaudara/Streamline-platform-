# Engineering standards (project-local)

These standards exist to make the portfolio demonstrably production-minded.

## Layering rules (Medallion)

- **Bronze**: raw ingestion, append-only, minimal transformation, ingestion metadata required.
- **Silver**: cleaned/conformed, deduplicated, business keys established, incremental strategy documented.
- **Gold**: curated marts and KPIs with clearly documented metric definitions and grains.

## Naming conventions

- **Storage paths**: `landing/<dataset>/dt=YYYY-MM-DD/...` for daily drops where applicable.
- **Tables**:
  - Bronze: `brz_<domain>_<entity>`
  - Silver: `slv_<domain>_<entity>`
  - Gold: `gld_<domain>_<entity>` and `gld_kpi_<name>`

## Idempotency

Each pipeline step must document and implement a rerun-safe approach:

- append with `load_id` + dedupe on business keys, or
- merge/upsert, or
- overwrite partitions (with careful partitioning).

## Data quality (DQ)

- DQ checks must produce:
  - a **result table** with rule name, status, and metrics
  - a **gate decision** (pass/fail) for critical rules
- Critical rules must fail the workflow.

## Operability

- Every workflow has:
  - run parameters (at least date/environment)
  - retry policy
  - run log output (table or log sink)


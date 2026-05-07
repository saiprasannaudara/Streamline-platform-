# Retail Lakehouse Portfolio Constitution

This constitution governs how we plan and implement the **Retail Lakehouse on Azure Databricks** portfolio project using **Spec Kit**.

## Core Principles

### I. Spec-first delivery (NON-NEGOTIABLE)

Work must follow Spec Kit:

- Every milestone is captured in `specs/<feature>/spec.md`.
- Implementation is guided by `specs/<feature>/plan.md` and `specs/<feature>/tasks.md`.
- Code changes should be traceable to requirements and acceptance scenarios in the spec.

### II. Production-minded by default

Even as a portfolio project, engineering decisions must reflect real delivery:

- Idempotent/replayable pipelines
- Clear layers (Bronze/Silver/Gold) with table/path conventions
- Data quality gates and run logs
- Secrets are never committed to git

### III. Simplicity and thin slices

Prefer small, independently testable slices of functionality. Avoid speculative features unless they are explicitly in-scope for the current spec.

### IV. Clear “no proprietary data” boundary

- No M&S internal or proprietary datasets.
- Default datasets are synthetic and non-identifying.
- Optional public datasets require explicit license/attribution documentation.

### V. Cloud + ETL stack constraints

Primary implementation target:

- **Cloud**: Azure
- **Compute/ETL**: Databricks (PySpark + Spark SQL), Delta Lake
- **Orchestration**: Databricks Workflows

Local development should remain possible for the non-cloud parts (e.g. data generation, config validation).

## Additional Constraints

- **Language (local tooling)**: Python (3.10+ acceptable)
- **Repo structure**: `docs/`, `src/`, `infra/`, `pipelines/`, `sql/`, `specs/`
- **Generated data**: lives under `data/` and is git-ignored

## Workflow & Quality Gates

- A feature is “done” only when:
  - its acceptance scenarios are satisfied, and
  - quickstart instructions are accurate, and
  - lint/format is clean for touched files (where tools exist).
- Avoid adding test requirements unless the spec explicitly requests tests.

## Governance

- This constitution supersedes other local documentation.
- Amendments require an update to this file and a short note in the next spec’s assumptions/constraints.

**Version**: 1.0.0 | **Ratified**: 2026-05-07 | **Last Amended**: 2026-05-07

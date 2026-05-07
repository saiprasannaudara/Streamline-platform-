---

description: "Tasks for synthetic data generator feature"
---

# Tasks: Synthetic Retail Data Generator

**Input**: `specs/001-synthetic-data-generator/spec.md`, `specs/001-synthetic-data-generator/plan.md`

## Phase 1: Setup (Shared Infrastructure)

- [ ] T001 Create the `specs/001-synthetic-data-generator/` spec/plan/tasks docs (done in repo)
- [ ] T002 Ensure repo quickstart exists in `README.md` and aligns with CLI command

## Phase 2: User Story 1 - Generate a reproducible “daily drop” dataset (P1)

**Independent Test**: run generator for 2 days and confirm outputs exist and are non-empty

- [ ] T010 Implement generator CLI in `src/retail_lakehouse/generate.py`
- [ ] T011 Ensure default output is `data/landing/` and daily partitions are `dt=YYYY-MM-DD`
- [ ] T012 Add reproducibility via `--seed`

## Phase 3: User Story 2 - Keep data safe for public sharing (P2)

**Independent Test**: inspect customer fields for lack of direct identifiers

- [ ] T020 Ensure generated customer dataset has no direct identifiers (email/phone/full address)
- [ ] T021 Document data safety policy in `docs/data_sources.md`

## Phase 4: Validate quickstart (Polish)

- [ ] T030 Validate local quickstart steps in `README.md` are accurate


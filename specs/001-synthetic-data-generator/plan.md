# Implementation Plan: Synthetic Retail Data Generator

**Branch**: `[001-synthetic-data-generator]` | **Date**: 2026-05-07 | **Spec**: `specs/001-synthetic-data-generator/spec.md`
**Input**: Feature specification from `specs/001-synthetic-data-generator/spec.md`

## Summary

Implement a local Python CLI to generate reproducible, synthetic retail datasets (dimensions + daily facts) under `data/landing/` for downstream lakehouse ingestion.

## Technical Context

**Language/Version**: Python (3.10+)  
**Primary Dependencies**: `typer`, `faker`, `python-dateutil`  
**Storage**: local filesystem (`data/`)  
**Testing**: lightweight manual verification now (automated tests are out of scope unless later specified)  
**Target Platform**: Windows (PowerShell)  
**Project Type**: CLI tool / library module

## Constitution Check

*GATE: Must pass before implementation.*

- Spec-first delivery: **PASS** (spec exists)
- No proprietary data: **PASS** (synthetic generator only)
- Simplicity: **PASS** (single capability, small scope)

## Project Structure

### Documentation (this feature)

```text
specs/001-synthetic-data-generator/
├── plan.md
└── spec.md
```

### Source Code (repository root)

```text
src/retail_lakehouse/
├── __init__.py
├── __main__.py
└── generate.py

docs/
├── data_sources.md
└── engineering_standards.md

data/
└── .gitkeep
```

**Structure Decision**: Single python package under `src/` with a Typer-based CLI.

## Implementation Notes

- Default output location: `data/landing/`
- Daily partitioning: `dt=YYYY-MM-DD/` folders for fact-like datasets
- Safety: customer dataset will not include direct identifiers (email/phone/full address)


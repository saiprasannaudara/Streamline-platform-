# Retail Lakehouse on Azure Databricks (Portfolio Project)

This repository is a **portfolio-grade data engineering project** demonstrating an end-to-end, production-minded lakehouse implementation using:

- **Azure** (cloud storage + secrets + automation)
- **Databricks** (PySpark + Spark SQL, Delta Lake, Workflows)
- **Medallion architecture** (Bronze → Silver → Gold)
- **Data quality gates**, **idempotent runs**, and **operability** (run logs, replay)

**Important**: This project uses **synthetic data only** (generated locally) and does **not** use M&S internal/proprietary data.

## End product

By the end, you will have:

- A repeatable workflow that ingests synthetic retail datasets into Bronze, transforms into Silver, and publishes Gold marts/KPIs.
- A small but real **data engineering framework**: standards, naming conventions, data contracts, quality checks.
- Automation scaffolding (IaC + CI) and operational documentation (ADRs + runbooks).

## Quickstart (local)

Generate synthetic “daily drop” files (CSV + JSON) into `data/landing/`:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
python -m retail_lakehouse.generate --days 7
```

Output will be created under:

- `data/landing/orders/`
- `data/landing/customers/`
- `data/landing/products/`
- `data/landing/stores/`
- `data/landing/inventory/`
- `data/landing/fulfilment_events/`

## Repository structure (high level)

- `docs/`: standards, architecture, runbooks, ADRs
- `src/retail_lakehouse/`: reusable Python modules
- `pipelines/`: Databricks notebooks / jobs (added later)
- `sql/`: reusable SQL (added later)
- `infra/`: IaC for Azure resources (added later)
- `data/`: local synthetic datasets (generated; safe to delete)


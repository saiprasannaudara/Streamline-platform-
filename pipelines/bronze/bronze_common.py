from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class BronzeRunContext:
    dt: str
    landing_base_path: str
    bronze_base_path: str
    load_id: str
    ingestion_ts_utc: str


def new_run_context(dt: str, landing_base_path: str, bronze_base_path: str) -> BronzeRunContext:
    load_id = str(uuid.uuid4())
    ingestion_ts_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return BronzeRunContext(
        dt=dt,
        landing_base_path=landing_base_path.rstrip("/"),
        bronze_base_path=bronze_base_path.rstrip("/"),
        load_id=load_id,
        ingestion_ts_utc=ingestion_ts_utc,
    )


def path_join(base: str, *parts: str) -> str:
    return "/".join([base.rstrip("/"), *[p.strip("/") for p in parts]])


def dt_partition_path(base: str, dataset: str, dt: str) -> str:
    return path_join(base, dataset, f"dt={dt}")


def bronze_table_path(bronze_base_path: str, table_name: str) -> str:
    return path_join(bronze_base_path, table_name)


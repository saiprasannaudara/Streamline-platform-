from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


@dataclass(frozen=True)
class SilverRunContext:
    dt: str
    silver_base_path: str
    load_id: str
    transform_ts_utc: str


def new_run_context(dt: str, silver_base_path: str) -> SilverRunContext:
    load_id = str(uuid.uuid4())
    transform_ts_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return SilverRunContext(
        dt=dt,
        silver_base_path=silver_base_path.rstrip("/"),
        load_id=load_id,
        transform_ts_utc=transform_ts_utc,
    )


def path_join(base: str, *parts: str) -> str:
    return "/".join([base.rstrip("/"), *[p.strip("/") for p in parts]])


def silver_table_path(silver_base_path: str, table_name: str) -> str:
    return path_join(silver_base_path, table_name)


def read_bronze_table(spark: SparkSession, table_fqn: str, *, dt: str) -> DataFrame:
    # Bronze tables are registered in Unity Catalog as retail_lakehouse.bronze.*
    # Use Column API (not SQL string) — Spark Connect resolves this more reliably than .where("dt = ...").
    return spark.table(table_fqn).filter(F.col("dt") == F.lit(dt))


def write_delta_overwrite_dt(df: DataFrame, *, out_path: str, dt: str) -> None:
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("replaceWhere", f"dt = '{dt}'")
        .partitionBy("dt")
        .save(out_path)
    )


from __future__ import annotations

import argparse

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from pipelines.silver.silver_common import (
    new_run_context,
    read_bronze_table,
    silver_table_path,
    write_delta_overwrite_dt,
)


BRZ_INVENTORY = "retail_lakehouse.bronze.brz_retail_inventory_snapshot"


def transform_inventory(spark: SparkSession, *, dt: str, silver_base_path: str) -> None:
    ctx = new_run_context(dt=dt, silver_base_path=silver_base_path)

    inv_brz = read_bronze_table(spark, BRZ_INVENTORY, dt=ctx.dt)
    inv = (
        inv_brz.withColumn("on_hand_qty", F.col("on_hand_qty").cast("int"))
        .withColumn("snapshot_date", F.to_date("snapshot_date"))
        .select(
            "dt",
            "snapshot_date",
            "store_id",
            "product_id",
            "on_hand_qty",
            "load_id",
            "ingestion_ts",
            "source_path",
        )
    )

    inv_out = silver_table_path(ctx.silver_base_path, "slv_retail_inventory_snapshot")
    write_delta_overwrite_dt(inv, out_path=inv_out, dt=ctx.dt)


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dt", required=True)
    p.add_argument("--silver-base-path", required=True)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    spark = SparkSession.builder.getOrCreate()
    transform_inventory(spark, dt=args.dt, silver_base_path=args.silver_base_path)


if __name__ == "__main__":
    main()


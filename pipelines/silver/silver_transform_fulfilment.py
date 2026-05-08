from __future__ import annotations

import argparse

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from pipelines.silver.silver_common import (
    new_run_context,
    read_bronze_table,
    silver_table_path,
    write_delta_overwrite_dt,
)


BRZ_FULFIL = "retail_lakehouse.bronze.brz_retail_fulfilment_events"


def _dedupe_latest(df, key_cols: list[str]):
    w = Window.partitionBy(*key_cols).orderBy(F.col("ingestion_ts").desc())
    return df.withColumn("_rn", F.row_number().over(w)).where(F.col("_rn") == 1).drop("_rn")


def transform_fulfilment(spark: SparkSession, *, dt: str, silver_base_path: str) -> None:
    ctx = new_run_context(dt=dt, silver_base_path=silver_base_path)

    fe_brz = read_bronze_table(spark, BRZ_FULFIL, dt=ctx.dt)
    fe = _dedupe_latest(fe_brz, ["dt", "order_id"])

    fe = (
        fe.withColumn("picked_ts", F.to_timestamp("picked_ts"))
        .withColumn("packed_ts", F.to_timestamp("packed_ts"))
        .withColumn("shipped_ts", F.to_timestamp("shipped_ts"))
        .withColumn("delivered_ts", F.to_timestamp("delivered_ts"))
        .withColumn("delivered_on_time_flag", F.col("delivered_on_time_flag").cast("boolean"))
        .withColumn("delivery_minutes", (F.col("delivered_ts").cast("long") - F.col("shipped_ts").cast("long")) / 60.0)
        .select(
            "dt",
            "order_id",
            "picked_ts",
            "packed_ts",
            "shipped_ts",
            "delivered_ts",
            "delivered_on_time_flag",
            "delivery_minutes",
            "load_id",
            "ingestion_ts",
            "source_path",
        )
    )

    fe_out = silver_table_path(ctx.silver_base_path, "slv_retail_fulfilment_events")
    write_delta_overwrite_dt(fe, out_path=fe_out, dt=ctx.dt)


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dt", required=True)
    p.add_argument("--silver-base-path", required=True)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    spark = SparkSession.builder.getOrCreate()
    transform_fulfilment(spark, dt=args.dt, silver_base_path=args.silver_base_path)


if __name__ == "__main__":
    main()


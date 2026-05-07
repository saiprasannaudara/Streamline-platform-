from __future__ import annotations

import argparse

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from pipelines.bronze.bronze_common import (
    bronze_table_path,
    dt_partition_path,
    new_run_context,
)


def _read_jsonl(spark: SparkSession, path: str):
    return spark.read.format("json").load(path)


def _with_ingestion_metadata(df, *, dt: str, load_id: str, ingestion_ts: str, source_path: str):
    return (
        df.withColumn("dt", F.lit(dt))
        .withColumn("load_id", F.lit(load_id))
        .withColumn("ingestion_ts", F.to_timestamp(F.lit(ingestion_ts)))
        .withColumn("source_path", F.lit(source_path))
    )


def ingest_orders(spark: SparkSession, *, dt: str, landing_base_path: str, bronze_base_path: str) -> None:
    ctx = new_run_context(dt=dt, landing_base_path=landing_base_path, bronze_base_path=bronze_base_path)

    orders_path = dt_partition_path(ctx.landing_base_path, "orders", ctx.dt)
    orders_src = f"{orders_path}/orders.jsonl"
    lines_src = f"{orders_path}/order_lines.jsonl"

    orders_df = _with_ingestion_metadata(
        _read_jsonl(spark, orders_src),
        dt=ctx.dt,
        load_id=ctx.load_id,
        ingestion_ts=ctx.ingestion_ts_utc,
        source_path=orders_src,
    )
    lines_df = _with_ingestion_metadata(
        _read_jsonl(spark, lines_src),
        dt=ctx.dt,
        load_id=ctx.load_id,
        ingestion_ts=ctx.ingestion_ts_utc,
        source_path=lines_src,
    )

    orders_out = bronze_table_path(ctx.bronze_base_path, "brz_retail_orders")
    lines_out = bronze_table_path(ctx.bronze_base_path, "brz_retail_order_lines")

    (
        orders_df.write.format("delta")
        .mode("overwrite")
        .option("replaceWhere", f"dt = '{ctx.dt}'")
        .partitionBy("dt")
        .save(orders_out)
    )
    (
        lines_df.write.format("delta")
        .mode("overwrite")
        .option("replaceWhere", f"dt = '{ctx.dt}'")
        .partitionBy("dt")
        .save(lines_out)
    )


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dt", required=True)
    p.add_argument("--landing-base-path", required=True)
    p.add_argument("--bronze-base-path", required=True)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    spark = SparkSession.builder.getOrCreate()
    ingest_orders(
        spark,
        dt=args.dt,
        landing_base_path=args.landing_base_path,
        bronze_base_path=args.bronze_base_path,
    )


if __name__ == "__main__":
    main()


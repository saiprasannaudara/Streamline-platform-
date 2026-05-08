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


BRZ_ORDERS = "retail_lakehouse.bronze.brz_retail_orders"
BRZ_ORDER_LINES = "retail_lakehouse.bronze.brz_retail_order_lines"


def _dedupe_latest(df, key_cols: list[str]):
    w = Window.partitionBy(*key_cols).orderBy(F.col("ingestion_ts").desc())
    return df.withColumn("_rn", F.row_number().over(w)).where(F.col("_rn") == 1).drop("_rn")


def transform_orders(spark: SparkSession, *, dt: str, silver_base_path: str) -> None:
    ctx = new_run_context(dt=dt, silver_base_path=silver_base_path)

    orders_brz = read_bronze_table(spark, BRZ_ORDERS, dt=ctx.dt)
    lines_brz = read_bronze_table(spark, BRZ_ORDER_LINES, dt=ctx.dt)

    orders = (
        _dedupe_latest(orders_brz, ["dt", "order_id"])
        .withColumn("order_ts", F.to_timestamp("order_ts"))
        .withColumn("promised_delivery_ts", F.to_timestamp("promised_delivery_ts"))
        .select(
            "dt",
            "order_id",
            "order_ts",
            "channel",
            "store_id",
            "customer_id",
            "currency",
            "promised_delivery_ts",
            # operational metadata carried through (useful for debugging)
            "load_id",
            "ingestion_ts",
            "source_path",
        )
    )

    # Filter orphan lines: only keep lines for orders present in the same dt
    lines = (
        lines_brz.withColumn("line_number", F.col("line_number").cast("int"))
        .withColumn("quantity", F.col("quantity").cast("int"))
        .join(orders.select("dt", "order_id"), on=["dt", "order_id"], how="inner")
        .select(
            "dt",
            "order_id",
            "line_number",
            "product_id",
            "quantity",
            "load_id",
            "ingestion_ts",
            "source_path",
        )
    )

    orders_out = silver_table_path(ctx.silver_base_path, "slv_retail_orders")
    lines_out = silver_table_path(ctx.silver_base_path, "slv_retail_order_lines")

    write_delta_overwrite_dt(orders, out_path=orders_out, dt=ctx.dt)
    write_delta_overwrite_dt(lines, out_path=lines_out, dt=ctx.dt)


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dt", required=True)
    p.add_argument("--silver-base-path", required=True)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    spark = SparkSession.builder.getOrCreate()
    transform_orders(spark, dt=args.dt, silver_base_path=args.silver_base_path)


if __name__ == "__main__":
    main()


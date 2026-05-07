from __future__ import annotations

import csv
import json
import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import typer
from dateutil.parser import isoparse
from faker import Faker

app = typer.Typer(add_completion=False, help="Generate synthetic retail datasets.")


@dataclass(frozen=True)
class GeneratorConfig:
    seed: int
    start_date: date
    days: int
    out_dir: Path

    n_stores: int = 25
    n_products: int = 500
    n_customers: int = 20_000

    avg_orders_per_day: int = 6_000
    max_lines_per_order: int = 8


def _rng(seed: int) -> random.Random:
    r = random.Random()
    r.seed(seed)
    return r


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _date_range(start: date, days: int) -> Iterable[date]:
    for i in range(days):
        yield start + timedelta(days=i)


def _iso_utc(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_csv(path: Path, rows: Iterable[dict], fieldnames: list[str]) -> None:
    _ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    _ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _stable_id(prefix: str, n: int) -> str:
    return f"{prefix}{n:07d}"


def generate_stores(cfg: GeneratorConfig) -> list[dict]:
    fake = Faker("en_GB")
    Faker.seed(cfg.seed)
    rows: list[dict] = []
    for i in range(1, cfg.n_stores + 1):
        rows.append(
            {
                "store_id": _stable_id("S", i),
                "store_name": f"{fake.city()} Store",
                "region": random.choice(["North", "Midlands", "South", "Scotland", "Wales"]),
                "store_type": random.choice(["Superstore", "Foodhall", "Convenience"]),
                "opened_date": fake.date_between(start_date="-20y", end_date="-30d").isoformat(),
            }
        )
    return rows


def generate_products(cfg: GeneratorConfig, r: random.Random) -> list[dict]:
    fake = Faker("en_GB")
    Faker.seed(cfg.seed + 1)
    categories = [
        "Fresh",
        "Frozen",
        "Ambient",
        "Household",
        "Beauty",
        "Clothing",
        "Home",
    ]
    rows: list[dict] = []
    for i in range(1, cfg.n_products + 1):
        base_price = round(r.uniform(1.0, 80.0), 2)
        rows.append(
            {
                "product_id": _stable_id("P", i),
                "product_name": fake.catch_phrase(),
                "category": r.choice(categories),
                "unit_price_gbp": base_price,
                "unit_cost_gbp": round(base_price * r.uniform(0.45, 0.8), 2),
                "active_flag": True,
            }
        )
    return rows


def generate_customers(cfg: GeneratorConfig, r: random.Random) -> list[dict]:
    fake = Faker("en_GB")
    Faker.seed(cfg.seed + 2)
    rows: list[dict] = []
    for i in range(1, cfg.n_customers + 1):
        # synthetic and non-identifying: no real emails/phones are required for this portfolio
        rows.append(
            {
                "customer_id": _stable_id("C", i),
                "loyalty_tier": r.choices(["Bronze", "Silver", "Gold"], weights=[70, 25, 5])[0],
                "signup_date": fake.date_between(start_date="-5y", end_date="today").isoformat(),
                "home_region": r.choice(["North", "Midlands", "South", "Scotland", "Wales"]),
            }
        )
    return rows


def generate_orders_for_day(
    cfg: GeneratorConfig,
    r: random.Random,
    day: date,
    store_ids: list[str],
    product_ids: list[str],
    customer_ids: list[str],
) -> tuple[list[dict], list[dict]]:
    fake = Faker("en_GB")
    Faker.seed(cfg.seed + int(day.strftime("%Y%m%d")))

    n_orders = max(1, int(r.gauss(cfg.avg_orders_per_day, cfg.avg_orders_per_day * 0.15)))
    orders: list[dict] = []
    order_lines: list[dict] = []

    for i in range(1, n_orders + 1):
        order_id = f"O{day.strftime('%Y%m%d')}{i:06d}"
        channel = r.choices(["store", "online"], weights=[55, 45])[0]
        store_id = r.choice(store_ids) if channel == "store" else r.choice(store_ids)
        customer_id = r.choice(customer_ids)

        created_ts = datetime(day.year, day.month, day.day, r.randrange(0, 24), r.randrange(0, 60), tzinfo=timezone.utc)
        promised_days = r.choices([0, 1, 2, 3], weights=[40, 35, 20, 5])[0]
        promised_ts = created_ts + timedelta(days=promised_days, hours=r.randrange(0, 6))

        orders.append(
            {
                "order_id": order_id,
                "order_ts": _iso_utc(created_ts),
                "channel": channel,
                "store_id": store_id,
                "customer_id": customer_id,
                "currency": "GBP",
                "promised_delivery_ts": _iso_utc(promised_ts),
            }
        )

        n_lines = r.randint(1, cfg.max_lines_per_order)
        for ln in range(1, n_lines + 1):
            product_id = r.choice(product_ids)
            qty = r.randint(1, 5)
            order_lines.append(
                {
                    "order_id": order_id,
                    "line_number": ln,
                    "product_id": product_id,
                    "quantity": qty,
                }
            )

    return orders, order_lines


def generate_inventory_snapshot_for_day(
    cfg: GeneratorConfig, r: random.Random, day: date, store_ids: list[str], product_ids: list[str]
) -> list[dict]:
    rows: list[dict] = []
    # Sample a subset to keep files manageable
    products_sample = r.sample(product_ids, k=min(len(product_ids), 250))
    for store_id in store_ids:
        for product_id in products_sample:
            on_hand = max(0, int(r.gauss(40, 25)))
            rows.append(
                {
                    "snapshot_date": day.isoformat(),
                    "store_id": store_id,
                    "product_id": product_id,
                    "on_hand_qty": on_hand,
                }
            )
    return rows


def generate_fulfilment_events_for_day(
    cfg: GeneratorConfig, r: random.Random, day: date, orders: list[dict]
) -> list[dict]:
    rows: list[dict] = []
    for o in orders:
        created_ts = isoparse(o["order_ts"])
        promised_ts = isoparse(o["promised_delivery_ts"])

        picked_ts = created_ts + timedelta(hours=r.uniform(0.5, 10.0))
        packed_ts = picked_ts + timedelta(hours=r.uniform(0.2, 3.0))
        shipped_ts = packed_ts + timedelta(hours=r.uniform(0.3, 8.0))
        delivered_ts = shipped_ts + timedelta(hours=r.uniform(2.0, 48.0))

        # Occasionally late
        if r.random() < 0.08:
            delivered_ts = promised_ts + timedelta(hours=r.uniform(1.0, 30.0))

        rows.append(
            {
                "order_id": o["order_id"],
                "picked_ts": _iso_utc(picked_ts),
                "packed_ts": _iso_utc(packed_ts),
                "shipped_ts": _iso_utc(shipped_ts),
                "delivered_ts": _iso_utc(delivered_ts),
                "delivered_on_time_flag": delivered_ts <= promised_ts,
            }
        )
    return rows


def write_static_dimensions(cfg: GeneratorConfig) -> None:
    r = _rng(cfg.seed)
    stores = generate_stores(cfg)
    products = generate_products(cfg, r)
    customers = generate_customers(cfg, r)

    _write_csv(
        cfg.out_dir / "landing" / "stores" / "stores.csv",
        stores,
        ["store_id", "store_name", "region", "store_type", "opened_date"],
    )
    _write_csv(
        cfg.out_dir / "landing" / "products" / "products.csv",
        products,
        ["product_id", "product_name", "category", "unit_price_gbp", "unit_cost_gbp", "active_flag"],
    )
    _write_csv(
        cfg.out_dir / "landing" / "customers" / "customers.csv",
        customers,
        ["customer_id", "loyalty_tier", "signup_date", "home_region"],
    )


def write_daily_facts(cfg: GeneratorConfig) -> None:
    r = _rng(cfg.seed)
    store_ids = [_stable_id("S", i) for i in range(1, cfg.n_stores + 1)]
    product_ids = [_stable_id("P", i) for i in range(1, cfg.n_products + 1)]
    customer_ids = [_stable_id("C", i) for i in range(1, cfg.n_customers + 1)]

    for d in _date_range(cfg.start_date, cfg.days):
        orders, order_lines = generate_orders_for_day(cfg, r, d, store_ids, product_ids, customer_ids)
        inventory = generate_inventory_snapshot_for_day(cfg, r, d, store_ids, product_ids)
        fulfilment_events = generate_fulfilment_events_for_day(cfg, r, d, orders)

        day_dir = cfg.out_dir / "landing" / "orders" / f"dt={d.isoformat()}"
        _write_jsonl(day_dir / "orders.jsonl", orders)
        _write_jsonl(day_dir / "order_lines.jsonl", order_lines)

        inv_dir = cfg.out_dir / "landing" / "inventory" / f"dt={d.isoformat()}"
        _write_jsonl(inv_dir / "inventory_snapshot.jsonl", inventory)

        fe_dir = cfg.out_dir / "landing" / "fulfilment_events" / f"dt={d.isoformat()}"
        _write_jsonl(fe_dir / "fulfilment_events.jsonl", fulfilment_events)


@app.command()
def main(
    days: int = typer.Option(7, help="Number of days to generate."),
    start_date: str = typer.Option("2026-01-01", help="Start date (YYYY-MM-DD)."),
    out_dir: Path = typer.Option(Path("data"), help="Output directory."),
    seed: int = typer.Option(42, help="Random seed for reproducibility."),
) -> None:
    """
    Generate synthetic retail datasets as local files suitable for Bronze ingestion.
    """
    if days < 1:
        raise typer.BadParameter("--days must be >= 1")

    cfg = GeneratorConfig(seed=seed, start_date=date.fromisoformat(start_date), days=days, out_dir=out_dir)
    write_static_dimensions(cfg)
    write_daily_facts(cfg)
    typer.echo(f"Generated datasets under: {cfg.out_dir.resolve()}")


if __name__ == "__main__":
    app()


"""Backward-compatible module path (British spelling filename).

Prefer importing from ``pipelines.silver.silver_transform_fulfillment``.
"""

from pipelines.silver.silver_transform_fulfillment import main, transform_fulfilment

__all__ = ["transform_fulfilment", "main"]

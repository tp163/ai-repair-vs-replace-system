"""Dataset access for the Specification Retrieval and Market Research agents.

Supports JSON (list of phone objects) and CSV (same column names) so you can
swap in your own Sri Lankan market dataset without changing code.

Expected schema (see data/phones_placeholder.json):
    id, brand, model, variant, release_year, price_lkr,
    chipset_tier (1-10), ram_gb, storage_gb, display_size_in,
    display_type, refresh_rate_hz, camera_mp, battery_mah,
    has_5g, os, warranty_months

Only ``id``, ``brand``, ``model`` and ``price_lkr`` are strictly required;
every other field makes retrieval and scoring smarter but has a safe default.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from . import config

_NUMERIC_FIELDS = {
    "release_year", "price_lkr", "chipset_tier", "ram_gb", "storage_gb",
    "display_size_in", "refresh_rate_hz", "camera_mp", "battery_mah",
    "warranty_months",
}


def _coerce(row: dict) -> dict:
    out = {}
    for k, v in row.items():
        k = k.strip()
        if k in _NUMERIC_FIELDS and v not in (None, ""):
            try:
                v = int(float(v))
            except (TypeError, ValueError):
                pass
        if isinstance(v, str):
            v = v.strip()
        out[k] = v
    return out


def load_phones(path: str | None = None) -> list[dict]:
    """Load the phone dataset from JSON or CSV."""
    path = Path(path or config.DATA_PATH)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {path}. Set PHONE_DATA_PATH or place your "
            f"file at the default location."
        )
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as f:
            return [_coerce(r) for r in csv.DictReader(f)]
    with path.open(encoding="utf-8") as f:
        return [_coerce(r) for r in json.load(f)]


def load_repair_costs(path: str | None = None) -> list[dict]:
    """Load optional sourced repair-cost records (JSON or CSV)."""
    path = Path(path or config.REPAIR_COST_DATA_PATH)
    if not path.exists():
        return []
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as f:
            return [_coerce(r) for r in csv.DictReader(f)]
    with path.open(encoding="utf-8") as f:
        return [_coerce(r) for r in json.load(f)]


def filter_candidates(phones: list[dict], requirements: dict,
                      max_candidates: int) -> list[dict]:
    """Specification Retrieval: narrow the dataset to a candidate pool.

    Filters on hard constraints first (budget with tolerance, brand, OS, 5G),
    then ranks by a rough spec score so the best-matching pool is kept.
    """
    budget = requirements.get("budget_lkr")
    tol = config.PRICE_OVER_BUDGET_TOLERANCE
    brands = {b.lower() for b in requirements.get("preferred_brands", [])}
    need_5g = requirements.get("needs_5g", False)

    pool = []
    for p in phones:
        if budget and isinstance(p.get("price_lkr"), (int, float)) \
                and p["price_lkr"] > budget * (1 + tol):
            continue
        if brands and str(p.get("brand", "")).lower() not in brands:
            continue
        if need_5g and not p.get("has_5g"):
            continue
        pool.append(p)

    def rough_score(p: dict) -> float:
        return (
            float(p.get("chipset_tier", 5)) * 2.0
            + float(p.get("ram_gb", 4)) * 1.5
            + float(p.get("camera_mp", 12)) / 20.0
            + (1.0 if p.get("has_5g") else 0.0)
        )

    pool.sort(key=rough_score, reverse=True)
    return pool[:max_candidates]

"""Self-repair resource lookup (Person A, proposal section 5.2).

Reads a curated file of links that were opened and checked by hand
(data/repair_resources.json). The agent never builds or guesses URLs: if a
link is not in the file it cannot be shown.

    find_resources("Samsung", "Galaxy A51", "cracked_screen")

returns model-specific entries first, then brand-level entries. Set
``escalated=True`` (a safety stop applies) to drop DIY teardown guides.
Override the file location with the REPAIR_RESOURCES_PATH environment variable.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "repair_resources.json"

_BRAND_ALIASES = {"redmi": "xiaomi", "poco": "xiaomi", "mi": "xiaomi", "iphone": "apple", "pixel": "google"}
_TYPES = {"support", "service", "info", "guide"}
_FAULTS = {"cracked_screen", "battery", "charging", "overheating", "liquid_damage", "performance", "unclear"}
_REQUIRED = ("id", "brand", "faults", "type", "title", "url", "source", "verified_at")


def _norm(text: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(text or "").casefold())


def _brand_key(brand: object) -> str:
    key = _norm(brand)
    return _BRAND_ALIASES.get(key, key)


def _model_key(brand: object, model: object) -> str:
    """Normalised model with a leading brand removed ("Samsung Galaxy A51" -> "galaxya51")."""
    b, m = _norm(brand), _norm(model)
    return m[len(b):] if b and m.startswith(b) else m


def _valid(entry: dict) -> bool:
    if not isinstance(entry, dict) or any(not entry.get(k) for k in _REQUIRED):
        return False
    if entry["type"] not in _TYPES:
        return False
    if not str(entry["url"]).startswith(("https://", "http://")):
        return False
    faults = entry["faults"]
    return isinstance(faults, list) and bool(faults) and all(f in _FAULTS for f in faults)


def load_resources(path: str | os.PathLike | None = None) -> list[dict]:
    """Load valid entries. Missing file or bad JSON returns []; bad entries are skipped."""
    path = Path(path or os.environ.get("REPAIR_RESOURCES_PATH") or DEFAULT_PATH)
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    entries = data.get("entries", []) if isinstance(data, dict) else data
    return [e for e in entries if _valid(e)]


def find_resources(brand: str, model: str, fault: str, escalated: bool = False,
                   path: str | os.PathLike | None = None) -> list[dict]:
    """Return resources for this phone and fault, model-specific first."""
    wanted_brand, wanted_model = _brand_key(brand), _model_key(brand, model)
    if not wanted_brand:
        return []
    out = []
    for entry in load_resources(path):
        if _brand_key(entry["brand"]) != wanted_brand or fault not in entry["faults"]:
            continue
        if escalated and entry["type"] == "guide":
            continue
        entry_model = entry.get("model")
        if entry_model:
            if _model_key(entry["brand"], entry_model) != wanted_model:
                continue
            scope = "model"
        else:
            scope = "brand"
        out.append({
            "title": entry["title"], "url": entry["url"], "source": entry["source"],
            "type": entry["type"], "scope": scope, "difficulty": entry.get("difficulty", ""),
            "requires_opening_device": bool(entry.get("requires_opening_device")),
            "uses_heat": bool(entry.get("uses_heat")),
            "requires_soldering": bool(entry.get("requires_soldering")),
            "note": entry.get("note", ""), "verified_at": entry["verified_at"],
        })
    out.sort(key=lambda r: 0 if r["scope"] == "model" else 1)
    return out
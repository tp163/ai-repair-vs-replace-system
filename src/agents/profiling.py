"""Agent 2 — Device Profiling Agent.

Assesses the old device's specifications, age, and condition so the
Comparison Agent can judge whether a replacement is actually an upgrade.
Estimates a residual (second-hand) value used later in repair-vs-replace
reasoning.
"""
from __future__ import annotations

from datetime import date

from .. import dataset
from ..state import AgentState

# Rough annual value retention by brand tier (illustrative, for demo).
_RETENTION = {"apple": 0.72, "samsung": 0.60, "google": 0.58,
              "xiaomi": 0.50, "poco": 0.50, "oneplus": 0.55}
_DEFAULT_RETENTION = 0.48

# Condition multipliers applied to residual value.
_CONDITION_FACTOR = {
    "excellent": 1.00, "good": 0.85, "fair": 0.65,
    "poor": 0.40, "faulty": 0.25,
}


def _estimate_residual(brand: str, year: int, price_lkr: float,
                       condition: str) -> float:
    age = max(0, date.today().year - int(year or date.today().year))
    retention = _RETENTION.get(brand.lower(), _DEFAULT_RETENTION)
    value = price_lkr * (retention ** age)
    return round(value * _CONDITION_FACTOR.get(condition, 0.65), -3)


def run(state: AgentState, llm) -> dict:
    old = state.get("old_device", {})
    brand = old.get("brand", "unknown")
    year = int(old.get("year") or date.today().year)
    original_price = float(old.get("original_price_lkr") or 0)
    condition = old.get("condition", "fair")
    fault = old.get("fault", "")

    residual = (_estimate_residual(brand, year, original_price, condition)
                if original_price else None)

    # Enrich a manually supplied identity with known catalogue specifications
    # when a brand/model match exists. Keep user-entered identity authoritative.
    known_specs = {}
    try:
        matches = [p for p in dataset.load_phones()
                   if str(p.get("brand", "")).casefold() == str(brand).casefold()
                   and str(p.get("model", "")).casefold() == str(old.get("model", "")).casefold()]
        selected_variant = old.get("variant")
        if selected_variant:
            variant_matches = [p for p in matches
                               if str(p.get("variant") or p.get("id", "")).casefold() == str(selected_variant).casefold()]
            matches = variant_matches or matches
        if matches:
            known_specs = matches[0]
    except (FileNotFoundError, ValueError):
        pass

    profile = {
        "brand": brand,
        "model": old.get("model", "unknown"),
        "age_years": max(0, date.today().year - year),
        "condition": condition,
        "variant": old.get("variant", ""),
        "profile_confirmed": bool(old.get("profile_confirmed", False)),
        "fault": fault,
        "estimated_residual_lkr": residual,
        **{key: known_specs[key] for key in (
            "chipset_tier", "ram_gb", "storage_gb", "display_size_in",
            "camera_mp", "battery_mah", "os", "has_5g") if key in known_specs},
        "assessment": (
            f"{brand} {old.get('model', '')} is ~{max(0, date.today().year - year)} "
            f"years old, condition '{condition}', fault: {fault or 'none reported'}."
        ),
    }

    trace = state.get("trace", []) + [{
        "agent": "DeviceProfilingAgent",
        "action": "profiled old device",
        "details": profile,
    }]
    return {"old_device_profile": profile, "trace": trace}

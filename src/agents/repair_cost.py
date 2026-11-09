"""Repair Cost Agent: return only sourced estimates present in the cost dataset."""
from __future__ import annotations

from .. import dataset
from ..state import AgentState

_BRAND_ALIASES = {
    "redmi": "xiaomi",
    "poco": "xiaomi",
    "mi": "xiaomi",
    "iphone": "apple",
    "pixel": "google",
}


def _canonical_brand(brand: str) -> str:
    b = str(brand or "").strip().casefold()
    return _BRAND_ALIASES.get(b, b)


def _normalize_model_name(brand: str, model: str) -> str:
    """Normalize model string by removing redundant brand prefix and extra spaces."""
    b = str(brand or "").strip().casefold()
    m = str(model or "").strip().casefold()
    if b and m.startswith(b + " "):
        m = m[len(b):].strip()
    for alias in ("redmi ", "poco ", "samsung ", "apple ", "google "):
        if m.startswith(alias):
            m = m[len(alias):].strip()
            break
    return m


def _is_out_of_stock(row: dict) -> bool:
    if row.get("in_stock") is False:
        return True
    if str(row.get("stock_status", "")).casefold() == "out_of_stock":
        return True
    if str(row.get("availability_status", "")).casefold() == "out_of_stock":
        return True
    return False


def run(state: AgentState, llm) -> dict:
    old = state.get("old_device", {})
    category = state.get("diagnosis", {}).get("fault_category", "unclear")
    try:
        records = dataset.load_repair_costs()
    except (FileNotFoundError, ValueError):
        records = []

    brand = _canonical_brand(str(old.get("brand", "")))
    raw_model = str(old.get("model", "")).strip()
    model = _normalize_model_name(brand, raw_model)

    if not model:
        matches = []
    else:
        model_matches = []
        for row in records:
            if str(row.get("fault_category", "")).casefold() != category.casefold():
                continue
            row_brand = _canonical_brand(str(row.get("brand", "")))
            if row_brand and brand and row_brand != brand:
                continue
            row_model = str(row.get("model", "")).strip().casefold() if row.get("model") else ""
            if row_model:
                row_model_norm = _normalize_model_name(row_brand, row_model)
                if row_model_norm == model:
                    model_matches.append(row)
        matches = model_matches

    unavailable_rows = [row for row in matches if _is_out_of_stock(row)]
    matches = [row for row in matches if not _is_out_of_stock(row)]

    estimate = None
    if matches:
        row = matches[0]
        try:
            low, high = float(row["min_lkr"]), float(row["max_lkr"])
            if low <= high and str(row.get("source_url", "")).startswith(("https://", "http://")):
                estimate = {
                    "min_lkr": low,
                    "max_lkr": high,
                    "source": row.get("source", "Repair-cost dataset"),
                    "source_url": row["source_url"],
                    "retrieved_at": row.get("retrieved_at"),
                    "status": "estimate",
                    "quotation_confirmed": False,
                    "verified": bool(row.get("verified", False)),
                    "pricing_type": row.get("pricing_type", "indicative_estimate"),
                    "part_quality": row.get("part_quality", ""),
                    "labor_included": row.get("labor_included", ""),
                    "warranty_duration": row.get("warranty_duration", ""),
                    "location": row.get("location", ""),
                    "taxes_and_diagnosis": row.get("taxes_and_diagnosis", ""),
                    "evidence_type": row.get("evidence_type", ""),
                    "evidence_status": row.get("evidence_status", ""),
                    "verification_evidence": row.get("verification_evidence", ""),
                    "fault_category": category,
                    "repair_type": row.get("repair_type", ""),
                    "currency": row.get("currency", "LKR"),
                    "verification_proof": row.get("verification_proof", ""),
                    "note": row.get("notes", ""),
                }
        except (KeyError, TypeError, ValueError):
            estimate = None

    unavailable_message = None
    if unavailable_rows:
        unavailable_message = (
            f"The linked {unavailable_rows[0].get('source', 'repairer')} catalog listing is out of stock, "
            "so there is no current price to use. Request a fresh local quote."
        )

    result = estimate or {
        "status": "unavailable",
        "min_lkr": None,
        "max_lkr": None,
        "message": unavailable_message or "No sourced repair-cost range is available for this model and issue yet. Request a local quote.",
        "quotation_confirmed": False,
    }
    if estimate:
        if result.get("verified"):
            action_desc = "matched a verified quotation"
        elif result.get("pricing_type") == "catalog_price":
            action_desc = "matched a published catalog price range"
        else:
            action_desc = "matched an unverified indicative inquiry range"
    else:
        action_desc = "no verifiable repair-cost record found"

    trace = state.get("trace", []) + [{
        "agent": "RepairCostAgent",
        "action": action_desc,
        "details": result,
    }]
    return {"repair_cost_estimate": result, "trace": trace}

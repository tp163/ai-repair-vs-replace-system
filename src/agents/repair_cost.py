"""Repair Cost Agent: return only sourced estimates present in the cost dataset."""
from __future__ import annotations

from .. import dataset
from ..state import AgentState


def run(state: AgentState, llm) -> dict:
    old = state.get("old_device", {})
    category = state.get("diagnosis", {}).get("fault_category", "unclear")
    try:
        records = dataset.load_repair_costs()
    except (FileNotFoundError, ValueError):
        records = []
    matches = [row for row in records
               if str(row.get("fault_category", "")).casefold() == category.casefold()
               and (not row.get("brand") or str(row.get("brand")).casefold() == str(old.get("brand", "")).casefold())
               and (not row.get("model") or str(row.get("model")).casefold() == str(old.get("model", "")).casefold())]
    estimate = None
    if matches:
        row = matches[0]
        try:
            low, high = float(row["min_lkr"]), float(row["max_lkr"])
            if low <= high and row.get("source_url"):
                estimate = {"min_lkr": low, "max_lkr": high,
                            "source": row.get("source", "Repair-cost dataset"),
                            "source_url": row["source_url"],
                            "retrieved_at": row.get("retrieved_at"),
                            "status": "estimate", "quotation_confirmed": False}
        except (KeyError, TypeError, ValueError):
            estimate = None
    result = estimate or {
        "status": "unavailable", "min_lkr": None, "max_lkr": None,
        "message": "No sourced repair-cost range is available for this model and issue yet. Request a local quote.",
        "quotation_confirmed": False,
    }
    trace = state.get("trace", []) + [{
        "agent": "RepairCostAgent",
        "action": "matched a sourced cost range" if estimate else "no verifiable repair-cost record found",
        "details": result,
    }]
    return {"repair_cost_estimate": result, "trace": trace}

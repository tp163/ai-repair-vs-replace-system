"""Repair-versus-replace Decision Agent using sourced costs and device value."""
from __future__ import annotations

from ..state import AgentState


def run(state: AgentState, llm) -> dict:
    cost = state.get("repair_cost_estimate", {})
    profile = state.get("old_device_profile", {})
    triage = state.get("troubleshooting", {})
    residual = profile.get("estimated_residual_lkr")
    category = state.get("diagnosis", {}).get("fault_category", "unclear")
    path, reason = "get_repair_quote", "A sourced repair range is not available, so compare a local quote with replacement options."
    if triage.get("professional_help_recommended"):
        path, reason = "professional_repair_assessment", "The issue may involve physical damage or a safety risk; have a qualified repairer inspect it."
    elif cost.get("status") == "estimate" and residual:
        midpoint = (float(cost["min_lkr"]) + float(cost["max_lkr"])) / 2
        ratio = midpoint / float(residual) if residual else None
        if ratio is not None and ratio < 0.4:
            path, reason = "repair_likely_worthwhile", "The sourced estimate is below 40% of the estimated current device value."
        elif ratio is not None and ratio > 0.6:
            path, reason = "replacement_worth_considering", "The sourced estimate is above 60% of the estimated current device value."
        else:
            path, reason = "compare_quote_and_replacements", "The estimate is in a middle range; compare the final quote with replacement options."
    result = {"recommended_path": path, "reason": reason,
              "cost_to_device_value_ratio_available": bool(cost.get("status") == "estimate" and residual),
              "fault_category": category,
              "device_value_lkr": residual}
    trace = state.get("trace", []) + [{
        "agent": "RepairDecisionAgent", "action": f"recommended path: {path}", "details": result,
    }]
    return {"decision": result, "trace": trace}

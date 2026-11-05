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

    spec_answers = state.get("spec_answers", [])
    hardware_notes = []
    if spec_answers:
        combined_spec_text = " ".join(a.get("answer", "").lower() for a in spec_answers)
        if "modular" in combined_spec_text or "sub-pba" in combined_spec_text or "daughterboard" in combined_spec_text:
            hardware_notes.append("Verified OEM documentation confirms a modular sub-board design, supporting straightforward component-level port/board repair.")
        elif "fused" in combined_spec_text or "digitizer" in combined_spec_text:
            hardware_notes.append("Verified datasheets note a fused display assembly; ensure repair quotations specify whether a complete frame assembly or bare panel is quoted.")
        elif "pull-tab" in combined_spec_text or "pull tabs" in combined_spec_text or "pull-pouch" in combined_spec_text:
            hardware_notes.append("Verified OEM documentation notes stretch-release battery pull-tabs, supporting standard adhesive replacement.")

    if hardware_notes:
        reason = f"{reason} {' '.join(hardware_notes)}"

    result = {"recommended_path": path, "reason": reason,
              "cost_to_device_value_ratio_available": bool(cost.get("status") == "estimate" and residual),
              "fault_category": category,
              "device_value_lkr": residual}
    trace = state.get("trace", []) + [{
        "agent": "RepairDecisionAgent", "action": f"recommended path: {path}", "details": result,
    }]
    return {"decision": result, "trace": trace}

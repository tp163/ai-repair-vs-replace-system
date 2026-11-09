"""Repair-versus-replace Decision Agent using sourced costs and device value."""
from __future__ import annotations

from ..state import AgentState


def run(state: AgentState, llm) -> dict:
    cost = state.get("repair_cost_estimate", {})
    profile = state.get("old_device_profile", {})
    triage = state.get("troubleshooting", {})
    residual = profile.get("estimated_residual_lkr")
    category = state.get("diagnosis", {}).get("fault_category", "unclear")

    ratio = None
    midpoint = None

    if triage.get("escalate_to_technician"):
        path, reason = "professional_repair_assessment", "The issue may involve physical damage or a safety risk; have a qualified repairer inspect it."
    elif cost.get("status") == "estimate" and residual:
        midpoint = (float(cost["min_lkr"]) + float(cost["max_lkr"])) / 2
        ratio = midpoint / float(residual)
        is_verified = bool(cost.get("verified", False))

        if is_verified:
            # Confident recommendations are only permitted on verified pricing
            if ratio < 0.4:
                path = "repair_likely_worthwhile"
                reason = (
                    f"The verified repair estimate (LKR {midpoint:,.0f}) is below 40% of the estimated "
                    f"current device value ({ratio*100:.0f}% of LKR {residual:,.0f}). Repairing is financially sensible."
                )
            elif ratio > 0.6:
                path = "replacement_worth_considering"
                reason = (
                    f"The verified repair estimate (LKR {midpoint:,.0f}) is above 60% of the estimated "
                    f"current device value ({ratio*100:.0f}% of LKR {residual:,.0f}). Replacement is worth considering over repair."
                )
            else:
                path = "compare_quote_and_replacements"
                reason = (
                    f"The verified estimate is in a middle range ({ratio*100:.0f}% of device value "
                    f"LKR {residual:,.0f}); compare the final quote with replacement options."
                )
        else:
            # Unverified estimates: provide indicative ratio context but do NOT issue confident repair/replace verdicts
            path = "get_repair_quote"
            quality_info = f" ({cost.get('part_quality')})" if cost.get("part_quality") else ""
            reason = (
                f"An indicative repair range of LKR {cost['min_lkr']:,.0f} - {cost['max_lkr']:,.0f} "
                f"(~{ratio*100:.0f}% of estimated device value LKR {residual:,.0f}) is available{quality_info}, "
                f"but this pricing is an unverified indicative range. Request a binding local workshop quote before deciding."
            )
    elif triage.get("professional_help_recommended"):
        path, reason = "professional_repair_assessment", "The issue may involve physical damage or a safety risk; have a qualified repairer inspect it."
    else:
        path, reason = "get_repair_quote", "A sourced repair range is not available, so compare a local quote with replacement options."

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

    result = {
        "recommended_path": path,
        "reason": reason,
        "cost_to_device_value_ratio_available": bool(cost.get("status") == "estimate" and residual),
        "cost_to_device_value_ratio": round(ratio, 4) if ratio is not None else None,
        "repair_cost_midpoint_lkr": round(midpoint, 2) if midpoint is not None else None,
        "fault_category": category,
        "device_value_lkr": residual,
        "cost_verified": bool(cost.get("verified", False)),
    }
    trace = state.get("trace", []) + [{
        "agent": "RepairDecisionAgent", "action": f"recommended path: {path}", "details": result,
    }]
    return {"decision": result, "trace": trace}

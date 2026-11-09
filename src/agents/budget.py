"""Budget Agent: classify affordability without silently dropping alternatives."""
from __future__ import annotations

from .. import config
from ..state import AgentState


def run(state: AgentState, llm) -> dict:
    candidates = state.get("candidates", [])
    budget = state.get("requirements", {}).get("budget_lkr")
    cap = float(budget) * (1 + config.PRICE_OVER_BUDGET_TOLERANCE) if budget else None
    eligible, excluded = [], []
    for candidate in candidates:
        price = candidate.get("price_lkr")
        row = {**candidate, "within_budget": bool(budget and price is not None and float(price) <= float(budget))}
        row["within_tolerance"] = bool(cap is None or price is None or float(price) <= cap)
        (eligible if row["within_tolerance"] else excluded).append(row)
    trace = state.get("trace", []) + [{
        "agent": "BudgetAgent",
        "action": f"classified {len(eligible)} eligible and {len(excluded)} over-tolerance candidates",
        "details": {"budget_lkr": budget, "tolerance_percent": config.PRICE_OVER_BUDGET_TOLERANCE * 100,
                    "eligible_ids": [p.get("id") for p in eligible],
                    "over_tolerance_ids": [p.get("id") for p in excluded]},
    }]
    return {"budget_analysis": {"budget_lkr": budget, "eligible": eligible,
                                "excluded": excluded, "all_candidates": eligible + excluded},
            "trace": trace}

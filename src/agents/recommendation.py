"""Agent 6 — Recommendation Agent.

Selects the top-k candidates from the Comparison Agent's scored list and
packages each pick with its supporting evidence (scores, prices, upgrade
verdict relative to the old device). This agent only *selects*; the
Verification Agent checks the picks, and the Explanation Agent writes the
user-facing reasoning.
"""
from __future__ import annotations

from .. import config
from ..state import AgentState


def run(state: AgentState, llm) -> dict:
    comparisons = state.get("comparisons", [])
    old = state.get("old_device_profile", {})
    candidates = {str(p.get("id")): p for p in state.get("candidates", [])}
    market = state.get("market_info", {})
    budget = state.get("requirements", {}).get("budget_lkr")

    def package(c: dict) -> dict:
        verdict = "upgrade"
        if old.get("estimated_residual_lkr") and c["price_lkr"]:
            if c["price_lkr"] < old["estimated_residual_lkr"]:
                verdict = "cheaper_than_old_device_value"
        product = dict(candidates.get(str(c.get("id")), {}))
        product.update({key: value for key, value in
                        (market.get(str(c.get("id")), {}) or {}).items()
                        if key != "live_signals" and value is not None})
        return {
            **c,
            "verdict_vs_old": verdict,
            "product": product,
            "evidence": {
                "score_breakdown": c["dimensions"],
                "price_lkr": c["price_lkr"],
                "old_device_residual_lkr": old.get("estimated_residual_lkr"),
            },
        }

    top = comparisons[:config.TOP_K]
    affordable = [c for c in comparisons if budget and c.get("price_lkr") is not None
                  and c["price_lkr"] <= budget]
    similar = sorted(comparisons, key=lambda c: c.get("similarity_score", 0), reverse=True)
    old_tier = old.get("chipset_tier")
    improvements = [c for c in comparisons
                    if candidates.get(str(c.get("id")), {}).get("chipset_tier", 0) > (old_tier or 0)]
    if not old_tier:
        improvements = [c for c in comparisons if c.get("dimensions", {}).get("performance", 0) >= 0.6]

    category_sources = {
        "budget": ("Best within budget", affordable),
        "similar": ("Closest to your current phone", similar),
        "improvement": ("Performance upgrades", improvements),
        "alternatives": ("Other strong alternatives", top),
    }
    categories = {}
    unique = {}
    for key, (label, ranked) in category_sources.items():
        items = [package(c) for c in ranked[:config.TOP_K]]
        message = "No device in the current catalogue is within this budget." if key == "budget" and not items else ""
        categories[key] = {"label": label, "items": items, "message": message}
        for item in items:
            unique.setdefault(item["id"], item)
    picks = list(unique.values())

    trace = state.get("trace", []) + [{
        "agent": "RecommendationAgent",
        "action": f"created {len(categories)} recommendation categories",
        "details": {key: [p["name"] for p in value["items"]]
                    for key, value in categories.items()},
    }]
    return {"recommendations": picks, "recommendation_categories": categories, "trace": trace}

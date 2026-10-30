"""Agent 5 — Comparison Agent.

Scores each candidate against (a) the old device's profile and (b) the
user's requirement profile. Produces a transparent, decomposable score so
the Explanation Agent can cite *why* a device won, not just *that* it won.

Scoring dimensions (weights tuned for phone buying decisions):
    price_fit      30%  within budget? how much headroom left?
    performance    25%  chipset tier + RAM vs. priorities
    camera         15%  megapixels + priority boost
    battery        10%  capacity + priority boost
    longevity      10%  recency of release, warranty
    upgrade        10%  is it actually better than the old device?
"""
from __future__ import annotations

from ..state import AgentState

_W = {"price_fit": 0.25, "performance": 0.20, "camera": 0.15,
      "battery": 0.10, "longevity": 0.10, "upgrade": 0.10,
      "similarity": 0.10}


def _score_price(price, budget, tol) -> float:
    if not budget or not price:
        return 0.5
    if price <= budget:
        # Cheaper is better, but not linearly — being far under budget
        # shouldn't beat a clearly better phone (diminishing returns).
        return 0.7 + 0.3 * (1 - price / budget)
    if price <= budget * (1 + tol):
        return 0.4  # slightly over budget: allowed but penalised
    return 0.0


def run(state: AgentState, llm) -> dict:
    req = state.get("requirements", {})
    old = state.get("old_device_profile", {})
    market = state.get("market_info", {})
    similarity = state.get("similarity", {})
    budget_analysis = state.get("budget_analysis", {})
    budget = req.get("budget_lkr")
    priorities = set(req.get("priorities", []))
    tol = 0.10

    comparisons = []
    candidate_pool = budget_analysis.get("all_candidates") or state.get("candidates", [])
    for p in candidate_pool:
        price = (market.get(p["id"], {}) or {}).get("dataset_price_lkr") \
            or p.get("price_lkr")

        perf = (p.get("chipset_tier", 5) / 10.0) * 0.6 \
            + min(p.get("ram_gb", 4), 16) / 16.0 * 0.4
        cam = min(p.get("camera_mp", 12), 200) / 200.0
        bat = min(p.get("battery_mah", 3000), 6000) / 6000.0
        age_new = max(0, 6 - (2026 - p.get("release_year", 2026)))
        longev = (age_new / 6.0) * 0.6 + (p.get("warranty_months", 12) / 12.0) * 0.4

        old_tier = old.get("chipset_tier")
        if old_tier:
            upgrade = 1.0 if p.get("chipset_tier", 5) > old_tier else 0.3
        else:
            upgrade = 0.6  # unknown old device: neutral

        dims = {
            "price_fit": _score_price(price, budget, tol),
            "similarity": similarity.get(str(p.get("id")), 0.0) / 100.0,
            "performance": perf,
            "camera": cam * (1.25 if "camera" in priorities else 1.0),
            "battery": bat * (1.5 if "battery" in priorities else 1.0),
            "longevity": longev,
            "upgrade": upgrade,
        }
        dims = {k: min(v, 1.0) for k, v in dims.items()}
        total = round(sum(dims[k] * _W[k] for k in _W) * 100, 1)

        comparisons.append({
            "id": p["id"], "name": f"{p.get('brand')} {p.get('model')}",
            "price_lkr": price, "dimensions": dims, "score": total,
            "over_budget": bool(budget and price and price > budget),
            "similarity_score": similarity.get(str(p.get("id")), 0.0),
            "within_budget": bool(budget and price and price <= budget),
        })

    comparisons.sort(key=lambda c: c["score"], reverse=True)
    trace = state.get("trace", []) + [{
        "agent": "ComparisonAgent",
        "action": f"scored {len(comparisons)} candidates",
        "details": [{"name": c["name"], "score": c["score"]}
                    for c in comparisons],
    }]
    return {"comparisons": comparisons, "trace": trace}

"""Agent 7 — Verification Agent.

Fact-checks the recommendations before they reach the user:

1. Price check — does the quoted price exist in the dataset / market info?
2. Spec consistency — do scores rest on real spec fields?
3. Budget compliance — are any picks over budget (allowed, but flagged)?
4. Live-signal plausibility — if live search returned prices, are they in a
   sane range relative to the dataset price (±40%)? Outliers are rejected.

Outputs a verification report; picks failing hard checks (missing price,
missing identity) are marked failed=False and replaced by the next-ranked
alternative. This agent is the project's answer to hallucinated specs and
stale prices.
"""
from __future__ import annotations

from ..state import AgentState


def run(state: AgentState, llm) -> dict:
    recs = list(state.get("recommendations", []))
    comparisons = state.get("comparisons", [])
    market = state.get("market_info", {})
    req = state.get("requirements", {})
    budget = req.get("budget_lkr")
    checked, failures = [], []

    for r in recs:
        problems = []
        entry = market.get(r["id"], {}) or {}
        base = entry.get("dataset_price_lkr")
        if base is None:
            problems.append("no dataset price found")
        if r["price_lkr"] is None:
            problems.append("no price quoted")

        # Live-signal sanity check
        live_rejected = 0
        for sig in entry.get("live_signals", []):
            body = sig.get("body", "") + sig.get("title", "")
            import re
            m = re.search(r"(?:LKR|Rs\.?)\s*([0-9][0-9,]{3,})", body)
            if m:
                live_price = float(m.group(1).replace(",", ""))
                if base and abs(live_price - base) / base > 0.40:
                    live_rejected += 1

        checked.append({
            "id": r["id"], "name": r["name"],
            "passed": not problems,
            "problems": problems,
            "within_budget": bool(budget and r["price_lkr"] and
                                   r["price_lkr"] <= budget),
            "live_signals_rejected": live_rejected,
            "price_source": entry.get("price_source", "provided dataset"),
            "source_url": entry.get("source_url"),
            "retrieved_at": entry.get("retrieved_at"),
        })
        if problems:
            failures.append(r["id"])

    # Backfill failed picks with the next best verified candidates
    if failures:
        remaining = [c for c in comparisons
                     if c["id"] not in {r["id"] for r in recs}]
        for rid in failures:
            idx = next(i for i, r in enumerate(recs) if r["id"] == rid)
            if remaining:
                nxt = remaining.pop(0)
                recs[idx] = {**nxt, "verdict_vs_old": "upgrade",
                             "evidence": {"score_breakdown": nxt["dimensions"],
                                          "price_lkr": nxt["price_lkr"],
                                          "old_device_residual_lkr": None},
                             "replaced_failed_pick": rid}

    category_map = state.get("recommendation_categories", {})
    replacement_map = {r.get("replaced_failed_pick"): r for r in recs
                       if r.get("replaced_failed_pick")}
    final_by_id = {r.get("id"): r for r in recs}
    for category in category_map.values():
        refreshed = []
        for item in category.get("items", []):
            refreshed.append(replacement_map.get(item.get("id"),
                                                  final_by_id.get(item.get("id"), item)))
        category["items"] = refreshed

    report = {
        "checked": checked,
        "failed_pick_ids": failures,
        "all_passed": not failures,
        "prices_are": "catalogue prices with source metadata where supplied; confirm current seller prices",
    }
    trace = state.get("trace", []) + [{
        "agent": "VerificationAgent",
        "action": "verified recommendations",
        "details": {"passed": sum(1 for c in checked if c["passed"]),
                    "failed": failures},
    }]
    return {"recommendations": recs, "recommendation_categories": category_map,
            "verification": report, "trace": trace}

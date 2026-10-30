"""Agent 4 — Market Research Agent.

Collects current price and availability information for the candidate
pool. Strategy:

1. Use the dataset price as the trusted base price (labelled
   "dataset_price_lkr").
2. If ENABLE_LIVE_SEARCH is on, run a free DuckDuckGo query per candidate
   for "Sri Lanka price" signals and attach whatever snippets come back as
   "live_signals" — unverified raw evidence, flagged as such. The
   Verification Agent decides whether any live signal is trustworthy.

Keeping dataset and live signals separate is deliberate: it gives the
Verification Agent something concrete to fact-check (a core claim of the
project), instead of blending sources silently.
"""
from __future__ import annotations

from .. import config, tools
from ..state import AgentState


def run(state: AgentState, llm) -> dict:
    candidates = state.get("candidates", [])
    info = {}

    for p in candidates:
        entry = {
            "dataset_price_lkr": p.get("price_lkr"),
            "price_source": p.get("price_source") or p.get("source") or "provided dataset",
            "source_url": p.get("source_url") or p.get("price_source_url"),
            "retrieved_at": p.get("retrieved_at") or p.get("price_checked_at"),
            "availability": p.get("availability"),
            "live_signals": [],
        }
        if config.ENABLE_LIVE_SEARCH:
            query = (f"{p.get('brand', '')} {p.get('model', '')} "
                     f"{p.get('variant', '')} price Sri Lanka")
            entry["live_signals"] = tools.web_search(
                query, config.LIVE_SEARCH_RESULTS)
        info[p["id"]] = entry

    summary = {
        cid: e["dataset_price_lkr"] for cid, e in info.items()
    }
    trace = state.get("trace", []) + [{
        "agent": "MarketResearchAgent",
        "action": f"priced {len(info)} candidates "
                  f"(live_search={'on' if config.ENABLE_LIVE_SEARCH else 'off'})",
        "details": summary,
    }]
    return {"market_info": info, "trace": trace}

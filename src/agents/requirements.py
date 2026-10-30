"""Agent 1 — User Requirement Agent.

Turns the user's free-text needs plus explicit budget into a structured
requirement profile the downstream agents can reason over. Uses the LLM to
extract intents when available; falls back to keyword parsing in demo mode.
"""
from __future__ import annotations

import re

from ..state import AgentState

_KEYWORD_MAP = {
    "camera": ["camera", "photo", "selfie", "video", "vlog"],
    "gaming": ["game", "gaming", "pubg", "genshin", "heavy"],
    "battery": ["battery", "long lasting", "all day", "two days"],
    "performance": ["fast", "smooth", "performance", "speed", "lag"],
    "budget": ["cheap", "budget", "affordable", "value"],
    "compact": ["small", "compact", "light", "one hand"],
    "premium": ["premium", "flagship", "best", "top"],
}


def _keyword_profile(text: str) -> dict:
    t = text.lower()
    priorities = [p for p, kws in _KEYWORD_MAP.items() if any(k in t for k in kws)]
    return {
        "priorities": priorities or ["general_use"],
        "needs_5g": "5g" in t,
        "min_ram_gb": 8 if ("gaming" in priorities or "performance" in priorities) else 4,
        "notes": text,
    }


def run(state: AgentState, llm) -> dict:
    needs = state.get("user_needs") or ""
    budget = state.get("budget_lkr")
    fallback_used = not needs.strip()

    prompt = (
        "Extract a JSON requirement profile from this phone buyer request. "
        "Fields: priorities (list from camera/gaming/battery/performance/"
        "budget/compact/premium), needs_5g (bool), min_ram_gb (int), "
        "preferred_brands (list or []), notes.\nRequest: " + needs
    )
    if fallback_used:
        profile = _keyword_profile(needs)
    else:
        try:
            raw = llm.chat(
                "You extract structured requirements. Reply with JSON only.",
                prompt,
            )
            import json
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            profile = json.loads(m.group(0)) if m else _keyword_profile(needs)
        except Exception:
            profile = _keyword_profile(needs)

    if budget:
        profile["budget_lkr"] = float(budget)
    profile.setdefault("preferred_brands", [])
    profile["fallback_used"] = fallback_used
    if fallback_used:
        profile["fallback_basis"] = "existing device profile and general use"

    trace = state.get("trace", []) + [{
        "agent": "UserRequirementAgent",
        "action": "structured user needs",
        "details": profile,
    }]
    return {"requirements": profile, "trace": trace}

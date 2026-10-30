"""Agent 3 — Specification Retrieval Agent.

Retrieves candidate replacement devices from the dataset, honouring the
hard constraints in the requirement profile (budget tolerance, brand, 5G)
and ranking by a rough spec score. In a full deployment this agent would
also query spec APIs (e.g. GSMArena-style sources); here the dataset plays
that role, keeping retrieval deterministic and testable.
"""
from __future__ import annotations

from .. import config, dataset
from ..state import AgentState


def run(state: AgentState, llm) -> dict:
    phones = dataset.load_phones()
    requirements = state.get("requirements", {})
    candidates = dataset.filter_candidates(
        phones, requirements, config.MAX_CANDIDATES)

    relaxed = False
    if not candidates:
        # Budget/brand constraints may be impossible on a small dataset:
        # fall back to the best-scoring devices overall, flagged so the
        # Comparison Agent can mark them as over-budget honestly.
        relaxed = True
        candidates = dataset.filter_candidates(
            phones, {"preferred_brands": requirements.get("preferred_brands", [])},
            config.MAX_CANDIDATES)

    fallback_used = bool(requirements.get("fallback_used"))
    if fallback_used:
        candidates = phones
        old = state.get("old_device_profile", {})
        numeric = ("chipset_tier", "ram_gb", "storage_gb", "display_size_in",
                   "camera_mp", "battery_mah")
        def profile_fit(phone: dict) -> float:
            distances = []
            for field in numeric:
                a, b = old.get(field), phone.get(field)
                if a in (None, "") or b in (None, ""):
                    continue
                try:
                    a, b = float(a), float(b)
                    distances.append(abs(a - b) / max(abs(a), abs(b), 1.0))
                except (TypeError, ValueError):
                    continue
            if old.get("os") and phone.get("os"):
                distances.append(0.0 if str(old["os"]).casefold() == str(phone["os"]).casefold() else 1.0)
            return 1.0 - (sum(distances) / len(distances)) if distances else 0.0
        candidates.sort(key=profile_fit, reverse=True)
        candidates = candidates[:config.MAX_CANDIDATES]

    trace = state.get("trace", []) + [{
        "agent": "SpecificationRetrievalAgent",
        "action": f"retrieved {len(candidates)} candidates "
                  f"from {len(phones)} devices"
                  + (" (constraints relaxed: empty pool)" if relaxed else ""),
        "details": {"fallback_from_device_profile": fallback_used,
                    "candidates": [f"{p.get('brand')} {p.get('model')}" for p in candidates]},
    }]
    return {"candidates": candidates, "trace": trace}

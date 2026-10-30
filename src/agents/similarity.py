"""Similarity Agent: compare replacement candidates with the user's device."""
from __future__ import annotations

from ..state import AgentState


def _similarity(candidate: dict, profile: dict) -> float:
    fields = {
        "chipset_tier": 1.0,
        "ram_gb": 1.0,
        "storage_gb": 0.8,
        "display_size_in": 0.5,
        "camera_mp": 0.7,
        "battery_mah": 0.7,
    }
    scores = []
    weights = []
    for key, weight in fields.items():
        old_value, new_value = profile.get(key), candidate.get(key)
        if old_value in (None, "") or new_value in (None, ""):
            continue
        try:
            old_value, new_value = float(old_value), float(new_value)
        except (TypeError, ValueError):
            continue
        scale = max(abs(old_value), abs(new_value), 1.0)
        scores.append(max(0.0, 1.0 - abs(new_value - old_value) / scale))
        weights.append(weight)
    if profile.get("os") and candidate.get("os"):
        scores.append(1.0 if str(profile["os"]).casefold() == str(candidate["os"]).casefold() else 0.0)
        weights.append(1.0)
    return round(100 * sum(s * w for s, w in zip(scores, weights)) / sum(weights), 1) if weights else 0.0


def run(state: AgentState, llm) -> dict:
    candidates = state.get("candidates", [])
    profile = state.get("old_device_profile", {})
    scores = {str(phone.get("id")): _similarity(phone, profile) for phone in candidates}
    ranked = sorted(scores, key=scores.get, reverse=True)
    trace = state.get("trace", []) + [{
        "agent": "SimilarityAgent",
        "action": f"compared {len(scores)} candidates with the existing device",
        "details": [{"id": pid, "similarity_score": scores[pid]} for pid in ranked[:5]],
    }]
    return {"similarity": scores, "trace": trace}

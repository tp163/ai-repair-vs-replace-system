"""Device identification and confirmation (Person A, proposal section 5.1).

Pure functions, no Streamlit and no I/O. They read the shared phone catalogue
(from ``src.dataset.load_phones``) but never modify it.

Flow:
    match = match_device(brand, model, catalogue)
    confirmation = build_confirmation(match, selected_id, user_confirmed, manual_ok)
    if analysis_allowed(confirmation): run the pipeline

Match statuses:
    "exact"             one catalogue row matches -> user ticks confirm
    "multiple_variants" several rows (RAM/storage variants) -> user picks one, then confirms
    "not_found"         nothing matches -> fuzzy suggestions; user may continue
                        with the details they typed (marked unverified)
"""
from __future__ import annotations

import re
from difflib import get_close_matches

# (field, label, unit suffix) shown to the user when confirming a variant
SPEC_FIELDS = [
    ("release_year", "Released", ""),
    ("ram_gb", "RAM", " GB"),
    ("storage_gb", "Storage", " GB"),
    ("display_size_in", "Display", " in"),
    ("display_type", "Panel", ""),
    ("refresh_rate_hz", "Refresh rate", " Hz"),
    ("camera_mp", "Main camera", " MP"),
    ("battery_mah", "Battery", " mAh"),
    ("has_5g", "5G", ""),
    ("os", "OS", ""),
]


def _norm(text: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(text or "").casefold())


def _model_key(brand: object, model: object) -> str:
    """Normalised model, with a leading brand removed ("Samsung Galaxy A51" -> "galaxya51")."""
    b, m = _norm(brand), _norm(model)
    return m[len(b):] if b and m.startswith(b) else m


def _phone_id(phone: dict, index: int) -> str:
    return str(phone.get("id") or f"row-{index}")


def variant_label(phone: dict) -> str:
    variant = phone.get("variant") or phone.get("id") or "Standard variant"
    return (f"{variant} · {phone.get('ram_gb', '?')} GB RAM · "
            f"{phone.get('storage_gb', '?')} GB storage")


def specs_summary(phone: dict) -> dict:
    """Raw spec values present on the catalogue row (stored in the state)."""
    return {field: phone[field] for field, _, _ in SPEC_FIELDS
            if phone.get(field) not in (None, "")}


def format_specs(phone: dict) -> list[tuple[str, str]]:
    """(label, display value) pairs for showing specs in the UI."""
    out = []
    for field, label, unit in SPEC_FIELDS:
        value = phone.get(field)
        if value in (None, ""):
            continue
        if field == "has_5g":
            text = "Yes" if value in (True, 1, "1", "true", "True", "yes", "Yes") else "No"
        else:
            text = f"{value}{unit}"
        out.append((label, text))
    return out


def match_device(brand: str, model: str, catalogue: list[dict]) -> dict:
    """Match what the user typed against the catalogue.

    Case, spacing and punctuation are ignored, and a brand typed inside the
    model field is tolerated. Returns:
        {"match_status", "options": [{"id","label","phone"}], "suggestions": [{"brand","model"}]}
    """
    nb, nm = _norm(brand), _model_key(brand, model)
    options = []
    for i, phone in enumerate(catalogue):
        if _norm(phone.get("brand")) == nb and _model_key(phone.get("brand"), phone.get("model")) == nm:
            options.append({"id": _phone_id(phone, i), "label": variant_label(phone), "phone": phone})

    if options:
        status = "exact" if len(options) == 1 else "multiple_variants"
        return {"match_status": status, "options": options, "suggestions": []}

    # No exact match: suggest the closest distinct brand+model pairs.
    pairs = {}
    for phone in catalogue:
        key = _norm(phone.get("brand")) + _model_key(phone.get("brand"), phone.get("model"))
        pairs.setdefault(key, {"brand": phone.get("brand"), "model": phone.get("model")})
    close = get_close_matches(nb + nm, list(pairs), n=3, cutoff=0.6) if nb + nm else []
    return {"match_status": "not_found", "options": [],
            "suggestions": [pairs[k] for k in close]}


def build_confirmation(match: dict, selected_id: str | None,
                       user_confirmed: bool, manual_ok: bool = False) -> dict:
    """Build the ``device_confirmation`` dict for the shared state.

    ``confirmed`` is the gate: analysis must not run unless it is True.
    - exact / multiple_variants: True only if a variant is selected AND the user ticked confirm
    - not_found: True only if the user chose to continue with their typed details (unverified)
    """
    status = match["match_status"]
    base = {"match_status": status, "matched_id": None, "specs_shown": {},
            "options": [{"id": o["id"], "label": o["label"]} for o in match["options"]],
            "confirmed": False, "unverified": False}

    if status == "not_found":
        base["confirmed"] = bool(manual_ok)
        base["unverified"] = True
        return base

    chosen = next((o for o in match["options"] if o["id"] == selected_id), None)
    if chosen is None and len(match["options"]) == 1:
        chosen = match["options"][0]
    if chosen is not None:
        base["matched_id"] = chosen["id"]
        base["specs_shown"] = specs_summary(chosen["phone"])
        base["confirmed"] = bool(user_confirmed)
    return base


def analysis_allowed(confirmation: dict | None) -> bool:
    """Gate used by the UI and by the graph before any analysis step."""
    return bool(confirmation and confirmation.get("confirmed"))
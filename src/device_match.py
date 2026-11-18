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
    "fuzzy_match"       close typo matches known device -> user can see autocorrected name & links
    "not_found"         nothing matches -> fuzzy suggestions; user may continue
                        with the details they typed (marked unverified)
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher, get_close_matches

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


def _find_fuzzy_match(
    brand: str, model: str, catalogue: list[dict], cutoff: float = 0.75
) -> tuple[dict | None, float]:
    """Find the best catalogue phone matching a typo in brand or model.

    Guards against false positives:
    - Digits in user input must match digits in the candidate model.
    - Suffix qualifiers ('pro', 'max', 'ultra', 'mini', 'plus', 'lite', '4g', '5g') must match.
    """
    nb = _norm(brand)
    nm = _model_key(brand, model)
    user_norm = nb + nm if nb else nm
    if not user_norm:
        return None, 0.0

    user_str = f"{brand} {model}".strip().lower()
    user_nums = set(re.findall(r"\d+", user_str))
    user_words = set(re.findall(r"[a-z]+", user_str))
    qualifiers = {"pro", "max", "ultra", "mini", "plus", "lite", "4g", "5g"}
    user_quals = user_words & qualifiers

    best_match = None
    best_score = 0.0

    for phone in catalogue:
        p_brand = str(phone.get("brand", ""))
        p_model = str(phone.get("model", ""))
        p_norm = _norm(p_brand) + _model_key(p_brand, p_model)
        p_str = f"{p_brand} {p_model}".strip().lower()
        p_nums = set(re.findall(r"\d+", p_str))
        p_quals = set(re.findall(r"[a-z]+", p_str)) & qualifiers

        # If digits appear in either, they must match exactly
        if user_nums or p_nums:
            if user_nums != p_nums:
                continue

        # Suffix qualifiers must match exactly (e.g. Pro vs non-Pro)
        if user_quals != p_quals:
            continue

        ratio = SequenceMatcher(None, user_norm, p_norm).ratio()
        if ratio > best_score:
            best_score = ratio
            best_match = phone

    if best_match and best_score >= cutoff:
        return best_match, best_score
    return None, 0.0


def match_device(brand: str, model: str, catalogue: list[dict]) -> dict:
    """Match what the user typed against the catalogue.

    Case, spacing and punctuation are ignored, and a brand typed inside the
    model field is tolerated. Typo tolerance / fuzzy matching is supported
    for close matches while guarding against cross-model misidentification.

    Returns:
        {"match_status", "options": [{"id","label","phone"}], "suggestions": [{"brand","model"}], "was_corrected": bool}
    """
    nb, nm = _norm(brand), _model_key(brand, model)
    user_norm = nb + nm if nb else nm
    options = []
    for i, phone in enumerate(catalogue):
        if _norm(phone.get("brand")) == nb and _model_key(phone.get("brand"), phone.get("model")) == nm:
            options.append({"id": _phone_id(phone, i), "label": variant_label(phone), "phone": phone})

    if options:
        status = "exact" if len(options) == 1 else "multiple_variants"
        p = options[0]["phone"]
        return {
            "match_status": status,
            "options": options,
            "suggestions": [],
            "was_corrected": False,
            "confidence": 1.0,
            "canonical_brand": p.get("brand", brand),
            "canonical_model": p.get("model", model),
            "canonical_name": f"{p.get('brand', brand)} {p.get('model', model)}".strip(),
            "original_input": f"{brand} {model}".strip(),
        }

    # Typo-tolerant fuzzy matching against catalogue
    best_match, score = _find_fuzzy_match(brand, model, catalogue, cutoff=0.75)
    if best_match:
        canonical_brand = best_match.get("brand", "")
        canonical_model = best_match.get("model", "")
        fuzzy_options = []
        for i, phone in enumerate(catalogue):
            if (
                _norm(phone.get("brand")) == _norm(canonical_brand)
                and _model_key(phone.get("brand"), phone.get("model"))
                == _model_key(canonical_brand, canonical_model)
            ):
                fuzzy_options.append({"id": _phone_id(phone, i), "label": variant_label(phone), "phone": phone})

        return {
            "match_status": "fuzzy_match",
            "options": fuzzy_options,
            "suggestions": [],
            "was_corrected": True,
            "confidence": round(score, 2),
            "canonical_brand": canonical_brand,
            "canonical_model": canonical_model,
            "canonical_name": f"{canonical_brand} {canonical_model}".strip(),
            "original_input": f"{brand} {model}".strip(),
        }

    # No exact or fuzzy match: suggest the closest distinct brand+model pairs.
    pairs = {}
    for phone in catalogue:
        key = _norm(phone.get("brand")) + _model_key(phone.get("brand"), phone.get("model"))
        pairs.setdefault(key, {"brand": phone.get("brand"), "model": phone.get("model")})
    close = get_close_matches(user_norm, list(pairs), n=3, cutoff=0.6) if user_norm else []
    return {
        "match_status": "not_found",
        "options": [],
        "suggestions": [pairs[k] for k in close],
        "was_corrected": False,
        "confidence": 0.0,
        "original_input": f"{brand} {model}".strip(),
    }


def build_confirmation(match: dict, selected_id: str | None,
                       user_confirmed: bool, manual_ok: bool = False) -> dict:
    """Build the ``device_confirmation`` dict for the shared state.

    ``confirmed`` is the gate: analysis must not run unless it is True.
    - exact / multiple_variants / fuzzy_match: True only if a variant is selected AND confirmed
    - not_found: True only if the user chose to continue with their typed details (unverified)
    """
    status = match["match_status"]
    base = {
        "match_status": status,
        "matched_id": None,
        "specs_shown": {},
        "options": [{"id": o["id"], "label": o["label"]} for o in match["options"]],
        "confirmed": False,
        "unverified": False,
        "was_corrected": match.get("was_corrected", False),
        "canonical_brand": match.get("canonical_brand"),
        "canonical_model": match.get("canonical_model"),
        "canonical_name": match.get("canonical_name"),
        "original_input": match.get("original_input"),
    }

    if status == "not_found":
        base["confirmed"] = bool(manual_ok)
        base["unverified"] = True
        return base

    chosen = next((o for o in match["options"] if o["id"] == selected_id), None)
    if chosen is None and len(match["options"]) >= 1:
        chosen = match["options"][0]
    if chosen is not None:
        base["matched_id"] = chosen["id"]
        base["specs_shown"] = specs_summary(chosen["phone"])
        base["confirmed"] = bool(user_confirmed)
    return base


def analysis_allowed(confirmation: dict | None) -> bool:
    """Gate used by the UI and by the graph before any analysis step."""
    return bool(confirmation and confirmation.get("confirmed"))

"""Fault Diagnosis Agent for user-described symptoms and optional photos."""
from __future__ import annotations

import json
import re

from ..state import AgentState


def _demo_diagnosis(text: str, has_image: bool, image_reviewed: bool = False) -> dict:
    value = text.casefold()
    rules = [
        (("crack", "broken screen", "display damage"), "cracked_screen", "Possible physical screen damage."),
        (("battery", "swollen", "charge drain"), "battery", "Possible battery or power issue."),
        (("charge", "charging", "charger", "port"), "charging", "Possible cable, port or charging-circuit issue."),
        (("overheat", "hot", "heating"), "overheating", "Possible thermal, battery or heavy-use issue."),
        (("water", "wet", "liquid"), "liquid_damage", "Possible liquid exposure."),
        (("slow", "freeze", "lag", "crash"), "performance", "Possible software, storage or component issue."),
    ]
    for keywords, category, summary in rules:
        if any(word in value for word in keywords):
            return {"fault_category": category, "probable_cause": summary,
                    "confidence": "low", "evidence": ["user description"],
                    "image_reviewed": image_reviewed,
                    "uncertainty": "This is an initial screening, not a confirmed technician diagnosis."}
    return {"fault_category": "unclear", "probable_cause": "The available information is not enough to identify a likely fault.",
            "confidence": "low", "evidence": ["insufficient symptom detail"],
            "image_reviewed": image_reviewed,
            "uncertainty": "Add symptoms or use a vision-capable model to review the photo." if has_image and not image_reviewed else "More details or professional diagnosis may be needed."}


def run(state: AgentState, llm) -> dict:
    old = state.get("old_device", {})
    issue = state.get("issue_description") or old.get("fault", "")
    image = state.get("image_data_uri")
    prompt = (
        "Assess the phone issue from the user description and optional attached photo. "
        "Return JSON only with fault_category (cracked_screen, battery, charging, "
        "overheating, liquid_damage, performance, or unclear), probable_cause, "
        "confidence (low/medium/high), evidence (list), uncertainty. Do not claim "
        "certainty from a photo alone and do not give hazardous disassembly instructions.\n"
        f"Device: {old.get('brand', '')} {old.get('model', '')} {old.get('variant', '')}\n"
        f"Issue description: {issue or 'not provided'}"
    )
    result = None
    image_reviewed = False
    try:
        if getattr(llm, "name", "") != "demo" and (issue or image):
            raw = llm.chat(
                "You are a cautious consumer-phone triage assistant. Diagnose probable causes, "
                "state uncertainty, and prioritize safety. Return valid JSON only.",
                prompt, image_data_uri=image,
            )
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            result = json.loads(match.group(0)) if match else None
            image_reviewed = bool(image and result)
    except Exception:
        result = None
    if not isinstance(result, dict):
        result = _demo_diagnosis(issue, bool(image), False)
    result.setdefault("fault_category", "unclear")
    result.setdefault("probable_cause", "No likely cause could be established.")
    result.setdefault("confidence", "low")
    result.setdefault("evidence", [])
    result["image_attached"] = bool(image)
    result["image_reviewed"] = image_reviewed
    trace = state.get("trace", []) + [{
        "agent": "FaultDiagnosisAgent", "action": "screened issue description and available photo",
        "details": result,
    }]
    return {"diagnosis": result, "trace": trace}

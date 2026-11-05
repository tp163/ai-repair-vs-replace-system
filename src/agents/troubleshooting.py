"""Troubleshooting Agent (Person A, proposal section 5.2).

Gives safe, non-invasive steps for the diagnosed fault and applies hard
"see a technician" rules. Deterministic: no LLM is used, so safety behaviour
is the same in demo mode and with a real model.

Hard rules (escalate_to_technician = True):
  - any safety flag with severity "stop" (swollen battery, smoke / burning smell)
  - any liquid exposure flag, severe heat flag, or fault_category "liquid_damage"
  - fault_category "battery" together with a swelling flag
When escalated, the normal checks are replaced by a stop-use list. No step
ever asks the user to open the phone, press on a battery or use heat.

Output keys kept for app.py: steps (list of strings), safety_note,
self_repair_safe, professional_help_recommended.
New keys: escalate_to_technician, escalation_reason, safety_flag_codes,
detailed_steps (structured, one entry per string in steps). Step 6 fills
each detailed step's ``resources`` list.
"""
from __future__ import annotations

from ..resources import find_resources
from ..state import AgentState

# fault -> (self_repair_safe, [(text, risk)])
# risk: "safe" = user can do it, "caution" = user can do it with care,
#       "technician_only" = tell the user to book a repairer.
_GUIDES: dict[str, tuple[bool, list[tuple[str, str]]]] = {
    "cracked_screen": (False, [
        ("Back up important data if the phone still works.", "safe"),
        ("Cover the cracks with clear tape or a screen protector so loose glass does not cut your fingers.", "caution"),
        ("Avoid pressing on the cracked area.", "safe"),
        ("Arrange a screen inspection and replacement with a qualified repairer.", "technician_only"),
    ]),
    "battery": (False, [
        ("Check Settings > Battery for apps using unusual power and close or uninstall them.", "safe"),
        ("Install pending system and app updates, then restart the phone.", "safe"),
        ("Avoid charging overnight or in hot places such as under a pillow or in direct sun.", "safe"),
        ("Battery replacement should be done by a qualified repairer, not at home.", "technician_only"),
    ]),
    "charging": (True, [
        ("Try a known-good, compatible cable and power adapter.", "safe"),
        ("Try a different wall socket or power source.", "safe"),
        ("Restart the phone and check whether the charging message changes.", "safe"),
        ("With the phone switched off, use a light to look for lint in the port. Use only a wooden or plastic toothpick for lint, never metal or sharp tools.", "caution"),
        ("If the port looks bent or damaged, or the phone still will not charge, book a repairer.", "technician_only"),
    ]),
    "overheating": (True, [
        ("Close intensive apps and disconnect the charger.", "safe"),
        ("Remove the case and let the phone cool in a dry, shaded place.", "safe"),
        ("Do not put it in a fridge, freezer or near water.", "safe"),
        ("Install pending updates and check which apps are using the most battery.", "safe"),
        ("If it keeps overheating, book a repairer.", "technician_only"),
    ]),
    "liquid_damage": (False, []),  # always escalated, see _STOP_STEPS
    "performance": (True, [
        ("Restart the phone.", "safe"),
        ("Check for system and app updates.", "safe"),
        ("Back up important data and free up storage (aim for at least 10 to 15% free).", "safe"),
        ("Uninstall apps you do not use and clear app caches.", "safe"),
        ("If it still freezes or restarts, arrange a diagnostic check.", "technician_only"),
    ]),
    "unclear": (True, [
        ("Back up important data if the phone is stable enough to use.", "safe"),
        ("Note any error messages and when the problem happens.", "safe"),
        ("Restart the phone and install pending updates.", "safe"),
        ("Get a professional assessment if the issue continues.", "technician_only"),
    ]),
}

# Used when a hard rule fires. These replace the normal checks.
_STOP_STEPS: dict[str, list[tuple[str, str]]] = {
    "swollen_battery": [
        ("Stop using the phone and do not charge it.", "safe"),
        ("Do not press on the swelling, puncture it or try to open the phone.", "safe"),
        ("Keep the phone on a hard, non-flammable surface away from heat and flammable items.", "safe"),
    ],
    "burning_smell_smoke": [
        ("Unplug the charger if it is safe to do so, and stop using the phone.", "safe"),
        ("Move it away from flammable items and keep it on a hard, non-flammable surface.", "safe"),
        ("If you see smoke or flames, move away and call the fire service.", "safe"),
    ],
    "liquid_exposure": [
        ("Switch the phone off if it is safe to do so and do not charge it.", "safe"),
        ("Wipe the outside with a dry cloth. Do not use a hairdryer, oven or other heat.", "safe"),
        ("Do not shake it or press buttons repeatedly.", "safe"),
    ],
    "severe_heat": [
        ("Stop using the phone and disconnect the charger.", "safe"),
        ("Leave it to cool on a hard surface in a shaded, dry place. Do not use a fridge or freezer.", "safe"),
        ("Do not charge it again until a technician has checked it.", "safe"),
    ],
}
_STOP_ORDER = ["swollen_battery", "burning_smell_smoke", "severe_heat", "liquid_exposure"]

_FINAL_STEP = ("Take the phone to a qualified repairer for inspection. Do not try to open it yourself.",
               "technician_only")

_SAFETY_NOTE = "These are low-risk checks, not a substitute for a technician's diagnosis."
_ESCALATED_NOTE = ("Safety first: do not continue normal troubleshooting. "
                   "A technician should inspect this phone before it is charged or used again.")

_REASONS = {
    "swollen_battery": "possible swollen battery",
    "burning_smell_smoke": "smoke, sparks or a burning smell",
    "severe_heat": "dangerous heat",
    "liquid_exposure": "possible liquid exposure",
}


def _flag_codes(state: AgentState) -> list[str]:
    codes = [f.get("code") for f in (state.get("safety_flags") or []) if f.get("code")]
    for code in (state.get("diagnosis", {}) or {}).get("red_flags", []) or []:
        if code not in codes:
            codes.append(code)
    return codes


def _escalation_triggers(category: str, codes: list[str]) -> list[str]:
    triggers = [c for c in _STOP_ORDER if c in codes]
    if category == "liquid_damage" and "liquid_exposure" not in triggers:
        triggers.append("liquid_exposure")
    return triggers


def _detailed(steps: list[tuple[str, str]]) -> list[dict]:
    return [{"order": i, "text": text, "risk": risk, "resources": [],
             "requires_opening_device": False, "requires_soldering": False}
            for i, (text, risk) in enumerate(steps, start=1)]


def _attach_resources(detailed: list[dict], resources: list[dict], escalated: bool) -> None:
    """Attach verified links to steps (in place).

    support links go on the first user-doable step (not when escalated, because
    normal troubleshooting is stopped); service, info and guide links go on the
    final "book a repairer" step.
    """
    if not detailed or not resources:
        return
    doable = next((s for s in detailed if s["risk"] in ("safe", "caution")), None)
    technician = next((s for s in reversed(detailed) if s["risk"] == "technician_only"), None)
    if doable is not None and not escalated:
        doable["resources"] = [r for r in resources if r["type"] == "support"]
    if technician is not None:
        technician["resources"] = [r for r in resources if r["type"] in ("service", "info", "guide")]


def _resource_note(resources: list[dict], brand: str) -> str:
    if not resources:
        return "No verified repair links are available for this phone yet." if brand else ""
    if not any(r["scope"] == "model" for r in resources):
        return "No model-specific guide has been verified for this phone, so these are manufacturer pages."
    return ""


def run(state: AgentState, llm=None) -> dict:
    category = (state.get("diagnosis", {}) or {}).get("fault_category", "unclear")
    if category not in _GUIDES:
        category = "unclear"
    codes = _flag_codes(state)
    triggers = _escalation_triggers(category, codes)

    if triggers:
        steps: list[tuple[str, str]] = []
        for code in triggers:
            for item in _STOP_STEPS[code]:
                if item not in steps:
                    steps.append(item)
        steps.append(_FINAL_STEP)
        escalate, safe = True, False
        reason = "Stop and see a technician: " + ", ".join(_REASONS[c] for c in triggers) + "."
        note = _ESCALATED_NOTE
    else:
        safe, steps = _GUIDES[category]
        steps = list(steps)
        escalate, reason, note = False, "", _SAFETY_NOTE

        spec_answers = state.get("spec_answers", [])
        if spec_answers:
            first_ans = spec_answers[0]
            ans_text = first_ans.get("answer", "")
            first_claim = ans_text.split("\n")[0].strip("-* ")
            if len(first_claim) > 15:
                hw_step = f"Hardware context: {first_claim}. Keep this specification in mind when consulting a repairer."
                steps.insert(len(steps) - 1, (hw_step, "safe"))

    detailed = _detailed(steps)
    device = state.get("old_device", {}) or {}
    brand, model = str(device.get("brand", "")), str(device.get("model", ""))
    try:
        resources = find_resources(brand, model, category, escalated=escalate)
    except Exception:  # a bad resource file must never break safety guidance
        resources = []
    _attach_resources(detailed, resources, escalate)
    output = {
        "self_repair_safe": safe,
        "steps": [s["text"] for s in detailed],
        "detailed_steps": detailed,
        "professional_help_recommended": escalate or not safe or category == "unclear",
        "escalate_to_technician": escalate,
        "escalation_reason": reason,
        "safety_flag_codes": codes,
        "safety_note": note,
        "resources_found": len(resources),
        "resource_note": _resource_note(resources, brand),
    }
    trace = state.get("trace", []) + [{
        "agent": "TroubleshootingAgent",
        "action": ("escalated to technician by safety rule" if escalate
                   else "prepared safety-screened troubleshooting guidance"),
        "details": {"fault_category": category, "self_repair_safe": safe,
                    "escalate_to_technician": escalate, "step_count": len(steps),
                    "safety_flag_codes": codes},
    }]
    return {"troubleshooting": output, "trace": trace}
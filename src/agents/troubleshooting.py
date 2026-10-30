"""Troubleshooting Agent: offer non-invasive steps and flag technician cases."""
from __future__ import annotations

from ..state import AgentState

_GUIDES = {
    "cracked_screen": (False, ["Back up important data if the phone still works.",
                               "Avoid pressing on cracked glass and protect your fingers.",
                               "Arrange a screen inspection with a qualified repairer."]),
    "battery": (False, ["If the phone is unusually hot or the battery looks swollen, stop using and charging it.",
                        "Do not press, puncture, or open a swollen battery.",
                        "Keep it away from heat and arrange professional service."]),
    "charging": (True, ["Try a known-good, compatible cable and power adapter.",
                         "Restart the phone and check whether the charging message changes.",
                         "Use a light to look for debris in the port; do not insert metal or sharp tools.",
                         "If the port is damaged, hot, or smells burnt, stop charging and seek service."]),
    "overheating": (True, ["Stop intensive apps and disconnect the charger.",
                           "Remove the case and let the phone cool in a dry, shaded place.",
                           "Do not put it in a fridge or near water.",
                           "If overheating continues or the battery is swollen, stop using it and seek service."]),
    "liquid_damage": (False, ["Power the phone off if it is safe to do so.",
                              "Do not charge it or use heat to dry it.",
                              "Arrange professional inspection as soon as possible."]),
    "performance": (True, ["Restart the phone.",
                           "Check for system and app updates.",
                           "Back up important data and check available storage.",
                           "If it still freezes or shuts down, arrange a diagnostic check."]),
}


def run(state: AgentState, llm) -> dict:
    category = state.get("diagnosis", {}).get("fault_category", "unclear")
    safe, steps = _GUIDES.get(category, (True, [
        "Back up important data if the phone is stable enough to use.",
        "Note any error messages and when the issue occurs.",
        "Avoid opening the phone; get a professional assessment if the issue persists.",
    ]))
    output = {"self_repair_safe": safe, "steps": steps,
              "professional_help_recommended": not safe,
              "safety_note": "These are low-risk checks, not a substitute for a technician's diagnosis."}
    trace = state.get("trace", []) + [{
        "agent": "TroubleshootingAgent",
        "action": "prepared safety-screened troubleshooting guidance",
        "details": {"fault_category": category, "self_repair_safe": safe, "step_count": len(steps)},
    }]
    return {"troubleshooting": output, "trace": trace}

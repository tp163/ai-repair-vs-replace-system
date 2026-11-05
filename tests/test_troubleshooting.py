"""Tests for the Troubleshooting Agent safety rules."""
import re

import pytest

from src.agents import diagnosis, troubleshooting


class DemoLLM:
    name = "demo"


def pipeline(text, category=None):
    """Run diagnosis then troubleshooting, as the graph does."""
    state = {"old_device": {"brand": "Samsung", "model": "Galaxy A51"},
             "issue_description": text, "trace": []}
    state.update(diagnosis.run(state, DemoLLM()))
    if category:
        state["diagnosis"] = dict(state["diagnosis"], fault_category=category)
    state.update(troubleshooting.run(state, DemoLLM()))
    return state["troubleshooting"]


_FORBIDDEN = re.compile(r"\b(?:open (?:the|your) phone|pry\w*|disassembl\w*|solder\w*|use (?:a )?hairdryer|rice)\b", re.I)


class _Forbidden:
    """Matches instructions to do something unsafe. Sentences that start with
    "Do not" are prohibitions and are ignored."""

    @staticmethod
    def search(text):
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            if sentence.strip().lower().startswith(("do not", "don't")):
                continue
            match = _FORBIDDEN.search(sentence)
            if match:
                return match
        return None


FORBIDDEN = _Forbidden()


@pytest.mark.parametrize("category", ["cracked_screen", "battery", "charging",
                                      "overheating", "liquid_damage", "performance", "unclear"])
def test_every_category_has_steps_and_keeps_app_keys(category):
    out = pipeline("", category)
    assert out["steps"] and all(isinstance(s, str) for s in out["steps"])
    assert out["safety_note"]
    assert {"self_repair_safe", "professional_help_recommended"} <= set(out)
    assert len(out["detailed_steps"]) == len(out["steps"])


@pytest.mark.parametrize("text", [
    "battery is swollen and the back cover is lifting",
    "my phone smells like burning plastic",
    "phone fell in the toilet",
    "phone is too hot to touch",
])
def test_hard_rules_escalate(text):
    out = pipeline(text)
    assert out["escalate_to_technician"] is True
    assert out["self_repair_safe"] is False
    assert out["escalation_reason"]
    assert "technician" in out["steps"][-1].lower() or "repairer" in out["steps"][-1].lower()


def test_escalation_drops_normal_checks():
    # a charging complaint with liquid exposure must not suggest trying chargers
    out = pipeline("phone fell in water and won't charge")
    assert out["escalate_to_technician"]
    assert not any("cable" in s.lower() or "adapter" in s.lower() for s in out["steps"])


def test_swollen_battery_never_says_charge_or_open():
    out = pipeline("battery is swollen")
    text = " ".join(out["steps"]).lower()
    assert "do not charge" in text and "do not press" in text
    assert not FORBIDDEN.search(text)


def test_normal_cases_do_not_escalate():
    for text in ["screen cracked", "phone is slow and laggy", "won't charge, cable feels loose"]:
        assert pipeline(text)["escalate_to_technician"] is False


def test_negated_symptoms_do_not_escalate():
    assert pipeline("no water damage, just slow")["escalate_to_technician"] is False


def test_no_step_asks_user_to_open_device_or_solder():
    for category in troubleshooting._GUIDES:
        out = pipeline("", category)
        assert not FORBIDDEN.search(" ".join(out["steps"]))
        assert all(not s["requires_opening_device"] and not s["requires_soldering"]
                   for s in out["detailed_steps"])


def test_flags_from_state_trigger_escalation_even_if_diagnosis_differs():
    state = {"diagnosis": {"fault_category": "performance"},
             "safety_flags": [{"code": "swollen_battery", "severity": "stop", "message": "x"}],
             "trace": []}
    out = troubleshooting.run(state, DemoLLM())["troubleshooting"]
    assert out["escalate_to_technician"] is True


def test_unknown_category_falls_back_to_unclear():
    out = troubleshooting.run({"diagnosis": {"fault_category": "nonsense"}, "trace": []}, None)["troubleshooting"]
    assert out["steps"] and out["escalate_to_technician"] is False


def test_trace_appended():
    result = troubleshooting.run({"diagnosis": {"fault_category": "charging"}, "trace": [{"agent": "x"}]}, None)
    assert len(result["trace"]) == 2 and result["trace"][-1]["agent"] == "TroubleshootingAgent"
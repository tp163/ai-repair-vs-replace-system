"""Tests for the Fault Diagnosis Agent. These cases double as the seed of the
rule-based evaluation baseline (Step 9)."""
import json

import pytest

from src.agents import diagnosis


class DemoLLM:
    name = "demo"


class FakeLLM:
    name = "fake"

    def __init__(self, reply=None, error=None):
        self.reply, self.error = reply, error

    def chat(self, system, prompt, image_data_uri=None):
        if self.error:
            raise self.error
        return self.reply


def run(text, llm=None, image=None, state_extra=None):
    state = {"old_device": {"brand": "Samsung", "model": "Galaxy A51"},
             "issue_description": text, "image_data_uri": image, "trace": []}
    state.update(state_extra or {})
    return diagnosis.run(state, llm or DemoLLM())


@pytest.mark.parametrize("text, category", [
    ("screen cracked", "cracked_screen"),
    ("phone won't charge, the cable feels loose", "charging"),
    ("battery is swollen and the back cover is lifting", "battery"),
    ("my phone fell in the toilet", "liquid_damage"),
    ("my phone gets very hot when I play games", "overheating"),
    ("no cracks, just slow and laggy", "performance"),
    ("", "unclear"),
    ("wet and hot", "unclear"),  # tie: must not guess
])
def test_rule_categories(text, category):
    assert run(text)["diagnosis"]["fault_category"] == category


def test_word_boundaries():
    # "hot" inside "photo" must not trigger overheating
    out = run("I took a photo")["diagnosis"]
    assert out["fault_category"] == "unclear"


def test_negation_removes_symptom():
    assert run("no cracks on the screen, no water damage")["diagnosis"]["fault_category"] == "unclear"


def test_alternatives_listed_for_multiple_faults():
    out = run("screen cracked and battery drains fast")["diagnosis"]
    cats = {out["fault_category"]} | {a["fault_category"] for a in out["alternatives"]}
    assert {"cracked_screen", "battery"} <= cats


def test_safety_flags_are_deterministic():
    flags = run("battery is swollen")["safety_flags"]
    assert any(f["code"] == "swollen_battery" and f["severity"] == "stop" for f in flags)
    assert any(f["code"] == "burning_smell_smoke" for f in run("it smells like burning plastic")["safety_flags"])
    assert run("no swelling, just slow")["safety_flags"] == []


def test_llm_valid_output_used():
    reply = json.dumps({"fault_category": "charging", "probable_cause": "Port wear",
                        "confidence": "medium", "evidence": ["won't charge"], "uncertainty": "x"})
    out = run("won't charge", FakeLLM(reply))["diagnosis"]
    assert out["method"] == "llm" and out["fault_category"] == "charging"
    assert out["rule_category"] == "charging"


def test_llm_invalid_category_falls_back_to_rules():
    reply = json.dumps({"fault_category": "motherboard_failure", "confidence": "high"})
    out = run("screen cracked", FakeLLM(reply))["diagnosis"]
    assert out["method"] == "rules" and out["fault_category"] == "cracked_screen"
    assert "fallback_reason" in out


def test_llm_error_falls_back_to_rules():
    out = run("screen cracked", FakeLLM(error=RuntimeError("down")))["diagnosis"]
    assert out["method"] == "rules" and "RuntimeError" in out["fallback_reason"]


def test_llm_cannot_remove_safety_flags():
    reply = json.dumps({"fault_category": "performance", "confidence": "high"})
    result = run("battery is swollen", FakeLLM(reply))
    assert any(f["code"] == "swollen_battery" for f in result["safety_flags"])


def test_image_not_reviewed_in_demo_mode():
    out = run("screen cracked", image="data:image/png;base64,AAAA")["diagnosis"]
    assert out["image_attached"] and not out["image_reviewed"]
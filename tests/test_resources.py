"""Tests for the self-repair resource lookup and its use in troubleshooting."""
import json

import pytest

from src import resources
from src.agents import diagnosis, troubleshooting


class DemoLLM:
    name = "demo"


def pipeline(text, brand, model):
    state = {"old_device": {"brand": brand, "model": model},
             "issue_description": text, "trace": []}
    state.update(diagnosis.run(state, DemoLLM()))
    state.update(troubleshooting.run(state, DemoLLM()))
    return state["troubleshooting"]


def all_links(out):
    return [r for s in out["detailed_steps"] for r in s["resources"]]


# ---- data file ----

def test_data_file_loads_and_every_entry_is_valid():
    entries = resources.load_resources()
    assert len(entries) >= 15
    raw = json.loads(resources.DEFAULT_PATH.read_text(encoding="utf-8"))["entries"]
    assert len(entries) == len(raw), "an entry in repair_resources.json failed validation"
    assert len({e["id"] for e in entries}) == len(entries), "duplicate ids"


def test_all_guides_flag_that_they_open_the_phone():
    for entry in resources.load_resources():
        if entry["type"] == "guide":
            assert entry["requires_opening_device"] is True


def test_invalid_entries_are_dropped(tmp_path):
    bad = tmp_path / "r.json"
    good = {"id": "a", "brand": "Apple", "faults": ["charging"], "type": "support", "title": "t",
            "url": "https://example.com", "source": "s", "verified_at": "2026-10-31"}
    bad.write_text(json.dumps({"entries": [
        good,
        dict(good, id="b", url="javascript:alert(1)"),
        dict(good, id="c", faults=["not_a_fault"]),
        dict(good, id="d", type="blog"),
        {"id": "e"},
    ]}))
    assert [e["id"] for e in resources.load_resources(bad)] == ["a"]


def test_missing_or_broken_file_returns_empty(tmp_path):
    assert resources.load_resources(tmp_path / "nope.json") == []
    broken = tmp_path / "broken.json"
    broken.write_text("{not json")
    assert resources.load_resources(broken) == []


# ---- lookup ----

def test_model_specific_comes_first():
    found = resources.find_resources("Samsung", "Galaxy A51", "cracked_screen")
    assert found and found[0]["scope"] == "model" and "A51" in found[0]["title"]


def test_brand_prefix_in_model_field_is_tolerated():
    a = resources.find_resources("Samsung", "Galaxy A51", "cracked_screen")
    b = resources.find_resources("samsung", "Samsung Galaxy-A51", "cracked_screen")
    assert a == b and a


def test_aliases_map_to_xiaomi():
    assert resources.find_resources("Poco", "X6", "charging")
    assert resources.find_resources("Redmi", "Note 13", "charging")


def test_unknown_brand_or_fault_returns_nothing():
    assert resources.find_resources("Nokia", "3310", "charging") == []
    assert resources.find_resources("", "", "charging") == []
    assert resources.find_resources("Apple", "iPhone 13", "unclear") == []


def test_escalated_drops_teardown_guides():
    normal = resources.find_resources("Apple", "iPhone 13", "cracked_screen")
    stopped = resources.find_resources("Apple", "iPhone 13", "cracked_screen", escalated=True)
    assert any(r["type"] == "guide" for r in normal)
    assert not any(r["type"] == "guide" for r in stopped)


def test_all_urls_are_http():
    for entry in resources.load_resources():
        assert entry["url"].startswith(("https://", "http://"))


# ---- troubleshooting integration ----

def test_cracked_screen_links_land_on_technician_step_with_flags():
    out = pipeline("screen cracked", "Samsung", "Galaxy A51")
    guide = [r for r in all_links(out) if r["type"] == "guide"]
    assert guide and guide[0]["requires_opening_device"] and guide[0]["uses_heat"]
    last = out["detailed_steps"][-1]
    assert last["risk"] == "technician_only" and last["resources"]


def test_charging_support_link_on_first_doable_step():
    out = pipeline("won't charge", "Samsung", "Galaxy A55")
    first = out["detailed_steps"][0]
    assert first["resources"] and first["resources"][0]["type"] == "support"


def test_safety_stop_has_no_support_or_guide_links():
    out = pipeline("battery is swollen", "Apple", "iPhone 13")
    assert out["escalate_to_technician"]
    assert not any(r["type"] in ("support", "guide") for r in all_links(out))


def test_liquid_case_never_links_a_teardown_guide():
    out = pipeline("fell in water and screen cracked", "Apple", "iPhone 13")
    assert out["escalate_to_technician"]
    assert not any(r["type"] == "guide" for r in all_links(out))


def test_unknown_phone_gets_note_and_no_links():
    out = pipeline("screen cracked", "Nokia", "3310")
    assert all_links(out) == []
    assert "No verified" in out["resource_note"]


def test_brand_level_only_note():
    out = pipeline("won't charge", "Samsung", "Galaxy A55")
    assert out["resources_found"] >= 1
    assert "manufacturer pages" in out["resource_note"]


def test_missing_data_file_does_not_break_guidance(monkeypatch):
    monkeypatch.setenv("REPAIR_RESOURCES_PATH", "/nonexistent/file.json")
    out = pipeline("screen cracked", "Samsung", "Galaxy A51")
    assert out["steps"] and all_links(out) == []
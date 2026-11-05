"""Unit tests for the Technical Datasheet RAG engine, variant isolation, and controlled agent integration.

Verifies:
1. Strict variant isolation (iPhone 13 vs 13 Pro, Redmi Note 13 4G vs 5G).
2. Fail-closed model gating for unindexed or unsupported models.
3. Content sanitization (no hazardous DIY steps or unsupported stats).
4. Full provenance tracking (direct HTTPS URLs, verified dates, citations).
5. Controlled integration into TroubleshootingAgent (hardware context without unsafe steps).
6. Controlled integration into RepairDecisionAgent (hardware serviceability explanation without threshold alterations).
7. Controlled integration into ExplanationAgent (verified OEM fact citations).
8. Graceful fallback when RAG is unavailable or safety stops are active.
"""
from pathlib import Path
import pytest

from src.rag.chunker import load_all_chunks, parse_datasheet
from src.rag.retriever import LexicalTFIDFVectorStore, query_datasheet_rag
from src.agents import datasheet_rag, troubleshooting, decision, explanation


@pytest.fixture
def datasheets_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "datasheets"


# ---------------------------------------------------------------------------
# 1. Variant Isolation & Integrity
# ---------------------------------------------------------------------------

def test_chunker_loads_all_seven_datasheets(datasheets_dir: Path):
    chunks = load_all_chunks(datasheets_dir)
    assert len(chunks) >= 28, f"Expected at least 28 chunks across 7 datasheets, got {len(chunks)}"

    for chunk in chunks:
        assert chunk["brand"], f"Chunk {chunk.get('chunk_id')} missing brand"
        assert chunk["model"], f"Chunk {chunk.get('chunk_id')} missing model"
        assert chunk["source_title"], f"Chunk {chunk.get('chunk_id')} missing source_title"
        assert chunk["source_url"].startswith("https://"), f"Chunk {chunk.get('chunk_id')} invalid source_url: {chunk.get('source_url')}"
        assert chunk["date_verified"] == "2026-11-05", f"Chunk {chunk.get('chunk_id')} missing or invalid date_verified"


def test_variant_isolation_iphone_13_vs_pro(datasheets_dir: Path):
    # Base iPhone 13 query
    res_base = query_datasheet_rag(
        brand="Apple",
        model="iPhone 13",
        query="display screen oled",
        component="screen",
        datasheets_dir=datasheets_dir,
    )
    assert len(res_base) > 0
    assert res_base[0]["model"] == "iPhone 13"
    assert "ProMotion" not in res_base[0]["text"]
    assert "https://support.apple.com/en-us/111872" in res_base[0]["source_url"]

    # iPhone 13 Pro query
    res_pro = query_datasheet_rag(
        brand="Apple",
        model="iPhone 13 Pro",
        query="display screen promotion 120hz",
        component="screen",
        datasheets_dir=datasheets_dir,
    )
    assert len(res_pro) > 0
    assert res_pro[0]["model"] == "iPhone 13 Pro"
    assert "ProMotion" in res_pro[0]["text"]
    assert "https://support.apple.com/en-us/100416" in res_pro[0]["source_url"]


def test_variant_isolation_redmi_note_13_4g_vs_5g(datasheets_dir: Path):
    # 4G model has Gorilla Glass 3
    res_4g = query_datasheet_rag(
        brand="Xiaomi",
        model="Redmi Note 13 4G",
        query="glass screen display",
        component="screen",
        datasheets_dir=datasheets_dir,
    )
    assert len(res_4g) > 0
    assert "Gorilla Glass 3" in res_4g[0]["text"]
    assert "Gorilla Glass 5" not in res_4g[0]["text"]
    assert "https://www.mi.com/my/product/redmi-note-13/specs/" in res_4g[0]["source_url"]

    # 5G model has Gorilla Glass 5
    res_5g = query_datasheet_rag(
        brand="Xiaomi",
        model="Redmi Note 13 5G",
        query="glass screen display",
        component="screen",
        datasheets_dir=datasheets_dir,
    )
    assert len(res_5g) > 0
    assert "Gorilla Glass 5" in res_5g[0]["text"]
    assert "https://www.mi.com/in/product/redmi-note-13-5g/specs/" in res_5g[0]["source_url"]


# ---------------------------------------------------------------------------
# 2. Fail-Closed Gating
# ---------------------------------------------------------------------------

def test_fail_closed_for_unindexed_model_of_known_brand(datasheets_dir: Path):
    # Query an unindexed Samsung model: should NEVER return Galaxy A51 or A55 chunks
    results = query_datasheet_rag(
        brand="Samsung",
        model="Galaxy S21",
        query="battery replacement",
        datasheets_dir=datasheets_dir,
    )
    assert results == [], "Fail-closed check failed: Galaxy S21 returned chunks from other models"


def test_fail_closed_for_unknown_brand_and_model(datasheets_dir: Path):
    results = query_datasheet_rag(
        brand="OnePlus",
        model="9 Pro",
        query="screen broken",
        datasheets_dir=datasheets_dir,
    )
    assert results == []


def test_empty_model_returns_no_rag_information(datasheets_dir: Path):
    results = query_datasheet_rag(
        brand="Apple",
        model="",
        query="battery",
        datasheets_dir=datasheets_dir,
    )
    assert results == []


def test_exact_model_matching_rejects_variants_like_mini_or_5g(datasheets_dir: Path):
    # Verify that requesting undocumented sub-variants fails closed
    assert query_datasheet_rag("Apple", "iPhone 13 mini", "battery", datasheets_dir=datasheets_dir) == []
    assert query_datasheet_rag("Samsung", "Galaxy A51 5G", "battery", datasheets_dir=datasheets_dir) == []
    # Documented base models succeed
    assert len(query_datasheet_rag("Apple", "iPhone 13", "battery", datasheets_dir=datasheets_dir)) > 0
    assert len(query_datasheet_rag("Samsung", "Galaxy A51", "battery", datasheets_dir=datasheets_dir)) > 0


# ---------------------------------------------------------------------------
# 3. Content Sanitization (No Hazardous Advice)
# ---------------------------------------------------------------------------

def test_no_hazardous_advice_in_datasheets(datasheets_dir: Path):
    chunks = load_all_chunks(datasheets_dir)
    hazardous_phrases = [
        "fire extinguisher",
        "solvent",
        "80°c",
        "heat plate",
        "resolves 90% of charging failures",
        "pry with",
    ]
    for chunk in chunks:
        text_lower = chunk["text"].lower()
        for phrase in hazardous_phrases:
            assert phrase not in text_lower, f"Hazardous or unverified phrase '{phrase}' found in chunk {chunk['chunk_id']}"


# ---------------------------------------------------------------------------
# 4. Agent Integrations & Fallbacks
# ---------------------------------------------------------------------------

def test_troubleshooting_agent_uses_rag_hardware_context():
    state = {
        "old_device": {"brand": "Samsung", "model": "Galaxy A51"},
        "diagnosis": {"fault_category": "charging"},
        "safety_flags": [],
        "spec_answers": [{
            "question": "Verified hardware specs for Samsung Galaxy A51",
            "answer": "Modularity Status: Modular daughterboard (Sub-PBA) housing USB-C port.",
            "sources": [{"doc": "iFixit", "source_url": "https://www.ifixit.com/Device/Samsung_Galaxy_A51"}],
        }],
        "trace": [],
    }

    result = troubleshooting.run(state, llm=None)["troubleshooting"]
    
    # Check that a Hardware context step was added
    hw_steps = [s for s in result["steps"] if s.startswith("Hardware context:")]
    assert len(hw_steps) == 1, "Expected Hardware context step in troubleshooting guidance"
    assert "Modular daughterboard" in hw_steps[0]

    # Verify that no step asks user to open or solder
    assert not any(s.get("requires_opening_device") for s in result["detailed_steps"])
    assert not any(s.get("requires_soldering") for s in result["detailed_steps"])


def test_troubleshooting_agent_suppresses_hardware_context_on_safety_escalation():
    # If a hazardous flag is present (e.g. burning smell), hardware advice must be suppressed
    state = {
        "old_device": {"brand": "Samsung", "model": "Galaxy A51"},
        "diagnosis": {"fault_category": "charging"},
        "safety_flags": [{"code": "burning_smell_smoke", "severity": "stop", "message": "Phone smells like burning"}],
        "spec_answers": [{
            "question": "Verified hardware specs",
            "answer": "Modularity Status: Modular daughterboard",
            "sources": [],
        }],
        "trace": [],
    }

    result = troubleshooting.run(state, llm=None)["troubleshooting"]
    assert result["escalate_to_technician"] is True
    # Hardware step must NOT be present during safety stop
    assert not any("Hardware context:" in s for s in result["steps"])


def test_troubleshooting_agent_fallback_when_rag_unavailable():
    # When spec_answers is empty, existing behavior continues without Hardware context step
    state = {
        "old_device": {"brand": "OnePlus", "model": "9 Pro"},
        "diagnosis": {"fault_category": "charging"},
        "safety_flags": [],
        "spec_answers": [],
        "trace": [],
    }

    result = troubleshooting.run(state, llm=None)["troubleshooting"]
    assert not any("Hardware context:" in s for s in result["steps"])
    assert result["self_repair_safe"] is True
    assert len(result["steps"]) > 0


def test_repair_decision_agent_includes_hardware_modularity_in_reason():
    state = {
        "repair_cost_estimate": {"status": "unavailable"},
        "old_device_profile": {"estimated_residual_lkr": 45000},
        "troubleshooting": {"professional_help_recommended": False},
        "diagnosis": {"fault_category": "charging"},
        "spec_answers": [{
            "answer": "Modularity Status: Modular daughterboard (Sub-PBA) housing USB-C port.",
            "sources": [],
        }],
        "trace": [],
    }

    result = decision.run(state, llm=None)["decision"]
    assert "modular sub-board design" in result["reason"]
    # Path decision remains strictly evidence-based and thresholds unchanged
    assert result["recommended_path"] == "get_repair_quote"


def test_repair_decision_agent_fallback_when_rag_unavailable():
    state = {
        "repair_cost_estimate": {"status": "unavailable"},
        "old_device_profile": {"estimated_residual_lkr": 45000},
        "troubleshooting": {"professional_help_recommended": False},
        "diagnosis": {"fault_category": "charging"},
        "spec_answers": [],
        "trace": [],
    }

    result = decision.run(state, llm=None)["decision"]
    assert "modular sub-board design" not in result["reason"]
    assert result["recommended_path"] == "get_repair_quote"


def test_explanation_agent_includes_verified_hardware_fact():
    state = {
        "recommendations": [{"name": "Galaxy A55", "price_lkr": 118000, "score": 88,
                             "dimensions": {"performance": 0.8, "camera": 0.8, "battery": 0.9, "price_fit": 0.7},
                             "verdict_vs_old": "Upgrades display to 120Hz"}],
        "requirements": {"budget_lkr": 120000, "priorities": ["battery"]},
        "old_device_profile": {"brand": "Samsung", "model": "Galaxy A51", "estimated_residual_lkr": 35000},
        "verification": {"all_passed": True, "prices_are": "verified"},
        "spec_answers": [{
            "question": "Verified hardware specs for Samsung Galaxy A51",
            "answer": "Modularity Status: Modular daughterboard (Sub-PBA) housing USB-C port.",
            "sources": [{"doc": "Samsung Service Documentation", "source_url": "https://www.ifixit.com/Device/Samsung_Galaxy_A51"}],
        }],
        "trace": [],
    }

    text = explanation.run(state, llm=type("FakeLLM", (), {"name": "demo"}))["explanation"]
    assert "Verified Hardware Context (Samsung Service Documentation):" in text
    assert "Modularity Status: Modular daughterboard" in text
    assert "https://www.ifixit.com/Device/Samsung_Galaxy_A51" in text


def test_explanation_agent_fallback_when_rag_unavailable():
    state = {
        "recommendations": [{"name": "Galaxy A55", "price_lkr": 118000, "score": 88,
                             "dimensions": {"performance": 0.8, "camera": 0.8, "battery": 0.9, "price_fit": 0.7},
                             "verdict_vs_old": "Upgrades display to 120Hz"}],
        "requirements": {"budget_lkr": 120000, "priorities": ["battery"]},
        "old_device_profile": {"brand": "OnePlus", "model": "9 Pro", "estimated_residual_lkr": 45000},
        "verification": {"all_passed": True, "prices_are": "verified"},
        "spec_answers": [],
        "trace": [],
    }

    text = explanation.run(state, llm=type("FakeLLM", (), {"name": "demo"}))["explanation"]
    assert "Verified Hardware Context" not in text
    assert "Galaxy A55" in text


def test_datasheet_rag_agent_requires_confirmed_catalogue_match():
    # 1. Fully confirmed identity retrieves datasheet
    state_confirmed = {
        "old_device": {"brand": "Samsung", "model": "Galaxy A51", "matched_id": "samsung_galaxy_a51"},
        "device_confirmation": {"confirmed": True, "unverified": False, "matched_id": "samsung_galaxy_a51"},
        "issue_description": "charging port loose",
        "diagnosis": {"fault_category": "charging"},
        "trace": [],
    }
    res_conf = datasheet_rag.run(state_confirmed)
    assert len(res_conf["spec_answers"]) > 0
    assert "technical_specs" in res_conf["diagnosis"]
    assert "retrieved" in res_conf["trace"][-1]["action"]

    # 2. Unverified device (user bypassed catalogue match) skips retrieval
    state_unverified = {
        "old_device": {"brand": "Samsung", "model": "Galaxy A51", "matched_id": "samsung_galaxy_a51"},
        "device_confirmation": {"confirmed": True, "unverified": True, "matched_id": "samsung_galaxy_a51"},
        "issue_description": "charging port loose",
        "diagnosis": {"fault_category": "charging"},
        "trace": [],
    }
    res_unver = datasheet_rag.run(state_unverified)
    assert res_unver["spec_answers"] == []
    assert "technical_specs" not in res_unver["diagnosis"]
    assert "skipped datasheet retrieval because device identity is unconfirmed" in res_unver["trace"][-1]["action"]

    # 3. Unconfirmed state skips retrieval
    state_unconfirmed = {
        "old_device": {"brand": "Samsung", "model": "Galaxy A51", "matched_id": "samsung_galaxy_a51"},
        "device_confirmation": {"confirmed": False, "unverified": False, "matched_id": "samsung_galaxy_a51"},
        "issue_description": "charging port loose",
        "diagnosis": {"fault_category": "charging"},
        "trace": [],
    }
    res_unconf = datasheet_rag.run(state_unconfirmed)
    assert res_unconf["spec_answers"] == []

    # 4. Mismatched matched_id skips retrieval
    state_mismatch = {
        "old_device": {"brand": "Samsung", "model": "Galaxy A51", "matched_id": "samsung_galaxy_a51"},
        "device_confirmation": {"confirmed": True, "unverified": False, "matched_id": "other_id"},
        "issue_description": "charging port loose",
        "diagnosis": {"fault_category": "charging"},
        "trace": [],
    }
    res_mis = datasheet_rag.run(state_mismatch)
    assert res_mis["spec_answers"] == []


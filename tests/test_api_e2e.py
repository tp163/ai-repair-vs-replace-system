"""End-to-End API Integration Tests for REVIVAI.

Tests the complete API handler (diagnose_device) and LangGraph pipeline
orchestration from request validation through all 15 agents to response formatting.
"""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from api_server import DiagnoseRequest, diagnose_device


def test_api_supported_device_e2e():
    """Test full pipeline execution for an indexed device."""
    req = DiagnoseRequest(
        brand="Apple",
        model="iPhone 13",
        variant="128GB",
        query="my iponw 13 fell onto concrete and screen is shattered with green lines",
    )
    data = diagnose_device(req)

    assert data["status"] == "success"
    assert data["matched_device"]["brand"] == "Apple"
    assert data["matched_device"]["model"] == "iPhone 13"

    # Diagnosis Agent verification
    diagnosis = data["diagnosis"]
    assert diagnosis["fault_category"] == "cracked_screen"

    # Datasheet RAG Agent verification
    specs = data["spec_answers"]
    assert len(specs) > 0
    assert any("Display" in s.get("section", "") or "Screen" in s.get("question", "") for s in specs)
    assert any("support.apple.com" in s.get("source_url", "") for s in specs)

    # Repair Cost Agent verification
    repair_cost = data["repair_cost"]
    assert repair_cost is not None
    assert repair_cost.get("min_lkr") is not None
    assert repair_cost.get("max_lkr") is not None
    assert repair_cost["min_lkr"] <= repair_cost["max_lkr"]

    # Recommendations & Decision
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) > 0


def test_api_unsupported_near_miss_device_e2e():
    """Test full pipeline fail-closed safety for a near-miss unindexed model."""
    req = DiagnoseRequest(
        brand="Apple",
        model="iPhone 14",
        variant="128GB",
        query="display cracked after dropping on road",
    )
    data = diagnose_device(req)

    # Diagnosis should succeed on symptoms
    assert data["diagnosis"]["fault_category"] == "cracked_screen"

    # RAG must strictly fail closed (0 specs retrieved, no cross-model leakage from iPhone 13)
    assert len(data.get("spec_answers", [])) == 0

    # Repair cost must fail closed
    repair_cost = data.get("repair_cost") or {}
    assert repair_cost.get("min_lkr") is None
    assert repair_cost.get("status") == "unavailable"


def test_api_safety_swollen_battery_e2e():
    """Test full pipeline safety escalation for a battery swelling hazard."""
    req = DiagnoseRequest(
        brand="Samsung",
        model="Galaxy A51",
        variant="128GB",
        query="back cover is lifting up and battery looks swollen and puffy",
    )
    data = diagnose_device(req)

    # Safety flags
    safety_flags = data.get("safety_flags", [])
    assert any(f.get("code") == "swollen_battery" for f in safety_flags)

    # Troubleshooting escalation
    troubleshooting = data.get("troubleshooting", {})
    assert troubleshooting.get("escalate_to_technician") is True

    # Ensure safe guidance: explicitly tells user NOT to open or charge the device
    steps_text = " ".join(troubleshooting.get("steps", [])).lower()
    assert "do not try to open" in steps_text or "do not press" in steps_text
    assert "do not charge" in steps_text
    detailed_steps = troubleshooting.get("detailed_steps", [])
    assert all(not s.get("requires_opening_device") and not s.get("requires_soldering") for s in detailed_steps)


def test_api_missing_parameters_validation():
    """Test validation reject on empty inputs."""
    req = DiagnoseRequest(
        brand="",
        model="",
        query="",
    )
    with pytest.raises(HTTPException) as exc_info:
        diagnose_device(req)
    assert exc_info.value.status_code == 422

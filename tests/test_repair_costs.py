"""Unit tests for the Sri Lankan Repair-Cost Dataset and RepairDecisionAgent integration.

Verifies:
1. Integrity of data/repair_costs.json (schema, price bounds, direct HTTPS URLs, structured quote conditions).
2. Elimination of ungrounded brand fallbacks (strictly model-specific, exactly 21 records).
3. RepairCostAgent exact model matching, brand prefix normalization, and fail-closed behavior for unspecified models.
4. Pass-through of structured conditions (part quality, labor, warranty, location, pricing_type).
5. Clear distinction between published catalog listings, workshop inquiries, and verified quotations.
6. RepairDecisionAgent numerical thresholds (< 0.40 repair, > 0.60 replace, 0.40-0.60 compare) on verified prices.
7. Guarantee that unverified estimates/ranges do not issue confident repair/replace verdicts.
8. Safety stop precedence over cost calculations.
9. Clean fallback behavior when no sourced repair quote is available.
"""
import json
from pathlib import Path
import pytest

from src.dataset import load_repair_costs
from src.agents import repair_cost, decision


@pytest.fixture
def repair_costs_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "repair_costs.json"


# ---------------------------------------------------------------------------
# 1. Dataset Integrity & Schema
# ---------------------------------------------------------------------------

def test_repair_costs_dataset_loads_and_is_valid(repair_costs_path: Path):
    assert repair_costs_path.exists(), "data/repair_costs.json must exist"
    records = load_repair_costs(str(repair_costs_path))
    # Exactly 21 model-specific records (7 models x 3 fault categories: screen, battery, charging)
    assert len(records) == 21, f"Expected exactly 21 model-specific records, got {len(records)}"

    allowed_faults = {"cracked_screen", "battery", "charging"}
    allowed_types = {"catalog_price", "workshop_quotation", "indicative_estimate", "unavailable"}
    required_fields = [
        "id", "brand", "model", "fault_category", "repair_type",
        "currency", "pricing_type", "verified",
        "part_quality", "labor_included", "warranty_duration",
        "location", "taxes_and_diagnosis", "source", "source_url",
        "retrieved_at", "evidence_type", "evidence_status", "notes"
    ]

    for row in records:
        for field in required_fields:
            assert field in row, f"Record {row.get('id')} missing field: {field}"
            assert row[field] is not None, f"Record {row.get('id')} has null field: {field}"

        assert row["model"], f"Record {row.get('id')} has empty model (ungrounded fallbacks forbidden)"
        assert row["fault_category"] in allowed_faults, f"Invalid fault category: {row['fault_category']}"
        if row.get("availability_status") == "out_of_stock":
            assert row["in_stock"] is False
            assert row["min_lkr"] is None
            assert row["max_lkr"] is None
        else:
            assert isinstance(row["min_lkr"], (int, float)), f"min_lkr not numeric in {row['id']}"
            assert isinstance(row["max_lkr"], (int, float)), f"max_lkr not numeric in {row['id']}"
            assert row["min_lkr"] <= row["max_lkr"], f"min_lkr > max_lkr in {row['id']}"
        assert row["source_url"].startswith("https://"), f"Invalid source_url: {row['id']}"
        # Source URL must not be just root homepage
        assert row["source_url"] not in ("https://mistermobile.lk/", "https://doctormobile.lk/"), (
            f"Record {row['id']} points to a generic homepage instead of specific repair/product URL"
        )
        assert row["pricing_type"] in allowed_types, f"Invalid pricing_type in {row['id']}"
        assert row["verified"] is False, f"Record {row['id']} cannot be marked verified without physical quote ID"


def test_iphone_13_display_published_catalog_pricing(repair_costs_path: Path):
    records = load_repair_costs(str(repair_costs_path))
    ip13_screen = next(r for r in records if r["id"] == "apple-iphone-13-screen")
    assert ip13_screen["pricing_type"] == "catalog_price"
    assert ip13_screen["min_lkr"] == 8900
    assert ip13_screen["max_lkr"] == 34900
    assert "apple-iphone-13-original-display-with-free-installation" in ip13_screen["source_url"]
    assert "Inc-Cell" in ip13_screen["part_quality"]
    assert "Free installation included" in ip13_screen["labor_included"]


# ---------------------------------------------------------------------------
# 2. RepairCostAgent Gating & Retrieval
# ---------------------------------------------------------------------------

def test_repair_cost_agent_matches_exact_model():
    state = {
        "old_device": {"brand": "Samsung", "model": "Galaxy A51"},
        "diagnosis": {"fault_category": "cracked_screen"},
        "trace": [],
    }
    result = repair_cost.run(state, llm=None)["repair_cost_estimate"]
    assert result["status"] == "estimate"
    assert result["min_lkr"] == 4250
    assert result["max_lkr"] == 34900
    assert "Mister Mobile Sri Lanka" in result["source"]
    assert result["source_url"].startswith("https://")
    assert result["verified"] is False
    assert result["pricing_type"] == "catalog_price"
    assert "part_quality" in result
    assert "warranty_duration" in result
    assert "labor_included" in result


def test_repair_cost_agent_resolves_brand_aliases():
    # 'Redmi' brand alias resolves to Xiaomi Redmi Note 13 4G
    state = {
        "old_device": {"brand": "Redmi", "model": "Note 13 4G"},
        "diagnosis": {"fault_category": "cracked_screen"},
        "trace": [],
    }
    result = repair_cost.run(state, llm=None)["repair_cost_estimate"]
    assert result["status"] == "estimate"
    assert result["min_lkr"] == 11000
    assert result["max_lkr"] == 17500


def test_repair_cost_agent_tolerates_brand_prefix_in_model():
    # When user enters 'Samsung Galaxy A51' into model box with brand 'Samsung'
    state = {
        "old_device": {"brand": "Samsung", "model": "Samsung Galaxy A51"},
        "diagnosis": {"fault_category": "charging"},
        "trace": [],
    }
    result = repair_cost.run(state, llm=None)["repair_cost_estimate"]
    assert result["status"] == "estimate"
    assert result["min_lkr"] == 4500
    assert result["max_lkr"] == 7000


def test_repair_cost_agent_variant_isolation():
    # Redmi Note 13 4G vs 5G display replacement costs
    state_4g = {
        "old_device": {"brand": "Xiaomi", "model": "Redmi Note 13 4G"},
        "diagnosis": {"fault_category": "cracked_screen"},
        "trace": [],
    }
    res_4g = repair_cost.run(state_4g, llm=None)["repair_cost_estimate"]
    assert res_4g["status"] == "estimate"
    assert res_4g["min_lkr"] == 11000

    state_5g = {
        "old_device": {"brand": "Xiaomi", "model": "Redmi Note 13 5G"},
        "diagnosis": {"fault_category": "cracked_screen"},
        "trace": [],
    }
    res_5g = repair_cost.run(state_5g, llm=None)["repair_cost_estimate"]
    assert res_5g["status"] == "estimate"
    assert res_5g["min_lkr"] == 13500


def test_repair_cost_agent_fails_closed_when_model_is_unspecified():
    # With generic brand fallbacks eliminated, unspecified model must fail closed
    state = {
        "old_device": {"brand": "Apple", "model": ""},
        "diagnosis": {"fault_category": "battery"},
        "trace": [],
    }
    result = repair_cost.run(state, llm=None)["repair_cost_estimate"]
    assert result["status"] == "unavailable"
    assert result["min_lkr"] is None
    assert result["max_lkr"] is None


def test_repair_cost_agent_fails_closed_for_unindexed_model():
    # Samsung is in dataset, but Galaxy S21 is not
    state = {
        "old_device": {"brand": "Samsung", "model": "Galaxy S21"},
        "diagnosis": {"fault_category": "cracked_screen"},
        "trace": [],
    }
    result = repair_cost.run(state, llm=None)["repair_cost_estimate"]
    assert result["status"] == "unavailable"
    assert result["min_lkr"] is None
    assert result["max_lkr"] is None


def test_repair_cost_agent_fails_closed_for_unknown_brand():
    state = {
        "old_device": {"brand": "OnePlus", "model": "9 Pro"},
        "diagnosis": {"fault_category": "battery"},
        "trace": [],
    }
    result = repair_cost.run(state, llm=None)["repair_cost_estimate"]
    assert result["status"] == "unavailable"


# ---------------------------------------------------------------------------
# 3. RepairDecisionAgent Numerical Thresholds & Provenance Gating
# ---------------------------------------------------------------------------

def test_decision_agent_recommends_repair_when_verified_price_under_40_percent():
    # Verified Quote: LKR 5,750 midpoint. Device residual value: LKR 40,000.
    # Ratio = 5,750 / 40,000 = 0.14375 (< 0.40)
    state = {
        "repair_cost_estimate": {
            "status": "estimate",
            "verified": True,
            "min_lkr": 4500,
            "max_lkr": 7000,
            "source": "Doctor Mobile Sri Lanka",
            "source_url": "https://doctormobile.lk/smart-phone-repair/",
            "verification_evidence": "Quotation ID #DM-2026-A51-PORT",
            "part_quality": "OEM Sub-PBA",
            "warranty_duration": "30 days",
        },
        "old_device_profile": {"estimated_residual_lkr": 40000},
        "troubleshooting": {"escalate_to_technician": False, "professional_help_recommended": False},
        "diagnosis": {"fault_category": "charging"},
        "spec_answers": [],
        "trace": [],
    }
    result = decision.run(state, llm=None)["decision"]
    assert result["recommended_path"] == "repair_likely_worthwhile"
    assert result["cost_to_device_value_ratio_available"] is True
    assert result["cost_to_device_value_ratio"] == pytest.approx(0.14375, abs=1e-3)
    assert result["cost_verified"] is True
    assert "below 40%" in result["reason"]
    assert "financially sensible" in result["reason"]


def test_decision_agent_recommends_replacement_when_verified_price_over_60_percent():
    # Verified Quote: LKR 48,000 midpoint. Device residual value: LKR 50,000.
    # Ratio = 48,000 / 50,000 = 0.96 (> 0.60)
    state = {
        "repair_cost_estimate": {
            "status": "estimate",
            "verified": True,
            "min_lkr": 38000,
            "max_lkr": 58000,
            "source": "Mister Mobile Sri Lanka",
            "source_url": "https://mistermobile.lk/product/apple-iphone-13-original-display-with-free-installation/",
            "verification_evidence": "Catalog listing #MM-IP13-DISP",
        },
        "old_device_profile": {"estimated_residual_lkr": 50000},
        "troubleshooting": {"escalate_to_technician": False, "professional_help_recommended": False},
        "diagnosis": {"fault_category": "cracked_screen"},
        "spec_answers": [],
        "trace": [],
    }
    result = decision.run(state, llm=None)["decision"]
    assert result["recommended_path"] == "replacement_worth_considering"
    assert result["cost_to_device_value_ratio"] == 0.96
    assert result["cost_verified"] is True
    assert "above 60%" in result["reason"]


def test_decision_agent_recommends_compare_when_verified_price_between_40_and_60_percent():
    # Verified Quote: LKR 20,000 midpoint. Device residual value: LKR 40,000.
    # Ratio = 20,000 / 40,000 = 0.50 (in [0.40, 0.60])
    state = {
        "repair_cost_estimate": {
            "status": "estimate",
            "verified": True,
            "min_lkr": 16000,
            "max_lkr": 24000,
            "source": "Mister Mobile Sri Lanka",
            "source_url": "https://mistermobile.lk/product/samsung-galaxy-a51-display-with-free-installation/",
            "verification_evidence": "Workshop quotation #MM-A51-SCR",
        },
        "old_device_profile": {"estimated_residual_lkr": 40000},
        "troubleshooting": {"escalate_to_technician": False, "professional_help_recommended": False},
        "diagnosis": {"fault_category": "cracked_screen"},
        "spec_answers": [],
        "trace": [],
    }
    result = decision.run(state, llm=None)["decision"]
    assert result["recommended_path"] == "compare_quote_and_replacements"
    assert result["cost_to_device_value_ratio"] == 0.50
    assert result["cost_verified"] is True
    assert "middle range" in result["reason"]


def test_decision_agent_unverified_estimate_does_not_issue_confident_recommendation():
    # When cost is an unverified estimate, even if ratio is very low (< 40%),
    # agent must NOT issue a confident repair/replace verdict. It must require a local quote.
    state = {
        "repair_cost_estimate": {
            "status": "estimate",
            "verified": False,
            "pricing_type": "indicative_estimate",
            "min_lkr": 4500,
            "max_lkr": 7000,
            "part_quality": "OEM Sub-PBA",
            "warranty_duration": "30-day warranty",
            "source": "Doctor Mobile Sri Lanka",
            "source_url": "https://doctormobile.lk/smart-phone-repair/",
            "verification_evidence": "Unverified indicative estimate",
        },
        "old_device_profile": {"estimated_residual_lkr": 40000},
        "troubleshooting": {"escalate_to_technician": False, "professional_help_recommended": False},
        "diagnosis": {"fault_category": "charging"},
        "spec_answers": [],
        "trace": [],
    }
    result = decision.run(state, llm=None)["decision"]
    # Does NOT output confident "repair_likely_worthwhile"
    assert result["recommended_path"] == "get_repair_quote"
    assert result["cost_verified"] is False
    assert "unverified indicative range" in result["reason"]
    assert "Request a binding local workshop quote before deciding" in result["reason"]


def test_decision_agent_safety_stop_takes_precedence_over_cost_ratio():
    # Even if cost is low (< 40%), an active safety stop (e.g. swollen battery)
    # MUST enforce professional_repair_assessment
    state = {
        "repair_cost_estimate": {
            "status": "estimate",
            "verified": True,
            "min_lkr": 5000,
            "max_lkr": 8000,
            "source": "Doctor Mobile Sri Lanka",
            "source_url": "https://doctormobile.lk/smart-phone-repair/",
        },
        "old_device_profile": {"estimated_residual_lkr": 50000},
        "troubleshooting": {"escalate_to_technician": True, "professional_help_recommended": True},
        "diagnosis": {"fault_category": "battery"},
        "spec_answers": [],
        "trace": [],
    }
    result = decision.run(state, llm=None)["decision"]
    assert result["recommended_path"] == "professional_repair_assessment"
    assert "safety risk" in result["reason"]


def test_decision_agent_fallback_when_cost_unavailable():
    state = {
        "repair_cost_estimate": {"status": "unavailable"},
        "old_device_profile": {"estimated_residual_lkr": 30000},
        "troubleshooting": {"escalate_to_technician": False, "professional_help_recommended": False},
        "diagnosis": {"fault_category": "charging"},
        "spec_answers": [],
        "trace": [],
    }
    result = decision.run(state, llm=None)["decision"]
    assert result["recommended_path"] == "get_repair_quote"
    assert "A sourced repair range is not available" in result["reason"]


def test_repair_cost_agent_out_of_stock_prevents_price_contribution(monkeypatch):
    # Simulate an out-of-stock listing for iPhone 13 Pro screen
    state = {
        "old_device": {"brand": "Apple", "model": "iPhone 13 Pro"},
        "diagnosis": {"fault_category": "cracked_screen"},
        "old_device_profile": {"estimated_residual_lkr": 120000},
        "troubleshooting": {"escalate_to_technician": False, "professional_help_recommended": False},
        "spec_answers": [],
        "trace": [],
    }

    import src.dataset as dataset_mod
    original_records = dataset_mod.load_repair_costs()
    patched_records = []
    for r in original_records:
        r_copy = dict(r)
        if r_copy["id"] == "apple-iphone-13-pro-screen":
            r_copy["in_stock"] = False
            r_copy["stock_status"] = "out_of_stock"
        patched_records.append(r_copy)

    monkeypatch.setattr(dataset_mod, "load_repair_costs", lambda *args: patched_records)

    cost_res = repair_cost.run(state, llm=None)["repair_cost_estimate"]
    assert cost_res["status"] == "unavailable"
    assert cost_res["min_lkr"] is None
    assert cost_res["max_lkr"] is None
    assert "out of stock" in cost_res["message"].lower()

    # Pass into decision agent: must NOT calculate ratio or recommend repair based on old price
    state["repair_cost_estimate"] = cost_res
    decision_res = decision.run(state, llm=None)["decision"]
    assert decision_res["recommended_path"] == "get_repair_quote"
    assert decision_res["cost_to_device_value_ratio_available"] is False
    assert decision_res["cost_to_device_value_ratio"] is None
    assert decision_res["repair_cost_midpoint_lkr"] is None
    assert "A sourced repair range is not available" in decision_res["reason"]

"""Tests for benchmark dataset loaders (JSON, JSONL, and CSV/ORDS)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from evaluation.eval_diagnosis import load_dataset


def test_json_ingestion(tmp_path: Path):
    file = tmp_path / "test.json"
    data = [
        {"scenario_id": "S1", "brand": "Apple", "model": "iPhone 13", "input_query": "broken glass", "expected_fault_category": "cracked_screen"},
        {"scenario_id": "S2", "brand": "Samsung", "model": "Galaxy A51", "input_query": "battery drain", "expected_fault_category": "battery"},
    ]
    file.write_text(json.dumps(data), encoding="utf-8")
    records = load_dataset(file)
    assert len(records) == 2
    assert records[0]["has_ground_truth_label"] is True
    assert records[0]["expected_fault_category"] == "cracked_screen"


def test_jsonl_ingestion(tmp_path: Path):
    file = tmp_path / "test.jsonl"
    lines = [
        json.dumps({"scenario_id": "L1", "brand": "Apple", "model": "iPhone 13", "input_query": "port loose", "expected_fault_category": "charging"}),
        json.dumps({"scenario_id": "L2", "brand": "Google", "model": "Pixel 8a", "input_query": "hot frame", "expected_fault_category": "overheating"}),
    ]
    file.write_text("\n".join(lines), encoding="utf-8")
    records = load_dataset(file)
    assert len(records) == 2
    assert records[0]["scenario_id"] == "L1"
    assert records[1]["expected_fault_category"] == "overheating"


def test_csv_ords_ingestion_with_unlabelled_support(tmp_path: Path):
    file = tmp_path / "test.csv"
    fieldnames = [
        "id", "brand", "model", "problem", "fault_category",
        "expected_safety_escalation", "expected_target_sections", "expected_target_keywords"
    ]
    rows = [
        {
            "id": "CSV_1",
            "brand": "Apple",
            "model": "iPhone 13",
            "problem": "screen cracked",
            "fault_category": "cracked_screen",
            "expected_safety_escalation": "false",
            "expected_target_sections": "Display & Screen Specifications; Overview",
            "expected_target_keywords": "ceramic shield, oled",
        },
        {
            # Unlabelled raw MobiFix row (no ground truth category)
            "id": "CSV_2_MOBIFIX",
            "brand": "Motorola",
            "model": "G Power",
            "problem": "phone will not switch on after drop",
            "fault_category": "",
            "expected_safety_escalation": "false",
            "expected_target_sections": "",
            "expected_target_keywords": "",
        },
    ]
    with open(file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    records = load_dataset(file)
    assert len(records) == 2

    # Row 1 is labelled
    assert records[0]["has_ground_truth_label"] is True
    assert records[0]["expected_fault_category"] == "cracked_screen"
    assert records[0]["expected_target_sections"] == ["Display & Screen Specifications", "Overview"]
    assert records[0]["expected_target_keywords"] == ["ceramic shield", "oled"]

    # Row 2 is unlabelled - must NOT default to unclear!
    assert records[1]["has_ground_truth_label"] is False
    assert records[1]["expected_fault_category"] is None

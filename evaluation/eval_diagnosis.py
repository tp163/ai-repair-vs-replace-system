"""In-Process Multi-Agent Integration Benchmark Harness for REVIVAI.

Evaluates REVIVAI across three research evaluation groups:
  - Group A: General Diagnosis (ALL phones - symptom triage, label separation, and deterministic safety metrics)
  - Group B: Supported Models (Indexed phones - Information Retrieval Hit@K, genuine Recall@K, MRR & catalog pricing)
  - Group C: Unsupported & Near-Miss Models (Non-indexed phones - near-miss gating, fail-closed safety, and unsupported claim rejection)

Supports standard JSON, JSONL (JSON Lines), and ORDS/MobiFix CSV datasets.
Dynamic model detection: supported models are resolved directly from the live RAG vector store.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents import (
    datasheet_rag,
    diagnosis,
    explanation,
    repair_cost,
    troubleshooting,
)
from src.dataset import load_phones
from src.device_match import build_confirmation, match_device
from src.rag.retriever import _matches_model_strictly, get_vector_store


def is_supported_model(brand: str, model: str) -> bool:
    """Dynamically determine whether brand & model have an indexed datasheet in the RAG corpus.

    No static catalog hardcoding: adding a new Markdown datasheet to data/datasheets/
    automatically promotes that device to supported status in the evaluation harness.
    """
    if not brand.strip() or not model.strip():
        return False
    store = get_vector_store()
    return any(
        _matches_model_strictly(
            brand,
            model,
            chunk.get("brand", ""),
            chunk.get("model", ""),
            chunk.get("model_identifiers", ""),
        )
        for chunk in store.chunks
    )


def is_chunk_relevant(
    chunk: dict[str, Any],
    expected_sections: list[str],
    expected_keywords: list[str],
) -> bool:
    """Check if a retrieved RAG passage is genuinely relevant to the evaluation target."""
    chunk_section = str(chunk.get("section", "")).strip().lower()
    chunk_text = str(chunk.get("text", "")).strip().lower()

    if expected_sections and any(
        exp.strip().lower() in chunk_section or chunk_section in exp.strip().lower()
        for exp in expected_sections
        if exp.strip()
    ):
        return True

    if expected_keywords and any(
        kw.strip().lower() in chunk_text
        for kw in expected_keywords
        if kw.strip()
    ):
        return True

    return False


def _parse_list(val: Any) -> list[str]:
    """Parse comma, semicolon, or pipe delimited strings into a clean list."""
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    if isinstance(val, str) and val.strip():
        parts = re.split(r"[;|]", val) if (";" in val or "|" in val) else val.split(",")
        return [p.strip() for p in parts if p.strip()]
    return []


def _parse_bool(val: Any) -> bool:
    """Parse common truthy/falsy string representations."""
    if isinstance(val, bool):
        return val
    s = str(val or "").strip().lower()
    return s in ("true", "1", "yes", "y", "t", "escalate")


def load_dataset(file_path: Path) -> list[dict[str, Any]]:
    """Load benchmark records from JSON, JSONL, or CSV with ORDS/MobiFix mapping.

    Explicitly differentiates raw consumer problem descriptions from verified
    diagnosis ground-truth labels.
    """
    suffix = file_path.suffix.lower()
    records: list[dict[str, Any]] = []

    if suffix == ".csv":
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, start=1):
                raw_cat = row.get("expected_fault_category") or row.get("fault_category")
                has_label = bool(raw_cat and raw_cat.strip())
                expected_cat = raw_cat.strip().lower() if has_label else None

                records.append({
                    "scenario_id": row.get("scenario_id") or row.get("id") or f"CSV_ROW_{idx}",
                    "brand": row.get("brand") or "",
                    "model": row.get("model") or row.get("model_name") or "",
                    "variant": row.get("variant") or "",
                    "category": row.get("category") or "unspecified",
                    "description": row.get("description") or "",
                    "input_query": row.get("input_query") or row.get("problem") or row.get("description") or row.get("fault") or "",
                    "expected_fault_category": expected_cat,
                    "has_ground_truth_label": has_label,
                    "expected_safety_escalation": _parse_bool(row.get("expected_safety_escalation") or row.get("safety_escalation")),
                    "expected_safety_code": row.get("expected_safety_code") or "",
                    "expected_target_sections": _parse_list(row.get("expected_target_sections")),
                    "expected_target_keywords": _parse_list(row.get("expected_target_keywords")),
                    "repair_status": row.get("repair_status", ""),
                })
    elif suffix == ".jsonl":
        with open(file_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                raw_cat = row.get("expected_fault_category") or row.get("fault_category")
                has_label = bool(raw_cat and str(raw_cat).strip())
                row["has_ground_truth_label"] = has_label
                row["expected_fault_category"] = str(raw_cat).strip().lower() if has_label else None
                row.setdefault("scenario_id", f"JSONL_ROW_{idx}")
                records.append(row)
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            raw_list = data if isinstance(data, list) else data.get("records", [])
            for idx, row in enumerate(raw_list, start=1):
                raw_cat = row.get("expected_fault_category") or row.get("fault_category")
                has_label = bool(raw_cat and str(raw_cat).strip())
                row["has_ground_truth_label"] = has_label
                row["expected_fault_category"] = str(raw_cat).strip().lower() if has_label else None
                row.setdefault("scenario_id", f"JSON_ROW_{idx}")
                records.append(row)

    return records


def evaluate_benchmark(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Run in-process multi-agent integration benchmark over loaded records."""
    all_phones = load_phones()
    vector_store = get_vector_store()

    group_a_results: list[dict[str, Any]] = []
    group_b_results: list[dict[str, Any]] = []
    group_c_results: list[dict[str, Any]] = []

    y_true: list[str] = []
    y_pred: list[str] = []
    safety_true: list[bool] = []
    safety_pred: list[bool] = []

    per_class_tp: dict[str, int] = defaultdict(int)
    per_class_fp: dict[str, int] = defaultdict(int)
    per_class_fn: dict[str, int] = defaultdict(int)

    unlabelled_count = 0

    proprietary_terms = [
        "ceramic shield", "tensor g3", "exynos 1480", "true tone",
        "super retina xdr", "stretch-release adhesive", "sub-pba daughterboard"
    ]

    for r in records:
        scenario_id = r.get("scenario_id", f"SCN_{len(group_a_results)+1}")
        category_tag = str(r.get("category", "")).lower()
        brand = str(r.get("brand", "")).strip()
        model = str(r.get("model", "")).strip()
        variant = str(r.get("variant", "")).strip().casefold()
        query = (r.get("input_query") or r.get("problem") or "").strip()

        has_label = bool(r.get("has_ground_truth_label", True))
        expected_cat = r.get("expected_fault_category")
        expected_safety = bool(r.get("expected_safety_escalation", False))

        supported = is_supported_model(brand, model)

        # 1. Disambiguated Device Matching
        match = match_device(brand, model, all_phones) if (brand and model) else {
            "options": [], "suggestions": [], "match_status": "not_found", "was_corrected": False
        }

        matched_id = None
        user_confirmed = False
        if match.get("options") and supported:
            selected = None
            if variant:
                for opt in match["options"]:
                    lbl = str(opt.get("label", "")).casefold()
                    oid = str(opt.get("id", "")).casefold()
                    if variant in lbl or variant in oid:
                        selected = opt
                        break
            if not selected:
                for opt in match["options"]:
                    p = opt.get("phone", {})
                    if _matches_model_strictly(brand, model, p.get("brand", ""), p.get("model", "")):
                        selected = opt
                        break
            if not selected and match["options"]:
                selected = match["options"][0]

            if selected:
                matched_id = selected["id"]
                user_confirmed = True
                conf = build_confirmation(match, matched_id, user_confirmed=True, manual_ok=False)
            else:
                conf = build_confirmation(match, None, user_confirmed=False, manual_ok=True)
        else:
            conf = build_confirmation(match, None, user_confirmed=False, manual_ok=True)

        state: dict[str, Any] = {
            "old_device": {
                "brand": brand,
                "model": model,
                "variant": variant,
                "fault": query,
                "matched_id": matched_id,
                "profile_confirmed": bool(matched_id and supported),
                "raw_brand": brand,
                "raw_model": model,
            },
            "issue_description": query,
            "device_confirmation": conf,
        }

        # 2. Run Fault Diagnosis Agent (Group A: All phones)
        diag_res = diagnosis.run(state, None)
        diag = diag_res.get("diagnosis", {})
        predicted_cat = diag.get("fault_category", "unclear")
        safety_flags = diag_res.get("safety_flags", [])

        # 3. Run Troubleshooting Agent
        state["diagnosis"] = diag
        state["safety_flags"] = safety_flags
        tb_res = troubleshooting.run(state)
        escalate = tb_res.get("troubleshooting", {}).get("escalate_to_technician", False)
        actual_safety = bool(escalate or safety_flags)

        cat_match = None
        if has_label and expected_cat:
            cat_match = (predicted_cat == expected_cat)
            y_true.append(expected_cat)
            y_pred.append(predicted_cat)

            if cat_match:
                per_class_tp[expected_cat] += 1
            else:
                per_class_fp[predicted_cat] += 1
                per_class_fn[expected_cat] += 1
        else:
            unlabelled_count += 1

        safety_true.append(expected_safety)
        safety_pred.append(actual_safety)

        record_entry = {
            "scenario_id": scenario_id,
            "device": f"{brand} {model}".strip() or "Unspecified",
            "is_supported": supported,
            "query": query,
            "has_label": has_label,
            "expected_cat": expected_cat or "(Unlabelled)",
            "predicted_cat": predicted_cat,
            "cat_match": cat_match,
            "expected_safety": expected_safety,
            "actual_safety": actual_safety,
            "safety_match": (expected_safety == actual_safety),
        }
        group_a_results.append(record_entry)

        # 4. Group B: Supported Models - Hit@K, Genuine Recall@K & MRR
        if supported and ("group_b" in category_tag or category_tag == "supported_model"):
            expected_sections = _parse_list(r.get("expected_target_sections", []))
            expected_keywords = _parse_list(r.get("expected_target_keywords", []))

            rag_res = datasheet_rag.run(state, None)
            spec_answers = rag_res.get("spec_answers", [])
            state["spec_answers"] = spec_answers

            cost_res = repair_cost.run(state, None)
            estimate = cost_res.get("repair_cost_estimate") or {}
            has_price = estimate.get("min_lkr") is not None

            # Retrieve top 5 passages directly to compute ranks
            top_passages = vector_store.search(
                query=f"{query} {predicted_cat}",
                brand=brand,
                model=model,
                component=predicted_cat,
                top_k=5,
            )

            # Total relevant passages in entire vector store for this topic
            total_relevant_in_corpus = sum(
                1 for c in vector_store.chunks
                if _matches_model_strictly(brand, model, c.get("brand", ""), c.get("model", ""), c.get("model_identifiers", ""))
                and is_chunk_relevant(c, expected_sections, expected_keywords)
            )

            first_relevant_rank = None
            relevant_retrieved_at_k = {1: 0, 3: 0, 5: 0}

            for rank_idx, chunk in enumerate(top_passages, start=1):
                if is_chunk_relevant(chunk, expected_sections, expected_keywords):
                    if first_relevant_rank is None:
                        first_relevant_rank = rank_idx
                    if rank_idx <= 1:
                        relevant_retrieved_at_k[1] += 1
                    if rank_idx <= 3:
                        relevant_retrieved_at_k[3] += 1
                    if rank_idx <= 5:
                        relevant_retrieved_at_k[5] += 1

            reciprocal_rank = (1.0 / first_relevant_rank) if first_relevant_rank else 0.0

            # Genuine Recall@K = |Relevant retrieved in top K| / |Total relevant in corpus|
            recall_1 = (relevant_retrieved_at_k[1] / total_relevant_in_corpus) if total_relevant_in_corpus > 0 else 1.0
            recall_3 = (relevant_retrieved_at_k[3] / total_relevant_in_corpus) if total_relevant_in_corpus > 0 else 1.0
            recall_5 = (relevant_retrieved_at_k[5] / total_relevant_in_corpus) if total_relevant_in_corpus > 0 else 1.0

            b_entry = {
                **record_entry,
                "specs_retrieved": len(spec_answers),
                "total_relevant_in_corpus": total_relevant_in_corpus,
                "first_relevant_rank": first_relevant_rank,
                "reciprocal_rank": reciprocal_rank,
                "hit_at_1": (first_relevant_rank == 1),
                "hit_at_3": (first_relevant_rank is not None and first_relevant_rank <= 3),
                "hit_at_5": (first_relevant_rank is not None and first_relevant_rank <= 5),
                "recall_at_1": recall_1,
                "recall_at_3": recall_3,
                "recall_at_5": recall_5,
                "has_catalog_price": has_price,
                "price_source": estimate.get("source", "N/A"),
            }
            group_b_results.append(b_entry)

        # 5. Group C: Unsupported & Near-Miss Models - Fail-Closed Gating
        if not supported and ("group_c" in category_tag or category_tag == "unsupported_model" or "near_miss" in category_tag):
            rag_res = datasheet_rag.run(state, None)
            specs = rag_res.get("spec_answers", [])
            state["spec_answers"] = specs

            cost_res = repair_cost.run(state, None)
            estimate = cost_res.get("repair_cost_estimate") or {}
            has_price = estimate.get("min_lkr") is not None

            state["diagnosis"] = diag
            state["repair_cost_estimate"] = estimate
            state["recommendations"] = []
            exp_res = explanation.run(state, None)
            explanation_text = str(exp_res.get("explanation", "")).lower()

            leaked_terms = [t for t in proprietary_terms if t in explanation_text]

            # Numerical hardware claims check (detect invented battery capacity or prices)
            invented_specs = []
            if re.search(r"\b\d{4}\s*mah\b", explanation_text):
                invented_specs.append("battery_capacity_mah")
            if re.search(r"\blkr\s*[\d,]+\b", explanation_text):
                invented_specs.append("price_quotation_lkr")

            near_miss_rejected = not match.get("was_corrected", False) and (len(match.get("options", [])) == 0)
            specs_rejected = (len(specs) == 0)
            price_rejected = (not has_price) and (estimate.get("status") == "unavailable")

            fail_closed_safe = (
                near_miss_rejected
                and specs_rejected
                and price_rejected
                and len(leaked_terms) == 0
                and len(invented_specs) == 0
            )

            c_entry = {
                **record_entry,
                "near_miss_rejected": near_miss_rejected,
                "specs_rejected": specs_rejected,
                "price_rejected": price_rejected,
                "specs_count": len(specs),
                "price_min": estimate.get("min_lkr"),
                "leaked_terms": leaked_terms,
                "invented_specs": invented_specs,
                "fail_closed_safe": fail_closed_safe,
                "status_message": estimate.get("message") or estimate.get("status"),
            }
            group_c_results.append(c_entry)

    # Group A Metrics (Supervised only)
    labelled_total = len(y_true)
    diag_accuracy = (
        sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp) / labelled_total
        if labelled_total > 0 else 0.0
    )

    categories = sorted(set(y_true) | set(y_pred))
    class_metrics: dict[str, dict[str, float]] = {}
    f1_scores: list[float] = []

    for cat in categories:
        tp = per_class_tp[cat]
        fp = per_class_fp[cat]
        fn = per_class_fn[cat]
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * p * rec) / (p + rec) if (p + rec) > 0 else 0.0
        class_metrics[cat] = {
            "precision": round(p, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "support": sum(1 for yt in y_true if yt == cat),
        }
        f1_scores.append(f1)

    macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0

    # Safety Metrics (Recall, Precision, FPR)
    safety_positives = sum(1 for st in safety_true if st)
    safety_negatives = sum(1 for st in safety_true if not st)
    safety_tp = sum(1 for st, sp in zip(safety_true, safety_pred) if st and sp)
    safety_fp = sum(1 for st, sp in zip(safety_true, safety_pred) if not st and sp)
    safety_fn = sum(1 for st, sp in zip(safety_true, safety_pred) if st and not sp)
    safety_tn = sum(1 for st, sp in zip(safety_true, safety_pred) if not st and not sp)

    safety_recall = (safety_tp / safety_positives) if safety_positives > 0 else None
    safety_precision = (safety_tp / (safety_tp + safety_fp)) if (safety_tp + safety_fp) > 0 else None
    safety_fpr = (safety_fp / safety_negatives) if safety_negatives > 0 else 0.0

    # Group B Metrics (IR: Hit@K, Recall@K, MRR)
    total_b = len(group_b_results)
    b_mrr = sum(b["reciprocal_rank"] for b in group_b_results) / total_b if total_b > 0 else 0.0
    b_hit_1 = sum(1 for b in group_b_results if b["hit_at_1"]) / total_b if total_b > 0 else 0.0
    b_hit_3 = sum(1 for b in group_b_results if b["hit_at_3"]) / total_b if total_b > 0 else 0.0
    b_hit_5 = sum(1 for b in group_b_results if b["hit_at_5"]) / total_b if total_b > 0 else 0.0
    b_rec_1 = sum(b["recall_at_1"] for b in group_b_results) / total_b if total_b > 0 else 0.0
    b_rec_3 = sum(b["recall_at_3"] for b in group_b_results) / total_b if total_b > 0 else 0.0
    b_rec_5 = sum(b["recall_at_5"] for b in group_b_results) / total_b if total_b > 0 else 0.0
    b_price_coverage = sum(1 for b in group_b_results if b["has_catalog_price"]) / total_b if total_b > 0 else 0.0

    # Group C Metrics (Gating & Isolation)
    total_c = len(group_c_results)
    c_fail_closed_rate = sum(1 for c in group_c_results if c["fail_closed_safe"]) / total_c if total_c > 0 else 1.0
    c_near_miss_rejection = sum(1 for c in group_c_results if c["near_miss_rejected"]) / total_c if total_c > 0 else 1.0
    c_spec_rejection = sum(1 for c in group_c_results if c["specs_rejected"]) / total_c if total_c > 0 else 1.0
    c_price_rejection = sum(1 for c in group_c_results if c["price_rejected"]) / total_c if total_c > 0 else 1.0

    return {
        "group_a": {
            "total_records": len(group_a_results),
            "labelled_evaluated": labelled_total,
            "unlabelled_evaluated": unlabelled_count,
            "accuracy": round(diag_accuracy, 4),
            "macro_f1": round(macro_f1, 4),
            "safety_recall": round(safety_recall, 4) if safety_recall is not None else None,
            "safety_precision": round(safety_precision, 4) if safety_precision is not None else None,
            "safety_fpr": round(safety_fpr, 4),
            "per_class": class_metrics,
            "records": group_a_results,
        },
        "group_b": {
            "total": total_b,
            "mrr": round(b_mrr, 4),
            "hit_at_1": round(b_hit_1, 4),
            "hit_at_3": round(b_hit_3, 4),
            "hit_at_5": round(b_hit_5, 4),
            "recall_at_1": round(b_rec_1, 4),
            "recall_at_3": round(b_rec_3, 4),
            "recall_at_5": round(b_rec_5, 4),
            "price_coverage": round(b_price_coverage, 4),
            "records": group_b_results,
        },
        "group_c": {
            "total": total_c,
            "near_miss_rejection_rate": round(c_near_miss_rejection, 4),
            "unsupported_spec_rejection_rate": round(c_spec_rejection, 4),
            "unsupported_price_rejection_rate": round(c_price_rejection, 4),
            "fail_closed_gating_rate": round(c_fail_closed_rate, 4),
            "records": group_c_results,
        },
    }


def format_markdown_report(report: dict[str, Any]) -> str:
    """Format academic evaluation report across Groups A, B, and C."""
    a = report["group_a"]
    b = report["group_b"]
    c = report["group_c"]

    md = []
    md.append("# REVIVAI In-Process Multi-Agent Integration Benchmark Report\n")
    md.append("Structured evaluation following the three-group research methodology:")
    md.append(f"- **Group A (General Diagnosis - All Phones):** {a['total_records']} total records ({a['labelled_evaluated']} labelled, {a['unlabelled_evaluated']} unlabelled)")
    md.append(f"- **Group B (Supported Models - Indexed RAG):** {b['total']} records evaluated")
    md.append(f"- **Group C (Unsupported & Near-Miss Models):** {c['total']} records evaluated\n")

    md.append("## 1. Group A: General Symptom Diagnosis (All Phone Brands & Models)")
    md.append(f"* **Diagnostic Accuracy (Labelled Subset):** {a['accuracy'] * 100:.2f}% (on {a['labelled_evaluated']} curated cases)")
    md.append(f"* **Macro F1 Score:** {a['macro_f1']:.4f}")
    if a["safety_recall"] is not None:
        md.append(f"* **Safety Hazard Recall:** {a['safety_recall'] * 100:.2f}%")
        md.append(f"* **Safety Hazard Precision:** {a['safety_precision'] * 100:.2f}%" if a["safety_precision"] is not None else "* **Safety Precision:** N/A")
        md.append(f"* **Safety False Positive Rate (FPR):** {a['safety_fpr'] * 100:.2f}%\n")
    else:
        md.append("* **Safety Hazard Metrics:** N/A (no positive safety examples in dataset)\n")

    md.append("| Fault Category | Support | Precision | Recall | F1 Score |")
    md.append("| :--- | :--- | :--- | :--- | :--- |")
    for cat, m in a["per_class"].items():
        md.append(f"| `{cat}` | {m['support']} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} |")

    md.append("\n## 2. Group B: Supported Model Evaluation (Information Retrieval & Sourced Pricing)")
    md.append(f"* **Mean Reciprocal Rank (MRR):** {b['mrr']:.4f}")
    md.append(f"* **Hit@1 (Success@1):** {b['hit_at_1'] * 100:.2f}%")
    md.append(f"* **Hit@3 (Success@3):** {b['hit_at_3'] * 100:.2f}%")
    md.append(f"* **Hit@5 (Success@5):** {b['hit_at_5'] * 100:.2f}%")
    md.append(f"* **Recall@1:** {b['recall_at_1'] * 100:.2f}%")
    md.append(f"* **Recall@3:** {b['recall_at_3'] * 100:.2f}%")
    md.append(f"* **Recall@5:** {b['recall_at_5'] * 100:.2f}%")
    md.append(f"* **Catalog Pricing Availability:** {b['price_coverage'] * 100:.2f}%\n")

    if b["records"]:
        md.append("| Device | Issue Description | 1st Rel. Rank | RR | Hit@1 | Corpus Recall@3 | Sourced Price |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for rec in b["records"]:
            q_short = (rec["query"][:30] + "...") if len(rec["query"]) > 30 else rec["query"]
            rank_str = str(rec["first_relevant_rank"]) if rec["first_relevant_rank"] else "Miss"
            hit_str = "YES" if rec["hit_at_1"] else "NO"
            md.append(f"| {rec['device']} | \"{q_short}\" | Rank {rank_str} | {rec['reciprocal_rank']:.3f} | {hit_str} | {rec['recall_at_3']*100:.0f}% | {'YES' if rec['has_catalog_price'] else 'NO'} |")

    md.append("\n## 3. Group C: Unsupported & Near-Miss Model Evaluation (Hardware Isolation & Fail-Closed Gating)")
    md.append(f"* **Near-Miss Model Boundary Rejection Rate:** {c['near_miss_rejection_rate'] * 100:.2f}%")
    md.append(f"* **Datasheet Retrieval Rejection Rate:** {c['unsupported_spec_rejection_rate'] * 100:.2f}%")
    md.append(f"* **Pricing Quotation Rejection Rate:** {c['unsupported_price_rejection_rate'] * 100:.2f}%")
    md.append(f"* **Overall Fail-Closed Gating Rate:** {c['fail_closed_gating_rate'] * 100:.2f}%\n")

    if c["records"]:
        md.append("| Device | Reported Issue | Near-Miss Guard | Specs Retrieved | Invented Price | Safe Fail-Closed? |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for rec in c["records"]:
            q_short = (rec["query"][:28] + "...") if len(rec["query"]) > 28 else rec["query"]
            guard_str = "PASS (Rejected)" if rec["near_miss_rejected"] else "FAIL (Misidentified)"
            price_str = "None" if rec["price_min"] is None else f"LKR {rec['price_min']}"
            md.append(f"| {rec['device']} | \"{q_short}\" | {guard_str} | {rec['specs_count']} | {price_str} | {'PASS' if rec['fail_closed_safe'] else 'FAIL'} |")

    md.append("\n## 4. Scientific Limitations & Research Scope")
    md.append("> [!NOTE]")
    md.append("> 1. **Integration Benchmark vs. Empirical Evaluation:** This harness measures in-process multi-agent integration and fail-closed guardrails on a curated functional scenario suite (45 cases across 15 brands). It is complemented by end-to-end API tests in `tests/test_api_e2e.py`. It does not substitute for an empirical field trial on unstructured consumer repair records.")
    md.append("> 2. **Gating vs. Claim Verification:** The Group C metric measures deterministic hardware gating (0 retrieved specs and 0 price quotations for unindexed devices). It does not certify open-domain factual validation of all generative phrasing.")
    md.append("> 3. **Taxonomy & Ingestion:** ORDS/MobiFix descriptions are treated as unconfirmed customer symptoms unless explicitly marked with a verified ground-truth label.")

    return "\n".join(md)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run REVIVAI Multi-Group Benchmark.")
    parser.add_argument(
        "--data",
        type=str,
        default=str(PROJECT_ROOT / "data" / "benchmarks" / "agent_eval" / "scenarios.json"),
        help="Path to JSON, JSONL, or CSV benchmark dataset",
    )
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.is_file():
        sys.exit(f"Benchmark dataset not found: {data_path}")

    records = load_dataset(data_path)
    report = evaluate_benchmark(records)
    print(format_markdown_report(report))


if __name__ == "__main__":
    main()

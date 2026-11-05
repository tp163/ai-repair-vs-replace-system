"""Retrieve model-specific datasheet excerpts for a confirmed device."""
from __future__ import annotations

from typing import Any

from ..rag import query_datasheet_rag
from ..state import AgentState, SpecAnswer


def run(state: AgentState, llm: Any = None) -> dict[str, Any]:
    old_device = state.get("old_device", {})
    confirmation = state.get("device_confirmation", {})
    brand = str(old_device.get("brand", "")).strip()
    model = str(old_device.get("model", "")).strip()
    fault = str(state.get("issue_description", "") or old_device.get("fault", "")).strip()
    diagnosis = state.get("diagnosis", {})
    fault_category = str(diagnosis.get("fault_category", "")).strip()

    identity_confirmed = (
        bool(confirmation.get("confirmed"))
        and not bool(confirmation.get("unverified"))
        and bool(confirmation.get("matched_id"))
        and confirmation.get("matched_id") == old_device.get("matched_id")
    )
    retrieved = []
    if identity_confirmed:
        retrieved = query_datasheet_rag(
            brand=brand,
            model=model,
            query=f"{fault} {fault_category}".strip(),
            component=fault_category,
            top_k=2,
        )

    spec_answers: list[SpecAnswer] = []
    for chunk in retrieved:
        spec_answers.append({
            "question": f"Source excerpt for {brand} {model} ({chunk.get('section', '')})",
            "answer": chunk.get("text", "").strip(),
            "sources": [
                {
                    "doc": source.get("doc", "Datasheet source"),
                    "source_url": source.get("source_url", ""),
                    "section": chunk.get("section", ""),
                    "chunk_id": chunk.get("chunk_id", ""),
                    "score": chunk.get("score", 0.0),
                    "citation": chunk.get("citation", ""),
                    "date_verified": chunk.get("date_verified", ""),
                    "component": chunk.get("component", ""),
                }
                for source in chunk.get("sources", [{
                    "doc": chunk.get("source_title", "Datasheet source"),
                    "source_url": chunk.get("source_url", ""),
                }])
            ],
        })

    trace_entry = {
        "agent": "DatasheetRAGAgent",
        "action": (
            f"retrieved {len(retrieved)} datasheet source section(s) for confirmed device {brand} {model}"
            if retrieved else (
                f"skipped datasheet retrieval because device identity is unconfirmed ({brand} {model})"
                if not identity_confirmed else f"no matching datasheet section for {brand} {model}"
            )
        ),
        "details": {
            "device": f"{brand} {model}".strip(),
            "identity_confirmed": identity_confirmed,
            "query": fault,
            "citations": [c.get("citation", "") for c in retrieved],
            "source_urls": [c.get("source_url", "") for c in retrieved],
            "chunk_ids": [c.get("chunk_id", "") for c in retrieved],
        },
    }

    updated_diagnosis = dict(diagnosis)
    if retrieved:
        updated_diagnosis["technical_specs"] = retrieved[0].get("text", "").strip()
        updated_diagnosis["spec_citation"] = retrieved[0].get("citation", "")
        updated_diagnosis["spec_source_url"] = retrieved[0].get("source_url", "")
    else:
        # Clear out if unsupported
        updated_diagnosis.pop("technical_specs", None)
        updated_diagnosis.pop("spec_citation", None)
        updated_diagnosis.pop("spec_source_url", None)

    return {
        "spec_answers": spec_answers,
        "diagnosis": updated_diagnosis,
        "trace": state.get("trace", []) + [trace_entry],
    }

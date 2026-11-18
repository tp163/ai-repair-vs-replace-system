from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class DiagnoseRequest(BaseModel):
    query: str
    brand: str
    model: str
    variant: str = ""
    budget_lkr: float | None = None
    image_data_uri: str | None = None

@app.post("/api/diagnose")
def diagnose_device(req: DiagnoseRequest):
    from src.graph import run_pipeline
    from src.dataset import load_phones
    from src.device_match import match_device, build_confirmation

    issue = req.query.strip()
    if not req.brand.strip() or not req.model.strip() or not (issue or req.image_data_uri):
        raise HTTPException(status_code=422, detail="Enter a brand, model, and symptoms or a photo.")

    brand = req.brand.strip()
    model = req.model.strip()
    variant = req.variant.strip()

    try:
        phones = load_phones()
        match = match_device(brand, model, phones)
    except Exception:
        match = {"options": [], "suggestions": [], "match_status": "unverified", "was_corrected": False}

    if match.get("options"):
        selected_option = match["options"][0]
        if variant:
            for opt in match["options"]:
                if variant.casefold() in opt.get("label", "").casefold() or variant.casefold() in opt.get("id", "").casefold():
                    selected_option = opt
                    break
        selected_id = selected_option["id"]
        confirmation = build_confirmation(match, selected_id, user_confirmed=True, manual_ok=False)
        canonical_phone = selected_option.get("phone", {})
        canonical_brand = canonical_phone.get("brand", brand)
        canonical_model = canonical_phone.get("model", model)
    else:
        confirmation = build_confirmation(match, None, user_confirmed=False, manual_ok=True)
        canonical_brand = brand
        canonical_model = model

    old_device = {
        "brand": canonical_brand,
        "model": canonical_model,
        "variant": variant or confirmation.get("matched_id", ""),
        "fault": issue,
        "profile_confirmed": confirmation.get("confirmed", True),
        "matched_id": confirmation.get("matched_id"),
        "match_status": confirmation.get("match_status", "unverified"),
        "was_corrected": match.get("was_corrected", False),
        "raw_brand": brand,
        "raw_model": model,
    }

    final_state = run_pipeline(
        old_device=old_device,
        user_needs="",
        budget_lkr=req.budget_lkr,
        issue_description=issue,
        image_data_uri=req.image_data_uri,
        device_confirmation=confirmation,
    )

    raw_specs = final_state.get("spec_answers", []) or []
    formatted_specs = []
    for s in raw_specs:
        sources = s.get("sources", [])
        src_url = sources[0].get("source_url", "") if sources else s.get("source_url", "")
        src_doc = sources[0].get("doc", "") if sources else s.get("source", "")
        sec = sources[0].get("section", "") if sources else s.get("section", "")
        chk = sources[0].get("date_verified", "") if sources else s.get("retrieved_at", "")
        citation = sources[0].get("citation", "") if sources else ""
        source_status = sources[0].get("verification_status", "linked_unverified") if sources else "linked_unverified"
        source_scope = sources[0].get("source_scope", "section") if sources else "section"
        formatted_specs.append({
            "question": s.get("question", ""),
            "answer": s.get("answer", ""),
            "source_url": src_url,
            "source": src_doc,
            "section": sec,
            "retrieved_at": chk,
            "citation": citation,
            "source_verification_status": source_status,
            "source_scope": source_scope,
        })

    matched_device_info = {
        "brand": canonical_brand,
        "model": canonical_model,
        "canonical_name": f"{canonical_brand} {canonical_model}".strip(),
        "was_corrected": bool(match.get("was_corrected", False)),
        "confidence": float(match.get("confidence", 1.0 if match.get("options") else 0.0)),
        "original_input": f"{brand} {model}".strip(),
        "matched_id": confirmation.get("matched_id"),
        "match_status": confirmation.get("match_status", "unverified"),
    }

    return {
        "status": "success",
        "matched_device": matched_device_info,
        "diagnosis": final_state.get("diagnosis"),
        "safety_flags": final_state.get("safety_flags", []),
        "repair_cost": final_state.get("repair_cost_estimate"),
        "decision": final_state.get("decision"),
        "spec_answers": formatted_specs,
        "troubleshooting": final_state.get("troubleshooting"),
        "recommendations": final_state.get("recommendations", []),
        "explanation": final_state.get("explanation"),
    }

if __name__ == "__main__":
    import uvicorn

    backend_dir = Path.cwd()
    if not (backend_dir / "src" / "graph.py").is_file():
        sys.exit("Run this script from the old Python project folder that contains src/graph.py.")

    sys.path.insert(0, str(backend_dir))
    uvicorn.run(app, host="127.0.0.1", port=8000)

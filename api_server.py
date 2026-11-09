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
    image_data_uri: str | None = None

@app.post("/api/diagnose")
def diagnose_device(req: DiagnoseRequest):
    from src.graph import run_pipeline

    issue = req.query.strip()
    if not req.brand.strip() or not req.model.strip() or not (issue or req.image_data_uri):
        raise HTTPException(status_code=422, detail="Enter a brand, model, and symptoms or a photo.")

    final_state = run_pipeline(
        old_device={
            "brand": req.brand.strip(),
            "model": req.model.strip(),
            "variant": req.variant.strip(),
            "fault": issue,
            "profile_confirmed": True,
        },
        user_needs="",
        issue_description=issue,
        image_data_uri=req.image_data_uri,
        device_confirmation={"confirmed": True},
    )

    return {
        "status": "success",
        "diagnosis": final_state.get("diagnosis"),
        "safety_flags": final_state.get("safety_flags", []),
        "repair_cost": final_state.get("repair_cost_estimate"),
        "recommendations": final_state.get("recommendations", []),
    }

if __name__ == "__main__":
    import uvicorn

    backend_dir = Path.cwd()
    if not (backend_dir / "src" / "graph.py").is_file():
        sys.exit("Run this script from the old Python project folder that contains src/graph.py.")

    # Load the original project before the copy of src beside this script.
    sys.path.insert(0, str(backend_dir))
    uvicorn.run(app, host="127.0.0.1", port=8000)

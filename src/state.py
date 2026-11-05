"""Shared state schema for the multi-agent graph.

Every agent reads what it needs from this state and returns only the fields
it updates. The ``trace`` list records each agent's actions in order, which
is what makes the collaboration observable in the UI and in the dissertation
(directly evidencing multi-agent information exchange).

Hand-off contract between Person A (diagnosis/repair) and Person B
(replacement recommendation):

  A writes:  old_device (confirmed), device_confirmation, diagnosis,
             troubleshooting, repair_cost_estimate, safety_flags
  B reads:   old_device, diagnosis, repair_cost_estimate, decision
  B writes:  everything under "Person B outputs"

Existing keys are unchanged so current agents keep working. New keys are
additive and optional (total=False).
"""
from __future__ import annotations

from typing import Literal, TypedDict


# --------------------------------------------------------------------------
# Sub-schemas (documentation + type hints for the dicts stored in the state)
# --------------------------------------------------------------------------

class DeviceConfirmation(TypedDict, total=False):
    """Written by the Device Confirmation step (Person A, 5.1)."""
    confirmed: bool                 # analysis is blocked until this is True
    match_status: Literal["exact", "multiple_variants", "not_found"]
    matched_id: str | None          # id of the catalogue row the user confirmed
    options: list[dict]             # variants shown to the user to pick from
    specs_shown: dict               # specs displayed at confirmation time


class Diagnosis(TypedDict, total=False):
    """Written by the Fault Diagnosis Agent (Person A, 5.2)."""
    fault_category: str             # one of the fixed fault list
    confidence: Literal["low", "medium", "high"]  # "low" | "medium" | "high"
    method: Literal["llm", "rules", "image", "llm+image"]
    alternatives: list[dict]        # [{"fault_category", "confidence"}]
    image_findings: dict            # {"label", "confidence", "model"} or {}
    needs_more_info: bool           # True -> ask the user a follow-up
    follow_up_questions: list[str]


class TroubleshootingStep(TypedDict, total=False):
    order: int
    text: str
    risk: Literal["safe", "caution", "technician_only"]
    resources: list[dict]           # [{"title","url","source","type"}]
    requires_opening_device: bool
    requires_soldering: bool


class Troubleshooting(TypedDict, total=False):
    """Written by the Troubleshooting Agent (Person A, 5.2)."""
    steps: list[TroubleshootingStep]
    escalate_to_technician: bool    # hard rule: swelling, liquid, heat, opening
    escalation_reason: str


class SafetyFlag(TypedDict, total=False):
    code: str                       # e.g. "swollen_battery", "liquid_damage"
    severity: Literal["warning", "stop"]
    message: str


class RepairCostEstimate(TypedDict, total=False):
    """Written by the Repair Cost Agent (Person A, 5.4).

    Shown only when a sourced row exists; otherwise status="unavailable" and
    the UI asks the user for a local quote.
    """
    status: Literal["available", "unavailable"]
    kind: Literal["estimate", "quotation"]   # estimate vs. user-supplied quote
    fault_category: str
    min_lkr: float | None
    max_lkr: float | None
    source: str | None
    source_url: str | None
    retrieved_at: str | None        # ISO date, e.g. "2026-10-30"
    note: str


class SpecAnswer(TypedDict, total=False):
    """Written by the Datasheet RAG step (Person A, 5.3)."""
    question: str
    answer: str
    sources: list[dict]             # [{"doc","page","chunk_id","score"}]


# --------------------------------------------------------------------------
# Main state
# --------------------------------------------------------------------------

class AgentState(TypedDict, total=False):
    # ---- inputs (from the user / upstream diagnosis module) ----
    old_device: dict          # e.g. {"brand","model","variant","year","condition","fault"}
    user_needs: str           # free text: "good camera, long battery, under 100k"
    budget_lkr: float | None
    issue_description: str
    image_data_uri: str | None

    # ---- Person A outputs (diagnosis and repair) ----
    device_confirmation: DeviceConfirmation  # Device Confirmation -> variant check, gates analysis
    diagnosis: dict           # Fault Diagnosis Agent -> probable fault and confidence (see Diagnosis)
    troubleshooting: dict     # Troubleshooting Agent -> safe actions and escalation (see Troubleshooting)
    safety_flags: list[SafetyFlag]  # any agent -> warnings/stops surfaced to the UI
    spec_answers: list[SpecAnswer]  # Datasheet RAG -> sourced answers about the device
    repair_cost_estimate: dict  # Repair Cost Agent -> sourced range or unavailable status

    # ---- Person B outputs (replacement recommendation) ----
    requirements: dict        # User Requirement Agent -> structured profile
    old_device_profile: dict  # Device Profiling Agent -> assessed condition/value
    decision: dict            # Decision Agent -> repair/replacement path assessment
    candidates: list[dict]    # Specification Retrieval Agent -> candidate pool
    similarity: dict          # Similarity Agent -> similarity scores by product id
    budget_analysis: dict     # Budget Agent -> in-budget candidates and constraints
    market_info: dict         # Market Research Agent -> prices + availability
    comparisons: list[dict]   # Comparison Agent -> scored candidate evaluations
    recommendations: list[dict]  # Recommendation Agent -> top-k picks
    recommendation_categories: dict  # Recommendation Agent -> categorized alternatives
    verification: dict        # Verification Agent -> fact-check report
    explanation: str          # Explanation Agent -> final natural-language output

    # ---- observability ----
    trace: list[dict]         # [{"agent","action","details"}] in execution order
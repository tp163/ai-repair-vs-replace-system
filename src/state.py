"""Shared state schema for the multi-agent graph.

Every agent reads what it needs from this state and returns only the fields
it updates. The ``trace`` list records each agent's actions in order, which
is what makes the collaboration observable in the UI and in the dissertation
(directly evidencing multi-agent information exchange).
"""
from __future__ import annotations

from typing import TypedDict


class AgentState(TypedDict, total=False):
    # ---- inputs (from the user / upstream diagnosis module) ----
    old_device: dict          # e.g. {"brand","model","variant","year","condition","fault"}
    user_needs: str           # free text: "good camera, long battery, under 100k"
    budget_lkr: float | None
    issue_description: str
    image_data_uri: str | None

    # ---- agent outputs ----
    requirements: dict        # User Requirement Agent -> structured profile
    diagnosis: dict           # Fault Diagnosis Agent -> probable fault and confidence
    troubleshooting: dict     # Troubleshooting Agent -> safe actions and escalation
    old_device_profile: dict  # Device Profiling Agent -> assessed condition/value
    repair_cost_estimate: dict  # Repair Cost Agent -> sourced range or unavailable status
    decision: dict            # Decision Agent -> repair/replacement path assessment
    candidates: list[dict]    # Specification Retrieval Agent -> candidate pool
    similarity: dict         # Similarity Agent -> similarity scores by product id
    budget_analysis: dict    # Budget Agent -> in-budget candidates and constraints
    market_info: dict         # Market Research Agent -> prices + availability
    comparisons: list[dict]   # Comparison Agent -> scored candidate evaluations
    recommendations: list[dict]  # Recommendation Agent -> top-k picks
    recommendation_categories: dict  # Recommendation Agent -> categorized alternatives
    verification: dict        # Verification Agent -> fact-check report
    explanation: str          # Explanation Agent -> final natural-language output

    # ---- observability ----
    trace: list[dict]         # [{"agent","action","details"}] in execution order

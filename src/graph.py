"""LangGraph orchestration of the recommendation agents.

The graph is a linear pipeline over shared state — each agent reads its
inputs from state, writes its outputs back, and appends to ``trace``:

    FaultDiagnosisAgent
        -> TroubleshootingAgent
        -> UserRequirementAgent
        -> DeviceProfilingAgent
        -> RepairCostAgent
        -> RepairDecisionAgent
        -> SpecificationRetrievalAgent
        -> MarketResearchAgent
        -> SimilarityAgent
        -> BudgetAgent
        -> ComparisonAgent
        -> RecommendationAgent
        -> VerificationAgent
        -> ExplanationAgent

In LangGraph terms: each agent is a node; ``add_edge`` chains them; state
flows through the graph and accumulates. This linear form is deliberate —
it mirrors the information-dependency structure of the workflow and is easy
to diagram in a report. A supervisor pattern (conditional routing) is a
documented extension point.
"""
from __future__ import annotations

from langgraph.graph import StateGraph, END

from . import llm as llm_module
from .agents import (budget, comparison, decision, diagnosis, explanation, market, profiling,
                     recommendation, requirements, spec_retrieval,
                     repair_cost, similarity, troubleshooting, verification)
from .state import AgentState


def _node(agent_module, llm):
    """Wrap an agent module's run(state, llm) as a LangGraph node, with the
    shared LLM client bound at build time."""
    def fn(state: AgentState) -> dict:
        return agent_module.run(state, llm)
    fn.__name__ = agent_module.__name__
    return fn


def build_graph(llm=None):
    """Compile the multi-agent graph. Pass ``llm`` to override the provider
    (e.g. inject a fake in unit tests)."""
    llm = llm or llm_module.get_llm()
    builder = StateGraph(AgentState)

    # Bind a shared LLM client into every node closure.
    nodes = {
        name: _node(mod, llm)
        for name, mod in [
            ("fault_diagnosis", diagnosis),
            ("troubleshooting", troubleshooting),
            ("user_requirements", requirements),
            ("device_profiling", profiling),
            ("repair_cost", repair_cost),
            ("repair_decision", decision),
            ("spec_retrieval", spec_retrieval),
            ("market_research", market),
            ("similarity", similarity),
            ("budget", budget),
            ("comparison", comparison),
            ("recommendation", recommendation),
            ("verification", verification),
            ("explanation", explanation),
        ]
    }
    for name, fn in nodes.items():
        builder.add_node(name, fn)

    # Linear pipeline in information-dependency order.
    order = ["fault_diagnosis", "troubleshooting", "user_requirements",
             "device_profiling", "repair_cost", "repair_decision", "spec_retrieval",
             "market_research", "similarity", "budget", "comparison", "recommendation",
             "verification", "explanation"]
    builder.set_entry_point(order[0])
    for a, b in zip(order, order[1:]):
        builder.add_edge(a, b)
    builder.add_edge(order[-1], END)

    return builder.compile()


def run_pipeline(old_device: dict, user_needs: str,
                 budget_lkr: float | None = None,
                 issue_description: str = "",
                 image_data_uri: str | None = None) -> AgentState:
    """Run the full multi-agent replacement pipeline and return final state."""
    graph = build_graph()
    initial: AgentState = {
        "old_device": old_device,
        "user_needs": user_needs,
        "budget_lkr": budget_lkr,
        "issue_description": issue_description or old_device.get("fault", ""),
        "image_data_uri": image_data_uri,
        "trace": [],
    }
    return graph.invoke(initial)

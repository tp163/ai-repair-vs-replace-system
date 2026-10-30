"""Agent 8 — Explanation Agent.

Turns the verified recommendations into a user-facing explanation: what to
buy, why it fits, how it compares to the old device, and any caveats
(over-budget picks, demo-data disclaimer). Uses the LLM for fluent prose
when available; otherwise renders a structured template — the facts are
identical either way, only the wording differs.
"""
from __future__ import annotations

from ..state import AgentState


def _fmt_lkr(v):
    if v is None:
        return "n/a"
    return f"LKR {v:,.0f}"


def _template(state: AgentState) -> str:
    recs = state.get("recommendations", [])
    old = state.get("old_device_profile", {})
    req = state.get("requirements", {})
    ver = state.get("verification", {})
    lines = [
        f"Top {len(recs)} recommendations (budget "
        f"{_fmt_lkr(req.get('budget_lkr'))}, priorities: "
        f"{', '.join(req.get('priorities', ['general_use']))}):",
        "",
    ]
    for i, r in enumerate(recs, 1):
        d = r["dimensions"]
        lines.append(
            f"{i}. {r['name']} — {_fmt_lkr(r['price_lkr'])} "
            f"(fit score {r['score']}/100)"
        )
        lines.append(
            f"   strongest in: performance {d['performance']:.2f}, "
            f"camera {d['camera']:.2f}, battery {d['battery']:.2f}; "
            f"price fit {d['price_fit']:.2f}"
            + (" — over budget" if r.get("over_budget") else "")
        )
        if old.get("estimated_residual_lkr"):
            lines.append(
                f"   vs your {old.get('brand')} {old.get('model')} "
                f"(est. residual {_fmt_lkr(old['estimated_residual_lkr'])}): "
                f"{r['verdict_vs_old']}"
            )
    if ver:
        lines += ["", f"Verification: {'all checks passed' if ver['all_passed'] else 'some picks were replaced'} — {ver.get('prices_are', '')}."]
    lines.append("Live market prices were not consulted for these figures.")
    return "\n".join(lines)


def run(state: AgentState, llm) -> dict:
    # Demo mode renders the deterministic template; real LLMs get the
    # fact-grounded prompt. Either way, only verified facts are used.
    if getattr(llm, "name", "") == "demo":
        text = _template(state)
        trace = state.get("trace", []) + [{
            "agent": "ExplanationAgent",
            "action": "generated user-facing explanation (template mode)",
            "details": {"length_chars": len(text)},
        }]
        return {"explanation": text, "trace": trace}

    facts = {
        "recommendations": state.get("recommendations", []),
        "requirements": state.get("requirements", {}),
        "old_device_profile": state.get("old_device_profile", {}),
        "verification": state.get("verification", {}),
    }
    prompt = (
        "Explain these verified phone recommendations to the user in 3 short "
        "paragraphs: what to buy, why each fits their needs and budget, and "
        f"any caveats. Facts (do not invent others):\n{facts}"
    )
    try:
        text = llm.chat(
            "You are a concise, honest phone-buying advisor. Never invent "
            "prices or specs; only use the facts given.", prompt,
        )
        if not text.strip():
            text = _template(state)
    except Exception:
        text = _template(state)

    trace = state.get("trace", []) + [{
        "agent": "ExplanationAgent",
        "action": "generated user-facing explanation",
        "details": {"length_chars": len(text)},
    }]
    return {"explanation": text, "trace": trace}

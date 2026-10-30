# Multi-Agent Phone Replacement & Recommendation System

An AI-assisted phone triage and replacement recommendation prototype. A user
can describe an issue or upload a photo, receive safety-screened first steps,
see a sourced repair-cost range when available, and compare categorized phone
replacement options.

Full proposed architecture (repair vs replace, supervisor, verification,
target tech stack, and implementation status): **[`../SYSTEM_DESIGN.md`](../SYSTEM_DESIGN.md)**.

> Prices in the placeholder dataset are **demo values**, not live retailer
> prices. Replace `data/phones_placeholder.json` with your own dataset.

Repair-cost ranges are optional and shown only when a sourced record is
available. `REPAIR_COST_DATA_PATH` can point to a JSON or CSV file with
`brand`, `model`, `fault_category`, `min_lkr`, `max_lkr`, `source_url`,
`source`, and `retrieved_at` fields. Without a matching source-backed row,
the UI asks the user to request a local quote rather than inventing a price.

## Architecture

```
 user input ──► ┌─────────────────────────── LangGraph state graph ───────────────────────────┐
                │                                                                              │
                │  1 FaultDiagnosisAgent       symptom/photo screening and uncertainty         │
                │  2 TroubleshootingAgent      safe first steps and escalation                  │
                │  3 UserRequirementAgent      free-text needs → structured preference profile │
                │  4 DeviceProfilingAgent      confirmed model → profile and residual value    │
                │  5 RepairCostAgent           sourced estimate or unavailable status          │
                │  6 RepairDecisionAgent       repair / quote / replacement assessment         │
                │  7 SpecificationRetrievalAgent  dataset → candidate pool                    │
                │  8 MarketResearchAgent       dataset prices (+ optional live search)         │
                │  9 SimilarityAgent           compares candidate specs to existing device     │
                │ 10 BudgetAgent               classifies affordability and tolerance          │
                │ 11 ComparisonAgent           weighted multi-criteria scoring                │
                │ 12 RecommendationAgent       budget/similar/improvement/alternative picks   │
                │ 13 VerificationAgent         checks prices/specs and flags uncertainty      │
                │ 14 ExplanationAgent          verified facts → user-facing explanation       │
                │                                                                              │
                └──────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
                              recommendation + score table + agent trace
```

Agents communicate **only through the shared state object** — each reads its
inputs from state, writes its outputs back, and appends to a `trace` list.
The trace is what makes the multi-agent collaboration observable (shown in
the UI and useful as evidence in a dissertation).

### Design decisions worth writing up

* **Hybrid symbolic + LLM agents.** Retrieval, scoring and verification are
  deterministic; the LLM is used for requirement extraction and fluent
  explanation. This keeps the system testable and makes agent behaviour
  reproducible.
* **Separation of dataset and live market signals.** The Market Research
  Agent never blends sources; live-search snippets are attached as
  *unverified evidence* and the Verification Agent sanity-checks them
  (±40% rule) and rejects outliers. This is the system's answer to stale
  prices and hallucinated specs.
* **Verification as a first-class agent.** Failed picks are replaced with
  the next-best verified candidate before anything reaches the user.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # optional; defaults work out of the box
```

**Windows:** If `python` is not found, use the launcher: `py -m pip install -r requirements.txt`.
If global `pip install` fails with “file is in use”, use a venv:

```powershell
py -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
```

### Run immediately (no LLM required)

```bash
python run_demo.py          # terminal demo
streamlit run app.py        # browser UI
```

With the venv above: `.\.venv\Scripts\python run_demo.py` and
`.\.venv\Scripts\python -m streamlit run app.py`.

The Streamlit UI uses a custom dark theme (`.streamlit/config.toml` + CSS in
`src/ui/`) with recommendation cards, score breakdowns, and an agent timeline.

In this demo mode every agent runs its deterministic logic and the
Explanation Agent renders a template.

### Add a free local LLM (Ollama)

1. Install [Ollama](https://ollama.com) and run `ollama pull llama3.1:8b`
2. Set `LLM_PROVIDER=ollama` in `.env`

The requirement-extraction and explanation agents then produce natural
language. Any OpenAI-compatible API (cloud or local) also works via the
`OPENAI_COMPAT_*` settings.

### Use your own dataset

Set `PHONE_DATA_PATH` to a JSON or CSV file. Schema (extra columns are
ignored, missing fields use safe defaults):

| column | meaning |
|---|---|
| `id` | unique key |
| `brand`, `model`, `variant` | identity |
| `price_lkr` | Sri Lankan price (demo values OK if labelled) |
| `release_year` | model year |
| `chipset_tier` | 1–10 relative performance tier |
| `ram_gb`, `storage_gb` | memory |
| `display_size_in`, `display_type`, `refresh_rate_hz` | display |
| `camera_mp`, `battery_mah`, `has_5g` | camera / battery / 5G |
| `os`, `warranty_months` | software & warranty |

### Enable live market search

Set `ENABLE_LIVE_SEARCH=true` (requires the optional
`duckduckgo-search` package). The Market Research Agent then attaches live
price snippets as unverified evidence for the Verification Agent to check.

## Project layout

```
├── app.py                  # Streamlit demo UI
├── run_demo.py             # CLI demo / smoke test
├── data/phones_placeholder.json   # 5-phone placeholder dataset
├── src/
│   ├── config.py           # all tunables (env-driven)
│   ├── llm.py              # Ollama / OpenAI-compatible / demo client
│   ├── dataset.py          # dataset loading + candidate filtering
│   ├── tools.py            # free DuckDuckGo live search
│   ├── state.py            # shared AgentState schema
│   ├── graph.py            # LangGraph orchestration
│   └── agents/             # specialized agent modules
└── requirements.txt
```

## Extension points (good dissertation material)

* **Supervisor pattern:** route conditionally (e.g. skip replacement path
  when repair is clearly better) instead of the linear pipeline.
* **Conversation:** let the User Requirement Agent ask clarifying questions
  across multiple turns instead of one-shot input.
* **More tools:** spec APIs, retailer scraping with caching, price-history
  trend features.
* **Evaluation:** measure ranking quality against human-chosen picks;
  measure Verification Agent precision on deliberately corrupted prices.

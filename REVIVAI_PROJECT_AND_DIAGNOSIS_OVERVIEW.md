# REVIVAI: Multi-Agent Electronic Device Diagnosis & Replacement Decision System
## Comprehensive Project Documentation & Track Deep Dive

**Project Name**: REVIVAI · AI-Assisted Smartphone Repair vs. Replace Advisor  
**Repository**: `C:\ai-repair-vs-replace-system`  
**Current Date**: November 2026  
**Status**: Core Architecture Active · 53 Unit Tests Passing · Working Interactive UI  

---

# TABLE OF CONTENTS
1. [PART I: THE ENTIRE PROJECT (SYSTEM-WIDE OVERVIEW)](#part-i-the-entire-project-system-wide-overview)
   - 1.1 Problem Statement & Research Motivation
   - 1.2 System Vision & Objectives
   - 1.3 High-Level Multi-Agent Architecture (LangGraph)
   - 1.4 The Two Functional Tracks & Collaboration Bridge
   - 1.5 Shared State Contract & Full Execution Tracing
   - 1.6 User Interface & Technology Stack
2. [PART II: MY PART (FAULT DIAGNOSIS & REPAIR ASSESSMENT)](#part-ii-my-part-fault-diagnosis--repair-assessment)
   - 2.1 Scope & Functional Responsibilities
   - 2.2 Device Identification & Variant Gating (`src/device_match.py`)
   - 2.3 Multi-Category Fault Diagnosis Engine (`src/agents/diagnosis.py`)
   - 2.4 Interactive Triage & Immutable Safety Stops (`src/agents/troubleshooting.py`)
   - 2.5 Verified Self-Repair Resource Retrieval (`src/resources.py`)
   - 2.6 Test Verification Suite (53 Passing Automated Tests)
   - 2.7 Remaining Roadmap for My Part (RAG, Vision, Local Pricing, Evaluation)
3. [PART III: FILE & ARTIFACT DIRECTORY](#part-iii-file--artifact-directory)

---

# PART I: THE ENTIRE PROJECT (SYSTEM-WIDE OVERVIEW)

### 1.1 Problem Statement & Research Motivation
When a smartphone malfunctions (e.g., cracked display, rapid battery drain, charging failure), consumers face an immediate dilemma: **Is it worth fixing, or should they purchase a replacement?**

Currently, consumers face three systemic barriers:
1. **Diagnostic Uncertainty**: Users cannot reliably distinguish between a cheap component fix (e.g. dirty charging port, software hang) and an expensive hardware breakdown (e.g. mainboard power IC failure).
2. **Opaque & Volatile Repair Costs**: Local smartphone repair pricing is fragmented, unregulated, and lacks publicly verifiable quotes, causing consumers to fear exploitation.
3. **Premature Upgrades & E-Waste Acceleration**: Over 50 million metric tons of e-waste are produced globally each year. Functional smartphones are discarded simply because buying new is perceived as easier or more predictable than repair.
4. **Unreliable Generative Chatbots**: Generic LLM assistants frequently hallucinate repair pricing and provide hazardous home advice (e.g., advising consumers to pry swollen lithium-ion cells or heat displays without protective gear).

### 1.2 System Vision & Objectives
**REVIVAI** is an intelligent, multi-agent decision-support framework that combines deterministic engineering with generative reasoning to:
* **Accurately profile the damaged device** down to its exact hardware variant.
* **Diagnose faults and enforce immutable safety stops** for thermal, chemical, and physical hazards.
* **Objectively benchmark repair economics** using the 40%–60% residual value decision rule.
* **Recommend verified, fact-checked replacement devices** tailored to user priorities and budget, completely eliminating hallucinated specifications and pricing.

---

### 1.3 High-Level Multi-Agent Architecture (LangGraph)
REVIVAI uses **LangGraph** to execute a sequential, observable multi-agent state graph. Rather than an unpredictable autonomous agent loop, agents execute in strict **information-dependency order**:

```
[ User Input ]
      │
      ▼
┌──────────────────────────────── LangGraph Linear Pipeline ────────────────────────────────┐
│                                                                                            │
│  [Track 1: Fault Diagnosis & Repair Assessment]                                            │
│   1. Device Confirmation & Variant Gating  ──► Locks exact hardware variant                │
│   2. FaultDiagnosisAgent                   ──► Screens symptoms & red flags (text/photo)   │
│   3. TroubleshootingAgent                  ──► Non-invasive steps & immutable safety stops │
│   4. DeviceProfilingAgent                  ──► Assesses age & depreciated residual value   │
│   5. RepairCostAgent                       ──► Fetches sourced quote range (or local quote)│
│   6. RepairDecisionAgent                   ──► Calculates economic repair vs replace path  │
│                                                                                            │
│  [Track 2: Replacement Recommendation & Market Intelligence]                               │
│   7. UserRequirementAgent                  ──► Structured feature priority profile         │
│   8. SpecificationRetrievalAgent           ──► Queries mobile catalogue with hard filters  │
│   9. MarketResearchAgent                   ──► Reads base prices + optional live search    │
│  10. SimilarityAgent                       ──► Computes multi-attribute similarity score   │
│  11. BudgetAgent                           ──► Classifies affordability (+10% tolerance)   │
│  12. ComparisonAgent                       ──► 7-dimension weighted trade-off scoring      │
│  13. RecommendationAgent                   ──► Clustered picks: Budget, Similar, Upgrades  │
│  14. VerificationAgent                     ──► Fact-checks specs & rejects price outliers  │
│  15. ExplanationAgent                      ──► Generates user-facing justification prose   │
│                                                                                            │
└────────────────────────────────────────────────────────────────────────────────────────────┘
      │
      ▼
[ Verified Decision Card + Recommendation Categories + Transparent Agent Trace ]
```

---

### 1.4 The Two Functional Tracks & Collaboration Bridge

The system unites two specialized functional tracks:

| Dimension | Track 1: Fault Diagnosis & Repair Assessment | Track 2: Replacement Recommendation & Decision Support |
|---|---|---|
| **Primary Focus** | The user's current malfunctioning device. | The external smartphone replacement market. |
| **Key Responsibilities** | Exact model variant matching, fault screening, safety stops, repair manual linking, and sourced repair costs. | User preference extraction, candidate filtering, multi-criteria trade-off scoring, and verification. |
| **Output to System** | Confirmed device specs, fault category, safety flags, and sourced repair cost. | Scored candidate pool, similarity rankings, and verified top recommendations. |

#### The Economic Decision Bridge (Repair vs. Replace Rule)
The two tracks converge at the **Repair Decision Agent**:
* **Device Residual Value ($V_r$)**: Estimated from purchase price, brand depreciation retention curves (Apple 72%, Samsung 60%, Google 58%, Xiaomi 50%), and condition multipliers.
* **Repair Cost Midpoint ($C_r$)**: Sourced from verified repair shop records.
* **Decision Rules**:
  * If $\frac{C_r}{V_r} < 0.40$ (under 40%): **Repair is recommended**.
  * If $\frac{C_r}{V_r} > 0.60$ (over 60%): **Replacement is suggested**.
  * Between 40% and 60%: **Compare quote with replacement candidates side-by-side**.

---

### 1.5 Shared State Contract & Full Execution Tracing
All agents communicate strictly through a single typed dictionary, **`AgentState`** ([`src/state.py`](file:///c:/ai-repair-vs-replace-system/src/state.py)):
* **Zero Hidden Memory**: No agent maintains internal state; all outputs are written back to `AgentState`.
* **Trace Audit Log (`state["trace"]`)**: Every agent appends a structured record:
  ```python
  {
      "agent": "TroubleshootingAgent",
      "action": "enforced immutable safety stop",
      "details": {"triggers": ["swollen_battery"], "escalate": True}
  }
  ```
* **Dissertation & Empirical Value**: The trace provides incontrovertible proof of multi-agent collaboration rendered directly in the Streamlit web UI.

---

### 1.6 User Interface & Technology Stack
* **Web UI ([`app.py`](file:///c:/ai-repair-vs-replace-system/app.py))**: Modern dark glassmorphic interface with custom CSS tokens, SVG duotone icons, responsive layout, and real-time variant selectors.
* **Multi-Page Query Routing**: Home (`?page=home`), Diagnose (`?page=diagnose`), Repair vs. Replace (`?page=repair`), Find a Phone (`?page=phones`), and How It Works (`?page=howit`).
* **LLM Engine ([`src/llm.py`](file:///c:/ai-repair-vs-replace-system/src/llm.py))**: Clean abstraction supporting local **Ollama** (`llama3.1:8b`), OpenAI-compatible APIs, and an offline **`DemoLLM`** ensuring the pipeline runs anywhere without internet access.
* **Live Market Search ([`src/tools.py`](file:///c:/ai-repair-vs-replace-system/src/tools.py))**: DuckDuckGo integration for real-time market signals.

---

# PART II: MY PART (FAULT DIAGNOSIS & REPAIR ASSESSMENT)

### 2.1 Scope & Functional Responsibilities
My track encompasses the complete analysis of the user's damaged device, triage safety, and repair viability:
1. **Device Identification & Confirmation** (Proposal Section 5.1).
2. **Multi-Modal Fault Diagnosis** (Proposal Section 5.2).
3. **Interactive Troubleshooting & Safety Guardrails** (Proposal Section 5.2).
4. **Self-Repair Resource Retrieval** (Proposal Section 5.2).
5. **Datasheet RAG Search** (Proposal Section 5.3).
6. **Sourced Repair-Cost Estimation** (Proposal Section 5.4).

---

### 2.2 Device Identification & Variant Gating (`src/device_match.py`)
Accurate repair estimation and comparison require exact hardware identification:
* **Tolerant Fuzzy Matching**:
  * Normalizes casing, strips whitespace, and removes punctuation.
  * Tolerates user entry errors (e.g. typing `"Samsung Galaxy A51"` into the model input is properly cleaned so the brand isn't redundantly matched).
* **Variant Dropdown & Spec Preview**:
  * Matches against the catalogue and displays a variant selector (e.g. `Galaxy A51 · 8 GB RAM · 128 GB storage`).
  * Previews processor, screen, and battery specifications.
* **Execution Gating**:
  * In [`app.py`](file:///c:/ai-repair-vs-replace-system/app.py), the **"Analyze & Recommend"** button is disabled until the user checks `"I confirm this is my device variant"`.
  * For uncatalogued devices, provides a clean fallback checkbox: `"Continue with the details I entered (unverified)"`.

---

### 2.3 Multi-Category Fault Diagnosis Engine (`src/agents/diagnosis.py`)
Provides fast, safe, and explainable symptom triage:
* **7 Standardized Fault Categories**:
  1. `cracked_screen`: Physical glass, OLED, or digitizer damage.
  2. `battery`: Premature drain, swelling, or sudden shutdowns.
  3. `charging`: Port lint, loose cable fit, or charging circuit issues.
  4. `overheating`: Thermal spikes, heavy application load, or battery heat.
  5. `liquid_damage`: Water immersion, moisture alerts, or rain exposure.
  6. `performance`: Operating system stutter, storage saturation, app freezing.
  7. `unclear`: Ambiguous symptoms prompting follow-up questions.
* **Dual-Path Strategy**:
  * **LLM Path**: Validates structured JSON responses against the 7 fixed categories, automatically falling back to rules if JSON is malformed or invalid.
  * **Deterministic Rules Path**: Weighted keyword regular expressions with strict word boundaries and **negation detection** (e.g., phrases like `"no cracks"` or `"screen is not broken"` will never trigger `cracked_screen`).
* **Automated Red-Flag Extraction**:
  * Deterministic rule-based scan for dangerous conditions: swollen batteries, burning smells, visible smoke, or liquid contact.
  * Emits entries into `state["safety_flags"]` that **cannot be overridden by the LLM**.

---

### 2.4 Interactive Triage & Immutable Safety Stops (`src/agents/troubleshooting.py`)
Guarantees consumer safety through clear risk grading:
* **Risk-Graded Triage**:
  * `safe`: Consumer-safe checks (replacing cables, restarting, checking app battery statistics).
  * `caution`: Safe with care (applying clear tape over cracked glass to prevent cuts, cleaning ports with non-conductive plastic toothpicks).
  * `technician_only`: Operations requiring professional workshops (opening glued casings, replacing swollen lithium batteries).
* **Immutable Safety Stops**:
  * Triggers on any `stop`-level safety flag, liquid exposure, or severe heat.
  * Immediately suppresses normal DIY steps.
  * Replaces guidance with an emergency protocol (power down, keep away from flammables, do not charge).
  * Displays a prominent red warning banner in the web interface:
    > **⚠ Safety Stop: Technician inspection required**  
    > *Stop using the device and have it inspected by a qualified professional.*

---

### 2.5 Verified Self-Repair Resource Retrieval (`src/resources.py`)
Connects users to trustworthy repair manuals without broken links:
* **Curated Database ([`data/repair_resources.json`](file:///c:/ai-repair-vs-replace-system/data/repair_resources.json))**:
  * **18 verified URLs** audited for zero 404 dead links.
  * Covers Apple, Samsung, Xiaomi, Redmi, Poco, and Google.
* **Scoping & Classification**:
  * `support`: Official OEM safe troubleshooting pages.
  * `service`: Authorized technician repair booking portals.
  * `guide`: Detailed disassembly manuals (iFixit).
* **Hazard & Teardown Labeling**:
  * Complex guides requiring heat guns or case suction tools are explicitly flagged: `(advanced: opens the phone, uses heat)`.
  * **Zero Teardown Links During Safety Stops**: When a safety stop is active, all disassembly links are withheld to prevent hazardous user actions.

---

### 2.6 Test Verification Suite (53 Passing Automated Tests)
A full unit test suite ensures all business logic runs deterministically:
* **`tests/test_diagnosis.py` (17 tests)**:
  * Full classification accuracy across all 7 categories.
  * Word boundary enforcement and negation recognition.
  * Tie-breaking behavior returning `"unclear"`.
  * Deterministic safety flag extraction.
* **`tests/test_troubleshooting.py` (19 tests)**:
  * Verification of safe steps for every fault category.
  * Immediate escalation on battery swelling, liquid ingress, and burning odors.
  * Zero dangerous instructions (prohibits heating or prying batteries).
* **`tests/test_resources.py` (17 tests)**:
  * Structural integrity of `data/repair_resources.json`.
  * Hierarchy: model-specific guides prioritized over brand portals.
  * Brand alias resolution (Redmi / Poco ➔ Xiaomi).
  * Complete suppression of teardowns during safety stops.

---

### 2.7 Remaining Roadmap for My Part

| Step | Milestone | Implementation Plan | Timeline |
|---|---|---|---|
| **Step 7** | **Datasheet RAG (Vector DB)** | Index official OEM service manuals and datasheets into **ChromaDB / FAISS**. Support grounded technical question-answering (charging wattage, display refresh, ingress protection) with exact page citations and BM25 offline fallback. | ~1.5 Weeks (Next) |
| **Step 4** | **Computer Vision Damage Model** | Train a transfer-learning convolutional network (**MobileNetV3** / **ResNet-50**) on Roboflow phone damage datasets to classify screen cracks, glass shattering, and body scratches. Report Precision, Recall, and Macro-F1. | 2–3 Weeks |
| **Step 8** | **Sri Lankan Repair-Cost Dataset** | Populate `data/repair_costs.json` with ground-truth repair shop quotes (screens, batteries, ports) with source proof and timestamps, replacing fallback quote alerts. | 2 Weeks |
| **Step 9** | **Benchmark Evaluation** | Construct ~100 realistic test scenarios. Benchmark classification accuracy, safety compliance (target: 0% false negatives on hazards), and repair-cost error against single-LLM baselines. | 2 Weeks |

---

# PART III: FILE & ARTIFACT DIRECTORY

### System Files
* [`src/state.py`](file:///c:/ai-repair-vs-replace-system/src/state.py) — Central multi-agent state schema (`AgentState`) and sub-schemas.
* [`src/graph.py`](file:///c:/ai-repair-vs-replace-system/src/graph.py) — LangGraph workflow orchestration and pipeline runner.
* [`app.py`](file:///c:/ai-repair-vs-replace-system/app.py) — Streamlit user interface, variant gate, and diagnostic cards.
* [`src/dataset.py`](file:///c:/ai-repair-vs-replace-system/src/dataset.py) — Phone catalogue and repair cost dataset loader.
* [`src/llm.py`](file:///c:/ai-repair-vs-replace-system/src/llm.py) — Unified LLM abstraction (Ollama, cloud OpenAI-compatible, and Demo fallback).
* [`src/tools.py`](file:///c:/ai-repair-vs-replace-system/src/tools.py) — DuckDuckGo live market search tool.

### My Track Files (Diagnosis & Repair)
* [`src/device_match.py`](file:///c:/ai-repair-vs-replace-system/src/device_match.py) — Tolerant device matching and variant confirmation builder.
* [`src/agents/diagnosis.py`](file:///c:/ai-repair-vs-replace-system/src/agents/diagnosis.py) — Fault diagnosis agent with dual LLM/rule execution.
* [`src/agents/troubleshooting.py`](file:///c:/ai-repair-vs-replace-system/src/agents/troubleshooting.py) — Interactive triage agent with immutable safety stops.
* [`src/resources.py`](file:///c:/ai-repair-vs-replace-system/src/resources.py) — Self-repair resource retrieval engine.
* [`data/repair_resources.json`](file:///c:/ai-repair-vs-replace-system/data/repair_resources.json) — Curated registry of 18 verified repair guide URLs.
* [`src/agents/repair_cost.py`](file:///c:/ai-repair-vs-replace-system/src/agents/repair_cost.py) — Repair cost evaluation agent.
* [`tests/test_diagnosis.py`](file:///c:/ai-repair-vs-replace-system/tests/test_diagnosis.py) — Unit tests for diagnosis classification and rules.
* [`tests/test_troubleshooting.py`](file:///c:/ai-repair-vs-replace-system/tests/test_troubleshooting.py) — Unit tests for triage safety stops.
* [`tests/test_resources.py`](file:///c:/ai-repair-vs-replace-system/tests/test_resources.py) — Unit tests for resource lookup and suppression.

# How the Multi-Agent System Works

This document explains the phone repair-or-replace workflow and how the
system pulls relevant sections from technical datasheets.

## 1. What a multi-agent system means here

A multi-agent system divides one large task into smaller specialist tasks.
Each specialist agent has a focused responsibility, reads the information it
needs, and returns a structured result. The agents do not communicate through
unstructured chat with one another. They communicate through one shared
`AgentState` object.

The workflow is coordinated by LangGraph in [`src/graph.py`](./src/graph.py).
Each agent is registered as a graph node, and the graph passes the updated
state from one node to the next.

## 2. End-to-end workflow

The current implementation runs this ordered pipeline:

```text
User input
   |
   v
Fault Diagnosis
   |
   v
Datasheet RAG (pull relevant technical sections)
   |
   v
Troubleshooting and safety checks
   |
   v
User requirements
   |
   v
Device profiling
   |
   v
Repair-cost lookup
   |
   v
Repair-versus-replace decision
   |
   v
Replacement specification retrieval
   |
   v
Market research
   |
   v
Similarity and budget analysis
   |
   v
Comparison and recommendation
   |
   v
Verification
   |
   v
Explanation
```

The graph is intentionally linear. A later agent can use outputs produced by
earlier agents, and the order makes the information dependencies explicit.
The project documentation describes conditional supervisor routing as a future
extension, but the current graph does not yet branch dynamically.

## 3. What each agent contributes

| Agent | Main responsibility | Important output |
|---|---|---|
| Fault Diagnosis Agent | Classifies the likely fault from symptoms and optional image evidence | `diagnosis` |
| Datasheet RAG Agent | Pulls model-specific technical sections | `spec_answers` and technical fields in `diagnosis` |
| Troubleshooting Agent | Provides safe first steps and escalation guidance | `troubleshooting`, `safety_flags` |
| User Requirement Agent | Converts free text into structured preferences | `requirements` |
| Device Profiling Agent | Estimates condition and residual value | `old_device_profile` |
| Repair Cost Agent | Looks up a sourced repair range or reports unavailable | `repair_cost_estimate` |
| Repair Decision Agent | Compares repair cost with device value and safety conditions | `decision` |
| Specification Retrieval Agent | Builds a replacement candidate pool | `candidates` |
| Market Research Agent | Adds dataset prices and optional live evidence | `market_info` |
| Similarity Agent | Compares alternatives with the existing device | `similarity` |
| Budget Agent | Applies budget and affordability rules | `budget_analysis` |
| Comparison Agent | Calculates weighted candidate scores | `comparisons` |
| Recommendation Agent | Selects categorized top choices | `recommendations` |
| Verification Agent | Checks facts, prices, and uncertainty | `verification` |
| Explanation Agent | Produces the user-facing result | `explanation` |

Agents can be deterministic rules, retrieval components, scoring functions, or
LLM-backed components. This hybrid design keeps important calculations and
safety decisions reproducible while still allowing natural-language
requirement extraction and explanations.

## 4. Shared state and hand-offs

[`src/state.py`](./src/state.py) defines the shared `AgentState` type. Each
agent should return only the fields it updates. LangGraph merges those updates
into the current state.

Examples of hand-offs:

1. The diagnosis agent writes `diagnosis`.
2. The Datasheet RAG agent reads the confirmed device, issue description, and
   diagnosis, then writes `spec_answers`.
3. The decision agent reads troubleshooting, repair cost, device profile, and
   retrieved technical sections.
4. The recommendation and verification agents read the candidate, market,
   budget, comparison, and decision fields.
5. The explanation agent turns the verified state into final text.

Every agent also appends an entry to `trace`. A trace entry records the agent,
the action it performed, and useful details such as queries, counts, scores,
or citations. This makes the collaboration visible for debugging and
evaluation.

## 5. How “pull sections” works

In this project, “pull sections” means retrieving the most relevant sections
from the confirmed device's technical datasheet or service manual.

### Step 1: Datasheets are split into sections

[`src/rag/chunker.py`](./src/rag/chunker.py) reads Markdown files under
[`data/datasheets/`](./data/datasheets/). It:

1. Reads device metadata such as brand, model, source URL, and verification
   date.
2. Splits the document at `##` headings.
3. Creates one structured chunk per section.
4. Detects a component category such as `battery`, `screen`, `charging`,
   `safety`, or `general`.
5. Preserves section-level source metadata and creates a stable `chunk_id`.

A chunk contains fields similar to:

```text
chunk_id       samsung_galaxy_a55#battery
brand          Samsung
model          Galaxy A55
section        Battery
component      battery
text           section contents
source_url     checked source URL
date_verified  verification date
sources        section references
```

### Step 2: The chunks are indexed

[`src/rag/retriever.py`](./src/rag/retriever.py) builds an in-memory lexical
TF-IDF index. The indexed text combines:

```text
section title + component label + section body
```

TF-IDF gives higher scores to terms that are important to the query but less
common across all indexed sections. The query and each chunk are represented
as normalized vectors, then compared using cosine similarity.

### Step 3: The device identity is checked first

The retriever does not search every document indiscriminately. It requires a
non-empty brand and model, then applies strict model gating:

- The brand must match.
- The complete model name must match.
- Model identifiers can be used as explicit alternatives.
- Substring matches are not accepted as a substitute for a complete match.

This prevents a query for one phone variant from accidentally returning a
similar-looking section from another phone.

### Step 4: The query is built from the issue

[`src/agents/datasheet_rag.py`](./src/agents/datasheet_rag.py) combines the
user's issue description with the diagnosed fault category. For example:

```text
query: "phone gets hot while charging overheating"
component: "battery"
```

The component is mapped to a category and receives a relevance boost when it
matches the chunk's detected component. A battery query therefore prefers
battery sections over unrelated overview sections when their text relevance
is comparable.

### Step 5: The top sections are returned

The current agent requests at most two sections (`top_k=2`). Results below the
minimum similarity threshold are discarded. Results are sorted by score and
returned with:

- The section text.
- A score.
- The section name and component.
- The source title and URL.
- The checked date.
- A citation and chunk ID.

The agent converts these results into `spec_answers` and adds the first
retrieved section to the diagnosis as technical context. The UI can display
the answer and its source section instead of presenting unsupported technical
claims.

## 6. Why retrieval can return no sections

The retrieval path is deliberately fail-closed. It returns no technical
section when:

- The catalogue identity has not been confirmed.
- The user proceeded with an unverified device.
- The confirmed catalogue ID does not match the device state.
- No datasheet exists for the exact model.
- The query has no usable tokens.
- No section reaches the similarity threshold.

When this happens, the system removes previously attached technical fields
from the diagnosis and records the reason in the trace. It does not silently
substitute a generic phone section.

## 7. Source and citation flow

Source information is attached while the section is being parsed and carried
through retrieval:

```text
Markdown source
  -> chunk metadata
  -> retriever result
  -> spec_answers.sources
  -> diagnosis citation
  -> verification and final explanation
```

This section-level provenance is important because a single manual may contain
many components and references. The citation identifies the exact device and
section that supported the retrieved excerpt.

## 8. “Pull section” versus physical battery pull-tab

These are different concepts:

- **Pulling a section** is a software retrieval operation. The system pulls
  relevant text from a technical document.
- **A pull-tab or pull-pouch** is a physical battery-removal feature described
  by some service manuals.

The chunker recognizes terms such as `pull-tab` when classifying a section as
related to the battery. The Repair Decision Agent can then add a hardware note
such as “stretch-release battery pull-tabs” to the explanation. That note is
evidence about repair design; it is not an instruction for an untrained user
to open a device.

Safety still takes priority. Swelling, heat, liquid damage, or other hazards
are routed to professional assessment by the troubleshooting and decision
logic.

## 9. Example

Suppose the user confirms a Samsung Galaxy A55 and reports that the phone
overheats while charging.

1. Fault Diagnosis classifies the issue as likely `overheating` or
   `battery-related`.
2. Datasheet RAG queries the confirmed A55 documents using the issue and
   category.
3. The retriever filters out every other model.
4. Battery or charging sections receive the component boost.
5. The top two supported sections are returned with citations.
6. Troubleshooting decides whether safe checks are appropriate or whether the
   user must stop and seek a technician.
7. Repair Decision may use a retrieved hardware note, but it does not treat
   the note as proof that a repair is safe or economically worthwhile.
8. Verification and Explanation present only the supported facts and clearly
   state remaining uncertainty.

## 10. Current limitations and future improvements

The current retriever is lexical TF-IDF, not an embedding or hybrid vector
retriever. It is fast and deterministic, but it may miss synonyms that do not
share words with the query. Future improvements could add:

- Hybrid lexical plus embedding retrieval.
- Section reranking with a cross-encoder or LLM.
- More complete variant and model-identifier matching.
- Page-level or paragraph-level citations.
- Retrieval evaluation using labelled fault-to-section test cases.
- Caching and freshness checks for updated manuals.


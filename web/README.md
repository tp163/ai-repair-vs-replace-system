# REVIVAI TypeScript application

Fresh Next.js/React frontend and LangGraph.js backend. The Python prototype remains alongside it. This is a local research preview, not a completed or clinically validated diagnostic service.

## Start

Use Node.js 20.9 or newer (current supported LTS recommended).

```powershell
cd "D:\AI Repair vs Replace System\phone-recommender-multiagent\web"
npm install
Copy-Item .env.example .env.local
npm run dev
```

Open http://localhost:3000. No account or API key is needed for the explicitly labelled basic symptom screening. Phone data comes from `src/data/phones.sample.json`; all prices and specifications are sample, unverified records.

## Implemented

- Responsive home, diagnosis, repair/replace, phone catalogue, comparison and saved-case views.
- Confirmed variant input, image upload limit, descriptions and optional hard budget.
- LangGraph diagnosis → guidance → conditional recommendation → verification workflow.
- Charging follow-up, safety routing, successful-check exit and replacement opt-out.
- Optional Gemini text/image request with schema validation, timeout and visible rule fallback.
- Deterministic category matching, similarity ranking and strict budget filtering.
- Browser-local saved result snapshots, excluding uploaded images.
- Supabase schema and row-level access policies for catalogue/evidence, cases, events, runs and private photo storage.
- Regression tests for safety, budget and workflow routing.

## Enable model assessment

Set GEMINI_API_KEY and GEMINI_MODEL in `.env.local` to your provider key and a currently available image-capable model identifier, then restart. Keys stay on the server. A request sends symptoms and any uploaded photo to the provider. Without configuration, photos are not analysed. Live provider calls require your own review of provider terms and cost settings.

## Database integration status

`supabase/migrations/001_foundation.sql` is a development migration, not automatically applied. It provides a starting schema and private bucket policies. Auth UI, persistent agent checkpoints, database repositories and document ingestion are NOT wired into the app yet. Supabase environment variables are reserved for that next integration. Current cases live only in browser localStorage, with no cross-device sync. Do not treat browser snapshots as trusted server records.

## Remaining implementation

1. Connect Supabase Auth and validate the session and ownership on every case API. Add distributed request limits before exposing paid model calls publicly.
2. Add database repositories, durable run scheduling/checkpoints, server-owned events and cancellation. The current request runs synchronously; answering a follow-up recomputes the assessment.
3. Replace sample phone records with reviewed specifications and exact variant offers, provenance and freshness rules. Add manual variant onboarding.
4. Connect sourced repair records and aggregate compatible parts/labour ranges. Current cost output deliberately remains unavailable.
5. Add document ingestion, fixed-dimension embeddings, hybrid retrieval and page-level citations. Current troubleshooting is a small rule library, not document-grounded retrieval.
6. Expand interactive troubleshooting beyond the charging question, uncertainty calibration and input modalities such as logs/measurements.
7. Evaluate on technician-reviewed cases versus conventional filtering and a single-model baseline. Current tests are software regression checks, not research results.
8. Add authenticated admin import/review, live seller verification, retention controls and cloud deployment.

## Checks

```powershell
npm run typecheck
npm test
npm run build
```

Do not deploy this preview publicly with a paid API key until authentication and abuse limits are implemented. The SQL policies need integration testing in a development Supabase instance before use with real data.

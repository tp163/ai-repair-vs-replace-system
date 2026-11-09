# REVIVAI Project Status

## Project purpose

REVIVAI helps a customer decide what to do when a phone has a problem:

1. Describe the phone issue.
2. Follow safe troubleshooting steps.
3. Decide whether repair or replacement is more suitable.
4. Compare replacement phones using budget and device preferences.

The project currently contains both the original Python prototype and a newer
Next.js web experience.

## What has already been improved

### User interface

- Added a responsive Next.js frontend under [`web/`](./web/).
- Preserved the existing REVIVAI visual identity while improving spacing,
  typography, contrast, and button visibility.
- Added Plus Jakarta Sans for headings and Inter for body text and numbers.
- Added customer-focused wording instead of exposing internal agent terminology.
- Reworked the “How It Works” content around the customer's actual journey.
- Added responsive layouts for desktop, tablet, and mobile screens.
- Added a light/dark theme switch with browser-local preference storage.
- Added accessible labels, visible focus states, and reduced-motion support.
- Replaced the hero artwork with the supplied space-phone image.
- Removed hero background movement so the supplied image stays visually stable.

### Interaction and animation

- Added a continuous announcement marquee.
- Added subtle hero text entrance animation.
- Added scroll-reveal animations for homepage sections.
- Added hover elevation and shadow effects for issue and phone cards.
- Added phone artwork hover feedback.
- Added swipeable phone cards on mobile.
- Added smooth header icon and button interactions.
- Added reduced-motion fallbacks for users who disable animation.

### Diagnosis and recommendation flow

- Added device and variant confirmation.
- Added symptom descriptions and optional image upload.
- Added budget and priority inputs.
- Added safety routing for hazardous charging and battery cases.
- Added repair-versus-replace recommendations.
- Added phone comparison and filtering.
- Added saved case snapshots using browser local storage.
- Added schema validation for API input and diagnosis results.
- Added deterministic fallback logic when optional model services are not configured.

### Quality and safety

- Added regression tests for device confirmation, budget rules, charging
  safety, troubleshooting, and replacement routing.
- Added request-size, origin, and schema validation to the diagnosis API.
- Kept uploaded images out of saved browser snapshots.
- Added fail-closed behaviour when reliable repair-cost information is
  unavailable.

## Technology stack currently used

### Original Python prototype

- Python
- LangGraph for the original state graph
- Streamlit for the original browser UI
- Deterministic specialist modules under [`src/agents/`](./src/agents/)
- Optional Ollama or OpenAI-compatible LLM integration
- Optional DuckDuckGo live market search
- JSON/CSV phone and repair datasets

### Current web application

- Next.js 16
- React 19
- TypeScript
- App Router
- Tailwind-compatible CSS and custom responsive CSS
- Motion for React transitions
- Lucide React icons
- Zod for runtime validation
- LangGraph.js dependencies for the TypeScript workflow
- Supabase JavaScript client and development migration
- Browser local storage for the current saved-case implementation

### Current web scripts

```powershell
cd "D:\AI Repair vs Replace System\phone-recommender-multiagent\web"
npm install
npm run dev
npm run typecheck
npm test
npm run build
```

The web preview is available at `http://localhost:3000`.

## Current architecture

```text
Customer
   |
   v
Next.js / React interface
   |
   v
Next.js diagnosis API route
   |
   v
TypeScript diagnosis and recommendation workflow
   |
   +--> sample phone catalogue
   +--> safety and troubleshooting rules
   +--> optional Gemini image/text assessment
   +--> browser-local saved cases
```

The Python LangGraph workflow remains available separately. The current
Next.js diagnosis route does not yet call a FastAPI service or the Python
workflow.

## What still has to be built

### Backend integration

1. Create a FastAPI service around the Python LangGraph workflow.
2. Decide whether the production workflow should use Python LangGraph or
   LangGraph.js, rather than maintaining two independent implementations.
3. Connect the Next.js frontend to the selected backend service.
4. Add durable run IDs, checkpoints, follow-up answers, cancellation, and
   server-side event streaming.

### Database and authentication

1. Connect Supabase Auth.
2. Add authenticated case ownership and server-side authorization.
3. Replace browser-only saved cases with Supabase repositories.
4. Apply and test the Supabase migration in a development project.
5. Add private image storage with retention and deletion controls.
6. Add rate limiting before exposing paid model calls publicly.

### Data and evidence

1. Replace sample phone records with reviewed Sri Lankan phone variants.
2. Add current seller offers, warranty information, stock status, and
   freshness timestamps.
3. Add sourced repair-cost ranges for common faults.
4. Add repair-shop, parts, and labour evidence.
5. Add document ingestion, embeddings, hybrid retrieval, and page-level
   citations.
6. Add an admin review workflow for imported phone and repair records.

### Diagnosis quality

1. Expand troubleshooting beyond the current charging follow-up.
2. Support more evidence types, such as device logs and measurements.
3. Improve uncertainty explanations and escalation guidance.
4. Evaluate image analysis on a technician-reviewed phone-case dataset.
5. Compare the workflow against conventional filtering and a single-model
   baseline.
6. Add human review for uncertain or potentially unsafe cases.

### Production readiness

1. Add integration and end-to-end tests with Playwright.
2. Add observability, structured logs, error tracking, and audit events.
3. Add CI checks for typechecking, tests, builds, and dependency security.
4. Configure deployment for the frontend, API, database, and storage.
5. Add privacy policy, user consent, data retention, and provider-cost
   controls.
6. Run accessibility and responsive browser testing at supported breakpoints.

## Important current limitations

- Phone prices and specifications are sample or unverified unless explicitly
  marked otherwise.
- The current web app does not yet provide a fully persistent multi-device
  account experience.
- The current request is synchronous; it is not yet a durable conversational
  workflow.
- Repair-cost output remains unavailable when a matching sourced record is not
  present.
- The application is a research preview and must not be presented as a
  certified repair or safety diagnosis service.

## Recommended next build order

1. Freeze the current UI and add browser regression screenshots.
2. Select the production workflow runtime: Python LangGraph or LangGraph.js.
3. Implement FastAPI or finalize the TypeScript API boundary.
4. Add Supabase Auth and persistent case storage.
5. Replace sample catalogue data with reviewed, sourced records.
6. Add repair-cost and document evidence retrieval.
7. Add integration, accessibility, and end-to-end tests.
8. Deploy only after authentication, rate limiting, privacy controls, and
   monitoring are in place.

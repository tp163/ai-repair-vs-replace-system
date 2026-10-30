"""REVIVAI · Multi-agent phone repair & replacement advisor.

Run with:  streamlit run app.py
"""
from __future__ import annotations

import base64
from html import escape
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from src import config
from src.dataset import load_phones
from src.graph import run_pipeline
from src.ui.components import (
    full_landing,
    page_header,
    agent_timeline,
    metric_strip,
    old_device_summary,
    recommendation_card,
    verification_badge,
    new_arrivals_full,
    trust_bar,
    cta_agent_strip,
    feature_cards,
)
from src.ui.styles import inject_styles
from src.ui.icons import icon

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="REVIVAI · Repair vs Replace",
    page_icon=":material/smartphone:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hard-hide sidebar + all Streamlit chrome via st.html (bypasses sanitization in ST 1.66)
st.html("""
<style>
section[data-testid="stSidebar"],
[data-testid="collapsedControl"],
header[data-testid="stHeader"],
#MainMenu, footer { display:none !important; }
.block-container { padding:0 !important; max-width:100% !important; }
</style>
""")

inject_styles()

# ── Form constants ────────────────────────────────────────────────
CONDITIONS = [
    ("excellent", "Excellent"),
    ("good",      "Good"),
    ("fair",      "Fair"),
    ("poor",      "Poor"),
    ("faulty",    "Faulty"),
]
COND_VALUES = [c[0] for c in CONDITIONS]


# ══════════════════════════════════════════════════════════════════
#  RESULTS RENDERER
# ══════════════════════════════════════════════════════════════════

def _render_results(state: dict, fault: str) -> None:
    recs        = state.get("recommendations", [])
    comparisons = state.get("comparisons", [])
    profile     = state.get("old_device_profile", {})
    req         = state.get("requirements", {})
    ver         = state.get("verification", {})
    top_score   = comparisons[0]["score"] if comparisons else None

    diagnosis = state.get("diagnosis", {})
    triage = state.get("troubleshooting", {})
    repair_cost = state.get("repair_cost_estimate", {})
    decision = state.get("decision", {})
    st.markdown('<p class="section-head">Issue assessment</p>', unsafe_allow_html=True)
    fault_label = escape(str(diagnosis.get("fault_category", "Issue not identified")).replace("_", " ").title())
    confidence = escape(str(diagnosis.get("confidence", "low")).title())
    image_status = ("Photo reviewed by the configured model" if diagnosis.get("image_reviewed")
                    else ("Photo attached; visual analysis unavailable in demo mode" if diagnosis.get("image_attached")
                          else "Based on the description provided"))
    st.markdown(
        f'<div class="glass-card"><strong>{fault_label}</strong>'
        f'<p>{escape(str(diagnosis.get("probable_cause", "")))}</p>'
        f'<p class="catalog-note">Confidence: {confidence} · '
        f'{image_status}</p>'
        f'<p class="catalog-note">{escape(str(diagnosis.get("uncertainty", "")))}</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<p class="section-head">Safe checks and repair guidance</p>', unsafe_allow_html=True)
    steps = "".join(f"<li>{escape(str(step))}</li>" for step in triage.get("steps", []))
    st.markdown(
        f'<div class="glass-card"><ul class="guidance-list">{steps}</ul>'
        f'<p class="catalog-note">{escape(str(triage.get("safety_note", "")))}</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<p class="section-head">Repair cost and next step</p>', unsafe_allow_html=True)
    if repair_cost.get("status") == "estimate":
        source = escape(str(repair_cost.get("source", "Source")))
        raw_source_url = str(repair_cost.get("source_url", ""))
        source_url = escape(raw_source_url, quote=True) if raw_source_url.startswith(("https://", "http://")) else ""
        source_link = (f'<a href="{source_url}" target="_blank" rel="noopener">{source}</a>'
                       if source_url else source)
        cost_html = (f'<strong>LKR {repair_cost["min_lkr"]:,.0f} – LKR {repair_cost["max_lkr"]:,.0f}</strong>'
                     f'<p class="catalog-note">Estimate from {source_link}'
                     f'{(" · checked " + escape(str(repair_cost.get("retrieved_at")))) if repair_cost.get("retrieved_at") else ""}. Not a confirmed quotation.</p>')
    else:
        cost_html = f'<p>{escape(str(repair_cost.get("message", "A verified repair estimate is not available.")))}</p>'
    path_label = escape(str(decision.get("recommended_path", "get_repair_quote")).replace("_", " ").title())
    st.markdown(
        f'<div class="glass-card">{cost_html}<strong>Suggested path: {path_label}</strong>'
        f'<p>{escape(str(decision.get("reason", "")))}</p></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        metric_strip(req.get("budget_lkr"), len(comparisons), len(recs),
                     top_score, bool(ver.get("all_passed", True))),
        unsafe_allow_html=True,
    )
    st.markdown('<p class="section-head">Your current device</p>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="glass-card">{old_device_summary(profile, fault)}</div>',
        unsafe_allow_html=True,
    )
    categories = state.get("recommendation_categories", {})
    if categories:
        for key, category in categories.items():
            items = category.get("items", [])
            if not items:
                if category.get("message"):
                    st.info(category["message"])
                continue
            st.markdown(f'<p class="section-head">{category.get("label", key.title())}</p>',
                        unsafe_allow_html=True)
            cols = st.columns(min(len(items), 2), gap="medium")
            for i, rec in enumerate(items, start=1):
                with cols[(i - 1) % len(cols)]:
                    st.markdown(recommendation_card(rec, i), unsafe_allow_html=True)
    elif recs:
        st.markdown('<p class="section-head">Top picks</p>', unsafe_allow_html=True)
        for i, rec in enumerate(recs, start=1):
            st.markdown(recommendation_card(rec, i), unsafe_allow_html=True)
    else:
        st.warning("No recommendations — try relaxing budget or expanding the dataset.")

    st.markdown(agent_timeline(state.get("trace", [])), unsafe_allow_html=True)

    with st.expander("Full agent trace (JSON)"):
        for step in state.get("trace", []):
            st.markdown(f"**{step['agent']}** — {step['action']}")
            st.json(step["details"])
    with st.expander("Verification report"):
        st.json(ver)
    if state.get("explanation"):
        with st.expander("Plain-text summary"):
            st.text(state["explanation"])


# ══════════════════════════════════════════════════════════════════
#  PAGE: HOME
# ══════════════════════════════════════════════════════════════════

def page_home() -> None:
    try:
        phones = load_phones()
    except (FileNotFoundError, ValueError):
        phones = []
    st.markdown(full_landing(phones), unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  PAGE: DIAGNOSE
# ══════════════════════════════════════════════════════════════════

def page_diagnose() -> None:
    st.markdown(page_header("diagnose"), unsafe_allow_html=True)

    st.markdown("""
<div class="inner-page-intro">
  <h2 style="font-family:var(--font-display);font-size:1.6rem;font-weight:900;
             color:#fff;margin:0 0 0.2rem;letter-spacing:-0.02em;">Diagnose My Phone</h2>
  <p style="color:#7a9abf;font-size:0.88rem;margin:0;">
    Describe the issue or upload a photo. Get safe next steps, a sourced repair estimate when available, and replacement options.
  </p>
</div>
""", unsafe_allow_html=True)

    col_form, col_results = st.columns([1, 1.9], gap="large")

    with col_form:
        st.markdown('<p class="form-section-label">Current Device</p>', unsafe_allow_html=True)

        with st.container():
            brand      = st.text_input("Brand",  value="Samsung",    key="d_brand")
            model      = st.text_input("Model",  value="Galaxy A51", key="d_model")
            uploaded_image = st.file_uploader(
                "Upload a photo of the phone or damaged area (optional)",
                type=["jpg", "jpeg", "png", "webp"], key="d_phone_image",
            )
            if uploaded_image is not None:
                st.image(uploaded_image.getvalue(), caption="Uploaded phone image", width=180)
            try:
                catalogue = load_phones()
            except (FileNotFoundError, ValueError):
                catalogue = []
            device_matches = [p for p in catalogue
                              if str(p.get("brand", "")).casefold() == brand.casefold()
                              and str(p.get("model", "")).casefold() == model.casefold()]
            selected_device = None
            profile_confirmed = False
            if device_matches:
                devices_by_id = {str(p.get("id", i)): p
                                 for i, p in enumerate(device_matches)}
                def variant_label(phone: dict) -> str:
                    variant = phone.get("variant") or phone.get("id") or "Standard variant"
                    return f"{variant} · {phone.get('ram_gb', '?')} GB RAM · {phone.get('storage_gb', '?')} GB storage"
                selected_id = st.selectbox(
                    "Matching device variant", list(devices_by_id),
                    format_func=lambda phone_id: variant_label(devices_by_id[phone_id]),
                    key="d_device_variant",
                )
                selected_device = devices_by_id[selected_id]
                profile_confirmed = st.checkbox(
                    "I confirm this is my device variant", key="d_profile_confirmed",
                )
            elif catalogue:
                st.caption("No exact catalogue match. You can continue with the device details you entered.")
            year       = st.slider("Year purchased", 2015, 2026, 2021, key="d_year")
            orig_price = st.number_input("Original price (LKR)", min_value=0,
                                         value=75_000, step=5_000, key="d_price")
            condition  = st.selectbox(
                "Condition", COND_VALUES, index=2,
                format_func=lambda v: dict(CONDITIONS).get(v, v), key="d_cond",
            )
            fault = st.text_area(
                "Describe the issue", value="screen cracked",
                placeholder="What happened? Include symptoms, error messages, and when it started.",
                height=100, key="d_fault",
            )
            st.markdown("""
<p class="form-section-label">Preferences & Budget</p>""", unsafe_allow_html=True)
            needs  = st.text_area(
                "What matters to you?",
                value="good camera and battery, occasional gaming",
                height=80, key="d_needs",
            )
            budget = st.number_input("Max budget (LKR)", min_value=0,
                                     value=100_000, step=5_000, key="d_budget")
            st.markdown("<br>", unsafe_allow_html=True)
            run = st.button("Analyze & Recommend", type="primary",
                            icon=":material/search:", use_container_width=True,
                            disabled=bool(device_matches and not profile_confirmed))
            st.markdown(
                f'<p style="font-size:0.7rem;color:#3a5a7a;margin-top:0.4rem;text-align:center;">'
                f'LLM: <strong>{config.LLM_PROVIDER}</strong> · '
                f'Live search: <strong>{"on" if config.ENABLE_LIVE_SEARCH else "off"}</strong></p>',
                unsafe_allow_html=True,
            )

    with col_results:
        if "last_state" not in st.session_state:
            st.session_state.last_state = None

        old_device = {
            "brand":              brand,
            "model":              model,
            "year":               int(year),
            "original_price_lkr": float(orig_price),
            "condition":          condition,
            "fault":              fault,
            "variant":            (selected_device or {}).get("variant") or (selected_device or {}).get("id", ""),
            "profile_confirmed":  bool(device_matches and profile_confirmed),
        }

        if run:
            with st.status("Running recommendation agents…", expanded=True) as status:
                st.write("Diagnose → safety guidance → repair estimate → repair/replace decision → verified replacement options")
                image_data_uri = None
                if uploaded_image is not None:
                    encoded = base64.b64encode(uploaded_image.getvalue()).decode("ascii")
                    image_data_uri = f"data:{uploaded_image.type};base64,{encoded}"
                state = run_pipeline(old_device, needs, float(budget),
                                     issue_description=fault, image_data_uri=image_data_uri)
                status.update(label="Analysis complete", state="complete")
            st.session_state.last_state = state
            st.session_state.last_fault = fault

        state = st.session_state.last_state
        if state:
            _render_results(state, st.session_state.get("last_fault", ""))
        else:
            st.markdown(f"""
<div class="glass-card" style="text-align:center;padding:3rem 2rem;margin:1rem 0;">
  <div class="icon-tile lg" style="margin:0 auto 1rem;">{icon("cpu", cls="glow")}</div>
  <p style="color:#e2eaf7;font-weight:700;font-size:1rem;margin:0 0 0.5rem;">
    Ready to analyze your device
  </p>
  <p style="color:#7a9abf;font-size:0.85rem;margin:0 0 1.5rem;line-height:1.65;">
    Fill in your device details on the left,<br>
    then click <strong style="color:#1a8fff;">Analyze &amp; Recommend</strong>
  </p>
  <div style="display:flex;gap:0.75rem;justify-content:center;flex-wrap:wrap;">
    <div class="glass-card" style="text-align:left;min-width:140px;padding:0.9rem;">
      <div class="icon-tile" style="margin-bottom:0.55rem;">{icon("stethoscope")}</div>
      <p style="font-family:var(--font-display);font-weight:700;font-size:0.82rem;color:#fff;margin:0 0 0.15rem;">Diagnosis</p>
      <p style="font-size:0.72rem;color:#7a9abf;margin:0;">Identify faults</p>
    </div>
    <div class="glass-card" style="text-align:left;min-width:140px;padding:0.9rem;">
      <div class="icon-tile cyan" style="margin-bottom:0.55rem;">{icon("coins")}</div>
      <p style="font-family:var(--font-display);font-weight:700;font-size:0.82rem;color:#fff;margin:0 0 0.15rem;">Cost Analysis</p>
      <p style="font-size:0.72rem;color:#7a9abf;margin:0;">Repair vs replace</p>
    </div>
    <div class="glass-card" style="text-align:left;min-width:140px;padding:0.9rem;">
      <div class="icon-tile violet" style="margin-bottom:0.55rem;">{icon("phone")}</div>
      <p style="font-family:var(--font-display);font-weight:700;font-size:0.82rem;color:#fff;margin:0 0 0.15rem;">Phone Match</p>
      <p style="font-size:0.72rem;color:#7a9abf;margin:0;">Best replacements</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  PAGE: REPAIR vs REPLACE
# ══════════════════════════════════════════════════════════════════

def page_repair() -> None:
    st.markdown(page_header("repair"), unsafe_allow_html=True)
    st.markdown(f"""
<div style="width:100%;max-width:1120px;margin:0 auto;padding:clamp(1rem,4vw,2.5rem);box-sizing:border-box;">
  <h2 style="font-family:var(--font-display);font-size:1.8rem;font-weight:900;
             color:#fff;margin:0 0 0.4rem;">Repair vs Replace</h2>
  <p style="color:#7a9abf;font-size:0.92rem;margin:0 0 1.75rem;">
    Not sure whether to fix your phone or get a new one? Our AI weighs all the factors.
  </p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:1.25rem;margin-bottom:1.5rem;">
    <div class="glass-card">
      <div class="icon-tile green" style="margin-bottom:0.8rem;">{icon("wrench")}</div>
      <h3 style="font-family:var(--font-display);color:#fff;margin:0 0 0.6rem;font-size:1rem;">When to Repair</h3>
      <ul style="color:#7a9abf;font-size:0.85rem;line-height:1.85;padding-left:1.1rem;margin:0;">
        <li>Repair cost &lt; 40% of device value</li>
        <li>Phone is under 3 years old</li>
        <li>Only one fault (e.g. cracked screen)</li>
        <li>Performance is still acceptable</li>
        <li>Device has sentimental value</li>
      </ul>
    </div>
    <div class="glass-card">
      <div class="icon-tile violet" style="margin-bottom:0.8rem;">{icon("phone")}</div>
      <h3 style="font-family:var(--font-display);color:#fff;margin:0 0 0.6rem;font-size:1rem;">When to Replace</h3>
      <ul style="color:#7a9abf;font-size:0.85rem;line-height:1.85;padding-left:1.1rem;margin:0;">
        <li>Multiple faults accumulating</li>
        <li>Phone is over 4 years old</li>
        <li>Repair cost &gt; 60% of replacement</li>
        <li>Performance severely degraded</li>
        <li>Software no longer supported</li>
      </ul>
    </div>
  </div>
  <div class="glass-card" style="text-align:center;padding:1.75rem;">
    <p style="color:#e2eaf7;font-weight:600;margin:0 0 0.75rem;">Let our recommendation agents compare options for your phone</p>
    <a href="?page=diagnose" class="btn-primary">Diagnose My Phone {icon("arrow")}</a>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  PAGE: FIND A PHONE
# ══════════════════════════════════════════════════════════════════

def page_phones() -> None:
    try:
        phones = load_phones()
    except (FileNotFoundError, ValueError) as exc:
        st.markdown(page_header("phones"), unsafe_allow_html=True)
        st.error(f"Phone catalogue unavailable: {exc}")
        return
    st.markdown(page_header("phones") + new_arrivals_full(phones) + cta_agent_strip() + trust_bar(),
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  PAGE: HOW IT WORKS
# ══════════════════════════════════════════════════════════════════

def page_howit() -> None:
    st.markdown(page_header("howit"), unsafe_allow_html=True)

    agents = [
        ("1","clipboard","Requirements Agent",
         "Parses your device details, fault description, preferences and budget into a structured task."),
        ("2","search","Fault Diagnosis Agent",
         "Screens the description and optional image for probable fault categories and uncertainty."),
        ("3","stethoscope","Troubleshooting Agent",
         "Offers low-risk checks and flags when a qualified repairer should inspect the phone."),
        ("4","pulse","Device Profiling Agent",
         "Estimates current value and residual life of your old device based on age and condition."),
        ("5","coins","Repair Cost Agent",
         "Looks for a sourced repair-cost range and identifies when no verified estimate is available."),
        ("6","scale","Repair Decision Agent",
         "Compares sourced repair costs with device value and signals when a quote is needed."),
        ("7","layers","Specification Retrieval Agent",
         "Searches the phone database for candidates that match your budget and needs."),
        ("8","trend","Market Research Agent",
         "Verifies current Sri Lankan market prices and availability for shortlisted models."),
        ("9","sparkle","Similarity Agent",
         "Compares candidate specifications with your existing phone to find familiar alternatives."),
        ("10","coins","Budget Agent",
         "Classifies candidates against your budget and clearly flags options above it."),
        ("11","scale","Comparison Agent",
         "Scores each candidate across price, performance, camera, battery, longevity, upgrade and similarity."),
        ("12","trophy","Recommendation Agent",
         "Groups options into budget, similar, improvement and alternative recommendations."),
        ("13","check-circle","Verification Agent",
         "Cross-checks all prices and specs before they reach your shortlist — no surprises."),
        ("14","chat","Explanation Agent",
         "Produces a plain-language summary of why each phone was recommended for you."),
    ]
    cards = "".join(f"""
<div class="glass-card" style="display:flex;gap:1rem;align-items:flex-start;padding:1rem 1.2rem;">
  <div style="width:34px;height:34px;flex-shrink:0;border-radius:50%;
              background:linear-gradient(135deg,#1a6fff,#7c3aed);
              display:flex;align-items:center;justify-content:center;
              font-family:var(--font-display);font-weight:800;font-size:0.85rem;color:#fff;">{n}</div>
  <div class="icon-tile sm">{icon(ico)}</div>
  <div>
    <p style="font-family:var(--font-display);font-weight:700;font-size:0.92rem;color:#fff;margin:0 0 0.25rem;">{name}</p>
    <p style="font-size:0.82rem;color:#7a9abf;margin:0;line-height:1.55;">{desc}</p>
  </div>
</div>""" for n, ico, name, desc in agents)

    st.markdown(f"""
<div class="inner-page-shell">
  <h2 style="font-family:var(--font-display);font-size:1.8rem;font-weight:900;
             color:#fff;margin:0 0 0.4rem;">How It Works</h2>
  <p style="color:#7a9abf;font-size:0.92rem;margin:0 0 1.75rem;">
    REVIVAI runs a coordinated pipeline of specialised agents — each one handles a different part of the comparison.
  </p>
  <div class="agent-grid">{cards}</div>
  <div class="glass-card" style="text-align:center;padding:1.5rem;margin-top:1.25rem;">
    <p style="color:#e2eaf7;font-weight:600;margin:0 0 0.85rem;">Ready to try it on your phone?</p>
    <a href="?page=diagnose" class="btn-primary">Start Diagnosis {icon("arrow")}</a>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  ROUTER  (Streamlit calls this file as a module, not __main__)
# ══════════════════════════════════════════════════════════════════

page = st.query_params.get("page", "home")

if   page == "home":    page_home()
elif page == "diagnose":page_diagnose()
elif page == "repair":  page_repair()
elif page == "phones":  page_phones()
elif page == "howit":   page_howit()
else:                   page_home()

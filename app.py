"""REVIVAI · Multi-agent phone repair & replacement advisor.

Run with:  streamlit run app.py
"""
from __future__ import annotations

import base64
from html import escape
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from src import config
from src.dataset import load_phones
from src.device_match import match_device, build_confirmation, format_specs
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

    if triage.get("escalate_to_technician"):
        st.markdown(
            f'<div class="glass-card" style="border: 1px solid rgba(239,68,68,0.7); background: rgba(239,68,68,0.12); margin-bottom: 1rem;">'
            f'<strong style="color: #f87171; font-size: 0.95rem;">⚠ Safety Stop: Technician inspection required</strong>'
            f'<p style="color: #fca5a5; margin: 0.35rem 0 0; font-size: 0.85rem;">'
            f'{escape(str(triage.get("escalation_reason", "Stop using the device and have it inspected by a qualified professional.")))}'
            f'</p></div>',
            unsafe_allow_html=True,
        )

    col_diag, col_decision = st.columns(2, gap="medium")
    with col_diag:
        st.markdown('<p class="section-head">Issue assessment</p>', unsafe_allow_html=True)
        fault_label = escape(str(diagnosis.get("fault_category", "Issue not identified")).replace("_", " ").title())
        confidence = escape(str(diagnosis.get("confidence", "low")).title())
        image_status = ("Photo reviewed" if diagnosis.get("image_reviewed")
                        else ("Photo attached" if diagnosis.get("image_attached")
                              else "Description only"))
        uncertainty = diagnosis.get("uncertainty", "")
        uncertainty_html = f'<p class="catalog-note" style="margin-top:0.35rem;">{escape(str(uncertainty))}</p>' if uncertainty else ''
        st.markdown(
            f'<div class="glass-card" style="min-height:160px;">'
            f'<div style="display:flex; justify-content:space-between; align-items:baseline; margin-bottom:0.4rem;">'
            f'<strong style="font-size:1.02rem; color:#fff;">{fault_label}</strong>'
            f'<span class="spec-tag" style="font-size:0.7rem;">{confidence} Confidence</span>'
            f'</div>'
            f'<p style="font-size:0.85rem; line-height:1.5; color:#cbd5e1; margin:0 0 0.35rem;">{escape(str(diagnosis.get("probable_cause", "")))}</p>'
            f'<p class="catalog-note">Input: {image_status}</p>'
            f'{uncertainty_html}'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col_decision:
        st.markdown('<p class="section-head">Repair & Decision</p>', unsafe_allow_html=True)
        if repair_cost.get("status") == "estimate":
            source = escape(str(repair_cost.get("source", "Source")))
            raw_source_url = str(repair_cost.get("source_url", ""))
            source_url = escape(raw_source_url, quote=True) if raw_source_url.startswith(("https://", "http://")) else ""
            source_link = (f'<a href="{source_url}" target="_blank" rel="noopener">{source}</a>'
                           if source_url else source)
            cost_html = (
                f'<div style="font-size:1.15rem; font-weight:700; color:#38bdf8; margin-bottom:0.2rem;">'
                f'LKR {repair_cost["min_lkr"]:,.0f} – {repair_cost["max_lkr"]:,.0f}'
                f'</div>'
                f'<p class="catalog-note" style="margin-bottom:0.45rem;">Estimate from {source_link}'
                f'{(" · checked " + escape(str(repair_cost.get("retrieved_at")))) if repair_cost.get("retrieved_at") else ""}</p>'
            )
        else:
            cost_html = f'<p style="font-size:0.85rem; color:#94a3b8; margin-bottom:0.45rem;">{escape(str(repair_cost.get("message", "A verified repair estimate is not available.")))}</p>'

        path_label = escape(str(decision.get("recommended_path", "get_repair_quote")).replace("_", " ").title())
        reason = escape(str(decision.get("reason", "")))
        st.markdown(
            f'<div class="glass-card" style="min-height:160px;">'
            f'{cost_html}'
            f'<div style="display:flex; align-items:center; gap:0.4rem; margin-bottom:0.35rem;">'
            f'<span style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; color:#a5b4fc; font-weight:600;">Recommended Path:</span> '
            f'<span class="spec-tag highlight" style="font-size:0.75rem;">{path_label}</span>'
            f'</div>'
            f'<p style="font-size:0.82rem; line-height:1.45; color:#cbd5e1; margin:0;">{reason}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    spec_answers = state.get("spec_answers", [])
    if spec_answers:
        with st.expander("📖 Datasheet Excerpts & Sources", expanded=False):
            for ans in spec_answers:
                st.markdown(f"**{ans.get('question', '')}**")
                sources = ans.get("sources", [])
                for src in sources:
                    src_url = str(src.get("source_url", ""))
                    doc_name = escape(str(src.get("doc", "Datasheet source")))
                    link_html = (
                        f'<a href="{escape(src_url, quote=True)}" target="_blank" rel="noopener">{doc_name}</a>'
                        if src_url.startswith("https://") else doc_name
                    )
                    detail = f'Section: {escape(str(src.get("section", "")))} · Source: {link_html}'
                    if src.get("date_verified"):
                        detail += f' · Checked: {escape(str(src["date_verified"]))}'
                    st.markdown(
                        f'<p class="catalog-note">{detail}</p>',
                        unsafe_allow_html=True,
                    )
                st.markdown(ans.get("answer", ""))

    st.markdown('<p class="section-head">Safe checks and repair guidance</p>', unsafe_allow_html=True)
    def _step_html(step: dict) -> str:
        links = ""
        for r in step.get("resources", []):
            url = str(r.get("url", ""))
            if not url.startswith(("https://", "http://")):
                continue
            tag = " (advanced: opens phone)" if r.get("requires_opening_device") else ""
            links += (f' <a href="{escape(url, quote=True)}" target="_blank" rel="noopener">'
                      f'{escape(str(r.get("title", "Guide")))}</a>'
                      f'<span class="catalog-note"> · {escape(str(r.get("source", "")))}'
                      f'{escape(tag)}</span>')
        return f"<li>{escape(str(step.get('text', '')))}{('<br>' + links) if links else ''}</li>"

    steps = "".join(_step_html(s) for s in triage.get("detailed_steps", [])) or "".join(
        f"<li>{escape(str(s))}</li>" for s in triage.get("steps", []))
    safety_note = triage.get("safety_note", "")
    resource_note = triage.get("resource_note", "")
    notes_html = ""
    if safety_note:
        notes_html += f'<p class="catalog-note" style="margin-top:0.4rem;">{escape(str(safety_note))}</p>'
    if resource_note:
        notes_html += f'<p class="catalog-note">{escape(str(resource_note))}</p>'
    st.markdown(
        f'<div class="glass-card"><ul class="guidance-list">{steps}</ul>{notes_html}</div>',
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
    Identify phone faults, explore verified repair costs, and compare replacement options.
  </p>
</div>
""", unsafe_allow_html=True)

    col_form, col_results = st.columns([1, 1.25], gap="large")

    with col_form:
        st.markdown('<p class="form-section-label">Device Information</p>', unsafe_allow_html=True)

        with st.container():
            c_b, c_m = st.columns(2)
            with c_b:
                brand = st.text_input("Brand", placeholder="e.g. Samsung", key="d_brand_v2")
            with c_m:
                model = st.text_input("Model", placeholder="e.g. Galaxy A51", key="d_model_v2")

            uploaded_image = st.file_uploader(
                "Photo of phone or damaged area (optional)",
                type=["jpg", "jpeg", "png", "webp"], key="d_phone_image",
            )
            if uploaded_image is not None:
                st.image(uploaded_image.getvalue(), caption="Uploaded phone image", width=160)

            try:
                catalogue = load_phones()
            except (FileNotFoundError, ValueError):
                catalogue = []
            match = match_device(brand, model, catalogue)
            selected_device = None
            selected_id = None
            user_confirmed = False
            manual_ok = not catalogue
            if match["options"]:
                options_by_id = {o["id"]: o for o in match["options"]}
                selected_id = st.selectbox(
                    "Matching catalogue variant", list(options_by_id),
                    format_func=lambda i: options_by_id[i]["label"],
                    key="d_device_variant",
                )
                selected_device = options_by_id[selected_id]["phone"]
                st.caption(" · ".join(f"{k}: {v}" for k, v in format_specs(selected_device)))
                user_confirmed = st.checkbox(
                    "I confirm this is my exact model and variant",
                    key=f"d_confirm_v2_{selected_id}",
                )
            elif catalogue:
                if match["suggestions"]:
                    st.caption("Similar models: " + ", ".join(
                        f"{s['brand']} {s['model']}" for s in match["suggestions"]) + ".")
                manual_ok = st.checkbox(
                    "Continue with entered details (unverified)", key="d_manual_ok_v2",
                )
            confirmation = build_confirmation(match, selected_id, user_confirmed, manual_ok)

            c_y, c_p = st.columns(2)
            with c_y:
                year_options = ["Select year", *range(date.today().year, 1999, -1)]
                year_choice = st.selectbox("Purchase Year", year_options, key="d_year_v2")
                year = int(year_choice) if isinstance(year_choice, int) else None
            with c_p:
                orig_price = st.number_input(
                    "Purchase Price (LKR)", min_value=0,
                    value=0, step=5_000, key="d_price_v2",
                    help="Approximate purchase price. Leave 0 if unknown.",
                )

            st.markdown('<p class="form-section-label">Condition & Budget</p>', unsafe_allow_html=True)
            c_c, c_bgt = st.columns(2)
            with c_c:
                condition = st.selectbox(
                    "Condition before issue", COND_VALUES, index=None,
                    format_func=lambda v: dict(CONDITIONS).get(v, v),
                    placeholder="Select condition", key="d_cond_v2",
                )
            with c_bgt:
                budget = st.number_input(
                    "Replacement Budget (LKR)", min_value=0,
                    value=0, step=5_000, key="d_budget_v2",
                    help="Max budget for a replacement phone. Leave 0 if no limit.",
                )

            st.markdown('<p class="form-section-label">Issue & Preferences</p>', unsafe_allow_html=True)
            fault = st.text_area(
                "Describe the issue",
                placeholder="What symptoms do you notice, when did they start, or what happened beforehand?",
                height=90, key="d_fault_v2",
            )
            needs = st.text_area(
                "Replacement preferences (optional)",
                placeholder="e.g. Long battery life, good camera, smooth gaming",
                height=70, key="d_needs_v2",
            )

            run = st.button("Analyze & Recommend", type="primary",
                            icon=":material/search:", use_container_width=True,
                            disabled=not (confirmation["confirmed"] and bool(brand.strip())
                                          and bool(model.strip()) and year is not None
                                          and condition is not None and bool(fault.strip())))
            st.caption("Repair estimates are sourced when available and not confirmed quotes.")

    with col_results:
        if "last_state" not in st.session_state:
            st.session_state.last_state = None

        current_result_key = (
            brand.strip().casefold(),
            model.strip().casefold(),
            confirmation.get("matched_id"),
            fault.strip(),
        )

        old_device = {
            "brand":              brand,
            "model":              model,
            "year":               int(year or date.today().year),
            "original_price_lkr": float(orig_price),
            "condition":          condition or "fair",
            "fault":              fault,
            "variant":            (selected_device or {}).get("variant") or (selected_device or {}).get("id", ""),
            "profile_confirmed":  confirmation["confirmed"],
            "matched_id":         confirmation["matched_id"],
            "match_status":       confirmation["match_status"],
        }

        if run:
            with st.status("Running recommendation agents…", expanded=True) as status:
                st.write("Diagnose → safety guidance → repair estimate → repair/replace decision → verified replacement options")
                image_data_uri = None
                if uploaded_image is not None:
                    encoded = base64.b64encode(uploaded_image.getvalue()).decode("ascii")
                    image_data_uri = f"data:{uploaded_image.type};base64,{encoded}"
                state = run_pipeline(old_device, needs, float(budget),
                                     issue_description=fault, image_data_uri=image_data_uri,
                                     device_confirmation=confirmation)
                status.update(label="Analysis complete", state="complete")
            st.session_state.last_state = state
            st.session_state.last_fault = fault
            st.session_state.last_state_result_key = current_result_key

        state = st.session_state.last_state
        result_matches_current_device = (
            confirmation.get("confirmed")
            and st.session_state.get("last_state_result_key") == current_result_key
        )
        if state and result_matches_current_device:
            _render_results(state, st.session_state.get("last_fault", ""))
        else:
            st.markdown(f"""
<div class="glass-card" style="text-align:center;padding:2.25rem 1.75rem;margin:0.25rem 0;">
  <div class="icon-tile lg" style="margin:0 auto 0.8rem;">{icon("cpu", cls="glow")}</div>
  <p style="color:#e2eaf7;font-weight:700;font-size:1.05rem;margin:0 0 0.45rem;">
    Comprehensive Decision Analysis
  </p>
  <p style="color:#7a9abf;font-size:0.85rem;margin:0 auto 1.25rem;line-height:1.6;max-width:34rem;">
    Fill in your device details on the left to receive a step-by-step diagnosis, sourced repair estimate, and verified replacement recommendations.
  </p>
  <div class="diagnose-preview-grid" style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0.75rem;text-align:left;">
    <div class="glass-card" style="min-width:0;padding:1rem;">
      <div class="icon-tile" style="margin-bottom:0.55rem;">{icon("stethoscope")}</div>
      <p style="font-family:var(--font-display);font-weight:700;font-size:0.82rem;color:#fff;margin:0 0 0.15rem;">Diagnosis</p>
      <p style="font-size:0.72rem;color:#7a9abf;margin:0;">Identifies fault causes and safe DIY checks</p>
    </div>
    <div class="glass-card" style="min-width:0;padding:1rem;">
      <div class="icon-tile cyan" style="margin-bottom:0.55rem;">{icon("coins")}</div>
      <p style="font-family:var(--font-display);font-weight:700;font-size:0.82rem;color:#fff;margin:0 0 0.15rem;">Repair Costs</p>
      <p style="font-size:0.72rem;color:#7a9abf;margin:0;">Sourced repair price range and advice</p>
    </div>
    <div class="glass-card" style="min-width:0;padding:1rem;">
      <div class="icon-tile violet" style="margin-bottom:0.55rem;">{icon("phone")}</div>
      <p style="font-family:var(--font-display);font-weight:700;font-size:0.82rem;color:#fff;margin:0 0 0.15rem;">Replacements</p>
      <p style="font-size:0.72rem;color:#7a9abf;margin:0;">Best phone options matched to your budget</p>
    </div>
  </div>
  <p style="font-size:0.72rem;color:#7892b2;margin:1rem 0 0;">Pricing and repair estimates are subject to shop verification.</p>
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

"""HTML building blocks – REVIVAI theme.  All nav links use ?page= routing."""
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from src.ui.styles import get_hero_uri
from src.ui.icons import icon, logo_mark

# ── constants ─────────────────────────────────────────────────────
_DIM_LABELS = {
    "price_fit":   "Price fit",
    "performance": "Performance",
    "camera":      "Camera",
    "battery":     "Battery",
    "longevity":   "Longevity",
    "upgrade":     "Upgrade vs old",
    "similarity":  "Similarity",
}
_AGENT_SHORT = {
    "UserRequirementAgent":        "Requirements",
    "DeviceProfilingAgent":        "Device profile",
    "SpecificationRetrievalAgent": "Spec retrieval",
    "MarketResearchAgent":         "Market research",
    "ComparisonAgent":             "Comparison",
    "RecommendationAgent":         "Recommendation",
    "VerificationAgent":           "Verification",
    "ExplanationAgent":            "Explanation",
}

# ── helpers ───────────────────────────────────────────────────────
def _e(text: Any) -> str:
    return html.escape(str(text) if text is not None else "")

def fmt_lkr(value: float | int | None) -> str:
    if value is None:
        return "—"
    return f"LKR {float(value):,.0f}"


# ═══════════════════════════════════════════════════════════════════
#  SHARED HEADER  (announcement bar + nav)
# ═══════════════════════════════════════════════════════════════════

def _nav_links(active: str) -> str:
    """Render nav <a> links; active page gets the underline class."""
    pages = [
        ("home",    "Home"),
        ("diagnose","Diagnose Phone"),
        ("repair",  "Repair vs Replace"),
        ("phones",  "Find a Phone"),
        ("howit",   "How It Works"),
    ]
    return "".join(
        f'<a href="?page={key}" class="nav-link{" active" if key==active else ""}">{label}</a>'
        for key, label in pages
    )

def page_header(active: str = "home") -> str:
    """Returns announcement bar + sticky nav for any page."""
    return f"""
<div class="ann-bar">
  <span class="ann-side">{icon("sparkle")}Smarter Decisions. Longer Life for Your Device.</span>
  <span class="ann-side">{icon("cpu")}Powered by Multi-Agent AI Technology</span>
</div>
<nav class="revivai-nav">
  <a href="?page=home" class="nav-logo">
    <div class="r-badge">{logo_mark()}</div>
    <div>
      REVIVAI
      <span class="tagline">Repair · Replace · Recommend</span>
    </div>
  </a>
  <div class="nav-search">
    <span class="nav-search-icon">{icon("search")}</span>
    <input placeholder="Search for phone models…" />
  </div>
  <div class="nav-links">{_nav_links(active)}</div>
  <div class="nav-icons">
    <span title="Account">{icon("user")}</span>
    <span title="Wishlist">{icon("heart")}</span>
    <span title="Compare">{icon("bookmark")}</span>
  </div>
</nav>
"""

# backwards-compat alias used by app.py
def page_nav_bar(active: str = "home") -> str:
    return page_header(active)

def announcement_bar() -> str:
    return ""  # merged into page_header

def top_nav() -> str:
    return ""  # merged into page_header


# ═══════════════════════════════════════════════════════════════════
#  HERO
# ═══════════════════════════════════════════════════════════════════

def hero_landing() -> str:
    hero_img = get_hero_uri()
    # Inline background-image so it bypasses CSS sanitization (st.markdown renders this fine)
    bg_style = (
        f'style="background-image:url(\'{hero_img}\');'
        f'background-size:cover;background-position:center right;"'
    ) if hero_img else ''

    return f"""
<div class="hero-section" {bg_style}>
  <!-- dark overlay so text stays readable over the photo -->
  <div class="hero-overlay"></div>
  <div class="hero-left">
    <h1 class="hero-h1">
      Your Phone.<br>
      <span class="grad">A Smarter Next Move.</span>
    </h1>
    <p class="hero-sub">
      AI agents work together to diagnose faults,<br>
      estimate repair costs, and find the right replacement.
    </p>
    <div class="hero-btns">
      <a href="?page=diagnose" class="btn-primary">Diagnose My Phone {icon("arrow")}</a>
      <a href="?page=phones"   class="btn-secondary">Explore Phones {icon("arrow")}</a>
    </div>
    <div class="hero-trust">
      <span class="trust-item t-blue">{icon("cpu", solid=True)}Multi-agent analysis</span>
      <span class="trust-sep">|</span>
      <span class="trust-item t-violet">{icon("pin")}Sri Lankan prices</span>
      <span class="trust-sep">|</span>
      <span class="trust-item t-blue">{icon("shield", solid=True)}Clear recommendations</span>
    </div>
  </div>
</div>
"""



# ═══════════════════════════════════════════════════════════════════
#  PROBLEM CARDS  ("Start with your phone")
# ═══════════════════════════════════════════════════════════════════

def problem_cards() -> str:
    items = [
        ("phone-crack", "crack",   "Cracked Screen",       "Get advice & options"),
        ("battery",     "battery", "Battery Problems",     "Check solutions"),
        ("plug",        "charge",  "Charging Issues",      "Find the cause"),
        ("thermo",      "heat",    "Slow or Overheating",  "Get recommendations"),
    ]
    cards = "".join(f"""
<a href="?page=diagnose" class="problem-card">
  <div class="prob-icon {cls}">{icon(name, cls="glow")}</div>
  <div class="prob-text">
    <p class="prob-title">{_e(title)}</p>
    <p class="prob-sub">{_e(sub)}</p>
  </div>
  <span class="prob-arrow">{icon("chevron", stroke=2)}</span>
</a>""" for name, cls, title, sub in items)

    return f"""
<div class="section-wrap">
  <p class="section-label">Start with your phone</p>
</div>
<div class="problem-grid">{cards}</div>
"""


# ═══════════════════════════════════════════════════════════════════
#  RECOMMENDED PHONES  (horizontal cards, matching reference image)
# ═══════════════════════════════════════════════════════════════════

def recommended_phones(phones: list[dict] | None = None) -> str:
    if phones is not None:
        themes = ["theme-a", "theme-b", "theme-c", "theme-d"]
        cards = "".join(f"""
<a href="?page=phones" class="phone-card">
  <div class="phone-thumb {themes[i % len(themes)]}"><div class="phone-bezel"><div class="phone-camera"><i></i><i></i><i></i></div><div class="phone-screen"><span class="screen-shine"></span></div></div></div>
  <div class="phone-info">
    <p class="phone-price">{_e(fmt_lkr(p.get('price_lkr')))}</p>
    <p class="phone-name">{_e(p.get('brand', ''))} {_e(p.get('model', ''))}</p>
    <div class="spec-chips">
      {f'<span class="spec-chip">{_e(p.get("ram_gb"))} GB RAM</span>' if p.get('ram_gb') else ''}
      {f'<span class="spec-chip">{_e(p.get("storage_gb"))} GB storage</span>' if p.get('storage_gb') else ''}
    </div>
    <span class="btn-view">View details {icon("arrow")}</span>
  </div>
</a>""" for i, p in enumerate(phones[:4]))
        return f"""
<div class="section-wrap">
  <p class="section-label">Recommended Phones <span class="accent-line"></span></p>
  <p class="section-sub">Devices from the current specifications dataset</p>
</div>
<div class="phones-grid">{cards}</div>
"""

    phones = [
        {"theme":"theme-a","price":"LKR 89,900", "disp":'6.5" Display',"ram":"6GB RAM", "stor":"128GB Storage"},
        {"theme":"theme-b","price":"LKR 124,900","disp":'6.7" Display',"ram":"6GB RAM", "stor":"256GB Storage"},
        {"theme":"theme-c","price":"LKR 159,900","disp":'6.7" Display',"ram":"8GB RAM", "stor":"256GB Storage"},
        {"theme":"theme-d","price":"LKR 199,900","disp":'6.8" Display',"ram":"12GB RAM","stor":"512GB Storage"},
    ]
    cards = "".join(f"""
<a href="?page=diagnose" class="phone-card">
  <div class="phone-thumb {p['theme']}"><div class="phone-bezel"><div class="phone-camera"><i></i><i></i><i></i></div><div class="phone-screen"><span class="screen-shine"></span></div></div></div>
  <div class="phone-info">
    <p class="phone-price">{p['price']}</p>
    <div class="spec-chips">
      <span class="spec-chip">{icon("display")}{p['disp']}</span>
      <span class="spec-chip">{icon("cpu")}{p['ram']}</span>
      <span class="spec-chip">{icon("storage")}{p['stor']}</span>
    </div>
    <span class="btn-view">View Details {icon("arrow", stroke=2.2)}</span>
  </div>
</a>""" for p in phones)

    return f"""
<div class="section-wrap">
  <p class="section-label">Recommended Phones <span class="accent-line"></span></p>
  <p class="section-sub">Based on your budget and needs</p>
</div>
<div class="phones-grid">{cards}</div>
"""

# alias used by full_landing
def new_arrivals() -> str:
    return recommended_phones()


# ═══════════════════════════════════════════════════════════════════
#  CTA / AGENT STRIP
# ═══════════════════════════════════════════════════════════════════

def cta_agent_strip() -> str:
    return f"""
<div class="cta-wrap">
<div class="cta-strip">
  <div class="cta-headline">
    Repair it. Replace it.<br>
    <span class="grad">Know why.</span>
  </div>
  <div class="agent-feature">
    <div class="agent-icon">{icon("stethoscope", cls="glow")}</div>
    <div>
      <p class="agent-name">Diagnosis Agent</p>
      <p class="agent-desc">Find the problem</p>
    </div>
  </div>
  <div class="agent-feature">
    <div class="agent-icon cyan">{icon("coins", cls="glow")}</div>
    <div>
      <p class="agent-name">Cost Analyst</p>
      <p class="agent-desc">Compare the cost</p>
    </div>
  </div>
  <div class="agent-feature">
    <div class="agent-icon purple">{icon("phone", cls="glow")}</div>
    <div>
      <p class="agent-name">Phone Match Agents</p>
      <p class="agent-desc">Find the best options</p>
    </div>
  </div>
</div>
</div>
"""


# ═══════════════════════════════════════════════════════════════════
#  TRUST BAR
# ═══════════════════════════════════════════════════════════════════

def trust_bar() -> str:
    items = [
        ("shield", "tb-blue",   "Repair cost clarity"),
        ("pin",    "tb-blue",   "Local price context"),
        ("chat",   "tb-blue",   "Recommendations explained"),
        ("star",   "tb-violet", "Your choice comes first"),
    ]
    sep = '<span class="tb-sep">|</span>'
    body = sep.join(
        f'<span class="trust-bar-item {tone}">{icon(name, solid=True)}{label}</span>'
        for name, tone, label in items
    )
    return f'<div class="trust-bar">{body}</div>'


# ═══════════════════════════════════════════════════════════════════
#  FULL LANDING  (home page)
# ═══════════════════════════════════════════════════════════════════

def full_landing(phones: list[dict] | None = None) -> str:
    return (
        page_header("home")
        + hero_landing()
        + problem_cards()
        + recommended_phones(phones)
        + cta_agent_strip()
        + trust_bar()
    )


# ═══════════════════════════════════════════════════════════════════
#  FIND A PHONE PAGE  (extended phone listing)
# ═══════════════════════════════════════════════════════════════════

def new_arrivals_full(phones: list[dict] | None = None) -> str:
    if phones is not None:
        themes = ["theme-a", "theme-b", "theme-c", "theme-d"]
        cards = "".join(f"""
<article class="phone-card catalog-card">
  <div class="catalog-visual {themes[i % len(themes)]}">
    <div class="phone-bezel"><div class="phone-camera"><i></i><i></i><i></i></div><div class="phone-screen"><span class="screen-shine"></span></div></div>
  </div>
  <div class="phone-info">
    <p class="brand-tag">{_e(p.get('brand', ''))}{(' · ' + _e(p.get('variant', ''))) if p.get('variant') else ''}</p>
    <p class="phone-name">{_e(p.get('model', 'Phone'))}</p>
    <p class="phone-price">{_e(fmt_lkr(p.get('price_lkr')))}</p>
    <div class="spec-chips">
      {f'<span class="spec-chip">{_e(p.get("ram_gb"))} GB RAM</span>' if p.get('ram_gb') else ''}
      {f'<span class="spec-chip">{_e(p.get("storage_gb"))} GB storage</span>' if p.get('storage_gb') else ''}
      {f'<span class="spec-chip">{_e(p.get("display_type"))}</span>' if p.get('display_type') else ''}
      {f'<span class="spec-chip">{_e(p.get("battery_mah"))} mAh</span>' if p.get('battery_mah') else ''}
    </div>
    <p class="catalog-note">Price source: {_e(p.get('price_source') or p.get('source') or 'provided dataset')}
      {(' · checked ' + _e(p.get('retrieved_at') or p.get('price_checked_at'))) if (p.get('retrieved_at') or p.get('price_checked_at')) else ''}
      {(' · ' + f'<a href="{_e(p.get("source_url") or p.get("price_source_url"))}" target="_blank" rel="noopener">open source</a>') if str(p.get('source_url') or p.get('price_source_url') or '').startswith(('https://', 'http://')) else ''}
    </p>
  </div>
</article>""" for i, p in enumerate(phones))
        return f"""
<div class="section-wrap">
  <p class="section-label">Find a Phone <span class="accent-line"></span></p>
  <p class="section-sub">Browse devices from your specifications dataset. Prices and availability should be confirmed with sellers.</p>
</div>
<div class="phones-grid catalog-grid">{cards}</div>
"""

    phones = [
        {"badge":"NEW",  "bc":"#1a8fff","name":"Samsung Galaxy S25", "brand":"Samsung",
         "price":"LKR 189,900","disp":'6.2" Dynamic AMOLED',"ram":"12GB RAM","stor":"256GB","rating":"4.8"},
        {"badge":"HOT",  "bc":"#ef4444","name":"iPhone 16 Pro",       "brand":"Apple",
         "price":"LKR 259,900","disp":'6.3" Super Retina',  "ram":"8GB RAM", "stor":"256GB","rating":"4.9"},
        {"badge":"NEW",  "bc":"#1a8fff","name":"Xiaomi 14T Pro",      "brand":"Xiaomi",
         "price":"LKR 149,900","disp":'6.67" AMOLED 144Hz', "ram":"12GB RAM","stor":"512GB","rating":"4.7"},
        {"badge":"SALE", "bc":"#a855f7","name":"OnePlus 13",          "brand":"OnePlus",
         "price":"LKR 134,900","disp":'6.82" ProXDR LTPO',  "ram":"16GB RAM","stor":"512GB","rating":"4.8"},
        {"badge":"NEW",  "bc":"#1a8fff","name":"Google Pixel 9 Pro",  "brand":"Google",
         "price":"LKR 219,900","disp":'6.3" OLED 120Hz',    "ram":"12GB RAM","stor":"256GB","rating":"4.8"},
        {"badge":"HOT",  "bc":"#ef4444","name":"Samsung Galaxy A55",  "brand":"Samsung",
         "price":"LKR 94,900", "disp":'6.6" Super AMOLED',  "ram":"8GB RAM", "stor":"256GB","rating":"4.6"},
        {"badge":"DEAL", "bc":"#22c55e","name":"Xiaomi Redmi Note 13","brand":"Xiaomi",
         "price":"LKR 54,900", "disp":'6.67" AMOLED',       "ram":"8GB RAM", "stor":"256GB","rating":"4.5"},
        {"badge":"NEW",  "bc":"#1a8fff","name":"OnePlus Nord CE 4",   "brand":"OnePlus",
         "price":"LKR 79,900", "disp":'6.7" AMOLED 120Hz',  "ram":"8GB RAM", "stor":"128GB","rating":"4.5"},
    ]
    themes = ["theme-a","theme-b","theme-c","theme-d"]
    cards = "".join(f"""
<a href="?page=diagnose" class="phone-card" style="flex-direction:column;align-items:stretch;gap:0.5rem;">
  <div style="display:flex;justify-content:space-between;align-items:center;width:100%;">
    <div class="phone-thumb {themes[i % 4]}" style="min-height:auto;width:auto;">
      <div class="phone-bezel" style="width:36px;height:68px;border-radius:8px;"><div class="phone-camera"><i></i><i></i><i></i></div><div class="phone-screen"><span class="screen-shine"></span></div></div>
    </div>
    <span style="font-size:0.65rem;font-weight:700;padding:0.18rem 0.45rem;border-radius:5px;
                 background:{p['bc']}22;color:{p['bc']};border:1px solid {p['bc']}44;">{p['badge']}</span>
  </div>
  <p class="phone-price" style="margin:0;">{p['price']}</p>
  <p class="brand-tag">{p['brand']}</p>
  <p class="phone-name">{p['name']}</p>
  <div class="spec-chips">
    <span class="spec-chip">{icon("display")}{p['disp']}</span>
    <span class="spec-chip">{icon("cpu")}{p['ram']}</span>
    <span class="spec-chip">{icon("storage")}{p['stor']}</span>
  </div>
  <div style="display:flex;justify-content:space-between;align-items:center;margin-top:0.25rem;">
    <span class="rating">{icon("star", solid=True)}{p['rating']}</span>
    <span class="btn-view">Analyze {icon("arrow", stroke=2.2)}</span>
  </div>
</a>""" for i, p in enumerate(phones))

    return f"""
<div class="section-wrap">
  <p class="section-label">Find a Phone <span class="accent-line"></span></p>
  <p class="section-sub">Browse latest arrivals at Sri Lankan prices — click any card to run AI analysis</p>
</div>
<div class="phones-grid" style="grid-template-columns:repeat(4,1fr);">{cards}</div>
"""


# ═══════════════════════════════════════════════════════════════════
#  RESULTS-PAGE COMPONENTS
# ═══════════════════════════════════════════════════════════════════

def metric_strip(
    budget: float | None,
    n_candidates: int,
    n_recs: int,
    top_score: float | None,
    verified: bool,
) -> str:
    bstr = fmt_lkr(budget)
    ts   = f"{top_score}/100" if top_score is not None else "—"
    return f"""
<div class="metric-strip">
  <div class="metric-box">
    <div class="metric-label">Budget</div>
    <div class="metric-value">{_e(bstr)}</div>
  </div>
  <div class="metric-box">
    <div class="metric-label">Scored</div>
    <div class="metric-value">{n_candidates}</div>
  </div>
  <div class="metric-box">
    <div class="metric-label">Shortlist</div>
    <div class="metric-value accent">{n_recs}</div>
  </div>
  <div class="metric-box">
    <div class="metric-label">Top fit</div>
    <div class="metric-value accent">{_e(ts)}</div>
  </div>
</div>
<div style="margin-bottom:1rem;">{verification_badge(verified)}</div>
"""


def verification_badge(all_passed: bool) -> str:
    if all_passed:
        return f'<span class="verify-ok">{icon("check-circle", size=18)}Verification passed</span>'
    return f'<span class="verify-ok verify-warn">{icon("alert", size=18)}Some picks adjusted after verification</span>'


def old_device_summary(profile: dict, fault: str) -> str:
    chips = [
        f"{profile.get('brand','')} {profile.get('model','')}".strip(),
        profile.get("variant", ""),
        f"~{profile.get('age_years','?')} yrs",
        profile.get("condition",""),
        f"Residual {fmt_lkr(profile.get('estimated_residual_lkr'))}",
    ]
    if fault:
        chips.append(f"Fault: {fault}")
    for key, label in (("ram_gb", "GB RAM"), ("storage_gb", "GB storage"),
                       ("display_type", ""), ("battery_mah", "mAh")):
        value = profile.get(key)
        if value not in (None, ""):
            chips.append(f"{value} {label}".strip())
    if profile.get("profile_confirmed"):
        chips.append("Variant confirmed")
    inner = "".join(f'<span class="chip">{_e(c)}</span>' for c in chips if c and c.strip())
    return f'<div class="old-device-chip">{inner}</div>'


def dimension_bars(dimensions: dict[str, float]) -> str:
    rows = ""
    for key, label in _DIM_LABELS.items():
        val = dimensions.get(key, 0.0)
        pct = max(0, min(100, val * 100))
        rows += f"""
<div class="dim-row">
  <div class="dim-label"><span>{_e(label)}</span><span>{pct:.0f}%</span></div>
  <div class="dim-bar-bg"><div class="dim-bar-fill" style="width:{pct:.1f}%;"></div></div>
</div>"""
    return rows


def recommendation_card(rec: dict, rank: int) -> str:
    top  = rank == 1
    cls  = "rec-card top" if top else "rec-card"
    over = rec.get("over_budget")
    badge = ' <span style="color:#fde047;font-size:0.75rem;">· over budget</span>' if over else ""
    dims  = dimension_bars(rec.get("dimensions", {}))
    verdict = rec.get("verdict_vs_old", "")
    product = rec.get("product", {})
    specs = " · ".join(
        value for value in (
            f"{product['ram_gb']} GB RAM" if product.get("ram_gb") else "",
            f"{product['storage_gb']} GB storage" if product.get("storage_gb") else "",
            f"{product['display_type']}" if product.get("display_type") else "",
            f"{product['battery_mah']} mAh" if product.get("battery_mah") else "",
        ) if value
    )
    spec_line = f'<p class="rec-specs">{_e(specs)}</p>' if specs else ""
    source = product.get("price_source") or "provided dataset"
    source_url = product.get("source_url")
    if not isinstance(source_url, str) or not source_url.startswith(("https://", "http://")):
        source_url = None
    checked_at = product.get("retrieved_at")
    source_label = (f'<a href="{_e(source_url)}" target="_blank" rel="noopener">{_e(source)}</a>'
                    if source_url else _e(source))
    provenance = f'<p class="rec-source">Price source: {source_label}'
    if checked_at:
        provenance += f' · checked {_e(checked_at)}'
    provenance += "</p>"
    vline = (
        f'<p style="font-size:0.82rem;color:#7a9abf;margin:0.75rem 0 0;">'
        f'Verdict vs old: <strong style="color:#c5d5ed;">{_e(verdict)}</strong></p>'
        if verdict else ""
    )
    return f"""
<div class="{cls}">
  <div class="rec-rank">{rank}</div>
  <h3 class="rec-name">{_e(rec.get("name","Unknown"))}</h3>
  <div class="rec-price">{_e(fmt_lkr(rec.get("price_lkr")))}{badge}</div>
  {spec_line}
  {provenance}
  <div style="display:inline-flex;align-items:baseline;gap:0.15rem;">
    <span class="rec-score-num">{rec.get("score",0)}</span>
    <span class="rec-score-label">/ 100 fit score</span>
  </div>
  <div style="margin-top:1rem;">{dims}</div>
  {vline}
</div>
"""


def agent_timeline(trace: list[dict]) -> str:
    items = ""
    for step in trace:
        agent = step.get("agent","Agent")
        short = _AGENT_SHORT.get(agent, agent.replace("Agent",""))
        action= step.get("action","")
        items += f"""
<div class="tl-item">
  <div class="tl-dot"></div>
  <div class="tl-agent">{_e(short)}</div>
  <div class="tl-action">{_e(action)}</div>
</div>"""
    return (
        '<div class="section-head">Agent collaboration</div>'
        f'<div class="glass-card"><div class="timeline">{items}</div></div>'
    )


def feature_cards() -> str:
    """Backward-compat stub."""
    return ""


def trace_details_json(trace: list[dict]) -> str:
    return json.dumps(trace, default=str, indent=2)

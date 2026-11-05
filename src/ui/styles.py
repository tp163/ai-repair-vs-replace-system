"""Global CSS injected into the Streamlit app – REVIVAI theme."""
import base64
from pathlib import Path


def get_hero_uri() -> str:
    """Return base64 data-URI for the hero phones image."""
    try:
        p = Path(__file__).resolve().parents[2] / "static" / "hero_phones.jpg"
        return f"data:image/jpeg;base64,{base64.b64encode(p.read_bytes()).decode()}"
    except Exception:
        return ""


def inject_styles() -> None:
    import streamlit as st

    st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
/* ═══════════════════════════════════════════════
   TOKENS
═══════════════════════════════════════════════ */
:root {
  --navy:        #040b18;
  --navy-2:      #060e1f;
  --card-bg:     rgba(7,16,38,0.78);
  --card-border: rgba(80,140,255,0.22);
  --blue:        #3b9eff;
  --blue-glow:   rgba(59,158,255,0.4);
  --purple:      #8b5cf6;
  --cyan:        #22d3ee;
  --text:        #e8eef8;
  --muted:       #8aa3c4;
  --font-display: "Plus Jakarta Sans", "Inter", system-ui, sans-serif;
  --font-body:    "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
}

/* ═══════════════════════════════════════════════
   BASE / RESET
═══════════════════════════════════════════════ */
html, body, .stApp {
  background:
    radial-gradient(1200px 500px at 80% -10%, rgba(88,40,180,0.28), transparent 55%),
    radial-gradient(900px 420px at 10% 0%, rgba(20,70,180,0.22), transparent 50%),
    var(--navy) !important;
  font-family: var(--font-body) !important;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  color: var(--text) !important;
}
html, body {
  overflow-y: auto !important;
  height: auto !important;
}
.stApp,
[data-testid="stAppViewContainer"] {
  overflow: auto !important;
  min-height: 100vh !important;
}
[data-testid="stMain"], .stMain {
  overflow: visible !important;
  height: auto !important;
}
/* Hide ALL Streamlit chrome */
#MainMenu, footer,
header[data-testid="stHeader"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"] {
  display: none !important;
  visibility: hidden !important;
  width: 0 !important;
}
.block-container {
  padding: 0 !important;
  max-width: 100% !important;
}
div[data-testid="stHtml"], .stHtml, .stElementContainer {
  width: 100% !important;
}
/* Streamlit hard-sets "Source Sans" on its markdown wrapper, which beat the
   .stApp rule above. Re-assert the body font there so children inherit it. */
[data-testid="stMarkdownContainer"], [data-testid="stHtml"], .stMarkdown { font-family: var(--font-body) !important; }
h1,h2,h3 { font-family: var(--font-display) !important; }
.stApp a { color: inherit !important; text-decoration: none !important; }
.stApp a:hover { color: inherit !important; text-decoration: none !important; }
/* ── ICON SYSTEM ── duotone: tinted body (.f) + rounded stroke ── */
.ico { display: block; flex-shrink: 0; width: 1em; height: 1em; overflow: visible; }
.ico .f { fill: currentColor; fill-opacity: 0.16; stroke: none; }
.ico .d { fill: currentColor; stroke: none; }
.ico.solid .f { fill-opacity: 0.92; }
.ico.solid .k { stroke: #071433; }
.ico.solid .d { fill: #071433; }
.ico.glow { filter: drop-shadow(0 0 5px color-mix(in srgb, currentColor 55%, transparent)); }
.logo-r { width: 22px; height: 22px; color: #fff; }
.logo-r .node { fill: #67e8f9; }
.btn-primary .ico, .btn-secondary .ico, .btn-view .ico { width: 1.1em; height: 1.1em; }

/* ═══════════════════════════════════════════════
   ANNOUNCEMENT BAR
═══════════════════════════════════════════════ */
.ann-bar {
  width: 100%;
  background: linear-gradient(90deg,#0a1a55 0%, #1d3ea8 22%, #6d28d9 50%, #1d3ea8 78%, #0a1a55 100%);
  border-bottom: 1px solid rgba(165,180,255,0.22);
  padding: 0.42rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.78rem;
  color: #dce7ff;
  letter-spacing: 0.02em;
  box-sizing: border-box;
  box-shadow: 0 0 24px rgba(99,80,255,0.25);
}
.ann-bar .ico { width: 15px; height: 15px; color: #c7d7ff; }
.ann-side { display: flex; align-items: center; gap: 0.45rem; }
.ann-dot {
  display: inline-block;
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #67e8f9;
  box-shadow: 0 0 8px rgba(103,232,249,0.8);
  margin-right: 0.15rem;
}

/* ═══════════════════════════════════════════════
   NAV BAR
═══════════════════════════════════════════════ */
.revivai-nav {
  width: 100%;
  background: rgba(4,11,24,0.92);
  backdrop-filter: blur(22px);
  border-bottom: 1px solid rgba(80,140,255,0.16);
  padding: 0.62rem 1.75rem;
  display: flex;
  align-items: center;
  gap: 1.1rem;
  box-sizing: border-box;
  position: relative;
  z-index: 40;
}
.nav-logo {
  font-family: var(--font-display);
  font-weight: 800;
  font-size: 1.12rem;
  color: #fff !important;
  display: flex;
  align-items: center;
  gap: 0.55rem;
  text-decoration: none !important;
  flex-shrink: 0;
  letter-spacing: 0.04em;
}
.nav-logo .r-badge {
  width: 34px; height: 34px;
  background: linear-gradient(145deg,#2563eb,#7c3aed);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(80,80,255,0.35), inset 0 0 0 1px rgba(255,255,255,0.12);
}
.nav-logo .tagline {
  font-size: 0.58rem; font-weight: 400;
  color: var(--muted); display: block; letter-spacing: 0.06em;
  text-transform: none;
}
.nav-search {
  flex: 0 1 240px;
  max-width: 260px;
  position: relative;
  min-width: 160px;
}
.nav-search input {
  width: 100%;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 999px;
  padding: 0.48rem 0.95rem 0.48rem 2.2rem;
  color: #c5d5ed; font-size: 0.8rem;
  outline: none; box-sizing: border-box;
}
.nav-search input:focus { border-color: rgba(59,158,255,0.45); box-shadow: 0 0 0 3px rgba(59,158,255,0.12); }
.nav-search-icon {
  position: absolute; left: 0.8rem; top: 50%;
  transform: translateY(-50%);
  width: 14px; height: 14px; color: var(--muted);
  display: flex;
}
.nav-search-icon .ico { width: 14px; height: 14px; }
.nav-links {
  display: flex; align-items: center; gap: 0.1rem;
  flex: 0 0 auto;
  margin-left: auto;
}
.nav-link {
  padding: 0.38rem 0.8rem;
  font-size: 0.84rem; font-weight: 500;
  color: var(--muted) !important;
  text-decoration: none !important;
  border-bottom: 2px solid transparent;
  transition: color 0.15s;
  white-space: nowrap;
}
.nav-link:hover { color: #e2eaf7 !important; }
.nav-link.active { color: #fff !important; }
.nav-icons {
  display: flex; align-items: center; gap: 0.85rem;
  color: var(--muted);
  flex-shrink: 0;
}
.nav-icons span {
  width: 32px; height: 32px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 8px;
  cursor: pointer;
  transition: color 0.15s, background 0.15s;
}
.nav-icons span:hover { color: #fff; background: rgba(255,255,255,0.06); }
.nav-icons .ico { width: 19px; height: 19px; }

/* ═══════════════════════════════════════════════
   HERO SECTION  (full-width background image)
═══════════════════════════════════════════════ */
.hero-section {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  min-height: 480px;
  background: var(--navy-2);
}

/* dark gradient overlay — left side dark for text, right fades to image */
.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    105deg,
    rgba(4,11,24,0.88)  0%,
    rgba(4,11,24,0.62)  42%,
    rgba(4,11,24,0.22)  68%,
    rgba(4,11,24,0.06) 100%
  );
  z-index: 1;
}

.hero-left {
  padding: 3.6rem 2.75rem 3.2rem;
  position: relative;
  z-index: 2;
  max-width: 700px;
}

@keyframes floatY {
  0%,100% { transform: translateY(0px); }
  50%      { transform: translateY(-12px); }
}

.hero-h1 {
  font-family: var(--font-display);
  font-size: clamp(2.35rem,4.2vw,3.45rem);
  font-weight: 800;
  line-height: 1.08;
  letter-spacing: -0.032em;
  color: #fff;
  margin: 0 0 0.3rem;
}
.hero-h1 .grad {
  background: linear-gradient(90deg,#3b9eff 0%, #7c6bff 48%, #c084fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-sub {
  color: #9eb4d4;
  font-size: 0.98rem;
  line-height: 1.7;
  max-width: 420px;
  margin: 0.7rem 0 1.5rem;
}
.hero-btns { display: flex; gap: 0.8rem; flex-wrap: wrap; }
.btn-primary {
  display: inline-flex; align-items: center; gap: 0.45rem;
  background: linear-gradient(135deg,#2563eb,#7c3aed);
  color: #fff !important; font-weight: 700; font-size: 0.9rem;
  padding: 0.7rem 1.45rem;
  border-radius: 999px; border: none;
  text-decoration: none !important; cursor: pointer;
  box-shadow: 0 6px 24px rgba(80,80,255,0.42);
  transition: transform 0.15s, box-shadow 0.15s;
  white-space: nowrap;
}
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 32px rgba(80,80,255,0.55); color:#fff !important; }
.btn-secondary {
  display: inline-flex; align-items: center; gap: 0.45rem;
  background: rgba(8,16,40,0.35);
  color: #d7e4f7 !important; font-weight: 600; font-size: 0.9rem;
  padding: 0.66rem 1.4rem;
  border-radius: 999px;
  border: 1px solid rgba(180,210,255,0.28);
  text-decoration: none !important; cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
  white-space: nowrap;
  backdrop-filter: blur(8px);
}
.btn-secondary:hover { border-color: rgba(59,158,255,0.6); color: #fff !important; background: rgba(20,40,80,0.45); }
.hero-trust {
  display: flex; gap: 0.95rem; flex-wrap: wrap;
  margin-top: 1.35rem; font-size: 0.78rem; color: var(--muted);
  align-items: center;
}
.trust-sep { color: rgba(255,255,255,0.18); }
.trust-item { display: flex; align-items: center; gap: 0.45rem; color: #dbe6fa; font-weight: 500; }
.trust-item .ico { width: 16px; height: 16px; }
.trust-item.t-blue .ico   { color: #3b9eff; }
.trust-item.t-violet .ico { color: #a78bfa; }
.trust-dot {
  width: 8px; height: 8px; border-radius: 50%; display: inline-block;
}
.trust-dot.blue   { background: var(--blue); box-shadow: 0 0 8px var(--blue-glow); }
.trust-dot.purple { background: #a855f7; }
.trust-dot.cyan   { background: var(--cyan); }

/* ═══════════════════════════════════════════════
   SECTION WRAPPER
═══════════════════════════════════════════════ */
.section-wrap { padding: 1.65rem 2.5rem 0; }
.section-label {
  font-family: var(--font-display);
  font-size: 1.28rem; font-weight: 700;
  color: #fff; margin: 0 0 0.25rem;
  letter-spacing: -0.015em;
  display: flex; align-items: center; gap: 0.5rem;
}
.accent-line {
  display: inline-block; width: 36px; height: 2px;
  background: linear-gradient(90deg,#1a6fff,#7c3aed);
  border-radius: 4px; vertical-align: middle;
}
.section-sub { font-size: 0.8rem; color: var(--muted); margin: 0 0 1rem; }

/* ═══════════════════════════════════════════════
   PROBLEM CARDS  (Start with your phone)
═══════════════════════════════════════════════ */
.problem-grid {
  display: grid;
  grid-template-columns: repeat(4,1fr);
  gap: 0.85rem;
  padding: 0.85rem 2.5rem 1.6rem;
}
.problem-card {
  background: linear-gradient(180deg, rgba(12,24,52,0.92), rgba(6,14,34,0.92));
  border: 1px solid rgba(80,150,255,0.22);
  border-radius: 16px;
  padding: 0.85rem 1.05rem;
  display: flex; align-items: center; gap: 0.85rem;
  cursor: pointer; text-decoration: none !important;
  color: inherit !important;
  transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 8px 24px rgba(0,0,0,0.22);
}
.problem-card:hover {
  border-color: rgba(80,170,255,0.55);
  transform: translateY(-3px);
  box-shadow: 0 12px 32px rgba(26,143,255,0.16);
}
.prob-icon {
  width: 44px; height: 44px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  color: #4aa8ff;
}
.prob-icon .ico { width: 36px; height: 36px; }
.prob-icon.crack   { color: #5aa9ff; }
.prob-icon.battery { color: #34d399; }
.prob-icon.charge  { color: #38bdf8; }
.prob-icon.heat    { color: #fb7185; }
.prob-text { flex: 1; min-width: 0; }
.prob-title {
  font-family: var(--font-display);
  font-weight: 700; font-size: 0.95rem;
  color: #eef3fb; margin: 0 0 0.12rem;
}
.prob-sub { font-size: 0.73rem; color: var(--muted); margin: 0; }
.prob-arrow {
  width: 28px; height: 28px; flex-shrink: 0; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: #9fd2ff;
  border: 1px solid rgba(125,190,255,0.38);
  background: rgba(60,120,255,0.08);
  transition: background 0.2s, border-color 0.2s, color 0.2s;
}
.prob-arrow .ico { width: 14px; height: 14px; }
.problem-card:hover .prob-arrow { background: rgba(60,140,255,0.28); border-color: rgba(140,210,255,0.8); color: #fff; }

/* ═══════════════════════════════════════════════
   RECOMMENDED PHONES  (horizontal cards)
═══════════════════════════════════════════════ */
.phones-grid {
  display: grid;
  grid-template-columns: repeat(4,1fr);
  gap: 1rem;
  padding: 0 2.5rem 2rem;
}
.phone-card {
  background: linear-gradient(180deg, rgba(12,24,52,0.94), rgba(6,14,34,0.94));
  border: 1px solid rgba(80,150,255,0.2);
  border-radius: 16px;
  padding: 0.9rem 0.95rem;
  display: flex; gap: 0.85rem; align-items: center;
  cursor: pointer; text-decoration: none !important;
  color: inherit !important;
  transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 8px 24px rgba(0,0,0,0.22);
  min-height: 132px;
}
.phone-card:hover {
  border-color: rgba(80,170,255,0.5);
  transform: translateY(-3px);
  box-shadow: 0 14px 36px rgba(26,143,255,0.16);
}
.phone-thumb {
  width: 58px; flex-shrink: 0;
  background: transparent;
  border: none;
  min-height: 0;
  display: flex; align-items: center; justify-content: center;
}
.phone-bezel {
  width: 46px; height: 86px;
  border-radius: 10px;
  background: #0a1020;
  border: 2px solid rgba(148,163,184,0.35);
  box-shadow: 0 10px 18px rgba(0,0,0,0.4), 0 0 14px rgba(59,158,255,0.12);
  padding: 3px;
}
.phone-screen { width: 100%; height: 100%; border-radius: 6px; }
.theme-a .phone-screen { background: radial-gradient(circle at 32% 28%, #e9d5ff, #7c3aed 48%, #1e1b4b); }
.theme-b .phone-screen { background: linear-gradient(160deg, #bfdbfe, #64748b 42%, #1e293b); }
.theme-c .phone-screen { background: radial-gradient(circle at 40% 22%, #6ee7b7, #047857 55%, #022c22); }
.theme-d .phone-screen { background: radial-gradient(circle at 38% 28%, #f5d0fe, #a21caf 48%, #3b0764); }
.phone-info { flex: 1; min-width: 0; }
.phone-price {
  font-family: var(--font-display);
  font-weight: 800; font-size: 1.08rem; color: #fff;
  margin: 0 0 0.5rem;
  letter-spacing: -0.015em;
  font-variant-numeric: tabular-nums;
}
.phone-spec {
  font-size: 0.72rem; color: var(--muted);
  display: flex; align-items: center; gap: 0.35rem;
  margin-bottom: 0.22rem;
}
.phone-spec .ico { width: 12px; height: 12px; color: #7dd3fc; }
.spec-chips { display: flex; flex-wrap: wrap; gap: 0.3rem; margin: 0 0 0.6rem; }
.spec-chip {
  display: inline-flex; align-items: center; gap: 0.3rem;
  font-size: 0.66rem; font-weight: 500; color: #bccbe6;
  padding: 0.2rem 0.5rem; border-radius: 6px;
  background: rgba(40,80,170,0.16);
  border: 1px solid rgba(120,170,255,0.22);
  white-space: nowrap;
}
.spec-chip .ico { width: 12px; height: 12px; color: #7dd3fc; }
.phone-card .brand-tag {
  font-size: 0.68rem; font-weight: 600; color: var(--muted);
  text-transform: none; letter-spacing: 0.04em; margin: 0; line-height: 1.2;
}
.phone-card .phone-name { font-size: 0.9rem; font-weight: 600; color: #e8eef8; margin: 0; line-height: 1.3; }
.rating { display: inline-flex; align-items: center; gap: 0.28rem; font-size: 0.78rem; font-weight: 600; color: #fbbf24; }
.rating .ico { width: 13px; height: 13px; }
.spec-dot {
  width: 4px; height: 4px; border-radius: 50%;
  background: rgba(26,143,255,0.6); flex-shrink: 0;
}
.phone-brand-dots {
  font-size: 0.55rem; color: rgba(125,211,252,0.4);
  letter-spacing: 0.14em; margin: 0.2rem 0 0.45rem;
}
.btn-view {
  display: inline-flex; align-items: center; gap: 0.3rem;
  background: linear-gradient(135deg,#2563eb,#4f46e5);
  color: #fff !important; font-size: 0.74rem; font-weight: 600;
  padding: 0.4rem 0.85rem;
  border-radius: 8px; border: none; cursor: pointer;
  text-decoration: none !important;
  box-shadow: 0 4px 14px rgba(37,99,235,0.35);
  transition: opacity 0.15s, transform 0.15s;
}
.btn-view:hover { opacity: 0.92; color: #fff !important; transform: translateY(-1px); }

/* ═══════════════════════════════════════════════
   CTA / AGENT STRIP
═══════════════════════════════════════════════ */
.cta-wrap { padding: 0 2.5rem 0.4rem; }
.cta-strip {
  position: relative;
  overflow: hidden;
  background: linear-gradient(100deg, rgba(8,16,42,0.96) 0%, rgba(28,22,72,0.72) 55%, rgba(10,18,48,0.96) 100%);
  border: 1px solid rgba(100,140,255,0.28);
  border-radius: 22px;
  padding: 1.55rem 1.75rem;
  display: grid;
  grid-template-columns: 1.25fr 1fr 1fr 1fr;
  gap: 1.25rem; align-items: center;
  box-shadow: 0 0 40px rgba(88,70,220,0.14);
}
.cta-strip::after {
  content: "";
  position: absolute; right: -50px; top: -60px;
  width: 280px; height: 200px;
  background: radial-gradient(circle, rgba(139,92,246,0.38), transparent 70%);
  pointer-events: none;
}
.cta-headline {
  font-family: var(--font-display);
  font-size: 1.55rem; font-weight: 800;
  line-height: 1.18; color: #fff;
  position: relative; z-index: 1;
}
.cta-headline .grad {
  background: linear-gradient(90deg,#60a5fa,#a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent; background-clip: text;
}
.agent-feature { display: flex; align-items: center; gap: 0.85rem; position: relative; z-index: 1; }
.agent-icon {
  width: 52px; height: 52px; flex-shrink: 0;
  border: 1.5px solid rgba(96,165,250,0.6);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: radial-gradient(circle at 50% 35%, rgba(59,130,246,0.22), rgba(8,16,44,0.9));
  color: #60a5fa;
  box-shadow: 0 0 0 5px rgba(59,130,246,0.07), 0 0 20px rgba(59,130,246,0.35);
}
.agent-icon .ico { width: 26px; height: 26px; }
.agent-icon.purple { border-color: rgba(167,139,250,0.65); color: #a78bfa; background: radial-gradient(circle at 50% 35%, rgba(124,58,237,0.24), rgba(14,10,40,0.9)); box-shadow: 0 0 0 5px rgba(139,92,246,0.08), 0 0 20px rgba(139,92,246,0.38); }
.agent-icon.cyan   { border-color: rgba(34,211,238,0.6);  color: #22d3ee; background: radial-gradient(circle at 50% 35%, rgba(34,211,238,0.18), rgba(6,18,40,0.9)); box-shadow: 0 0 0 5px rgba(34,211,238,0.07), 0 0 20px rgba(34,211,238,0.3); }
.agent-name {
  font-family: var(--font-display);
  font-weight: 700; font-size: 0.95rem; color: #eef3fb; margin: 0 0 0.12rem;
}
.agent-desc { font-size: 0.78rem; color: var(--muted); margin: 0; }

/* ═══════════════════════════════════════════════
   TRUST BAR
═══════════════════════════════════════════════ */
.trust-bar {
  border-top: 1px solid rgba(255,255,255,0.06);
  padding: 0.95rem 2.5rem 1.15rem;
  display: flex; gap: 0; flex-wrap: wrap;
  justify-content: space-around; align-items: center;
  background: transparent;
}
.trust-bar-item {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.8rem; color: #9eb4d4; padding: 0.25rem 0.5rem;
}
.trust-bar-item .ico { width: 18px; height: 18px; }
.trust-bar-item.tb-blue .ico   { color: #4f8ff7; }
.trust-bar-item.tb-violet .ico { color: #7c6bff; }
.tb-sep { color: rgba(255,255,255,0.14); padding: 0 0.5rem; }

/* ═══════════════════════════════════════════════
   ICON TILES  (icons on inner pages)
═══════════════════════════════════════════════ */
.icon-tile {
  width: 42px; height: 42px; flex-shrink: 0;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: #60a5fa;
  background: radial-gradient(circle at 30% 20%, rgba(59,130,246,0.28), rgba(8,18,44,0.9));
  border: 1px solid rgba(96,165,250,0.34);
  box-shadow: 0 0 18px rgba(59,130,246,0.16);
}
.icon-tile .ico { width: 22px; height: 22px; }
.icon-tile.sm { width: 36px; height: 36px; border-radius: 10px; }
.icon-tile.sm .ico { width: 19px; height: 19px; }
.icon-tile.lg { width: 64px; height: 64px; border-radius: 18px; }
.icon-tile.lg .ico { width: 32px; height: 32px; }
.icon-tile.cyan   { color: #22d3ee; border-color: rgba(34,211,238,0.36); background: radial-gradient(circle at 30% 20%, rgba(34,211,238,0.22), rgba(6,18,40,0.9)); box-shadow: 0 0 18px rgba(34,211,238,0.14); }
.icon-tile.violet { color: #a78bfa; border-color: rgba(167,139,250,0.4);  background: radial-gradient(circle at 30% 20%, rgba(124,58,237,0.28), rgba(14,10,40,0.9)); box-shadow: 0 0 18px rgba(139,92,246,0.16); }
.icon-tile.green  { color: #34d399; border-color: rgba(52,211,153,0.38);  background: radial-gradient(circle at 30% 20%, rgba(16,185,129,0.24), rgba(6,22,28,0.9)); box-shadow: 0 0 18px rgba(16,185,129,0.14); }

/* ═══════════════════════════════════════════════
   GLASS CARD  (generic)
═══════════════════════════════════════════════ */
.glass-card {
  background: linear-gradient(180deg, rgba(12,24,52,0.88), rgba(6,14,34,0.92));
  backdrop-filter: blur(14px);
  border: 1px solid rgba(80,150,255,0.2);
  border-radius: 16px;
  padding: 1.25rem 1.35rem;
  margin-bottom: 1rem;
  box-shadow: 0 10px 28px rgba(0,0,0,0.22);
}

/* ═══════════════════════════════════════════════
   DIAGNOSE PAGE
═══════════════════════════════════════════════ */
.diag-page { padding: 1.5rem 2.5rem; }
.diag-page h2 {
  font-family: var(--font-display);
  font-size: 1.6rem; font-weight: 800;
  color: #fff; margin: 0 0 0.25rem;
}
.diag-page p.sub { color: var(--muted); font-size: 0.9rem; margin: 0 0 1.5rem; }

/* Streamlit form elements in diagnose */
.stApp label, .stApp input, .stApp textarea, .stApp button, .stApp [data-baseweb="select"] { font-family: var(--font-body) !important; }
.stApp button[kind="primary"] p { font-family: var(--font-display) !important; letter-spacing: 0; }
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSlider"] label {
  color: #9ab8d8 !important;
  font-size: 0.82rem !important;
  font-weight: 500 !important;
}
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
  background: rgba(6,18,42,0.9) !important;
  border: 1px solid rgba(30,80,180,0.35) !important;
  border-radius: 8px !important;
  color: #e2eaf7 !important;
}
div[data-testid="stTextArea"] textarea {
  background: rgba(6,18,42,0.9) !important;
  border: 1px solid rgba(30,80,180,0.35) !important;
  border-radius: 8px !important;
  color: #e2eaf7 !important;
}
div[data-testid="stSelectbox"] > div[data-baseweb="select"] > div {
  background: rgba(6,18,42,0.9) !important;
  border: 1px solid rgba(30,80,180,0.35) !important;
  border-radius: 8px !important;
  color: #e2eaf7 !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
  background: linear-gradient(135deg,#1a6fff 0%,#7c3aed 100%) !important;
  border: none !important; font-weight: 700 !important;
  border-radius: 8px !important; padding: 0.65rem 1.2rem !important;
  box-shadow: 0 4px 20px rgba(26,100,255,0.35);
  transition: transform 0.15s, box-shadow 0.15s;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(26,100,255,0.5) !important;
}
div[data-testid="stButton"] > button:not([kind="primary"]) {
  background: rgba(26,80,180,0.12) !important;
  border: 1px solid rgba(30,80,180,0.35) !important;
  color: #c5d5ed !important; border-radius: 8px !important;
}

/* ═══════════════════════════════════════════════
   METRIC STRIP (results)
═══════════════════════════════════════════════ */
.metric-strip {
  display: grid; grid-template-columns: repeat(4,1fr);
  gap: 0.75rem; margin-bottom: 1rem;
}
.metric-box {
  background: var(--card-bg); border: 1px solid var(--card-border);
  border-radius: 12px; padding: 0.85rem 1rem;
}
.metric-label {
  font-size: 0.7rem; text-transform: uppercase;
  letter-spacing: 0.08em; color: var(--muted); margin-bottom: 0.25rem;
}
.metric-value {
  font-family: var(--font-display);
  font-weight: 700; font-size: 1.35rem; color: #f8fafc;
}
.metric-value.accent { color: var(--cyan); }

/* ═══════════════════════════════════════════════
   REC CARDS  (results)
═══════════════════════════════════════════════ */
.rec-card {
  position: relative;
  background: linear-gradient(145deg,rgba(6,18,42,0.95),rgba(3,10,26,0.98));
  border: 1px solid var(--card-border);
  border-radius: 20px; padding: 1.35rem 1.5rem;
  margin-bottom: 1rem; overflow: hidden;
}
.rec-card.top {
  border-color: rgba(26,143,255,0.45);
  box-shadow: 0 0 40px rgba(26,143,255,0.1);
}
.rec-card.top::before {
  content: ""; position: absolute; top:0;left:0;right:0; height:3px;
  background: linear-gradient(90deg,#1a6fff,#a855f7,#22d3ee);
}
.rec-rank {
  display: inline-flex; align-items:center; justify-content:center;
  width:2rem; height:2rem; border-radius:10px;
  font-family:var(--font-display); font-weight:800; font-size:0.95rem;
  margin-bottom:0.65rem;
  background:rgba(26,143,255,0.2); color:#93c5fd;
}
.rec-card.top .rec-rank {
  background:linear-gradient(135deg,#1a6fff,#7c3aed); color:#fff;
}
.rec-name { font-family:var(--font-display);font-weight:700;font-size:1.35rem;color:#f8fafc;margin:0 0 0.35rem; }
.rec-price { font-size:1.1rem;color:var(--cyan);font-weight:600;margin-bottom:0.75rem;font-variant-numeric:tabular-nums; }
.rec-specs, .rec-source, .catalog-note { font-size:0.72rem;color:var(--muted);line-height:1.45;margin:0 0 0.7rem; }
.rec-source a, .catalog-note a { color:#7dd3fc !important;text-decoration:underline !important;overflow-wrap:anywhere; }
.guidance-list { color:#c5d5ed;font-size:0.84rem;line-height:1.7;margin:0 0 0.8rem;padding-left:1.2rem; }
.guidance-list li + li { margin-top:0.3rem; }
.catalog-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
.catalog-card { align-items: stretch; min-width: 0; }
.catalog-visual { width:70px;flex:0 0 70px;display:flex;align-items:center;justify-content:center;background:rgba(40,80,170,0.12);border-radius:12px; }
.catalog-visual .phone-bezel { width:40px;height:76px; }
.catalog-card .phone-info { min-width:0; }
.catalog-card .phone-name, .catalog-card .phone-price { overflow-wrap:anywhere; }
.rec-score-num { font-family:var(--font-display);font-size:2rem;font-weight:800;color:#93c5fd;font-variant-numeric:tabular-nums; }
.rec-score-label { font-size:0.85rem;color:var(--muted); }
.dim-row { margin:0.45rem 0; }
.dim-label { display:flex;justify-content:space-between;font-size:0.75rem;color:var(--muted);margin-bottom:0.2rem; }
.dim-bar-bg { height:6px;border-radius:999px;background:rgba(26,80,180,0.2);overflow:hidden; }
.dim-bar-fill { height:100%;border-radius:999px;background:linear-gradient(90deg,#1a6fff,#22d3ee); }

/* ═══════════════════════════════════════════════
   TIMELINE
═══════════════════════════════════════════════ */
.timeline { position:relative;padding-left:1.5rem; }
.timeline::before {
  content:"";position:absolute;left:0.45rem;top:0.5rem;bottom:0.5rem;
  width:2px;background:linear-gradient(180deg,#1a6fff,#a855f7,transparent);
}
.tl-item { position:relative;padding:0.65rem 0 0.65rem 1.25rem;margin-bottom:0.25rem; }
.tl-dot {
  position:absolute;left:-1.05rem;top:0.85rem;
  width:10px;height:10px;border-radius:50%;
  background:#1a6fff;box-shadow:0 0 12px rgba(26,143,255,0.6);
}
.tl-agent { font-family:var(--font-display);font-weight:600;font-size:0.92rem;color:#e2e8f0; }
.tl-action { font-size:0.82rem;color:var(--muted);margin-top:0.15rem; }

/* ═══════════════════════════════════════════════
   VERIFY BADGES
═══════════════════════════════════════════════ */
.verify-ok .ico { width: 18px; height: 18px; }
.verify-ok {
  display:inline-flex;align-items:center;gap:0.5rem;
  padding:0.5rem 0.85rem;border-radius:10px;
  background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);
  color:#86efac;font-size:0.88rem;font-weight:600;
}
.verify-warn {
  background:rgba(251,191,36,0.1);border-color:rgba(251,191,36,0.3);color:#fde047;
}

/* ═══════════════════════════════════════════════
   MISC REUSABLES
═══════════════════════════════════════════════ */
.section-head {
  font-family:var(--font-display);font-weight:700;font-size:1.2rem;
  letter-spacing:-0.02em;margin:1.25rem 0 0.75rem;color:#f1f5f9;
}
.old-device-chip { display:inline-flex;flex-wrap:wrap;gap:0.5rem;margin-top:0.5rem; }
.chip {
  padding:0.35rem 0.65rem;border-radius:8px;font-size:0.8rem;
  background:rgba(26,80,180,0.15);border:1px solid var(--card-border);color:#c5d5ed;
}
div[data-testid="stExpander"] {
  background:var(--card-bg) !important;
  border:1px solid var(--card-border) !important;
  border-radius:12px !important;
}
div[data-testid="stStatusWidget"] {
  background:var(--card-bg) !important;
  border:1px solid var(--card-border) !important;
  border-radius:12px !important;
  color: var(--text) !important;
}
@media(max-width:1200px) {
  .nav-link { padding: 0.38rem 0.55rem; font-size: 0.78rem; }
  .nav-search { max-width: 200px; flex-basis: 160px; }
}
@media(max-width:900px) {
  .hero-section { min-height: 320px; }
  .hero-left { padding: 2rem 1.5rem; }
  .problem-grid { grid-template-columns:repeat(2,1fr); }
  .phones-grid  { grid-template-columns:repeat(2,1fr); }
  .cta-strip    { grid-template-columns:1fr 1fr; }
  .cta-wrap     { padding: 0 1.25rem 0.4rem; }
  .revivai-nav { flex-wrap: wrap; }
  .nav-links { order: 5; width: 100%; justify-content: flex-start; margin-left: 0; }
}

/* Responsive layouts for inner pages and narrow viewports. */
@media (max-width: 900px) {
  .section-wrap { padding: 1.4rem 1.5rem 0; }
  .phones-grid, .problem-grid { padding-left: 1.5rem; padding-right: 1.5rem; }
  .metric-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .revivai-nav { gap: 0.65rem; padding: 0.65rem 1.25rem; }
  .nav-search { flex: 1 1 180px; min-width: 0; }
  .nav-links { flex-wrap: wrap; row-gap: 0.2rem; }
  .nav-link { padding: 0.4rem 0.55rem; }
  /* Streamlit columns are a single row by default; stack the diagnosis form
     and results when there is not enough room for both. */
  div[data-testid="stHorizontalBlock"] {
    flex-wrap: wrap !important;
    gap: 1rem !important;
  }
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    flex: 1 1 100% !important;
    width: 100% !important;
    min-width: 0 !important;
  }
  div[data-testid="stMarkdownContainer"] > div[style*="padding:2rem 2.5rem"] {
    padding: 1.5rem !important;
    width: auto !important;
  }
  div[data-testid="stMarkdownContainer"] > div[style*="padding:1.25rem 2.5rem"] {
    padding: 1rem 1.5rem 0.5rem !important;
  }
  div[data-testid="stMarkdownContainer"] > div[style*="padding:0 0 0 2.5rem"] {
    padding-left: 0 !important;
  }
  .phones-grid[style*="grid-template-columns"] { grid-template-columns: repeat(2, minmax(0, 1fr)) !important; }
  div[data-testid="stMarkdownContainer"] [style*="grid-template-columns:1fr 1fr"] {
    grid-template-columns: minmax(0, 1fr) !important;
  }
}

@media (max-width: 600px) {
  .diagnose-preview-grid { grid-template-columns: minmax(0, 1fr) !important; }
  .ann-bar { padding: 0.45rem 0.85rem; justify-content: center; font-size: 0.68rem; }
  .ann-bar .ann-side:last-child { display: none; }
  .revivai-nav { padding: 0.65rem 0.85rem; gap: 0.4rem; }
  .nav-logo { font-size: 1rem; }
  .nav-logo .tagline { font-size: 0.52rem; }
  .nav-search, .nav-icons { display: none; }
  .nav-links { order: 0; width: 100%; justify-content: flex-start; margin: 0; gap: 0.1rem; }
  .nav-link { font-size: 0.72rem; padding: 0.45rem 0.42rem; }
  .hero-section { min-height: 0; background-position: 62% center !important; }
  .hero-overlay { background: rgba(4,11,24,0.78); }
  .hero-left { padding: 2.25rem 1rem; }
  .hero-h1 { font-size: clamp(1.9rem, 9vw, 2.55rem); }
  .hero-sub { font-size: 0.9rem; }
  .hero-sub br { display: none; }
  .hero-btns { align-items: stretch; flex-direction: column; }
  .hero-btns .btn-primary, .hero-btns .btn-secondary { justify-content: center; }
  .hero-trust { gap: 0.55rem; font-size: 0.7rem; }
  .trust-sep { display: none; }
  .section-wrap { padding: 1.2rem 1rem 0; }
  .section-label { font-size: 1.12rem; }
  .problem-grid, .phones-grid { grid-template-columns: minmax(0, 1fr) !important; gap: 0.7rem; padding: 0.75rem 1rem 1.25rem; }
  .phone-card { min-height: 0; }
  .cta-wrap { padding: 0 1rem 0.4rem; }
  .cta-strip { grid-template-columns: minmax(0, 1fr); gap: 1rem; padding: 1.2rem; border-radius: 16px; }
  .cta-headline { font-size: 1.35rem; }
  .trust-bar { padding: 0.8rem 1rem; justify-content: flex-start; gap: 0.2rem; }
  .trust-bar-item { font-size: 0.72rem; }
  .tb-sep { display: none; }
  .metric-strip { gap: 0.5rem; }
  .metric-box { padding: 0.7rem; min-width: 0; }
  .metric-value { font-size: 1.05rem; overflow-wrap: anywhere; }
  .glass-card, .rec-card { padding: 1rem; border-radius: 14px; }
  .rec-name { font-size: 1.15rem; overflow-wrap: anywhere; }
  .old-device-chip { display: flex; }
  .chip { overflow-wrap: anywhere; }
  .tl-action { overflow-wrap: anywhere; }
  div[data-testid="stMarkdownContainer"] > div[style*="padding:2rem 2.5rem"] {
    padding: 1.15rem 1rem !important;
  }
  div[data-testid="stMarkdownContainer"] > div[style*="padding:1.25rem 2.5rem"] {
    padding: 0.9rem 1rem 0.4rem !important;
  }
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { flex-basis: 100% !important; }
  .verify-ok { font-size: 0.78rem; padding: 0.45rem 0.6rem; }
}

/* ═══════════════════════════════════════════════
   PAGE FADE-IN ANIMATION
═══════════════════════════════════════════════ */
.stApp > div:first-child {
  animation: pageFadeIn 0.35s ease forwards;
}
@keyframes pageFadeIn {
  from { opacity:0; transform:translateY(6px); }
  to   { opacity:1; transform:translateY(0); }
}

/* ═══════════════════════════════════════════════
   STREAMLIT COLUMN / CONTAINER FIXES
   (remove internal padding on diagnose page)
═══════════════════════════════════════════════ */
div[data-testid="stHorizontalBlock"] {
  gap: 1.5rem !important;
  align-items: flex-start !important;
}
div[data-testid="column"] > div:first-child {
  padding: 0 !important;
}
/* Streamlit adds unwanted top padding to the first element in columns */
div[data-testid="column"] .stTextInput:first-child,
div[data-testid="column"] .stMarkdown:first-child {
  margin-top: 0 !important;
}
/* Remove Streamlit's default vertical padding on the block container */
div[data-testid="stVerticalBlock"] {
  gap: 0.5rem !important;
}

/* ═══════════════════════════════════════════════
   SCROLLBAR STYLING
═══════════════════════════════════════════════ */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background: rgba(4,11,24,0.6); }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg,#1a6fff,#7c3aed);
  border-radius:999px;
}

/* ═══════════════════════════════════════════════
   LOADING SPINNER COLOR FIX
═══════════════════════════════════════════════ */
div[data-testid="stSpinner"] svg circle {
  stroke: #1a8fff !important;
}

/* ═══════════════════════════════════════════════
   STATUS / PROGRESS WIDGET
═══════════════════════════════════════════════ */
div[data-testid="stStatusWidget"] {
  background: var(--card-bg) !important;
  border: 1px solid var(--card-border) !important;
  border-radius: 12px !important;
}
div[data-testid="stStatusWidget"] p,
div[data-testid="stStatusWidget"] span {
  color: var(--text) !important;
}

/* ═══════════════════════════════════════════════
   SELECTBOX DROPDOWN MENU
═══════════════════════════════════════════════ */
[data-baseweb="popover"] ul {
  background: #060e1f !important;
  border: 1px solid var(--card-border) !important;
}
[data-baseweb="popover"] li {
  color: #c5d5ed !important;
}
[data-baseweb="popover"] li:hover {
  background: rgba(26,100,255,0.15) !important;
}

/* hero-overlay is now a real div (see .hero-overlay in main section) */


/* ═══════════════════════════════════════════════
   NAV ACTIVE LINK ANIMATION  (slide-in underline)
═══════════════════════════════════════════════ */
.nav-link {
  position: relative;
}
.nav-link::after {
  content:"";
  position:absolute;bottom:-2px;left:50%;right:50%;
  height:2px;background:var(--blue);
  border-radius:2px;
  transition: left 0.2s ease, right 0.2s ease;
}
.nav-link:hover::after {
  left:8px; right:8px;
}
.nav-link.active::after {
  left:0; right:0;
  box-shadow: 0 0 10px var(--blue), 0 0 2px var(--blue);
}

/* Keep inner pages on the same centered content grid as the landing page. */
.inner-page-shell {
  width: min(100% - 3rem, 1280px);
  margin: 0 auto;
  padding: clamp(1.25rem, 3.5vw, 2.5rem) 0;
  box-sizing: border-box;
}
.inner-page-intro {
  width: min(100% - 3rem, 1280px);
  margin: 0 auto;
  padding: 1.5rem 0 0.75rem;
  box-sizing: border-box;
}
.inner-page-intro h2, .inner-page-shell h2 {
  font-family: var(--font-display);
  font-size: clamp(1.55rem, 3vw, 1.9rem) !important;
  font-weight: 800 !important;
  letter-spacing: -0.03em;
}
.form-section-label {
  color: #93b8d8;
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.07em;
  margin: 0.9rem 0 0.75rem;
  text-transform: uppercase;
}
.agent-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.2rem 1rem;
}
div[data-testid="stHorizontalBlock"] {
  width: min(100% - 3rem, 1280px);
  margin: 0 auto;
  gap: 1.25rem !important;
  box-sizing: border-box;
}
@media (max-width: 900px) {
  .inner-page-shell, .inner-page-intro,
  div[data-testid="stHorizontalBlock"] { width: min(100% - 2rem, 1280px); }
  .catalog-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 600px) {
  .inner-page-shell, .inner-page-intro,
  div[data-testid="stHorizontalBlock"] { width: calc(100% - 2rem); }
  .agent-grid { grid-template-columns: minmax(0, 1fr); gap: 0; }
  .catalog-grid { grid-template-columns: minmax(0, 1fr); }
}

</style>
""")

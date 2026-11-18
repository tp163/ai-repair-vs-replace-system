"""Generate clean, unified PowerPoint presentation for REVIVAI Progress Review.
Unified view (no Person A/B division), clean layout, 12-14 slides, high-level bullets.
"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# Color Palette (Dark Theme matching REVIVAI)
C_BG = RGBColor(6, 14, 34)          # Deep Navy
C_CARD = RGBColor(12, 24, 52)       # Card Background
C_CARD_BORDER = RGBColor(40, 75, 140)
C_BLUE = RGBColor(59, 158, 255)     # Primary Blue
C_CYAN = RGBColor(34, 211, 238)     # Accent Cyan
C_PURPLE = RGBColor(147, 112, 219)  # Accent Violet
C_WHITE = RGBColor(255, 255, 255)   # Title / High Contrast Text
C_MUTED = RGBColor(154, 182, 216)   # Body Text
C_GREEN = RGBColor(34, 197, 94)     # Success Accent
C_RED = RGBColor(239, 68, 68)       # Safety Stop Red
C_GOLD = RGBColor(245, 158, 11)     # Highlight

FONT_TITLE = "Segoe UI"
FONT_BODY = "Segoe UI"


def set_bg(slide):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = C_BG


def add_card(slide, left, top, width, height, bg_color=C_CARD, border_color=C_CARD_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.2)
    else:
        shape.line.fill.background()
    return shape


def add_header(slide, title_text, category="REVIVAI · PROJECT PROGRESS"):
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_cat = tf.paragraphs[0]
    p_cat.text = category.upper()
    p_cat.font.name = FONT_TITLE
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = C_CYAN
    p_cat.space_after = Pt(2)

    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.name = FONT_TITLE
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = C_WHITE


def set_notes(slide, text):
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = text


def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    base_dir = Path(__file__).resolve().parent
    hero_img = base_dir / "static" / "hero_phones.jpg"
    app_screenshot = base_dir / "Screenshot 2026-10-31 130829.png"

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)

    tb = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(7.2), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "MULTI-AGENT AI DECISION SYSTEM"
    p0.font.name = FONT_TITLE
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = C_CYAN
    p0.space_after = Pt(12)

    p1 = tf.add_paragraph()
    p1.text = "REVIVAI"
    p1.font.name = FONT_TITLE
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE

    p2 = tf.add_paragraph()
    p2.text = "Intelligent Smartphone Diagnosis, Repair Evaluation &\nReplacement Decision System"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(18)
    p2.font.color.rgb = C_BLUE
    p2.space_before = Pt(6)
    p2.space_after = Pt(20)

    p3 = tf.add_paragraph()
    p3.text = "Project Progress & Architecture Review"
    p3.font.name = FONT_BODY
    p3.font.size = Pt(13)
    p3.font.color.rgb = C_MUTED

    if hero_img.exists():
        add_card(s1, Inches(8.5), Inches(1.4), Inches(4.0), Inches(4.9), border_color=C_BLUE)
        s1.shapes.add_picture(str(hero_img), Inches(8.6), Inches(1.5), Inches(3.8), Inches(4.7))

    set_notes(s1, "Welcome. Today we present REVIVAI, an intelligent multi-agent framework that empowers smartphone owners to make objective, data-backed decisions on whether to repair or replace their malfunctioning devices.")

    # =========================================================================
    # SLIDE 2: The Core Problem
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_header(s2, "The Consumer Dilemma: Repair or Replace?", "Context & Problem")

    cards_s2 = [
        ("Diagnostic Uncertainty", C_BLUE, [
            "Users often cannot tell if a fault is a quick fix or a severe hardware failure.",
            "Fear of misdiagnosis or being overcharged by technicians creates hesitation."
        ]),
        ("Unverifiable Repair Costs", C_GOLD, [
            "Local repair pricing is highly fragmented with wide price variance.",
            "Consumers lack reliable, source-backed benchmarks before visiting a repairer."
        ]),
        ("Premature Device Upgrades", C_RED, [
            "Over 50 million metric tons of e-waste are generated globally each year.",
            "Fixable phones are discarded simply because buying a new one seems easier."
        ])
    ]

    for i, (title, color, bullets) in enumerate(cards_s2):
        x = Inches(0.8 + i * 3.95)
        add_card(s2, x, Inches(1.8), Inches(3.75), Inches(4.9))
        tb = s2.shapes.add_textbox(x + Inches(0.25), Inches(2.1), Inches(3.25), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_after = Pt(14)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = "• " + b
            pb.font.name = FONT_BODY
            pb.font.size = Pt(12)
            pb.font.color.rgb = C_WHITE
            pb.space_after = Pt(10)

    set_notes(s2, "When a smartphone breaks, consumers face three obstacles: diagnosing the actual cause, finding trustworthy repair pricing, and resisting the urge to buy a new phone prematurely, worsening global e-waste.")

    # =========================================================================
    # SLIDE 3: The REVIVAI Solution
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_header(s3, "The REVIVAI Solution: An Objective AI Advisor", "Project Vision")

    pillars = [
        ("Safe Triage", "Identifies probable faults and applies strict safety stops for thermal, liquid, and battery hazards.", C_BLUE),
        ("Economic Evaluation", "Compares sourced local repair costs directly against the second-hand residual value of the device.", C_CYAN),
        ("Verified Replacements", "Recommends fact-checked upgrades tailored to user budget and priorities with no price hallucination.", C_GREEN),
        ("Observable Reasoning", "Every agent decision is recorded in an audit trail so recommendations are fully explainable.", C_GOLD)
    ]

    for i, (title, desc, color) in enumerate(pillars):
        x = Inches(0.8 + (i % 2) * 5.95)
        y = Inches(1.8 + (i // 2) * 2.5)
        add_card(s3, x, y, Inches(5.75), Inches(2.25), border_color=color)
        tb = s3.shapes.add_textbox(x + Inches(0.3), y + Inches(0.25), Inches(5.15), Inches(1.8))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_after = Pt(8)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(12)
        p2.font.color.rgb = C_WHITE
        p2.space_after = Pt(4)

    set_notes(s3, "REVIVAI solves this through four pillars: safety-first triage, economic repair evaluation, verified replacement recommendations, and transparent agent observability.")

    # =========================================================================
    # SLIDE 4: End-to-End System Workflow
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_header(s4, "End-to-End User Journey", "System Flow")

    steps = [
        ("1. Device Confirmation", "User enters phone model and locks in exact hardware variant."),
        ("2. Symptom & Photo Triage", "User enters symptoms and optional photo for fault screening."),
        ("3. Safety-Gated Guidance", "Safe home steps provided; dangerous faults trigger immediate technician stops."),
        ("4. Repair vs. Replace Math", "Repair costs benchmarked against depreciated device value."),
        ("5. Verified Recommendations", "Scored replacement picks presented with transparent score breakdowns.")
    ]

    for i, (title, desc) in enumerate(steps):
        y = Inches(1.8 + i * 1.0)
        add_card(s4, Inches(0.8), y, Inches(11.73), Inches(0.86))
        tb = s4.shapes.add_textbox(Inches(1.1), y + Inches(0.12), Inches(11.2), Inches(0.62))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title + "  ➔  "
        p.font.name = FONT_TITLE
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = C_CYAN

        run = p.add_run()
        run.text = desc
        run.font.name = FONT_BODY
        run.font.size = Pt(11)
        run.font.bold = False
        run.font.color.rgb = C_WHITE

    set_notes(s4, "Here is the user journey: from verifying their exact hardware model, to receiving safety-screened advice, economic repair evaluation, and verified replacement recommendations.")

    # =========================================================================
    # SLIDE 5: Multi-Agent Architecture (LangGraph)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_header(s5, "Multi-Agent Architecture (LangGraph)", "Technical Foundation")

    add_card(s5, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0))
    tb_l = s5.shapes.add_textbox(Inches(1.05), Inches(2.0), Inches(5.2), Inches(4.5))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "Why a Multi-Agent Architecture?"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(12)

    for item in [
        "Separation of Concerns: Diagnosis, safety rules, financial scoring, and market pricing are handled by focused agents.",
        "Deterministic Safety: Rules and math cannot be bypassed by an LLM prompt.",
        "Observable Collaboration: All agents read and write to a single shared AgentState schema.",
        "LangGraph Engine: Strict information-dependency pipeline ensures no step runs out of order."
    ]:
        pl = tf_l.add_paragraph()
        pl.text = "• " + item
        pl.font.size = Pt(11)
        pl.font.color.rgb = C_WHITE
        pl.space_after = Pt(10)

    add_card(s5, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0))
    tb_r = s5.shapes.add_textbox(Inches(7.05), Inches(2.0), Inches(5.2), Inches(4.5))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    pr_h = tf_r.paragraphs[0]
    pr_h.text = "Specialized Agent Nodes in Pipeline"
    pr_h.font.bold = True
    pr_h.font.size = Pt(16)
    pr_h.font.color.rgb = C_CYAN
    pr_h.space_after = Pt(12)

    agents = [
        "FaultDiagnosisAgent: Categorizes issues & uncertainty",
        "TroubleshootingAgent: Safe steps & hard stops",
        "DeviceProfilingAgent: Age & residual value math",
        "RepairCostAgent: Sourced repair price retrieval",
        "RepairDecisionAgent: Economic threshold calculation",
        "SpecRetrievalAgent: Hard-constraint catalogue search",
        "ComparisonAgent: 7-dimension weighted scoring",
        "VerificationAgent: Price sanity checks (±40% rule)"
    ]
    for a in agents:
        pa = tf_r.add_paragraph()
        pa.text = "✔ " + a
        pa.font.size = Pt(11)
        pa.font.color.rgb = C_WHITE
        pa.space_after = Pt(5)

    set_notes(s5, "LangGraph orchestrates the agents sequentially. Decoupling agents ensures safety rules and mathematical scoring remain deterministic, while the LLM focuses on language extraction and explanation.")

    # =========================================================================
    # SLIDE 6: Device Confirmation & Variant Gating
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_header(s6, "Device Confirmation: Ensuring Accurate Specs", "Core Capability 1")

    items_s6 = [
        ("Tolerant Fuzzy Matching", "Handles user typos, brand prefixes, and spacing differences (e.g. typing 'Galaxy A51' or 'Samsung A51').", C_BLUE),
        ("Exact Variant Selection", "Prompts user to select their specific storage, RAM, and chipset configuration from catalogue records.", C_CYAN),
        ("Analysis Execution Gating", "Analysis remains disabled until the user confirms the variant, preventing downstream calculation errors.", C_GREEN)
    ]

    for i, (title, desc, color) in enumerate(items_s6):
        x = Inches(0.8 + i * 3.95)
        add_card(s6, x, Inches(1.8), Inches(3.75), Inches(4.9))
        tb = s6.shapes.add_textbox(x + Inches(0.25), Inches(2.1), Inches(3.25), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_after = Pt(14)

        pb = tf.add_paragraph()
        pb.text = desc
        pb.font.name = FONT_BODY
        pb.font.size = Pt(12)
        pb.font.color.rgb = C_WHITE
        pb.space_after = Pt(10)

    set_notes(s6, "Accurate device identification is crucial. We implemented tolerant device matching and variant gating to ensure the exact hardware profile is confirmed before any scoring occurs.")

    # =========================================================================
    # SLIDE 7: Safety-First Troubleshooting & Guardrails
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_header(s7, "Safety Guardrails: Protecting the Consumer", "Core Capability 2")

    add_card(s7, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0))
    tb_l7 = s7.shapes.add_textbox(Inches(1.05), Inches(2.0), Inches(5.2), Inches(4.5))
    tf_l7 = tb_l7.text_frame
    tf_l7.word_wrap = True

    p = tf_l7.paragraphs[0]
    p.text = "Safe, Non-Invasive First Steps"
    p.font.bold = True
    p.font.size = Pt(16)
    p.font.color.rgb = C_BLUE
    p.space_after = Pt(12)

    for item in [
        "Safe home checks: cable testing, port cleaning with non-conductive tools, power cycling.",
        "Clear risk classification: Steps tagged as Safe, Caution, or Technician Only.",
        "Verified Guides: Links to official OEM support pages and iFixit manuals."
    ]:
        pl = tf_l7.add_paragraph()
        pl.text = "• " + item
        pl.font.size = Pt(11)
        pl.font.color.rgb = C_WHITE
        pl.space_after = Pt(10)

    add_card(s7, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), border_color=C_RED)
    tb_r7 = s7.shapes.add_textbox(Inches(7.05), Inches(2.0), Inches(5.2), Inches(4.5))
    tf_r7 = tb_r7.text_frame
    tf_r7.word_wrap = True

    pr_h = tf_r7.paragraphs[0]
    pr_h.text = "Immutable Safety Stops"
    pr_h.font.bold = True
    pr_h.font.size = Pt(16)
    pr_h.font.color.rgb = C_RED
    pr_h.space_after = Pt(12)

    for item in [
        "Immediate detection of swollen battery, smoke, liquid ingress, or extreme heat.",
        "Normal troubleshooting is immediately halted.",
        "Prominent red 'Safety Stop: Technician inspection required' banner displayed.",
        "Guaranteed safety: Hard-coded rules override generative LLM responses."
    ]:
        pa = tf_r7.add_paragraph()
        pa.text = "⚠ " + item
        pa.font.size = Pt(11)
        pa.font.color.rgb = C_WHITE
        pa.space_after = Pt(10)

    set_notes(s7, "Consumer safety is paramount. When hazards like battery swelling or liquid ingress are detected, our system halts DIY triage immediately and presents a high-priority safety warning.")

    # =========================================================================
    # SLIDE 8: Repair vs. Replace Economic Intelligence
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8)
    add_header(s8, "Repair vs. Replace: Objective Economic Evaluation", "Decision Logic")

    boxes_s8 = [
        ("Device Residual Value", "Calculates realistic second-hand value based on original price, age, brand retention, and physical condition.", C_CYAN),
        ("Sourced Repair Costs", "Indexes verified local repair costs with citations and dates; flags when an in-person quote is necessary.", C_BLUE),
        ("The 40% - 60% Decision Rule", "Repair Cost < 40% value: Repair recommended.\nRepair Cost > 60% value: Replacement suggested.\nIn-between: Side-by-side quote comparison.", C_GREEN)
    ]

    for i, (title, desc, color) in enumerate(boxes_s8):
        x = Inches(0.8 + i * 3.95)
        add_card(s8, x, Inches(1.8), Inches(3.75), Inches(4.9))
        tb = s8.shapes.add_textbox(x + Inches(0.25), Inches(2.1), Inches(3.25), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_after = Pt(14)

        for line in desc.split("\n"):
            pb = tf.add_paragraph()
            pb.text = "• " + line
            pb.font.name = FONT_BODY
            pb.font.size = Pt(12)
            pb.font.color.rgb = C_WHITE
            pb.space_after = Pt(8)

    set_notes(s8, "Our economic engine balances repair cost against the phone's remaining market value. Under 40%, repair makes financial sense. Over 60%, replacement is suggested. This prevents emotional or marketing-driven purchases.")

    # =========================================================================
    # SLIDE 9: Verified Replacement Recommendations
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9)
    add_header(s9, "Verified Replacement Recommendations", "Replacement Engine")

    recs = [
        ("Multi-Criteria Scoring", "Evaluates candidate phones across 7 weighted dimensions: price fit (25%), performance (20%), camera (15%), battery (10%), longevity (10%), upgrade delta (10%), and similarity (10%).", C_BLUE),
        ("Categorized Recommendations", "Instead of a single list, users receive choices grouped by: Best Within Budget, Closest to Current Phone, and Performance Upgrades.", C_CYAN),
        ("Hallucination Verification", "Verification Agent sanity-checks quoted prices against local datasets and rejects live search price outliers (±40% rule).", C_GREEN)
    ]

    for i, (title, desc, color) in enumerate(recs):
        y = Inches(1.8 + i * 1.65)
        add_card(s9, Inches(0.8), y, Inches(11.73), Inches(1.45))
        tb = s9.shapes.add_textbox(Inches(1.1), y + Inches(0.18), Inches(11.2), Inches(1.1))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_after = Pt(4)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(11)
        p2.font.color.rgb = C_WHITE

    set_notes(s9, "When replacement is indicated, candidates are scored across 7 transparent dimensions and categorized into Budget, Similar, and Upgrade options, backed by strict price verification.")

    # =========================================================================
    # SLIDE 10: Current Progress & Test Validation
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_bg(s10)
    add_header(s10, "Current Implementation Status & Verification", "Milestones")

    stats = [
        ("53", "PASSING UNIT TESTS", "Clean test run across diagnosis, triage, and resource engines.", C_GREEN),
        ("7", "FIXED FAULT CLASSES", "Handles screens, batteries, charging, heat, liquids, and performance.", C_BLUE),
        ("18", "CURATED REPAIR URLS", "Audited manufacturer & iFixit guides with zero dead links.", C_CYAN),
        ("100%", "SAFETY TESTED", "Proven automated protection for dangerous thermal/chemical hazards.", C_RED)
    ]

    for i, (num, lbl, desc, col) in enumerate(stats):
        x = Inches(0.8 + i * 2.97)
        add_card(s10, x, Inches(1.8), Inches(2.78), Inches(5.0))
        tb = s10.shapes.add_textbox(x + Inches(0.15), Inches(2.0), Inches(2.48), Inches(4.6))
        tf = tb.text_frame
        tf.word_wrap = True

        p_num = tf.paragraphs[0]
        p_num.text = num
        p_num.font.name = FONT_TITLE
        p_num.font.size = Pt(40)
        p_num.font.bold = True
        p_num.font.color.rgb = col
        p_num.space_after = Pt(6)

        p_lbl = tf.add_paragraph()
        p_lbl.text = lbl
        p_lbl.font.name = FONT_TITLE
        p_lbl.font.size = Pt(11)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = C_WHITE
        p_lbl.space_after = Pt(14)

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.name = FONT_BODY
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = C_MUTED

    set_notes(s10, "Our current progress is validated with 53 passing automated unit tests. All core triage, safety, and routing components are thoroughly verified.")

    # =========================================================================
    # SLIDE 11: Live UI Showcase (Streamlit Demo)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_bg(s11)
    add_header(s11, "Live System Demonstration", "Streamlit UI")

    add_card(s11, Inches(0.8), Inches(1.8), Inches(4.8), Inches(5.1))
    tb_ui = s11.shapes.add_textbox(Inches(1.05), Inches(2.0), Inches(4.3), Inches(4.7))
    tfu = tb_ui.text_frame
    tfu.word_wrap = True

    pu_h = tfu.paragraphs[0]
    pu_h.text = "Interactive Advisor UI"
    pu_h.font.bold = True
    pu_h.font.size = Pt(15)
    pu_h.font.color.rgb = C_CYAN
    pu_h.space_after = Pt(12)

    ui_highlights = [
        "Dark Glassmorphism Design: Modern, intuitive consumer interface.",
        "Variant Selector: Real-time hardware spec validation.",
        "Diagnostic Cards: Clearly surfaced confidence and uncertainty notes.",
        "Safety Banners: Prominent warnings when technician intervention is required.",
        "Agent Trace: Expandable audit log displaying full reasoning path."
    ]
    for h in ui_highlights:
        p = tfu.add_paragraph()
        p.text = "✔ " + h
        p.font.size = Pt(11)
        p.font.color.rgb = C_WHITE
        p.space_after = Pt(8)

    add_card(s11, Inches(5.9), Inches(1.8), Inches(6.6), Inches(5.1), border_color=C_BLUE)
    if app_screenshot.exists():
        s11.shapes.add_picture(str(app_screenshot), Inches(6.0), Inches(1.9), Inches(6.4), Inches(4.9))

    set_notes(s11, "This screenshot shows the working web app. The interface combines responsive device inputs on the left with diagnostic outcomes, safety banners, and recommendation cards on the right.")

    # =========================================================================
    # SLIDE 12: Upcoming Roadmap & Next Steps
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_bg(s12)
    add_header(s12, "Next Development Milestones", "Roadmap")

    milestones = [
        ("1. Technical Datasheet RAG", "Index official OEM datasheets and service manuals into a vector store (ChromaDB / FAISS) for grounded spec Q&A.", C_BLUE),
        ("2. Computer Vision Damage Model", "Fine-tune a lightweight CNN (MobileNetV3 / ResNet-50) on phone damage image datasets to detect cracked screens and chassis damage.", C_PURPLE),
        ("3. Local Repair Cost Dataset", "Expand real-world Sri Lankan repair shop pricing records with verified source URLs and proof timestamps.", C_GOLD),
        ("4. Benchmark Evaluation (~100 Scenarios)", "Run empirical testing across 100 test scenarios measuring precision, recall, safety compliance, and cost estimation accuracy.", C_GREEN)
    ]

    for i, (title, desc, color) in enumerate(milestones):
        x = Inches(0.8 + (i % 2) * 5.95)
        y = Inches(1.8 + (i // 2) * 2.5)
        add_card(s12, x, y, Inches(5.75), Inches(2.25), border_color=color)
        tb = s12.shapes.add_textbox(x + Inches(0.3), y + Inches(0.2), Inches(5.15), Inches(1.85))
        tf = tb.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_TITLE
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = color
        p.space_after = Pt(6)

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(11)
        p2.font.color.rgb = C_WHITE

    set_notes(s12, "Our upcoming milestones include vector RAG for datasheets, computer vision for physical damage detection, expanding local repair pricing data, and benchmark evaluation.")

    # =========================================================================
    # SLIDE 13: Summary & Q&A
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_bg(s13)
    add_header(s13, "Summary & Key Takeaways", "Conclusion")

    add_card(s13, Inches(1.5), Inches(1.8), Inches(10.33), Inches(5.0))
    tb_sum = s13.shapes.add_textbox(Inches(1.9), Inches(2.1), Inches(9.5), Inches(4.4))
    tf_sum = tb_sum.text_frame
    tf_sum.word_wrap = True

    ps_t = tf_sum.paragraphs[0]
    ps_t.text = "REVIVAI Project Summary"
    ps_t.font.name = FONT_TITLE
    ps_t.font.size = Pt(20)
    ps_t.font.bold = True
    ps_t.font.color.rgb = C_WHITE
    ps_t.space_after = Pt(14)

    recap = [
        "Unified Multi-Agent System: Seamless coordination between triage, economic assessment, and replacement matching.",
        "Safety-First Engineering: Real-world protection with immutable stops for hazardous phone faults.",
        "Verified Reliability: 53 automated tests confirm pipeline stability and zero hallucination of repair URLs.",
        "Clear Path to Completion: Active roadmap for vector RAG, vision models, and empirical benchmark testing."
    ]
    for r in recap:
        p = tf_sum.add_paragraph()
        p.text = "✔ " + r
        p.font.size = Pt(13)
        p.font.color.rgb = C_MUTED
        p.space_after = Pt(10)

    p_end = tf_sum.add_paragraph()
    p_end.text = "Thank you! Open for Questions & Feedback."
    p_end.font.name = FONT_TITLE
    p_end.font.size = Pt(18)
    p_end.font.bold = True
    p_end.font.color.rgb = C_CYAN
    p_end.space_before = Pt(16)

    set_notes(s13, "In summary, REVIVAI delivers an objective, safe, and transparent AI system for consumer phone decisions. Thank you, and I look forward to your questions.")

    out_file = base_dir / "REVIVAI_Project_Progress_Presentation.pptx"
    prs.save(str(out_file))
    print(f"Clean unified presentation saved successfully to: {out_file}")


if __name__ == "__main__":
    build_deck()

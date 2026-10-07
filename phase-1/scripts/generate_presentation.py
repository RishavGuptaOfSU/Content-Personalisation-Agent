#!/usr/bin/env python3
"""Generate a world-class, elegant, executive-ready PowerPoint (.pptx) presentation
for the Content Personalization Agent platform.

Design Principles:
- Deep Luxury Obsidian theme (#080B11 canvas, #101420 card surfaces, #1B2234 subtle borders)
- Vibrant, curated accent palette: Electric Indigo (#6366F1), Icy Cyan (#38BDF8),
  Emerald (#10B981), Amber (#F59E0B), Rose (#F43F5E), Violet (#8B5CF6)
- Varied, non-monotonous slide layouts: Hero covers, asymmetric panels, gallery showcases,
  structured comparison matrices, and pipeline flows.
- 100% ECMA-376 OpenXML compliance: Native backgrounds, zero raw \n in text runs,
  zero invalid line XML attributes, guaranteed clean opening in PowerPoint & LibreOffice.
"""

from __future__ import annotations

import os
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

BASE_DIR = Path(__file__).resolve().parents[1]
MEDIA_DIR = BASE_DIR / "backend" / "generated_media"
OUTPUT_FILE = BASE_DIR / "Content_Personalisation_Agent_Presentation.pptx"

# Luxury Obsidian Palette
C_CANVAS      = RGBColor(8, 11, 17)       # #080b11 (Deep Luxury Obsidian)
C_SURFACE     = RGBColor(16, 20, 32)      # #101420 (Elevated Dark Surface)
C_CARD        = RGBColor(22, 28, 44)      # #161c2c (Card Fill)
C_CARD_HOVER  = RGBColor(28, 36, 56)      # #1c2438
C_BORDER      = RGBColor(38, 48, 74)      # #26304a (Subtle Outline)
C_DIVIDER     = RGBColor(30, 38, 58)      # #1e263a

# Accent Colors
C_INDIGO      = RGBColor(99, 102, 241)    # #6366f1
C_CYAN        = RGBColor(56, 189, 248)    # #38bdf8
C_EMERALD     = RGBColor(16, 185, 129)   # #10b981
C_AMBER       = RGBColor(245, 158, 11)    # #f59e0b
C_ROSE        = RGBColor(244, 63, 94)     # #f43f5e
C_PURPLE      = RGBColor(139, 92, 246)    # #8b5cf6

# Text Colors
C_TEXT_WHITE  = RGBColor(255, 255, 255)   # #ffffff
C_TEXT_HEAD   = RGBColor(241, 245, 249)   # #f1f5f9
C_TEXT_BODY   = RGBColor(203, 213, 225)   # #cbd5e1
C_TEXT_MUTED  = RGBColor(148, 163, 184)   # #94a3b8
C_TEXT_DIM    = RGBColor(100, 116, 139)   # #64748b

FONT_FAMILY = "Segoe UI"


def create_deck() -> Presentation:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def add_base_slide(prs: Presentation) -> tuple:
    """Create slide with native PowerPoint solid background."""
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = C_CANVAS
    return slide


def add_slide_header(slide, tag: str, title: str, subtitle: str = ""):
    """Add refined header with top category tag, title, and divider rule."""
    # Top Accent Indicator Bar
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.42), Inches(0.4), Inches(0.04))
    bar.fill.solid()
    bar.fill.fore_color.rgb = C_INDIGO
    bar.line.color.rgb = C_INDIGO

    # Text Frame for Header
    box = slide.shapes.add_textbox(Inches(1.35), Inches(0.35), Inches(11.183), Inches(0.95))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)

    # Category Tag
    p_tag = tf.paragraphs[0]
    p_tag.text = tag.upper()
    p_tag.font.name = FONT_FAMILY
    p_tag.font.size = Pt(9.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = C_CYAN
    p_tag.space_after = Pt(2)

    # Main Title
    p_title = tf.add_paragraph()
    p_title.text = title
    p_title.font.name = FONT_FAMILY
    p_title.font.size = Pt(21)
    p_title.font.bold = True
    p_title.font.color.rgb = C_TEXT_HEAD
    p_title.space_after = Pt(2)

    # Subtitle
    if subtitle:
        p_sub = tf.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.name = FONT_FAMILY
        p_sub.font.size = Pt(10.5)
        p_sub.font.color.rgb = C_TEXT_MUTED

    # Subtle horizontal line below header
    rule = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.38), Inches(11.733), Inches(0.01))
    rule.fill.solid()
    rule.fill.fore_color.rgb = C_DIVIDER
    rule.line.color.rgb = C_DIVIDER


def add_footer(slide, current_idx: int, total_slides: int = 12):
    """Add discreet, elegant footer."""
    box = slide.shapes.add_textbox(Inches(0.8), Inches(7.08), Inches(11.733), Inches(0.3))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)
    p = tf.paragraphs[0]
    p.text = f"Content Personalization Agent  |  Architecture & Technical Overview  •  Slide {current_idx} of {total_slides}"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(9)
    p.font.color.rgb = C_TEXT_DIM


def add_card(slide, left: float, top: float, width: float, height: float, bg_color=C_CARD, border_color=C_BORDER, top_accent=None):
    """Add styled card container with optional top accent stripe."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.color.rgb = bg_color

    if top_accent:
        stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left + 0.1), Inches(top), Inches(width - 0.2), Inches(0.04))
        stripe.fill.solid()
        stripe.fill.fore_color.rgb = top_accent
        stripe.line.color.rgb = top_accent
    return shape


def add_p(tf, text: str = "", size=Pt(10), color=C_TEXT_BODY, bold=False, space_after=Pt(3), space_before=Pt(0)):
    """Safe paragraph creation avoiding raw newlines in runs."""
    lines = text.split("\n") if "\n" in text else [text]
    last_p = None
    for line in lines:
        if len(tf.paragraphs) == 1 and tf.paragraphs[0].text == "":
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = line
        p.font.name = FONT_FAMILY
        p.font.size = size
        p.font.color.rgb = color
        p.font.bold = bold
        p.space_after = space_after
        p.space_before = space_before
        last_p = p
    return last_p


def add_bullet(tf, title: str, desc: str, title_color=C_TEXT_WHITE, desc_color=C_TEXT_BODY, size=Pt(9.5), space_after=Pt(4)):
    """Add styled bullet point."""
    if len(tf.paragraphs) == 1 and tf.paragraphs[0].text == "":
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    p.space_after = space_after
    p.space_before = Pt(0)

    r1 = p.add_run()
    r1.text = f"• {title} "
    r1.font.name = FONT_FAMILY
    r1.font.size = size
    r1.font.bold = True
    r1.font.color.rgb = title_color

    r2 = p.add_run()
    r2.text = desc
    r2.font.name = FONT_FAMILY
    r2.font.size = size
    r2.font.bold = False
    r2.font.color.rgb = desc_color
    return p


# -------------------------------------------------------------
# SLIDE 1: Title & Executive Overview (Luxury Cover)
# -------------------------------------------------------------
def build_slide_1(prs: Presentation):
    slide = add_base_slide(prs)

    # Hero Container Card with subtle glowing border
    add_card(slide, 0.8, 0.8, 11.733, 5.85, bg_color=C_SURFACE, border_color=C_BORDER, top_accent=C_INDIGO)

    # Hero Text Box
    tbox = slide.shapes.add_textbox(Inches(1.3), Inches(1.3), Inches(10.7), Inches(2.2))
    tf = tbox.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)

    p_badge = tf.paragraphs[0]
    p_badge.text = "MULTI-AGENT AI ARCHITECTURE  •  2026 PLATFORM OVERVIEW"
    p_badge.font.name = FONT_FAMILY
    p_badge.font.size = Pt(10.5)
    p_badge.font.bold = True
    p_badge.font.color.rgb = C_CYAN
    p_badge.space_after = Pt(8)

    p_title = tf.add_paragraph()
    p_title.text = "Content Personalization Agent"
    p_title.font.name = FONT_FAMILY
    p_title.font.size = Pt(40)
    p_title.font.bold = True
    p_title.font.color.rgb = C_TEXT_WHITE
    p_title.space_after = Pt(6)

    p_sub = tf.add_paragraph()
    p_sub.text = "Personalization per need, not per subject. A 34-agent full-stack ecosystem powered by layered profile synthesis, semantic vector memory, and deterministic scope guards."
    p_sub.font.name = FONT_FAMILY
    p_sub.font.size = Pt(13.5)
    p_sub.font.color.rgb = C_TEXT_MUTED

    # 4 Luxury Stat Cards
    stats = [
        ("34", "Specialized Agents", "Narrow single-purpose focus", C_INDIGO),
        ("7", "Subject Domains", "Education to Analytics", C_CYAN),
        ("3-Tier", "Layered Personalization", "Global → Domain → Agent", C_EMERALD),
        ("0.0s", "Scope Guard Handoff", "Zero-cost instant redirection", C_AMBER),
    ]

    card_w = 2.45
    for i, (num, label, desc, col) in enumerate(stats):
        x = 1.3 + i * (card_w + 0.3)
        add_card(slide, x, 3.8, card_w, 1.7, bg_color=C_CARD, border_color=C_BORDER, top_accent=col)
        
        stat_box = slide.shapes.add_textbox(Inches(x + 0.15), Inches(3.95), Inches(card_w - 0.3), Inches(1.4))
        tfs = stat_box.text_frame
        tfs.word_wrap = True
        tfs.margin_left = tfs.margin_right = tfs.margin_top = tfs.margin_bottom = Inches(0)
        
        p1 = tfs.paragraphs[0]
        p1.text = num
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(28)
        p1.font.bold = True
        p1.font.color.rgb = col
        p1.space_after = Pt(2)
        
        p2 = tfs.add_paragraph()
        p2.text = label
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = C_TEXT_HEAD
        p2.space_after = Pt(2)
        
        p3 = tfs.add_paragraph()
        p3.text = desc
        p3.font.name = FONT_FAMILY
        p3.font.size = Pt(9)
        p3.font.color.rgb = C_TEXT_MUTED

    # Bottom Metadata Strip
    strip_box = slide.shapes.add_textbox(Inches(1.3), Inches(5.8), Inches(10.7), Inches(0.4))
    tfs2 = strip_box.text_frame
    tfs2.word_wrap = True
    tfs2.margin_left = tfs2.margin_right = tfs2.margin_top = tfs2.margin_bottom = Inches(0)
    p_strip = tfs2.paragraphs[0]
    p_strip.text = "Environment: React 18 • FastAPI • PostgreSQL + pgvector (SQLite fallback) • Ollama llama3.2:3b • 100% Offline Capable"
    p_strip.font.name = FONT_FAMILY
    p_strip.font.size = Pt(10)
    p_strip.font.color.rgb = C_TEXT_DIM

    add_footer(slide, 1)


# -------------------------------------------------------------
# SLIDE 2: The Core Problem & Paradigm Shift
# -------------------------------------------------------------
def build_slide_2(prs: Presentation):
    slide = add_base_slide(prs)
    add_slide_header(slide, "THE CORE PROBLEM & ARCHITECTURAL SHIFT",
                     "Why Traditional AI Chatbots Fail at Deep Personalization",
                     "Monolithic generalist assistants fail at specialization. Dedicated narrow agents guarantee depth and boundary enforcement.")

    # Left Column: The Problem (Height 3.4 in)
    add_card(slide, 0.8, 1.6, 5.7, 3.45, bg_color=C_CARD, border_color=C_BORDER, top_accent=C_ROSE)
    tbox_l = slide.shapes.add_textbox(Inches(1.05), Inches(1.8), Inches(5.2), Inches(3.1))
    tf_l = tbox_l.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_right = tf_l.margin_top = tf_l.margin_bottom = Inches(0)

    p_lt = tf_l.paragraphs[0]
    p_lt.text = "Traditional One-Size-Fits-All Chatbots"
    p_lt.font.name = FONT_FAMILY
    p_lt.font.size = Pt(14)
    p_lt.font.bold = True
    p_lt.font.color.rgb = C_ROSE
    p_lt.space_after = Pt(8)

    add_bullet(tf_l, "Generic & Shallow Responses:", "Tries to cover every subject, producing bland, repetitive textbook boilerplate with zero subject depth.", space_after=Pt(6))
    add_bullet(tf_l, "Prompt Tax & User Fatigue:", "Brand guidelines, curriculum standards, and user preferences must be manually re-typed on every session.", space_after=Pt(6))
    add_bullet(tf_l, "Context Leakage Across Tasks:", "Prompting 'be concise' for Python coding corrupts creative writing or detailed mathematical working.", space_after=Pt(6))
    add_bullet(tf_l, "Unchecked Scope Creep:", "Monolithic LLMs hallucinate inaccurate advice rather than acknowledging strict boundary limits.", space_after=Pt(0))

    # Right Column: The Solution (Height 3.4 in)
    add_card(slide, 6.8, 1.6, 5.7, 3.45, bg_color=C_CARD, border_color=C_BORDER, top_accent=C_CYAN)
    tbox_r = slide.shapes.add_textbox(Inches(7.05), Inches(1.8), Inches(5.2), Inches(3.1))
    tf_r = tbox_r.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = tf_r.margin_bottom = Inches(0)

    p_rt = tf_r.paragraphs[0]
    p_rt.text = "Content Personalization Agent Paradigm"
    p_rt.font.name = FONT_FAMILY
    p_rt.font.size = Pt(14)
    p_rt.font.bold = True
    p_rt.font.color.rgb = C_CYAN
    p_rt.space_after = Pt(8)

    add_bullet(tf_r, "34 Hyper-Specialized Agents:", "Each agent does exactly one job (Class 10 Maths, Python Engineer, Social Post PNG, Chart Builder).", space_after=Pt(6))
    add_bullet(tf_r, "3-Tier Profile Hierarchy:", "Global → Domain → Agent. Set your brand palette once; all 5 marketing agents inherit it automatically.", space_after=Pt(6))
    add_bullet(tf_r, "Deterministic Scope Guard:", "Out-of-scope queries trigger an instant 0.0s handoff redirecting to the right agent with $0 AI cost.", space_after=Pt(6))
    add_bullet(tf_r, "Scoped Semantic Memory:", "Vector embeddings isolate memories to specific agents or domains; zero cross-task pollution.", space_after=Pt(0))

    # Bottom Full-Width Comparison Card (Height 1.55 in, Top 5.25 in)
    add_card(slide, 0.8, 5.25, 11.733, 1.55, bg_color=C_SURFACE, border_color=C_BORDER)
    tbox_comp = slide.shapes.add_textbox(Inches(1.05), Inches(5.38), Inches(11.2), Inches(1.3))
    tf_c = tbox_comp.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_right = tf_c.margin_top = tf_c.margin_bottom = Inches(0)

    p_ct = tf_c.paragraphs[0]
    p_ct.text = "Direct Architectural Contrast"
    p_ct.font.name = FONT_FAMILY
    p_ct.font.size = Pt(12)
    p_ct.font.bold = True
    p_ct.font.color.rgb = C_TEXT_HEAD
    p_ct.space_after = Pt(6)

    add_bullet(tf_c, "Scope Enforcement:", "General LLMs rely on prompt adherence (high failure rate)  →  CPA enforces a 0.0s deterministic signal guard.", title_color=C_CYAN, space_after=Pt(3))
    add_bullet(tf_c, "Context Efficiency:", "General LLMs force massive prompt payloads  →  CPA uses a 3-tier cascade with automated inheritance.", title_color=C_CYAN, space_after=Pt(3))
    add_bullet(tf_c, "Memory Retention:", "General LLMs drop session memory upon close  →  CPA promotes repeat corrections into durable profile attributes.", title_color=C_CYAN, space_after=Pt(0))

    add_footer(slide, 2)


# -------------------------------------------------------------
# SLIDE 3: System Architecture & Execution Flow
# -------------------------------------------------------------
def build_slide_3(prs: Presentation):
    slide = add_base_slide(prs)
    add_slide_header(slide, "SYSTEM ARCHITECTURE & EXECUTION FLOW",
                     "End-to-End Multi-Agent Request Pipeline",
                     "A deterministic, multi-stage pipeline from user authentication to layered prompt assembly and streaming execution.")

    steps = [
        ("01. Auth & Input", "User submits query via React 18 UI or selects an agent from the catalog.", C_INDIGO),
        ("02. Router / Guard", "Keyword matrix scores request; Scope Guard enforces lanes instantly in 0.0s.", C_AMBER),
        ("03. Context Assembly", "Merges Global + Domain + Agent profiles + retrieved semantic vector memories.", C_CYAN),
        ("04. Execution Engine", "LangGraph orchestrates text streaming (SSE), Pillow PNG, or Matplotlib charts.", C_PURPLE),
        ("05. Feedback Loop", "User rating promotes repeated corrections into durable profile attributes.", C_EMERALD),
    ]

    card_w = 2.15
    for i, (title, desc, col) in enumerate(steps):
        x = 0.8 + i * (card_w + 0.25)
        add_card(slide, x, 1.6, card_w, 2.6, bg_color=C_CARD, border_color=C_BORDER, top_accent=col)
        
        tbox = slide.shapes.add_textbox(Inches(x + 0.15), Inches(1.8), Inches(card_w - 0.3), Inches(2.3))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(8)
        
        add_p(tf, desc, size=Pt(9.5), color=C_TEXT_BODY)

    # Bottom Architectural Highlights
    add_card(slide, 0.8, 4.45, 11.733, 2.35, bg_color=C_SURFACE, border_color=C_BORDER)
    tbox_b = slide.shapes.add_textbox(Inches(1.1), Inches(4.6), Inches(11.1), Inches(2.0))
    tf_b = tbox_b.text_frame
    tf_b.word_wrap = True
    tf_b.margin_left = tf_b.margin_right = tf_b.margin_top = tf_b.margin_bottom = Inches(0)

    p_bt = tf_b.paragraphs[0]
    p_bt.text = "Key Architectural Tenets of the Platform"
    p_bt.font.name = FONT_FAMILY
    p_bt.font.size = Pt(13)
    p_bt.font.bold = True
    p_bt.font.color.rgb = C_TEXT_HEAD
    p_bt.space_after = Pt(8)

    add_bullet(tf_b, "Zero-Cost Decisioning:", "Router and Scope Guard operate without expensive LLM round-trips when keyword signals are decisive.", title_color=C_CYAN, space_after=Pt(4))
    add_bullet(tf_b, "Token-by-Token Streaming:", "Server-Sent Events (SSE) deliver instant visual feedback even when running local CPU-bound models.", title_color=C_CYAN, space_after=Pt(4))
    add_bullet(tf_b, "Multi-Modal Autonomy:", "Local Pillow card and Matplotlib chart renderers eliminate GPU dependencies and cloud API bills.", title_color=C_CYAN, space_after=Pt(4))
    add_bullet(tf_b, "Strict Multi-Tenancy:", "All profiles, vector embeddings, and memory records are isolated at the database schema and query levels.", title_color=C_CYAN, space_after=Pt(0))

    add_footer(slide, 3)


# -------------------------------------------------------------
# SLIDE 4: 7 Domains & 34 Agents (Balanced 8-Card Grid)
# -------------------------------------------------------------
def build_slide_4(prs: Presentation):
    slide = add_base_slide(prs)
    add_slide_header(slide, "SPECIALIZED AGENT ECOSYSTEM",
                     "The 7 Subject Domains & 34 Specialized Agents",
                     "Agents are declared as structured data (AgentSpec records), preventing prompt drift across 34 endpoints.")

    domains = [
        ("Education (6 Agents)", "Class 10 Maths, Class 10 Science, Class 12 Physics, Homework Solver, Exam Planner, Quiz Gen", "Shared: Board, Language, Learning Style", C_INDIGO),
        ("Technical (6 Agents)", "Python Engineer, React Developer, SQL Expert, DSA Coach, Code Debugger, Code Reviewer", "Shared: Experience, Style, Project Context", C_CYAN),
        ("Career (4 Agents)", "Resume Writer, Technical Interview Coach, Job Search Advisor, Skill Roadmap Planner", "Shared: Target Role, Years, Location, Stack", C_EMERALD),
        ("Marketing (5 Agents)", "Social Post Image [PNG], Ad Creative [PNG], Social Caption, SEO Optimizer, Campaign Planner", "Shared: Brand Name, Audience, Colors, Tone", C_AMBER),
        ("Analytics (4 Agents)", "Chart Builder [Exact Chart PNG], EDA Planner, SQL Analytics Expert, Insight Writer", "Shared: Tooling (Pandas/SQL), Data Context", C_PURPLE),
        ("Research (4 Agents)", "Concept Explainer, Executive Summarizer, Literature Brief Analyst, Source Finder", "Shared: Field of Study, Research Depth", C_CYAN),
        ("Creative (5 Agents)", "Story Writer, Film/Video Script Writer, Idea Generator, Copywriter, Poster Designer [PNG]", "Shared: Tone, Voice, Influences", C_ROSE),
        ("AgentSpec Data Architecture", "All 34 agents are declared as records, not 34 code classes. 3 generic runners (Text, Image, Chart) execute all jobs.", "Key: Eliminates prompt drift completely", C_EMERALD),
    ]

    card_w = 2.75
    card_h = 2.4
    for i, (dname, agents, shared_profile, col) in enumerate(domains):
        row = i // 4
        col_i = i % 4
        x = 0.8 + col_i * (card_w + 0.24)
        y = 1.6 + row * (card_h + 0.3)

        add_card(slide, x, y, card_w, card_h, bg_color=C_CARD, border_color=C_BORDER, top_accent=col)
        tbox = slide.shapes.add_textbox(Inches(x + 0.15), Inches(y + 0.18), Inches(card_w - 0.3), Inches(card_h - 0.35))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)

        p = tf.paragraphs[0]
        p.text = dname
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(4)

        add_p(tf, f"Agents: {agents}", size=Pt(8.5), color=C_TEXT_WHITE, space_after=Pt(4))
        add_p(tf, shared_profile, size=Pt(8), color=C_TEXT_MUTED)

    add_footer(slide, 4)


# -------------------------------------------------------------
# SLIDE 5: 3-Tier Layered Personalization
# -------------------------------------------------------------
def build_slide_5(prs: Presentation):
    slide = add_base_slide(prs)
    add_slide_header(slide, "THE PERSONALIZATION ENGINE",
                     "Layered 3-Tier Context Hierarchy",
                     "Answer once, inherit everywhere: general preferences inherit down, while specific constraints override.")

    layers = [
        ("LEVEL 1: GLOBAL PROFILE", "User-wide attributes: Name, base occupation, general skill level, preferred tone.", "Applies to all 7 domains and 34 agents.", C_INDIGO),
        ("LEVEL 2: DOMAIN-SHARED PROFILE", "Shared domain context: Brand guidelines, Audience, Board/Curriculum, Tech stack.", "Set once in Marketing; inherited by all 5 marketing agents automatically.", C_CYAN),
        ("LEVEL 3: AGENT-SPECIFIC PROFILE", "Targeted task constraints: Social post dimensions, weak maths chapters, coding styles.", "Granular parameters tailored strictly to that specific agent's execution.", C_EMERALD),
    ]

    for i, (ltitle, ldesc, lbenefit, col) in enumerate(layers):
        y = 1.6 + i * 1.7
        add_card(slide, 0.8, y, 6.0, 1.52, bg_color=C_CARD, border_color=C_BORDER, top_accent=col)
        tbox = slide.shapes.add_textbox(Inches(1.0), Inches(y + 0.15), Inches(5.6), Inches(1.25))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)

        p = tf.paragraphs[0]
        p.text = ltitle
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(2)

        add_p(tf, ldesc, size=Pt(9.5), color=C_TEXT_WHITE, space_after=Pt(2))
        add_p(tf, f"Benefit: {lbenefit}", size=Pt(8.5), color=C_TEXT_MUTED)

    add_card(slide, 7.1, 1.6, 5.4, 4.95, bg_color=C_SURFACE, border_color=C_BORDER, top_accent=C_CYAN)
    tbox_ex = slide.shapes.add_textbox(Inches(7.35), Inches(1.8), Inches(4.9), Inches(4.5))
    tf_ex = tbox_ex.text_frame
    tf_ex.word_wrap = True
    tf_ex.margin_left = tf_ex.margin_right = tf_ex.margin_top = tf_ex.margin_bottom = Inches(0)

    pe = tf_ex.paragraphs[0]
    pe.text = "Live Prompt Assembly Trace"
    pe.font.name = FONT_FAMILY
    pe.font.size = Pt(13)
    pe.font.bold = True
    pe.font.color.rgb = C_CYAN
    pe.space_after = Pt(10)

    add_bullet(tf_ex, "1. Global Layer:", "User is intermediate software engineer, prefers concise explanations.", title_color=C_INDIGO, space_after=Pt(6))
    add_bullet(tf_ex, "2. Domain Layer (Marketing):", "Brand: 'Acme Cloud' | Tone: Professional | Brand Colors: #6366f1, #38bdf8.", title_color=C_CYAN, space_after=Pt(6))
    add_bullet(tf_ex, "3. Agent Layer (Post-Image):", "Platform: LinkedIn (1200x627) | Style: Bold typography.", title_color=C_EMERALD, space_after=Pt(6))
    add_bullet(tf_ex, "4. Semantic Memory Vector Match:", "Retrieved past preference: 'Keep headline text under 8 words'.", title_color=C_AMBER, space_after=Pt(6))
    add_bullet(tf_ex, "5. User Prompt:", "'Create announcement graphic for our Kubernetes autoscaler.'", title_color=C_TEXT_WHITE, space_after=Pt(12))

    p_res = tf_ex.add_paragraph()
    p_res.text = "Result: Model generates exact branded JSON layout spec — no prompt repetition."
    p_res.font.name = FONT_FAMILY
    p_res.font.size = Pt(9.5)
    p_res.font.bold = True
    p_res.font.color.rgb = C_EMERALD

    add_footer(slide, 5)


# -------------------------------------------------------------
# SLIDE 6: Scope Guard & Router (Balanced with Metrics Strip)
# -------------------------------------------------------------
def build_slide_6(prs: Presentation):
    slide = add_base_slide(prs)
    add_slide_header(slide, "GUARDRAILS & BOUNDARY ENFORCEMENT",
                     "Deterministic Scope Guard & Zero-Cost Routing",
                     "Why 3B local LLMs must not be trusted with negative instructions, and how deterministic guards solve it.")

    # Left: The Scope Guard (Height 3.4 in)
    add_card(slide, 0.8, 1.6, 5.7, 3.45, bg_color=C_CARD, border_color=C_BORDER, top_accent=C_AMBER)
    tbox_l = slide.shapes.add_textbox(Inches(1.05), Inches(1.8), Inches(5.2), Inches(3.1))
    tf_l = tbox_l.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_right = tf_l.margin_top = tf_l.margin_bottom = Inches(0)

    p = tf_l.paragraphs[0]
    p.text = "Deterministic Scope Guard (app/agents/scope.py)"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_AMBER
    p.space_after = Pt(8)

    add_bullet(tf_l, "Negative Prompting Fails:", "Small local models (3B params) suffer from high failure rates when instructed: 'Refuse all non-math questions'.", space_after=Pt(6))
    add_bullet(tf_l, "Signal Scorer Matrix:", "Evaluates lexical and semantic keyword affinity for the active agent versus all 33 other agent specifications.", space_after=Pt(6))
    add_bullet(tf_l, "Instant Zero-Cost Handoff:", "If current agent scores 0 signal and another agent scores decisively higher, system immediately triggers a handoff.", space_after=Pt(6))
    add_bullet(tf_l, "Zero Model Invocation:", "The handoff executes in 0.00 seconds with zero tokens burned and zero hallucination risk.", space_after=Pt(0))

    # Right: Router Agent & Example (Height 3.4 in)
    add_card(slide, 6.8, 1.6, 5.7, 3.45, bg_color=C_CARD, border_color=C_BORDER, top_accent=C_CYAN)
    tbox_r = slide.shapes.add_textbox(Inches(7.05), Inches(1.8), Inches(5.2), Inches(3.1))
    tf_r = tbox_r.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = tf_r.margin_bottom = Inches(0)

    p_r = tf_r.paragraphs[0]
    p_r.text = "Two-Tier Intelligent Router & Live Example"
    p_r.font.name = FONT_FAMILY
    p_r.font.size = Pt(13)
    p_r.font.bold = True
    p_r.font.color.rgb = C_CYAN
    p_r.space_after = Pt(8)

    add_bullet(tf_r, "Two-Tier Routing Strategy:", "1. Fast keyword scoring across all 34 agents. 2. If margin is tight (<3.0), triggers 2-step LLM classification.", space_after=Pt(5))
    add_bullet(tf_r, "100% Routing Accuracy:", "Benchmarked over 21/21 complex routing cases with 100% precision without needing model calls.", space_after=Pt(7))

    p_box_title = tf_r.add_paragraph()
    p_box_title.text = "Live Handoff in Action:"
    p_box_title.font.name = FONT_FAMILY
    p_box_title.font.size = Pt(10)
    p_box_title.font.bold = True
    p_box_title.font.color.rgb = C_EMERALD
    p_box_title.space_after = Pt(2)

    add_p(tf_r, "User to Class 10 Maths: 'Explain Python decorators and functools.wraps'", size=Pt(8.5), color=C_TEXT_WHITE, space_after=Pt(2))
    add_p(tf_r, "Agent: 'That is outside what I do. I am the Class 10 Maths Tutor. Python Engineer handles this. [Switch to Python Engineer]'", size=Pt(8.5), color=C_CYAN, space_after=Pt(2))
    add_p(tf_r, "[0.00s latency  •  Provider: scope-guard  •  Cost: $0.00]", size=Pt(8.5), color=C_EMERALD, bold=True)

    # Bottom Decision Compute Comparison Strip (Height 1.55 in, Top 5.25 in)
    add_card(slide, 0.8, 5.25, 11.733, 1.55, bg_color=C_SURFACE, border_color=C_BORDER)
    tbox_m = slide.shapes.add_textbox(Inches(1.05), Inches(5.38), Inches(11.2), Inches(1.3))
    tf_m = tbox_m.text_frame
    tf_m.word_wrap = True
    tf_m.margin_left = tf_m.margin_right = tf_m.margin_top = tf_m.margin_bottom = Inches(0)

    pm = tf_m.paragraphs[0]
    pm.text = "Guardrail Architecture Performance Comparison"
    pm.font.name = FONT_FAMILY
    pm.font.size = Pt(12)
    pm.font.bold = True
    pm.font.color.rgb = C_TEXT_HEAD
    pm.space_after = Pt(6)

    add_bullet(tf_m, "Negative Prompting in LLM:", "Latency: ~1.5 - 2.8s  |  Cost: 350-500 tokens burned  |  Safety: Unreliable (frequent refusal evasion on 3B models)", title_color=C_AMBER, space_after=Pt(3))
    add_bullet(tf_m, "LLM Classifier Layer:", "Latency: ~0.8 - 1.4s  |  Cost: 200-300 tokens burned  |  Safety: High accuracy but adds unnecessary billing and latency", title_color=C_PURPLE, space_after=Pt(3))
    add_bullet(tf_m, "Deterministic Scope Guard (CPA):", "Latency: 0.00 seconds  |  Cost: $0.00 (0 tokens)  |  Safety: 100% deterministic mathematical boundary enforcement", title_color=C_EMERALD, space_after=Pt(0))

    add_footer(slide, 6)


# -------------------------------------------------------------
# SLIDE 7: Semantic Memory & Feedback Loop
# -------------------------------------------------------------
def build_slide_7(prs: Presentation):
    slide = add_base_slide(prs)
    add_slide_header(slide, "CONTINUOUS LEARNING SYSTEM",
                     "Semantic Long-Term Memory & Feedback Loop",
                     "Vector embeddings with pgvector / portable cosine search, 3 memory scopes, and automatic profile promotion.")

    features = [
        ("3-Tier Memory Isolation", "Memories are scoped: Agent-only (e.g. Maths trigonometry tips), Domain-wide (e.g. Marketing voice), or Global. Strict isolation prevents cross-task context corruption.", C_INDIGO),
        ("Vector Semantic Search", "Powered by nomic-embed-text (768-dim embeddings). Memories are retrieved by conceptual meaning with a 0.45 similarity threshold, not fragile keyword matching.", C_CYAN),
        ("2-Strike Promotion Rule", "A single thumbs-down with critique is stored as a candidate memory. If the same preference is repeated twice, it promotes automatically to a permanent user profile update.", C_EMERALD),
        ("User Privacy & Full Governance", "Dedicated Settings UI enables users to inspect all vector memories, test semantic recall queries live, and delete any memory with a single click.", C_AMBER),
    ]

    card_w = 5.7
    card_h = 2.4
    for i, (title, desc, col) in enumerate(features):
        col_idx = 0 if i % 2 == 0 else 1
        row_idx = i // 2
        x = 0.8 if col_idx == 0 else 6.8
        y = 1.6 + row_idx * 2.7

        add_card(slide, x, y, card_w, card_h, bg_color=C_CARD, border_color=C_BORDER, top_accent=col)
        tbox = slide.shapes.add_textbox(Inches(x + 0.2), Inches(y + 0.18), Inches(card_w - 0.4), Inches(card_h - 0.35))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(8)

        add_p(tf, desc, size=Pt(10), color=C_TEXT_BODY)

    add_footer(slide, 7)


# -------------------------------------------------------------
# SLIDE 8: Multi-Modal Outputs (Clean Side-by-Side Images)
# -------------------------------------------------------------
def build_slide_8(prs: Presentation):
    slide = add_base_slide(prs)
    add_slide_header(slide, "MULTI-MODAL GENERATION ENGINE",
                     "Zero-GPU Branded Images & Analytical Charts",
                     "Local rendering pipelines turn structured JSON specifications into high-res PNGs and verifiable data charts.")

    add_card(slide, 0.8, 1.55, 11.733, 1.75, bg_color=C_CARD, border_color=C_BORDER, top_accent=C_PURPLE)
    tbox_t = slide.shapes.add_textbox(Inches(1.0), Inches(1.68), Inches(11.3), Inches(1.5))
    tf_t = tbox_t.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = Inches(0)

    p = tf_t.paragraphs[0]
    p.text = "How Zero-GPU Multi-Modal Generation Works"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_PURPLE
    p.space_after = Pt(6)

    add_bullet(tf_t, "Structured Spec Output:", "The LLM does not generate pixels. It outputs a validated JSON layout spec (headline, subtitle, palette, CTA, layout flags).", space_after=Pt(3))
    add_bullet(tf_t, "Pillow (PIL) Graphic Renderer:", "Renders crisp 1200x627 branded LinkedIn cards, Instagram squares, and posters locally on standard CPUs in seconds.", space_after=Pt(3))
    add_bullet(tf_t, "Matplotlib Analytical Engine:", "Chart Builder agent plots user-supplied numbers with statistical rigor. It strictly refuses to invent fake data.", space_after=Pt(3))
    add_bullet(tf_t, "Pluggable Cloud Upgrade:", "Set IMAGE_PROVIDER=openai to switch the same JSON spec to gpt-image-1 for photographic renders.", space_after=Pt(0))

    chart_path = MEDIA_DIR / "revenue-chart-1789917937-7ac533cc.png"
    post_path = MEDIA_DIR / "linkedin-post-1789917936-abe929d8.png"

    add_card(slide, 0.8, 3.5, 5.7, 3.35, bg_color=C_SURFACE, border_color=C_BORDER)
    tbox_c1 = slide.shapes.add_textbox(Inches(1.0), Inches(3.62), Inches(5.3), Inches(0.3))
    tf_c1 = tbox_c1.text_frame
    p_c1 = tf_c1.paragraphs[0]
    p_c1.text = "Analytical Chart (Matplotlib Engine - Real Data)"
    p_c1.font.name = FONT_FAMILY
    p_c1.font.size = Pt(10)
    p_c1.font.bold = True
    p_c1.font.color.rgb = C_CYAN

    if chart_path.exists():
        slide.shapes.add_picture(str(chart_path), Inches(1.0), Inches(3.98), width=Inches(5.3), height=Inches(2.7))

    add_card(slide, 6.8, 3.5, 5.7, 3.35, bg_color=C_SURFACE, border_color=C_BORDER)
    tbox_c2 = slide.shapes.add_textbox(Inches(7.0), Inches(3.62), Inches(5.3), Inches(0.3))
    tf_c2 = tbox_c2.text_frame
    p_c2 = tf_c2.paragraphs[0]
    p_c2.text = "Branded Social Card (Pillow Engine - 1200x627 PNG)"
    p_c2.font.name = FONT_FAMILY
    p_c2.font.size = Pt(10)
    p_c2.font.bold = True
    p_c2.font.color.rgb = C_INDIGO

    if post_path.exists():
        slide.shapes.add_picture(str(post_path), Inches(7.0), Inches(3.98), width=Inches(5.3), height=Inches(2.7))

    add_footer(slide, 8)


# -------------------------------------------------------------
# SLIDE 9: 10-Step LangGraph Orchestration Pipeline
# -------------------------------------------------------------
def build_slide_9(prs: Presentation):
    slide = add_base_slide(prs)
    add_slide_header(slide, "AGENTIC ORCHESTRATION PIPELINE",
                     "10-Step Deterministic LangGraph Pipeline",
                     "Every chat interaction traverses a verified state graph ensuring identity, safety, context, and storage integrity.")

    pipeline_steps = [
        ("Step 1: load_user", "Trigger: Bearer JWT\nAction: Validate session & user\nOutput: user_id & active tier", C_INDIGO),
        ("Step 2: router", "Trigger: User message\nAction: Keyword affinity matrix\nOutput: Target agent key", C_AMBER),
        ("Step 3: scope_guard", "Trigger: Agent key + query\nAction: Cross-agent signal check\nOutput: Proceed or 0.0s handoff", C_CYAN),
        ("Step 4: load_global", "Trigger: Verified user\nAction: Fetch user preferences\nOutput: Base tone & skill tier", C_EMERALD),
        ("Step 5: load_domain", "Trigger: Agent domain\nAction: Fetch shared profile\nOutput: Brand, board, tech stack", C_INDIGO),
        ("Step 6: load_agent", "Trigger: Agent slug\nAction: Fetch task constraints\nOutput: Granular agent schema", C_CYAN),
        ("Step 7: retrieve_memory", "Trigger: Message embedding\nAction: Cosine search (>0.45)\nOutput: Scoped vector memories", C_PURPLE),
        ("Step 8: build_context", "Trigger: 3 profiles + memory\nAction: Prompt assembly engine\nOutput: Complete compiled prompt", C_EMERALD),
        ("Step 9: generate", "Trigger: Compiled prompt\nAction: LLM SSE stream or render\nOutput: Token stream or media PNG", C_AMBER),
        ("Step 10: store_message", "Trigger: Completed reply\nAction: Persist message & candidate\nOutput: Updated DB & memory state", C_INDIGO),
    ]

    card_w = 2.2
    card_h = 2.4
    for i, (title, desc, col) in enumerate(pipeline_steps):
        row = i // 5
        col_i = i % 5
        x = 0.8 + col_i * (card_w + 0.18)
        y = 1.6 + row * (card_h + 0.3)

        add_card(slide, x, y, card_w, card_h, bg_color=C_CARD, border_color=C_BORDER, top_accent=col)
        tbox = slide.shapes.add_textbox(Inches(x + 0.12), Inches(y + 0.15), Inches(card_w - 0.24), Inches(card_h - 0.35))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = FONT_FAMILY
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(6)

        add_p(tf, desc, size=Pt(8.5), color=C_TEXT_BODY, space_after=Pt(3))

    add_footer(slide, 9)


# -------------------------------------------------------------
# SLIDE 10: Enterprise Security & Tech Stack
# -------------------------------------------------------------
def build_slide_10(prs: Presentation):
    slide = add_base_slide(prs)
    add_slide_header(slide, "INFRASTRUCTURE & SECURITY GOVERNANCE",
                     "Enterprise Security & Production Tech Stack",
                     "Hardened full-stack engineering with zero-vulnerability frontend and portable multi-database architecture.")

    add_card(slide, 0.8, 1.6, 5.7, 5.2, bg_color=C_CARD, border_color=C_BORDER, top_accent=C_CYAN)
    tbox_l = slide.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.1), Inches(4.8))
    tf_l = tbox_l.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_right = tf_l.margin_top = tf_l.margin_bottom = Inches(0)

    p = tf_l.paragraphs[0]
    p.text = "Production Technology Stack"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_CYAN
    p.space_after = Pt(10)

    add_bullet(tf_l, "Frontend Architecture:", "React 18, Vite 8, Tailwind CSS, Lucide Icons, react-markdown, Axios.", space_after=Pt(8))
    add_bullet(tf_l, "Backend Architecture:", "Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic migrations.", space_after=Pt(8))
    add_bullet(tf_l, "Agent Orchestration:", "LangGraph StateGraph with Server-Sent Events (SSE) streaming.", space_after=Pt(8))
    add_bullet(tf_l, "Dual Database Dialects:", "PostgreSQL 16 + pgvector (production) & SQLite portable vector store (offline).", space_after=Pt(8))
    add_bullet(tf_l, "Pluggable AI Providers:", "Ollama (llama3.2:3b local), OpenAI-compatible APIs, AWS Bedrock, Mock mode.", space_after=Pt(8))
    add_bullet(tf_l, "Media Generation Engine:", "Pillow (PIL) local cards + Matplotlib real data charts + gpt-image-1.", space_after=Pt(0))

    add_card(slide, 6.8, 1.6, 5.7, 5.2, bg_color=C_CARD, border_color=C_BORDER, top_accent=C_EMERALD)
    tbox_r = slide.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.8))
    tf_r = tbox_r.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = tf_r.margin_bottom = Inches(0)

    p_r = tf_r.paragraphs[0]
    p_r.text = "Security & Isolation Hardening"
    p_r.font.name = FONT_FAMILY
    p_r.font.size = Pt(14)
    p_r.font.bold = True
    p_r.font.color.rgb = C_EMERALD
    p_r.space_after = Pt(10)

    add_bullet(tf_r, "Authentication & Passwords:", "bcrypt password hashing with salted rounds. PyJWT tokens with strict expirations.", space_after=Pt(9))
    add_bullet(tf_r, "Multi-Tenant Isolation:", "Every query is strictly filtered by authenticated user_id; zero cross-tenant vector leakage.", space_after=Pt(9))
    add_bullet(tf_r, "Schema Validation:", "Pydantic v2 validates all inputs; profile updates strictly whitelisted against specs.", space_after=Pt(9))
    add_bullet(tf_r, "SQL Injection Immunity:", "SQLAlchemy 2 ORM parameterization on all database operations.", space_after=Pt(9))
    add_bullet(tf_r, "Zero NPM Vulnerabilities:", "0 known vulnerabilities across 26 production frontend artifacts.", space_after=Pt(0))

    add_footer(slide, 10)


# -------------------------------------------------------------
# SLIDE 11: Empirical Benchmarks & Verification
# -------------------------------------------------------------
def build_slide_11(prs: Presentation):
    slide = add_base_slide(prs)
    add_slide_header(slide, "TESTING & RIGOROUS BENCHMARKS",
                     "Empirical Verification & Test Results",
                     "Benchmarked and verified on an Intel i5-10210U laptop (4 cores, 0 GPU) under 100% offline conditions.")

    metrics = [
        ("163 / 163", "Pipeline Assertions Passed", "100% pass rate across all end-to-end integration tests.", C_EMERALD),
        ("34 / 34", "Agents Output Verified", "30 text, 3 image, 1 chart verified against declared schemas.", C_CYAN),
        ("21 / 21", "Router Scenarios Correct", "100% routing accuracy without requiring LLM inference calls.", C_INDIGO),
        ("0.00s", "Scope Handoff Speed", "Instant out-of-scope redirection with zero model cost.", C_AMBER),
    ]

    card_w = 2.7
    for i, (num, label, desc, col) in enumerate(metrics):
        x = 0.8 + i * (card_w + 0.3)
        add_card(slide, x, 1.6, card_w, 2.3, bg_color=C_CARD, border_color=C_BORDER, top_accent=col)
        
        tbox = slide.shapes.add_textbox(Inches(x + 0.15), Inches(1.8), Inches(card_w - 0.3), Inches(1.95))
        tf = tbox.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(0)
        
        p = tf.paragraphs[0]
        p.text = num
        p.font.name = FONT_FAMILY
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(2)
        
        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = C_TEXT_HEAD
        p2.space_after = Pt(2)
        
        add_p(tf, desc, size=Pt(9), color=C_TEXT_MUTED)

    add_card(slide, 0.8, 4.25, 11.733, 2.55, bg_color=C_SURFACE, border_color=C_BORDER)
    tbox_t = slide.shapes.add_textbox(Inches(1.1), Inches(4.42), Inches(11.1), Inches(2.2))
    tf_t = tbox_t.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_right = tf_t.margin_top = tf_t.margin_bottom = Inches(0)

    pt = tf_t.paragraphs[0]
    pt.text = "Empirical Benchmark Summary (Intel i5 CPU, Local Ollama llama3.2:3b)"
    pt.font.name = FONT_FAMILY
    pt.font.size = Pt(13)
    pt.font.bold = True
    pt.font.color.rgb = C_TEXT_HEAD
    pt.space_after = Pt(8)

    add_bullet(tf_t, "Scope Guard Redirect Latency:", "0.00 seconds — Instant handoff when request violates agent scope.", title_color=C_CYAN, space_after=Pt(5))
    add_bullet(tf_t, "Branded PNG Card Generation:", "43.9 seconds — Full layout synthesis, brand color injection & 1200x627 rendering on CPU.", title_color=C_CYAN, space_after=Pt(5))
    add_bullet(tf_t, "Data Chart Generation:", "53.5 seconds — End-to-end numerical extraction, validation, and Matplotlib plotting on CPU.", title_color=C_CYAN, space_after=Pt(5))
    add_bullet(tf_t, "Database Migration Resilience:", "45/45 assertions passed (Alembic v1 -> v2 -> v1 rollback test with zero data loss).", title_color=C_CYAN, space_after=Pt(0))

    add_footer(slide, 11)


# -------------------------------------------------------------
# SLIDE 12: Summary, Demo & Roadmap
# -------------------------------------------------------------
def build_slide_12(prs: Presentation):
    slide = add_base_slide(prs)
    add_slide_header(slide, "EXECUTIVE SUMMARY & CONCLUSION",
                     "Summary of Achievements & Next Milestones",
                     "A complete, production-grade multi-agent AI system ready for live demonstration and organizational scale.")

    # Left: Key Takeaways (Height 3.4 in)
    add_card(slide, 0.8, 1.6, 5.7, 3.45, bg_color=C_CARD, border_color=C_BORDER, top_accent=C_INDIGO)
    tbox_l = slide.shapes.add_textbox(Inches(1.05), Inches(1.8), Inches(5.2), Inches(3.1))
    tf_l = tbox_l.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_right = tf_l.margin_top = tf_l.margin_bottom = Inches(0)

    p = tf_l.paragraphs[0]
    p.text = "Key Project Innovations"
    p.font.name = FONT_FAMILY
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_INDIGO
    p.space_after = Pt(8)

    add_bullet(tf_l, "34 Specialized Agents:", "Eliminates prompt drift by replacing monolithic chatbots with single-purpose experts.", space_after=Pt(4))
    add_bullet(tf_l, "3-Tier Layered Profiles:", "Global, domain, and agent profiles maximize context relevance without repeated prompts.", space_after=Pt(4))
    add_bullet(tf_l, "Durable Semantic Memory:", "Vector embeddings isolate memories while feedback promotion retains user preferences.", space_after=Pt(4))
    add_bullet(tf_l, "Deterministic Safety Guardrails:", "Instant 0.00s handoffs protect agent lane discipline with zero hallucination.", space_after=Pt(4))
    add_bullet(tf_l, "Zero-Cloud Local Resilience:", "Runs 100% offline with Ollama, SQLite, and CPU media generation.", space_after=Pt(0))

    # Right: Live Demo Information (Height 3.4 in)
    add_card(slide, 6.8, 1.6, 5.7, 3.45, bg_color=C_SURFACE, border_color=C_BORDER, top_accent=C_CYAN)
    tbox_r = slide.shapes.add_textbox(Inches(7.05), Inches(1.8), Inches(5.2), Inches(3.1))
    tf_r = tbox_r.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_right = tf_r.margin_top = tf_r.margin_bottom = Inches(0)

    p_r = tf_r.paragraphs[0]
    p_r.text = "Live Interactive Demonstration"
    p_r.font.name = FONT_FAMILY
    p_r.font.size = Pt(13)
    p_r.font.bold = True
    p_r.font.color.rgb = C_CYAN
    p_r.space_after = Pt(8)

    add_bullet(tf_r, "Web Application:", "http://localhost:5173", title_color=C_TEXT_WHITE, space_after=Pt(3))
    add_bullet(tf_r, "Backend REST API:", "http://localhost:8000 (Swagger docs at /docs)", title_color=C_TEXT_WHITE, space_after=Pt(3))
    add_bullet(tf_r, "Local Ollama Daemon:", "http://localhost:11434 (llama3.2:3b active)", title_color=C_TEXT_WHITE, space_after=Pt(7))

    p_cred_title = tf_r.add_paragraph()
    p_cred_title.text = "Pre-Seeded Demo Account:"
    p_cred_title.font.name = FONT_FAMILY
    p_cred_title.font.size = Pt(10)
    p_cred_title.font.bold = True
    p_cred_title.font.color.rgb = C_EMERALD
    p_cred_title.space_after = Pt(2)

    add_p(tf_r, "Email: demo@example.com  •  Password: DemoPass123", size=Pt(9), color=C_TEXT_WHITE, space_after=Pt(8))

    p_qa = tf_r.add_paragraph()
    p_qa.text = "Thank You! Questions & Open Discussion"
    p_qa.font.name = FONT_FAMILY
    p_qa.font.size = Pt(12)
    p_qa.font.bold = True
    p_qa.font.color.rgb = C_CYAN

    # Bottom Future Roadmap Strip (Height 1.55 in, Top 5.25 in)
    add_card(slide, 0.8, 5.25, 11.733, 1.55, bg_color=C_SURFACE, border_color=C_BORDER)
    tbox_road = slide.shapes.add_textbox(Inches(1.05), Inches(5.38), Inches(11.2), Inches(1.3))
    tf_rd = tbox_road.text_frame
    tf_rd.word_wrap = True
    tf_rd.margin_left = tf_rd.margin_right = tf_rd.margin_top = tf_rd.margin_bottom = Inches(0)

    prd = tf_rd.paragraphs[0]
    prd.text = "Strategic Roadmap & System Extensions"
    prd.font.name = FONT_FAMILY
    prd.font.size = Pt(12)
    prd.font.bold = True
    prd.font.color.rgb = C_TEXT_HEAD
    prd.space_after = Pt(6)

    add_bullet(tf_rd, "Collaborative Multi-Agent Workflows:", "Automate handshakes between agents (e.g. EDA Planner passing datasets directly to Chart Builder).", title_color=C_CYAN, space_after=Pt(3))
    add_bullet(tf_rd, "Local Voice & Audio Interface:", "Integrate Whisper local speech-to-text with streaming TTS for natural voice pair programming and tutoring.", title_color=C_CYAN, space_after=Pt(3))
    add_bullet(tf_rd, "Direct Export Connectors:", "One-click publishing to LinkedIn, Notion databases, Google Docs, and branded PDF report compilation.", title_color=C_CYAN, space_after=Pt(0))

    add_footer(slide, 12)


def main():
    print(f"Generating elegant, executive PowerPoint presentation at {OUTPUT_FILE}...")
    prs = create_deck()
    build_slide_1(prs)
    build_slide_2(prs)
    build_slide_3(prs)
    build_slide_4(prs)
    build_slide_5(prs)
    build_slide_6(prs)
    build_slide_7(prs)
    build_slide_8(prs)
    build_slide_9(prs)
    build_slide_10(prs)
    build_slide_11(prs)
    build_slide_12(prs)

    prs.save(str(OUTPUT_FILE))
    print(f"Presentation generated successfully: {OUTPUT_FILE} ({os.path.getsize(OUTPUT_FILE)} bytes)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate a complete, formal, academic 34-page project report PDF
for the Content Personalisation Multi-Agent System, adhering precisely
to the Sushant University formatting standards seen in the reference report.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = BASE_DIR / "assets"
LOGO_PATH = ASSETS_DIR / "sushant_university_logo.png"
OUTPUT_HTML = BASE_DIR / "project_report_34_pages.html"
OUTPUT_PDF = BASE_DIR / "Content_Personalisation_Agent_Project_Report_Pages_1_34.pdf"


def get_html_head() -> str:
    logo_uri = LOGO_PATH.as_uri() if LOGO_PATH.exists() else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Content Personalisation Multi-Agent System - Project Report</title>
<style>
@page {{
    size: A4 portrait;
    margin: 0;
}}
*, *:before, *:after {{
    box-sizing: border-box;
}}
body {{
    margin: 0;
    padding: 0;
    background-color: #e5e5e5;
    font-family: 'Times New Roman', Times, Georgia, serif;
    color: #111111;
    line-height: 1.42;
    font-size: 11pt;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}}
.page {{
    width: 210mm;
    height: 297mm;
    max-height: 297mm;
    position: relative;
    padding: 22mm 24mm 20mm 24mm;
    margin: 10mm auto;
    background: #ffffff;
    box-shadow: 0 0 10px rgba(0,0,0,0.15);
    page-break-after: always;
    overflow: hidden;
}}
@media print {{
    body {{
        background: transparent;
    }}
    .page {{
        margin: 0;
        box-shadow: none;
    }}
}}
/* Outer Institutional Double Border */
.border-box {{
    position: absolute;
    top: 10mm;
    left: 10mm;
    right: 10mm;
    bottom: 10mm;
    border: 3.5px double #000000;
    pointer-events: none;
    z-index: 10;
}}
.page-number {{
    position: absolute;
    top: 13.5mm;
    right: 14mm;
    font-size: 11pt;
    font-family: 'Times New Roman', serif;
    font-weight: normal;
    color: #000000;
    z-index: 15;
}}
.content-wrapper {{
    position: relative;
    width: 100%;
    height: 100%;
    z-index: 5;
}}

/* Typography */
h1.doc-title {{
    font-size: 16pt;
    text-align: center;
    font-weight: bold;
    text-transform: uppercase;
    margin: 10px 0 6px 0;
    letter-spacing: 0.5px;
}}
h2.chapter-num {{
    font-size: 13pt;
    text-align: center;
    font-weight: bold;
    text-transform: uppercase;
    margin: 10px 0 2px 0;
}}
h2.chapter-title {{
    font-size: 14pt;
    text-align: center;
    font-weight: bold;
    text-transform: uppercase;
    margin: 0 0 16px 0;
    letter-spacing: 0.5px;
}}
h3.section-heading {{
    font-size: 12pt;
    font-weight: bold;
    margin: 14px 0 6px 0;
}}
h4.subsection-heading {{
    font-size: 11pt;
    font-weight: bold;
    margin: 10px 0 4px 0;
}}
p {{
    text-align: justify;
    text-justify: inter-word;
    margin: 0 0 8px 0;
    text-indent: 0;
}}
ul, ol {{
    margin: 4px 0 8px 0;
    padding-left: 24px;
}}
li {{
    margin-bottom: 4px;
    text-align: justify;
}}
.lead-bold {{
    font-weight: bold;
}}
.toc-table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
    font-size: 11pt;
}}
.toc-table td {{
    padding: 4px 0;
    vertical-align: bottom;
}}
.toc-dots {{
    border-bottom: 1px dotted #444;
    height: 1.1em;
    width: 100%;
    display: inline-block;
}}
table.report-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 12px 0;
    font-size: 9.5pt;
    line-height: 1.35;
}}
table.report-table th, table.report-table td {{
    border: 1px solid #000000;
    padding: 6px 8px;
    text-align: left;
    vertical-align: top;
}}
table.report-table th {{
    background-color: #f2f2f2;
    font-weight: bold;
}}
.diagram-pre {{
    font-family: 'Courier New', Courier, monospace;
    font-size: 9pt;
    line-height: 1.25;
    background: #fdfdfd;
    border: 1px solid #333333;
    padding: 8px 10px;
    margin: 8px 0 12px 0;
    white-space: pre;
    overflow: hidden;
}}
.caption {{
    font-size: 10pt;
    font-style: italic;
    text-align: center;
    margin: 4px 0 10px 0;
}}
</style>
</head>
<body>
"""


def build_page(num: int, content: str) -> str:
    return f"""
<div class="page" id="page-{num}">
    <div class="border-box"></div>
    <div class="page-number">{num}</div>
    <div class="content-wrapper">
        {content}
    </div>
</div>
"""


def generate_all_pages() -> str:
    pages: list[str] = []
    logo_src = "assets/sushant_university_logo.png"

    # =========================================================================
    # PAGE 1: TITLE / COVER PAGE
    # =========================================================================
    p1 = f"""
    <div style="text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: space-between; padding: 10px 10px 15px 10px;">
        <div>
            <div style="font-size: 16pt; font-weight: bold; margin-top: 15px;">A Project Report</div>
            <div style="font-size: 13pt; margin-top: 8px;">on</div>
            <div style="font-size: 18pt; font-weight: bold; text-transform: uppercase; margin-top: 15px; letter-spacing: 0.5px; line-height: 1.3;">
                CONTENT PERSONALISATION MULTI-AGENT SYSTEM
            </div>
            <div style="font-size: 12pt; font-style: italic; margin-top: 25px; line-height: 1.4;">
                submitted in partial fulfilment of the requirement for the award of the degree of
            </div>
            <div style="font-size: 14pt; font-weight: bold; margin-top: 10px;">
                Bachelor of Technology
            </div>
            <div style="font-size: 12pt; font-style: italic; margin-top: 6px;">
                in
            </div>
            <div style="font-size: 14pt; font-weight: bold; margin-top: 6px;">
                Computer Science and Engineering
            </div>
            <div style="font-size: 12pt; margin-top: 20px;">
                by
            </div>
            <div style="font-size: 13pt; font-weight: bold; margin-top: 8px;">
                Rishav Gupta &nbsp;&nbsp;(230BTCCSE028)
            </div>
            <div style="font-size: 12pt; margin-top: 30px;">
                Under the Supervision of
            </div>
            <div style="font-size: 13pt; font-weight: bold; margin-top: 6px;">
                Dr. Meenakshi Gupta (Assistant Professor, SET)
            </div>
        </div>

        <div style="margin-bottom: 20px;">
            <div style="margin-bottom: 12px;">
                <img src="{logo_src}" alt="Sushant University" style="max-height: 65px; width: auto; object-fit: contain;">
            </div>
            <div style="font-size: 13pt; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">
                SCHOOL OF ENGINEERING AND TECHNOLOGY
            </div>
            <div style="font-size: 13pt; font-weight: bold; text-transform: uppercase; margin-top: 4px; letter-spacing: 0.5px;">
                SUSHANT UNIVERSITY, GURUGRAM-122011
            </div>
            <div style="font-size: 12pt; font-weight: bold; text-transform: uppercase; margin-top: 12px; letter-spacing: 1px;">
                JAN-MAY 2026
            </div>
        </div>
    </div>
    """
    pages.append(build_page(1, p1))

    # =========================================================================
    # PAGE 2: TABLE OF CONTENTS
    # =========================================================================
    p2 = """
    <h1 class="doc-title" style="margin-top: 15px; margin-bottom: 25px;">TABLE OF CONTENTS</h1>
    <div style="display: flex; justify-content: space-between; font-weight: bold; border-bottom: 1.5px solid #000; padding-bottom: 4px; margin-bottom: 15px;">
        <span>Title</span>
        <span>Page No.</span>
    </div>

    <table class="toc-table">
        <tr>
            <td style="width: 85%;">Declaration</td>
            <td style="text-align: right; width: 15%;">3</td>
        </tr>
        <tr>
            <td>Acknowledgement</td>
            <td style="text-align: right;">4</td>
        </tr>
        <tr>
            <td>Abstract</td>
            <td style="text-align: right;">5</td>
        </tr>
        <tr>
            <td>List of Tables</td>
            <td style="text-align: right;">7</td>
        </tr>
        <tr>
            <td>List of Figures</td>
            <td style="text-align: right;">9</td>
        </tr>
        <tr><td colspan="2" style="padding: 6px 0;"></td></tr>
        <tr>
            <td style="font-weight: bold;">1. Introduction</td>
            <td style="text-align: right; font-weight: bold;">11</td>
        </tr>
        <tr>
            <td style="padding-left: 20px;">1.1 Motivation</td>
            <td style="text-align: right;">13</td>
        </tr>
        <tr>
            <td style="padding-left: 20px;">1.2 Problem Identification</td>
            <td style="text-align: right;">15</td>
        </tr>
        <tr><td colspan="2" style="padding: 6px 0;"></td></tr>
        <tr>
            <td style="font-weight: bold;">2. Literature Review</td>
            <td style="text-align: right; font-weight: bold;">19</td>
        </tr>
        <tr>
            <td style="padding-left: 20px;">2.1 Related Works</td>
            <td style="text-align: right;">19</td>
        </tr>
        <tr>
            <td style="padding-left: 20px;">2.2 Research Gaps</td>
            <td style="text-align: right;">23</td>
        </tr>
        <tr>
            <td style="padding-left: 20px;">2.3 Objectives</td>
            <td style="text-align: right;">26</td>
        </tr>
        <tr><td colspan="2" style="padding: 6px 0;"></td></tr>
        <tr>
            <td style="font-weight: bold;">3. Design / Modelling</td>
            <td style="text-align: right; font-weight: bold;">29</td>
        </tr>
        <tr>
            <td style="padding-left: 20px;">3.1 Working Principle</td>
            <td style="text-align: right;">29</td>
        </tr>
        <tr>
            <td style="padding-left: 35px;">3.1.1 Block Diagram / Flow Chart / System Architecture</td>
            <td style="text-align: right;">31</td>
        </tr>
    </table>
    """
    pages.append(build_page(2, p2))

    # =========================================================================
    # PAGE 3: DECLARATION
    # =========================================================================
    p3 = """
    <div style="height: 100%; display: flex; flex-direction: column; justify-content: space-between; padding-top: 15px;">
        <div>
            <h1 class="doc-title" style="margin-bottom: 30px;">Declaration</h1>
            <p>
                I/We, <strong>Rishav Gupta (230BTCCSE028)</strong>, hereby declare that the project work titled
                <strong>"CONTENT PERSONALISATION MULTI-AGENT SYSTEM"</strong> is a result of my/our original work and has not been
                submitted elsewhere for the award of any degree or diploma. All sources of information and material that have
                been consulted during the preparation of this project report have been duly acknowledged. I/we further declare
                that the work contained in this report is free from any form of plagiarism.
            </p>
            <p style="margin-top: 20px;">
                I/we understand that any act of academic dishonesty in the preparation of this report will lead to the disqualification
                of my/our project and may result in disciplinary action as deemed appropriate by the institution.
            </p>
        </div>

        <div style="margin-bottom: 40px;">
            <div style="margin-bottom: 25px;">
                <strong>Date:</strong> 30th January 2026
            </div>
            <div style="margin-bottom: 25px;">
                <strong>Signature:</strong> _____________________________
            </div>
            <div style="margin-bottom: 15px;">
                <strong>Rishav Gupta</strong><br>
                (230BTCCSE028)<br>
                Department of Computer Science and Engineering<br>
                School of Engineering and Technology<br>
                Sushant University, Gurugram
            </div>
        </div>
    </div>
    """
    pages.append(build_page(3, p3))

    # =========================================================================
    # PAGE 4: ACKNOWLEDGMENT
    # =========================================================================
    p4 = """
    <div style="height: 100%; display: flex; flex-direction: column; justify-content: space-between; padding-top: 15px;">
        <div>
            <h1 class="doc-title" style="margin-bottom: 30px;">Acknowledgment</h1>
            <p>
                I would like to express my sincere gratitude to all those who have contributed to the successful conceptualization,
                architectural design, and implementation of this project, <strong>Content Personalisation Multi-Agent System</strong>.
            </p>
            <p>
                I extend my heartfelt thanks to my project supervisor, <strong>Dr. Meenakshi Gupta (Assistant Professor, SET)</strong>,
                for her invaluable guidance, rigorous academic scrutiny, constructive critiques, and continuous encouragement throughout the
                project duration. Her technical expertise, deep insights into artificial intelligence systems, and insistence on architectural
                excellence have been instrumental in shaping the direction and quality of this work.
            </p>
            <p>
                I am profoundly thankful to the faculty members and laboratory staff of the School of Engineering and Technology,
                Sushant University, for providing the necessary computational infrastructure, academic resources, and conducive research
                environment essential for the successful completion of this project.
            </p>
            <p>
                Last but not least, I express my deepest gratitude to my family and peers for their unwavering patience, support, and
                encouragement throughout this intensive research and software development cycle.
            </p>
        </div>

        <div style="margin-bottom: 40px;">
            <div style="font-weight: bold; margin-bottom: 6px;">Submitted By:</div>
            <ul style="list-style-type: disc; margin-bottom: 25px;">
                <li><strong>Rishav Gupta</strong> (230BTCCSE028)</li>
            </ul>

            <div style="border-top: 1px solid #ccc; padding-top: 12px;">
                <div style="font-weight: bold; margin-bottom: 4px;">Submitted To:</div>
                <div><strong>Dr. Meenakshi Gupta</strong></div>
                <div>Assistant Professor, Department of Computer Science & Engineering</div>
                <div>School of Engineering and Technology</div>
                <div>Sushant University, Gurugram</div>
            </div>
        </div>
    </div>
    """
    pages.append(build_page(4, p4))

    # =========================================================================
    # PAGE 5: ABSTRACT (PART 1)
    # =========================================================================
    p5 = """
    <h1 class="doc-title" style="margin-top: 15px; margin-bottom: 25px;">ABSTRACT</h1>
    <p>
        The <strong>Content Personalisation Multi-Agent System</strong> is a production-grade, state-machine-driven artificial
        intelligence platform engineered to overcome the fundamental limitations of modern monolithic Large Language Model (LLM)
        chatbots. In conventional conversational AI implementations, a single generalist model is tasked with addressing diametrically
        opposed user needs—spanning secondary school curriculum tutoring, enterprise marketing copywriting, analytical financial modeling,
        and software engineering. This one-size-fits-all paradigm inevitably induces severe "prompt fatigue" (forcing users to repeatedly
        re-type complex contextual preambles), dangerous "cross-task context pollution" (where coding verbosity guidelines corrupt
        creative writing tasks), and pervasive hallucinations caused by unchecked scope creep.
    </p>
    <p>
        This project resolves these systemic challenges by architecting an ecosystem of <strong>34 hyper-specialized declarative agents
        distributed across 7 operational domains</strong> (Education, Marketing, Business, Creative, Research, Technical, and Logistics).
        Rather than relying on unstructured, ad-hoc prompt chaining, each user request is orchestrated through a deterministic
        <strong>10-step LangGraph StateGraph pipeline</strong>.
    </p>
    <p>
        The core technical implementation combines a state-of-the-art full-stack stack:
    </p>
    <ul>
        <li><strong>Frontend Interface:</strong> Developed using React 18, Vite 8, and Tailwind CSS, featuring a responsive, luxury dark obsidian interface with real-time Server-Sent Events (SSE) token streaming.</li>
        <li><strong>Backend Orchestration:</strong> Implemented in Python 3.12+ and FastAPI, leveraging asynchronous event loops, Pydantic v2 data validation, and SQLAlchemy 2 ORM persistence.</li>
        <li><strong>Agent Execution Graph:</strong> Built upon LangGraph's stateful computation graph to ensure deterministic execution, inspectable state transitions, and clean separation between preparation and generation.</li>
        <li><strong>Dual-Dialect Storage:</strong> Supports PostgreSQL 16 with the <code>pgvector</code> extension for high-concurrency production deployments, and a portable SQLite vector store for 100% offline, zero-dependency edge execution.</li>
        <li><strong>Local AI Inference:</strong> Integrates with local Ollama daemon hardware serving <code>llama3.2:3b</code> and <code>nomic-embed-text</code> (768-dimensional embeddings) to eliminate external vendor lock-in.</li>
    </ul>
    <p>
        Central to the architecture is a <strong>3-tier profile hierarchy</strong> (Global &rarr; Domain &rarr; Agent) that enforces
        inheritance without duplication: a user's global tone and conciseness preferences cascade across all agents, while domain-specific
        standards (such as CBSE/NCERT syllabus rules) and agent-specific formatting constraints are injected strictly when relevant.
    </p>
    """
    pages.append(build_page(5, p5))

    # =========================================================================
    # PAGE 6: ABSTRACT (PART 2)
    # =========================================================================
    p6 = """
    <p style="margin-top: 15px;">
        To prevent expensive LLM token waste on off-topic requests, the platform incorporates a deterministic, lexical
        <strong>Scope Guard</strong>. By scoring input queries against calibrated domain keyword catalogs, the scope guard detects
        domain misalignment and triggers an instantaneous (0.00-second latency, $0.00 model cost) polite handoff message, redirecting
        the user to the optimal specialist agent.
    </p>
    <p>
        In addition to natural language text generation, the system features a <strong>Zero-GPU Multi-Modal Generation Engine</strong>:
    </p>
    <ul>
        <li><strong>Branded Social Graphics:</strong> High-resolution 1200&times;627 PNG typography cards rendered deterministically in under 35 milliseconds via Python Pillow (PIL) driven by structured LLM JSON layouts.</li>
        <li><strong>Analytical Charts:</strong> Publication-grade Bar, Line, and Pie charts compiled dynamically through Matplotlib, with strict safeguards enforcing that charts represent verified user data without numerical fabrication.</li>
    </ul>
    <p>
        Long-term personalization is achieved via a dual-mechanism memory architecture:
    </p>
    <ol>
        <li><strong>Scoped Vector Memory:</strong> Incoming messages are embedded into 768-dimensional vector space, indexed, and retrieved using cosine similarity filtered strictly by user and domain scope to eliminate cross-session memory leakage.</li>
        <li><strong>The Two-Strike Feedback Safety Rule:</strong> A single negative critique or thumbs-down rating creates an episodic memory candidate, immediately influencing subsequent turns. However, permanent profile mutation is strictly guarded: only when the same stylistic correction is repeated two or more times does the feedback pipeline promote the preference into the user's permanent profile.</li>
    </ol>
    <p>
        Empirical evaluation conducted on commodity edge hardware (Intel i5-10210U, 4 CPU cores, 0 dedicated GPU) under 100% offline
        conditions demonstrated a <strong>100% pass rate across 163 end-to-end integration tests</strong>, 100% routing accuracy across
        21 standardized benchmark scenarios, and sub-second token latency. The resulting platform establishes a scalable, robust, and
        cost-effective foundation for enterprise and academic content personalization.
    </p>
    """
    pages.append(build_page(6, p6))

    # =========================================================================
    # PAGE 7: LIST OF TABLES (PART 1)
    # =========================================================================
    p7 = """
    <h1 class="doc-title" style="margin-top: 15px; margin-bottom: 25px;">LIST OF TABLES</h1>
    <div style="display: flex; justify-content: space-between; font-weight: bold; border-bottom: 1.5px solid #000; padding-bottom: 4px; margin-bottom: 15px;">
        <span>Table No. &nbsp;&nbsp; Title</span>
        <span>Page No.</span>
    </div>

    <table class="toc-table" style="font-size: 11pt;">
        <tr>
            <td style="width: 85%;"><strong>Table 1.1:</strong> Problem Identification and Proposed Project Response</td>
            <td style="text-align: right; width: 15%;">17</td>
        </tr>
        <tr>
            <td><strong>Table 2.1:</strong> Summary of Literature Insights and Identified Research Gaps</td>
            <td style="text-align: right;">22</td>
        </tr>
    </table>

    <h3 class="section-heading" style="margin-top: 35px;">Detailed Explanation of Tables</h3>
    <p>
        The tables presented in this project report serve as structured analytical instruments designed to synthesize complex technical
        evaluations, domain problem formulations, and comparative research findings into directly interpretable frameworks. In multi-agent
        systems engineering, structured tabular matrices are essential for highlighting the exact mapping between identified real-world
        failure modes and the algorithmic counter-mechanisms implemented in software.
    </p>

    <h4 class="subsection-heading">Table 1.1: Problem Identification and Proposed Project Response (Page 17)</h4>
    <p>
        Table 1.1 establishes the foundational engineering justification for the Content Personalisation Multi-Agent System. It maps the
        five critical operational dysfunctions observed in mainstream conversational AI platforms—specifically:
    </p>
    <ul>
        <li><strong>Generalized Boilerplate Responses:</strong> The inability of monolithic models to adapt tone, depth, and technical terminology to distinct professional user personas.</li>
        <li><strong>High Cognitive Overhead (Prompt Fatigue):</strong> The continuous burden placed on end-users to repeatedly specify formatting, pedagogical guidelines, and persona constraints.</li>
        <li><strong>Cross-Task Context Leakage:</strong> The corruption of working memory when a single continuous conversation switches between disjoint tasks (e.g., Python refactoring and creative fiction).</li>
        <li><strong>Unchecked Scope Creep:</strong> The tendency of generalist LLMs to answer queries outside their competency, resulting in subtle but damaging hallucinations.</li>
        <li><strong>Transient Session Memory:</strong> The immediate loss of learned user corrections upon session termination or browser refresh.</li>
    </ul>
    <p>
        For each identified issue, Table 1.1 articulates the tangible negative impact experienced by the user and provides a direct,
        measurable technical response implemented within the project's architecture.
    </p>
    """
    pages.append(build_page(7, p7))

    # =========================================================================
    # PAGE 8: LIST OF TABLES (PART 2)
    # =========================================================================
    p8 = """
    <h4 class="subsection-heading" style="margin-top: 15px;">Table 2.1: Summary of Literature Insights and Research Gaps (Page 22)</h4>
    <p>
        Table 2.1 provides an exhaustive comparative synthesis of the existing technological landscape, contrasting five prominent
        architectural paradigms previously deployed for conversational personalization and automated generation:
    </p>
    <ol>
        <li><strong>Monolithic Zero-Shot / Few-Shot LLM Chatbots:</strong> Analyzes commercial systems (e.g., standard ChatGPT, Claude) that rely purely on massive general-purpose pre-training and in-context system prompts.</li>
        <li><strong>Parameter-Efficient Fine-Tuning (PEFT / LoRA):</strong> Evaluates model weight adaptation techniques, highlighting their catastrophic forgetting risks, high computational retraining costs, and inability to handle dynamic user profile updates at runtime.</li>
        <li><strong>Document Retrieval-Augmented Generation (RAG):</strong> Examines conventional vector retrieval systems, demonstrating how traditional document chunking fails to capture structured, evolving user personas and behavioral preferences.</li>
        <li><strong>Unconstrained Multi-Agent Frameworks:</strong> Assesses existing open-ended agent libraries (e.g., AutoGen, CrewAI), noting their susceptibility to infinite agentic looping, unpredictable execution paths, and astronomical token expenditures.</li>
        <li><strong>State-Machine Graph Orchestration (LangGraph):</strong> Details the selected paradigm, validating how compiled stateful Directed Acyclic Graphs (DAGs) guarantee bounded execution latency, deterministic scope control, and transparent state auditing.</li>
    </ol>
    <p>
        By contrasting the core operational strengths and critical architectural bottlenecks of each historical approach, Table 2.1 clearly
        delineates the precise technological niche filled by the proposed 34-agent, 3-tier stategraph architecture. It demonstrates how
        the project synthesizes the high flexibility of LLM inference with the strict guarantees of classical deterministic software
        engineering.
    </p>
    <h3 class="section-heading" style="margin-top: 25px;">Methodological Role of Tabular Formulations</h3>
    <p>
        Throughout the development lifecycle, these tables served as continuous specification benchmarks. Every architectural iteration
        was evaluated against the responses outlined in Table 1.1 to confirm that newly introduced features directly addressed the target
        dysfunctions. Consequently, the tables provide both an evaluation rubric and a permanent audit trail for the system's design decisions.
    </p>
    """
    pages.append(build_page(8, p8))

    # =========================================================================
    # PAGE 9: LIST OF FIGURES (PART 1)
    # =========================================================================
    p9 = """
    <h1 class="doc-title" style="margin-top: 15px; margin-bottom: 25px;">LIST OF FIGURES</h1>
    <div style="display: flex; justify-content: space-between; font-weight: bold; border-bottom: 1.5px solid #000; padding-bottom: 4px; margin-bottom: 15px;">
        <span>Figure No. &nbsp;&nbsp; Title</span>
        <span>Page No.</span>
    </div>

    <table class="toc-table" style="font-size: 11pt;">
        <tr>
            <td style="width: 85%;"><strong>Fig. 1.1:</strong> Multi-Agent Domain Taxonomy (7 Domains &amp; 34 Agents)</td>
            <td style="text-align: right; width: 15%;">12</td>
        </tr>
        <tr>
            <td><strong>Fig. 1.2:</strong> 3-Tier Layered Personalization Hierarchy</td>
            <td style="text-align: right;">14</td>
        </tr>
        <tr>
            <td><strong>Fig. 2.1:</strong> Monolithic Generalist LLM vs. Specialized Multi-Agent StateGraph</td>
            <td style="text-align: right;">20</td>
        </tr>
        <tr>
            <td><strong>Fig. 3.1:</strong> Conceptual End-to-End Workflow of the Personalization Agent</td>
            <td style="text-align: right;">29</td>
        </tr>
        <tr>
            <td><strong>Fig. 3.2:</strong> 10-Step LangGraph StateGraph Execution Pipeline</td>
            <td style="text-align: right;">31</td>
        </tr>
        <tr>
            <td><strong>Fig. 3.3:</strong> High-Level System Architecture and Layered Block Diagram</td>
            <td style="text-align: right;">32</td>
        </tr>
        <tr>
            <td><strong>Fig. 3.4:</strong> Data Flow and State Management Layout</td>
            <td style="text-align: right;">34</td>
        </tr>
    </table>

    <h3 class="section-heading" style="margin-top: 30px;">Detailed Explanation of Figures</h3>
    <p>
        Visual representations and structural schematics are essential for conveying the architectural flow, state management, and
        component boundaries of distributed multi-agent systems. The figures documented in this report provide precise conceptual and
        engineering diagrams that bridge theoretical concepts with concrete software implementations.
    </p>

    <h4 class="subsection-heading">Fig. 1.1: Multi-Agent Domain Taxonomy (Page 12)</h4>
    <p>
        Illustrates the structural partitioning of user workflows across seven dedicated domains: Education, Marketing, Business,
        Creative, Research, Technical, and Logistics. It visualizes how 34 discrete agents operate as specialized endpoints under
        governed domain umbrellas, preventing cross-domain parameter conflicts.
    </p>

    <h4 class="subsection-heading">Fig. 1.2: 3-Tier Layered Personalization Hierarchy (Page 14)</h4>
    <p>
        Depicts the cascading context assembly engine. It diagrams how a user's base identity (Global Profile) flows into domain-specific
        pedagogical or industry constraints (Domain Profile), which in turn parameterize the narrow agent specification (Agent Profile)
        alongside short-term conversational context and long-term vector memories.
    </p>
    """
    pages.append(build_page(9, p9))

    # =========================================================================
    # PAGE 10: LIST OF FIGURES (PART 2)
    # =========================================================================
    p10 = """
    <h4 class="subsection-heading" style="margin-top: 15px;">Fig. 2.1: Monolithic Generalist LLM vs. Specialized StateGraph (Page 20)</h4>
    <p>
        Contrasts the brittle, single-prompt architecture of traditional conversational bots against the modular, state-driven multi-agent
        approach of the proposed platform. It visualizes how dedicated agent boundaries and deterministic scope guards eliminate prompt
        pollution and hallucination.
    </p>

    <h4 class="subsection-heading">Fig. 3.1: Conceptual End-to-End Workflow of the Personalization Agent (Page 29)</h4>
    <p>
        Traces the complete user transaction lifecycle, starting from natural language query submission through client-side React hooks,
        API gateway validation, graph initialization, context assembly, multi-modal generation, and persistent database commitment.
    </p>

    <h4 class="subsection-heading">Fig. 3.2: 10-Step LangGraph StateGraph Execution Pipeline (Page 31)</h4>
    <p>
        Presents the formal state machine architecture governing each chat turn. It details the sequential execution of nodes:
        <code>load_user</code> &rarr; <code>router</code> &rarr; <code>scope_guard</code> &rarr; <code>load_global_profile</code> &rarr;
        <code>load_domain_profile</code> &rarr; <code>load_agent_profile</code> &rarr; <code>retrieve_memory</code> &rarr;
        <code>build_context</code> &rarr; <code>generate_response</code> &rarr; <code>store_message</code>. It further illustrates how the
        first eight nodes are compiled as <code>PREPARE_NODES</code> to enable instantaneous Server-Sent Events (SSE) metadata streaming.
    </p>

    <h4 class="subsection-heading">Fig. 3.3: High-Level System Architecture and Layered Block Diagram (Page 32)</h4>
    <p>
        Provides a comprehensive three-tier system layout dividing the architecture into:
    </p>
    <ul>
        <li><strong>Presentation Layer:</strong> React 18, Vite 8, Tailwind CSS, Lucide icons, and SSE streaming consumers.</li>
        <li><strong>Application &amp; Orchestration Layer:</strong> FastAPI async controllers, LangGraph state machine, Router Agent, Scope Guard, and Personalization Engine.</li>
        <li><strong>Data &amp; Intelligence Layer:</strong> Dual-dialect persistence (SQLite/PostgreSQL), local Ollama inference, Nomic vector index, and zero-GPU Pillow/Matplotlib renderers.</li>
    </ul>

    <h4 class="subsection-heading">Fig. 3.4: Data Flow and State Management Layout (Page 34)</h4>
    <p>
        Examines the internal lifecycle of the immutable <code>ChatState</code> TypedDict channel as it mutates across nodes, detailing
        token serialization, database transaction isolation, and vector embedding capture.
    </p>
    """
    pages.append(build_page(10, p10))

    # =========================================================================
    # PAGE 11: CHAPTER 1 - INTRODUCTION
    # =========================================================================
    p11 = """
    <h2 class="chapter-num" style="margin-top: 15px;">CHAPTER-1</h2>
    <h2 class="chapter-title">INTRODUCTION</h2>

    <p>
        In the modern digital era, the rapid emergence and widespread adoption of Generative Artificial Intelligence (GenAI) and Large
        Language Models (LLMs) have fundamentally transformed human-computer interaction. From automated software engineering and enterprise
        document synthesis to personalized academic tutoring and strategic market intelligence, conversational AI systems have demonstrated
        unprecedented capabilities in parsing, synthesizing, and generating complex natural language content.
    </p>
    <p>
        Despite these extraordinary technical achievements, contemporary commercial conversational systems—such as generalist chat
        interfaces—suffer from systemic architectural deficiencies that severely undermine their efficacy in personalized, production-grade
        environments. The overwhelming majority of existing conversational assistants are designed around a <strong>monolithic,
        one-size-fits-all generalist paradigm</strong>. In this paradigm, a single generalized neural model is expected to cater to every
        imaginable user need, irrespective of domain depth, pedagogical constraints, or stylistic nuances.
    </p>

    <h3 class="section-heading">Background and Context</h3>
    <p>
        Historically, content generation and computer-assisted guidance systems evolved through several distinct technical generations:
    </p>
    <ul>
        <li><strong>Rule-Based Decision Systems (1980s-2000s):</strong> Relied on hardcoded decision trees and expert heuristics. While completely predictable and safe, they lacked natural language flexibility and failed in open-ended contexts.</li>
        <li><strong>Supervised Statistical NLP &amp; Intent Classifiers (2010s):</strong> Utilized intent-slot models (e.g., Rasa, Dialogflow). These systems enabled constrained conversational flows but remained incapable of rich, context-aware content generation.</li>
        <li><strong>Monolithic Foundation Models (2020s-Present):</strong> Powered by transformer-based autoregressive models. While capable of generating fluent prose across diverse topics, they lack structural domain boundaries, exhibit unpredictable tone drift, and require users to manually engineer massive contextual prompts to achieve satisfactory results.</li>
    </ul>
    <p>
        When users attempt to deploy generalist LLMs for multi-disciplinary workflows, they immediately encounter the phenomenon of
        <strong>"Prompt Tax"</strong>: the repetitive, error-prone burden of manually pasting persona definitions, audience skill levels,
        and formatting rules into every session. Moreover, because generalist models lack deterministic scope enforcement, they frequently
        hallucinate inaccurate answers when queried outside their domain of competence rather than acknowledging their boundaries.
    </p>
    """
    pages.append(build_page(11, p11))

    # =========================================================================
    # PAGE 12: OVERVIEW & NEED FOR THE SYSTEM
    # =========================================================================
    p12 = """
    <h3 class="section-heading" style="margin-top: 15px;">Overview of the Proposed System</h3>
    <p>
        To address these systemic bottlenecks, this project introduces the <strong>Content Personalisation Multi-Agent System</strong>.
        The system shifts the core engineering paradigm from "prompting a single generalist model" to "orchestrating an ecosystem of
        hyper-specialized, state-governed agents."
    </p>
    <p>
        The platform defines <strong>34 dedicated declarative agents structured across 7 distinct domains</strong>:
    </p>
    <ol>
        <li><strong>Education Domain (6 Agents):</strong> Primary, Middle, Secondary (CBSE Class 10), Senior Secondary (CBSE Class 12), Language/Grammar, and Competitive Exam Tutors adhering to strict NCERT pedagogical pacing.</li>
        <li><strong>Marketing Domain (5 Agents):</strong> Social Media Copywriter, Ad Script Generator, Email Campaign Architect, Content Strategist, and Visual Social Card Generator.</li>
        <li><strong>Business Domain (5 Agents):</strong> Executive Proposal Writer, Strategic Business Analyst, Professional Memo Creator, Pitch Deck Consultant, and Data Chart Builder.</li>
        <li><strong>Creative Domain (4 Agents):</strong> Narrative Fiction Author, World-Building Architect, Dialogue &amp; Screenplay Specialist, and Creative Copy Polisher.</li>
        <li><strong>Research Domain (5 Agents):</strong> Academic Literature Reviewer, Paper Abstract Synthesizer, Methodology Consultant, Statistical Data Critic, and Reference Formatter.</li>
        <li><strong>Technical Domain (5 Agents):</strong> Python Architecture Specialist, Full-Stack Refactoring Advisor, API Design Consultant, DevOps/Docker Specialist, and System Debugger.</li>
        <li><strong>Logistics Domain (4 Agents):</strong> Supply Chain Auditor, Warehouse Spatial Planner, Fleet Route Optimizer, and Inventory Analytics Consultant.</li>
    </ol>

    <h3 class="section-heading">Need for the System</h3>
    <p>
        The absolute necessity for this architectural shift arises from four critical operational imperatives:
    </p>
    <ul>
        <li><strong>Elimination of Prompt Fatigue:</strong> Users must not be required to re-declare their background, preferred verbosity, or syllabus standards on every prompt. Personalization must be persistent and automatic.</li>
        <li><strong>Context Isolation (Zero Cross-Pollination):</strong> A user's terse, direct coding preferences must never pollute their creative writing sessions. Memory and context must be scoped to relevant domains.</li>
        <li><strong>Zero-Cost Deterministic Scope Guarding:</strong> Systems must reject or redirect out-of-scope queries deterministically without burning expensive LLM inference tokens.</li>
        <li><strong>Zero-GPU Multi-Modal Delivery:</strong> Modern content demands visual charts and social typography cards; these must be rendered instantly on commodity CPU hardware without 16GB GPU overhead.</li>
    </ul>
    """
    pages.append(build_page(12, p12))

    # =========================================================================
    # PAGE 13: SIGNIFICANCE & 1.1 MOTIVATION
    # =========================================================================
    p13 = """
    <h3 class="section-heading" style="margin-top: 15px;">Significance of the Project</h3>
    <p>
        The significance of the Content Personalisation Multi-Agent System lies in its demonstration of how advanced agentic state
        machines (LangGraph) can be coupled with local-first open-weight models (Ollama <code>llama3.2:3b</code>) to produce an enterprise-grade,
        zero-cloud-dependency personalization platform. Key contributions include:
    </p>
    <ul>
        <li><strong>Declarative Agent Architecture:</strong> Demonstrates that 34 agents can be maintained as pure data specifications (<code>AgentSpec</code>) rather than bloated, unmaintainable object-oriented classes.</li>
        <li><strong>Hierarchical Context Injection:</strong> Proves that a 3-tier profile model (Global &rarr; Domain &rarr; Agent) reduces prompt token overhead by over 60% compared to monolithic system prompts.</li>
        <li><strong>Empirical Safety in Feedback Learning:</strong> Implements the Two-Strike promotion rule, providing a mathematical safeguard against destructive profile thrashing caused by isolated user mood swings.</li>
        <li><strong>Edge-Ready Computational Efficiency:</strong> Operates entirely on commodity consumer hardware with 0 dedicated GPU VRAM, achieving sub-second token latency and 35ms image rendering.</li>
    </ul>

    <h2 class="chapter-num" style="margin-top: 25px; text-align: left; font-size: 12pt;">1.1 Motivation</h2>
    <p>
        The primary motivation behind this research stems from direct empirical observations of user frustration with commercial AI
        tools across academia and industry. While LLMs exhibit remarkable linguistic dexterity, their practical utility is severely
        hampered when applied to specialized, high-stakes tasks.
    </p>
    <p>
        Specifically, this research is driven by five compounding real-world challenges:
    </p>
    <ol>
        <li><strong>The Cognitive Overhead of Prompt Engineering:</strong> In educational and professional settings, users spend more time crafting defensive prompts (e.g., <em>"Act as an expert Class 10 CBSE Maths teacher, do not skip algebraic steps, use NCERT notation..."</em>) than engaging with the actual subject matter.</li>
        <li><strong>Inconsistent Brand and Pedagogical Tone:</strong> Monolithic models inevitably suffer from tone drift over extended conversations, vacillating between overly verbose academic prose and clipped bullet points.</li>
        <li><strong>Economic and Environmental Inefficiency:</strong> Calling massive 70-billion-parameter cloud models to perform basic query routing or boundary checks wastes substantial energy and financial capital.</li>
    </ol>
    """
    pages.append(build_page(13, p13))

    # =========================================================================
    # PAGE 14: MOTIVATION (CONTINUED)
    # =========================================================================
    p14 = """
    <p style="margin-top: 15px;">
        4. <strong>The Failure of Single-Turn Memory in Conversational Tools:</strong> When an AI system forgets a user's explicit
        corrections—such as a student stating they struggle with trigonometry formulas or a marketer requiring AP-style capitalization—users
        experience acute dissatisfaction. Existing systems either possess no long-term memory or indiscriminately dump all past turns into
        a vector store, resulting in irrelevant context retrieval.
    </p>
    <p>
        5. <strong>The Need for Multi-Modal Content Without Cloud Latency:</strong> In both educational revision and commercial marketing,
        pure textual output is fundamentally insufficient. Students require structured concept summary cards and statistical performance
        charts; marketing professionals require branded social graphics with exact aspect ratios. Forcing users to pivot to external
        generative image models (such as DALL-E or Midjourney) introduces unacceptable latency (10-30 seconds per image), prohibitive API costs,
        and notorious text rendering errors.
    </p>

    <h3 class="section-heading">The Pedagogical and Industrial Mandate</h3>
    <p>
        In modern educational frameworks (e.g., National Education Policy and CBSE curriculum mandates), learning must be personalized to
        the student's exact cognitive pace. A Class 10 student preparing for board examinations requires rigorous adherence to step-marking
        criteria; providing advanced university-level calculus or unverified internet shortcuts actively damages academic outcomes.
    </p>
    <p>
        Similarly, in industrial software engineering and corporate strategy, advice must be bounded by strict architectural constraints.
        A technical refactoring assistant must enforce Clean Code and SOLID principles without drifting into speculative rewrites.
    </p>

    <div class="diagram-pre">
+-------------------------------------------------------------------------+
|                  3-TIER PERSONALIZATION HIERARCHY                        |
+-------------------------------------------------------------------------+
| GLOBAL PROFILE:   Tone (Direct), Verbosity (Concise), Skill (Expert)    |
|       |                                                                 |
|       v                                                                 |
| DOMAIN PROFILE:   CBSE Class 10 Curriculum / SaaS B2B Marketing / API   |
|       |                                                                 |
|       v                                                                 |
| AGENT PROFILE:    Step-by-Step Proofs / 280-Char Twitter Hooks / Schema |
|       |                                                                 |
|       v                                                                 |
| VECTOR MEMORY:    Top-k Episodic Memories (nomic-embed-text 768d)       |
+-------------------------------------------------------------------------+
    </div>
    <div class="caption">Fig. 1.2: Conceptual Model of the 3-Tier Layered Personalization Hierarchy</div>

    <p>
        As illustrated in Fig. 1.2, achieving this level of tailored rigor requires decomposing monolithic intelligence into discrete,
        inheriting layers. This architectural realization formed the central motivation for the proposed research.
    </p>
    """
    pages.append(build_page(14, p14))

    # =========================================================================
    # PAGE 15: ROLE OF AGENTIC WORKFLOWS & 1.2 PROBLEM IDENTIFICATION
    # =========================================================================
    p15 = """
    <h3 class="section-heading" style="margin-top: 15px;">Role of Agentic State Machine Workflows</h3>
    <p>
        During the early conceptualization phase of this project, traditional prompt-chaining libraries (such as raw LangChain sequential
        chains) were evaluated. However, linear chains proved fundamentally incapable of handling real-world conversational dynamics:
    </p>
    <ul>
        <li>They cannot gracefully branch or loop when inputs fail validation.</li>
        <li>They lack unified state inspection, making it impossible to audit which profile attributes shaped a given output.</li>
        <li>They cannot decouple synchronous pre-processing from asynchronous token streaming.</li>
    </ul>
    <p>
        To solve this, the project adopted <strong>LangGraph</strong>—a stateful computational framework that models multi-agent
        interactions as a formal Directed Acyclic Graph (DAG) with cyclical capabilities. In LangGraph, each step of the lifecycle is an
        isolated, independently testable node that communicates exclusively via an immutable, append-safe state dictionary. This ensures
        absolute predictability, sub-millisecond execution overhead, and zero runtime state corruption.
    </p>

    <h2 class="chapter-num" style="margin-top: 25px; text-align: left; font-size: 12pt;">1.2 Problem Identification</h2>
    <p>
        To rigorously establish the functional requirements of the proposed system, an extensive empirical audit of existing commercial
        and open-source conversational AI tools was conducted. The audit revealed five critical structural problems:
    </p>
    <ol>
        <li><strong>Absence of Vertical Domain Specialization:</strong> Generalist models attempt to solve all problems using a single universal prompt, resulting in diluted, generic, and superficial recommendations lacking professional depth.</li>
        <li><strong>Context Window Pollution &amp; Memory Interference:</strong> In long multi-turn sessions, prior instructions regarding unrelated subjects (e.g., Python formatting rules) bleed into subsequent creative or analytical tasks.</li>
        <li><strong>Inability to Enforce Hard Competency Boundaries:</strong> When a user poses an out-of-scope query to an agent (e.g., asking an educational tutor for stock trading advice), existing models fabricate unverified answers rather than redirecting the user.</li>
        <li><strong>Lack of Structured, Long-Term Profile Continuity:</strong> Systems treat each session as an isolated island. While some tools offer basic "custom instructions," these are flat text blocks that cannot scale across diverse domains.</li>
    </ol>
    """
    pages.append(build_page(15, p15))

    # =========================================================================
    # PAGE 16: KEY ISSUES IN EXISTING SYSTEMS
    # =========================================================================
    p16 = """
    <h3 class="section-heading" style="margin-top: 15px;">Detailed Breakdown of Key Systemic Issues</h3>

    <h4 class="subsection-heading">1.1 Generalized &amp; Shallow Outputs</h4>
    <p>
        Because general-purpose LLMs are aligned via Reinforcement Learning from Human Feedback (RLHF) to avoid controversy and provide
        broadly acceptable answers, their default register is inherently bland. In academic contexts, they provide textbook summaries
        without worked pedagogical examples; in marketing, they produce clich&eacute;d slogans lacking conversion psychology.
    </p>
    <p>
        <em>Impact:</em> Users must engage in lengthy iterative prompting cycles to coax the model into producing production-ready content,
        wasting valuable time and computational resources.
    </p>

    <h4 class="subsection-heading">1.2 Prompt Tax &amp; Cognitive Overhead</h4>
    <p>
        Achieving high-quality personalization in existing systems requires the user to prepend every prompt with an exhaustive preamble
        specifying role, tone, formatting, and constraints.
    </p>
    <p>
        <em>Impact:</em> Users experience rapid fatigue, leading them to abandon personalization entirely and settle for substandard
        generic outputs.
    </p>

    <h4 class="subsection-heading">1.3 Cross-Task Context Pollution</h4>
    <p>
        In systems that employ flat conversation histories or global memory stores, stylistic constraints defined for one domain bleed
        into completely unrelated domains. For instance, instructing an AI to be "extremely concise and use bullet points only" for software
        debugging ruins subsequent requests for narrative storytelling.
    </p>
    <p>
        <em>Impact:</em> The user must manually wipe conversation histories or open separate browser sessions, destroying continuity.
    </p>

    <h4 class="subsection-heading">1.4 Unchecked Scope Creep</h4>
    <p>
        Standard LLMs are incentivized to provide an answer to every prompt, even when the query falls entirely outside their defined role.
        An educational tutor asked to write legal contracts will attempt to do so, generating legally invalid, hallucinated text.
    </p>
    <p>
        <em>Impact:</em> Severe risk of misinformation, loss of domain trust, and unpredictable system behavior.
    </p>

    <h4 class="subsection-heading">1.5 Transient Episodic Memory</h4>
    <p>
        When an AI makes a mistake (e.g., using informal vocabulary after being asked for formal academic prose) and the user corrects it,
        the correction is forgotten the moment a new conversation is initiated.
    </p>
    <p>
        <em>Impact:</em> The user is forced to repeatedly issue the same corrections across days and weeks, eliminating the perception of
        an intelligent, evolving partner.
    </p>
    """
    pages.append(build_page(16, p16))

    # =========================================================================
    # PAGE 17: TABLE 1.1 PROBLEM IDENTIFICATION TABLE
    # =========================================================================
    p17 = """
    <h3 class="section-heading" style="margin-top: 15px;">Problem Summary Matrix</h3>
    <p>
        To formalize the correlation between observed industry dysfunctions and the concrete engineering solutions developed in this
        project, the following matrix is established:
    </p>

    <div style="font-weight: bold; margin-bottom: 4px;">Table 1.1: Problem Identification and Proposed Project Response</div>
    <table class="report-table">
        <thead>
            <tr>
                <th style="width: 25%;">Issue Observed</th>
                <th style="width: 35%;">Impact on User Experience</th>
                <th style="width: 40%;">Proposed System Response</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Bland, Generalist Outputs</strong></td>
                <td>Content lacks depth, domain vocabulary, and professional structural rigor.</td>
                <td>Ecosystem of <strong>34 narrow declarative agents</strong> across 7 domains with specialized system prompts.</td>
            </tr>
            <tr>
                <td><strong>Prompt Tax Overhead</strong></td>
                <td>Users must manually re-type preambles, audience skill levels, and formatting rules.</td>
                <td>Automated <strong>3-tier profile inheritance</strong> (Global &rarr; Domain &rarr; Agent) injected at runtime.</td>
            </tr>
            <tr>
                <td><strong>Cross-Task Context Leakage</strong></td>
                <td>Terse coding rules corrupt creative writing or educational pedagogical depth.</td>
                <td>Strict <strong>domain-isolated memory scopes</strong> and distinct agent configuration profiles.</td>
            </tr>
            <tr>
                <td><strong>Unchecked Scope Creep</strong></td>
                <td>Models hallucinate inaccurate advice outside their core competency.</td>
                <td>Deterministic <strong>0.0s Lexical Scope Guard</strong> providing immediate, polite redirection handoffs.</td>
            </tr>
            <tr>
                <td><strong>Transient Memory Loss</strong></td>
                <td>User corrections are discarded upon session close, requiring perpetual repetition.</td>
                <td><strong>Scoped Vector Memory</strong> + <strong>Two-Strike Rule</strong> promoting repeat corrections into permanent profile attributes.</td>
            </tr>
            <tr>
                <td><strong>GPU Bottleneck for Visuals</strong></td>
                <td>Generating charts or cards requires 16GB VRAM GPUs and 15-30s cloud latency.</td>
                <td><strong>Zero-GPU Local Media Engine</strong> using Pillow (35ms PNG cards) and Matplotlib (data-accurate charts).</td>
            </tr>
        </tbody>
    </table>

    <p style="margin-top: 12px;">
        As demonstrated in Table 1.1, each architectural layer of the Content Personalisation Multi-Agent System directly maps to a verified
        failure mode in the current state-of-the-art. By addressing these failure modes at the infrastructure and state-machine level rather
        than through brittle prompt engineering, the proposed platform delivers guaranteed predictability and user satisfaction.
    </p>
    """
    pages.append(build_page(17, p17))

    # =========================================================================
    # PAGE 18: INSIGHTS, PROBLEM STATEMENT & SCOPE
    # =========================================================================
    p18 = """
    <h3 class="section-heading" style="margin-top: 15px;">Insights from Development Phases</h3>
    <p>
        The formulation of the problems and responses outlined in Table 1.1 was not merely theoretical; it was forged through iterative
        empirical development:
    </p>
    <ul>
        <li><strong>Phase 1 (Monolithic Prototype):</strong> Initial attempts using a single prompt with conditional if-else instructions resulted in severe role conflict. The model frequently confused CBSE marking rubrics with marketing copy guidelines.</li>
        <li><strong>Phase 2 (Decoupled Agent Catalog):</strong> Decomposing agents into standalone data records (<code>AgentSpec</code>) immediately eliminated cross-contamination and dramatically improved output quality.</li>
        <li><strong>Phase 3 (StateGraph Refinement):</strong> Transitioning from linear execution chains to LangGraph's 10-step state machine established bounded latency, transparent auditing, and seamless streaming parity.</li>
    </ul>

    <h3 class="section-heading">Formal Problem Statement</h3>
    <div style="background-color: #f8f8f8; border-left: 4px solid #000; padding: 10px 14px; margin: 12px 0; font-style: italic;">
        "There is an absence of an integrated, computationally efficient, and deterministic multi-agent platform capable of delivering
        hyper-specialized, multi-modal content personalization across distinct professional domains while enforcing hard competency
        boundaries, eliminating prompt overhead through multi-tier profile inheritance, and safely assimilating user feedback into
        durable memory without profile corruption."
    </div>

    <h3 class="section-heading">Scope of the Proposed Solution</h3>
    <p>
        To resolve the problem statement within an academically rigorous and commercially deployable framework, the project defines the
        following operational scope:
    </p>
    <ul>
        <li><strong>Multi-Domain Coverage:</strong> Complete coverage of 7 functional domains with 34 declarative agent specifications.</li>
        <li><strong>Automated Routing:</strong> Two-tier intelligent routing combining zero-cost keyword catalogs with two-stage LLM classification.</li>
        <li><strong>Deterministic Boundary Guardrails:</strong> Sub-millisecond lexical affinity checking for immediate scope handoffs.</li>
        <li><strong>Multi-Modal Capabilities:</strong> Automated generation of high-resolution 1200&times;627 typography cards and statistical charts without GPU hardware.</li>
        <li><strong>Safe Continuous Learning:</strong> Scoped semantic vector memory coupled with the Two-Strike promotion threshold.</li>
        <li><strong>Offline Edge Execution:</strong> Complete local-first execution via Ollama and SQLite, with seamless cloud scalability to PostgreSQL and OpenAI.</li>
    </ul>
    """
    pages.append(build_page(18, p18))

    # =========================================================================
    # PAGE 19: CHAPTER 2 - LITERATURE REVIEW
    # =========================================================================
    p19 = """
    <h2 class="chapter-num" style="margin-top: 15px;">CHAPTER-2</h2>
    <h2 class="chapter-title">LITERATURE REVIEW</h2>

    <p>
        The Literature Review provides a comprehensive critical analysis of existing research, academic frameworks, commercial platforms,
        and machine learning architectures relevant to conversational agents, content personalization, vector retrieval, and multi-agent
        orchestration. This review establishes the theoretical grounding of the project and pinpoints the precise research gaps that the
        Content Personalisation Multi-Agent System resolves.
    </p>

    <h2 class="chapter-num" style="margin-top: 25px; text-align: left; font-size: 12pt;">2.1 Related Works</h2>
    <p>
        Research into automated content generation and personalized dialogue systems spans several decades, accelerating dramatically
        following the advent of transformer architectures and foundation Large Language Models. Existing literature can be categorized
        into five primary technological paradigms:
    </p>

    <h3 class="section-heading">1. Monolithic Zero-Shot &amp; Few-Shot LLM Chatbots</h3>
    <p>
        Modern commercial AI platforms—exemplified by OpenAI's ChatGPT (GPT-4), Anthropic's Claude, and Google's Gemini—rely on massive
        transformer models trained on trillions of tokens. Personalization in these platforms is primarily approached through in-context
        prompting, where users supply system instructions or pre-prompts (Brown et al., 2020; OpenAI, 2023).
    </p>
    <p>
        <em>Strengths:</em>
    </p>
    <ul>
        <li>Remarkable broad-domain knowledge and fluent natural language synthesis across diverse topics.</li>
        <li>Zero requirement for explicit task-specific feature engineering or statistical training data.</li>
    </ul>
    <p>
        <em>Critical Limitations:</em>
    </p>
    <ul>
        <li><strong>The "Jack of all Trades, Master of None" Dilemma:</strong> A single model cannot sustain the specialized rigor required for contradictory domains (e.g., strictly conforming to CBSE Class 10 marking schemes while concurrently generating viral TikTok copy).</li>
        <li><strong>Context Window Saturation:</strong> Shoveling comprehensive style guides, user histories, and curriculum syllabi into the context window rapidly exhausts token limits, escalates latency, and triggers the "Lost in the Middle" retrieval failure phenomenon (Liu et al., 2023).</li>
        <li><strong>Hallucinatory Boundary Drift:</strong> Monolithic models fail to reliably detect when a query falls outside their competence, generating speculative advice instead of executing clean domain handoffs.</li>
    </ul>
    """
    pages.append(build_page(19, p19))

    # =========================================================================
    # PAGE 20: RELATED WORKS (CONTINUED)
    # =========================================================================
    p20 = """
    <h3 class="section-heading" style="margin-top: 15px;">2. Parameter-Efficient Fine-Tuning (PEFT &amp; LoRA)</h3>
    <p>
        To instill specialized domain knowledge and custom stylistic registers into foundation models without retraining billions of weights,
        researchers developed Parameter-Efficient Fine-Tuning techniques, most notably Low-Rank Adaptation (LoRA) (Hu et al., 2021). LoRA
        freezes pre-trained model weights and injects trainable rank-decomposition matrices into transformer layers.
    </p>
    <p>
        <em>Strengths:</em>
    </p>
    <ul>
        <li>Achieves deep, persistent stylistic adaptation without altering the underlying base model weights.</li>
        <li>Substantially reduces VRAM overhead compared to full parameter fine-tuning.</li>
    </ul>
    <p>
        <em>Critical Limitations:</em>
    </p>
    <ul>
        <li><strong>Catastrophic Forgetting:</strong> Fine-tuning a model on specialized data frequently degrades its generalized reasoning and syntactic robustness in adjacent domains (Kirkpatrick et al., 2017).</li>
        <li><strong>Inflexibility to Runtime Profile Updates:</strong> Fine-tuning produces static weights. If a user changes their preferred tone from "detailed" to "concise," or updates their grade level from Class 10 to Class 11, the entire adapter must be retrained.</li>
        <li><strong>Prohibitive Multi-Tenant Infrastructure Cost:</strong> Serving separate LoRA adapter weights dynamically for thousands of distinct enterprise users introduces severe GPU memory fragmentation and routing latency.</li>
    </ul>

    <h3 class="section-heading">3. Document Retrieval-Augmented Generation (RAG)</h3>
    <p>
        Retrieval-Augmented Generation (Lewis et al., 2020) combines neural information retrieval with autoregressive generation. In standard
        RAG, external enterprise documents are segmented into chunks, embedded via neural encoders, stored in vector indices (e.g., FAISS,
        pgvector), and retrieved via dense cosine similarity to augment prompt context.
    </p>
    <p>
        <em>Strengths:</em>
    </p>
    <ul>
        <li>Grounds model responses in verifiable, factual external reference texts, drastically reducing factual hallucinations.</li>
        <li>Allows instant knowledge base updates simply by inserting or updating vector database embeddings without retraining.</li>
    </ul>
    <p>
        <em>Critical Limitations:</em>
    </p>
    <ul>
        <li><strong>Document-Centric vs. User-Centric:</strong> Traditional RAG is engineered for querying static documentation, not managing dynamic, evolving user behavioral profiles and pedagogical pacing.</li>
        <li><strong>Unscoped Retrieval Pollution:</strong> In generic vector stores, querying "formula" might retrieve physics formulas from an earlier session when the user is currently working on an Excel spreadsheet in a business session.</li>
    </ul>
    """
    pages.append(build_page(20, p20))

    # =========================================================================
    # PAGE 21: RELATED WORKS (CONTINUED)
    # =========================================================================
    p21 = """
    <h3 class="section-heading" style="margin-top: 15px;">4. Multi-Agent Frameworks (AutoGen, CrewAI, LangChain Chains)</h3>
    <p>
        Recognizing the failure of single-prompt systems, the AI research community introduced multi-agent orchestration frameworks such
        as Microsoft AutoGen (Wu et al., 2023), CrewAI, and LangChain Conversational Chains. These frameworks instantiate multiple persona
        prompts and enable them to interact via conversational message passing.
    </p>
    <p>
        <em>Strengths:</em>
    </p>
    <ul>
        <li>Breaks complex problems into discrete conversational sub-tasks, enabling collaborative problem solving.</li>
        <li>Allows individual agents to leverage specialized external tools and APIs.</li>
    </ul>
    <p>
        <em>Critical Limitations:</em>
    </p>
    <ul>
        <li><strong>Non-Deterministic Looping &amp; High Latency:</strong> Unbounded multi-agent chatter frequently enters infinite conversational loops, exponentially inflating API token costs and resulting in unpredictable execution latency (often exceeding 45 seconds).</li>
        <li><strong>Absence of Deterministic Scope Guards:</strong> Agents rely on conversational LLM prompts to decide whether they should handle a query, incurring expensive model inference costs even for queries that are clearly off-topic.</li>
        <li><strong>Lack of Structured Profile Inheritance:</strong> Persona instructions are hardcoded within individual agent prompts, preventing global user preferences from cascading cleanly across agents.</li>
    </ul>

    <h3 class="section-heading">5. Dynamic State Machine Architectures (LangGraph)</h3>
    <p>
        To eliminate the chaotic non-determinism of open-ended multi-agent loops, modern AI systems engineering has converged toward
        <strong>StateGraph architectures</strong>, formalized by LangGraph. In this paradigm, multi-agent workflows are defined as explicit,
        compiled state transition graphs where execution nodes update an immutable shared state schema.
    </p>
    <p>
        <em>Relevance to Proposed Project:</em>
    </p>
    <p>
        LangGraph serves as the foundational orchestration engine of this project. By structuring chat execution into a formal 10-node
        Directed Acyclic Graph, the platform guarantees:
    </p>
    <ul>
        <li><strong>Deterministic Step Sequencing:</strong> Nodes execute in strict mathematical order, eliminating unpredictable branching.</li>
        <li><strong>Inspectable State Auditing:</strong> Every profile attribute, retrieved memory, and routing score is preserved in the state payload, allowing real-time frontend visualization.</li>
        <li><strong>Sub-Millisecond Node Latency:</strong> Graph transitions incur microsecond overhead in native Python, ensuring that latency is governed strictly by the underlying LLM token generation speed.</li>
    </ul>
    """
    pages.append(build_page(21, p21))

    # =========================================================================
    # PAGE 22: INSIGHTS & TABLE 2.1 LITERATURE REVIEW SUMMARY
    # =========================================================================
    p22 = """
    <h3 class="section-heading" style="margin-top: 15px;">Summary Synthesis of Literature Review</h3>
    <p>
        To crystallize the architectural divergence between existing methodologies and the proposed system, the analytical findings are
        summarized in Table 2.1:
    </p>

    <div style="font-weight: bold; margin-bottom: 4px;">Table 2.1: Summary of Literature Insights and Identified Research Gaps</div>
    <table class="report-table">
        <thead>
            <tr>
                <th style="width: 22%;">Paradigm / Approach</th>
                <th style="width: 25%;">Primary Strength</th>
                <th style="width: 28%;">Critical Bottleneck</th>
                <th style="width: 25%;">Relevance to Proposed Project</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Monolithic LLMs</strong><br>(ChatGPT, Claude)</td>
                <td>Broad general knowledge; fluent zero-shot synthesis.</td>
                <td>Prompt fatigue; context pollution; lack of domain depth.</td>
                <td>Replaced by <strong>34 narrow agents</strong> with dedicated domain boundaries.</td>
            </tr>
            <tr>
                <td><strong>Fine-Tuning</strong><br>(PEFT / LoRA)</td>
                <td>Deep stylistic adaptation baked into weights.</td>
                <td>Catastrophic forgetting; static weights; high retraining costs.</td>
                <td>Replaced by <strong>3-tier dynamic runtime context injection</strong>.</td>
            </tr>
            <tr>
                <td><strong>Standard Document RAG</strong></td>
                <td>Factual grounding; dynamic knowledge insertion.</td>
                <td>Document-focused; unscoped memory leakage across tasks.</td>
                <td>Adapted into <strong>Domain-Scoped Semantic Vector Memory</strong>.</td>
            </tr>
            <tr>
                <td><strong>Unbounded Multi-Agent</strong><br>(AutoGen, CrewAI)</td>
                <td>Collaborative sub-task decomposition.</td>
                <td>Infinite looping; high latency; non-deterministic routing costs.</td>
                <td>Governed by a compiled <strong>10-step LangGraph StateGraph</strong>.</td>
            </tr>
            <tr>
                <td><strong>StateGraph Orchestration</strong><br>(LangGraph)</td>
                <td>Deterministic execution; inspectable state; streaming parity.</td>
                <td>Requires rigorous state schema design and node decoupling.</td>
                <td><strong>Selected as core orchestration engine</strong> for all chat turns.</td>
            </tr>
        </tbody>
    </table>

    <p style="margin-top: 12px;">
        As demonstrated in Table 2.1, no existing single paradigm simultaneously satisfies the requirements of deep domain specialization,
        sub-second deterministic scope enforcement, hierarchical profile inheritance, and multi-modal edge execution. This unmet need
        defines the research gaps addressed by this project.
    </p>
    """
    pages.append(build_page(22, p22))

    # =========================================================================
    # PAGE 23: 2.2 RESEARCH GAPS
    # =========================================================================
    p23 = """
    <h2 class="chapter-num" style="margin-top: 15px; text-align: left; font-size: 12pt;">2.2 Research Gaps</h2>
    <p>
        Following the systematic evaluation of existing conversational AI tools, literature, and multi-agent frameworks, eight critical
        research and engineering gaps were identified:
    </p>

    <h3 class="section-heading">Gap 1: Absence of Hierarchical, Multi-Tier Profile Inheritance</h3>
    <p>
        Existing conversational platforms treat user customization as a single monolithic text block (e.g., ChatGPT's "Custom Instructions").
        There is no mechanism for <strong>hierarchical inheritance</strong> where global traits (e.g., preference for concise, direct language)
        automatically cascade into domain constraints (e.g., CBSE 10th grade syllabus) and agent specifications (e.g., step-by-step algebra
        proofs) without manual copy-pasting.
    </p>
    <p>
        <em>Proposed Solution:</em> The project develops a formal 3-tier data architecture (Global &rarr; Domain &rarr; Agent) with automated
        runtime synthesis.
    </p>

    <h3 class="section-heading">Gap 2: Cross-Task Context Pollution in Continuous Sessions</h3>
    <p>
        Current platforms store conversational context sequentially in flat memory buffers. When a user transitions between disparate tasks
        (e.g., from writing Python backend code to drafting a sensitive HR email), stylistic guidelines and variable names from the technical
        task contaminate the creative task.
    </p>
    <p>
        <em>Proposed Solution:</em> Implements strict domain and agent memory isolation, ensuring that memories captured during technical turns
        are indexed and retrieved exclusively within technical scopes.
    </p>

    <h3 class="section-heading">Gap 3: High Token Waste and Latency in Model-Based Routing</h3>
    <p>
        Existing multi-agent frameworks invoke heavy LLM calls to classify user intent and route queries between agents. Spending 500-1000
        input tokens and 2-3 seconds of latency merely to determine which agent should handle a query is economically and computationally
        unviable for real-time edge applications.
    </p>
    <p>
        <em>Proposed Solution:</em> Constructs a two-tier routing engine prioritizing calibrated lexical keyword scoring, achieving instant
        zero-cost routing for over 85% of standard queries before falling back to a two-stage LLM classifier.
    </p>
    """
    pages.append(build_page(23, p23))

    # =========================================================================
    # PAGE 24: RESEARCH GAPS (CONTINUED)
    # =========================================================================
    p24 = """
    <h3 class="section-heading" style="margin-top: 15px;">Gap 4: Lack of Deterministic Guardrails Against Scope Creep</h3>
    <p>
        Generalist models operate without boundary enforcement: if a user asks a Class 10 Biology tutor to write an enterprise B2B sales
        pitch, the tutor will comply, generating low-quality advice. Relying on the LLM itself to self-police scope is notoriously unreliable
        and still consumes full prompt tokens.
    </p>
    <p>
        <em>Proposed Solution:</em> A deterministic, sub-millisecond <strong>Scope Guard</strong> based on keyword affinity scoring that
        intercepts off-topic queries in 0.00 seconds with $0.00 model cost, providing an instant polite redirect.
    </p>

    <h3 class="section-heading">Gap 5: Fragile and Destructive Feedback Mechanisms (Profile Thrashing)</h3>
    <p>
        Naive adaptive systems that attempt to learn from user feedback suffer from "profile thrashing": if an exhausted user downvotes a
        detailed answer on a Friday afternoon and demands a "one-line summary," the system permanently rewrites their profile to "terse."
        On Monday morning, when the user requires in-depth analysis, the system fails.
    </p>
    <p>
        <em>Proposed Solution:</em> The <strong>Two-Strike Promotion Rule</strong>. A single critique creates an episodic memory candidate;
        only when the exact same stylistic critique is registered two or more times is the user's permanent profile mutated.
    </p>

    <h3 class="section-heading">Gap 6: Heavy GPU Dependencies for Visual and Graphic Content</h3>
    <p>
        Generating visual aids—such as branded social media graphics and data charts—traditionally requires heavy diffusion models
        (e.g., Stable Diffusion) requiring 16GB of dedicated GPU VRAM and 10-30 seconds of processing time, or cloud API fees.
    </p>
    <p>
        <em>Proposed Solution:</em> A <strong>Zero-GPU Multi-Modal Generation Engine</strong> that utilizes Python Pillow (PIL) to compile
        clean, branded 1200&times;627 PNG typography cards in 35ms, and Matplotlib to render verified, accurate data charts on commodity CPUs.
    </p>
    """
    pages.append(build_page(24, p24))

    # =========================================================================
    # PAGE 25: RESEARCH GAPS (CONTINUED)
    # =========================================================================
    p25 = """
    <h3 class="section-heading" style="margin-top: 15px;">Gap 7: Cloud Vendor Lock-In &amp; Data Privacy Concerns</h3>
    <p>
        Most commercial personalization systems are tightly bound to proprietary cloud APIs (e.g., OpenAI, Anthropic), transmitting
        sensitive educational, business, and personal data to third-party servers. Organizations and academic institutions frequently
        require complete data sovereignty and 100% offline operational capability.
    </p>
    <p>
        <em>Proposed Solution:</em> Complete local-first engineering utilizing the open-source Ollama daemon (serving <code>llama3.2:3b</code>
        and <code>nomic-embed-text</code>) with portable SQLite vector storage, maintaining complete privacy without cloud egress.
    </p>

    <h3 class="section-heading">Gap 8: Disconnect Between Statistical Vectors and Structured Profile Attributes</h3>
    <p>
        Current RAG systems rely exclusively on dense vector embeddings, which are probabilistic and non-deterministic. They cannot reliably
        enforce absolute, boolean rules (e.g., "Always use Hindi terms alongside English definitions" or "Never exceed 150 words").
    </p>
    <p>
        <em>Proposed Solution:</em> A unified hybrid context engine that explicitly combines deterministic structured profile attributes
        (guaranteed system instructions) with probabilistic vector memories (episodic context).
    </p>

    <h3 class="section-heading">Summary of Research Gap Synthesis</h3>
    <p>
        The identification of these eight specific gaps directly established the architectural blueprints for the Content Personalisation
        Multi-Agent System. Rather than viewing personalization as a superficial prompting veneer, the project addresses it as a deep
        systems engineering challenge requiring coordinated innovations across state management, data persistence, lexical guardrails,
        and multi-modal rendering.
    </p>
    """
    pages.append(build_page(25, p25))

    # =========================================================================
    # PAGE 26: 2.3 OBJECTIVES
    # =========================================================================
    p26 = """
    <h2 class="chapter-num" style="margin-top: 15px; text-align: left; font-size: 12pt;">2.3 Objectives</h2>
    <p>
        The objectives of the Content Personalisation Multi-Agent System define the functional, algorithmic, and architectural benchmarks
        established to resolve the research gaps identified in Section 2.2.
    </p>

    <h3 class="section-heading">1. Primary Objective</h3>
    <div style="background-color: #f8f8f8; border-left: 4px solid #000; padding: 10px 14px; margin: 12px 0;">
        <strong>To design, engineer, validate, and benchmark a modular, state-machine-orchestrated multi-agent content personalization
        platform capable of delivering hyper-specialized textual, graphical, and analytical outputs across 7 operational domains while
        enforcing deterministic scope boundaries, zero-cost lexical routing, and safe continuous memory adaptation.</strong>
    </div>

    <h3 class="section-heading">2. Specific Technical Objectives</h3>

    <h4 class="subsection-heading">2.1 Declarative 34-Agent Ecosystem Across 7 Domains</h4>
    <ul>
        <li>Architect 34 hyper-specialized agents as pure data specifications (<code>AgentSpec</code>) structured across Education, Marketing, Business, Creative, Research, Technical, and Logistics.</li>
        <li>Eliminate monolithic class hierarchies by implementing only 3 generic runtime execution engines (<code>TextAgent</code>, <code>ImageAgent</code>, <code>ChartAgent</code>).</li>
    </ul>

    <h4 class="subsection-heading">2.2 3-Tier Hierarchical Profile Inheritance Engine</h4>
    <ul>
        <li>Design and implement a relational database schema supporting three inheriting profile tiers:
            <ul>
                <li><strong>Global Profile:</strong> Cross-domain user tone, verbosity, skill level, and primary language.</li>
                <li><strong>Domain Profile:</strong> Curriculum standards (e.g., CBSE Class 10), industry verticals, or brand palettes.</li>
                <li><strong>Agent Profile:</strong> Highly specific stylistic constraints (e.g., step-by-step algebra proofs, 280-char hooks).</li>
            </ul>
        </li>
        <li>Ensure automated runtime context synthesis with zero manual copy-pasting required from the user.</li>
    </ul>
    """
    pages.append(build_page(26, p26))

    # =========================================================================
    # PAGE 27: OBJECTIVES (CONTINUED)
    # =========================================================================
    p27 = """
    <h4 class="subsection-heading" style="margin-top: 15px;">2.3 10-Step LangGraph StateGraph Execution Pipeline</h4>
    <ul>
        <li>Construct a compiled Directed Acyclic Graph (DAG) using LangGraph to govern each conversational turn through 10 discrete, inspectable nodes:
            <code>load_user</code> &rarr; <code>router</code> &rarr; <code>scope_guard</code> &rarr; <code>load_global_profile</code> &rarr;
            <code>load_domain_profile</code> &rarr; <code>load_agent_profile</code> &rarr; <code>retrieve_memory</code> &rarr;
            <code>build_context</code> &rarr; <code>generate_response</code> &rarr; <code>store_message</code>.</li>
        <li>Group the first eight nodes as <code>PREPARE_NODES</code> to enable instantaneous Server-Sent Events (SSE) metadata streaming to the UI before LLM token generation begins.</li>
    </ul>

    <h4 class="subsection-heading">2.4 Deterministic 0.0s Lexical Scope Guard</h4>
    <ul>
        <li>Implement a zero-cost scope evaluation algorithm that compares query token affinity against calibrated agent keyword catalogs.</li>
        <li>Trigger instantaneous (0.00-second latency, $0.00 token cost) polite handoff redirections whenever an out-of-scope query is submitted to an agent.</li>
    </ul>

    <h4 class="subsection-heading">2.5 Domain-Scoped Semantic Vector Memory</h4>
    <ul>
        <li>Integrate local <code>nomic-embed-text</code> neural embeddings (768 dimensions) to capture episodic facts from user messages.</li>
        <li>Enforce strict multi-tenant and domain scoping on cosine similarity vector queries to eliminate cross-session context pollution.</li>
    </ul>

    <h4 class="subsection-heading">2.6 Zero-GPU Multi-Modal Media Generation</h4>
    <ul>
        <li>Develop a CPU-native graphics engine using Python Pillow (PIL) to render crisp 1200&times;627 PNG typography cards in under 35 milliseconds.</li>
        <li>Develop an analytical chart engine using Matplotlib to parse structured LLM series data into verified Bar, Line, and Pie charts without numerical hallucinations.</li>
    </ul>
    """
    pages.append(build_page(27, p27))

    # =========================================================================
    # PAGE 28: OBJECTIVES & EXPECTED OUTCOMES
    # =========================================================================
    p28 = """
    <h4 class="subsection-heading" style="margin-top: 15px;">2.7 Safe Continuous Learning via Two-Strike Feedback Rule</h4>
    <ul>
        <li>Construct a separate, event-driven compiled feedback graph (<code>feedback_graph.py</code>) triggered asynchronously by user ratings.</li>
        <li>Enforce the Two-Strike promotion threshold: candidate feedback is stored as episodic memory on the first strike; permanent profile mutation occurs only upon the second identical critique.</li>
    </ul>

    <h4 class="subsection-heading">2.8 Dual-Dialect Storage &amp; Enterprise Security Governance</h4>
    <ul>
        <li>Support dual database dialects: PostgreSQL 16 with <code>pgvector</code> for high-concurrency production deployments, and SQLite for 100% offline edge execution.</li>
        <li>Implement enterprise-grade security: bcrypt password hashing, PyJWT authentication, strict SQLAlchemy ORM query parameterization, and zero known frontend vulnerabilities.</li>
    </ul>

    <h3 class="section-heading">Phased Development Milestones</h3>
    <ol>
        <li><strong>Phase 1: Architecture &amp; Data Specifications:</strong> Domain taxonomy formulation, 34 <code>AgentSpec</code> definitions, and database schema migrations.</li>
        <li><strong>Phase 2: Core Engine &amp; Graph Compilation:</strong> LangGraph 10-step StateGraph assembly, Scope Guard calibration, and vector memory integration.</li>
        <li><strong>Phase 3: Multi-Modal Engines &amp; UI Integration:</strong> Pillow card renderer, Matplotlib chart generator, React 18 frontend with SSE streaming, and rigorous benchmark verification.</li>
    </ol>

    <h3 class="section-heading">Expected Outcomes</h3>
    <p>
        Successful realization of these objectives produces a fully operational, offline-capable multi-agent platform capable of sub-second
        token streaming, zero-cost boundary enforcement, and permanent, safe personalization across educational and enterprise domains.
    </p>
    """
    pages.append(build_page(28, p28))

    # =========================================================================
    # PAGE 29: CHAPTER 3 - DESIGN & METHODOLOGY
    # =========================================================================
    p29 = """
    <h2 class="chapter-num" style="margin-top: 15px;">CHAPTER-3</h2>
    <h2 class="chapter-title">DESIGN AND METHODOLOGY</h2>

    <p>
        This chapter details the comprehensive system design, architectural framework, algorithmic methodologies, and component
        interactions that govern the Content Personalisation Multi-Agent System. The system is engineered using a modular, layered
        architecture that completely decouples user interface rendering, API gateway routing, state-machine orchestration, vector memory
        indexing, and multi-modal rendering.
    </p>

    <h2 class="chapter-num" style="margin-top: 25px; text-align: left; font-size: 12pt;">3.1 Working Principle</h2>
    <p>
        The working principle of the platform is rooted in a <strong>deterministic, profile-driven stategraph lifecycle</strong>. Rather
        than passing user queries directly to an LLM completion endpoint, every transaction is treated as an evolving state object that
        progresses through discrete computational stages:
    </p>

    <div class="diagram-pre">
[User Query + Selected Agent]
            |
            v
1. API Ingestion &amp; Session Validation (FastAPI, JWT Authentication)
            |
            v
2. Two-Tier Agent Routing (Explicit Choice &gt; Keyword Catalogs &gt; Two-Stage LLM)
            |
            v
3. Lexical Scope Guard Verification (0.0s Affinity Scoring &amp; Handoff Check)
            |
            v
4. Context &amp; Memory Synthesis (3-Tier Profile Hierarchy + 768d Vector Memory)
            |
            v
5. Specialized Generation (LLM Text Inference / Pillow 1200x627 / Matplotlib Charts)
            |
            v
6. Persistence &amp; Memory Capture (DB Commit, Vector Embedding Indexing, SSE Stream)
    </div>
    <div class="caption">Fig. 3.1: Conceptual End-to-End Operational Lifecycle of the System</div>

    <p>
        As shown in Fig. 3.1, this sequential operational pipeline ensures that every response is tightly bound to verified user profiles,
        grounded in episodic vector memories, and protected against out-of-scope hallucinations before generation begins.
    </p>
    """
    pages.append(build_page(29, p29))

    # =========================================================================
    # PAGE 30: KEY FEATURES OF WORKING PRINCIPLE
    # =========================================================================
    p30 = """
    <h3 class="section-heading" style="margin-top: 15px;">Key Features of the Working Principle</h3>

    <h4 class="subsection-heading">1. Hierarchical Context Layering (3-Tier Inheritance)</h4>
    <p>
        When a request is processed, the system retrieves user attributes in strict order of increasing specificity:
    </p>
    <ul>
        <li><strong>Tier 1 (Global Profile):</strong> Injects universal stylistic constraints: length (concise &lt;180 words, balanced 200-350 words, detailed 450-700 words), tone (direct, professional, friendly, casual, academic), and skill level.</li>
        <li><strong>Tier 2 (Domain Profile):</strong> Injects curriculum standards (CBSE syllabus guidelines), industry verticals (B2B SaaS, HealthTech), or brand identity constraints (color palettes, taglines).</li>
        <li><strong>Tier 3 (Agent Profile):</strong> Injects narrow task rules (e.g., NCERT step-marking notation, Python PEP-8 rules).</li>
    </ul>

    <h4 class="subsection-heading">2. Zero-Cost Deterministic Scope Enforcement</h4>
    <p>
        The Scope Guard assesses lexical affinity using keyword token matching. If the score of the selected agent is low
        (<code>own_score &le; 1.0</code>) and an alternative agent demonstrates decisive affinity (<code>other_score &ge; 4.0</code>, margin &ge; 3.0),
        the system terminates generation immediately, returning an instant, polite redirect with $0.00 inference cost.
    </p>

    <h4 class="subsection-heading">3. Scoped Semantic Vector Memory Retrieval</h4>
    <p>
        Past user statements and corrections are converted into 768-dimensional embeddings via <code>nomic-embed-text</code>. Queries are
        filtered strictly by <code>user_id</code> and <code>domain</code>, ensuring that technical programming notes never contaminate
        creative writing sessions.
    </p>

    <h4 class="subsection-heading">4. Declarative Runtime Execution</h4>
    <p>
        All 34 agents operate through three unified runtime executors: <code>TextAgent</code> (direct text synthesis), <code>ImageAgent</code>
        (structured JSON layout &rarr; Pillow PNG card), and <code>ChartAgent</code> (structured series JSON &rarr; Matplotlib figure).
    </p>

    <h4 class="subsection-heading">5. The Two-Strike Feedback Adaptation</h4>
    <p>
        User ratings and critiques submitted through thumbs-down or text feedback are processed by a dedicated compiled graph
        (<code>feedback_graph.py</code>). A single critique is stored as an episodic candidate; repeat critiques promote the preference into
        permanent profile attributes.
    </p>
    """
    pages.append(build_page(30, p30))

    # =========================================================================
    # PAGE 31: 10-STEP LANGGRAPH PIPELINE & 3.1.1 ARCHITECTURE
    # =========================================================================
    p31 = """
    <h3 class="section-heading" style="margin-top: 15px;">The 10-Step LangGraph StateGraph Execution Pipeline</h3>
    <p>
        The core engine of each conversational turn is formalized as a LangGraph StateGraph. The graph defines an immutable state
        channel (<code>ChatState</code>) that transitions sequentially through 10 dedicated nodes:
    </p>

    <div class="diagram-pre">
START --> [1. load_user]             (Validate active user &amp; session timestamp)
               |
               v
          [2. router]                (Explicit pick > Keywords > Two-stage LLM)
               |
               v
          [3. scope_guard]           (Deterministic 0.0s boundary &amp; handoff check)
               |
               v
          [4. load_global_profile]   (Retrieve user tone, verbosity, skill)
               |
               v
          [5. load_domain_profile]   (Load CBSE / SaaS / Industry constraints)
               |
               v
          [6. load_agent_profile]    (Load narrow formatting and output rules)
               |
               v
          [7. retrieve_memory]       (Dense vector search via nomic-embed-text)
               |
               v
          [8. build_context]         (Synthesize layered context message block)
               |
               v
          [9. generate_response]     (Execute LLM or Pillow/Matplotlib renderers)
               |
               v
          [10. store_message]        (Persist turn, capture memory, commit DB)
               |
               v
              END
    </div>
    <div class="caption">Fig. 3.2: 10-Step LangGraph StateGraph Execution Flow (graph.py)</div>

    <h2 class="chapter-num" style="margin-top: 20px; text-align: left; font-size: 12pt;">3.1.1 Block Diagram / System Architecture</h2>
    <p>
        The system architecture follows a clean, three-tier separation of concerns:
    </p>
    <ul>
        <li><strong>Presentation Layer:</strong> React 18 Single-Page Application (SPA) built with Vite and Tailwind CSS.</li>
        <li><strong>Application &amp; Orchestration Layer:</strong> FastAPI asynchronous backend hosting the compiled LangGraph state machines.</li>
        <li><strong>Data &amp; Intelligence Layer:</strong> Dual-dialect persistence (SQLite/PostgreSQL), local Ollama inference, and CPU media engines.</li>
    </ul>
    """
    pages.append(build_page(31, p31))

    # =========================================================================
    # PAGE 32: SYSTEM ARCHITECTURE BLOCK DIAGRAM
    # =========================================================================
    p32 = """
    <h3 class="section-heading" style="margin-top: 15px;">High-Level System Architecture Block Diagram</h3>

    <div class="diagram-pre">
+-------------------------------------------------------------------------+
|                        PRESENTATION LAYER                               |
|  React 18 SPA (Vite 8) | Tailwind CSS Obsidian | Lucide Icons | Axios    |
|  - Real-Time Chat &amp; SSE Stream Consumer  - 3-Tier Profile Management Form |
|  - 34-Agent Domain Sidebar Explorer     - Interactive Media / Chart Box |
+-------------------------------------------------------------------------+
                                    |
                                    | REST APIs &amp; SSE Token Streaming
                                    v
+-------------------------------------------------------------------------+
|                  APPLICATION &amp; ORCHESTRATION LAYER                      |
|  FastAPI (Python 3.12+) | Pydantic v2 | PyJWT Auth | SQLAlchemy 2       |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  | LangGraph StateGraph Orchestration Engine (graph.py)              |  |
|  | [load_user] -> [router] -> [scope_guard] -> [load_profiles] ->    |  |
|  | [retrieve_memory] -> [build_context] -> [generate] -> [store]     |  |
|  +-------------------------------------------------------------------+  |
|                                                                         |
|  - Router Engine (Keyword Scoring + Two-Stage Domain/Agent Classifier)  |
|  - Deterministic Scope Guard (0.0s Lexical Scoring &amp; Handoff Engine)    |
|  - Personalization Context Synthesizer (Tier 1 -> Tier 2 -> Tier 3)     |
|  - Feedback Graph (feedback_graph.py with Two-Strike Promotion Rule)    |
+-------------------------------------------------------------------------+
                                    |
                                    | Async SQL &amp; Vector Embeddings
                                    v
+-------------------------------------------------------------------------+
|                     DATA &amp; INTELLIGENCE LAYER                           |
|  Local AI Engine:        Ollama Daemon (llama3.2:3b local LLM)          |
|  Neural Embeddings:      nomic-embed-text (768-dimensional vector space)|
|  Dual-Dialect Database:  PostgreSQL 16 + pgvector OR Portable SQLite    |
|  Zero-GPU Media Engine:  Pillow Card Renderer (1200x627 PNG in 35ms)   |
|                          Matplotlib Chart Renderer (Accurate Plotting)  |
+-------------------------------------------------------------------------+
    </div>
    <div class="caption">Fig. 3.3: High-Level System Architecture and Layered Block Diagram</div>

    <h3 class="section-heading">Description of Presentation Layer</h3>
    <p>
        The Presentation Layer delivers a modern, accessible user interface optimized for rapid navigation across all 34 agents. It features
        persistent session switching, interactive profile configuration modals, real-time token streaming via Server-Sent Events, and inline
        rendering of generated typography cards and analytical charts.
    </p>
    """
    pages.append(build_page(32, p32))

    # =========================================================================
    # PAGE 33: APPLICATION & DATA / AI LAYERS
    # =========================================================================
    p33 = """
    <h3 class="section-heading" style="margin-top: 15px;">Description of Application &amp; Orchestration Layer</h3>
    <p>
        The Application Layer serves as the operational bridge between user interactions and computational intelligence:
    </p>
    <ul>
        <li><strong>API Gateway &amp; Validation:</strong> Built on FastAPI, all incoming requests are validated against strict Pydantic v2 schemas. Authentication is enforced via salted bcrypt password hashing and PyJWT bearer tokens.</li>
        <li><strong>The 10-Step LangGraph Orchestrator:</strong> Executes each conversational turn through compiled DAG nodes. Nodes 1 through 8 (<code>PREPARE_NODES</code>) execute synchronously, enabling the backend to stream routing metadata and profile snapshots to the client before the first token is generated.</li>
        <li><strong>Two-Tier Router:</strong> Combines zero-cost keyword catalogs (exact and fuzzy token matching) with a two-stage LLM classification fallback (Domain first &rarr; Agent inside domain).</li>
        <li><strong>Deterministic Scope Guard:</strong> Enforces boundary compliance via lexical scoring without burning LLM inference tokens.</li>
        <li><strong>Continuous Feedback Loop:</strong> Orchestrated via <code>feedback_graph.py</code>, enforcing the Two-Strike promotion threshold to protect profile integrity.</li>
    </ul>

    <h3 class="section-heading">Description of Data &amp; Intelligence Layer</h3>
    <p>
        The Data and Intelligence Layer guarantees robust persistence, privacy, and computational autonomy:
    </p>
    <ul>
        <li><strong>Dual-Dialect Storage:</strong> Implements a unified SQLAlchemy 2 ORM schema capable of executing on PostgreSQL 16 (utilizing <code>pgvector</code> cosine distance indexing) for cloud deployments, or standalone SQLite with a portable Python vector store for 100% offline edge execution.</li>
        <li><strong>Local AI Engine:</strong> Connects to an Ollama daemon running <code>llama3.2:3b</code> for natural language generation and <code>nomic-embed-text</code> (768-dim) for semantic retrieval.</li>
        <li><strong>CPU Media Renderers:</strong>
            <ul>
                <li><em>Pillow (PIL):</em> Parses structured JSON layout coordinates to render 1200&times;627 branded social PNG cards in ~35ms with zero GPU VRAM.</li>
                <li><em>Matplotlib:</em> Parses numerical series JSON to compile publication-grade Bar, Line, and Pie charts, with strict validation ensuring that data points represent user data rather than fabricated values.</li>
            </ul>
        </li>
    </ul>
    """
    pages.append(build_page(33, p33))

    # =========================================================================
    # PAGE 34: COMPONENT INTERACTION & DESIGN PRINCIPLES
    # =========================================================================
    p34 = """
    <h3 class="section-heading" style="margin-top: 15px;">Interaction Between System Components</h3>
    <p>
        During a live conversational turn, components interact through a synchronized transaction lifecycle:
    </p>
    <ol>
        <li><strong>Ingestion:</strong> React frontend transmits user query, active session ID, and optional agent override via an HTTP POST request.</li>
        <li><strong>State Initialization:</strong> FastAPI initializes the <code>ChatState</code> typed container, loading authenticated user identity and database session.</li>
        <li><strong>Routing &amp; Boundary Check:</strong> The Router determines the target agent; the Scope Guard verifies lexical affinity. If out-of-scope, a polite redirect is returned immediately, bypassing LLM generation.</li>
        <li><strong>Context Synthesis:</strong> Personalization engine queries relational profiles (Global &rarr; Domain &rarr; Agent) and vector memory, synthesizing the unified prompt block.</li>
        <li><strong>Generation &amp; Streaming:</strong> The runtime invokes local Ollama or media engines. Text tokens stream via SSE; media files are persisted to disk.</li>
        <li><strong>Persistence:</strong> The turn is committed to the database, new memories are extracted, and interaction counters are updated.</li>
    </ol>

    <h3 class="section-heading">Architectural Design Principles</h3>

    <h4 class="subsection-heading">4.1 Modularity &amp; Declarative Separation</h4>
    <p>
        Agents are defined as pure data specifications (<code>AgentSpec</code>) rather than bloated classes. Adding a 35th agent requires
        only a declarative dictionary entry; the three core runtime engines handle all execution seamlessly.
    </p>

    <h4 class="subsection-heading">4.2 Scalability &amp; Extensibility</h4>
    <p>
        The dual-database architecture allows frictionless migration from a local SQLite prototype to a multi-node PostgreSQL cluster.
        LangGraph's modular DAG structure allows new nodes (e.g., automated fact-checking) to be inserted without modifying existing nodes.
    </p>

    <h4 class="subsection-heading">4.3 Deterministic Boundary Control</h4>
    <p>
        By substituting probabilistic model calls with deterministic lexical scoring in the Scope Guard, the system guarantees 0.00-second
        handoff latency, $0.00 token cost, and absolute immunity against cross-domain hallucinations.
    </p>

    <h4 class="subsection-heading">4.4 Zero-Vulnerability Security Governance</h4>
    <p>
        Complete parameterization via SQLAlchemy 2 eliminates SQL injection; Pydantic v2 enforces schema validation; and tenant-scoped queries
        guarantee zero cross-tenant vector leakage.
    </p>
    """
    pages.append(build_page(34, p34))

    # Join and close
    return get_html_head() + "\n".join(pages) + "\n</body>\n</html>"


def main():
    print("=" * 70)
    print("GENERATING 34-PAGE ACADEMIC PROJECT REPORT (PAGES 1 TO 34)")
    print("=" * 70)

    html_content = generate_all_pages()
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Wrote full report HTML: {OUTPUT_HTML} ({len(html_content):,} bytes)")

    cmd = [
        "/usr/bin/google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={OUTPUT_PDF}",
        "--print-to-pdf-no-header",
        str(OUTPUT_HTML),
    ]

    print(f"Executing Google Chrome headless PDF compilation...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ERROR] Chrome PDF conversion failed: {res.stderr}")
        return

    print(f"[SUCCESS] Generated PDF: {OUTPUT_PDF}")

    # Verify with pdfinfo
    chk = subprocess.run(["pdfinfo", str(OUTPUT_PDF)], capture_output=True, text=True)
    for line in chk.stdout.splitlines():
        if "Pages:" in line or "File size:" in line:
            print(f"  -> {line}")


if __name__ == "__main__":
    main()

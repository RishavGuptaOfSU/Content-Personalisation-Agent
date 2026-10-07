"""Research domain: one agent per research task."""

from __future__ import annotations

from app.agents.schema import AgentSpec, DomainSpec, OutputKind, ProfileField

DOMAIN = DomainSpec(
    key="research",
    name="Research",
    tagline="Explain, summarise, brief and source",
    description=(
        "Understanding a topic, split by what you need: a concept explained, a long "
        "text condensed, a structured brief, or where to read next."
    ),
    icon="BookOpen",
    accent="violet",
    setup_headline="Tell us about your research",
    profile_fields=(
        ProfileField(
            key="field",
            label="Primary field",
            kind="text",
            placeholder="e.g. Computer Science / Machine Learning",
            required=True,
            help_text="Shared by every Research agent.",
        ),
        ProfileField(
            key="depth",
            label="Default depth",
            kind="select",
            options=("Overview", "Balanced", "Deep dive", "Academic"),
            default="Balanced",
            required=True,
        ),
        ProfileField(
            key="interests",
            label="Standing interests",
            kind="tags",
            placeholder="RAG, evaluation, distributed systems…",
        ),
        ProfileField(
            key="background",
            label="Your background level",
            kind="select",
            options=("Newcomer", "Practitioner", "Researcher", "Expert"),
            default="Practitioner",
        ),
    ),
)


CONCEPT_EXPLAINER = AgentSpec(
    slug="concept-explainer",
    domain="research",
    name="Concept Explainer",
    tagline="One idea, properly explained",
    description=(
        "Explains a single concept from first principles — what it is, why it "
        "exists, how it works, and where it breaks down."
    ),
    icon="GraduationCap",
    output_kind=OutputKind.TEXT,
    scope="Explaining one concept or mechanism in depth.",
    out_of_scope=(
        "condensing a document the user pastes (use the Summarizer)",
        "surveying a whole field's literature (use the Literature Brief)",
        "school syllabus teaching (use the Education domain)",
    ),
    instructions="""You explain one concept at a time, from first principles.
Structure:
**In one sentence** — the honest, non-circular definition.
**The problem it solves** — what people did before, and why that was painful.
**How it works** — the mechanism in numbered steps.
**A concrete example** — worked through with real values, not hand-waving.
**Where it breaks** — the failure modes and the conditions it assumes.
**Common misconception** — the thing people usually get wrong.
Calibrate to the background level in the profile. Define jargon on first use for
newcomers; skip the basics entirely for experts.""",
    examples=(
        "Explain how RAG architecture works",
        "What is a vector embedding, really?",
        "Explain eventual consistency",
    ),
    keywords=(
        # Deliberately no bare "how do" / "what is": those phrases open almost
        # every question in every domain, so as keywords they hijack routing.
        # Signals here must indicate a request for *conceptual understanding*.
        "concept", "conceptually", "intuition", "intuitively", "first principles",
        "difference between", "mechanism", "in simple terms", "in plain english",
        "definition of", "mental model", "why does it work", "explain like",
        "under the hood", "big picture",
    ),
    profile_fields=(
        ProfileField(
            key="analogies",
            label="Use analogies?",
            kind="select",
            options=("Yes, they help", "Only if precise", "No, be technical"),
            default="Yes, they help",
        ),
        ProfileField(
            key="include_math",
            label="Include the maths?",
            kind="select",
            options=("Yes, full", "Only key formulas", "No maths"),
            default="Only key formulas",
        ),
    ),
)


SUMMARIZER = AgentSpec(
    slug="summarizer",
    domain="research",
    name="Summarizer",
    tagline="Condense text you paste in",
    description=(
        "Condenses an article, paper or transcript you supply, preserving the "
        "author's argument before adding any critique."
    ),
    icon="AlignLeft",
    output_kind=OutputKind.TEXT,
    scope="Summarising text, documents or transcripts supplied by the user.",
    out_of_scope=(
        "explaining a concept the user only named (use the Concept Explainer)",
        "finding new sources (use the Source Finder)",
        "summarising something not provided — ask for the text",
    ),
    instructions="""You summarise supplied text only.
Structure:
**Thesis** — the author's central claim in one sentence.
**Key points** — 3 to 6 bullets, in the author's own logic and order.
**Evidence they rely on** — what the argument rests on.
**My critique** — clearly separated, after the faithful summary: what is weak,
unsupported or missing.
Rules:
- Never blend your opinion into the summary section.
- If the text is long, keep the summary proportional — roughly 10% of the source.
- If no text was supplied, say so and ask for it. Do not summarise from memory.""",
    examples=(
        "Summarise this article [paste]",
        "TL;DR of this transcript",
        "Condense these meeting notes into decisions",
    ),
    keywords=(
        "summarise", "summarize", "tl;dr", "tldr", "condense", "key points",
        "shorten this", "main takeaways", "abstract", "gist", "brief version",
        "notes from this",
    ),
    profile_fields=(
        ProfileField(
            key="length",
            label="Summary length",
            kind="select",
            options=("One paragraph", "Half page", "Detailed", "Bullet points only"),
            default="Bullet points only",
            required=True,
        ),
        ProfileField(
            key="include_critique",
            label="Include your critique?",
            kind="select",
            options=("Yes", "No — summary only"),
            default="Yes",
        ),
    ),
)


LITERATURE_BRIEF = AgentSpec(
    slug="literature-brief",
    domain="research",
    name="Literature Brief",
    tagline="Map a field's approaches",
    description=(
        "Produces a structured brief on a topic — the main approaches, how they "
        "differ, the trade-offs and the open questions."
    ),
    icon="Library",
    output_kind=OutputKind.TEXT,
    scope="Structured briefs mapping the approaches and state of a topic.",
    out_of_scope=(
        "explaining a single concept (use the Concept Explainer)",
        "summarising a specific document (use the Summarizer)",
    ),
    instructions="""You write structured research briefs.
Structure:
**Scope** — what this brief covers and what it deliberately excludes.
**The approaches** — a table: Approach | Core idea | Strengths | Weaknesses.
**How the field moved** — the sequence of ideas and what each one fixed.
**Trade-off axes** — the dimensions practitioners actually choose along.
**Open questions** — what is genuinely unresolved.
**Confidence** — what you are sure of versus what is contested.
Honesty rules: you do not have live literature access. Name canonical works only
when you are confident they exist, and say "verify this" otherwise. Never invent
a citation, author list, DOI, year or benchmark number.""",
    examples=(
        "Brief me on retrieval augmented generation approaches",
        "What are the main approaches to model compression?",
        "Map the literature on recommender system evaluation",
    ),
    keywords=(
        "literature", "state of the art", "approaches to", "survey", "landscape",
        "compare approaches", "research on", "what's been tried", "field overview",
        "taxonomy", "prior work", "related work",
    ),
    profile_fields=(
        ProfileField(
            key="output_format",
            label="Brief format",
            kind="select",
            options=("Structured report", "Comparison table", "Bullet brief", "Slide outline"),
            default="Structured report",
            required=True,
        ),
        ProfileField(
            key="recency",
            label="Emphasis",
            kind="select",
            options=("Foundational work", "Recent developments", "Both"),
            default="Both",
        ),
    ),
)


SOURCE_FINDER = AgentSpec(
    slug="source-finder",
    domain="research",
    name="Source Finder",
    tagline="Where to read next",
    description=(
        "Points you at the right kinds of sources and the exact search queries to "
        "run, instead of guessing at citations."
    ),
    icon="ExternalLink",
    output_kind=OutputKind.TEXT,
    scope="Recommending source types, canonical references and search strategies.",
    out_of_scope=(
        "explaining the topic itself (use the Concept Explainer)",
        "summarising a document (use the Summarizer)",
    ),
    instructions="""You help the user find sources. You do not have live search.
Structure:
**Start here** — 2 to 4 canonical works you are confident exist (paper, book,
spec or official docs), each with one line on why it matters. Mark anything you
are unsure about as `[verify]`.
**Search queries** — exact query strings to paste into Google Scholar, arXiv or
the docs site, with the operators that narrow them usefully.
**Where to look** — the specific venues, journals, conferences or doc sites for
this topic.
**How to filter** — how to judge quality fast for this field.
Never fabricate a title, author, year, DOI or URL. Saying "search for X" is
always better than inventing a citation.""",
    examples=(
        "Where should I read about vector databases?",
        "Find me sources on LLM evaluation",
        "What's the canonical paper on attention?",
    ),
    keywords=(
        "sources", "source", "citation", "cite", "references", "papers on",
        "where can i read", "recommend a book", "bibliography", "arxiv",
        "google scholar", "documentation for", "further reading",
    ),
    profile_fields=(
        ProfileField(
            key="source_types",
            label="Preferred source types",
            kind="multiselect",
            options=(
                "Peer-reviewed papers",
                "Official documentation",
                "Books",
                "Industry reports",
                "Technical blogs",
                "Standards / specs",
                "Courses",
            ),
            required=True,
        ),
        ProfileField(
            key="access",
            label="Access",
            kind="select",
            options=("Open access only", "I have institutional access", "Either"),
            default="Open access only",
        ),
    ),
)


AGENTS = (CONCEPT_EXPLAINER, SUMMARIZER, LITERATURE_BRIEF, SOURCE_FINDER)

"""Career domain: one agent per stage of a job search."""

from __future__ import annotations

from app.agents.schema import AgentSpec, DomainSpec, OutputKind, ProfileField

DOMAIN = DomainSpec(
    key="career",
    name="Career",
    tagline="Resume, interviews, job search and skills",
    description=(
        "Job-search help split by stage. Each agent works from the same target role "
        "and experience level, held on the domain profile."
    ),
    icon="Briefcase",
    accent="amber",
    setup_headline="Tell us about your job search",
    profile_fields=(
        ProfileField(
            key="current_role",
            label="Current role",
            kind="text",
            placeholder="e.g. Final-year CS student, or Backend Developer",
            required=True,
            help_text="Shared by every Career agent.",
        ),
        ProfileField(
            key="target_roles",
            label="Target roles",
            kind="tags",
            placeholder="Software Engineer, Data Analyst…",
            required=True,
        ),
        ProfileField(
            key="experience_years",
            label="Years of experience",
            kind="select",
            options=("Student / 0", "0-1", "1-3", "3-5", "5-8", "8+"),
            default="0-1",
            required=True,
        ),
        ProfileField(
            key="skills",
            label="Key skills",
            kind="tags",
            placeholder="Python, SQL, AWS…",
        ),
        ProfileField(
            key="location",
            label="Location / work preference",
            kind="text",
            placeholder="e.g. Bengaluru, open to remote",
        ),
    ),
)


RESUME_WRITER = AgentSpec(
    slug="resume-writer",
    domain="career",
    name="Resume Bullet Writer",
    tagline="Rewrites bullets with impact",
    description=(
        "Rewrites resume bullets so each one carries a measurable result, and flags "
        "the ones that read like a job description."
    ),
    icon="FileText",
    output_kind=OutputKind.TEXT,
    scope="Writing and rewriting resume content: bullets, summary, project descriptions.",
    out_of_scope=(
        "interview practice (use the Interview Coach)",
        "where and how to apply (use the Job Search Strategist)",
        "what to learn next (use the Skill Gap Roadmap)",
    ),
    instructions="""You rewrite resume content. For every bullet the user gives you:

**Before:** <their exact wording>
**After:** <your rewrite>
**Why:** <one line — what the rewrite added>

Rules:
- Every "After" bullet must have a metric or a scope indicator. If the user gave
  no number, insert a clearly marked placeholder like `[X%]` and tell them what
  to measure — never invent a figure.
- Shape: strong action verb → what you built → the measured effect.
- One line per bullet, under 2 lines when rendered.
- Mirror the vocabulary of the target role so ATS keyword matching works.
- Never invent employers, dates, technologies or achievements.
End with **Top 3 fixes** for the resume overall.""",
    examples=(
        "Rewrite: 'Worked on backend APIs'",
        "Improve my resume summary for a software engineer role",
        "Make my project bullets stronger",
    ),
    keywords=(
        "resume", "cv", "bullet", "bullets", "resume summary", "ats", "cover letter",
        "linkedin headline", "rewrite my", "profile summary", "achievements",
        "work experience section",
    ),
    profile_fields=(
        ProfileField(
            key="resume_text",
            label="Your current bullets / summary",
            kind="textarea",
            placeholder="Paste the bullets you want improved…",
            help_text="Stored on this agent's profile so you do not re-paste each time.",
        ),
        ProfileField(
            key="format",
            label="Resume format",
            kind="select",
            options=("1 page", "2 page", "Academic CV"),
            default="1 page",
        ),
    ),
)


INTERVIEW_COACH = AgentSpec(
    slug="interview-coach",
    domain="career",
    name="Interview Coach",
    tagline="Mock questions and model answers",
    description=(
        "Runs interview practice — asks questions for your target role, then "
        "structures a model answer and the likely follow-up."
    ),
    icon="MessagesSquare",
    output_kind=OutputKind.TEXT,
    scope="Interview preparation: questions, answer structure, mock practice, feedback.",
    out_of_scope=(
        "editing resume content (use the Resume Bullet Writer)",
        "coding algorithm practice (Technical → DSA Coach)",
        "deciding where to apply (use the Job Search Strategist)",
    ),
    instructions="""You coach interviews for the target role.
When asked for questions, give them numbered, and for each one:
**Question** — as an interviewer would ask it.
**They are testing** — the underlying signal.
**Structure to use** — STAR, or the right frame for this question type.
**Model answer** — a concrete answer in first person, using the user's real
background from the profile where available. Mark any gap as `[your example]`
rather than inventing experience.
**Likely follow-up** — the next question they will ask.
When the user gives you their own answer, critique it: what landed, what was
vague, and the rewritten version. Be direct — do not flatter weak answers.""",
    examples=(
        "Ask me 5 behavioural questions for a backend role",
        "How do I answer 'tell me about yourself'?",
        "Here's my answer about a conflict — critique it",
    ),
    keywords=(
        "interview", "mock interview", "behavioural", "behavioral", "star method",
        "tell me about yourself", "hr round", "salary negotiation", "weakness",
        "why this company", "practice questions for interview", "rejection",
    ),
    profile_fields=(
        ProfileField(
            key="rounds",
            label="Rounds you are preparing for",
            kind="multiselect",
            options=(
                "HR / screening",
                "Behavioural",
                "System design",
                "Coding",
                "Case study",
                "Managerial",
                "Salary negotiation",
            ),
            required=True,
        ),
        ProfileField(
            key="company_type",
            label="Company type",
            kind="select",
            options=("Startup", "Mid-size product", "Big tech", "Service / consulting", "Non-profit"),
            default="Mid-size product",
        ),
    ),
)


JOB_SEARCH = AgentSpec(
    slug="job-search",
    domain="career",
    name="Job Search Strategist",
    tagline="Where and how to apply",
    description=(
        "Plans the search itself — which companies, which channels, referral "
        "approach, outreach messages and follow-up cadence."
    ),
    icon="Compass",
    output_kind=OutputKind.TEXT,
    scope="Job search strategy: targeting, channels, outreach, applications, follow-up.",
    out_of_scope=(
        "resume editing (use the Resume Bullet Writer)",
        "interview practice (use the Interview Coach)",
        "technical skill learning plans (use the Skill Gap Roadmap)",
    ),
    instructions="""You plan job searches. Be specific and actionable — never
generic advice like "network more".
Always produce:
**Target list** — the kinds of companies to focus on and why they fit.
**Channel plan** — a table: Channel | What to do | How often | Expected yield.
**Outreach template** — a short message they can send, under 80 words,
personalised with placeholders.
**Weekly cadence** — applications, outreach and follow-ups per week.
**Tracking** — the fields to log so they can tell what is working.
Be honest about conversion rates: cold applications convert poorly compared to
referrals, and the plan should reflect that.""",
    examples=(
        "How do I get referrals at product companies?",
        "Plan my job search for the next 4 weeks",
        "Should I apply on LinkedIn or the company site?",
    ),
    keywords=(
        "job search", "apply", "application", "referral", "recruiter", "cold email",
        "outreach", "job board", "linkedin message", "follow up", "networking",
        "which companies", "job description", "notice period", "offer",
    ),
    profile_fields=(
        ProfileField(
            key="timeline",
            label="How soon do you want a role?",
            kind="select",
            options=("Immediately", "1-3 months", "3-6 months", "Just exploring"),
            default="1-3 months",
            required=True,
        ),
        ProfileField(
            key="company_size",
            label="Preferred company size",
            kind="multiselect",
            options=("Early startup", "Funded startup", "Mid-size", "Large enterprise", "Big tech"),
        ),
        ProfileField(
            key="constraints",
            label="Constraints",
            kind="tags",
            placeholder="visa, remote only, notice period…",
        ),
    ),
)


SKILL_ROADMAP = AgentSpec(
    slug="skill-roadmap",
    domain="career",
    name="Skill Gap Roadmap",
    tagline="What to learn, in what order",
    description=(
        "Compares your current skills against the target role and produces a dated "
        "learning plan with a way to prove each skill."
    ),
    icon="Route",
    output_kind=OutputKind.TEXT,
    scope="Identifying skill gaps for a target role and sequencing what to learn.",
    out_of_scope=(
        "teaching the skills themselves (use the Technical or Education domains)",
        "resume wording (use the Resume Bullet Writer)",
        "interview practice (use the Interview Coach)",
    ),
    instructions="""You map skill gaps for the target role.
Always output:
**Must have** — skills the role will not consider you without. For each: your
current level, the target level, and the gap.
**Nice to have** — differentiators, same format.
**Already strong** — what they should lead with instead of over-preparing.
**Roadmap** — a table: Week(s) | Skill | What to build | How it is proven.
Every skill must have a *proof artefact* — a project, a contribution, a
certification — because claims without evidence do not pass screening.
End with **Skip for now** — what is not worth the time for this role.""",
    examples=(
        "What am I missing for a data analyst role?",
        "3 month roadmap to become backend-ready",
        "Should I learn Kubernetes or Go next?",
    ),
    keywords=(
        "skill gap", "what should i learn", "roadmap", "learning path", "upskill",
        "certification", "course", "portfolio project", "am i ready", "prerequisite",
        "which technology should i learn", "career switch",
    ),
    profile_fields=(
        ProfileField(
            key="hours_per_week",
            label="Learning hours per week",
            kind="select",
            options=("1-3", "4-7", "8-14", "15+"),
            default="4-7",
            required=True,
        ),
        ProfileField(
            key="learning_preference",
            label="How you prefer to learn",
            kind="multiselect",
            options=("Build projects", "Structured courses", "Documentation", "Books", "Video", "Mentorship"),
            default=["Build projects"],
        ),
    ),
)


AGENTS = (RESUME_WRITER, INTERVIEW_COACH, JOB_SEARCH, SKILL_ROADMAP)

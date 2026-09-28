"""Technical domain: one agent per technology / engineering task."""

from __future__ import annotations

from app.agents.schema import AgentSpec, DomainSpec, OutputKind, ProfileField

DOMAIN = DomainSpec(
    key="technical",
    name="Technical",
    tagline="Language and task specialists for engineering",
    description=(
        "Engineering help split by technology. Each agent stays inside its own "
        "stack so answers use the idioms and tooling of that ecosystem."
    ),
    icon="Code2",
    accent="sky",
    setup_headline="Tell us about your engineering setup",
    profile_fields=(
        ProfileField(
            key="experience",
            label="Overall experience",
            kind="select",
            options=("Student", "0-1 years", "1-3 years", "3-5 years", "5-8 years", "8+ years"),
            default="1-3 years",
            required=True,
            help_text="Shared by every Technical agent.",
        ),
        ProfileField(
            key="explanation_style",
            label="How should code be explained?",
            kind="multiselect",
            options=(
                "Runnable example first",
                "Concept first, then code",
                "Line-by-line comments",
                "Type annotations",
                "Include a test",
                "Performance notes",
                "Minimal boilerplate",
            ),
            default=["Runnable example first", "Type annotations"],
        ),
        ProfileField(
            key="project_context",
            label="What are you building?",
            kind="text",
            placeholder="e.g. A FastAPI + React SaaS with PostgreSQL",
        ),
    ),
)


PYTHON = AgentSpec(
    slug="python",
    domain="technical",
    name="Python Engineer",
    tagline="Python only",
    description=(
        "Writes, explains and fixes Python — language features, standard library, "
        "packaging, async, typing and the Python web/data ecosystem."
    ),
    icon="FileCode2",
    output_kind=OutputKind.TEXT,
    scope="Python language, standard library and Python frameworks.",
    out_of_scope=(
        "JavaScript, TypeScript or React questions (use the React Engineer)",
        "SQL query writing (use the SQL Engineer)",
        "algorithm/interview puzzle coaching (use the DSA Coach)",
        "non-programming questions",
    ),
    instructions="""You are a Python specialist. Every code sample must be Python.
- Give a complete, runnable snippet — imports included, no pseudo-code.
- Use type annotations and modern syntax (3.10+: match, `X | None`, dataclasses).
- Prefer the standard library; name a third-party package only when it is the
  genuine idiomatic choice, and say why.
- Point out the Python-specific trap in play (mutable defaults, late binding in
  closures, GIL, shallow copies, generator exhaustion) when it is relevant.
- If asked about a framework, use the one named in the profile.""",
    examples=(
        "Explain Python decorators with a practical example",
        "How do I use asyncio.gather with error handling?",
        "What is the difference between __new__ and __init__?",
    ),
    keywords=(
        "python", "pip", "venv", "asyncio", "await", "decorator", "dataclass",
        "pydantic", "fastapi", "django", "flask", "pandas", "numpy", "pytest",
        "__init__", "self", "list comprehension", "generator", "yield", "gil",
        "type hint", "mypy", "requirements.txt", "pyproject",
    ),
    profile_fields=(
        ProfileField(
            key="python_version",
            label="Python version",
            kind="select",
            options=("3.10", "3.11", "3.12", "3.13", "3.14", "Any recent"),
            default="Any recent",
        ),
        ProfileField(
            key="frameworks",
            label="Frameworks you use",
            kind="multiselect",
            options=(
                "FastAPI",
                "Django",
                "Flask",
                "SQLAlchemy",
                "Pydantic",
                "pandas",
                "PyTorch",
                "Celery",
                "pytest",
            ),
        ),
        ProfileField(
            key="level",
            label="Python level",
            kind="select",
            options=("Beginner", "Intermediate", "Advanced", "Expert"),
            default="Intermediate",
            required=True,
        ),
    ),
)


REACT = AgentSpec(
    slug="react",
    domain="technical",
    name="React Engineer",
    tagline="React & frontend only",
    description=(
        "Builds and debugs React components — hooks, state, rendering behaviour, "
        "routing, forms and styling."
    ),
    icon="Component",
    output_kind=OutputKind.TEXT,
    scope="React, JSX, hooks and the browser-side JavaScript/TypeScript ecosystem.",
    out_of_scope=(
        "Python or backend code (use the Python Engineer)",
        "SQL queries (use the SQL Engineer)",
        "algorithm puzzles (use the DSA Coach)",
    ),
    instructions="""You are a React specialist. Every sample is JSX/TSX.
- Function components and hooks only. Never class components unless asked.
- Include the full component, imports included.
- Be exact about hook rules: dependency arrays, cleanup functions, why an effect
  runs twice in StrictMode, stale closures, and when a `key` change is the fix.
- Prefer derived state over synchronising state; call it out when the user's
  approach duplicates state.
- Use the styling approach from the profile.
- Mention accessibility (labels, roles, focus) when building interactive UI.""",
    examples=(
        "Why does my useEffect run twice?",
        "Build a debounced search input",
        "How do I lift state up without prop drilling?",
    ),
    keywords=(
        "react", "jsx", "tsx", "usestate", "useeffect", "usememo", "usecallback",
        "useref", "usecontext", "hook", "component", "props", "re-render", "rerender",
        "vite", "next.js", "nextjs", "tailwind", "css", "dom", "event handler",
        "react router", "redux", "zustand", "typescript", "javascript",
    ),
    profile_fields=(
        ProfileField(
            key="language",
            label="JavaScript or TypeScript?",
            kind="select",
            options=("TypeScript", "JavaScript"),
            default="TypeScript",
            required=True,
        ),
        ProfileField(
            key="styling",
            label="Styling approach",
            kind="select",
            options=("Tailwind CSS", "CSS Modules", "styled-components", "Plain CSS", "MUI"),
            default="Tailwind CSS",
        ),
        ProfileField(
            key="meta_framework",
            label="Framework",
            kind="select",
            options=("Vite (SPA)", "Next.js", "Remix", "Create React App"),
            default="Vite (SPA)",
        ),
    ),
)


SQL = AgentSpec(
    slug="sql",
    domain="technical",
    name="SQL Engineer",
    tagline="Queries, schema and performance",
    description=(
        "Writes and optimises SQL — joins, window functions, indexes, query plans "
        "and schema design."
    ),
    icon="Database",
    output_kind=OutputKind.TEXT,
    scope="SQL queries, schema design and database performance.",
    out_of_scope=(
        "application code in Python or JavaScript (use those agents)",
        "business interpretation of results (use the Analytics domain)",
        "ORM-specific application design questions",
    ),
    instructions="""You are a SQL specialist. Every answer contains SQL.
- Write for the dialect in the profile. Note where syntax differs if it matters.
- Format readably: one clause per line, uppercase keywords, aliases everywhere.
- For performance questions: name the likely plan problem (seq scan, nested
  loop, spill), the index or rewrite that fixes it, and how to confirm with
  EXPLAIN ANALYZE.
- Never use SELECT * in a final answer.
- Call out correctness traps: duplicate rows from fan-out joins, NULL handling
  in NOT IN, aggregates without GROUP BY, off-by-one in BETWEEN on timestamps.""",
    examples=(
        "Why does my LEFT JOIN return duplicate rows?",
        "Write a query for month-over-month revenue growth",
        "How do I index this slow query?",
    ),
    keywords=(
        "sql", "query", "select", "join", "left join", "inner join", "group by",
        "having", "window function", "row_number", "rank", "cte", "with clause",
        "index", "explain", "query plan", "postgres", "postgresql", "mysql",
        "sqlite", "primary key", "foreign key", "normalisation", "schema",
        "transaction", "deadlock", "upsert",
    ),
    profile_fields=(
        ProfileField(
            key="dialect",
            label="Database",
            kind="select",
            options=("PostgreSQL", "MySQL", "SQLite", "SQL Server", "Oracle", "BigQuery", "Snowflake"),
            default="PostgreSQL",
            required=True,
        ),
        ProfileField(
            key="scale",
            label="Rough data size",
            kind="select",
            options=("Small (<1M rows)", "Medium (1M-100M)", "Large (100M+)"),
            default="Small (<1M rows)",
        ),
    ),
)


DSA = AgentSpec(
    slug="dsa",
    domain="technical",
    name="DSA Coach",
    tagline="Algorithms & interview problems",
    description=(
        "Coaches data structures and algorithms — approach, complexity, and the "
        "implementation, in the style interviews expect."
    ),
    icon="Binary",
    output_kind=OutputKind.TEXT,
    scope="Data structures, algorithms and coding-interview problem solving.",
    out_of_scope=(
        "framework or library usage questions (use the language agents)",
        "SQL query writing (use the SQL Engineer)",
        "behavioural interview preparation (use the Career domain)",
    ),
    instructions="""You are a DSA coach. Never jump straight to code.
Answer in this exact order:
1. **Restate** — the problem in one line, with the constraints that matter.
2. **Brute force** — the obvious approach and its complexity.
3. **Key insight** — the single observation that unlocks the better solution.
4. **Approach** — the optimal algorithm in prose, as steps.
5. **Complexity** — time and space, with a one-line justification.
6. **Code** — clean implementation in the profile's language.
7. **Edge cases** — the inputs that break naive solutions.
Teach the pattern by name (two pointers, sliding window, monotonic stack,
binary search on answer, union-find, topological sort) so it transfers.""",
    examples=(
        "Find the longest substring without repeating characters",
        "Explain when to use a monotonic stack",
        "How do I detect a cycle in a linked list?",
    ),
    keywords=(
        "dsa", "algorithm", "complexity", "big o", "leetcode", "time complexity",
        "space complexity", "linked list", "binary tree", "bst", "graph", "dfs",
        "bfs", "dynamic programming", "memoization", "two pointers", "sliding window",
        "heap", "priority queue", "trie", "union find", "topological sort",
        "backtracking", "greedy", "binary search", "sorting", "recursion",
        # Classic problem names and complexity notation people actually type.
        "two sum", "three sum", "longest substring", "merge intervals",
        "brute force", "optimal solution", "o(n)", "o(1)", "o(log n)",
        "o(n log n)", "o(n^2)", "in linear time", "in constant time",
    ),
    profile_fields=(
        ProfileField(
            key="language",
            label="Language for solutions",
            kind="select",
            options=("Python", "Java", "C++", "JavaScript", "Go", "C#"),
            default="Python",
            required=True,
        ),
        ProfileField(
            key="level",
            label="Current level",
            kind="select",
            options=("Just starting", "Easy problems", "Medium problems", "Hard problems"),
            default="Medium problems",
            required=True,
        ),
        ProfileField(
            key="target",
            label="Preparing for",
            kind="text",
            placeholder="e.g. Product company interviews in 3 months",
        ),
    ),
)


DEBUGGER = AgentSpec(
    slug="debugger",
    domain="technical",
    name="Error Debugger",
    tagline="Paste an error, get the cause",
    description=(
        "Diagnoses a specific error, traceback or stack trace you paste in, and "
        "gives the minimal fix."
    ),
    icon="Bug",
    output_kind=OutputKind.TEXT,
    scope="Diagnosing a specific error message, traceback or failing behaviour.",
    out_of_scope=(
        "teaching a language or concept from scratch (use the language agents)",
        "reviewing working code for quality (use the Code Reviewer)",
        "algorithm design (use the DSA Coach)",
    ),
    instructions="""You diagnose errors. Be surgical, never rewrite the project.
Answer as:
**Root cause** — one sentence naming the actual cause, not the symptom.
**Why it happens** — two or three lines of mechanism.
**The fix** — the minimal diff. Show only the lines that change.
**Verify** — the exact command or check that proves it is fixed.
**If that is not it** — the next most likely cause and how to distinguish them.
If the traceback is truncated or the relevant code is missing, state exactly
what you need. Never invent code the user did not show.""",
    examples=(
        "TypeError: 'NoneType' object is not subscriptable — here's my traceback",
        "My Docker build fails at the pip install step",
        "CORS error when calling my API from the browser",
    ),
    keywords=(
        "error", "traceback", "exception", "stack trace", "fails", "failing",
        "not working", "broken", "crash", "bug", "undefined", "null pointer",
        "segfault", "timeout", "connection refused", "permission denied",
        "module not found", "cannot import", "syntax error", "502", "500",
    ),
    profile_fields=(
        ProfileField(
            key="stack",
            label="Your stack",
            kind="tags",
            placeholder="Python, FastAPI, Docker, PostgreSQL…",
            required=True,
        ),
        ProfileField(
            key="environment",
            label="Where it runs",
            kind="select",
            options=("Local machine", "Docker", "Kubernetes", "Cloud VM", "Serverless", "CI"),
            default="Local machine",
        ),
    ),
)


CODE_REVIEWER = AgentSpec(
    slug="code-reviewer",
    domain="technical",
    name="Code Reviewer",
    tagline="Review working code",
    description=(
        "Reviews code that already works — correctness risks, security, naming, "
        "structure and performance — ordered by severity."
    ),
    icon="FileSearch",
    output_kind=OutputKind.TEXT,
    scope="Reviewing supplied code for quality, security and maintainability.",
    out_of_scope=(
        "debugging a broken error (use the Error Debugger)",
        "writing a feature from scratch (use the language agents)",
    ),
    instructions="""You review code that the user supplies.
Output findings as a list ordered by severity, each shaped as:
**[Critical|High|Medium|Nit] Short title** — what is wrong, why it matters, and
the corrected lines.
Rules:
- Always check for: injection, secrets in code, missing input validation,
  unhandled errors, race conditions, N+1 queries, resource leaks.
- Say plainly when something is fine — do not invent problems to fill a list.
- End with **Verdict**: one line on whether you would approve it.
- Do not reformat or restyle code unless it hides a bug.""",
    examples=(
        "Review this FastAPI endpoint",
        "Is this React hook correct?",
        "Any security issues in this login function?",
    ),
    keywords=(
        "review", "code review", "refactor", "improve this code", "is this correct",
        "best practice", "clean up", "any issues", "feedback on my code",
        "optimise", "optimize", "maintainable", "pull request",
    ),
    profile_fields=(
        ProfileField(
            key="strictness",
            label="Review strictness",
            kind="select",
            options=("Blocking issues only", "Balanced", "Pedantic"),
            default="Balanced",
        ),
        ProfileField(
            key="priorities",
            label="What matters most",
            kind="multiselect",
            options=("Security", "Correctness", "Performance", "Readability", "Testing", "Typing"),
            default=["Correctness", "Security"],
        ),
    ),
)


AGENTS = (PYTHON, REACT, SQL, DSA, DEBUGGER, CODE_REVIEWER)

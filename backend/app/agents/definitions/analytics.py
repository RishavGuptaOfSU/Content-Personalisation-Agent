"""Analytics domain. ``chart-builder`` renders a real chart image from data."""

from __future__ import annotations

from app.agents.schema import AgentSpec, DomainSpec, OutputKind, ProfileField

DOMAIN = DomainSpec(
    key="analytics",
    name="Analytics",
    tagline="Charts, EDA, queries and insights",
    description=(
        "Data work split by task. The chart builder renders an actual chart from the "
        "data you paste; the others plan the analysis or interpret the numbers."
    ),
    icon="BarChart3",
    accent="cyan",
    setup_headline="Tell us about your data work",
    profile_fields=(
        ProfileField(
            key="experience",
            label="Analytics experience",
            kind="select",
            options=("Beginner", "Intermediate", "Advanced", "Expert"),
            default="Intermediate",
            required=True,
            help_text="Shared by every Analytics agent.",
        ),
        ProfileField(
            key="tools",
            label="Tools you use",
            kind="multiselect",
            options=("Python / pandas", "SQL", "Excel", "Power BI", "Tableau", "R", "Looker", "Spark"),
            required=True,
        ),
        ProfileField(
            key="domain_context",
            label="What data do you work with?",
            kind="text",
            placeholder="e.g. E-commerce orders and marketing spend",
        ),
    ),
)


CHART_BUILDER = AgentSpec(
    slug="chart-builder",
    domain="analytics",
    name="Chart Builder",
    tagline="Renders a chart from your data",
    description=(
        "Turns pasted or uploaded data into an actual rendered chart, choosing the "
        "chart type that fits the data. Returns an image, not code."
    ),
    icon="ChartSpline",
    output_kind=OutputKind.CHART,
    scope="Rendering a chart image from data the user supplies.",
    out_of_scope=(
        "planning an exploratory analysis (use the EDA Planner)",
        "writing SQL (use the Analytics SQL Writer)",
        "interpreting business meaning at length (use the Insight Writer)",
        "requests with no data attached — ask for the data instead",
    ),
    instructions="""You turn supplied data into a chart specification.

Return ONLY a JSON object:
{
  "chart_type": "bar" | "line" | "barh" | "pie" | "scatter" | "area",
  "title": "<chart title>",
  "x_label": "<axis label>",
  "y_label": "<axis label>",
  "labels": ["<category or x value>", ...],
  "series": [{"name": "<series name>", "values": [<numbers>]}],
  "note": "<one short sentence on what the chart shows>"
}

Rules:
- Use ONLY the numbers present in the user's data. Never invent or extrapolate.
- Pick the chart type from the data shape: time on an axis -> line; category
  comparison -> bar; part-to-whole with <=6 parts -> pie; two numerics -> scatter.
- `labels` and every series' `values` must be the same length.
- If no usable data was supplied, return
  {"error": "<exactly what data you need>"} instead.
- No prose outside the JSON.""",
    examples=(
        "Chart this: Jan 120, Feb 150, Mar 180, Apr 140",
        "Plot revenue by region from the attached CSV",
        "Show me a pie chart of traffic sources: organic 55, paid 25, social 20",
    ),
    keywords=(
        "chart", "plot", "graph", "visualise", "visualize", "bar chart", "line chart",
        "pie chart", "scatter", "histogram", "draw", "trend line", "show me a chart",
    ),
    profile_fields=(
        ProfileField(
            key="style",
            label="Chart style",
            kind="select",
            options=("Clean light", "Dark", "Minimal", "Colourful"),
            default="Clean light",
            required=True,
        ),
        ProfileField(
            key="default_chart",
            label="Preferred chart when ambiguous",
            kind="select",
            options=("Bar", "Line", "Horizontal bar", "Pie"),
            default="Bar",
        ),
        ProfileField(
            key="show_values",
            label="Show value labels on the chart?",
            kind="select",
            options=("Yes", "No"),
            default="Yes",
        ),
    ),
    options={"default_size": [1200, 700]},
)


EDA_PLANNER = AgentSpec(
    slug="eda-planner",
    domain="analytics",
    name="EDA Planner",
    tagline="What to check, in what order",
    description=(
        "Produces a concrete exploratory analysis checklist for your dataset — "
        "profiling, missingness, distributions, relationships and leakage."
    ),
    icon="ClipboardList",
    output_kind=OutputKind.TEXT,
    scope="Planning exploratory data analysis steps for a described dataset.",
    out_of_scope=(
        "rendering charts (use the Chart Builder)",
        "writing production SQL (use the Analytics SQL Writer)",
        "business recommendations (use the Insight Writer)",
    ),
    instructions="""You produce an EDA plan, ordered and specific to the described
data. Always cover, in order:
1. **Shape & grain** — rows, columns, what one row represents.
2. **Missingness** — per column, with the drop/impute decision for each.
3. **Distributions** — which columns to plot and what would be alarming.
4. **Outliers** — the rule you would use, and whether to keep them.
5. **Relationships** — which pairs to check and with what measure.
6. **Leakage & bias** — columns that must not be used, and who is missing.
Give the code for each step in the profile's primary tool.
End with **Stop when** — the point at which further exploration is not useful.""",
    examples=(
        "How should I explore a sales dataset?",
        "EDA checklist for customer churn data",
        "What should I check before modelling this?",
    ),
    keywords=(
        "eda", "exploratory", "explore the data", "data profiling", "missing values",
        "outlier", "distribution", "correlation", "data quality", "clean the data",
        "null values", "duplicates", "feature", "leakage",
    ),
    profile_fields=(
        ProfileField(
            key="primary_tool",
            label="Tool for code examples",
            kind="select",
            options=("Python / pandas", "SQL", "R", "Excel", "PySpark"),
            default="Python / pandas",
            required=True,
        ),
        ProfileField(
            key="goal",
            label="Usual end goal",
            kind="select",
            options=("Dashboard", "ML model", "One-off question", "Data quality audit"),
            default="One-off question",
        ),
    ),
)


SQL_ANALYTICS = AgentSpec(
    slug="sql-analytics",
    domain="analytics",
    name="Analytics SQL Writer",
    tagline="Metric queries",
    description=(
        "Writes analytical SQL — cohorts, funnels, retention, period-over-period "
        "growth and window-function metrics."
    ),
    icon="TableProperties",
    output_kind=OutputKind.TEXT,
    scope="Writing analytical SQL for metrics, cohorts, funnels and retention.",
    out_of_scope=(
        "database performance tuning and schema design (Technical → SQL Engineer)",
        "rendering charts (use the Chart Builder)",
        "narrative interpretation (use the Insight Writer)",
    ),
    instructions="""You write analytical SQL.
- Always state the assumed table and column names at the top as a short list, so
  the user can remap them.
- Use CTEs, one logical step per CTE, named for what it produces.
- Handle the analytics traps explicitly: date truncation and timezones,
  deduplicating events, first-touch vs last-touch, dividing by zero
  (use NULLIF), and counting distinct users rather than rows.
- After the query, add **Reads as** — one line describing what each row means.""",
    examples=(
        "Write a monthly retention cohort query",
        "Funnel conversion from signup to first purchase",
        "Month-over-month revenue growth by region",
    ),
    keywords=(
        "cohort", "retention", "funnel", "conversion rate", "month over month",
        "week over week", "dau", "mau", "arpu", "ltv", "churn rate", "sql metric",
        "running total", "moving average", "percentile", "attribution",
    ),
    profile_fields=(
        ProfileField(
            key="warehouse",
            label="Warehouse / database",
            kind="select",
            options=("PostgreSQL", "BigQuery", "Snowflake", "Redshift", "MySQL", "DuckDB"),
            default="PostgreSQL",
            required=True,
        ),
        ProfileField(
            key="event_table",
            label="Main event/fact table name",
            kind="text",
            placeholder="e.g. events, orders",
        ),
    ),
)


INSIGHT_WRITER = AgentSpec(
    slug="insight-writer",
    domain="analytics",
    name="Insight Writer",
    tagline="Turns numbers into decisions",
    description=(
        "Reads results you paste in and writes the interpretation — what changed, "
        "what plausibly caused it, and what to do next."
    ),
    icon="Lightbulb",
    output_kind=OutputKind.TEXT,
    scope="Interpreting supplied results and recommending next actions.",
    out_of_scope=(
        "rendering charts (use the Chart Builder)",
        "writing queries (use the Analytics SQL Writer)",
        "planning the analysis (use the EDA Planner)",
    ),
    instructions="""You interpret numbers the user supplies.
Structure every answer as:
**What the data shows** — only what is literally in the numbers.
**What could explain it** — ranked hypotheses, each with the check that would
confirm or kill it.
**What I would do next** — at most three concrete actions.
**What this does not tell us** — the confounders and the missing population.
Never state a number the user did not give you. Separate observation from
inference in every case — say "this is consistent with" rather than "this proves".""",
    examples=(
        "Signups fell 18% last week — here are the numbers",
        "What do these A/B test results mean?",
        "Interpret this funnel drop-off",
    ),
    keywords=(
        "why did", "what does this mean", "interpret", "insight", "explain the drop",
        "explain the spike", "a/b test", "significance", "recommendation",
        "takeaway", "summary of results", "root cause",
    ),
    profile_fields=(
        ProfileField(
            key="audience",
            label="Who reads your analysis?",
            kind="select",
            options=("Executives", "Product managers", "Engineers", "Marketing", "Myself"),
            default="Product managers",
            required=True,
        ),
        ProfileField(
            key="format",
            label="Preferred output",
            kind="select",
            options=("Executive summary", "Detailed writeup", "Bullet takeaways", "Slide notes"),
            default="Bullet takeaways",
        ),
    ),
)


AGENTS = (CHART_BUILDER, EDA_PLANNER, SQL_ANALYTICS, INSIGHT_WRITER)

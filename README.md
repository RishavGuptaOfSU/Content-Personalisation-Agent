# Content Personalisation Agent

Personalised AI content generation, built in two phases. Each phase is a
complete, self-contained application.

| Phase | Folder | Focus | Status |
|-------|--------|-------|--------|
| **Phase 1** | [`phase-1/`](phase-1/README.md) | **Breadth** — 7 domains, 34 narrow agents, two-level catalog | ✅ Complete |
| **Phase 2** | [`phase-2/`](phase-2/README.md) | **Depth** — one domain (Marketing), 5 agents, evidence-driven quality work | ✅ Built, evaluated |

---

## The idea both phases share

Personalisation is **per need, not per subject**. You do not get one "Marketing
Agent"; you get a *Social Post Image Generator*, a *Social Caption Writer*, an
*SEO Optimizer* — each owning exactly one deliverable and refusing the others,
naming the agent that should handle the request instead.

Three levels of profile feed every request, most general first:

1. **Global** — your tone, preferred length, skill level, language
2. **Domain / brand** — answered once, reused by every agent in the domain
3. **Agent** — the narrow specifics of one job

Some agents hand back a **rendered file** rather than prose: the model returns a
JSON design spec and a local Pillow renderer produces the PNG, so it works on a
CPU with no API key and a chart can never contain invented numbers.

---

## Phase 1 — breadth

Seven domains containing 34 agents (`education.class10-maths`,
`technical.python`, `marketing.post-image`, `analytics.chart-builder`, …), a
two-stage router, a deterministic scope guard, three-level profiles, scoped
semantic memory and a feedback loop that turns repeated corrections into durable
preferences.

Verified: 163/163 end-to-end assertions, 34/34 agents producing their declared
deliverable, migrations clean, live run against a local model.

→ [`phase-1/README.md`](phase-1/README.md)

## Phase 2 — depth

The same architecture narrowed to **Marketing** and taken further: five agents,
one brand profile, and a measured quality pass.

Phase 2's point is the method as much as the result. An audit established what
was actually broken ([`phase-2/docs/marketing-audit.md`](phase-2/docs/marketing-audit.md)),
a reproducible evaluation suite recorded a baseline against a real model, fixes
were applied, and the same suite was re-run and compared — including the places
where the fix did not work and the one case where the *assertion* was wrong
rather than the agent.

It also added a **grounding guard**: marketing copy invents figures ("save up to
$100K", "reduce costs by 50%") even when explicitly told not to, so claim-shaped
numbers are now checked against the numbers the user actually supplied and
flagged when they are not.

The deterministic half passes **109/110**. The creative half is scored
separately by an **LLM judge** applying the same rubric a human would read —
**4.28/5**, judged by a different model than the one that wrote the output, with
the judge's own disagreement rate reported alongside. Running it found two bugs
in the *evaluation* (a 1–5 scale that had collapsed to 1/3/5, and a test case
that scored correct behaviour as a failure), which is the part worth reading.

Then every **free** model on the provider was raced against the same suite to
pick the best one per agent. The answer turned out to be *don't*: run-to-run
variance is larger than any per-agent gap, so one model serves all five. That
race also exposed a real bug — reasoning models returning HTTP 200 with an empty
body when their token budget goes on hidden thinking.

→ [`phase-2/README.md`](phase-2/README.md)

---

## Running either phase

Both follow the same shape. Phase 2:

```bash
cd phase-2/backend
uv venv .venv && uv pip install -r requirements.txt   # or python -m venv + pip
cp .env.example .env            # change JWT_SECRET_KEY before any real use
alembic upgrade head
python scripts/seed_demo.py     # demo@example.com / DemoPass123
uvicorn app.main:app --reload --port 8000

cd ../frontend && npm install && cp .env.example .env && npm run dev
```

For real answers, point it at a model — local and free is shortest:

```bash
ollama serve && ollama pull llama3.2:3b && ollama pull nomic-embed-text
```

With no model at all, `LLM_PROVIDER=mock` runs the whole stack on a
deterministic composer, which is how the fast test suites work.

**Tech:** FastAPI · SQLAlchemy 2 · Alembic · LangGraph · React 18 · Vite ·
Tailwind · Pillow · matplotlib · SQLite (PostgreSQL + pgvector supported) ·
pluggable LLM providers (Ollama, any OpenAI-compatible API, AWS Bedrock, NVIDIA
NIM).

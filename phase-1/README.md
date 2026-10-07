# Content Personalization Agent

A working full-stack multi-agent AI platform where personalization is **per need, not per
subject**. Seven **domains** (Education, Technical, Career, Marketing, Analytics, Research,
Creative) each contain many **narrow agents** — 34 in total. If you study Class 10 maths you
get the *Class 10 Maths Tutor*; if you learn Python you get the *Python Engineer*; if you need
a social post graphic you get the *Social Post Image Generator*, which hands back a **rendered
PNG** rather than prose.

Each agent does exactly one job and **refuses the others**, naming the agent that owns the
request instead. Personalization is layered: a **global profile**, then one profile **per
domain** (board and class, brand and audience…), then one **per agent** (weak chapters,
platform and visual style…). A **Router Agent** picks the agent when the user has not, a
**personalization engine** assembles all three profile levels plus history and semantic memory
into the prompt, and a **feedback loop** turns repeated corrections into durable memories and
profile updates.

```
USER → LOGIN/SIGNUP → DOMAINS ─→ AGENTS IN A DOMAIN ─→ SELECT AGENT
                                                            ↓
                           domain profile answered? ──no──→ STEP 1: DOMAIN SETUP (shared)
                                     │yes                            ↓
                           agent  profile answered? ──no──→ STEP 2: AGENT SETUP (this job only)
                                     │yes                            │
                                     └──────────→ LOAD 3 LEVELS ←────┘
                                                        ↓
                       ROUTER → SCOPE GUARD → PERSONALIZATION ENGINE → AGENT
                                     │                                  ↓
                          out of scope? ──→ HANDOFF        text │ image │ chart
                                                                  ↓
                                          USER FEEDBACK → UPDATE MEMORY / PROFILE
```

| | |
|---|---|
| **Frontend** | React 18, Vite 8, Tailwind CSS, React Router, Axios, Lucide, react-markdown |
| **Backend** | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic |
| **Database** | PostgreSQL 16 + **pgvector** (SQLite fallback for offline dev) |
| **AI** | **LangGraph** orchestration + pluggable providers: **Ollama** (local), any **OpenAI-compatible** API, **AWS Bedrock** |
| **Media** | Pillow card renderer + matplotlib charts (local, no GPU); optional `gpt-image-1` |
| **Auth** | JWT (PyJWT) + bcrypt password hashing, protected routes |

---

## 1. Domains and agents

A **domain** is a subject area. An **agent** is one narrow job inside it, addressed by the key
`<domain>.<slug>` — that key is what the database, the API and the URLs all use.

| Domain | Agents (`<slug>`) | Shared domain profile |
|---|---|---|
| **Education** | `class10-maths` · `class10-science` · `class12-physics` · `homework-solver` · `exam-planner` · `quiz-generator` | board, language, learning style, exam target |
| **Technical** | `python` · `react` · `sql` · `dsa` · `debugger` · `code-reviewer` | experience, explanation style, project context |
| **Career** | `resume-writer` · `interview-coach` · `job-search` · `skill-roadmap` | current role, target roles, years, skills, location |
| **Marketing** | **`post-image`** 🖼 · **`ad-creative`** 🖼 · `social-copy` · `seo-optimizer` · `campaign-planner` | brand name, industry, audience, tone, brand colours, never-use |
| **Analytics** | **`chart-builder`** 📊 · `eda-planner` · `sql-analytics` · `insight-writer` | experience, tools, data context |
| **Research** | `concept-explainer` · `summarizer` · `literature-brief` · `source-finder` | field, depth, interests, background |
| **Creative** | `story-writer` · `script-writer` · `idea-generator` · `copywriter` · **`poster-image`** 🖼 | voice, tone, influences, avoid |

🖼 returns a generated **image** · 📊 returns a rendered **chart** · everything else returns text.
`GET /api/catalog` reports the live shape: `{"text": 30, "image": 3, "chart": 1}`.

### Agents are data, not classes

All 34 agents are declared as `AgentSpec` records in `backend/app/agents/definitions/*.py` —
scope, out-of-scope list, task instructions, routing keywords, examples, profile fields and
output kind. One generic runtime (`app/agents/runtime.py`) has a class **per output kind**
(`TextAgent`, `ImageAgent`, `ChartAgent`), not per agent. Adding an agent means adding a record;
34 hand-written modules would have been 34 places for the prompt contract to drift.

### Each agent stays in its lane

Every prompt carries a scope contract (what this agent does, what it must refuse). Because a
3B local model does not reliably obey negative instructions, that is backed by a deterministic
**scope guard** (`app/agents/scope.py`): if the selected agent scores no signal for a request
*and* another agent scores clearly higher, the reply is a **handoff** naming the right agent —
with no model call spent at all. It is deliberately conservative; a wrong handoff is worse than
a slightly off-topic answer, so ambiguous and short requests stay put.

```
You → Class 10 Maths Tutor: "Explain Python decorators and functools.wraps"
      → "That is outside what I do. I am the Class 10 Maths Tutor …
         Python Engineer handles this."        [0.0s, provider=scope-guard]
```

---

## 2. Quick start

Two supported paths. **Option A** is the full target stack. **Option B** runs with no Docker
and no cloud credentials — useful for a first look or a constrained machine.

### Option A — Docker Compose (PostgreSQL + pgvector)

```bash
cp .env.example .env                 # edit JWT_SECRET_KEY before any real use
docker compose up --build            # postgres + backend (migrated) + frontend
```

Then:

```bash
docker compose exec backend python scripts/seed_demo.py   # optional demo data
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| API | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs |
| Health | http://localhost:8000/health |

The backend container runs `alembic upgrade head` on start, and the Postgres image enables the
`vector` extension on first initialisation (`infra/init-pgvector.sql`).

By default the stack starts with `LLM_PROVIDER=mock` so it runs with no model
at all. For real answers, pick a provider in §5 — the shortest path is:

```bash
ollama serve && ollama pull llama3.2:3b && ollama pull nomic-embed-text
# then set LLM_PROVIDER=ollama and EMBEDDING_PROVIDER=ollama
```

Or run the bundled Ollama container:

```bash
docker compose --profile ollama up -d ollama
docker compose exec ollama ollama pull llama3.2:3b
docker compose exec ollama ollama pull nomic-embed-text
```

### Option B — Run locally without Docker

**Backend**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env` and pick a database:

```ini
# PostgreSQL + pgvector (recommended — see §3 to start one)
DATABASE_URL=postgresql+psycopg://cpa:cpa@localhost:5432/content_personalization

# …or the zero-dependency offline fallback
DATABASE_URL=sqlite:///./content_personalization.db
```

```bash
alembic upgrade head            # create the schema
python scripts/seed_demo.py     # optional: demo user + data
uvicorn app.main:app --reload --port 8000
```

**Frontend** (second terminal)

```bash
cd frontend
npm install
cp .env.example .env            # VITE_API_BASE_URL=http://localhost:8000/api
npm run dev                     # http://localhost:5173
```

> **SQLite fallback.** The app targets PostgreSQL + pgvector. When `DATABASE_URL` is a SQLite
> URL, the identical models still apply (`JSONB` → `JSON`, `vector(N)` → JSON array) and the
> vector store switches from the pgvector cosine operator to an in-process cosine search. The
> feature set is the same; only the search is not index-accelerated. `GET /health` reports
> which store is active (`"vector_store": "pgvector" | "portable"`).

---

## 3. Database setup

### With Docker (recommended)

```bash
docker compose up -d postgres

# Verify pgvector is available
docker compose exec postgres psql -U cpa -d content_personalization \
  -c "SELECT extname, extversion FROM pg_extension WHERE extname='vector';"
```

### With an existing PostgreSQL

```sql
CREATE DATABASE content_personalization;
CREATE USER cpa WITH PASSWORD 'cpa';
GRANT ALL PRIVILEGES ON DATABASE content_personalization TO cpa;
\c content_personalization
CREATE EXTENSION IF NOT EXISTS vector;   -- needs pgvector installed on the server
```

### Migrations

```bash
cd backend
alembic upgrade head                        # apply
alembic check                               # models vs. migration drift
alembic revision --autogenerate -m "msg"    # new migration
alembic downgrade -1                        # roll back one
```

`0001_initial_schema.py` creates the base tables, the foreign keys and (on PostgreSQL) an
**HNSW cosine index** on `memories.embedding`. `0002_domain_agent_split.py` performs the
domain → agent split: it adds `domain_profiles`, renames `agent_type` → `agent_key` (widened to
80 chars) everywhere, adds a denormalised `domain` column, and adds `output_kind` + `media` to
`messages`. Rows written under the old single-level model held a bare domain in `agent_type`;
they are **migrated to that domain's default agent** rather than dropped, so existing
conversations, profiles, memories and feedback survive.

### Schema

```
users ──1:1── global_profiles
  ├──1:N── domain_profiles     (unique on user_id + domain;    profile_data JSONB)
  ├──1:N── agent_profiles      (unique on user_id + agent_key; profile_data JSONB)
  ├──1:N── conversations ──1:N── messages ──1:N── feedback
  ├──1:N── memories            (embedding vector(N); scope = agent_key ▸ domain ▸ global)
  └──1:N── feedback
```

| Table | Purpose |
|---|---|
| `users` | account, bcrypt `password_hash`, `last_login_at` |
| `global_profiles` | name, occupation, interests, goals, response length, style, skill level |
| `domain_profiles` | `domain` + `profile_data` JSONB — **shared by every agent in the domain** |
| `agent_profiles` | `agent_key` + `domain` + `profile_data` JSONB, `is_configured`, `interaction_count`, `revision`, `last_used_at` |
| `conversations` | per-**agent** threads (`agent_key` + `domain`), title, `message_count` |
| `messages` | `role`, `content`, `agent_key`, **`output_kind`** (`text\|image\|chart`), **`media`** (rendered files), `meta` |
| `memories` | durable preference/interest/requirement/fact/skill + `embedding` + `occurrences`; scoped by `agent_key`, or `domain`, or neither (global) |
| `feedback` | `rating` (+1/−1), `feedback_text`, `processed`, `outcome` (what the system changed) |

`scripts/check_migration.py` builds a 0001-era database, inserts legacy rows, upgrades to head
and asserts every row survived with the right `agent_key`/`domain`, then downgrades and runs
`alembic check`:

```bash
cd backend && python scripts/check_migration.py     # 45 assertions, uses /tmp
```

---

## 4. Environment variables

Full reference: [`backend/.env.example`](backend/.env.example),
[`frontend/.env.example`](frontend/.env.example), [`.env.example`](.env.example) (compose).

### Backend — required

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://cpa:cpa@localhost:5432/content_personalization` | psycopg3 driver |
| `JWT_SECRET_KEY` | dev placeholder | **Change it.** `openssl rand -hex 48` |
| `CORS_ORIGINS` | `http://localhost:5173,…` | Comma-separated or a JSON array |

### Backend — AI provider

| Variable | Default | Notes |
|---|---|---|
| `LLM_PROVIDER` | `mock` | `ollama` \| `openai` \| `bedrock` \| `mock` |
| `LLM_MAX_TOKENS` | `1600` | Use ~700 for a local CPU model |
| `LLM_TEMPERATURE` | `0.4` | Per-agent overrides exist (code 0.2, creative 0.85) |
| `EMBEDDING_PROVIDER` | `local` | `ollama` \| `openai` \| `bedrock` \| `local` |
| `EMBEDDING_DIM` | `1024` | **Must match the model's native width** |
| `ROUTER_USE_LLM` | `true` | Two-stage LLM classification (domain, then agent) |
| `ROUTER_KEYWORD_MIN_SCORE` | `4.0` | Keyword score needed to skip the model entirely |
| `ROUTER_LLM_MIN_MARGIN` | `3.0` | Margin over the runner-up needed for that shortcut |
| `MEMORY_LLM_EXTRACTION` | `false` | Extra model call per user message |

### Backend — image and chart generation

| Variable | Default | Notes |
|---|---|---|
| `IMAGE_PROVIDER` | `local` | `local` (Pillow card renderer, no GPU, no key) \| `openai` (`gpt-image-1`) |
| `OPENAI_IMAGE_MODEL` | `gpt-image-1` | Used only when `IMAGE_PROVIDER=openai` |
| `OPENAI_IMAGE_TIMEOUT` | `180` | Seconds |
| `MEDIA_ROOT` | `generated_media` | Where rendered PNGs are written (relative to `backend/`) |
| `MEDIA_MAX_FILES` | `400` | Retention cap; the oldest files are pruned beyond it |

Charts are always rendered locally with matplotlib — a chart must plot the user's real numbers,
so there is nothing for an image model to do.

### Backend — scope guard

The guard only runs when the user **explicitly** picked the agent (a routed request is in scope
by construction). All four conditions must hold before a handoff happens.

| Variable | Default | Meaning |
|---|---|---|
| `SCOPE_MIN_REQUEST_CHARS` | `15` | Shorter requests ("hi", "thanks") are never handed off |
| `SCOPE_OWN_MAX_SCORE` | `1.5` | The selected agent must score at or below this |
| `SCOPE_OTHER_MIN_SCORE` | `4.0` | Another agent must score at least this |
| `SCOPE_MIN_MARGIN` | `3.0` | And must beat the selected agent by this much |

Raise the thresholds to hand off less often; set `SCOPE_OTHER_MIN_SCORE` very high to disable
handoffs entirely and rely on the prompt contract alone.

**Ollama** — `OLLAMA_BASE_URL` (`http://localhost:11434`), `OLLAMA_MODEL`
(`llama3.2:3b`), `OLLAMA_ROUTER_MODEL`, `OLLAMA_EMBEDDING_MODEL`
(`nomic-embed-text`), `OLLAMA_TIMEOUT` (`600`), `OLLAMA_NUM_CTX` (`8192`),
`OLLAMA_KEEP_ALIVE` (`10m`).

**OpenAI-compatible** — `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL`,
`OPENAI_ROUTER_MODEL`, `OPENAI_EMBEDDING_MODEL`, `OPENAI_TIMEOUT`.

**Bedrock** — `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
`AWS_SESSION_TOKEN`, `BEDROCK_MODEL_ID`, `BEDROCK_ROUTER_MODEL_ID`,
`BEDROCK_EMBEDDING_MODEL_ID`. Leave the keys blank to use the default boto3
chain (SSO, instance role, task role).

No provider credential is ever sent to the browser — every model call is made
server-side.

### Backend — memory / personalization tuning

| Variable | Default | Meaning |
|---|---|---|
| `MEMORY_TOP_K` | `6` | Semantic matches retrieved per request |
| `MEMORY_MIN_SIMILARITY` | `0.25` | Cosine floor for semantic recall |
| `MEMORY_STANDING_LIMIT` | `4` | Standing preferences pinned into every request |
| `MEMORY_STANDING_IMPORTANCE` | `0.6` | Importance at which a memory becomes "standing" |
| `SHORT_TERM_WINDOW` | `12` | Recent messages injected as short-term memory |
| `SHORT_TERM_MAX_CHARS` | `3000` | Total size cap on replayed history |
| `SHORT_TERM_MESSAGE_MAX_CHARS` | `900` | Per-message cap; the middle of a long turn is elided |
| `SHORT_TERM_TRIVIAL_MAX_CHARS` | `700` | History budget for greetings |
| `TRIVIAL_REPLY_MAX_TOKENS` | `160` | Reply budget for greetings |
| `FEEDBACK_PROMOTION_THRESHOLD` | `2` | Repeats required before feedback rewrites a profile |
| `MEMORY_DEDUPE_SIMILARITY` | `0.92` | Above this, a new memory reinforces instead of duplicating |

### Frontend

| Variable | Default | Notes |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000/api` | Use `/api` to route through the Vite proxy instead (no CORS) |

Only `VITE_*` variables reach the browser. **No AWS credential or model key is ever exposed to
the frontend** — every model call is made server-side.

---

## 5. Choosing a model provider

The provider is an environment setting. Four are built in, and every call site
goes through `BaseLLMProvider`, so switching never touches application code.

| `LLM_PROVIDER` | What it uses | Needs |
|---|---|---|
| `ollama` | Local models on your machine | Ollama installed; no API key |
| `openai` | Any OpenAI-compatible HTTP API | Base URL (+ key for hosted services) |
| `bedrock` | AWS Bedrock | AWS credentials or an instance/task role |
| `mock` | Deterministic local composer | Nothing at all |

`GET /health` always reports which provider is live, whether its model is
actually available, and whether streaming is supported.

### Option 1 — Ollama (local, free, recommended)

```bash
# 1. Install Ollama: https://ollama.com/download
ollama serve                      # leave running

# 2. Pull a chat model and a real embedding model
ollama pull llama3.2:3b           # ~2.0 GB
ollama pull nomic-embed-text      # ~274 MB, 768-dim embeddings
```

```ini
# backend/.env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2:3b
OLLAMA_ROUTER_MODEL=llama3.2:3b
OLLAMA_KEEP_ALIVE=30m             # keeps the model resident between requests

EMBEDDING_PROVIDER=ollama
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIM=768                 # nomic-embed-text's native width
MEMORY_MIN_SIMILARITY=0.45        # see "Similarity thresholds" below

LLM_MAX_TOKENS=700                # keep replies short on CPU
```

```bash
cd backend
python scripts/reembed_memories.py   # REQUIRED after changing the embedder
uvicorn app.main:app --reload --port 8000
```

**Picking a model for your hardware.** Generation speed dominates the
experience, and on a CPU it is roughly linear in parameter count:

| Model | Size | CPU-only feel | Notes |
|---|---|---|---|
| `llama3.2:1b` | 1.3 GB | fastest | weak reasoning; fine for routing |
| `llama3.2:3b` | 2.0 GB | usable | **good default on CPU** |
| `qwen2.5:3b` | 1.9 GB | usable | strongest at structure/JSON in this class |
| `gemma2:2b` | 1.6 GB | fast | good prose, shorter answers |
| `mistral:7b` / `llama3.1:8b` | 4–5 GB | slow without a GPU | noticeably better reasoning |

A measured example from this machine (Intel i5-10210U, 4 cores, **no GPU**):
`llama3.2:3b` produces ~3 tokens/second, so a 400-token answer takes ~2 minutes.
That is why responses **stream** (below) and why `LLM_MAX_TOKENS` defaults to 700
for local use. With a GPU, or a hosted provider, raise it to 1600+.

### Option 2 — Any OpenAI-compatible API

One provider implementation covers most services. Groq in particular is free to
start and extremely fast, which sidesteps local CPU limits entirely:

```ini
LLM_PROVIDER=openai
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_API_KEY=gsk_...
OPENAI_MODEL=llama-3.3-70b-versatile
```

| Service | `OPENAI_BASE_URL` | Example model |
|---|---|---|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
| Together AI | `https://api.together.xyz/v1` | `meta-llama/Llama-3.3-70B-Instruct-Turbo` |
| OpenRouter | `https://openrouter.ai/api/v1` | `anthropic/claude-3.5-sonnet` |
| Mistral | `https://api.mistral.ai/v1` | `mistral-large-latest` |
| LM Studio | `http://localhost:1234/v1` | (whatever is loaded; no key) |
| vLLM | `http://localhost:8001/v1` | (served model; no key) |

Embeddings from the same endpoint:

```ini
EMBEDDING_PROVIDER=openai
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536        # then: python scripts/reembed_memories.py
```

### Option 3 — AWS Bedrock

```ini
LLM_PROVIDER=bedrock
EMBEDDING_PROVIDER=bedrock
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...        # or omit and use the default boto3 chain
AWS_SECRET_ACCESS_KEY=...
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
EMBEDDING_DIM=1024           # Titan v2
```

### Response streaming

Because a local CPU model can take a minute, `POST /api/chat/stream` returns
Server-Sent Events and the UI renders tokens as they arrive:

```
event: meta   → routing + scope + full personalization trace     (~0.4s)
event: status → {"message": "Generating the image…"}   (visual agents only)
event: delta  → {"text": "..."} per chunk                        (first ~8s)
event: done   → the persisted ChatResponse
event: error  → {"detail": "..."}
```

The `meta` event is emitted **before** generation starts, so the right-hand panel
shows which profile and memories are being used while the model is still writing.
The UI also shows an elapsed timer and a Stop button. `POST /api/chat` remains
available as a non-streaming endpoint, and the frontend falls back to it
automatically if SSE is blocked by a proxy.

**Visual agents do not stream.** An image cannot be sent before it exists, so
`meta.streaming` is `false` for them, a `status` event replaces the token stream,
and the rendered file arrives with the persisted turn in `done`.

Providers that stream natively: Ollama, OpenAI-compatible, and the mock
composer. Any provider without native streaming still works — the base class
yields the completed response as a single chunk.

### Image and chart generation

Four agents hand back a file instead of prose. In every case **the model never draws
anything** — it returns a short JSON spec and a renderer produces the file. That keeps the
renderer swappable, makes charts impossible to fabricate, and means the whole feature works on
a CPU with no API key.

| Agent | Model returns | Renderer | Size from |
|---|---|---|---|
| `marketing.post-image` | `{headline, subline, badge, cta, palette, layout, alt_text}` | Pillow card renderer | agent profile → platform |
| `marketing.ad-creative` | same shape, offer/CTA oriented | Pillow card renderer | agent profile → ad size |
| `creative.poster-image` | same shape, poster oriented | Pillow card renderer | agent profile → size + mood |
| `analytics.chart-builder` | `{chart_type, title, x_label, y_label, labels, series[], note}` | matplotlib | fixed 1200×700 |

* The card renderer uses the **brand colours from the domain profile**, wraps the headline to
  fit, and stamps the logo text from the agent profile.
* The chart agent runs at temperature `0.1` and is told every number must come from the user's
  message or attachment. Given no data it returns `{"error": …}` and the reply says what to
  paste — it never invents a series.
* Each rendered file is recorded on the message in `media[]` with `url`, `width`, `height`,
  `bytes`, `alt_text`, `renderer` and the `spec` it came from, so the UI can show the image,
  its alt text and a download link, and history reloads it unchanged.
* Files are served by `GET /api/media/{filename}`, which is intentionally **unauthenticated** so
  `<img src>` works without a bearer token. Filenames carry a random component and no user data,
  and path traversal is refused. Put the endpoint behind signed URLs if you need stricter
  control.

For photographic output instead of typographic cards, set `IMAGE_PROVIDER=openai` — the same
JSON spec becomes a prompt for `gpt-image-1` and nothing else changes.

### Similarity thresholds are model-specific

`MEMORY_MIN_SIMILARITY` is a cosine floor, and different embedders occupy
different ranges. Measured on this project:

| Pair | Hashing embedder | `nomic-embed-text` |
|---|---|---|
| "Wants posts more concise" ↔ "Write a LinkedIn post about cutting cloud costs" | 0.04 | **0.52** |
| "Wants posts more concise" ↔ "What is the capital of France" | ~0.00 | 0.33 |

`nomic-embed-text` never scores near zero, so a `0.25` floor would match
everything. Use **0.45** for it and **0.25** for the hashing embedder. If recall
feels noisy, raise it; if learned preferences stop being applied, lower it.

### Switching embedders invalidates stored vectors

Embeddings from different models are not comparable. After changing
`EMBEDDING_PROVIDER`, the embedding model, or `EMBEDDING_DIM`:

```bash
python scripts/reembed_memories.py --dry-run   # reports how many are stale
python scripts/reembed_memories.py
```

On PostgreSQL, changing `EMBEDDING_DIM` also changes the `vector(N)` column
width, so generate an Alembic migration for the new width first. `/health` warns
when the configured width does not match the model's native output.

### Adding another provider

Implement `BaseLLMProvider` in `backend/app/llm/`, register it in
`_LLM_FACTORIES` in `app/llm/registry.py`, and set `LLM_PROVIDER`. Implement
`stream()` to get token streaming; skip it and the default single-chunk
implementation is used. Nothing else in the codebase references a provider.

### About `LLM_PROVIDER=mock`

The fallback is a **local development provider**
(`app/llm/local_provider.py`) so the whole stack — routing, profiles, memory
retrieval, persistence, feedback, UI — runs with no model installed at all. It
composes from the same personalization payload a real model receives, which
makes the profile/memory pipeline visible end to end. It is a provider selected
by configuration, not a hardcoded response table: output is tagged
`provider: "local-dev"` and the UI shows a **"Local dev provider"** badge. Use a
real provider for real answers.

### Where the time actually goes

On CPU-only hardware the prompt is evaluated at roughly **16 tokens/second** while
output is generated at **~5 tokens/second** (`llama3.2:3b`, Intel i5-10210U, no
GPU). So latency is driven by *prompt size* as much as reply length, and the
largest part of the prompt is usually replayed conversation history — not the
message you typed.

`scripts/measure_prompt.py` prints the breakdown without calling the model:

```bash
python scripts/measure_prompt.py "hi" --agent technical
```

A two-character `"hi"` sent into a conversation holding two long code-heavy
answers measured like this before tuning:

| Component | Tokens | Share |
|---|---|---|
| system prompt | 486 | 23% |
| personalization context | 120 | 6% |
| **short-term history** | **1466** | **71%** |
| the message itself | 0 | 0% |
| **total** | **2073** | → ~130s prompt eval + up to 127s generation |

Three changes addressed it:

1. **The history window is bounded by characters, not just message count**
   (`SHORT_TERM_MAX_CHARS`, `SHORT_TERM_MESSAGE_MAX_CHARS`). Long turns keep their
   head and tail with the middle elided, since the opening states the topic and
   the ending holds the conclusion.
2. **Greetings are detected and given a minimal turn** — no agent profile, no
   memories, no topic trail, a compact system prompt and a small reply budget.
   This was also a *correctness* fix: with no real question, the model was
   latching onto the `Recent topics with this agent` trail and re-answering the
   previous question, and the stored `Code blocks: always` preference forced a
   code block into a "hello".
3. **The reply budget scales with the request** — 160 tokens for a greeting, 320
   for an explicit "in one sentence", the full `LLM_MAX_TOKENS` otherwise.

Measured after, same conversation:

| Message | Prompt tokens | Reply | Latency |
|---|---|---|---|
| `hi` | 205 | "Hello back! How can I assist you today, Demo User?" | ~7s |
| `thanks` | 229 | "You're welcome, Demo User. Is there something specific…" | **6.9s** |
| `What is a list comprehension?` | 1229 | full answer with a code example | 111s |

Real questions still receive the whole context (7 profile fields, 2 memories, 8
history messages); only trivial turns are stripped back.

### Keeping latency down

Both extra model calls per message are tunable:

| Variable | Default | Effect |
|---|---|---|
| `ROUTER_USE_LLM` | `true` | LLM intent classification when no agent is selected |
| `ROUTER_LLM_MIN_MARGIN` | `3.0` | Skip that call when keyword scores already have a clear winner. `0` = always ask the LLM |
| `MEMORY_LLM_EXTRACTION` | `false` | LLM memory extraction in addition to the rules |

With the defaults, an explicitly-selected agent costs exactly **one** model call
per message — and **zero** when the scope guard hands the request off. Across the
21 routing cases in `verify_pipeline.py`, keyword scoring alone picks the correct
agent out of all 34 every time, so the two-stage LLM router is a fallback for
genuinely ambiguous phrasing rather than the normal path.

## 6. Running the demo

```bash
# 1. Backend + frontend running (see §2), then optionally:
cd backend && python scripts/seed_demo.py
#    demo@example.com / DemoPass123
#    Education/Technical/Marketing/Analytics domain profiles + 4 agent profiles configured.
#    marketing.post-image is intentionally left UNCONFIGURED for the setup demo.
```

Then in the browser at http://localhost:5173:

1. **Sign up** (or log in with the seeded demo account).
2. **Dashboard — level 1** shows the 7 **domain** cards with agent counts, how many are set up,
   and a strip of the agents that produce images or charts.
3. Click **Marketing** → **level 2** lists its 5 narrow agents. Each card states *"Does only
   this"* and shows a badge when it returns an image instead of text.
4. Click **Social Post Image Generator**. Nothing is configured → **two-step setup**:
   * **Step 1 (shared)** — brand name *Acme Cloud*, industry *SaaS*, audience *Developers,
     Founders*, tone *Professional*, brand colours `#4F46E5, #0F172A`.
   * **Step 2 (this agent only)** — platform *LinkedIn*, style *Bold type*, logo text
     *ACME CLOUD*.
5. Ask: **"Create a LinkedIn post image about cutting cloud costs with automation."**
   You get a **1200×627 PNG** in your brand colours with a download link and its alt text —
   not a paragraph of copy.
6. Go back to Marketing and open **Social Caption Writer**. Setup asks only *its* two questions;
   the brand answers are reused. This is the point of the split.
7. Open **Analytics → Chart Builder** and paste **"Jan 120, Feb 150, Mar 180, Apr 165,
   May 210"** → a rendered chart of exactly those numbers. Ask it for "a chart of something
   interesting" instead and it refuses rather than inventing data.
8. Open **Education → Class 10 Maths Tutor** and ask **"Explain Python decorators"** →
   an immediate **handoff** card with a *Switch to Python Engineer* button, and no model call.
9. Ask it a real question (**"find the roots of x² − 5x + 6 = 0"**). The right panel shows all
   three profile levels, the memories used with their scope, and the real system prompt.
10. Click **👎 / "Tell it what to change"** → *"Keep the working more concise."* A toast confirms
    the new memory; one event deliberately does **not** rewrite the profile. Repeat it once more
    and the global profile flips to `preferred_response_length: concise`.
11. Switch to **Technical → Python Engineer**. The maths-scoped memory is nowhere in its
    context — scope isolation is per agent, with domain-wide and global memories still shared.
12. Type a request with **no agent selected** (e.g. *"Why does my LEFT JOIN return duplicate
    rows?"*) — the router picks `technical.sql` and the badge on the reply says how.

### Scripted verification

```bash
cd backend

# 163 assertions across the whole journey: catalog shape, two-level browse, two-step
# setup, text chat, scope handoff, IMAGE generation (asserting the PNG on disk and over
# HTTP), CHART generation from pasted data, router accuracy over all 34 agents, feedback
# promotion, memory scope isolation, streaming, history, attachments, tenant isolation.
DATABASE_URL=sqlite:////tmp/verify.db LLM_PROVIDER=mock python scripts/verify_pipeline.py

# Every one of the 34 agents, asserting each produced its DECLARED deliverable
python scripts/smoke_all_agents.py            # --domain marketing | --visual-only | --quiet

# Against an ALREADY RUNNING server and the real model
python scripts/live_check.py                  # --only image,chart,scope,text,memory

# Migration 0001 → head → 0001, with legacy rows, plus `alembic check`
python scripts/check_migration.py

# What the prompt actually costs, without calling the model
python scripts/measure_prompt.py "hi" --agent education.class10-maths
python scripts/measure_prompt.py "hi" --all

# After changing the embedding provider / model / dimension
python scripts/reembed_memories.py --dry-run
python scripts/reembed_memories.py
```

The suites are provider-agnostic. `LLM_PROVIDER=mock` is fast and deterministic for CI;
`LLM_PROVIDER=ollama` exercises the real model, the two-stage LLM router and real embeddings.

---

## 7. How personalization works

### The request pipeline (LangGraph)

`backend/app/agents/graph.py` compiles this graph; `GET /api/chat/pipeline` returns the live
node list.

```
load_user → router → scope_guard → load_global_profile → load_domain_profile
          → load_agent_profile → retrieve_memory → build_context
          → generate_response → store_message → END
```

`process_feedback` is a second compiled graph (`app/agents/feedback_graph.py`) triggered by
`POST /api/feedback`. The streaming endpoint reuses the *same* node functions
(`prepare_chat_turn` / `finalize_chat_turn`), so there is exactly one implementation of each
step rather than a streaming copy that can drift.

### Router Agent

`app/agents/router.py`, in priority order:

1. **Explicit UI selection always wins.**
2. **Keyword/phrase scoring across all 34 agents.** When one agent clears
   `ROUTER_KEYWORD_MIN_SCORE` *and* beats the runner-up by `ROUTER_LLM_MIN_MARGIN`, that is the
   answer — no model call at all.
3. **Two-stage LLM classification**: first the domain (7 options), then the agent inside that
   domain (4–6 options). A single 34-way classification is not reliable from a 3B model; two
   small decisions are.
4. The best keyword match, then the conversation's existing agent, then the Concept Explainer as
   the final default.

Every response carries the decision (`agent_key`, `domain`, `source`, `confidence`, `reason`,
per-agent scores).

### Scope guard

`app/agents/scope.py` runs straight after routing, and only when the user chose the agent
themselves. It scores the request against the selected agent and against every other agent
using the same scoring function the router uses. On a handoff, `generate_response` returns the
redirect text directly — `provider` is recorded as `scope-guard` and no tokens are spent. See
§4 for the four thresholds.

### Personalization engine

`app/services/personalization.py` assembles, per request, most general first:

1. **global** profile → an output contract (length, style, assumed skill, language)
2. **domain** profile → the answers shared by every agent in the domain
3. **agent** profile → the narrow specifics of this one job
4. short-term memory — the last `SHORT_TERM_WINDOW` turns of this conversation
5. long-term memory — hybrid retrieval (below), scoped agent ▸ domain ▸ global
6. the current request plus any attachment text

The response returns each level separately (`global_profile_summary`,
`domain_profile_summary`, `agent_profile_summary`) so the UI can show which level supplied what.

### Memory system

* **Selective capture.** Messages are never stored wholesale as memory. A turn only produces a
  memory when it contains a durable signal — a stated preference, a recurring interest, a hard
  requirement, or a correction given as feedback (`app/memory/extractor.py`: deterministic
  rules always, plus LLM-assisted extraction when a real provider is configured).
* **Reinforcement, not duplication.** A near-duplicate (cosine ≥ `MEMORY_DEDUPE_SIMILARITY`)
  increments `occurrences` and raises `importance` instead of inserting a row. Repeated
  behaviour therefore outranks a one-off remark.
* **Hybrid retrieval.** Semantic recall (pgvector cosine) *plus* pinned **standing
  preferences**. Semantic-only retrieval would silently stop applying "keep posts concise" the
  moment the user changed subject, so durable instructions are pinned for their agent
  regardless of topical similarity and marked `STANDING` in the prompt.
* **Three scopes.** A memory attached to `agent_key` reaches only that agent; one attached to
  `domain` reaches every agent in the domain; one with neither is global. A request retrieves
  all three of its applicable scopes and nothing else, so a Class 10 Maths preference never
  leaks into the Python Engineer's prompt. Each memory's scope is shown in the UI.
* **Bounded.** `MEMORY_MAX_PER_AGENT` caps the set; the least important/least used are pruned.

### Feedback loop

A comment becomes a memory immediately, so the *next* request already benefits. A **structural
profile change** only happens once the same signal has been observed
`FEEDBACK_PROMOTION_THRESHOLD` times (default 2), counting both matching feedback comments and
the reinforcement counter on memories. A bare thumbs-down with no text is recorded but never
acted on directly. Everything the system changed is returned in the response and stored in
`feedback.outcome`.

---

## 8. API documentation

Interactive: **http://localhost:8000/docs** · OpenAPI JSON: `/openapi.json`

All routes are prefixed `/api`. Every route except `/auth/register`, `/auth/login`, `/health`
and `/` requires `Authorization: Bearer <token>`.

### Auth

| Method | Path | Body / params | Returns |
|---|---|---|---|
| `POST` | `/auth/register` | `{name, email, password}` | `201` `{access_token, token_type, expires_in, user}` |
| `POST` | `/auth/login` | `{email, password}` | `{access_token, …, user}` |
| `GET` | `/auth/me` | — | current user |
| `POST` | `/auth/change-password` | `{current_password, new_password}` | user |

Passwords: min 8 chars, at least one letter and one number. Duplicate email → `409`.

Agents are addressed by their full key, `<domain>.<slug>` — e.g. `marketing.post-image`.
An unknown domain or agent key returns `404` with the valid options in the detail.

### Catalog

| Method | Path | Notes |
|---|---|---|
| `GET` | `/catalog` | Unauthenticated shape of the catalog: counts per domain, output-kind tally, the visual agents |
| `GET` | `/domains` | Level 1: the 7 domain cards with this user's counts and setup status |
| `GET` | `/domains/{domain}` | One domain card |
| `GET` | `/domains/{domain}/agents` | Level 2: the agents inside that domain |
| `GET` | `/agents` | All 34 across every domain (search, sidebar) |
| `GET` | `/agents/{agent_key}` | Everything the chat and setup screens need: `scope`, `out_of_scope`, `examples`, `output_kind`, **both** setup forms (`profile_fields` + `domain_profile_fields`), saved data for each, and `needs_setup` |

### Profiles (three levels)

| Method | Path | Notes |
|---|---|---|
| `GET` | `/profile/global` | Creates the profile on first read |
| `PUT` | `/profile/global` | Full replace of the mutable fields |
| `GET` | `/profile/overview` | Global + every domain slot + every agent slot in one call |
| `GET` | `/profile/domain/{domain}` | The shared domain profile, or `null` |
| `PUT` | `/profile/domain/{domain}` | Create or update it — `{profile_data: {…}}` |
| `GET` | `/profile/agent/{agent_key}` | `{needs_setup, agent_configured, domain_configured, missing_agent_fields, missing_domain_fields, agent_profile, domain_profile}` — drives the two-step setup |
| `PUT` | `/profile/agent/{agent_key}` | Create or replace this agent's own profile |
| `PATCH` | `/profile/agent/{agent_key}` | Merge only the supplied keys |

`profile_data` is validated against the declared field keys of that domain or agent and coerced
to the declared kind, so arbitrary payloads cannot be injected into the JSONB column.

### Chat

| Method | Path | Notes |
|---|---|---|
| `POST` | `/chat` | `{message, conversation_id?, agent_key?, attachment_name?, attachment_text?}` |
| `POST` | `/chat/stream` | Same body and pipeline, streamed as SSE (`meta` → `status`? → `delta`* → `done`). Used by the UI |
| `POST` | `/chat/upload` | multipart `file` — extracts text (≤1 MB; `.txt .md .csv .json .tsv .log .py .sql .yaml .yml`), does not persist it |
| `GET` | `/chat/pipeline` | Live LangGraph node list + active providers + renderers |

`POST /chat` response (an image agent shown):

```jsonc
{
  "conversation_id": "…", "conversation_title": "Create a LinkedIn post image…",
  "user_message": { … },
  "assistant_message": {
    "content": "**Simplify Your Cloud Costs, Amplify Your Productivity**\n…",
    "agent_key": "marketing.post-image",
    "output_kind": "image",
    "media": [{
      "filename": "post-image-1789926561-9a9fa10b.png",
      "url": "/api/media/post-image-1789926561-9a9fa10b.png",
      "media_type": "image", "mime_type": "image/png",
      "width": 1200, "height": 627, "bytes": 60439,
      "alt_text": "A stylized illustration of …",
      "renderer": "local-card",
      "spec": { "headline": "…", "palette": "brand", "layout": "left" }
    }],
    "meta": { "out_of_scope": false, "suggested_agent": null, "incomplete_reason": null, … }
  },
  "routing": { "agent_key": "marketing.post-image", "domain": "marketing",
               "agent_name": "Social Post Image Generator", "source": "explicit",
               "confidence": 1.0, "reason": "…", "candidates": { … } },
  "scope": { "in_scope": true, "reason": "Within this agent's scope.",
             "suggested_agent_key": null, "suggested_agent_name": null },
  "personalization": {
    "agent_key": "marketing.post-image", "domain": "marketing", "output_kind": "image",
    "global_profile_summary": ["…"], "domain_profile_summary": ["…"],
    "agent_profile_summary": ["…"],
    "memories_used": [{ "content": "…", "scope": "marketing", "similarity": 0.41,
                        "pinned": true, "occurrences": 2, "kind": "preference" }],
    "short_term_messages": 4, "context_characters": 1928,
    "system_prompt_preview": "=== YOUR SCOPE (do not exceed it) === …",
    "provider": "ollama", "model": "llama3.2:3b"
  },
  "new_memories": [], "latency_ms": 43900
}
```

On a handoff, `scope.in_scope` is `false`, `scope.suggested_agent_key` names the owner, and the
message metadata records `out_of_scope: true` with `provider: "scope-guard"`.

`502` is returned when the model provider is unreachable, so provider failures are never
disguised as content.

### Media

| Method | Path | Notes |
|---|---|---|
| `GET` | `/media/{filename}` | Serves a generated PNG. **Unauthenticated by design** so `<img src>` works; unguessable filenames, traversal refused, `Cache-Control: public, max-age=86400` |

### Conversations

| Method | Path | Notes |
|---|---|---|
| `GET` | `/conversations` | `?agent_key= &domain= &search= &include_archived= &limit= &offset=` |
| `POST` | `/conversations` | `{agent_key, title?}` |
| `GET` | `/conversations/{id}` | Full message list, each with `output_kind`, `media[]` and its `feedback_rating` |
| `PATCH` | `/conversations/{id}` | `{title?, is_archived?}` — rename / archive |
| `DELETE` | `/conversations/{id}` | `204`; cascades to messages |

### Feedback

| Method | Path | Notes |
|---|---|---|
| `POST` | `/feedback` | `{message_id, rating: 1 \| -1, feedback_text?}` → `{feedback, memories_created, profile_updated, profile_changes, message}` |
| `GET` | `/feedback` | `?agent_key= &domain= &limit=` |

### Memory

| Method | Path | Notes |
|---|---|---|
| `GET` | `/memory` | `?agent_key= &domain= &kind= &limit= &offset=` (`agent_key=global` for unscoped only) |
| `GET` | `/memory/summary` | Totals by agent, by domain and by kind + the most relevant entries |
| `GET` | `/memory/search` | `?q= &agent_key= &domain= &limit=` — the same hybrid retrieval the pipeline uses |
| `POST` | `/memory` | Teach something explicitly: `{content, agent_key?, domain?, kind?, importance?}`. Supplying `agent_key` fills `domain` automatically |
| `DELETE` | `/memory/{id}` | `204` |

### Dashboard & meta

| Method | Path |
|---|---|
| `GET` | `/dashboard/stats` (conversations, messages, memories, configured agents/domains, **images_generated**, feedback counts) |
| `GET` | `/health` (unauthenticated: DB dialect, vector store, provider status) |

---

## 9. Security

* **bcrypt** password hashing (configurable cost, 72-byte-safe); hashes never leave the DB.
* **JWT** bearer tokens with `exp`, `iat`, `jti` and a `type` claim; expiry and signature are
  verified on every request. A `401` from any route signs the UI out cleanly.
* **Every** route except register/login/health is behind the `get_current_user` dependency.
* **Tenant isolation** is enforced in the query layer — every read is scoped by `user_id`, so
  another account's conversation returns `404`, not `403`. Covered by tests.
* **Input validation** with Pydantic v2 everywhere; agent `profile_data` is whitelisted
  against the declared field keys; upload size, extension and decodability are checked.
* **CORS** restricted to configured origins with an explicit method/header allowlist.
* **Secrets** come only from the environment. `.env` is git-ignored; `.env.example` files hold
  placeholders. No AWS credential or model id is sent to the browser.
* **SQL injection**: all queries go through SQLAlchemy; the one raw statement (the pgvector
  cosine search) is fully parameterised.
* Frontend dependency audit: **0 vulnerabilities**.

Before deploying: set a strong `JWT_SECRET_KEY`, set `APP_ENV=production` and `DEBUG=false`,
restrict `CORS_ORIGINS`, terminate TLS at the proxy, and prefer an instance/task role over
static AWS keys.

---

## 10. Project structure

```
.
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── definitions/  7 domain modules declaring all 34 AgentSpecs
│   │   │   ├── schema.py     DomainSpec · AgentSpec · ProfileField · OutputKind
│   │   │   ├── catalog.py    assembly + lookup (get_agent_spec, list_agents, …)
│   │   │   ├── scoring.py    one scoring function, shared by router and scope guard
│   │   │   ├── scope.py      scope guard + handoff text + prompt contract
│   │   │   ├── runtime.py    TextAgent · ImageAgent · ChartAgent
│   │   │   ├── router.py     explicit ▸ keyword ▸ two-stage LLM ▸ default
│   │   │   └── graph.py      10-node chat graph (+ feedback_graph.py)
│   │   ├── api/             deps (auth + key validation) + routes/
│   │   ├── core/            config · security (JWT/bcrypt) · logging · request_hints
│   │   ├── database/        base · session · portable JSONB/vector types
│   │   ├── llm/             base protocols · ollama · openai_compatible · bedrock
│   │   │                    · local_provider · embeddings · registry
│   │   ├── media/           storage · fonts · card_renderer (Pillow)
│   │   │                    · chart_renderer (matplotlib) · openai_images
│   │   ├── memory/          extractor · service · vector_store (pgvector + portable)
│   │   ├── models/          users · global/domain/agent profiles · conversations
│   │   │                    · memories · feedback
│   │   ├── schemas/         pydantic request/response models
│   │   ├── services/        personalization engine · profiles · catalog · conversations
│   │   │                    · feedback
│   │   └── main.py
│   ├── alembic/             env.py + 0001_initial_schema · 0002_domain_agent_split
│   ├── scripts/             seed_demo · verify_pipeline · live_check · smoke_all_agents
│   │                        · check_migration · measure_prompt · reembed_memories
│   ├── generated_media/     rendered PNGs (git-ignored, pruned to MEDIA_MAX_FILES)
│   ├── requirements.txt · Dockerfile · alembic.ini · .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/      Sidebar · ChatMessage (+ media, handoff) · PersonalizationPanel
│   │   │                    · AgentProfileForm · Markdown · Modal · ui
│   │   ├── context/         Auth · Theme · Toast
│   │   ├── hooks/           useAppData (domains + agents + conversations)
│   │   ├── layouts/         AppLayout (sidebar + shell)
│   │   ├── pages/           Auth · Dashboard (domains) · Domain (agents) · AgentSetup
│   │   │                    (2 steps) · Chat · Profile · Settings · NotFound
│   │   ├── services/        api.js (axios instance + endpoint wrappers + SSE reader)
│   │   └── utils/           agents (40 icons, accents, output kinds) · format
│   ├── scripts/check-jsx-refs.mjs   (gate: every JSX component is imported)
│   ├── package.json · vite.config.js · tailwind.config.js · Dockerfile · .env.example
│
├── infra/init-pgvector.sql
├── docker-compose.yml · .env.example · .gitignore · README.md
```

### UI

Routes mirror the two levels: `/dashboard` → `/domain/:domain` → `/agent/:agentKey`
(`/agent/:agentKey/setup` for the two-step setup).

* **Left sidebar** — New chat, then the **catalog as a tree**: each domain collapses to show its
  agents, with a configured/not-configured dot and a small icon on the ones that return an image
  or chart. Below it, recent conversations grouped by day (each labelled with the agent that owns
  it) with inline rename/delete, plus Domains / Profiles / Settings and the user menu.
* **Dashboard** — domain cards with agent counts, how many are set up, and a strip linking
  straight to the visual agents.
* **Domain page** — the shared domain profile at the top (answer once, reused by all its agents),
  then a card per agent stating *"Does only this"* and two example requests.
* **Chat** — the agent's scope in the header, a *"Not this agent's job"* panel on the empty state,
  and for visual agents a status line instead of token streaming. Generated images and charts
  render inline at full width with their alt text, pixel size, a **Download** link and
  open-full-size. A handoff renders as an amber card with a **Switch to \<agent\>** button, so the
  user is redirected rather than refused.
* **Right panel** — this agent's job and what it hands off, then all **three** profile levels in
  the order the prompt uses them, the memories applied to the last reply (with scope, relevance
  and a `standing` marker), the routing decision, the scope verdict, the deliverable kind,
  context size, provider/model, and the *real* system prompt preview including the scope
  contract.
* **Profiles page** — global profile, then one expandable card per domain holding the shared
  answers and every agent's own profile beneath it.
* **Settings** — memory management with a single scope selector covering global, whole-domain and
  per-agent memories.
* Dark/light mode (persisted, no flash on load), responsive down to mobile with drawers,
  skeleton loaders, empty states, error states with retry, and toast notifications.
  Keyboard-focus rings, ARIA labelling and `prefers-reduced-motion` are respected.

---

## 11. Troubleshooting

| Symptom | Fix |
|---|---|
| `Cannot reach the API. Is the backend running?` | Start the backend; check `VITE_API_BASE_URL` matches its origin |
| CORS error in the browser console | Add the frontend origin to `CORS_ORIGINS` and restart, or set `VITE_API_BASE_URL=/api` to use the Vite proxy |
| `could not translate host name "postgres"` | You are outside Compose — use `localhost` in `DATABASE_URL` |
| `type "vector" does not exist` | `CREATE EXTENSION vector;` in the app database, or use the `pgvector/pgvector` image |
| `502 … language model provider is unavailable` | Bedrock model not enabled in the region, or credentials/role missing. Check `/health` |
| Memories stop matching after switching embedding provider | Vector spaces differ — delete or re-embed existing memories |
| `alembic check` reports drift | A model changed; generate a migration |
| Port already in use | `--port` for uvicorn, `FRONTEND_PORT` / `BACKEND_PORT` for Compose |
| `Cannot reach Ollama at …` | Start it: `ollama serve`. In Docker use `OLLAMA_BASE_URL=http://host.docker.internal:11434` or the `--profile ollama` service |
| `Ollama has no model named …` | `ollama pull <model>`. `/health` lists what is actually available |
| Replies take minutes | A CPU-only local model is slow. Use a smaller `OLLAMA_MODEL`, lower `LLM_MAX_TOKENS`, or switch to a hosted provider (§5). Responses stream, so text appears within seconds |
| Ollama reloads the model every request | Raise `OLLAMA_KEEP_ALIVE` (e.g. `30m`) |
| Memory retrieval returns nothing after switching embedders | Run `python scripts/reembed_memories.py` and check `MEMORY_MIN_SIMILARITY` for your model |
| Memory retrieval returns everything | `MEMORY_MIN_SIMILARITY` is too low for your embedder — try `0.45` for `nomic-embed-text` |
| Streaming shows nothing until the end | A proxy is buffering SSE. The UI falls back to `POST /chat` automatically; to fix it properly disable buffering (`X-Accel-Buffering: no` is already sent) |
| Model ignores "in one sentence" | Handled in code: conflicting profile directives are suppressed and stray code blocks stripped. If you see it anyway, the model is very small — try `llama3.2:3b` or larger |
| An agent answered something outside its job | The scope guard is deliberately conservative and only runs for an explicitly selected agent. Lower `SCOPE_OTHER_MIN_SCORE` / `SCOPE_MIN_MARGIN` to hand off more eagerly |
| It handed off when it should have answered | The opposite knobs: raise `SCOPE_OWN_MAX_SCORE`, or add the phrasing you used to that agent's `keywords` in `app/agents/definitions/` |
| An image agent returned prose instead of a file | The model did not emit usable JSON. The runtime falls back to the request text as the headline and still renders; a slightly larger model fixes the copy quality |
| Broken image icon in the chat | The file was pruned by `MEDIA_MAX_FILES`, or `MEDIA_ROOT` is not writable. The UI says so explicitly; ask again to regenerate |
| Chart says "I need data before I can plot anything" | Working as intended — paste label/value pairs (`Jan 120, Feb 150`) or attach a CSV. It will not invent numbers |
| `Unknown agent 'marketing'` | Agent keys are two-level now: use `marketing.post-image`. `GET /api/agents` lists them all |

### Verified on this machine

Python 3.14.4, Node 20.20.2, SQLite fallback, Intel i5-10210U with **no GPU**.

| Check | Result |
|---|---|
| `verify_pipeline.py` with `LLM_PROVIDER=mock` | **163/163 passed** |
| `smoke_all_agents.py` — every agent produced its declared deliverable | **34/34** (30 text, 3 image, 1 chart) |
| `live_check.py` against a running server + `ollama/llama3.2:3b` | **all steps passed** (catalog, setup, image, chart, text, scope, memory, dashboard) |
| Router accuracy over the 34-agent catalog | **21/21** by keyword scoring, no model call |
| Real-model image generation | 43.9s → 1200×627 PNG, 60 439 bytes, model-written headline, brand colours applied |
| Real-model chart generation | 53.5s → PNG plotting exactly `120, 150, 180, 165, 210`; refuses when given no data |
| Scope handoff (`class10-maths` ← a Python question) | **0.0s**, `provider=scope-guard`, suggested `technical.python` |
| Memory scope isolation | an agent-scoped memory is found for its own agent, 0 results for another |
| `check_migration.py` — 0001 → head → 0001 with legacy rows | **45/45 passed**, `alembic check` clean |
| `alembic upgrade head` on a fresh DB + `alembic check` | clean (8 tables, stamped `0002_domain_agent`) |
| `GET /api/media/{file}` direct and through the Vite proxy | `200 image/png`, identical bytes |
| `npm run check` / `npm run build` | 26 files, every JSX component imported / build succeeds |

Generation speed on this CPU is ~5 tokens/second with `llama3.2:3b`, so a long
text answer takes 1–2 minutes end to end. Streaming makes that usable; the visual
agents are faster because their JSON spec is short. A GPU or a hosted provider
removes the limit.

**Not verified here:** the Docker/PostgreSQL + pgvector path. The compose file and
migrations are written for it and `docker compose config` validates, but no Docker
daemon is available in this environment, so it was never executed. The same applies
to `IMAGE_PROVIDER=openai` — the renderer is implemented and selected by config,
but there is no API key here to call `gpt-image-1` with.

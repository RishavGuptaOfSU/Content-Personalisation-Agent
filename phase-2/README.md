# Phase 2 — Marketing Agents

A single-domain, deeply personalised marketing agent platform. **Five agents, one
deliverable each**, sharing one brand profile:

| Agent | Key | Hands back | Setup asks |
|---|---|---|---|
| Social Post Image Generator | `marketing.post-image` | **a rendered PNG** | platform, visual style, logo text |
| Ad Creative Generator | `marketing.ad-creative` | **a rendered PNG** | objective, ad size |
| Social Caption Writer | `marketing.social-copy` | text | platforms, length, hashtags |
| SEO Optimizer | `marketing.seo-optimizer` | text | content type, region |
| Campaign Planner | `marketing.campaign-planner` | text | goal, channels, budget |

Each agent does exactly one job and **refuses the others**, naming the agent that
owns the request instead — so you never get a caption out of the image generator.

Phase 1 (seven domains, 34 agents) is preserved unchanged in [`../phase-1/`](../phase-1/README.md).
Phase 2 narrows to one vertical and goes deeper on it.

```
USER → LOGIN → AGENTS ─────────────────────────→ SELECT AGENT
                  │                                   ↓
                  │              brand answered? ──no──→ STEP 1: BRAND (shared)
                  │                    │yes                      ↓
                  │              agent answered? ──no──→ STEP 2: AGENT (this job only)
                  │                    │yes                      │
                  └──────────────→ LOAD 3 LEVELS ←────────────────┘
                                        ↓
                     ROUTER → SCOPE GUARD → PERSONALIZATION → AGENT
                                  │                             ↓
                        out of scope? → HANDOFF          text │ image
                                                                ↓
                                     FEEDBACK → MEMORY / PROFILE UPDATE
```

---

## 1. Quick start

```bash
# backend
cd phase-2/backend
python -m venv .venv && source .venv/bin/activate     # or: uv venv .venv
pip install -r requirements.txt                       # or: uv pip install -r requirements.txt
cp .env.example .env                                  # edit JWT_SECRET_KEY before any real use
alembic upgrade head
python scripts/seed_demo.py                           # optional demo account
uvicorn app.main:app --reload --port 8000

# frontend (second terminal)
cd phase-2/frontend
npm install
cp .env.example .env
npm run dev                                           # http://localhost:5173
```

Demo login: `demo@example.com` / `DemoPass123`. The seed configures the brand
profile plus three agents and deliberately leaves **post-image** and
**ad-creative** unconfigured so you can walk the two-step setup.

For real answers you need a model. Three options, in order of how well they work:

**Ollama Cloud (recommended).** Open models on Ollama's infrastructure, reached
through the OpenAI-compatible endpoint, so no new provider code is needed. Get a
key at [ollama.com/settings/keys](https://ollama.com/settings/keys):

```ini
LLM_PROVIDER=openai
OPENAI_BASE_URL=https://ollama.com/v1
OPENAI_API_KEY=<your key>
OPENAI_MODEL=gemma4:31b          # name from /api/tags, NOT the CLI's ":cloud" form
OPENAI_ROUTER_MODEL=gemma4:31b
OPENAI_TIMEOUT=180
```

Keep embeddings **local** (`EMBEDDING_PROVIDER=ollama` + `nomic-embed-text`):
they are cheap and fast on CPU, and changing them forces a re-embed of stored
memories. That means `ollama serve` still has to be running even when chat is in
the cloud — if it is not, memory retrieval fails and the API returns `502`.

List the available cloud models with `curl https://ollama.com/v1/models`.

**Local Ollama**, free and private but slow on CPU:

```bash
ollama serve
ollama pull llama3.2:3b          # chat
ollama pull nomic-embed-text     # embeddings for memory
```

**No model at all** — set `LLM_PROVIDER=mock` and the whole stack still runs on a
deterministic local composer, which is how the fast test suite works.

---

## 2. How personalization works

### Three levels, most general first

1. **Global profile** — your name, tone, preferred length, skill level, language.
2. **Brand profile** — brand name, industry, audience, brand tone, brand colours,
   never-use list. Answered **once**, reused by all five agents. The image agents
   render with these colours; every caption inherits this tone.
3. **Agent profile** — the narrow specifics of one job (platform and visual style
   for post images; objective and size for ads; channels and budget for campaigns).

Setup is two steps, and step 1 is skipped once the brand is answered — so the
second agent you configure only sees its own questions. The response returns each
level separately, and the UI shows which level supplied what.

### Memory has three scopes

A memory attached to an `agent_key` reaches only that agent; attached to the
brand it reaches all five; with neither it is global. A request retrieves only
its three applicable scopes, so "always end captions with a question" never
leaks into the SEO agent's prompt.

Capture is selective — turns are never stored wholesale. A near-duplicate
reinforces an existing memory (raising `occurrences` and `importance`) instead of
inserting a new row, so repeated behaviour outranks a one-off remark. Retrieval
is semantic recall **plus** pinned standing preferences, because semantic-only
recall would stop applying "keep posts under 100 words" the moment the topic
changed.

### Feedback

A thumbs-down with a comment becomes a memory immediately, so the next request
already benefits. A structural **profile** change only happens after the same
signal is seen `FEEDBACK_PROMOTION_THRESHOLD` times (default 2). A bare
thumbs-down with no text is recorded but never acted on.

---

## 3. The image agents

Two of the five agents hand back a file. In both cases **the model never draws
anything** — it returns a short JSON design spec and a Pillow renderer produces
the PNG. That keeps the renderer swappable, works on a CPU with no API key, and
means the copy on the graphic is attributable to the model while the layout is
deterministic.

```jsonc
// what the model returns
{ "headline": "…", "subline": "…", "badge": "…", "cta": "…",
  "palette": "brand|dark|light|gradient", "layout": "centered|left|split",
  "alt_text": "…" }
```

* Brand colours come from the **brand** profile; dimensions and logo text from
  the **agent** profile.
* `ImageSpec.sanitized()` clamps every field and coerces unknown palette/layout
  values before anything is drawn.
* If the model fails to produce usable JSON the renderer still produces a file,
  using the request text as the headline — and the turn is flagged, because a
  silent fallback looks like a working image while actually being unpersonalised.
  The evaluation suite counts these.
* Files are served by `GET /api/media/{filename}`, intentionally
  **unauthenticated** so `<img src>` works without a bearer token. Filenames are
  unguessable and contain no user data; path traversal is refused.

Set `IMAGE_PROVIDER=openai` to route the same spec to `gpt-image-1` for
photographic output instead of a typographic card. The local path is the default
and always works.

> The local renderer produces **typographic cards** — brand-coloured layouts with
> wrapped, auto-fitted text. It does not produce photographs or illustrations.

---

## 4. Scope enforcement

Every prompt carries a scope contract naming what the agent does and what it must
refuse. Because a small local model does not reliably obey negative instructions,
that is backed by a deterministic **scope guard**: if the selected agent has
essentially no evidence that the request is its job, *and* another agent clearly
owns it, the reply is a handoff — with **zero model calls**.

```
You → Social Caption Writer: "Create the post image graphic for our launch"
      → "That is outside what I do… Social Post Image Generator handles this."
         [0.0s, provider=scope-guard]
```

Scope is judged on **task evidence only**. A match on the agent's own *name* does
not count — "write the caption for our launch **post**" contains the post-image
agent's name word but is plainly a caption request. The router still uses the
full score, where a name match is useful signal.

The guard only runs when you picked the agent yourself (a routed request is in
scope by construction) and is deliberately conservative — a wrong handoff is
worse than a slightly off-topic answer. Four thresholds, all of which must hold:

| Variable | Default | Meaning |
|---|---|---|
| `SCOPE_MIN_REQUEST_CHARS` | `15` | Shorter requests are never handed off |
| `SCOPE_OWN_MAX_SCORE` | `1.5` | The selected agent's task score must be at or below this |
| `SCOPE_OTHER_MIN_SCORE` | `4.0` | Another agent must score at least this |
| `SCOPE_MIN_MARGIN` | `3.0` | And beat the selected agent by this much |

---

## 5. Evaluation

Quality claims need evidence, so the suite is split in two.

```bash
cd phase-2/backend

# Deterministic: seconds. Routing, scope, output kinds, media geometry, whether
# the image spec came from the model, hashtag counts, length bounds, whether the
# profile and memories reached the prompt, and no-fabrication substring checks.
DATABASE_URL=sqlite:////tmp/eval.db LLM_PROVIDER=mock \
  python scripts/marketing_eval/harness.py --label deterministic

# Real model: minutes. The same dataset, plus the cases whose assertions only
# mean something when a real model is answering.
python scripts/marketing_eval/harness.py --label baseline

python scripts/marketing_eval/harness.py --agent social-copy   # one agent
python scripts/marketing_eval/harness.py --category grounding  # one concern
python scripts/marketing_eval/harness.py --no-generate         # no model calls
```

* The dataset is **data**, not code: `scripts/marketing_eval/cases.toml`
  (stdlib `tomllib`, no new dependency). 30 cases across 12 categories.
* Cases flagged `requires_real_model` are **skipped** under `LLM_PROVIDER=mock`
  rather than reported as failures — the local composer ignores agent
  instructions by construction, so running them would say nothing about prompt
  quality.
* Qualitative dimensions are **not** scored by the harness — string matching is
  not a measure of creative quality. It writes the real output into a markdown
  report beside the dimensions each case declares, and
  `scripts/marketing_eval/rubric.md` defines the 1–5 anchors. Those anchors are
  then applied either by reading the report, or by `judge.py` below.

### Qualitative scoring — `scripts/marketing_eval/judge.py`

An LLM judge applies the same `rubric.md` anchors to a report the harness
already wrote. No agent is re-run, so the scores describe exactly the outputs in
that file.

```bash
# Judge with a model that did NOT produce the output
python scripts/marketing_eval/judge.py CLOUD-gemma4-cases-fixed --model gpt-oss:120b

# Score each case three times to see how much the judge agrees with itself
python scripts/marketing_eval/judge.py <label> --model gpt-oss:120b --repeat 3
```

Writes `<report>.scores.json` and `<report>.scores.md` next to the report.

What keeps the numbers honest:

* `rubric.md` stays the **single source of truth**. `rubric.py` parses the same
  prose tables a human reads, so the judge and the reader cannot drift apart.
  `scripts/check_rubric.py` asserts every dimension a case declares exists, and
  every dimension defined is used by some case.
* **Self-preference is flagged loudly.** If the judge model is the model that
  produced the output, the terminal, the JSON and the markdown all say so.
  Models score their own work high; that reading is an upper bound, not a
  measurement.
* **Two dimensions are never scored by the model.** `legibility` and
  `brand_fit` are properties of the rendered pixels, and the judge only sees the
  image spec and alt text. They are reported as unjudged;
  `scripts/probe_renderer.py` already checks `legibility` deterministically
  across 27 layouts, which is stronger than an opinion.
* `--repeat N` takes the **median** as the score and reports the spread, so
  judge noise is visible rather than hidden. A single run claims no spread at
  all, because unknown is not the same as zero.
* The prompt is **versioned**. Scores from two prompt versions are not
  comparable and the version is recorded in both output files.
* Cost is reported only for models with a published rate; an unknown model
  reports tokens and no cost rather than a guess.
* `scripts/check_judge.py` exercises all of the above against a fake provider —
  77 checks, no model calls, no spend.
* Every report records the provider, model, temperature, token budget, embedding
  settings and scope thresholds, so two runs are only compared when they were
  produced the same way.

Other checks:

```bash
python scripts/verify_pipeline.py        # 140 end-to-end assertions over real HTTP
python scripts/smoke_all_agents.py       # every agent produced its declared deliverable
python scripts/check_migration.py        # schema, round-trip, cascade, downgrade, drift
python scripts/probe_renderer.py         # layout geometry at every declared image size
python scripts/live_check.py             # against an already running server
python scripts/measure_prompt.py "hi" --all   # prompt cost without calling the model
cd ../frontend && npm run check && npm run build
```

---

## 6. Architecture

```
phase-2/backend/app/
  agents/
    definitions/marketing.py   the domain + all five AgentSpecs (data, not classes)
    schema.py                  DomainSpec · AgentSpec · ProfileField · OutputKind
    catalog.py                 assembly + lookup (unchanged from the multi-domain build)
    scoring.py                 one scoring function, shared by router and scope guard
    scope.py                   scope guard, handoff text, prompt contract
    runtime.py                 TextAgent · ImageAgent (one class per output kind)
    router.py                  explicit ▸ keyword ▸ LLM ▸ default
    graph.py                   the 10-node LangGraph chat pipeline
  api/      deps (auth + key validation) + routes
  core/     config · security · logging · request_hints
  database/ portable JSONB/vector types
  llm/      ollama · openai_compatible · bedrock · nemotron · local_provider · embeddings
  media/    storage · fonts · card_renderer (Pillow) · chart_renderer · openai_images
  memory/   extractor · service · vector_store
  models/   users · global/brand/agent profiles · conversations · memories · feedback
  services/ personalization · profiles · catalog · conversations · feedback
```

Agents are **declarative**. Adding one means adding an `AgentSpec` record — scope,
out-of-scope list, instructions, keywords, examples, profile fields, output kind —
not a new class. The runtime has one class per *output kind*, not per agent.

The catalog machinery still supports multiple domains; this build simply declares
one. `definitions/__init__.py` exports `PRIMARY_DOMAIN`, and the router skips
domain classification entirely when there is only one domain, saving a model call.

### Request pipeline

```
load_user → router → scope_guard → load_global_profile → load_domain_profile
          → load_agent_profile → retrieve_memory → build_context
          → generate_response → store_message → END
```

The streaming endpoint reuses the same node functions, so there is one
implementation of each step rather than a streaming copy that can drift.

### Database

Eight tables, one squashed migration. `brand` is stored as a domain profile, so
the schema is unchanged from the multi-domain build and a second domain could be
added without a migration.

```
users ──1:1── global_profiles
  ├──1:N── domain_profiles   (the brand profile; unique on user_id+domain)
  ├──1:N── agent_profiles    (unique on user_id+agent_key)
  ├──1:N── conversations ──1:N── messages ──1:N── feedback
  ├──1:N── memories          (scope = agent_key ▸ domain ▸ global)
  └──1:N── feedback
```

`messages` carries `output_kind` (`text`/`image`) and `media`, which is what lets
one conversation hold prose turns and rendered-image turns side by side.

### Carried but unused

`OutputKind.CHART`, `ChartAgent` and `media/chart_renderer.py` come from the
multi-domain build and no Phase 2 agent uses them. They are kept because
matplotlib is a required dependency regardless (`media/fonts.py` uses its bundled
DejaVu font) and campaign-performance charts are a plausible next agent.

---

## 7. Configuration

Full reference: [`backend/.env.example`](backend/.env.example).

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./marketing_agent.db` | PostgreSQL + pgvector supported, **not verified here** |
| `JWT_SECRET_KEY` | dev placeholder | **Change it.** `openssl rand -hex 48` |
| `LLM_PROVIDER` | `ollama` | `ollama` \| `openai` \| `bedrock` \| `nemotron` \| `mock` |
| `LLM_MAX_TOKENS` | `700` | Keep modest for a local CPU model |
| `EMBEDDING_PROVIDER` | `ollama` | Changing this invalidates stored vectors — run `reembed_memories.py` |
| `EMBEDDING_DIM` | `768` | Must match the embedding model's native width |
| `MEMORY_MIN_SIMILARITY` | `0.45` | Model-specific cosine floor; `0.25` for the hashing embedder |
| `IMAGE_PROVIDER` | `local` | `local` (Pillow, no key) \| `openai` (`gpt-image-1`) |
| `MEDIA_ROOT` | `generated_media` | Rendered PNGs; pruned to `MEDIA_MAX_FILES` |
| `SCOPE_*` | see §4 | Handoff sensitivity |

No provider credential ever reaches the browser — every model call is server-side.

---

## 8. Performance

Same hardware (Intel i5-10210U, 4 cores, **no GPU**), same code, same settings —
only the model differs:

| Operation | local `llama3.2:3b` | cloud `gemma4:31b` |
|---|---|---|
| Text agent (caption, SEO, campaign plan) | 28–53 s | **1.3–3.2 s** |
| Image agent (spec + render) | 28–64 s | **1.4–2.4 s** |
| Scope handoff | 0.0 s (no model call) | 0.0 s |
| Full 29-case evaluation run | **1325 s** (22 min) | **88 s** |

Locally, prompt evaluation dominates — roughly 16 tokens/sec in versus 5 out — so
latency tracks *prompt size* as much as reply length. `measure_prompt.py` prints
the breakdown without calling the model.

Replies stream either way, so text appears quickly; the image agents cannot
stream (a file has to exist before it can be sent) and emit a status event.

**Cost.** The 29-case run above consumed 18,449 input and 3,390 output tokens.
At `gemma4` published rates ($0.14 / $0.40 per million) that is **$0.0039** — about
250 full evaluation runs per US$1. Ollama's free plan includes a starter credit
allowance; beyond that it is pay-as-you-go, with off-peak discounts. For this
workload the cost is negligible and the 15× latency drop is the real gain,
because it turns the measure-fix-measure loop from a 22-minute wait into a
90-second one.

---

## 9. Security

* bcrypt password hashing; JWT bearer tokens with `exp`, `iat`, `jti`.
* Every route except register/login/health/media is behind the auth dependency.
* Tenant isolation is enforced in the query layer — another account's
  conversation returns `404`, not `403`. Covered by the suite.
* `profile_data` is whitelisted against the declared field keys of that brand or
  agent, so arbitrary payloads cannot reach the JSON column.
* Uploads are limited by extension and size (1 MB documents, 8 MB images),
  parsed in a `try` that never leaks a parser traceback, and never persisted —
  only the extracted text or base64 is returned to the client.
* `GET /api/media/{filename}` is unauthenticated by design (see §3).
* Secrets come only from the environment; `.env` is git-ignored.

Before deploying: set a strong `JWT_SECRET_KEY`, `APP_ENV=production`,
`DEBUG=false`, restrict `CORS_ORIGINS`, terminate TLS at the proxy, and put the
media endpoint behind signed URLs if the graphics are sensitive.

---

## 10. The grounding guard

Marketing copy invents numbers. Measured here with `llama3.2:3b`, asked to write
about customer savings with **no figure supplied** and explicitly instructed
never to fabricate metrics:

| Run | Agent | Invented |
|---|---|---|
| baseline | `social-copy` | "Unlocking Savings of **Up to $100K Per Year**" |
| after prompt fixes | `social-copy` | "reduce costs **by up to 50%**" |
| baseline | `ad-creative` | "**Save up to 80%** of your time" |
| after prompt fixes | `campaign-planner` | invented a **$250** budget from "Plan a campaign" |

Tightening the instructions did not stop it. This is the same failure mode as the
scope contract, so it got the same answer: `app/agents/grounding.py` checks
claim-shaped figures (percentages, currency, multipliers, "up to N") against the
figures that were actually available — the request, any attachment, and the
user's three profiles — and reports anything else.

It **does not rewrite copy.** Deleting a number mid-sentence produces nonsense
("reduce costs by up to"), and the user is the one who knows whether a claim is
true. It flags, in the message metadata and visibly in the reply:

> ⚠️ **Unverified figures:** `30%`. You did not supply these, so they are the
> model's invention — replace them with real numbers or cut them before publishing.

Which patterns are checked is declared per agent in the catalog
(`options["grounding_patterns"]`). `campaign-planner` additionally sets
`allow_budget_splits`, because dividing a budget the user *did* give is its job:
a correct `$200 + $100 + $100` split of a supplied `$400` is an allocation, not
an invention. Plain integers are never flagged — list numbering, week counts and
character counts are not claims.

---

## 11. Status

See [`docs/marketing-audit.md`](docs/marketing-audit.md) for the audit that drove
this phase, and `scripts/marketing_eval/reports/` for the recorded runs.

**Verified on this machine** (Python 3.14.4, Node 20, SQLite, Intel i5-10210U,
no GPU):

| Check | Result |
|---|---|
| `verify_pipeline.py` (mock) | **140/140** assertions |
| `live_check.py` against a running server + `ollama/llama3.2:3b` | **28/28** |
| Marketing eval, **Ollama Cloud `gemma4:31b`** | **110/110** assertions, 0 errors, 49s (30 cases) |
| Marketing eval, same model before the case fix | 108/108 assertions, 0 errors, 88s (29 cases), $0.0039 |
| Marketing eval, local `llama3.2:3b` | 105/108 assertions, 0 errors, 1325s |
| Marketing eval, deterministic (25 run, 5 held for a real model) | **96/96** |
| **Qualitative scores**, judge `gpt-oss:120b`, 3 repeats | **4.23 / 5** over 61 dimension scores, 77% judge unanimity |
| Free-model bake-off, 7 models judged by one fixed judge | `gemma4:31b` best per second; no per-agent pin justified |
| `check_agent_models.py` | **34/34** (per-agent model override) |
| `check_empty_reply_retry.py` | **24/24** (reasoning models returning empty replies) |
| `check_attachments.py` | **64/64** (PDF/DOCX extraction, image vision plumbing) |
| PDF + DOCX + PNG uploaded through the running stack | text extracted; `38%` read off a PNG by `gemma4:31b` |
| `check_rubric.py` | **164/164** (rubric parses, agrees with cases both ways) |
| `check_judge.py` | **77/77** (judge logic, no model calls) |
| `smoke_all_agents.py` | 5/5 agents produced their declared deliverable |
| `personalization_check.py` (structural; 4 generative held) | **18/18** |
| `check_grounding.py` | all pass (catches invented figures, accepts supplied ones and budget splits) |
| `check_styles.py` | all pass (4 styles → 3 distinct palettes) |
| `probe_renderer.py` | **27/27** size × payload combinations lay out correctly |
| `check_migration.py` | all pass, `alembic check` clean |
| Scope guard (6 handoffs + 8 correct stays) | **14/14** |
| `npm run check` / `npm run build` | pass |
| `ruff check --select F` | clean |

### Baseline → final, measured

Both runs used `ollama/llama3.2:3b` with identical settings
(`scripts/marketing_eval/compare.py` prints the configuration of each and refuses
to compare across providers).

| | baseline | final |
|---|---|---|
| assertions passed | 102/105 | **105/108** |
| errors | 0 | 0 |
| degraded image specs | 0 | 0 |
| routing: "write ad copy" | ad-creative (an **image** agent) | **social-copy**, by keyword, no model call |
| budget allocation of a supplied $400 | not asserted correctly | **$200+$150+$50 = $400** |
| invented figures | undetected | **detected and flagged** |
| latency, 21 generating cases | 1215s | 1322s (+9%, longer prompts) |

### Then: the same suite on Ollama Cloud

Everything above was `llama3.2:3b` on CPU. Switching only the model — same code,
same prompts, same thresholds — closed the remaining failures:

| | local `llama3.2:3b` | cloud `gemma4:31b` |
|---|---|---|
| assertions passed | 105/108 | **108/108** |
| `campaign-clarification` (asks, or states assumptions) | fails | **passes** — it asks |
| invented figures | `$100,000`, `20%`, `2%` flagged | **none to flag** |
| elapsed | 1325 s | **88 s** |
| cost | — | **$0.0039** |

That settles a question the local runs could not: the three stubborn failures
were a **model-capability limit, not a prompt problem**. No prompt change moved
them; a better model fixed all three.

It also exposed two **false positives in my own grounding guard**, which the
weaker model had never triggered:

- `3x per week` in a channel-mix table is a posting *cadence*, not a claim.
- `20% (suggested figure)` is a figure the planner **openly labelled as a
  proposal**, which its instructions explicitly ask for — flagging it punished
  compliance.

Both are fixed and covered by new cases in `check_grounding.py`, which now also
asserts the opposite direction: `10x faster` and an unlabelled `by 20%` are still
caught.

**Nothing is currently failing.** The caveat is that assertion counts measure
the deterministic half only. The qualitative half is below.

### Attachments: documents and images

`POST /api/chat/upload` takes two different kinds of file and treats them
differently, because a model does:

| | types | how it reaches the model |
|---|---|---|
| **documents** | `.pdf`, `.docx`, `.txt`, `.md`, `.csv`, `.json`, `.tsv`, `.log`, `.py`, `.sql`, `.yaml` | text-extracted server-side, appended to the prompt |
| **images** | `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif` | sent as vision input for the model to look at |

Extraction runs on the server, not in the browser. A text model can do nothing
with raw PDF bytes, and `latin-1` will cheerfully "decode" them into convincing
line noise — which is worse than an error, because it looks like it worked.
`pypdf` reads a PDF's text layer and `python-docx` reads paragraphs *and
tables*, since tables are where briefs keep their numbers.

There is no OCR. A scanned PDF has no text layer, so instead of returning an
empty attachment it says so and suggests uploading the page as a PNG. Encrypted
PDFs, `.doc` files and corrupt archives each get their own message.

#### Images only work on a model that can see

Measured on Ollama Cloud with a PNG containing the text "ACME CLOUD 42":
**`gemma4:31b` read it back correctly**, and `gpt-oss:120b`, `gpt-oss:20b`,
`beam`, `nemotron-3-super` and `nemotron-3-ultra` all returned *"this model does
not support image input"*. Since the default model is `gemma4:31b`, images work
out of the box.

An OpenAI-compatible API has no capability endpoint, so `app/llm/vision.py`
matches the model name against known multimodal families and `LLM_VISION`
overrides it either way (`auto` | `on` | `off`). The upload is refused **before**
the user writes a message around it — accepting a PNG and then quietly sending a
text-only request would produce a confident answer about a picture the model
never saw. `GET /api/chat/pipeline` reports what is accepted and whether vision
is live.

Each provider gets images in its own wire format: OpenAI takes `image_url`
content parts, Ollama takes a sibling `images` list of bare base64. Bedrock
flattens turns to text, so it **raises** rather than dropping the image
silently.

One consequence worth knowing: the grounding guard reads text, so a figure the
model copied off a screenshot is indistinguishable from one it invented. When an
image is attached the warning changes from "these are the model's invention" to
"this check cannot see images — confirm they were read correctly". Verified
live: the model read `38%` off a dashboard screenshot and the note said exactly
that.

### Which free model? Measured, not guessed

The plan was "the best free model for each of the five agents". All seven free
models were run through the full suite — same cases, same thresholds, only
`OPENAI_MODEL` changed — then judged by one fixed judge (`gpt-oss:120b`,
prompt v2, single pass).

First, the free set had to be established by probing all 22 models in
`/api/tags`. **Seven are free**; fifteen answer HTTP 402 "not included in your
free usage" (deepseek-v4-pro, glm-5.3, kimi-k3, minimax-m3, mistral-large-3 and
friends), HTTP 403 "being rolled out" (mistral-large-4), or HTTP 400 because
they are not chat models (`clef:27b` is a decision model serving
`/v1/systemone` only).

| model | judged | assertions | elapsed | note |
|---|---|---|---|---|
| `beam` | 4.16 | 108/110 | 142s | reasoning model |
| **`gemma4:31b`** | **4.15** | **109/110** | **43s** | |
| `gpt-oss:20b` | 3.89 | 105/110 | 113s | |
| `nemotron-3-ultra` | 3.87 | 107/110 | 386s | reasoning model |
| `nemotron-3-super` | 3.80 | 107/110 | 731s | reasoning model |
| `gpt-oss:120b` | 3.52 | 103/110 | 83s | **self-judged** — and still last |
| `nemotron-3-nano:30b` | — | 80/82 | 563s | **excluded**, 9 of 30 cases errored |

`beam` leads `gemma4:31b` by 0.01, which is nothing, and takes 3.3× as long.
`gpt-oss:120b` is a good judge and a poor generator here — it scored itself
lowest despite the self-preference bias working in its favour.

#### The bug this found: reasoning models returning nothing

The first bake-off looked like a provider outage — 4 to 19 cases per model
failing with "the language model provider is unavailable". It was not. A
reasoning model spends completion tokens on hidden thinking, and when the budget
runs out mid-thought the API returns **HTTP 200 with an empty message** and
`finish_reason: "length"`. Measured on `nemotron-3-nano:30b`: 1 request in 6
came back with 700 completion tokens and zero characters of content.

`app/llm/openai_compatible.py` now treats that exact signature — empty content
plus `finish_reason: "length"`, or a populated `reasoning` field with no answer
— as a budget problem and retries once with 3× headroom, capped by
`LLM_MAX_TOKENS_CEILING`. Everything else still fails immediately. Streaming got
the same treatment: it used to yield nothing at all, and now falls back to the
non-streaming path. `scripts/check_empty_reply_retry.py` covers it in 24 checks
against a fake transport.

That took five of the six viable models to **zero errors**.
`nemotron-3-nano:30b` still fails, and now says why: it escalated 700 → 2100 →
4000 tokens and produced **12,000–16,000 characters of reasoning with no answer**
each time, 41 retries in one run. That is the model, not the configuration.

#### Why nothing is pinned

The screening suggested two per-agent wins. Both were confirmed at repeat 3
against a same-day control run, and both evaporated:

| | `gemma4:31b` alone | mixed fleet | |
|---|---|---|---|
| overall | **4.28** | 4.18 | |
| `ad-creative` | **4.56** | 4.33 | pinned to `nemotron-3-super` (screened +0.45) |
| `social-copy` | 3.80 | **3.87** | pinned to `beam` (screened +0.33) |
| `post-image` | **4.25** | 3.88 | *same model in both runs* |
| elapsed | **54s** | 201s | |

The last row of that table is the point. `post-image` moved **0.37 with no
configuration change at all** — agents generate at temperature 0.4 and the judge
disagrees with itself by a mean spread of 0.51–0.54, so total run-to-run
variance swamps every per-agent gap on offer. The screening floor of 0.33 was
too lenient; `compare_models.py` now defaults to **0.5**, which is why it says
*pin nothing*.

So `AGENT_MODELS` is empty, and `gemma4:31b` serves all five agents. The
override exists, is tested, and is documented — it is simply not justified by
the evidence on the free tier. Re-check with:

```bash
python scripts/marketing_eval/compare_models.py BAKEOFF2
```

### Then: qualitative scores, measured

`judge.py` applied the `rubric.md` anchors to the cloud run, judged by
**`gpt-oss:120b`** — deliberately *not* the `gemma4:31b` that produced the
output, so this is not a self-evaluation.

| | result |
|---|---|
| mean score | **4.23 / 5** over 61 dimension scores in 22 cases |
| median-score distribution (1→5) | 0, 1, 19, 6, 35 |
| judge unanimity across 3 repeats | 77% identical, mean spread 0.33, worst 2 |
| strongest agents | seo-optimizer **4.6**, ad-creative **4.56** |
| weakest agent | social-copy **3.8** |
| weakest dimensions | `platform_fit`, `hook`, `offer_fidelity`, `uses_source_material`, `profile_awareness` |
| left unjudged | 6 (`legibility`, `brand_fit` — need the pixels) |
| judging cost | free tier, 68 calls, 213s |

Running the judge found **two defects in the evaluation itself**, which is the
more useful result:

1. **The 1–5 scale had collapsed to 1/3/5.** All 174 scores in the first pass
   were 1, 3 or 5 — never 2 or 4 — because the rubric tables anchor only those
   three levels and the judge read them as the only legal answers. Prompt v2
   names 2 and 4 explicitly; 2s and 4s now appear, and the worst repeat spread
   fell from 4 to 2. The first pass is kept as `*.scores-promptv1.json` so the
   change is auditable. **Scores from different prompt versions are not
   comparable**, and the version is recorded in every output file.
2. **One test case was self-contradictory.** `seo-content-type-aware` set the
   profile to *Landing page* but asked for "a blog post". The agent correctly
   followed the explicit request — and the `profile_awareness` anchor scored
   that correct behaviour **1/5, unanimously**. The rubric was wrong, not the
   agent. The anchor now states that an explicit request overrides a standing
   default, the case no longer names a content type, and a companion case
   (`seo-request-overrides-profile`) pins the override behaviour deliberately.

**What these scores are not:** an LLM judge is a cheap proxy for a human reader.
Judges favour their own output (flagged automatically when it happens), favour
longer answers, and cluster high — 35 of 61 medians are 5s. Treat a difference
smaller than the mean spread as noise. No human scoring pass has been recorded.

**Not executed at all:** PostgreSQL + pgvector (no Docker daemon available here)
and `IMAGE_PROVIDER=openai` (no API key available). Both are implemented and
selected by configuration; neither has been run.

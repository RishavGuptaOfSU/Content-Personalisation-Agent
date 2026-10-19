# Marketing domain audit — what drove Phase 2

This is the audit that Phase 2 was built from, with the evidence separated from
the speculation. Everything under "verified" was confirmed by running code, not
by reading filenames.

The audit was performed against the Phase 1 codebase (seven domains, 34 agents)
before Phase 2 narrowed to Marketing alone. Phase 1 is unchanged.

---

## Verified findings

### 1. The image agents were being told to write prose

`personalization._render_output_contract()` injected the global output contract
into **every** agent. The real assembled prompt for `marketing.post-image`
contained both of these:

```
=== HOW YOU WORK ===
Return ONLY a JSON object describing what to render, nothing else:
...
=== USER OUTPUT CONTRACT ===
- Aim for 200-350 words. Cover the essentials without padding.
- Warm and plain-spoken. Second person. No corporate filler.
- Assume working familiarity. Skip the basics.
```

At the `detailed` setting it becomes *"Go deep: 450-700 words, with structure,
edge cases and a worked example"* — to an agent whose output is a headline.

**Measured impact: none on JSON validity.** The baseline run produced 0 degraded
image specs across 6 image cases, so `llama3.2:3b` extracted usable JSON every
time despite the contradiction. Fixed for coherence, not because it was breaking
anything measurable. Reported honestly rather than claimed as a win.

### 2. Collected preferences were never actioned

11 of the 13 marketing agent profile fields were never referenced in their own
agent's `instructions`. Only `post-image.style` and `social-copy.use_hashtags`
were. The data reached the prompt as a bare fact in a context block with no
instruction on what to do with it.

Confirmed consequence in the baseline: `campaign-planner` collects a budget band
and its instructions never mentioned budget.

### 3. Two of nine advertised image sizes rendered broken

From `scripts/probe_renderer.py`:

| Size option | Rendered at | Problem |
|---|---|---|
| `Leaderboard 728x90` | **728×180** | Silently resized by `ImageSpec.sanitized()`, content overflowed the canvas, CTA drawn on top of the headline |
| `Instagram (square)` 1080×1080 | ok | CTA pill overlapped the text stack — on **both** image agents |
| LinkedIn / X / Facebook / Story | ok | verified good |

The leaderboard was visually confirmed unusable: headline cut off, "Start free
trial" printed over the text.

### 4. `ad-creative` could not be styled

It collected only `objective` and `size`, so `ImageSpec.style` was always empty
and the style→palette inference in `build_theme` never fired for ads.

### 5. `ad-creative` gave wrong handoff advice

Its `out_of_scope` said *"ad copy documents or keyword lists (use the SEO
Optimizer)"*. The SEO Optimizer does not write ad copy.

### 6. Routing was healthy; two requests escaped the domain

9/9 clear marketing requests routed correctly and 5/5 sibling handoffs worked.
But *"Help me promote our webinar"* and *"Make something for LinkedIn"* scored
**0.0 across the whole 34-agent catalog** and fell through to
`research.concept-explainer` — leaving marketing entirely. And *"Write ad copy
for our free trial"* routed to `ad-creative`, an **image** agent, for a text
request.

### 7. An agent's own name blocked legitimate handoffs

Diagnosed during the baseline. The scope guard compared the selected agent's
total score against the alternative's, and that total included a 2.0 bonus for
the agent's **name** appearing in the request:

| Selected agent | Request | Own score | Came from |
|---|---|---|---|
| `post-image` | "Write me the LinkedIn **caption** … launch **post**" | 3.2 | `post` (name) |
| `ad-creative` | "Write the body copy … for this **ad**" | 2.0 | `ad` (name) |
| `campaign-planner` | "Write the Instagram caption … of the **campaign**" | 3.0 | `campaign` (name) |

All three exceeded `SCOPE_OWN_MAX_SCORE=1.5` and so refused to hand off, even
though another agent plainly owned the request.

### 8. Word limits were unenforced

Instructions said "max 8 words"; `sanitized()` allowed 120 characters (~20
words); `_fit_text` then shrank the font and could hard-truncate to four lines.

### 9. Marketing copy invents figures — and instructions do not stop it

The strongest finding, and the one that needed new architecture. With **no
figure supplied** and an explicit instruction *"never fabricate metrics,
percentages, testimonials or customer names"*, `llama3.2:3b` produced:

| Run | Agent | Invented |
|---|---|---|
| baseline | `social-copy` | "Unlocking Savings of **Up to $100K Per Year**" |
| after prompt fixes | `social-copy` | "reduce infrastructure costs **by up to 50%**" |
| baseline | `ad-creative` | "**Save up to 80%** of your time" |
| after prompt fixes | `campaign-planner` | invented a **$250** budget from "Plan a campaign" |

Strengthening the instructions did not stop it. This is the same failure mode as
the scope contract, and got the same answer: a deterministic guard
(`app/agents/grounding.py`) that checks claim-shaped figures against the figures
actually available, and flags anything else.

---

## Corrected by the audit itself

One baseline "failure" was **my own bad assertion**, not an agent fault:
`campaign-budget-supplied` checked for the literal string `"400"`. The model had
correctly allocated `$200 + $100 + $100` without restating the total. The
assertion now sums the allocations instead.

---

## Hypotheses that did not survive measurement

| Hypothesis | What measurement showed |
|---|---|
| The prose contract breaks the JSON contract | 0 degraded specs in the baseline — it does not, on this model |
| The campaign plans are truncated by `LLM_MAX_TOKENS=700` | Output ended cleanly with all seven sections present; not truncated |
| Routing needs significant work | 9/9 and 5/5 correct; only two escapes and one text/image mix-up |
| `seo-optimizer` fabricates search volumes | It correctly refused in both runs |

---

## What the fixes actually achieved

Measured by re-running the same dataset against the same model and settings
(`scripts/marketing_eval/compare.py BASELINE FINAL`):

| | baseline | final |
|---|---|---|
| assertions passed | 102/105 | 105/108 |
| regressions | — | **none** |
| "write ad copy" routing | `ad-creative` (image) | `social-copy`, keyword, no model call |
| supplied $400 budget | assertion was wrong | allocations sum to $400 |
| invented figures | undetected | detected and flagged |
| latency, 21 generating cases | 1215s | 1322s (+9%) |

The +9% latency is the honest cost of longer instructions. No prompt change made
anything faster and none was claimed to.

Three findings did **not** yield to prompt engineering and needed code:

1. the scope guard's name-match flaw (fixed in `scoring.py` / `scope.py`),
2. the renderer geometry (fixed in `base.py` / `card_renderer.py`),
3. figure fabrication (new `grounding.py`).

---

## Still open

**`campaign-planner` does not ask for clarification.** Given only "Plan a
campaign" it produces a full plan rather than asking or labelling assumptions,
despite an explicit instruction to do one of the two. The invented budget is now
caught by the grounding guard, but the behaviour itself is unfixed on
`llama3.2:3b`. Options not yet taken: a deterministic pre-check that detects an
underspecified brief and returns a question without calling the model (the same
shape as the scope guard), or a larger model.

**Brand `products_services` and `positioning` fields were considered and not
added.** The hypothesis was that `ad-creative` fabricates because it has nothing
concrete to say. That is plausible but unmeasured, and the grounding guard now
addresses the symptom directly. Adding profile fields on a hypothesis is exactly
what the brief warned against, so they are left as the next thing to test: add
them, re-run the `grounding` category, and see whether the flag rate drops.

**Qualitative quality is now scored by an LLM judge, not by a human.**
`scripts/marketing_eval/judge.py` applies the `rubric.md` anchors to a report
the harness already wrote. Measured on the cloud run, judged by `gpt-oss:120b`
(not the `gemma4:31b` that generated the output): **4.23 / 5** across 61
dimension scores, 77% judge unanimity over three repeats. `legibility` and
`brand_fit` are reported unjudged — they are properties of the rendered pixels
and the judge only sees the spec and alt text.

Judging the first run found two defects in the **evaluation**, not the product,
which was the more valuable outcome:

* The 1–5 scale had silently collapsed to 1/3/5, because the rubric tables
  anchor only those three levels. Prompt v2 fixes it; the pre-fix scores are
  kept as `*.scores-promptv1.json`.
* `seo-content-type-aware` contradicted itself — profile *Landing page*, request
  "a blog post" — and the `profile_awareness` anchor scored the agent's correct
  choice (follow the explicit request) at 1/5, unanimously. The anchor and the
  case are both fixed, and a companion case now pins the override behaviour.

**No human scoring pass has been recorded.** An LLM judge is a proxy: it favours
its own output (detected and flagged automatically), favours length, and
clusters high. The numbers above carry a known spread, not a guarantee.

**One model per agent was tested and rejected.** All seven free Ollama Cloud
models (of 22 listed; the rest are paid) ran the full suite and were judged by
one fixed judge. `gemma4:31b` and `beam` tied at 4.15/4.16 with `beam` 3.3×
slower; `gpt-oss:120b` came last at 3.52 *while judging itself*. The two best
per-agent gaps were then pinned via `AGENT_MODELS` and confirmed at repeat 3:
the mixed fleet scored **4.18 against 4.28** for `gemma4:31b` alone, at 201s
against 54s. `post-image` moved 0.37 between two runs of the *same* model, which
is the measurement that settles it — run-to-run variance (judge spread 0.51–0.54
plus temperature 0.4 generation) is larger than any gap on offer. `AGENT_MODELS`
stays empty; `compare_models.py` enforces a 0.5 noise floor.

**The bake-off found a real provider bug.** Reasoning models return HTTP 200
with an empty message and `finish_reason: "length"` when the token budget goes
on hidden thinking — which surfaced as "the language model provider is
unavailable" and made runs non-comparable (4 to 19 cases errored per model).
`openai_compatible.py` now retries that specific signature with 3× headroom, and
the streaming path no longer yields silence. Five of six viable models went to
zero errors. `nemotron-3-nano:30b` remains unusable here: 12k–16k characters of
reasoning and no answer even at a 4000-token ceiling.

**Not executed at all:** PostgreSQL + pgvector (no Docker daemon available) and
`IMAGE_PROVIDER=openai` (no API key available).

# Qualitative rubric

The harness decides everything a machine can decide. It does **not** score the
dimensions below, because string matching is not a measure of creative quality.
Score these by reading the markdown report a run produces.

Score each declared dimension **1–5**. Write the score next to the `__/5` slot
in the report. A dimension only applies to a case if that case declares it.

Use the same brand context the harness configures:

> **Acme Cloud** — SaaS, audience *Developers and Founders*, tone *Professional*,
> never use *clickbait* or *emojis*. Positioning: engineering time saved, not price.

---

## Scoring anchors

**1** — unusable; would be discarded.
**2** — recognisable attempt, needs a rewrite.
**3** — usable after edits.
**4** — usable as-is with a tweak.
**5** — would ship unchanged.

Anchors are given for 1, 3 and 5. Use 2 and 4 for output that sits between two
anchors — most competent work is a 4, not a 5. Reserve 5 for output you would
publish with no edit at all: if you can name an edit, it is a 4.

One rule overrides the dimensions below: **an explicit instruction in the
request beats the standing brand or agent configuration.** If the profile is set
to *Landing page* and the request asks for a blog post, the blog post is
correct. Score the agent down for ignoring configuration only where the request
was silent about it.

---

## Dimensions

### Copy and text agents

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| `hook` | Opens with a definition or the product name | Opens with a clear statement | First line stands alone in a feed and earns the second |
| `audience_fit` | Generic business speak | Addresses the audience loosely | Speaks to a developer or founder's actual situation |
| `brand_tone` | Breaks the tone or uses a banned term | Roughly professional | Sounds like the brand, nothing banned |
| `usefulness` | Says nothing a reader could act on | One usable idea | A reader could act on it immediately |
| `no_filler` | Padded with marketing cliché | Some filler | Every sentence carries information |
| `instruction_following` | Ignores the explicit constraint | Partly honours it | Honours every stated constraint exactly |
| `platform_fit` | Wrong conventions for the platform | Mostly right | Correct length, formatting and CTA habit for that platform |
| `no_fabrication` | States invented figures or testimonials as fact | Vague but not false | Makes no claim that was not supplied |
| `honesty_about_limits` | Invents data it cannot have | Hedges | States plainly what it cannot know and how to verify |
| `uses_source_material` | Ignores the attachment | References it loosely | Built directly on the supplied text |
| `clarification_quality` | Invents the missing brief | Asks something vague | Asks the one question that unblocks the work, or labels assumptions clearly |

### Image agents

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| `headline_relevance` | Unrelated to the request | On topic | Says the one thing the request is actually about |
| `headline_brevity` | Overflows or wraps to four lines | Fits but is wordy | Short enough to read at a glance |
| `legibility` | Text collides or is clipped | Readable | Clear hierarchy, nothing colliding |
| `brand_fit` | Ignores the brand colours and tone | Uses the colours | Looks like the brand produced it |
| `alt_text` | Missing or just repeats the headline | Describes the image | Describes it usefully for a screen reader |
| `graceful_degradation` | Produces nonsense from a vague brief | Produces something generic | Produces something defensible, or says what it needs |

### Ad creative

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| `value_proposition` | Leads on the product name | States a benefit | States the outcome the buyer wants |
| `cta_quality` | No verb, or vague | A verb | Specific imperative matching the objective |
| `objective_alignment` | Contradicts the configured objective | Neutral | Clearly built for that objective |
| `offer_fidelity` | Changes or invents the offer | Mentions it | States the supplied offer exactly |

### Campaign planner

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| `objective_clarity` | No measurable objective | Measurable but vague | One sentence, measurable, time-bound |
| `channel_choice` | Channels the user does not have | Uses the configured channels | Right channel for each job, with a reason |
| `timeline_realism` | Impossible in the window | Plausible | Sequenced with dependencies that make sense |
| `kpi_quality` | Vanity metric only | A real metric | A primary metric plus a guardrail |
| `budget_handling` | Invents a budget, or ignores the one given | Mentions it | Allocates the supplied budget and labels anything suggested |
| `risks` | None named | Generic risks | The two or three things that would actually sink it |

### SEO

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| `intent_reading` | Misreads what the searcher wants | Names the intent | Names the intent and shapes the page around it |
| `keyword_relevance` | Unrelated or absurdly broad terms | Plausible terms | Terms this page could realistically rank for |
| `structure` | No usable outline | An outline | An outline that answers the intent in order |
| `actionability` | Advice with no next step | Some steps | Every recommendation is directly implementable |
| `profile_awareness` | Ignores the configured content type and region when the request says nothing about them | Generic | Applies the configured settings, or follows the request where it overrides them and says so |

---

## Dimensions a text judge must skip

`judge.py` reads the report, which contains the image *spec* and alt text but
not the pixels. These dimensions are properties of the rendered file, so a
text-only judge would be guessing:

- `legibility` — whether text collides, clips or overflows is geometry.
  `scripts/probe_renderer.py` already checks this deterministically across
  27 layout cases, which is a stronger measure than an opinion.
- `brand_fit` — the spec names a palette, but whether the result *looks* like
  the brand needs eyes on the image.

The judge reports these as unjudged rather than scoring them. Score them by
hand from the generated PNG, or trust the renderer probe for `legibility`.

---

## Recording a score

Keep scores alongside the report they belong to, in
`reports/<report-name>.scores.md`, so a later run can be compared against the
same reading. Note the model used — a 3B local model and a 70B hosted model are
not comparable, and neither is a scored run against an unscored one.

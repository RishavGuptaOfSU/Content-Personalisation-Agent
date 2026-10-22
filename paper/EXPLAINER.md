# The paper, in plain English

Prachi Sharma · Danish Kaul · Dishant Sherawat
School of Engineering and Technology, Sushant University, Gurugram, Haryana

For the authors, and for anyone who has to present or defend this work.
No jargon that isn't explained.

> A typeset version of this document is at `paper/explainer.pdf`.

---

## 1. Is the paper about our project?

**Yes — entirely.** It is not a literature survey or a side essay. Every number
in it was produced by running the code in this repository, and every section
describes something we actually built.

| Paper section | The code it describes | Size |
|---|---|---|
| 3.1 Eight-stage pipeline | `phase-2/backend/app/agents/graph.py` | 461 lines |
| 3.2 Three-level profile | `app/services/personalization.py` | 466 lines |
| 3.3 Scope guard | `app/agents/scope.py` | 138 lines |
| 3.4 Grounding guard | `app/agents/grounding.py` | 178 lines |
| 4.1 The 30-case dataset | `scripts/marketing_eval/cases.toml` | 30 cases |
| 4.2 Deterministic assertions | `scripts/marketing_eval/harness.py` | 110 assertions |
| 4.3 Rubric and judge | `scripts/marketing_eval/rubric.md`, `judge.py` | 32 dimensions |
| 5.3 Seven-model comparison | `scripts/marketing_eval/compare_models.py` | 7 runs |
| 5.6 The empty-reply defect | `app/llm/openai_compatible.py` | the fix is in `generate()` |

Phase 2 of the project is 76 Python modules and about 12,600 lines of
application code, plus 10 verification scripts. The paper reports on that.

There is a script, `paper/check_claims.py`, that re-reads the stored run reports
and checks that all 76 numbers in the manuscript still match them. If someone
asks "where does 4.28 come from", the answer is a file on disk, not a memory.

---

## 2. What problem were we solving?

Ask a language model to write marketing copy and two things go wrong.

**It doesn't know your brand.** It will write in a generic voice, pick the wrong
platform conventions, and ignore the fact that you never use emojis.

**It invents numbers.** Ask for a post about cloud costs and it will happily
write "cut your bill by 40%" — a figure nobody gave it. In marketing copy that
is not a harmless slip; it is a false claim published under your brand name.

We tried the obvious fix for the second problem first: we told the model, in its
instructions, not to invent figures. **It kept inventing figures.** That failure
is what shaped the whole project.

---

## 3. What we built

Five narrow agents instead of one general chatbot — a caption writer, an SEO
agent, a campaign planner, and two that produce images (a social post image and
an ad creative). Each one has its own instructions and its own settings.

Three things are worth understanding.

### Three-level profiles

Your details live at the level where they're actually true:

- **Global** — who you are, how you like to be spoken to
- **Domain** (marketing) — brand name, industry, audience, tone, banned words
- **Agent** — e.g. for the caption writer: which platforms, how long, hashtags

Say your brand tone once and all five agents get it. Say "max 3 hashtags" and
only the caption writer gets it, because it's meaningless to the others.

### The scope guard

If you're in the caption writer and you ask for an ad image, the system
**hands you off** to the right agent instead of doing a bad job.

The important part: this decision is made **in plain code, with no model call.**
It is instant and free. It compares how much evidence your request gives for the
current agent's job versus every other agent's job, and only redirects when the
mismatch is obvious — four separate conditions must all hold, because wrongly
redirecting someone is worse than answering slightly off-topic.

> **A bug worth telling the examiner about.** The first version scored each
> agent using its whole vocabulary *including its own name*. So "design an ad
> creative" sent to the caption writer scored highly for the caption writer —
> because the phrase contains words from its own name — and never got
> redirected. The fix was to score only *task* words and ignore name matches.

### The grounding guard

After the model writes something, we scan the text for claim-shaped numbers —
percentages, money, "10x", "up to" — and check each one against the numbers you
actually supplied in your request, your attachment, or your profile. Anything we
can't account for gets **flagged**.

Two design decisions here matter:

**It flags, it never rewrites.** Deleting a number mid-sentence gives you
"reduce costs by up to" — worse than the original. And only *you* know whether
the claim is true, so the system's job is to tell you, not to decide.

**It checks provenance, not truth.** We're not fact-checking the world. We're
asking: did this number come from the user, or did the model make it up? That's
a much cheaper question and the one that actually matters here.

---

## 4. How we measured it — and why that's the real contribution

This is the part a reviewer will care about most, so it's worth understanding
properly.

### Two kinds of question

Some questions a computer can answer exactly:

- Did it hand off to the right agent?
- Did the budget split add up to the €400 the user gave?
- Did it stay under 3 hashtags?
- Is the generated image exactly 1200×627 pixels?

We wrote **110 such checks** across 30 test cases. They run in seconds, cost
nothing, and give the same answer every time.

Other questions a computer cannot answer:

- Is this a good opening line?
- Does this sound like our brand?
- Would you actually publish this?

For those we used an **LLM judge** — a second, independent AI model that reads
the output against a written scoring guide (our `rubric.md`, 32 dimensions,
scored 1–5) and gives a score plus a reason.

### Then we checked whether we could trust the judge

Most people stop at "the judge gave us 4.23/5" and report that. We didn't, and
this is where the interesting results came from.

**We asked the judge the same question three times.** Same outputs, same
prompt, temperature set to zero so it should be deterministic.

It disagreed with itself. Mean spread **0.51–0.54 points on a 5-point scale.**

**Then we re-ran the whole system without changing anything** and judged again.
One agent's score moved by **0.37** — with zero changes to the code.

That single number reframed everything. It means any quality difference smaller
than about half a point is **noise, not a result.**

---

## 5. What we found

### Finding 1: The guards worked

Holding the model fixed, adding the guards took the deterministic suite from
**102/105 to 105/108** passing checks. Three failures remained and no amount of
prompt rewriting fixed them.

Then we swapped in a bigger model and changed nothing else. All three passed,
and the suite went to **110/110**. So those three failures were the *model's
limitation*, not our design's. You can only make that claim if you change one
thing at a time — which is the whole point of a controlled experiment.

### Finding 2: Our scoring scale had silently broken

The rubric defines what a 1, a 3 and a 5 look like for each dimension. We
assumed the judge would use 2 and 4 for in-between work.

It never did. Across **174 scores, every single one was a 1, a 3 or a 5.** Not
one 2, not one 4. Our five-point scale had quietly become a three-point scale,
and nothing in the system would ever have told us — we only saw it because we
plotted the distribution.

Fixing the prompt to name the middle values brought them back and cut the worst
disagreement from 4 points to 2.

### Finding 3: "Best model for each agent" sounds smart and isn't

We had five specialised agents, so the natural next step was to give each one
the model best suited to it. A first screening pass seemed to confirm this: two
agents looked 0.45 and 0.33 better under different models.

So we built it properly and tested it against a control:

| | One model for all | Mixed fleet |
|---|---|---|
| Overall score | **4.28** | 4.18 |
| Speed | **54 s** | 201 s |
| The two "improved" agents | 4.56 / 3.80 | 4.33 / **3.87** |

The mixed fleet was **worse overall and 3.7× slower.** One of the two "improved"
agents actually got *worse*. A proper statistical test (Wilcoxon signed-rank,
15 changed pairs) gave **p = 0.42** — nowhere near significant.

Why did screening lie to us? Because 0.33 and 0.45 are *inside the noise floor*
we measured. They were never real.

**We report this as a failure, in full, in the paper.** That's deliberate. A
negative result that saves someone else three days of work is worth more than a
positive result we had to squint at.

### Finding 4: A bug that looked like someone else's fault

While comparing models, four of them failed on 4–19 test cases each, reporting
what looked like the provider being down.

It wasn't. Some newer models "think" before answering, and that thinking burns
through the token budget. When it runs out mid-thought, the API returns
**success, with an empty message.** Our code saw an empty message and reported a
provider outage.

One model returned 700 tokens of pure thinking and *zero* characters of answer,
one request in six.

We now detect that exact signature and retry with more room. Five of six models
went to **zero errors**. The sixth is genuinely unusable for this task — it
produced 12,000–16,000 characters of reasoning and never answered, needing 41
retries in one run.

This mattered beyond robustness: before the fix, each model failed on a
*different* set of cases, so each model's score described a different subset of
the test. Any ranking would have been an accident of which cases survived.

---

## 6. The one-sentence version of each takeaway

1. **If you can check something in code, check it in code.** Telling a model
   "don't invent numbers" does not work. A 178-line checker does.
2. **Flag, don't fix.** When the system can't know if something is wrong, tell
   the user instead of silently editing.
3. **Publish your noise floor, not just your score.** We measured ours at half a
   point, and it invalidated two conclusions we had already drawn.
4. **Specialised agents don't need specialised models.** We tested it; the
   difference was smaller than the noise and cost 3.7× the latency.
5. **Test your test code.** Both of our worst bugs were in the *measuring*
   equipment, and both produced confident, wrong numbers.

---

## 7. Honest limitations

Expect to be asked about these. They're stated plainly in the paper's Threats to
Validity section, which is the correct place for them.

- **No human scoring pass.** Our judge was never checked against real human
  raters. This is the biggest weakness, and we say so.
- **One brand, one language, one industry.** All results use a single synthetic
  brand in English.
- **The 30 cases were written by us**, to probe failures we expected. They are
  not sampled from real traffic.
- **Small sample for the statistics.** 15 changed pairs. A bigger dataset might
  find an effect we couldn't.
- **The noise floor of 0.5 is ours**, for this task and this judge. It is not a
  universal constant.

---

## 8. Likely viva questions

**"Why not just fine-tune a model on the brand?"**
Too expensive per user, and it can't be updated the moment a brand changes its
tone. Profile composition at request time is instant and per-user.

**"Isn't using an AI to judge AI circular?"**
Yes, which is why we measured how much it disagrees with itself, used a
*different* model as judge than the one being judged, and flag loudly in the
code whenever those two are the same. Section 2.4 of the paper cites the
published work on self-preference bias.

**"Why is a negative result in the paper?"**
Because it's true, and because the reasoning behind it — effect size versus
measured noise — is the paper's main methodological point. Removing it would
leave the most useful finding out.

**"What's actually new here?"**
Three things: scope enforcement as a deterministic, zero-cost step rather than a
prompt instruction; provenance-checking of claim-shaped numbers rather than
fact-checking; and reporting judge variance as a required part of judge-based
evaluation.

**"Could you have just used a bigger model and skipped all this?"**
A bigger model fixed three test failures — we show that. It did *not* stop
figure fabrication, and it cannot do the scope handoff for free. The guards and
the model are solving different problems.

# Marketing evaluation — BAKEOFF2-beam

Generated 20261019T045445Z · 30 cases · 142s

## Configuration

| setting | value |
|---|---|
| `llm_provider` | openai |
| `llm_model` | beam |
| `llm_temperature` | 0.4 |
| `llm_max_tokens` | 700 |
| `embedding_provider` | ollama |
| `embedding_dim` | 768 |
| `memory_min_similarity` | 0.45 |
| `image_provider` | local |
| `router_use_llm` | True |
| `scope_own_max_score` | 1.5 |
| `scope_other_min_score` | 4.0 |

## Deterministic results

**108/110 assertions passed** across 30 cases.

| case | agent | category | assertions | failures |
|---|---|---|---|---|
| `copy-ordinary-linkedin` | social-copy | ordinary | 6/6 | 0 |
| `copy-complex-thread` | social-copy | complex | 2/2 | 0 |
| `copy-exact-constraint-hashtags` | social-copy | ordinary | 2/2 | 0 |
| `copy-no-hashtags-platform` | social-copy | platform | 2/2 | 0 |
| `copy-grounding-no-metrics` | social-copy | grounding | 3/3 | 0 |
| `copy-memory-applied` | social-copy | memory | 2/2 | 0 |
| `copy-out-of-scope-image` | social-copy | out_of_scope | 4/4 | 0 |
| `copy-ad-copy-routing` | — | routing | 2/2 | 0 |
| `image-ordinary-linkedin` | post-image | ordinary | 9/9 | 0 |
| `image-complex-detail` | post-image | complex | 5/5 | 0 |
| `image-ambiguous` | post-image | ambiguous | 4/4 | 0 |
| `image-brand-colours` | post-image | brand | 5/5 | 0 |
| `image-out-of-scope-caption` | post-image | out_of_scope | 4/4 | 0 |
| `image-out-of-scope-campaign` | post-image | out_of_scope | 4/4 | 0 |
| `ad-ordinary-trial` | ad-creative | ordinary | 8/8 | 0 |
| `ad-supplied-offer` | ad-creative | ordinary | 5/5 | 0 |
| `ad-grounding-no-invented-offer` | ad-creative | grounding | 6/6 | 0 |
| `ad-out-of-scope-copy` | ad-creative | out_of_scope | 4/4 | 0 |
| `seo-ordinary-landing` | seo-optimizer | ordinary | 4/4 | 0 |
| `seo-grounding-no-volumes` | seo-optimizer | grounding | 2/2 | 0 |
| `seo-attachment` | seo-optimizer | attachment | 2/2 | 0 |
| `seo-content-type-aware` | seo-optimizer | profile | 2/2 | 0 |
| `seo-request-overrides-profile` | seo-optimizer | profile | 1/1 | 0 |
| `seo-out-of-scope` | seo-optimizer | out_of_scope | 4/4 | 0 |
| `campaign-ordinary-launch` | campaign-planner | ordinary | 4/4 | 0 |
| `campaign-budget-supplied` | campaign-planner | complex | 2/3 | 1 |
| `campaign-clarification` | campaign-planner | clarification | 3/3 | 0 |
| `campaign-grounding-no-invented-budget` | campaign-planner | grounding | 1/2 | 1 |
| `campaign-out-of-scope-write` | campaign-planner | out_of_scope | 4/4 | 0 |
| `campaign-routing` | — | routing | 2/2 | 0 |

### Failed assertions

- `campaign-budget-supplied` — no figures the user did not supply → 0.5%
- `campaign-grounding-no-invented-budget` — no figures the user did not supply → 20%, 60%, 40%

## Outputs for qualitative scoring

Score each dimension 1–5 using `rubric.md`. The harness deliberately does
not score these.

### `copy-ordinary-linkedin` — marketing.social-copy (ordinary)

**Request:** Write a LinkedIn post about how much cloud spend sits idle

**Reply:**

```
Most cloud spend isn't doing anything right now.

Idle resources pile up between deploys, tests, and weekends.

The real cost isn't the invoice. It's the engineering hours spent hunting them down and cleaning them up.

Acme Cloud keeps your environments lean so your team ships instead of scavenging.

See how it works.

#CloudEngineering #DevOps #AcmeCloud

**Why this works:** Leads with a hook that stands alone, then reframes idle spend as an engineering-time problem rather than a price problem. Ends with a single, low-friction CTA.
```

**Score:** hook __/5 · audience_fit __/5 · brand_tone __/5 · usefulness __/5 · no_filler __/5

---

### `copy-complex-thread` — marketing.social-copy (complex)

**Request:** Write a 3-post X thread explaining why we rebuilt our cost allocation engine.
Post 1 is the problem, post 2 the rebuild, post 3 the result. Keep each under
280 characters and number them.

**Reply:**

```
1/3 Cost allocation was guesswork. Tags drifted, shared resources got dumped on one team, and engineers spent hours reconciling bills instead of shipping. We needed a model that matched how teams actually build. #CloudCosts #Engineering

2/3 So we rebuilt it. Usage-based attribution, automatic shared-cost splitting, and a tagging policy enforced at deploy time. No manual spreadsheets. The engine now maps spend to the service and team that actually incurred it. #FinOps #Cloud

3/3 Result: teams see their own spend in real time, finance gets clean reports, and engineers stop chasing invoices. Allocation went from a monthly fire drill to a background process. #AcmeCloud #DevTools

**Why this works:** Each post carries one idea (problem, rebuild, result) so the thread reads as a story, and the copy leads with engineering time saved rather than price.
```

**Score:** instruction_following __/5 · hook __/5 · brand_tone __/5

---

### `copy-exact-constraint-hashtags` — marketing.social-copy (ordinary)

**Request:** LinkedIn post about our new pricing. Use at most 2 hashtags.

**Reply:**

```
We just simplified our pricing.

One plan, everything included — so your engineers spend less time managing cloud costs and more time building.

See the new plans and start a trial.

#AcmeCloud #CloudPricing

**Why this works:** Leads with the change, then ties it to engineering time saved rather than cost alone. Single-sentence paragraphs keep it scannable on LinkedIn.
```

**Score:** instruction_following __/5

---

### `copy-no-hashtags-platform` — marketing.social-copy (platform)

**Request:** Write the Facebook post copy for our webinar on Thursday

**Reply:**

```
Join us Thursday for a live session on how engineering teams cut wasted cloud hours and ship faster. We'll walk through practical patterns you can apply this week — no fluff, just what works.

Save your seat here: [registration link]

Spots are limited, so grab yours now.

**Why this works:** Conversational opener, short paragraphs, and a single explicit CTA fit Facebook's format; the angle leads with engineering time saved rather than price, per your standing preference.
```

**Score:** platform_fit __/5 · usefulness __/5

---

### `copy-grounding-no-metrics` — marketing.social-copy (grounding)

**Request:** Write a LinkedIn post about how much money we save customers

**Reply:**

```
Your engineers shouldn't spend their week fighting infrastructure.

Acme Cloud handles provisioning, scaling, and reliability so your team ships features instead of maintaining plumbing.

The result is engineering time back — hours that go toward product, not platform.

See how much time your team could reclaim. Link in comments.

#AcmeCloud #DevTools #Engineering #CloudComputing

**Why this works:** Positions on engineering time reclaimed rather than price, matching your standing positioning. Single-sentence paragraphs keep it scannable on LinkedIn.
```

**Score:** no_fabrication __/5 · brand_tone __/5

---

### `copy-memory-applied` — marketing.social-copy (memory)

**Request:** Another LinkedIn post, this time about staging environments left running

**Reply:**

```
Staging environments don't need to run 24/7.

Most teams spin them up for a test, then forget them. The result is wasted compute and hours lost tracking it down.

The fix isn't more process. It's a habit: spin down when idle, automate the teardown, and make ownership visible.

At Acme Cloud, we help engineering teams reclaim the hours lost chasing idle infrastructure.

What's your team's teardown habit?

#DevOps #CloudEngineering #EngineeringProductivity

**Why this works:** Leads with a contrarian hook, frames the problem as lost engineering time (not cost), and ends with a low-friction question that invites comments. Single-sentence paragraphs keep it scannable on mobile.
```

**Score:** instruction_following __/5 · usefulness __/5

---

### `copy-out-of-scope-image` — marketing.social-copy (out_of_scope)

**Request:** Create the post image graphic for our launch announcement

**Reply:**

```
That is outside what I do. I am the **Social Caption Writer** — Writing post captions, social copy and ad copy.

**Social Post Image Generator** handles this: Producing a social post image: headline, supporting line and brand styling, rendered at the right size for the platform.

Switch to it and send your message again, or ask me something in my area:

- Write a LinkedIn caption about AI automation
- Instagram caption for our product launch
- A 3-post X thread on why we rebuilt our API
```

---

### `image-ordinary-linkedin` — marketing.post-image (ordinary)

**Request:** Create a LinkedIn post image about cutting cloud costs with automation

**Rendered:** `post-image-1792385592-4558b286.png` 1200×627 (57664 bytes)

**Alt text:** LinkedIn post graphic with headline about automating cloud work to reclaim engineering time

**Spec from the model:**

```json
{
  "headline": "Automate cloud work, reclaim engineering time",
  "subline": "Let automation handle the toil your team shouldn't do",
  "badge": "automation",
  "cta": "See how it works",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Automate cloud work, reclaim engineering time**
Let automation handle the toil your team shouldn't do

*1200×627 · CTA: See how it works · brand palette*
```

**Score:** headline_relevance __/5 · headline_brevity __/5 · legibility __/5 · brand_fit __/5 · alt_text __/5

---

### `image-complex-detail` — marketing.post-image (complex)

**Request:** A post image announcing our Series A. The headline should lead on what it means
for customers, not on the amount. Add a short supporting line and a call to
action that points at the changelog.

**Rendered:** `post-image-1792385598-44c7f4db.png` 1200×627 (62668 bytes)

**Alt text:** LinkedIn post graphic announcing Acme Cloud's Series A with a customer-focused headline and a call to action to read the changelog.

**Spec from the model:**

```json
{
  "headline": "More engineering capacity for your roadmap",
  "subline": "Series A funds platform and reliability work.",
  "badge": "",
  "cta": "See the changelog",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**More engineering capacity for your roadmap**
Series A funds platform and reliability work.

*1200×627 · CTA: See the changelog · brand palette*
```

**Score:** headline_relevance __/5 · instruction_following __/5 · legibility __/5

---

### `image-ambiguous` — marketing.post-image (ambiguous)

**Request:** Make us a graphic

**Rendered:** `post-image-1792385603-e470913d.png` 1200×627 (37251 bytes)

**Alt text:** Graphic with the headline: Make us a graphic

**Spec from the model:**

```json
{
  "headline": "Make us a graphic",
  "subline": "",
  "badge": "",
  "cta": "",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Make us a graphic**

*1200×627 · brand palette*
```

**Score:** headline_relevance __/5 · graceful_degradation __/5

---

### `image-brand-colours` — marketing.post-image (brand)

**Request:** Instagram square graphic announcing our new usage-based pricing

**Rendered:** `post-image-1792385607-58cff570.png` 1200×627 (52189 bytes)

**Alt text:** Square Instagram graphic announcing Acme Cloud's new usage-based pricing with a bold headline.

**Spec from the model:**

```json
{
  "headline": "Usage-based pricing is live",
  "subline": "Pay for what you use, nothing more",
  "badge": "New pricing",
  "cta": "See pricing",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Usage-based pricing is live**
Pay for what you use, nothing more

*1200×627 · CTA: See pricing · brand palette*
```

**Score:** brand_fit __/5 · legibility __/5 · headline_brevity __/5

---

### `image-out-of-scope-caption` — marketing.post-image (out_of_scope)

**Request:** Write me the LinkedIn caption to go with our launch post

**Reply:**

```
That is outside what I do. I am the **Social Post Image Generator** — Producing a social post image: headline, supporting line and brand styling, rendered at the right size for the platform.

**Social Caption Writer** handles this: Writing post captions, social copy and ad copy.

Switch to it and send your message again, or ask me something in my area:

- Create a LinkedIn post image about AI automation
- Instagram graphic announcing our new pricing
- A post image for our webinar next Thursday
```

---

### `image-out-of-scope-campaign` — marketing.post-image (out_of_scope)

**Request:** Plan a six week campaign across five channels with a budget split

**Reply:**

```
That is outside what I do. I am the **Social Post Image Generator** — Producing a social post image: headline, supporting line and brand styling, rendered at the right size for the platform.

**Campaign Planner** handles this: Planning marketing campaigns: objectives, channels, calendar, KPIs.

Switch to it and send your message again, or ask me something in my area:

- Create a LinkedIn post image about AI automation
- Instagram graphic announcing our new pricing
- A post image for our webinar next Thursday
```

---

### `ad-ordinary-trial` — marketing.ad-creative (ordinary)

**Request:** Ad creative promoting our free trial for engineering teams

**Rendered:** `ad-creative-1792385612-0d29e280.png` 1080×1080 (79804 bytes)

**Alt text:** Ad creative promoting a free trial of Acme Cloud for engineering teams.

**Spec from the model:**

```json
{
  "headline": "Free up engineering time",
  "subline": "Automate cloud ops for dev teams",
  "badge": "Free trial",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Free up engineering time**
Automate cloud ops for dev teams

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · objective_alignment __/5 · legibility __/5 · alt_text __/5

---

### `ad-supplied-offer` — marketing.ad-creative (ordinary)

**Request:** Ad image promoting 30% off annual plans until 31 March

**Rendered:** `ad-creative-1792385624-d3c3c9f6.png` 1080×1080 (87587 bytes)

**Alt text:** Square promotional image for 30% off annual plans until 31 March.

**Spec from the model:**

```json
{
  "headline": "Ship faster with less friction",
  "subline": "30% off annual plans until 31 March",
  "badge": "30% off until 31 March",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Ship faster with less friction**
30% off annual plans until 31 March

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · offer_fidelity __/5

---

### `ad-grounding-no-invented-offer` — marketing.ad-creative (grounding)

**Request:** Make an ad creative that will get engineering managers to sign up

**Rendered:** `ad-creative-1792385629-37058d5a.png` 1080×1080 (91291 bytes)

**Alt text:** Ad creative for Acme Cloud promoting free trial signups to engineering managers.

**Spec from the model:**

```json
{
  "headline": "Save engineering time every sprint",
  "subline": "Automate the workflows your team repeats daily",
  "badge": "Acme Cloud",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Save engineering time every sprint**
Automate the workflows your team repeats daily

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** no_fabrication __/5 · value_proposition __/5

---

### `ad-out-of-scope-copy` — marketing.ad-creative (out_of_scope)

**Request:** Write the body copy and three headline variants for this ad

**Reply:**

```
That is outside what I do. I am the **Ad Creative Generator** — Rendering a paid advertising creative image with offer and CTA.

**Social Caption Writer** handles this: Writing post captions, social copy and ad copy.

Switch to it and send your message again, or ask me something in my area:

- An ad creative for our spring promotion
- Make a Google Display ad for our analytics tool
- Ad image promoting 30% off annual plans
```

---

### `seo-ordinary-landing` — marketing.seo-optimizer (ordinary)

**Request:** Optimise our cloud cost automation landing page for search

**Reply:**

```
**Primary keyword** — "cloud cost automation" (commercial intent: buyers comparing solutions).

**Secondary keywords**
- cloud cost optimization tools
- reduce cloud spend automatically
- cloud spend management
- FinOps automation
- cloud cost monitoring
- automate cloud savings

**Title tag** — "Cloud Cost Automation for Developers | Acme Cloud" (50 chars)

**Meta description** — "Automate cloud cost optimization and save engineering time. Acme Cloud helps developers and founders cut cloud spend without manual effort." (138 chars)

**H2 outline** (landing page: offer first, then proof)
1. Hero — automate cloud cost savings, one-line value prop
2. Proof — time saved, customer logos, before/after
3. How it works — connect → detect waste → act
4. Key capabilities — rightsizing, scheduling, anomaly alerts
5. Integrations — AWS, GCP, Azure
6. Objections / FAQ — security, setup time, rollback
7. Final CTA — start free / book demo

**Internal link targets** — case studies, integration docs, FinOps blog posts, security/compliance page. (I'm not leading with pricing, per your standing positioning rule.)

Notes: I have no live search data, so volumes, difficulty, CPC and rankings aren't something I can state — use Google Search Console, Ahrefs or Semrush for those. No page copy was supplied, so the keywords above are inferred from your brand/audience context rather than drawn from existing copy.
```

**Score:** intent_reading __/5 · keyword_relevance __/5 · structure __/5 · actionability __/5

---

### `seo-grounding-no-volumes` — marketing.seo-optimizer (grounding)

**Request:** Give me the search volume and keyword difficulty for 'cloud cost tool'

**Reply:**

```
I can't see search volume or keyword difficulty — I have no access to live search data, so I won't guess at a number.

For real figures, pull them from a keyword tool: **Google Keyword Planner** (free, needs a Google Ads account), **Ahrefs Keywords Explorer**, **SEMrush Keyword Magic Tool**, or **Moz Keyword Explorer**. If you want, I can still build the SEO assets (title, meta, H2 outline, internal links) for a landing page targeting "cloud cost tool" once you share the page copy or key details.
```

**Score:** no_fabrication __/5 · honesty_about_limits __/5

---

### `seo-attachment` — marketing.seo-optimizer (attachment)

**Request:** Optimise this page copy for search

**Reply:**

```
**Primary keyword** — "find idle cloud capacity" (commercial intent: evaluating a tool to solve an idle-resource problem).

**Secondary keywords**
- idle cloud resources
- cloud waste detection
- unused cloud instances
- cloud cost automation
- automated cloud audit
- engineering time saved

**Title tag** — "Find Idle Cloud Capacity Automatically | Acme Cloud" (50 characters)

**Meta description** — "Acme Cloud connects to your account and reports idle cloud capacity automatically. Trusted by engineering teams." (111 characters)

**H2 outline** (landing page: offer first, then proof)
1. Find idle cloud capacity automatically
2. Trusted by engineering teams
3. How it works: connect, detect, report
4. What we flag as idle
5. Give engineering time back
6. Start your first scan

**Internal link targets**
- /docs/getting-started (setup walkthrough)
- /integrations (supported cloud providers)
- /case-studies (engineering team outcomes)
- /security (account access and data handling)
- /blog (cloud cost and waste guides)

Observed from your copy: the value prop, the automatic-detection angle, the engineering-teams trust signal, and the account-connection mechanism. Assumed from your profile: India/English locale, landing-page shape, and the engineering-time-saved positioning. I have no live search data, so volumes and difficulty aren't included — a tool like Google Keyword Planner or Ahrefs would give those.
```

**Score:** uses_source_material __/5 · keyword_relevance __/5 · structure __/5

---

### `seo-content-type-aware` — marketing.seo-optimizer (profile)

**Request:** SEO for our Kubernetes rightsizing feature

**Reply:**

```
**Primary keyword** — "Kubernetes rightsizing" (commercial intent: evaluators comparing solutions)

**Secondary keywords**
- Kubernetes resource optimization
- right-size Kubernetes workloads
- Kubernetes CPU and memory tuning
- reduce Kubernetes waste
- Kubernetes autoscaling vs rightsizing
- Kubernetes cost automation

**Title tag** — "Kubernetes Rightsizing That Saves Eng Time | Acme Cloud" (55 chars)

**Meta description** — "Right-size Kubernetes workloads automatically and give your engineers time back. Acme Cloud tunes CPU and memory without manual toil." (132 chars)

**H2 outline** (landing page, offer → proof → action)
1. Right-size Kubernetes workloads automatically
2. How Acme Cloud rightsizes your clusters
3. Engineering time saved (proof)
4. Trusted by teams running Kubernetes at scale (social proof)
5. Frequently asked questions
6. Get started — book a demo

**Internal link targets**
- Cloud cost automation landing page (related feature)
- Kubernetes documentation / setup guide
- Case studies from teams running Kubernetes
- Blog: Kubernetes resource requests vs limits

Observed: drawn from your recent "cloud cost automation" request and the standing instruction to position on engineering time saved, not price. Assumed: feature set (auto-tuning CPU/memory), audience of developers and founders in India, and that a demo CTA fits your funnel. No search volumes or difficulty scores available — use Google Keyword Planner or Ahrefs for real figures.
```

**Score:** intent_reading __/5 · structure __/5 · profile_awareness __/5

---

### `seo-request-overrides-profile` — marketing.seo-optimizer (profile)

**Request:** SEO for a blog post about rightsizing Kubernetes requests

**Reply:**

```
**Primary keyword** — "Kubernetes rightsizing requests" (informational)

**Secondary keywords**
- Kubernetes resource requests
- rightsize Kubernetes pods
- Kubernetes CPU memory requests
- Kubernetes cost optimization
- VPA Kubernetes
- Kubernetes autoscaling

**Title tag** — "Rightsizing Kubernetes Requests: A Practical Guide" (50 chars)

**Meta description** — "Learn how to rightsize Kubernetes requests to cut waste and save engineering time. Practical steps, metrics, and pitfalls for developers." (137 chars)

**H2 outline**
1. What Kubernetes requests actually do
2. How to measure current request usage
3. Step-by-step rightsizing process
4. Common pitfalls and how to avoid them
5. When to automate vs. do it manually
6. Next steps and related reading

**Internal link targets**
- Acme Cloud Kubernetes rightsizing feature page
- Cloud cost automation landing page
- VPA / autoscaling documentation
- Cluster cost dashboard overview

Note: I assumed the post is informational and India/English per your profile; no search volume or difficulty data is available to me. Keywords are drawn from the topic rather than supplied copy.
```

**Score:** intent_reading __/5 · structure __/5 · profile_awareness __/5

---

### `seo-out-of-scope` — marketing.seo-optimizer (out_of_scope)

**Request:** Design an ad creative for the free trial

**Reply:**

```
That is outside what I do. I am the **SEO Optimizer** — Search optimisation: keywords, titles, meta descriptions, on-page structure.

**Ad Creative Generator** handles this: Rendering a paid advertising creative image with offer and CTA.

Switch to it and send your message again, or ask me something in my area:

- SEO for a blog post about DevOps automation
- Title and meta for our pricing page
- Keyword ideas for a beginner Python course
```

---

### `campaign-ordinary-launch` — marketing.campaign-planner (ordinary)

**Request:** Plan a two week launch campaign for our cost automation feature

**Reply:**

```
**Assumptions**
- Start date assumed: next Monday (adjust if your launch date differs).
- No budget dollar amount was given, so I'm planning inside the small band (<$500/mo) and showing percentages only.
- Messaging leans on the standing rule: position on engineering time saved, never on price.

**Objective** — Generate qualified leads (demo requests / trial signups) for Acme Cloud's cost automation feature over the two-week launch window.

**Audience** — Developers and founders managing cloud infrastructure; the one thing they care about is reclaiming engineering time from manual cost tracking.

**Channel mix**

| Channel | Message angle | Format | Frequency |
|---|---|---|---|
| LinkedIn | "Stop babysitting cloud costs" — time saved | Text + image posts, 1 short video | 3x/week |
| Email | Launch + value proof to existing list | HTML email (2 sends) | Week 1 announce, Week 2 case/proof |
| Blog / SEO | Feature launch post + "automate cloud cost reviews" SEO article | Long-form articles | 1 each week |

Budget (within small band, percentages only): LinkedIn 40% (boosted posts), Email 20% (tooling), Blog/SEO 40% (content).

**Calendar**

| Day | Slot | What it needs |
|---|---|---|
| Mon W1 | Blog | Launch post: problem → feature → time saved |
| Tue W1 | LinkedIn | Announcement post + link to blog |
| Wed W1 | Email | Launch announcement to list |
| Thu W1 | LinkedIn | Short video: before/after workflow |
| Fri W1 | LinkedIn | Founder/dev quote or poll |
| Mon W2 | Blog | SEO article targeting "automate cloud cost reviews" |
| Tue W2 | LinkedIn | Customer-style proof point |
| Wed W2 | Email | Follow-up: proof + CTA to demo |
| Thu W2 | LinkedIn | Objection handling (setup time) |
| Fri W2 | LinkedIn | Recap + final CTA |

**Primary KPI** — Qualified leads (demo/trial signups) attributed to campaign (suggested target: set your own baseline +20%). Guardrail: email unsubscribe rate and LinkedIn engagement must not drop vs. prior 4-week average.

**Risks**
- Audience may care more about dollar savings than time saved; test messaging early.
- Two-week window is short for SEO to compound; blog supports, not drives, leads.
- Small budget limits paid reach; organic + email carry the load.

---
⚠️ **Unverified figures:** `40%`, `20%`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** objective_clarity __/5 · channel_choice __/5 · timeline_realism __/5 · kpi_quality __/5 · risks __/5

---

### `campaign-budget-supplied` — marketing.campaign-planner (complex)

**Request:** Plan a 6 week campaign to get 100 free trial signups. Budget is $400 total
across the whole six weeks. We have LinkedIn, email and our blog.

**Reply:**

```
**Objective** — Generate 100 free trial signups for Acme Cloud within 6 weeks, positioning on engineering time saved (never price).

**Audience** — Developers and Founders; the one thing they care about is getting engineering time back.

**Channel mix**

| Channel | Message angle | Format | Frequency |
|---|---|---|---|
| LinkedIn | Engineering time saved | Sponsored post + organic | 3x/week |
| Email | Time-saved case study | Newsletter + drip | 1x/week + drip |
| Blog / SEO | "How to reclaim engineering time" | Long-form post | 1/week |

**Calendar** (6 weeks; start date TBD)

| Week | Focus |
|---|---|
| 1 | Publish pillar blog post; launch email drip; LinkedIn organic teaser |
| 2 | LinkedIn sponsored push; email case study; SEO optimize pillar |
| 3 | Second blog post; LinkedIn carousel; email follow-up |
| 4 | Mid-campaign review; LinkedIn retargeting; email reminder |
| 5 | Third blog post; LinkedIn testimonials; email last-chance |
| 6 | Final push; recap email; LinkedIn wrap-up |

**Budget** — $400 total (your stated amount): LinkedIn ads $200, email tooling/list $100, blog content/boost $100. (suggestion)

**Primary KPI** — 100 trial signups (≈17/week). Guardrail: email unsubscribe rate stays below 0.5% and cost per signup ≤ $4 (suggested).

**Risks** — LinkedIn traffic may not convert to trials; content production bottleneck across 6 posts; audience fatigue from weekly email.

---
⚠️ **Unverified figures:** `0.5%`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** budget_handling __/5 · objective_clarity __/5 · kpi_quality __/5 · timeline_realism __/5

---

### `campaign-clarification` — marketing.campaign-planner (clarification)

**Request:** Plan a campaign

**Reply:**

```
I can plan this, but I need a bit more to work with. Two quick questions:

1. What's the campaign objective — e.g., lead generation, free trial signups, webinar registrations?
2. What's the time window and target audience (or should I assume developers and founders over a set period)?
```

**Score:** clarification_quality __/5 · no_fabrication __/5

---

### `campaign-grounding-no-invented-budget` — marketing.campaign-planner (grounding)

**Request:** Plan a one month awareness campaign on LinkedIn and email

**Reply:**

```
**Objective** — Grow awareness of Acme Cloud among developers and founders by lifting LinkedIn reach and email open reach by a suggested 20% over one month (baseline TBD by you).

**Audience** — Developers and founders; the one thing they care about is engineering time saved, not price.

**Channel mix**

| Channel | Message angle | Format | Frequency |
|---|---|---|---|
| LinkedIn | Engineering time saved | Thought-leadership posts, carousels | 3x/week |
| Email | Engineering time saved | Newsletter + product update | 1x/week |

**Calendar** (assuming a Monday start; adjust as needed)

| Week | LinkedIn (3 slots) | Email (1 slot) |
|---|---|---|
| 1 | Problem framing: where dev time leaks | Series intro + what's coming |
| 2 | How Acme Cloud saves engineering time | Short case study |
| 3 | Social proof / customer quotes | Practical tips |
| 4 | Recap + soft CTA to learn more | Wrap-up + resource link |

**Budget** — No amount stated; planning within your Small (<$500/mo) band. Suggested split: ~60% LinkedIn promotion, ~40% email tooling (suggestion only).

**Primary KPI** — LinkedIn impressions (single number deciding success). Guardrail: email unsubscribe rate must not increase.

**Risks** — (1) Audience fatigue from 3x/week posting without variety; (2) email list too small to move reach meaningfully; (3) messaging drifts toward price instead of time saved.

---
⚠️ **Unverified figures:** `20%`, `60%`, `40%`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** no_fabrication __/5 · budget_handling __/5 · channel_choice __/5

---

### `campaign-out-of-scope-write` — marketing.campaign-planner (out_of_scope)

**Request:** Write the Instagram caption for day one of the campaign

**Reply:**

```
That is outside what I do. I am the **Campaign Planner** — Planning marketing campaigns: objectives, channels, calendar, KPIs.

**Social Caption Writer** handles this: Writing post captions, social copy and ad copy.

Switch to it and send your message again, or ask me something in my area:

- Plan a 2 week launch campaign for our app
- Campaign to get 100 webinar signups
- A monthly content calendar for LinkedIn
```

---

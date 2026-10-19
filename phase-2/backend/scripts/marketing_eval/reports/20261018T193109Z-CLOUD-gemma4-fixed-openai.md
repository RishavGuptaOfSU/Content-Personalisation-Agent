# Marketing evaluation — CLOUD-gemma4-fixed

Generated 20261018T193109Z · 29 cases · 88s

## Configuration

| setting | value |
|---|---|
| `llm_provider` | openai |
| `llm_model` | gemma4:31b |
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

**108/108 assertions passed** across 29 cases.

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
| `seo-content-type-aware` | seo-optimizer | profile | 1/1 | 0 |
| `seo-out-of-scope` | seo-optimizer | out_of_scope | 4/4 | 0 |
| `campaign-ordinary-launch` | campaign-planner | ordinary | 4/4 | 0 |
| `campaign-budget-supplied` | campaign-planner | complex | 3/3 | 0 |
| `campaign-clarification` | campaign-planner | clarification | 3/3 | 0 |
| `campaign-grounding-no-invented-budget` | campaign-planner | grounding | 2/2 | 0 |
| `campaign-out-of-scope-write` | campaign-planner | out_of_scope | 4/4 | 0 |
| `campaign-routing` | — | routing | 2/2 | 0 |

## Outputs for qualitative scoring

Score each dimension 1–5 using `rubric.md`. The harness deliberately does
not score these.

### `copy-ordinary-linkedin` — marketing.social-copy (ordinary)

**Request:** Write a LinkedIn post about how much cloud spend sits idle

**Reply:**

```
Your cloud infrastructure is likely running resources you aren't using.

Idle instances and over-provisioned clusters drain your engineering momentum.

When your team spends hours auditing waste, they aren't shipping features.

Acme Cloud automates the cleanup so your developers can focus on building.

Stop managing waste and start deploying code.

#CloudComputing #DevOps #SaaS #EngineeringEfficiency

**Why this works**
It focuses on the loss of engineering time rather than monetary cost.
The structure uses a strong hook and single-sentence paragraphs for readability.
```

**Score:** hook __/5 · audience_fit __/5 · brand_tone __/5 · usefulness __/5 · no_filler __/5

---

### `copy-complex-thread` — marketing.social-copy (complex)

**Request:** Write a 3-post X thread explaining why we rebuilt our cost allocation engine.
Post 1 is the problem, post 2 the rebuild, post 3 the result. Keep each under
280 characters and number them.

**Reply:**

```
1/ Our original cost allocation engine couldn't keep up with complex infrastructure growth. It created visibility gaps that made it impossible for founders to see exactly where engineering resources were being spent.

2/ We rebuilt the engine from the ground up to handle granular tagging and real-time data processing. The new architecture eliminates manual reconciliation and automates the mapping of spend to specific features.

3/ The result is a massive reduction in time spent on financial auditing. Your engineering team can now focus on shipping code instead of chasing down cloud spend discrepancies.

**Why this works**
It follows a clear problem-solution-benefit narrative. It focuses on engineering time saved rather than price.
```

**Score:** instruction_following __/5 · hook __/5 · brand_tone __/5

---

### `copy-exact-constraint-hashtags` — marketing.social-copy (ordinary)

**Request:** LinkedIn post about our new pricing. Use at most 2 hashtags.

**Reply:**

```
Stop wasting engineering hours on cloud cost management.

Our new pricing model is designed to let your team focus on shipping features instead of auditing bills.

You get predictable scaling that aligns with your growth.

Spend your time building, not calculating.

Check the new tiers on our site.

#AcmeCloud #SaaS

**Why this works**
It focuses on the value of engineering time saved rather than the cost.
The structure follows the LinkedIn hook-and-single-sentence format for readability.
```

**Score:** instruction_following __/5

---

### `copy-no-hashtags-platform` — marketing.social-copy (platform)

**Request:** Write the Facebook post copy for our webinar on Thursday

**Reply:**

```
Are you spending more time managing your infrastructure than writing code?

We are hosting a webinar this Thursday to show you how to reclaim your engineering hours.

We will walk through the specific workflows that eliminate manual scaling and configuration overhead.

Register here to save your spot: [Link]

**Why this works**
It focuses on the pain point of wasted engineering time rather than cost.
The structure uses a conversational opener and a clear, explicit CTA.
```

**Score:** platform_fit __/5 · usefulness __/5

---

### `copy-grounding-no-metrics` — marketing.social-copy (grounding)

**Request:** Write a LinkedIn post about how much money we save customers

**Reply:**

```
I handle writing post captions, social copy, and ad copy; this request falls under the marketing domain's positioning, which is managed by a strategic agent.
```

**Score:** no_fabrication __/5 · brand_tone __/5

---

### `copy-memory-applied` — marketing.social-copy (memory)

**Request:** Another LinkedIn post, this time about staging environments left running

**Reply:**

```
Stop wasting engineering hours on ghost environments.

Staging servers left running after a sprint are more than just a cost leak.

They create configuration drift and maintenance overhead for your team.

Automating the teardown of these environments lets your developers focus on shipping code instead of managing infrastructure.

Check out how Acme Cloud handles automated cleanup.

#DevOps #SaaS #EngineeringEfficiency

**Why this works**
It targets a specific technical pain point for developers and founders.
It focuses on time and effort saved rather than monetary cost.
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

**Rendered:** `post-image-1792351800-8f6080c7.png` 1200×627 (41439 bytes)

**Alt text:** Bold text on a dark background discussing cloud cost automation for infrastructure efficiency.

**Spec from the model:**

```json
{
  "headline": "automate your cloud cost reduction",
  "subline": "stop manual tracking and eliminate wasted spend",
  "badge": "infrastructure efficiency",
  "cta": "learn more",
  "palette": "dark",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**automate your cloud cost reduction**
stop manual tracking and eliminate wasted spend

*1200×627 · CTA: learn more · dark palette*
```

**Score:** headline_relevance __/5 · headline_brevity __/5 · legibility __/5 · brand_fit __/5 · alt_text __/5

---

### `image-complex-detail` — marketing.post-image (complex)

**Request:** A post image announcing our Series A. The headline should lead on what it means
for customers, not on the amount. Add a short supporting line and a call to
action that points at the changelog.

**Rendered:** `post-image-1792351803-927e0439.png` 1200×627 (58329 bytes)

**Alt text:** Professional announcement graphic stating that series a funding will lead to faster feature delivery.

**Spec from the model:**

```json
{
  "headline": "faster feature delivery for your team",
  "subline": "our series a funding accelerates our product roadmap",
  "badge": "company news",
  "cta": "view the changelog",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**faster feature delivery for your team**
our series a funding accelerates our product roadmap

*1200×627 · CTA: view the changelog · brand palette*
```

**Score:** headline_relevance __/5 · instruction_following __/5 · legibility __/5

---

### `image-ambiguous` — marketing.post-image (ambiguous)

**Request:** Make us a graphic

**Rendered:** `post-image-1792351805-86fe4bd5.png` 1200×627 (61593 bytes)

**Alt text:** A professional bold graphic announcing automated scaling to save engineering time.

**Spec from the model:**

```json
{
  "headline": "deploy faster with automated scaling",
  "subline": "reduce manual infrastructure overhead for your engineering team",
  "badge": "developer tools",
  "cta": "learn more",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**deploy faster with automated scaling**
reduce manual infrastructure overhead for your engineering team

*1200×627 · CTA: learn more · brand palette*
```

**Score:** headline_relevance __/5 · graceful_degradation __/5

---

### `image-brand-colours` — marketing.post-image (brand)

**Request:** Instagram square graphic announcing our new usage-based pricing

**Rendered:** `post-image-1792351807-0389a19c.png` 1200×627 (50764 bytes)

**Alt text:** A bold graphic announcing the transition to usage-based pricing for Acme Cloud.

**Spec from the model:**

```json
{
  "headline": "usage-based pricing is here",
  "subline": "pay only for the resources you actually use",
  "badge": "new update",
  "cta": "learn more",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**usage-based pricing is here**
pay only for the resources you actually use

*1200×627 · CTA: learn more · brand palette*
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

**Rendered:** `ad-creative-1792351829-da497e01.png` 1080×1080 (93859 bytes)

**Alt text:** Professional ad showing a clean code interface with a call to start a free trial.

**Spec from the model:**

```json
{
  "headline": "Ship code faster with less effort",
  "subline": "Automated infrastructure management for engineering teams",
  "badge": "Free trial",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "split",
  "style": ""
}
```

**Reply:**

```
**Ship code faster with less effort**
Automated infrastructure management for engineering teams

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · objective_alignment __/5 · legibility __/5 · alt_text __/5

---

### `ad-supplied-offer` — marketing.ad-creative (ordinary)

**Request:** Ad image promoting 30% off annual plans until 31 March

**Rendered:** `ad-creative-1792351831-615740fb.png` 1080×1080 (95066 bytes)

**Alt text:** Professional brand image with a 30% discount badge and call to action for a free trial.

**Spec from the model:**

```json
{
  "headline": "Scale Your Infrastructure Faster",
  "subline": "Enterprise cloud tools for developers and founders",
  "badge": "30% off annual plans",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "split",
  "style": ""
}
```

**Reply:**

```
**Scale Your Infrastructure Faster**
Enterprise cloud tools for developers and founders

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · offer_fidelity __/5

---

### `ad-grounding-no-invented-offer` — marketing.ad-creative (grounding)

**Request:** Make an ad creative that will get engineering managers to sign up

**Rendered:** `ad-creative-1792351833-fc0cbcaa.png` 1080×1080 (87061 bytes)

**Alt text:** Professional ad showing a streamlined cloud infrastructure dashboard with a call to action for a free trial.

**Spec from the model:**

```json
{
  "headline": "Ship Features Faster",
  "subline": "Automate infrastructure management for your engineering team",
  "badge": "Free trial",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "split",
  "style": ""
}
```

**Reply:**

```
**Ship Features Faster**
Automate infrastructure management for your engineering team

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
Since you didn't provide the page copy, I am assuming your core value proposition focuses on engineering efficiency and automated cost reduction for SaaS teams.

**Primary keyword** — cloud cost automation (commercial)

**Secondary keywords**
- cloud spend optimization
- automated cloud cost management
- reduce cloud waste
- cloud financial management for developers
- cloud cost governance tools

**Title tag** — Cloud Cost Automation for Developers | Acme Cloud (52 characters)

**Meta description** — Stop wasting engineering hours on manual cloud billing. Automate your cost optimization and reclaim your sprint capacity with Acme Cloud. (142 characters)

**H2 outline**
*   **The Offer:** Automate your cloud cost management to save engineering time.
*   **Proof:** How leading SaaS teams reduced waste without manual auditing.
*   **The Problem:** Why manual cost tracking kills developer productivity.
*   **The Solution:** Key automation features (Right-sizing, scheduling, anomaly detection).
*   **Implementation:** How to integrate Acme Cloud into your existing workflow.
*   **Final CTA:** Start automating your cloud spend.

**Internal link targets**
- Pricing page (for plan tiers)
- Documentation (for integration guides)
- Case studies (for proof of engineering time saved)
```

**Score:** intent_reading __/5 · keyword_relevance __/5 · structure __/5 · actionability __/5

---

### `seo-grounding-no-volumes` — marketing.seo-optimizer (grounding)

**Request:** Give me the search volume and keyword difficulty for 'cloud cost tool'

**Reply:**

```
I cannot see search volume or keyword difficulty; you would need a tool like Ahrefs, SEMrush, or Google Keyword Planner for those figures.
```

**Score:** no_fabrication __/5 · honesty_about_limits __/5

---

### `seo-attachment` — marketing.seo-optimizer (attachment)

**Request:** Optimise this page copy for search

**Reply:**

```
Based on the copy provided, I have focused on the core value of identifying idle capacity to save engineering effort.

**Primary keyword** — cloud cost automation (commercial)

**Secondary keywords**
- idle cloud capacity
- cloud waste detection
- cloud resource optimization
- automated cloud auditing
- engineering efficiency tools

**Title tag** — Cloud Cost Automation for Engineering Teams | Acme Cloud (56 characters)

**Meta description** — Automatically find and remove idle cloud capacity. Stop wasting engineering time on manual audits. Trusted by high-growth teams. (138 characters)

**H2 outline**
- Stop wasting engineering hours on manual cloud audits (The Offer)
- Trusted by engineering teams at scale (Proof)
- How Acme Cloud detects idle capacity (Process)
- Reclaim your sprint capacity (Value/Outcome)
- Get started with Acme Cloud (CTA)

**Internal link targets**
- Pricing page
- Documentation/Integration guide
- Case studies (Engineering efficiency)

**Observations vs. Assumptions**
- **Observed:** The copy explicitly mentions finding idle capacity automatically and being trusted by engineering teams.
- **Assumed:** Since the goal is a landing page for developers and founders, I have assumed the "cost" being optimized is not just monetary, but the operational overhead (engineering time) required to manage it.
```

**Score:** uses_source_material __/5 · keyword_relevance __/5 · structure __/5

---

### `seo-content-type-aware` — marketing.seo-optimizer (profile)

**Request:** SEO for a blog post about rightsizing Kubernetes requests

**Reply:**

```
Since this is a blog post, I have structured the H2s to answer the core technical question first before expanding into broader optimization strategies.

**Primary keyword** — rightsizing kubernetes requests (informational)

**Secondary keywords**
- K8s resource limits vs requests
- Kubernetes VPA configuration
- optimize pod resource allocation
- kubernetes cpu throttling
- memory limit tuning

**Title tag** — How to Rightsize Kubernetes Requests for Performance (56 characters)

**Meta description** — Stop wasting cluster resources. Learn how to accurately rightsize Kubernetes requests to prevent throttling and save engineering time. (142 characters)

**H2 outline**
- What is Kubernetes Rightsizing? (The direct answer)
- The Difference Between Requests and Limits
- Signs Your Pods are Under- or Over-Provisioned
- Step-by-Step Guide to Rightsizing Your Requests
- Automating the Process with Vertical Pod Autoscaler (VPA)
- Measuring Success: Engineering Time Saved vs. Resource Waste

**Internal link targets**
- Cloud cost automation landing page
- Kubernetes monitoring documentation
- Guide to cluster autoscaling
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
I am producing a plan based on **Assumptions** because no specific objective, audience segment, or time window was provided.

**Assumptions**
- Objective: Generate 50 new trial sign-ups (suggestion).
- Audience: Founders who care about reducing engineering overhead.
- Window: 14 days starting next Monday.

**Objective**
Generate 50 new trial sign-ups for the cost automation feature by emphasizing engineering time saved.

**Audience**
Founders; they care about reclaiming developer hours spent on manual infrastructure management.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering efficiency | Text-based thought leadership | 3x per week |
| Email | Operational overhead | Direct outreach / Newsletter | 2x per campaign |
| Blog / SEO | Automation vs. Manual | Long-form guide | 1x per campaign |

**Calendar**
| Date | LinkedIn | Email | Blog |
| :--- | :--- | :--- | :--- |
| Day 1 | Teaser: The cost of manual work | - | - |
| Day 3 | Feature announcement | Launch Email 1 | - |
| Day 5 | Case study: Hours saved | - | Deep-dive Guide |
| Day 8 | Common automation pitfalls | - | - |
| Day 10 | Comparison: Manual vs. Auto | Follow-up Email 2 | - |
| Day 12 | User testimonial | - | - |
| Day 14 | Final call to action | - | - |

**Budget**
I have planned this within your small budget band (<$500/mo).

**Primary KPI**
Number of new trial sign-ups (suggestion: 50), with a guardrail metric of maintaining a lead-to-customer conversion rate of at least 5% (suggestion).

**Risks**
- Messaging focuses too much on cost savings rather than engineering time.
- Low email open rates due to poor subject line alignment with founder pain points.

---
⚠️ **Unverified figures:** `2x`, `1x`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** objective_clarity __/5 · channel_choice __/5 · timeline_realism __/5 · kpi_quality __/5 · risks __/5

---

### `campaign-budget-supplied` — marketing.campaign-planner (complex)

**Request:** Plan a 6 week campaign to get 100 free trial signups. Budget is $400 total
across the whole six weeks. We have LinkedIn, email and our blog.

**Reply:**

```
I am producing a plan based on the following **Assumptions**: your target audience is Developers and Founders who care about saving engineering time, and the campaign window starts next Monday.

**Objective** — Generate 100 free trial signups for Acme Cloud within six weeks.

**Audience** — Developers and Founders; they care about reducing manual engineering overhead.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering time saved | Text-based thought leadership | 3x / week |
| Email | Efficiency gains vs. manual work | Direct outreach / Newsletter | 1x / week |
| Blog / SEO | Technical "How-to" for efficiency | Long-form guide | 1x / week |

**Calendar**
| Week | Blog Focus | LinkedIn Focus | Email Focus |
| :--- | :--- | :--- | :--- |
| 1 | The cost of manual setup | Problem awareness | Introduction to efficiency |
| 2 | Workflow optimization guide | Solution teaser | Case study: Time saved |
| 3 | Scaling without adding headcount | Feature deep-dive | Direct trial invitation |
| 4 | Common engineering bottlenecks | Comparison (Manual vs. Acme) | Reminder: Time recovery |
| 5 | Integration best practices | User success stories | Final push for trial |
| 6 | Future of automated infra | Urgency/Last call | Closing offer |

**Budget**
I have allocated your $400 total as follows:
- LinkedIn Sponsored Content: $250 (suggestion)
- Email Tooling/Lead List: $100 (suggestion)
- Blog Distribution/Promotion: $50 (suggestion)

**Primary KPI** — Total number of free trial signups.
**Guardrail Metric** — Email unsubscribe rate.

**Risks**
1. Messaging focuses too much on features rather than engineering time saved.
2. Low organic reach on LinkedIn limiting the top-of-funnel flow.
```

**Score:** budget_handling __/5 · objective_clarity __/5 · kpi_quality __/5 · timeline_realism __/5

---

### `campaign-clarification` — marketing.campaign-planner (clarification)

**Request:** Plan a campaign

**Reply:**

```
I handle planning marketing objectives, channels, calendars, and KPIs. Since you didn't provide a goal, audience, or timeframe, I need a bit more info:

1. What is the specific objective or product feature you are promoting?
2. What is the duration of the campaign?
```

**Score:** clarification_quality __/5 · no_fabrication __/5

---

### `campaign-grounding-no-invented-budget` — marketing.campaign-planner (grounding)

**Request:** Plan a one month awareness campaign on LinkedIn and email

**Reply:**

```
Since you didn't specify a target audience or a specific goal for this awareness push, I am proceeding with **Assumptions**.

**Assumptions**
- Objective: Increase brand visibility among Developers and Founders.
- Audience: Technical decision-makers who care about reducing engineering toil.
- Time window: 30 days.

**Objective**
Increase monthly unique website visits from LinkedIn and Email by 20% (suggested figure) to build a top-of-funnel lead pool.

**Audience**
Developers and Founders; they care about reclaiming engineering time spent on infrastructure.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering time saved | Thought-leadership text | 3x / week |
| Email | Efficiency gains | Educational newsletter | 1x / week |

**Calendar**
| Week | LinkedIn Focus | Email Focus |
| :--- | :--- | :--- |
| Week 1 | The cost of manual toil | Introduction to efficiency |
| Week 2 | Case study: Time reclaimed | Tooling comparison |
| Week 3 | Common engineering bottlenecks | The "Future State" of dev-ops |
| Week 4 | Summary of time-saving wins | Call to action for discovery |

**Budget**
I have planned this within your small budget band (<$500/mo), focusing on organic reach and existing email lists.

**Primary KPI**
Total unique landing page visits (suggested figure), with a guardrail metric of Email Unsubscribe Rate (must not increase).

**Risks**
- Content feels too generic to attract high-level Founders.
- Low engagement if the LinkedIn posts don't spark technical discussion.
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

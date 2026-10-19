# Marketing evaluation — VERIFY-single-gemma4

Generated 20261019T054624Z · 30 cases · 54s

## Configuration

| setting | value |
|---|---|
| `llm_provider` | openai |
| `llm_model` | gemma4:31b |
| `agent_models` | {} |
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

**109/110 assertions passed** across 30 cases.

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
| `campaign-budget-supplied` | campaign-planner | complex | 3/3 | 0 |
| `campaign-clarification` | campaign-planner | clarification | 3/3 | 0 |
| `campaign-grounding-no-invented-budget` | campaign-planner | grounding | 1/2 | 1 |
| `campaign-out-of-scope-write` | campaign-planner | out_of_scope | 4/4 | 0 |
| `campaign-routing` | — | routing | 2/2 | 0 |

### Failed assertions

- `campaign-grounding-no-invented-budget` — no figures the user did not supply → 1%

## Outputs for qualitative scoring

Score each dimension 1–5 using `rubric.md`. The harness deliberately does
not score these.

### `copy-ordinary-linkedin` — marketing.social-copy (ordinary)

**Request:** Write a LinkedIn post about how much cloud spend sits idle

**Reply:**

```
Your cloud infrastructure is likely leaking engineering hours.

Idle resources do more than waste budget.

They create operational noise and maintenance overhead for your team.

When you automate the cleanup of unused instances, you give your developers their focus back.

Stop managing waste and start shipping features.

Book a demo to see how Acme Cloud optimizes your environment.

#CloudComputing #DevOps #SaaS #EngineeringEfficiency

**Why this works**
It focuses on the loss of engineering time rather than cost.
The structure uses a strong hook and a clear, single CTA.
```

**Score:** hook __/5 · audience_fit __/5 · brand_tone __/5 · usefulness __/5 · no_filler __/5

---

### `copy-complex-thread` — marketing.social-copy (complex)

**Request:** Write a 3-post X thread explaining why we rebuilt our cost allocation engine.
Post 1 is the problem, post 2 the rebuild, post 3 the result. Keep each under
280 characters and number them.

**Reply:**

```
1/ Our old cost allocation engine couldn't keep up with complex infrastructure. Developers spent hours manually tagging resources and chasing leaks instead of shipping code.

2/ We rebuilt the engine from the ground up to automate attribution. By shifting to a real-time mapping system, we eliminated the need for manual overhead.

3/ The result is a massive reduction in engineering toil. Your team now gets precise visibility into spend without sacrificing a single hour of development time.

**Why this works**
Focuses on engineering time saved rather than price.
Follows a clear problem-solution-result narrative arc.
```

**Score:** instruction_following __/5 · hook __/5 · brand_tone __/5

---

### `copy-exact-constraint-hashtags` — marketing.social-copy (ordinary)

**Request:** LinkedIn post about our new pricing. Use at most 2 hashtags.

**Reply:**

```
Stop wasting engineering hours on cloud cost management.

Our new pricing structure is designed to let your team focus on shipping features instead of auditing bills.

You get predictable costs that scale with your growth.

Reclaim your development cycle today.

Check the new plans on our site.

#AcmeCloud #SaaS

**Why this works**
Focuses on engineering time saved rather than price points to appeal to technical founders.
Uses a clean, single-sentence structure for high readability on LinkedIn.
```

**Score:** instruction_following __/5

---

### `copy-no-hashtags-platform` — marketing.social-copy (platform)

**Request:** Write the Facebook post copy for our webinar on Thursday

**Reply:**

```
Stop wasting your engineering cycles on infrastructure overhead.

Join us this Thursday for a live webinar where we show you how to automate your cloud environment. 

You will learn how to reclaim your team's time and focus on shipping features instead of managing servers.

Register here: [Link]

**Why this works**
Focuses on engineering time saved rather than cost. Uses a direct, conversational tone suited for Facebook.
```

**Score:** platform_fit __/5 · usefulness __/5

---

### `copy-grounding-no-metrics` — marketing.social-copy (grounding)

**Request:** Write a LinkedIn post about how much money we save customers

**Reply:**

```
I handle writing post captions, social copy and ad copy; positioning on cost savings falls under the strategy handled by a Marketing Strategist.
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

Automate your teardowns to keep your infrastructure clean.

Reclaim your focus for building features that matter.

Check out our automation tools here: [Link]

#DevOps #CloudComputing #SaaS

**Why this works**
It targets the pain of maintenance overhead rather than cost.
The structure uses a strong hook and a clear, single CTA.
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

**Rendered:** `post-image-1792388744-c3b5f4f9.png` 1200×627 (57503 bytes)

**Alt text:** Bold text on a brand-colored background discussing cloud cost automation.

**Spec from the model:**

```json
{
  "headline": "automate your cloud cost reduction",
  "subline": "eliminate manual waste with automated scaling and scheduling",
  "badge": "cloud efficiency",
  "cta": "learn how",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**automate your cloud cost reduction**
eliminate manual waste with automated scaling and scheduling

*1200×627 · CTA: learn how · brand palette*
```

**Score:** headline_relevance __/5 · headline_brevity __/5 · legibility __/5 · brand_fit __/5 · alt_text __/5

---

### `image-complex-detail` — marketing.post-image (complex)

**Request:** A post image announcing our Series A. The headline should lead on what it means
for customers, not on the amount. Add a short supporting line and a call to
action that points at the changelog.

**Rendered:** `post-image-1792388747-b5c31c93.png` 1200×627 (56357 bytes)

**Alt text:** Professional announcement graphic stating that Series A funding will lead to faster feature shipping.

**Spec from the model:**

```json
{
  "headline": "faster feature shipping for your team",
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
**faster feature shipping for your team**
our series a funding accelerates our product roadmap

*1200×627 · CTA: view the changelog · brand palette*
```

**Score:** headline_relevance __/5 · instruction_following __/5 · legibility __/5

---

### `image-ambiguous` — marketing.post-image (ambiguous)

**Request:** Make us a graphic

**Rendered:** `post-image-1792388748-d923f376.png` 1200×627 (62564 bytes)

**Alt text:** Bold text on a brand-colored background announcing automated scaling to save engineering time.

**Spec from the model:**

```json
{
  "headline": "deploy faster with automated scaling",
  "subline": "reduce manual infrastructure overhead for your engineering team",
  "badge": "platform update",
  "cta": "explore the docs",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**deploy faster with automated scaling**
reduce manual infrastructure overhead for your engineering team

*1200×627 · CTA: explore the docs · brand palette*
```

**Score:** headline_relevance __/5 · graceful_degradation __/5

---

### `image-brand-colours` — marketing.post-image (brand)

**Request:** Instagram square graphic announcing our new usage-based pricing

**Rendered:** `post-image-1792388750-43509ea7.png` 1200×627 (50764 bytes)

**Alt text:** A bold professional graphic announcing the transition to usage-based pricing for Acme Cloud.

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

**Rendered:** `ad-creative-1792388752-0efae1b0.png` 1080×1080 (90824 bytes)

**Alt text:** Professional blue and dark navy ad with centered text promoting a free trial for engineering teams.

**Spec from the model:**

```json
{
  "headline": "Ship code faster with less effort",
  "subline": "Automated cloud infrastructure for engineering teams",
  "badge": "Free trial",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Ship code faster with less effort**
Automated cloud infrastructure for engineering teams

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · objective_alignment __/5 · legibility __/5 · alt_text __/5

---

### `ad-supplied-offer` — marketing.ad-creative (ordinary)

**Request:** Ad image promoting 30% off annual plans until 31 March

**Rendered:** `ad-creative-1792388754-771c7a37.png` 1080×1080 (95681 bytes)

**Alt text:** Professional cloud infrastructure graphic with a discount offer for annual plans.

**Spec from the model:**

```json
{
  "headline": "Scale Your Infrastructure Faster",
  "subline": "Deploy cloud resources with professional precision",
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
Deploy cloud resources with professional precision

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · offer_fidelity __/5

---

### `ad-grounding-no-invented-offer` — marketing.ad-creative (grounding)

**Request:** Make an ad creative that will get engineering managers to sign up

**Rendered:** `ad-creative-1792388756-56b88790.png` 1080×1080 (86957 bytes)

**Alt text:** Professional ad showing a streamlined cloud infrastructure interface with a call to start a free trial.

**Spec from the model:**

```json
{
  "headline": "Ship Features Faster",
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
**Ship Features Faster**
Automated infrastructure management for engineering teams

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
Since you didn't provide the page copy, I am assuming your focus is on reducing manual overhead for engineering teams rather than just lowering the monthly bill.

**Primary keyword** — cloud cost automation (commercial)

**Secondary keywords**
- automated cloud cost optimization
- cloud spend management for developers
- reduce cloud waste automatically
- cloud cost governance tools
- FinOps automation software

**Title tag** — Cloud Cost Automation for Engineering Teams | Acme Cloud (56 characters)

**Meta description** — Stop wasting engineering hours on manual cost tracking. Automate your cloud spend management and eliminate waste with Acme Cloud. (138 characters)

**H2 outline**
- Stop wasting engineering cycles on manual cost tracking (The Offer)
- How Acme Cloud automates your cloud spend (The Solution)
- Trusted by engineering leaders at scale (Proof/Social Validation)
- From manual spreadsheets to automated governance (The Transition/Benefit)
- Integration and deployment specs (Technical Specs)
- Ready to reclaim your engineering time? (CTA)

**Internal link targets**
- Product features page
- Case studies (Engineering efficiency)
- Documentation (API/Integration)
- Pricing page
```

**Score:** intent_reading __/5 · keyword_relevance __/5 · structure __/5 · actionability __/5

---

### `seo-grounding-no-volumes` — marketing.seo-optimizer (grounding)

**Request:** Give me the search volume and keyword difficulty for 'cloud cost tool'

**Reply:**

```
I handle keywords, titles, meta descriptions, and on-page structure; however, I cannot provide search volume or keyword difficulty as I have no access to live search data. You would need a tool like Ahrefs, SEMrush, or Google Keyword Planner to get those figures.
```

**Score:** no_fabrication __/5 · honesty_about_limits __/5

---

### `seo-attachment` — marketing.seo-optimizer (attachment)

**Request:** Optimise this page copy for search

**Reply:**

```
Based on the copy provided, I've focused on the core value of identifying idle capacity to save engineering time.

**Observation:** The copy explicitly mentions automatic discovery of idle cloud capacity and trust from engineering teams.
**Assumption:** I am assuming the target user is looking for a way to reduce manual cloud auditing to free up developer hours.

**Primary keyword** — cloud cost automation (commercial)

**Secondary keywords**
- idle cloud capacity
- cloud resource optimization
- automated cloud auditing
- cloud waste detection
- engineering productivity tools

**Title tag** — Cloud Cost Automation for Engineering Teams | Acme Cloud (56 characters)

**Meta description** — Automatically find idle cloud capacity and stop wasting engineering time on manual audits. Trusted by top dev teams. (118 characters)

**H2 outline**
- Stop wasting engineering hours on manual cloud audits (The Offer)
- Trusted by engineering teams at scale (Proof)
- How Acme Cloud detects idle capacity (How it works)
- Reclaim your roadmap by automating resource cleanup (Benefit/Value)
- Connect your account in minutes (Call to Action)

**Internal link targets**
- Documentation: Connection guide
- Blog: Guide to identifying zombie resources
- Pricing/Plans page
```

**Score:** uses_source_material __/5 · keyword_relevance __/5 · structure __/5

---

### `seo-content-type-aware` — marketing.seo-optimizer (profile)

**Request:** SEO for our Kubernetes rightsizing feature

**Reply:**

```
Since you didn't provide page copy, I am assuming this is a feature-specific landing page focused on automating resource allocation to save engineering hours.

**Primary keyword** — Kubernetes rightsizing (Commercial)

**Secondary keywords**
- K8s resource optimization
- automated pod autoscaling
- Kubernetes cost efficiency
- reduce cloud waste
- CPU and memory rightsizing
- Kubernetes resource limits

**Title tag** — Kubernetes Rightsizing: Automate Resource Optimization (56 characters)

**Meta description** — Stop wasting engineering hours on manual tuning. Automate your Kubernetes rightsizing to optimize performance and reduce cloud waste. (141 characters)

**H2 outline**
- **The Solution:** Automated Kubernetes Rightsizing (Lead with the offer: how it removes the manual burden from devs)
- **Stop the Manual Tuning Cycle** (Proof/Pain: contrast manual YAML editing vs. automated optimization)
- **How it Works** (Technical mechanism: observation, recommendation, and application)
- **Reclaim Your Engineering Time** (Value prop: focus on velocity and stability over manual cost-cutting)
- **Integration and Deployment** (Ease of setup for existing clusters)
- **Ready to Automate Your Cluster?** (Final CTA)

**Internal link targets**
- Cloud cost automation landing page
- Documentation: Installation guide
- Pricing page
- Blog: Guide to K8s resource limits
```

**Score:** intent_reading __/5 · structure __/5 · profile_awareness __/5

---

### `seo-request-overrides-profile` — marketing.seo-optimizer (profile)

**Request:** SEO for a blog post about rightsizing Kubernetes requests

**Reply:**

```
**Primary keyword** — Kubernetes rightsizing (informational)

**Secondary keywords**
- K8s resource requests and limits
- Kubernetes cost optimization
- pod autoscaling best practices
- rightsizing containers
- Kubernetes CPU and memory tuning

**Title tag** — How to Rightsize Kubernetes Requests for Better Performance (58)

**Meta description** — Stop wasting engineering time on manual tuning. Learn how to rightsize Kubernetes requests to optimize performance and reduce cloud waste. (142)

**H2 outline**
- What is Kubernetes rightsizing and why it matters
- The impact of incorrect resource requests on cluster stability
- Step-by-step guide to analyzing pod resource usage
- Automating the rightsizing process to save engineering hours
- Common pitfalls when setting CPU and memory limits
- Measuring the success of your rightsizing strategy

**Internal link targets**
- Kubernetes rightsizing feature landing page
- Cloud cost automation overview
- Documentation on resource quota management
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
Since you didn't specify an objective or audience, I am producing a plan based on **Assumptions**.

**Assumptions**
- Objective: Generate 50 new trial sign-ups (suggested).
- Audience: Founders who care about reducing engineering overhead.
- Time window: 14 days.

**Objective**
Generate 50 new trial sign-ups for the cost automation feature within two weeks.

**Audience**
Founders; they care about reclaiming engineering time spent on manual cost management.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering time saved | Text-based post | 3x per week |
| Email | Automation vs. Manual toil | Direct outreach | 2x per week |
| Blog / SEO | Guide to cost automation | Long-form article | 1x total |

**Calendar**
| Day | LinkedIn | Email | Blog |
| :--- | :--- | :--- | :--- |
| 1 | Teaser: The cost of manual toil | - | - |
| 3 | Feature reveal: Time saved | Announcement | Launch Article |
| 5 | - | Case study/Use case | - |
| 8 | User pain point: Manual audits | - | - |
| 10 | - | Direct CTA to trial | - |
| 12 | Comparison: Before vs After | - | - |
| 14 | Last call for launch offer | Final reminder | - |

**Budget**
I have planned this within your small budget band (<$500/mo).

**Primary KPI**
Number of new trial sign-ups (suggested: 50), with a guardrail metric of maintaining a <5% email unsubscribe rate.

**Risks**
- Messaging focuses too much on price rather than engineering time.
- Low organic reach on LinkedIn limiting the top-of-funnel flow.

---
⚠️ **Unverified figures:** `1x`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** objective_clarity __/5 · channel_choice __/5 · timeline_realism __/5 · kpi_quality __/5 · risks __/5

---

### `campaign-budget-supplied` — marketing.campaign-planner (complex)

**Request:** Plan a 6 week campaign to get 100 free trial signups. Budget is $400 total
across the whole six weeks. We have LinkedIn, email and our blog.

**Reply:**

```
Since you didn't specify a target audience or time window beyond the duration, I am proceeding with **Assumptions**.

**Assumptions**
- Audience: Founders who care about reducing engineering overhead.
- Time window: Starting next Monday for 6 weeks.

**Objective**
Generate 100 free trial signups for Acme Cloud within 6 weeks.

**Audience**
Founders; they care about reclaiming engineering time to focus on product growth.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering time saved | Text-based thought leadership | 3x / week |
| Email | Efficiency gains vs. manual setup | Direct outreach/Newsletter | 1x / week |
| Blog | Technical "How-to" for efficiency | Long-form guide | 1x / week |

**Calendar**
| Week | Blog Focus | Email Focus | LinkedIn Focus |
| :--- | :--- | :--- | :--- |
| 1 | The cost of manual infra | Intro to time-saving | Problem awareness |
| 2 | Workflow optimization | Case study: Time saved | Solution benefits |
| 3 | Scaling without hiring | Comparison: Manual vs. Acme | Feature deep-dive |
| 4 | Reducing dev burnout | The "Founder's Dilemma" | User testimonials |
| 5 | Automation blueprints | Direct trial invitation | Urgency/Efficiency |
| 6 | Future-proofing your stack | Final trial push | Recap & Results |

**Budget**
Total: $400 (allocated as requested).
- LinkedIn Sponsored Content: $250 (suggestion)
- Email Tooling/List growth: $100 (suggestion)
- Blog Promotion/Distribution: $50 (suggestion)

**Primary KPI**
Total free trial signups (Target: 100).
Guardrail: Cost per lead (CPL) must not exceed $4.00 (suggestion).

**Risks**
- High friction in the signup flow causing drop-offs.
- Messaging focusing too much on features rather than time saved.
```

**Score:** budget_handling __/5 · objective_clarity __/5 · kpi_quality __/5 · timeline_realism __/5

---

### `campaign-clarification` — marketing.campaign-planner (clarification)

**Request:** Plan a campaign

**Reply:**

```
I will produce a plan based on assumptions since your request didn't include an objective, audience, or timeframe.

**Assumptions**
- Objective: Generate 20 new free trial sign-ups.
- Audience: Founders who care about reducing engineering overhead.
- Time window: 30 days.

**Objective**
Secure 20 new free trial sign-ups for Acme Cloud within 30 days.

**Audience**
Founders; they care about reclaiming engineering time to focus on core product features.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering time saved | Text-based thought leadership | 2x per week |
| Email | Solving dev bottlenecks | Direct outreach/Newsletter | 1x per week |
| Blog / SEO | Technical efficiency guides | Long-form "How-to" | 1x per week |

**Calendar**
| Date | LinkedIn | Email | Blog |
| :--- | :--- | :--- | :--- |
| Week 1 | Post: The cost of dev toil | Intro: The time-save angle | Guide: Optimizing dev workflows |
| Week 2 | Post: Scaling without hiring | Case study: Time recovered | — |
| Week 3 | Post: Technical debt vs. Speed | Direct offer: Trial access | Guide: Reducing infrastructure lag |
| Week 4 | Post: Founder's focus | Final reminder: Trial access | — |

**Budget**
I have planned this within your small budget band (<$500/mo), focusing primarily on organic reach and existing lists.

**Primary KPI**
Number of new trial sign-ups (Suggested: 20), with a guardrail metric of maintaining a lead-to-trial conversion rate of at least 5% (suggested).

**Risks**
- Messaging focuses too much on the tool rather than the time saved.
- Low organic reach on LinkedIn limiting the top-of-funnel flow.
```

**Score:** clarification_quality __/5 · no_fabrication __/5

---

### `campaign-grounding-no-invented-budget` — marketing.campaign-planner (grounding)

**Request:** Plan a one month awareness campaign on LinkedIn and email

**Reply:**

```
I am producing a plan based on **Assumptions** because your request did not specify an objective, audience, or time window.

**Assumptions**
- Objective: Increase brand awareness among developers.
- Audience: Senior Developers who care about reducing wasted engineering hours.
- Window: 30 days.

**Objective**
Increase monthly unique website visits from LinkedIn and Email by 15% (suggested).

**Audience**
Senior Developers; they care about reclaiming their time from tedious infrastructure maintenance.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering time saved | Text + Image | 2x / week |
| Email | Efficiency gains | Newsletter/Direct | 1x / week |

**Calendar**
| Week | LinkedIn Focus | Email Focus |
| :--- | :--- | :--- |
| Week 1 | The cost of manual setup | Introduction to efficiency |
| Week 2 | Comparison: Old vs. New way | Case study: Hours saved |
| Week 3 | Common engineering bottlenecks | Technical deep-dive |
| Week 4 | Scaling without adding headcount | Summary of benefits |

**Budget**
I have planned this within your small budget band (<$500/mo).

**Primary KPI**
Total unique landing page views (suggested), with a guardrail of maintaining a <1% email unsubscribe rate.

**Risks**
- Content feels too "salesy" for a developer audience.
- Low engagement due to lack of technical depth in the LinkedIn posts.

---
⚠️ **Unverified figures:** `1%`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
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

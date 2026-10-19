# Marketing evaluation — CLOUD-gemma4-cases-fixed

Generated 20261018T205401Z · 30 cases · 49s

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

**110/110 assertions passed** across 30 cases.

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
Your cloud infrastructure is likely leaking engineering hours.

Idle resources do more than waste budget.

They create operational noise and maintenance overhead for your team.

When you stop managing ghost instances, your developers can focus on shipping features instead of auditing spreadsheets.

Reclaim your team's focus by automating resource cleanup.

Check out our guide to lean infrastructure.

#CloudComputing #DevOps #SaaS #EngineeringEfficiency #AcmeCloud

**Why this works**
It pivots the conversation from financial cost to engineering time, hitting a primary pain point for founders.
```

**Score:** hook __/5 · audience_fit __/5 · brand_tone __/5 · usefulness __/5 · no_filler __/5

---

### `copy-complex-thread` — marketing.social-copy (complex)

**Request:** Write a 3-post X thread explaining why we rebuilt our cost allocation engine.
Post 1 is the problem, post 2 the rebuild, post 3 the result. Keep each under
280 characters and number them.

**Reply:**

```
1/ Our old cost allocation engine couldn't keep pace with your scaling infrastructure. Tracking spend across fragmented environments became a manual burden for your engineering teams.

2/ We rebuilt the engine from the ground up to automate resource tagging and attribution. The new architecture handles high-cardinality data in real-time without lagging.

3/ You now get precise visibility into where your resources go. This eliminates the manual audit cycle and lets your developers focus on shipping code instead of spreadsheets.

**Why this works**
It follows a clear problem-solution-benefit narrative.
It focuses on engineering time saved rather than pricing.
```

**Score:** instruction_following __/5 · hook __/5 · brand_tone __/5

---

### `copy-exact-constraint-hashtags` — marketing.social-copy (ordinary)

**Request:** LinkedIn post about our new pricing. Use at most 2 hashtags.

**Reply:**

```
Stop wasting engineering hours on manual cost optimization.

Acme Cloud now offers a pricing structure that scales with your actual usage.

You can focus on shipping features instead of managing infrastructure overhead.

Check the new tiers on our site.

#AcmeCloud #SaaS

**Why this works**
It focuses on engineering time saved rather than price.
The structure follows the LinkedIn hook and single-sentence paragraph format.
```

**Score:** instruction_following __/5

---

### `copy-no-hashtags-platform` — marketing.social-copy (platform)

**Request:** Write the Facebook post copy for our webinar on Thursday

**Reply:**

```
Ever feel like your engineering team is spending more time managing infrastructure than shipping features?

We are hosting a webinar this Thursday to show you how to reclaim those hours. We will dive into the specific workflows that eliminate manual overhead and get your developers back to building.

Register here to save your spot: [Link]

**Why this works**
Focuses on the pain point of wasted engineering time rather than cost.
Uses a conversational tone with a clear, direct call to action.
```

**Score:** platform_fit __/5 · usefulness __/5

---

### `copy-grounding-no-metrics` — marketing.social-copy (grounding)

**Request:** Write a LinkedIn post about how much money we save customers

**Reply:**

```
I handle writing post captions and social copy; positioning on cost savings falls under the strategy of a Marketing Strategist.
```

**Score:** no_fabrication __/5 · brand_tone __/5

---

### `copy-memory-applied` — marketing.social-copy (memory)

**Request:** Another LinkedIn post, this time about staging environments left running

**Reply:**

```
Stop wasting engineering hours on ghost environments.

Staging servers left running create noise and drain your focus.

You spend more time managing infrastructure than shipping features.

Acme Cloud automates the cleanup so your team stays lean.

Reclaim your deployment pipeline today.

#DevOps #CloudComputing #EngineeringEfficiency

**Why this works**
It targets a specific technical pain point for developers.
The hook creates immediate urgency regarding wasted time.
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

**Rendered:** `post-image-1792356805-1d44d03f.png` 1200×627 (58216 bytes)

**Alt text:** Professional graphic with bold text about automating cloud cost reduction on a brand-colored background.

**Spec from the model:**

```json
{
  "headline": "automate your cloud cost reduction",
  "subline": "stop manual tracking and start optimizing infrastructure spend",
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
stop manual tracking and start optimizing infrastructure spend

*1200×627 · CTA: learn how · brand palette*
```

**Score:** headline_relevance __/5 · headline_brevity __/5 · legibility __/5 · brand_fit __/5 · alt_text __/5

---

### `image-complex-detail` — marketing.post-image (complex)

**Request:** A post image announcing our Series A. The headline should lead on what it means
for customers, not on the amount. Add a short supporting line and a call to
action that points at the changelog.

**Rendered:** `post-image-1792356807-829c38bb.png` 1200×627 (55817 bytes)

**Alt text:** A professional announcement graphic stating that Series A funding will accelerate the product roadmap.

**Spec from the model:**

```json
{
  "headline": "accelerating our product roadmap",
  "subline": "more features and faster updates for your infrastructure",
  "badge": "series a",
  "cta": "view the changelog",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**accelerating our product roadmap**
more features and faster updates for your infrastructure

*1200×627 · CTA: view the changelog · brand palette*
```

**Score:** headline_relevance __/5 · instruction_following __/5 · legibility __/5

---

### `image-ambiguous` — marketing.post-image (ambiguous)

**Request:** Make us a graphic

**Rendered:** `post-image-1792356809-06edc501.png` 1200×627 (63055 bytes)

**Alt text:** Bold text on a brand-colored background announcing automated scaling for developers.

**Spec from the model:**

```json
{
  "headline": "deploy faster with automated scaling",
  "subline": "reduce manual infrastructure management for your engineering team",
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
reduce manual infrastructure management for your engineering team

*1200×627 · CTA: learn more · brand palette*
```

**Score:** headline_relevance __/5 · graceful_degradation __/5

---

### `image-brand-colours` — marketing.post-image (brand)

**Request:** Instagram square graphic announcing our new usage-based pricing

**Rendered:** `post-image-1792356813-58554565.png` 1200×627 (51412 bytes)

**Alt text:** A bold graphic announcing the transition to usage-based pricing for Acme Cloud.

**Spec from the model:**

```json
{
  "headline": "usage-based pricing is here",
  "subline": "pay only for the resources you actually use",
  "badge": "new update",
  "cta": "see how it works",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**usage-based pricing is here**
pay only for the resources you actually use

*1200×627 · CTA: see how it works · brand palette*
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

**Rendered:** `ad-creative-1792356815-c7a54c23.png` 1080×1080 (89502 bytes)

**Alt text:** Professional ad for Acme Cloud featuring a dark blue palette and a call to action for a free trial.

**Spec from the model:**

```json
{
  "headline": "Ship code faster with less effort",
  "subline": "Automated infrastructure for engineering teams",
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
Automated infrastructure for engineering teams

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · objective_alignment __/5 · legibility __/5 · alt_text __/5

---

### `ad-supplied-offer` — marketing.ad-creative (ordinary)

**Request:** Ad image promoting 30% off annual plans until 31 March

**Rendered:** `ad-creative-1792356817-c26704e6.png` 1080×1080 (101650 bytes)

**Alt text:** Professional ad for Acme Cloud featuring a 30% discount on annual plans.

**Spec from the model:**

```json
{
  "headline": "Scale Your Infrastructure Faster",
  "subline": "Professional cloud management for developers and founders",
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
Professional cloud management for developers and founders

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · offer_fidelity __/5

---

### `ad-grounding-no-invented-offer` — marketing.ad-creative (grounding)

**Request:** Make an ad creative that will get engineering managers to sign up

**Rendered:** `ad-creative-1792356818-a3c8143c.png` 1080×1080 (87743 bytes)

**Alt text:** Professional ad for Acme Cloud showing a split layout with a focus on engineering efficiency.

**Spec from the model:**

```json
{
  "headline": "Ship features faster",
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
**Ship features faster**
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
Since you didn't provide the page copy, I am assuming your core value proposition focuses on reducing engineering toil rather than just lowering the monthly bill.

**Primary keyword** — cloud cost automation (commercial)

**Secondary keywords**
- FinOps automation tools
- reduce cloud waste
- automated cloud cost optimization
- cloud spend management for developers
- infrastructure cost automation

**Title tag** — Cloud Cost Automation for Engineering Teams | Acme Cloud (57)

**Meta description** — Stop wasting engineering hours on manual cost tracking. Automate your cloud spend and reclaim your sprint capacity with Acme Cloud. (138)

**H2 outline**
- **The offer:** Automate your cloud cost management to save engineering time.
- **Proof:** How top engineering teams reduced manual FinOps toil.
- **The problem:** Why manual cost tracking kills developer productivity.
- **The solution:** Automated visibility and remediation for your cloud spend.
- **Key features:** Real-time waste detection and automated scaling.
- **Onboarding:** How to integrate Acme Cloud into your existing pipeline.
- **FAQ:** Addressing technical implementation and security.

**Internal link targets**
- Pricing page (for plan tiers)
- Documentation (for API integration guides)
- Case studies (for engineering efficiency metrics)
- Contact/Demo page
```

**Score:** intent_reading __/5 · keyword_relevance __/5 · structure __/5 · actionability __/5

---

### `seo-grounding-no-volumes` — marketing.seo-optimizer (grounding)

**Request:** Give me the search volume and keyword difficulty for 'cloud cost tool'

**Reply:**

```
I cannot see search volume or keyword difficulty; you would need a tool like Ahrefs, SEMrush, or Google Keyword Planner to get those figures.
```

**Score:** no_fabrication __/5 · honesty_about_limits __/5

---

### `seo-attachment` — marketing.seo-optimizer (attachment)

**Request:** Optimise this page copy for search

**Reply:**

```
Based on the copy provided, I've focused on the core value of identifying idle capacity to save engineering effort.

**Observation:** The source text focuses on "idle cloud capacity" and "reporting" what is no longer useful.
**Assumption:** I am assuming your target audience is looking for "automation" to reduce the manual toil of cloud auditing.

**Primary keyword** — cloud cost automation (commercial)

**Secondary keywords**
- identify idle cloud resources
- cloud capacity optimization
- automated cloud auditing
- reduce cloud waste
- cloud resource management

**Title tag** — Cloud Cost Automation for Engineering Teams | Acme Cloud (57 characters)

**Meta description** — Automatically find and report idle cloud capacity. Stop wasting engineering time on manual audits. Trusted by dev teams. (124 characters)

**H2 outline**
- Stop wasting engineering hours on manual cloud audits (The Offer)
- Trusted by engineering teams at scale (Proof)
- How Acme Cloud identifies idle capacity (How it works)
- Connect your account in minutes (Low friction/CTA)
- Stop the leak of unused resources (The outcome)

**Internal link targets**
- Documentation: Connection guide
- Case studies: Engineering time saved
- Pricing/Plans page
```

**Score:** uses_source_material __/5 · keyword_relevance __/5 · structure __/5

---

### `seo-content-type-aware` — marketing.seo-optimizer (profile)

**Request:** SEO for our Kubernetes rightsizing feature

**Reply:**

```
Since you didn't provide page copy, I'm assuming this is a new feature landing page focused on reducing engineering toil through automated resource allocation.

**Primary keyword** — Kubernetes rightsizing (Commercial)

**Secondary keywords**
- K8s resource optimization
- automated pod rightsizing
- Kubernetes cost efficiency
- CPU and memory limits automation
- reduce Kubernetes waste

**Title tag** — Kubernetes Rightsizing: Automate Resource Limits (52 characters)

**Meta description** — Stop wasting engineering hours on manual tuning. Automate your Kubernetes rightsizing to optimize performance and reclaim developer time. (142 characters)

**H2 outline**
- **The Solution:** Automated Kubernetes rightsizing for lean clusters.
- **Stop the Manual Toil:** How automation saves your engineering team's time.
- **Precision Scaling:** Balancing CPU and memory limits without the guesswork.
- **Integration:** How it fits into your existing K8s workflow.
- **Proof:** Performance gains and stability metrics.
- **Get Started:** Deploy rightsizing in your cluster.

**Internal link targets**
- Cloud cost automation landing page
- Documentation: Installing the Acme Cloud agent
- Pricing page (for plan tiers)
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
- optimize Kubernetes pod memory
- Kubernetes CPU throttling
- vertical pod autoscaler
- reduce cloud waste K8s

**Title tag** — How to Rightsize Kubernetes Requests for Better Performance (58)

**Meta description** — Stop over-provisioning. Learn how to rightsize your Kubernetes requests to eliminate waste and stop CPU throttling in your clusters. (138)

**H2 outline**
- What is Kubernetes rightsizing and why it matters
- The impact of incorrect resource requests on cluster stability
- How to analyze your current resource usage
- Step-by-step guide to adjusting requests and limits
- Automating rightsizing with VPA and Goldilocks
- Measuring the impact on engineering efficiency

**Internal link targets**
- Kubernetes rightsizing feature landing page
- Cloud cost automation overview
- Guide to reducing cloud waste
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
I am producing a plan based on **Assumptions** because no specific objective or audience segment was provided.

**Assumptions**
- Objective: Generate 50 new demo sign-ups (suggested).
- Audience: Founders who care about reducing engineering overhead.
- Time window: 14 days.

**Objective**
Generate 50 new demo sign-ups (suggested) for the cost automation feature.

**Audience**
Founders; they care about reclaiming engineering time spent on manual cost management.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering time saved | Text post | 3x / week |
| Email | Efficiency gains | Direct outreach | 2x / campaign |
| Blog / SEO | Automation vs Manual | Long-form guide | 1x / campaign |

**Calendar**
| Day | LinkedIn | Email | Blog / SEO |
| :--- | :--- | :--- | :--- |
| 1 | Teaser post | - | - |
| 3 | Feature benefit post | Announcement email | Launch guide |
| 5 | - | - | - |
| 7 | Case study/use case | - | - |
| 9 | - | Follow-up email | - |
| 11 | Comparison post | - | - |
| 14 | Last call/Summary | - | - |

**Budget**
Planned within your small budget band (<$500/mo).

**Primary KPI**
Number of demo sign-ups (suggested: 50), with the guardrail metric being the email unsubscribe rate.

**Risks**
- Messaging focuses too much on cost savings rather than engineering time.
- Low organic reach on LinkedIn limiting the top-of-funnel flow.

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
I am producing a plan based on the following **Assumptions**: Your target audience is Developers and Founders who care about reducing wasted engineering time, and the campaign runs from Week 1 to Week 6.

**Objective** — Generate 100 free trial signups for Acme Cloud within six weeks.

**Audience** — Developers and Founders; they care about reclaiming engineering hours spent on infrastructure.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering time saved | Text-based posts | 3x / week |
| Email | Efficiency gains/Case study | Direct outreach | 1x / week |
| Blog / SEO | Technical "How-to" guides | Long-form articles | 1x / week |

**Calendar**
| Week | Blog Focus | LinkedIn Focus | Email Focus |
| :--- | :--- | :--- | :--- |
| 1 | Problem: Time waste | Problem awareness | Intro to efficiency |
| 2 | Solution: Acme Cloud | Feature: Automation | The "Time-Back" value |
| 3 | Comparison: Old vs New | User testimonial | Case study snippet |
| 4 | Integration guide | Technical deep-dive | Direct trial invite |
| 5 | Scaling efficiency | Objection handling | Last call for early access |
| 6 | Summary of gains | Final push/Urgency | Final trial reminder |

**Budget**
Total: $400 (Allocated as follows)
- LinkedIn (Paid amplification): $250 (suggestion)
- Email (Tooling/Lists): $100 (suggestion)
- Blog (Distribution/Promoted): $50 (suggestion)

**Primary KPI** — Total number of free trial signups.
**Guardrail Metric** — Lead-to-signup conversion rate (must not drop).

**Risks**
- Messaging focuses too much on features rather than time saved.
- Low organic reach on LinkedIn requiring higher ad spend than suggested.
- Email deliverability issues limiting the reach of the trial invites.
```

**Score:** budget_handling __/5 · objective_clarity __/5 · kpi_quality __/5 · timeline_realism __/5

---

### `campaign-clarification` — marketing.campaign-planner (clarification)

**Request:** Plan a campaign

**Reply:**

```
I handle planning marketing campaigns (objectives, channels, calendar, and KPIs). Since you didn't provide a goal, audience, or timeframe, I have two questions:

1. What is the specific objective or product feature you are promoting?
2. What is the desired time window for this campaign?
```

**Score:** clarification_quality __/5 · no_fabrication __/5

---

### `campaign-grounding-no-invented-budget` — marketing.campaign-planner (grounding)

**Request:** Plan a one month awareness campaign on LinkedIn and email

**Reply:**

```
I will produce a plan based on assumptions since no specific objective or audience segment was provided.

**Assumptions**
- Objective: Increase brand awareness among Founders.
- Audience: Technical Founders who care about reducing engineering overhead.
- Time window: 30 days.

**Objective**
Increase monthly website visits from LinkedIn and Email by 20% (suggested) to build a top-of-funnel lead pool.

**Audience**
Technical Founders; they care about reclaiming engineering time for core product features.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering time saved | Thought-leadership posts | 3x per week |
| Email | Efficiency gains | Educational newsletter | 1x per week |

**Calendar**
| Week | LinkedIn Focus | Email Focus |
| :--- | :--- | :--- |
| Week 1 | The cost of manual setup | Introduction to efficiency |
| Week 2 | Case study: Time reclaimed | Deep dive: Workflow optimization |
| Week 3 | Common engineering bottlenecks | Comparison: Old vs. New way |
| Week 4 | Future-proofing your stack | Summary of time-saving wins |

**Budget**
I have planned this within your small budget band (<$500/mo).

**Primary KPI**
Total unique landing page visits (suggested), with a guardrail metric of Email Unsubscribe Rate (must not increase by more than 1% suggested).

**Risks**
- Content feels too generic to appeal to technical founders.
- Low email open rates due to lack of a pre-existing warm list.
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

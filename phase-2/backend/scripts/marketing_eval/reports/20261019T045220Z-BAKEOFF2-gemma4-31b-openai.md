# Marketing evaluation — BAKEOFF2-gemma4-31b

Generated 20261019T045220Z · 30 cases · 43s

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
Your cloud infrastructure is likely costing you more than it delivers.

Idle resources drain your budget without adding a single line of value to your product.

Most teams over-provision to avoid downtime, but they end up paying for capacity they never actually use.

Acme Cloud helps you identify these gaps so your engineers can focus on shipping features instead of managing waste.

Stop paying for silence.

Check your utilization today.

#CloudComputing #SaaS #EngineeringEfficiency #CloudSpend

**Why this works**
It targets the pain of wasted resources and positions the value on engineering focus rather than cost.
```

**Score:** hook __/5 · audience_fit __/5 · brand_tone __/5 · usefulness __/5 · no_filler __/5

---

### `copy-complex-thread` — marketing.social-copy (complex)

**Request:** Write a 3-post X thread explaining why we rebuilt our cost allocation engine.
Post 1 is the problem, post 2 the rebuild, post 3 the result. Keep each under
280 characters and number them.

**Reply:**

```
1/ Tracking cloud spend across microservices became a manual nightmare. Your engineering team was spending hours every month auditing spreadsheets instead of shipping features.

2/ We rebuilt our cost allocation engine from the ground up. The new system automates resource tagging and maps spend to specific teams in real time.

3/ Now, your developers get instant visibility into their resource usage. You reclaim engineering hours and eliminate the monthly audit cycle.

**Why this works**
Focuses on engineering time saved rather than price.
Follows a clear problem-solution-result narrative.
```

**Score:** instruction_following __/5 · hook __/5 · brand_tone __/5

---

### `copy-exact-constraint-hashtags` — marketing.social-copy (ordinary)

**Request:** LinkedIn post about our new pricing. Use at most 2 hashtags.

**Reply:**

```
Stop wasting engineering hours on complex cost forecasting.

Our new pricing structure simplifies how you scale.

You can now focus on shipping features instead of managing cloud budgets.

Check the updated pricing page for details.

#AcmeCloud #SaaS

**Why this works**
It focuses on engineering time saved rather than price points.
The structure follows LinkedIn's hook-and-single-sentence format.
```

**Score:** instruction_following __/5

---

### `copy-no-hashtags-platform` — marketing.social-copy (platform)

**Request:** Write the Facebook post copy for our webinar on Thursday

**Reply:**

```
Ever feel like your engineering team is spending more time managing infrastructure than shipping features?

We are hosting a webinar this Thursday to show you how to reclaim those hours. You will learn how to automate the tedious parts of your cloud workflow so your developers can focus on building.

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
I handle writing post captions and social copy; this request falls under the Marketing domain's positioning rules, which are managed by the Campaign Planner.
```

**Score:** no_fabrication __/5 · brand_tone __/5

---

### `copy-memory-applied` — marketing.social-copy (memory)

**Request:** Another LinkedIn post, this time about staging environments left running

**Reply:**

```
Stop wasting engineering hours on ghost environments.

Staging servers left running after a sprint create unnecessary noise and infrastructure clutter.

You spend more time auditing old instances than shipping new features.

Automate your cleanup to keep your pipeline lean.

Check out our automation tools here.

#DevOps #CloudComputing #EngineeringEfficiency

**Why this works**
Focuses on the pain of wasted engineering time rather than cost.
Uses a strong hook to target developer frustration with infrastructure clutter.
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

**Rendered:** `post-image-1792385510-a99df96a.png` 1200×627 (57781 bytes)

**Alt text:** Bold text on a professional brand background discussing cloud cost automation.

**Spec from the model:**

```json
{
  "headline": "automate your cloud cost reduction",
  "subline": "stop manual tracking and eliminate wasted spend",
  "badge": "cloud efficiency",
  "cta": "start automating",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**automate your cloud cost reduction**
stop manual tracking and eliminate wasted spend

*1200×627 · CTA: start automating · brand palette*
```

**Score:** headline_relevance __/5 · headline_brevity __/5 · legibility __/5 · brand_fit __/5 · alt_text __/5

---

### `image-complex-detail` — marketing.post-image (complex)

**Request:** A post image announcing our Series A. The headline should lead on what it means
for customers, not on the amount. Add a short supporting line and a call to
action that points at the changelog.

**Rendered:** `post-image-1792385511-dfde73c8.png` 1200×627 (59180 bytes)

**Alt text:** A bold professional graphic announcing Series A funding focused on faster feature delivery.

**Spec from the model:**

```json
{
  "headline": "faster feature delivery for developers",
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
**faster feature delivery for developers**
our series a funding accelerates our product roadmap

*1200×627 · CTA: view the changelog · brand palette*
```

**Score:** headline_relevance __/5 · instruction_following __/5 · legibility __/5

---

### `image-ambiguous` — marketing.post-image (ambiguous)

**Request:** Make us a graphic

**Rendered:** `post-image-1792385513-de39c7ec.png` 1200×627 (62564 bytes)

**Alt text:** A professional bold graphic announcing automated scaling to save engineering time.

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

**Rendered:** `post-image-1792385514-1db5f2bb.png` 1200×627 (52499 bytes)

**Alt text:** A bold professional graphic announcing the launch of usage-based pricing for Acme Cloud.

**Spec from the model:**

```json
{
  "headline": "pay only for what you use",
  "subline": "transparent usage-based pricing is now available",
  "badge": "new update",
  "cta": "learn more",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**pay only for what you use**
transparent usage-based pricing is now available

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

**Rendered:** `ad-creative-1792385516-fa429353.png` 1080×1080 (82586 bytes)

**Alt text:** Professional blue and dark navy ad showing a promise of faster shipping for engineering teams.

**Spec from the model:**

```json
{
  "headline": "Ship code faster",
  "subline": "Automate your infrastructure deployment pipeline",
  "badge": "Free trial",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Ship code faster**
Automate your infrastructure deployment pipeline

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · objective_alignment __/5 · legibility __/5 · alt_text __/5

---

### `ad-supplied-offer` — marketing.ad-creative (ordinary)

**Request:** Ad image promoting 30% off annual plans until 31 March

**Rendered:** `ad-creative-1792385518-501c892e.png` 1080×1080 (97568 bytes)

**Alt text:** Professional ad for Acme Cloud featuring a 30% discount on annual plans.

**Spec from the model:**

```json
{
  "headline": "Scale Your Infrastructure Faster",
  "subline": "Enterprise cloud management for developers and founders",
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
Enterprise cloud management for developers and founders

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · offer_fidelity __/5

---

### `ad-grounding-no-invented-offer` — marketing.ad-creative (grounding)

**Request:** Make an ad creative that will get engineering managers to sign up

**Rendered:** `ad-creative-1792385520-d29e3eba.png` 1080×1080 (82881 bytes)

**Alt text:** Professional blue and dark navy graphic focusing on deployment speed for engineering managers.

**Spec from the model:**

```json
{
  "headline": "Deploy Code Faster",
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
**Deploy Code Faster**
Automated infrastructure for engineering teams

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
Since you didn't provide the page copy, I am assuming your core value proposition focuses on reducing engineering overhead rather than just the monthly bill.

**Primary keyword** — cloud cost automation (commercial)

**Secondary keywords**
- cloud spend optimization
- automated cloud cost management
- reduce cloud waste
- FinOps automation tools
- cloud infrastructure cost control

**Title tag** — Cloud Cost Automation for Developers | Acme Cloud (52 characters)

**Meta description** — Stop wasting engineering hours on manual cloud billing. Automate your cost optimization and reclaim your sprint capacity with Acme Cloud. (142 characters)

**H2 outline**
*   **The Offer:** Automate your cloud cost management to save engineering time.
*   **Proof:** How Acme Cloud reduces manual FinOps overhead (Case studies/metrics).
*   **Core Features:** Automated waste detection and right-sizing.
*   **Developer Experience:** Integration with your existing CI/CD pipeline.
*   **Objection Handling:** Security, permissions, and safety guardrails.
*   **Call to Action:** Start automating your cloud spend.

**Internal link targets**
- Pricing page
- Documentation (Setup guide)
- Feature deep-dive: Right-sizing
- Contact/Demo request page
```

**Score:** intent_reading __/5 · keyword_relevance __/5 · structure __/5 · actionability __/5

---

### `seo-grounding-no-volumes` — marketing.seo-optimizer (grounding)

**Request:** Give me the search volume and keyword difficulty for 'cloud cost tool'

**Reply:**

```
I handle search optimisation including keywords, titles, and on-page structure, but I cannot provide search volume or keyword difficulty; you would need a tool like Ahrefs or SEMrush for those figures.
```

**Score:** no_fabrication __/5 · honesty_about_limits __/5

---

### `seo-attachment` — marketing.seo-optimizer (attachment)

**Request:** Optimise this page copy for search

**Reply:**

```
Based on the copy provided, I've focused on the core value of identifying idle capacity to save engineering time.

**Observation:** The source text focuses on "idle cloud capacity" and "reporting" what is no longer useful.
**Assumption:** I am assuming the target user is looking for an automated tool to reduce manual auditing of cloud resources.

**Primary keyword** — cloud cost automation (commercial)

**Secondary keywords**
- idle cloud capacity
- cloud resource optimization
- cloud waste detection
- automated cloud auditing
- engineering efficiency tools

**Title tag** — Cloud Cost Automation for Engineering Teams | Acme Cloud (56 characters)

**Meta description** — Automatically find idle cloud capacity and stop wasting engineering time on manual audits. Trusted by high-growth dev teams. (132 characters)

**H2 outline**
- Stop wasting engineering hours on manual cloud audits (The Offer)
- Trusted by engineering teams at scale (Proof)
- How Acme Cloud detects idle capacity (Process)
- Reclaim your sprint capacity (Benefit/Outcome)
- Get started with Acme Cloud (CTA)

**Internal link targets**
- Pricing page
- Documentation/Integration guide
- Case studies (Engineering efficiency)
```

**Score:** uses_source_material __/5 · keyword_relevance __/5 · structure __/5

---

### `seo-content-type-aware` — marketing.seo-optimizer (profile)

**Request:** SEO for our Kubernetes rightsizing feature

**Reply:**

```
Since you didn't provide page copy, I'm assuming this is a feature-specific landing page focused on reducing engineering overhead rather than cost.

**Primary keyword** — Kubernetes rightsizing (Commercial)

**Secondary keywords**
- K8s resource optimization
- automated pod autoscaling
- Kubernetes CPU memory tuning
- eliminate overprovisioning
- Kubernetes cluster efficiency

**Title tag** — Kubernetes Rightsizing: Automate Resource Tuning (48 characters)

**Meta description** — Stop wasting engineering hours on manual tuning. Automate your Kubernetes rightsizing to optimize performance and reclaim developer time. (142 characters)

**H2 outline**
- **The end of manual resource tuning** (Lead with the offer: automated rightsizing to save engineering time)
- **How Acme Cloud optimizes your pods** (Technical mechanism and proof of efficiency)
- **Stop overprovisioning without the risk** (Address the fear of crashes/OOM kills)
- **Reclaim your engineering roadmap** (Contrast manual toil vs. automated scaling)
- **Get started with Kubernetes rightsizing** (Final CTA)

**Internal link targets**
- Cloud cost automation landing page
- Kubernetes integration documentation
- Developer experience case studies
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
- optimize Kubernetes cost
- pod autoscaling best practices
- Kubernetes memory leak detection
- rightsizing containers

**Title tag** — How to Rightsize Kubernetes Requests for Better Performance (58)

**Meta description** — Stop wasting engineering time on manual tuning. Learn how to rightsize your Kubernetes requests to improve stability and reduce cloud waste. (142)

**H2 outline**
- What is Kubernetes rightsizing and why it matters
- The impact of over-provisioning on cluster stability
- How to analyze current resource usage vs. requests
- Step-by-step guide to adjusting requests and limits
- Automating rightsizing to save engineering hours
- Common pitfalls when tuning K8s resources

**Internal link targets**
- Kubernetes rightsizing feature landing page
- Cloud cost automation guide
- Documentation on resource quotas
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
Generate a suggested 50 new demo sign-ups for the cost automation feature.

**Audience**
Founders; they care about reclaiming engineering time spent on manual cost management.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering time saved | Text-based post | 3x per week |
| Email | Automation vs. Manual toil | Direct outreach | 2x per campaign |
| Blog / SEO | Guide to cost automation | Long-form article | 1x per campaign |

**Calendar**
| Date | LinkedIn | Email | Blog / SEO |
| :--- | :--- | :--- | :--- |
| Day 1 | Announcement | - | Feature Deep-dive |
| Day 3 | Pain point: Manual toil | - | - |
| Day 5 | - | Launch Announcement | - |
| Day 8 | Case study/Benefit | - | - |
| Day 10 | - | Follow-up / Reminder | - |
| Day 12 | Final call to action | - | - |
| Day 14 | Results/Thank you | - | - |

**Budget**
I have planned this within your small budget band (<$500/mo).

**Primary KPI**
Total number of demo sign-ups (suggested 50), with a guardrail metric of maintaining a current email unsubscribe rate below 1% (suggested).

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
I am producing a plan based on the following **Assumptions**: your target audience is Developers and Founders who care most about saving engineering time, and the campaign runs from Monday, Week 1 to Sunday, Week 6.

**Objective** — Generate 100 new free trial signups for Acme Cloud within six weeks.

**Audience** — Developers and Founders; they care about reducing manual toil to focus on core product builds.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering time saved | Text-based thought leadership | 3x / week |
| Email | Solving specific dev bottlenecks | Direct outreach / Newsletter | 1x / week |
| Blog | Technical "How-to" guides | Long-form articles | 1x / week |

**Calendar**
| Week | Blog Focus | Email Focus | LinkedIn Focus |
| :--- | :--- | :--- | :--- |
| 1 | The cost of manual setup | Problem introduction | Pain point awareness |
| 2 | Automating X workflow | The "Better Way" | Case study snippet |
| 3 | Scaling without adding headcount | Efficiency gains | Feature deep-dive |
| 4 | Comparison: Manual vs. Acme | Time-to-value | User testimonial |
| 5 | Advanced optimization tips | Direct trial invite | Objection handling |
| 6 | Summary of time-saving wins | Last call for trial | Urgency/Recap |

**Budget**
I have allocated your $400 total budget as follows:
- LinkedIn Sponsored Content: $300 (suggested)
- Email Tooling/Lead List: $100 (suggested)
- Blog: $0 (organic)

**Primary KPI** — Total number of free trial signups. 
**Guardrail Metric** — Email unsubscribe rate.

**Risks**
- High friction in the signup flow causing drop-offs.
- Content focusing too much on features rather than time saved.
```

**Score:** budget_handling __/5 · objective_clarity __/5 · kpi_quality __/5 · timeline_realism __/5

---

### `campaign-clarification` — marketing.campaign-planner (clarification)

**Request:** Plan a campaign

**Reply:**

```
I will ask two short questions to avoid inventing a brief: What is the specific objective or product you are promoting, and what is the time window for this campaign?
```

**Score:** clarification_quality __/5 · no_fabrication __/5

---

### `campaign-grounding-no-invented-budget` — marketing.campaign-planner (grounding)

**Request:** Plan a one month awareness campaign on LinkedIn and email

**Reply:**

```
I will produce a plan based on assumptions since no specific objective or audience segment was provided.

**Assumptions**
- Objective: Increase brand awareness among Founders to drive lead generation.
- Audience: Technical Founders who care about reducing engineering overhead.
- Time window: 30 days.

**Objective**
Generate 50 new qualified leads by increasing brand visibility among technical founders.

**Audience**
Technical Founders; they care about reclaiming engineering time for core product development.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering time saved | Thought leadership posts | 3x per week |
| Email | Efficiency gains | Educational sequence | 1x per week |

**Calendar**
| Week | LinkedIn Focus | Email Focus |
| :--- | :--- | :--- |
| Week 1 | The cost of manual infra | The "Engineering Leak" |
| Week 2 | Automation vs. Manual work | Case study: Time reclaimed |
| Week 3 | Scaling without adding headcount | The efficiency roadmap |
| Week 4 | Future-proofing your stack | Final call to action |

**Budget**
I have planned this within your small budget band (<$500/mo).

**Primary KPI**
Total number of new leads (suggested: 50), with a guardrail metric of email unsubscribe rate (suggested: <1%).

**Risks**
- Messaging focuses too much on features rather than time saved.
- Low LinkedIn organic reach limiting the top-of-funnel awareness.

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

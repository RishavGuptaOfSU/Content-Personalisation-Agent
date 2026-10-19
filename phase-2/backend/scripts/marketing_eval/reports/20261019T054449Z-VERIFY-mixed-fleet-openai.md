# Marketing evaluation — VERIFY-mixed-fleet

Generated 20261019T054449Z · 30 cases · 201s

## Configuration

| setting | value |
|---|---|
| `llm_provider` | openai |
| `llm_model` | gemma4:31b |
| `agent_models` | {'marketing.ad-creative': 'nemotron-3-super', 'marketing.social-copy': 'beam'} |
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
| `campaign-clarification` | campaign-planner | clarification | 2/3 | 1 |
| `campaign-grounding-no-invented-budget` | campaign-planner | grounding | 2/2 | 0 |
| `campaign-out-of-scope-write` | campaign-planner | out_of_scope | 4/4 | 0 |
| `campaign-routing` | — | routing | 2/2 | 0 |

### Failed assertions

- `campaign-clarification` — no figures the user did not supply → 1%

## Outputs for qualitative scoring

Score each dimension 1–5 using `rubric.md`. The harness deliberately does
not score these.

### `copy-ordinary-linkedin` — marketing.social-copy (ordinary)

**Request:** Write a LinkedIn post about how much cloud spend sits idle

**Reply:**

```
Most teams are paying for cloud capacity that nobody is using.

Idle spend rarely shows up as a line item.

It shows up as engineering hours — someone investigating a spike, someone right-sizing a cluster, someone explaining the bill to finance.

The invoice is the symptom. The lost focus is the cost.

If you want your engineers building product instead of chasing infrastructure, that's the problem worth solving.

What's the biggest source of idle spend you've found in your stack?

#CloudEngineering #DevOps #SaaS

**Why this works:** It reframes idle spend as lost engineering focus rather than a price problem, matching the brand's positioning, and ends with a single question CTA.
```

**Score:** hook __/5 · audience_fit __/5 · brand_tone __/5 · usefulness __/5 · no_filler __/5

---

### `copy-complex-thread` — marketing.social-copy (complex)

**Request:** Write a 3-post X thread explaining why we rebuilt our cost allocation engine.
Post 1 is the problem, post 2 the rebuild, post 3 the result. Keep each under
280 characters and number them.

**Reply:**

```
1/ Our cost allocation engine was built for a simpler world. As customers scaled, tagging gaps and manual reconciliation piled up. Engineers spent hours chasing spend instead of shipping. We needed a system that attributed cost accurately without the busywork.

2/ We rebuilt it from scratch: automated tag inheritance, real-time attribution, and a rules engine that maps spend to teams and projects without manual spreadsheets. The goal was zero-touch allocation engineers never have to think about.

3/ The result: allocation runs automatically, reconciliation dropped to near zero, and engineering time went back to building product. Cost visibility stayed accurate without the overhead. That's the win we were after. #CloudCosts #Engineering

**Why this works:** Each post carries one idea (problem, rebuild, result), stays well under 280 characters, and frames the outcome around engineering time reclaimed rather than price. Numbered for thread readability. No emojis or clickbait.
```

**Score:** instruction_following __/5 · hook __/5 · brand_tone __/5

---

### `copy-exact-constraint-hashtags` — marketing.social-copy (ordinary)

**Request:** LinkedIn post about our new pricing. Use at most 2 hashtags.

**Reply:**

```
Acme Cloud has new pricing.

We've restructured our plans around how engineering teams actually ship — by workload and usage, not seat count.

Simpler to predict, easier to scale.

Take a look at the new tiers and see what fits your team.

#CloudComputing #DevTools

**Why this works:** Leads with the news, explains the change in one line, ends with a single clear CTA. No hype, no emojis.
```

**Score:** instruction_following __/5

---

### `copy-no-hashtags-platform` — marketing.social-copy (platform)

**Request:** Write the Facebook post copy for our webinar on Thursday

**Reply:**

```
Join us this Thursday for a live webinar on getting more from your cloud setup — without the guesswork.

We'll walk through practical ways to keep your infrastructure lean, your deploys fast, and your team focused on shipping instead of firefighting. Bring your questions; we'll answer them live.

Save your seat now — registration takes a minute.

**Why this works:** Conversational opener and short paragraphs fit Facebook's feed, and the explicit CTA tells readers exactly what to do next. No hashtags per platform rules.
```

**Score:** platform_fit __/5 · usefulness __/5

---

### `copy-grounding-no-metrics` — marketing.social-copy (grounding)

**Request:** Write a LinkedIn post about how much money we save customers

**Reply:**

```
Your cloud bill isn't where the real savings are. Your engineers' time is.

Every hour spent chasing runaway spend or tuning instances is an hour not spent shipping. Acme Cloud gives developers the visibility and guardrails to keep cloud costs predictable — so your team spends less time managing spend and more time building.

See how engineering teams reclaim their weeks: [link]

#CloudEngineering #DeveloperTools #EngineeringProductivity

**Why this works:** Leads with a contrarian hook that reframes "savings" as engineering time, matching our positioning. Single-sentence paragraphs and one CTA keep it scannable on LinkedIn.
```

**Score:** no_fabrication __/5 · brand_tone __/5

---

### `copy-memory-applied` — marketing.social-copy (memory)

**Request:** Another LinkedIn post, this time about staging environments left running

**Reply:**

```
Staging environments left running are the quietest tax on your engineering team.

They don't break anything. They just sit there, consuming attention — someone has to remember to tear them down, someone has to check whether they're still needed, someone has to debug why prod behaves differently.

The fix isn't a policy. It's making teardown the default.

At Acme Cloud, we're building environments that expire on their own, so your engineers spend their time shipping, not janitoring.

See how it works → acmecloud.com

#DevOps #Engineering #Cloud

**Why this works**
- Opens with a standalone hook that names the problem without clickbait.
- Frames the value as engineering time saved, not cost, per your positioning.
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

**Rendered:** `post-image-1792388530-d2145683.png` 1200×627 (58229 bytes)

**Alt text:** Bold text on a brand-colored background discussing cloud cost automation.

**Spec from the model:**

```json
{
  "headline": "automate your cloud cost reductions",
  "subline": "eliminate manual waste with automated resource scaling",
  "badge": "cloud efficiency",
  "cta": "start automating",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**automate your cloud cost reductions**
eliminate manual waste with automated resource scaling

*1200×627 · CTA: start automating · brand palette*
```

**Score:** headline_relevance __/5 · headline_brevity __/5 · legibility __/5 · brand_fit __/5 · alt_text __/5

---

### `image-complex-detail` — marketing.post-image (complex)

**Request:** A post image announcing our Series A. The headline should lead on what it means
for customers, not on the amount. Add a short supporting line and a call to
action that points at the changelog.

**Rendered:** `post-image-1792388532-a8962992.png` 1200×627 (55664 bytes)

**Alt text:** A professional announcement graphic stating that Series A funding will accelerate the product roadmap.

**Spec from the model:**

```json
{
  "headline": "accelerating our product roadmap",
  "subline": "more features and faster releases for every developer",
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
more features and faster releases for every developer

*1200×627 · CTA: view the changelog · brand palette*
```

**Score:** headline_relevance __/5 · instruction_following __/5 · legibility __/5

---

### `image-ambiguous` — marketing.post-image (ambiguous)

**Request:** Make us a graphic

**Rendered:** `post-image-1792388534-c8102ac6.png` 1200×627 (61151 bytes)

**Alt text:** A professional bold graphic for Acme Cloud focusing on automated scaling to save engineering time.

**Spec from the model:**

```json
{
  "headline": "deploy faster with automated scaling",
  "subline": "reduce manual configuration and reclaim your engineering hours",
  "badge": "developer tools",
  "cta": "get started",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**deploy faster with automated scaling**
reduce manual configuration and reclaim your engineering hours

*1200×627 · CTA: get started · brand palette*
```

**Score:** headline_relevance __/5 · graceful_degradation __/5

---

### `image-brand-colours` — marketing.post-image (brand)

**Request:** Instagram square graphic announcing our new usage-based pricing

**Rendered:** `post-image-1792388535-7aec11a2.png` 1200×627 (50764 bytes)

**Alt text:** A bold professional graphic announcing the launch of usage-based pricing for Acme Cloud.

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

**Rendered:** `ad-creative-1792388597-130963b9.png` 1080×1080 (93471 bytes)

**Alt text:** Image showing engineering team collaborating on Acme Cloud dashboard with a free trial badge and call-to-action button.

**Spec from the model:**

```json
{
  "headline": "Accelerate your engineering workflow",
  "subline": "Access full platform, collaborate in real time, no setup",
  "badge": "Free trial",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Accelerate your engineering workflow**
Access full platform, collaborate in real time, no setup

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · objective_alignment __/5 · legibility __/5 · alt_text __/5

---

### `ad-supplied-offer` — marketing.ad-creative (ordinary)

**Request:** Ad image promoting 30% off annual plans until 31 March

**Rendered:** `ad-creative-1792388636-520b3dae.png` 1080×1080 (88718 bytes)

**Alt text:** A square ad featuring a developer viewing a screen with a 30% off badge and a Start free trial button.

**Spec from the model:**

```json
{
  "headline": "Lower your cloud spend",
  "subline": "Get 30% off annual Acme Cloud plans",
  "badge": "30% off",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Lower your cloud spend**
Get 30% off annual Acme Cloud plans

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · offer_fidelity __/5

---

### `ad-grounding-no-invented-offer` — marketing.ad-creative (grounding)

**Request:** Make an ad creative that will get engineering managers to sign up

**Rendered:** `ad-creative-1792388653-e34a78e1.png` 1080×1080 (92396 bytes)

**Alt text:** Illustration of a developer dashboard showing a streamlined workflow with a call-to-action button.

**Spec from the model:**

```json
{
  "headline": "Ship faster with less friction",
  "subline": "Automate testing and deployment in one unified platform",
  "badge": "Acme Cloud",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Ship faster with less friction**
Automate testing and deployment in one unified platform

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
Since you didn't provide the page copy, I am assuming the core value proposition is reducing engineering overhead through automated cost management.

**Primary keyword** — cloud cost automation (commercial)

**Secondary keywords**
- automated cloud cost optimization
- reduce cloud spend for developers
- cloud waste management tool
- FinOps automation software
- cloud infrastructure cost control

**Title tag** — Cloud Cost Automation for Developers | Acme Cloud (52)

**Meta description** — Stop wasting engineering hours on manual cost tracking. Automate your cloud spend and reclaim your time with Acme Cloud. (124)

**H2 outline**
- **The Offer:** Automate your cloud cost management to save engineering time.
- **Proof:** How top engineering teams reduce waste without manual auditing.
- **Core Features:** Automated scaling, waste detection, and budget alerts.
- **Developer Benefits:** Shift focus from spreadsheets back to shipping code.
- **Integration:** How Acme Cloud plugs into your existing stack.
- **Final CTA:** Start automating your infrastructure costs.

**Internal link targets**
- Pricing page (for plan details)
- Documentation (for integration guides)
- Case studies (for proof of engineering time saved)
```

**Score:** intent_reading __/5 · keyword_relevance __/5 · structure __/5 · actionability __/5

---

### `seo-grounding-no-volumes` — marketing.seo-optimizer (grounding)

**Request:** Give me the search volume and keyword difficulty for 'cloud cost tool'

**Reply:**

```
I cannot see live search data; you would need a tool like Ahrefs, SEMrush, or Google Keyword Planner to get those figures.
```

**Score:** no_fabrication __/5 · honesty_about_limits __/5

---

### `seo-attachment` — marketing.seo-optimizer (attachment)

**Request:** Optimise this page copy for search

**Reply:**

```
Based on the copy provided, I've focused on the "idle capacity" and "engineering time" angles.

**Observed from copy:** Focus on automatic discovery of idle cloud capacity and trust from engineering teams.
**Assumed:** You are targeting a B2B SaaS audience looking to reduce operational waste without manual auditing.

**Primary keyword** — cloud cost automation (commercial)

**Secondary keywords**
- identify idle cloud resources
- cloud waste management
- automated cloud auditing
- reduce cloud spend
- cloud infrastructure optimization

**Title tag** — Cloud Cost Automation for Engineering Teams | Acme Cloud (56 characters)

**Meta description** — Automatically find idle cloud capacity and reclaim engineering time. Stop wasting resources with Acme Cloud's automated reporting. (138 characters)

**H2 outline**
- **Stop wasting engineering hours on manual cloud audits** (The core offer and value prop)
- **How Acme Cloud identifies idle capacity** (The mechanism/process)
- **Trusted by engineering teams at scale** (Social proof and trust signals)
- **Connect your account in minutes** (Low-friction call to action)
- **Frequently asked questions about cloud automation** (Handling objections)

**Internal link targets**
- Pricing page
- Documentation/Integration guide
- Case studies/Customer success stories
```

**Score:** uses_source_material __/5 · keyword_relevance __/5 · structure __/5

---

### `seo-content-type-aware` — marketing.seo-optimizer (profile)

**Request:** SEO for our Kubernetes rightsizing feature

**Reply:**

```
Since you didn't provide page copy, I am assuming this is a feature-specific landing page focused on reducing engineering overhead rather than cost.

**Primary keyword** — Kubernetes rightsizing (Commercial)

**Secondary keywords**
- K8s resource optimization
- automated pod rightsizing
- Kubernetes CPU and memory tuning
- reduce Kubernetes over-provisioning
- K8s engineering efficiency

**Title tag** — Kubernetes Rightsizing: Automate Resource Tuning (51 characters)

**Meta description** — Stop wasting engineering hours on manual K8s tuning. Automate your Kubernetes rightsizing to reclaim developer time. (121 characters)

**H2 outline**
- **The Rightsizing Solution**: Lead with the automated tuning offer and the immediate impact on engineering velocity.
- **Stop Manual Resource Tuning**: Contrast the pain of manual YAML edits with automated optimization.
- **How it Works**: Technical breakdown of the rightsizing mechanism for developers.
- **Engineering Time Recovered**: Proof and metrics focusing on hours saved per sprint.
- **Integration & Deployment**: How to plug the feature into existing clusters.
- **Frequently Asked Questions**: Address technical objections regarding stability and performance.

**Internal link targets**
- Cloud cost automation landing page
- Documentation: Installation guide
- Pricing page
- Case studies: Engineering efficiency
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
- vertical pod autoscaler
- Kubernetes memory leaks

**Title tag** — How to Rightsize Kubernetes Requests for Better Performance (58)

**Meta description** — Stop wasting engineering time on manual tuning. Learn how to rightsize Kubernetes requests to stabilize your clusters and optimize resource use. (142)

**H2 outline**
- What is Kubernetes rightsizing and why it matters
- The impact of incorrect resource requests on cluster stability
- How to analyze current resource utilization
- Step-by-step guide to adjusting requests and limits
- Automating rightsizing with VPA and HPA
- Common pitfalls when rightsizing production workloads

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
Since you didn't specify an objective or audience for this feature, I am producing a plan based on **Assumptions**.

**Assumptions**
- Objective: Generate 50 (suggested) new demo sign-ups.
- Audience: Founders who care about reducing engineering overhead.
- Time window: 14 days.

**Objective** — Generate 50 (suggested) new demo sign-ups for the cost automation feature within two weeks.

**Audience** — Founders; they care about reclaiming engineering time spent on manual cost management.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering time saved | Text post | 3x per week |
| Email | Operational efficiency | Direct mail | 2x per campaign |
| Blog / SEO | How-to / Guide | Long-form article | 1x per campaign |

**Calendar**
| Day | Activity | Focus |
| :--- | :--- | :--- |
| Day 1 | Blog Post | Deep dive into automation vs. manual work |
| Day 2 | LinkedIn Post 1 | Problem: The cost of manual tracking |
| Day 4 | LinkedIn Post 2 | Solution: Feature introduction |
| Day 6 | Email 1 | Announcement and demo invite |
| Day 8 | LinkedIn Post 3 | Benefit: Engineering hours reclaimed |
| Day 10 | LinkedIn Post 4 | Social proof / Use case |
| Day 12 | Email 2 | Last call for early access/demo |
| Day 14 | LinkedIn Post 5 | Summary of value and final CTA |

**Budget**
I have planned this within your small budget band (<$500/mo) using organic reach and existing email lists.

**Primary KPI** — Total number of demo sign-ups.
**Guardrail Metric** — Email unsubscribe rate.

**Risks**
- Low organic reach on LinkedIn limiting the top-of-funnel.
- Messaging focusing too much on "cost" rather than "time saved."

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
Since you didn't specify a target audience or time window for the launch, I am producing a plan based on **Assumptions**.

**Assumptions**
- Audience: Mid-level Developers who care about reducing manual infrastructure toil.
- Window: A 6-week sprint starting next Monday.

**Objective**
Generate 100 new free trial signups for Acme Cloud within 6 weeks.

**Audience**
Developers; they care about reclaiming engineering time spent on maintenance.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering time saved | Text-based thought leadership | 2x / week |
| Email | Workflow optimization | Direct outreach/Newsletter | 1x / week |
| Blog | Technical "How-to" guides | Long-form tutorials | 1x / week |

**Calendar**
| Week | Blog Focus | LinkedIn Focus | Email Focus |
| :--- | :--- | :--- | :--- |
| 1 | Problem: Time waste | Intro to the "Time-Save" angle | Announcement |
| 2 | Solution: Acme Cloud | Case study snippet | Feature deep-dive |
| 3 | Tutorial: Setup | Comparison: Manual vs. Acme | User testimonial |
| 4 | Tutorial: Scaling | Common pitfalls avoided | "How it works" guide |
| 5 | Best Practices | Efficiency tips | Urgency/Trial reminder |
| 6 | Summary/ROI | Final call to action | Last chance for trial |

**Budget**
Total: $400.
- LinkedIn Sponsored Content: $300 (suggestion)
- Email Tooling/Misc: $100 (suggestion)

**Primary KPI**
Total Free Trial Signups (Target: 100).
Guardrail: Lead-to-Trial conversion rate must not drop below 5% (suggestion).

**Risks**
- High friction in the signup flow causing drop-offs.
- Content focusing too heavily on features rather than time saved.
```

**Score:** budget_handling __/5 · objective_clarity __/5 · kpi_quality __/5 · timeline_realism __/5

---

### `campaign-clarification` — marketing.campaign-planner (clarification)

**Request:** Plan a campaign

**Reply:**

```
I am producing a plan based on **Assumptions** because your request did not include an objective, audience, or time window.

**Assumptions**
- Objective: Generate 50 new free trial sign-ups.
- Audience: Founders who care about reducing engineering overhead.
- Time window: 30 days.

**Objective**
Acquire 50 new free trial sign-ups by emphasizing engineering time saved.

**Audience**
Founders; they care about accelerating their product roadmap by reducing manual infrastructure work.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering efficiency | Text-based thought leadership | 3x per week |
| Email | Direct value proposition | Problem/Solution sequence | 1x per week |
| Blog / SEO | Technical "How-to" | Long-form guide | 2x per month |

**Calendar**
| Date | LinkedIn | Email | Blog |
| :--- | :--- | :--- | :--- |
| Week 1 | Efficiency hook | Intro: The time cost | Guide: Reducing Overhead |
| Week 2 | Case study angle | The "Build vs Buy" logic | - |
| Week 3 | Feature spotlight | Social proof/Testimonial | Guide: Scaling Fast |
| Week 4 | Final urgency/CTA | Direct invitation | - |

**Budget**
I have planned this within your small budget band (<$500/mo).

**Primary KPI**
Number of new free trial sign-ups (Suggested: 50).
Guardrail: Email unsubscribe rate (Suggested: <1%).

**Risks**
- Messaging focuses too much on features rather than time saved.
- Low organic reach on LinkedIn limiting the top-of-funnel.

---
⚠️ **Unverified figures:** `1%`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** clarification_quality __/5 · no_fabrication __/5

---

### `campaign-grounding-no-invented-budget` — marketing.campaign-planner (grounding)

**Request:** Plan a one month awareness campaign on LinkedIn and email

**Reply:**

```
Since you didn't specify a target audience or a specific goal for this awareness push, I am producing a plan based on **Assumptions**.

**Assumptions**
- Audience: Founders who care about reducing engineering overhead.
- Objective: Increase brand visibility among decision-makers.
- Window: 30 days.

**Objective**
Generate 50 new qualified leads (suggested) via demo requests or sign-ups.

**Audience**
Founders; they care about reclaiming engineering time to focus on core product features.

**Channel mix**
| Channel | Message angle | Format | Frequency |
| :--- | :--- | :--- | :--- |
| LinkedIn | Engineering efficiency | Text-based thought leadership | 3x per week |
| Email | Solving technical debt | Educational sequence | 1x per week |

**Calendar**
| Week | LinkedIn Focus | Email Focus |
| :--- | :--- | :--- |
| Week 1 | The cost of wasted dev time | Introduction to the efficiency gap |
| Week 2 | Comparison: Manual vs. Acme Cloud | Case study on time saved |
| Week 3 | Scaling without adding headcount | The "hidden" cost of maintenance |
| Week 4 | Future-proofing your stack | Final call to action for demo |

**Budget**
I have planned this within your small budget band (<$500/mo).

**Primary KPI**
Total number of demo requests (suggested), with the guardrail metric being the email unsubscribe rate.

**Risks**
- Messaging feels too generic to attract technical founders.
- Low engagement due to lack of visual assets on LinkedIn.
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

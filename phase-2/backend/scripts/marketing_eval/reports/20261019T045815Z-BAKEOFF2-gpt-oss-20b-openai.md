# Marketing evaluation — BAKEOFF2-gpt-oss-20b

Generated 20261019T045815Z · 30 cases · 113s

## Configuration

| setting | value |
|---|---|
| `llm_provider` | openai |
| `llm_model` | gpt-oss:20b |
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

**105/110 assertions passed** across 30 cases.

| case | agent | category | assertions | failures |
|---|---|---|---|---|
| `copy-ordinary-linkedin` | social-copy | ordinary | 6/6 | 0 |
| `copy-complex-thread` | social-copy | complex | 1/2 | 1 |
| `copy-exact-constraint-hashtags` | social-copy | ordinary | 2/2 | 0 |
| `copy-no-hashtags-platform` | social-copy | platform | 2/2 | 0 |
| `copy-grounding-no-metrics` | social-copy | grounding | 2/3 | 1 |
| `copy-memory-applied` | social-copy | memory | 2/2 | 0 |
| `copy-out-of-scope-image` | social-copy | out_of_scope | 4/4 | 0 |
| `copy-ad-copy-routing` | — | routing | 2/2 | 0 |
| `image-ordinary-linkedin` | post-image | ordinary | 9/9 | 0 |
| `image-complex-detail` | post-image | complex | 5/5 | 0 |
| `image-ambiguous` | post-image | ambiguous | 4/4 | 0 |
| `image-brand-colours` | post-image | brand | 4/5 | 1 |
| `image-out-of-scope-caption` | post-image | out_of_scope | 4/4 | 0 |
| `image-out-of-scope-campaign` | post-image | out_of_scope | 4/4 | 0 |
| `ad-ordinary-trial` | ad-creative | ordinary | 8/8 | 0 |
| `ad-supplied-offer` | ad-creative | ordinary | 5/5 | 0 |
| `ad-grounding-no-invented-offer` | ad-creative | grounding | 6/6 | 0 |
| `ad-out-of-scope-copy` | ad-creative | out_of_scope | 4/4 | 0 |
| `seo-ordinary-landing` | seo-optimizer | ordinary | 4/4 | 0 |
| `seo-grounding-no-volumes` | seo-optimizer | grounding | 1/2 | 1 |
| `seo-attachment` | seo-optimizer | attachment | 2/2 | 0 |
| `seo-content-type-aware` | seo-optimizer | profile | 2/2 | 0 |
| `seo-request-overrides-profile` | seo-optimizer | profile | 1/1 | 0 |
| `seo-out-of-scope` | seo-optimizer | out_of_scope | 4/4 | 0 |
| `campaign-ordinary-launch` | campaign-planner | ordinary | 4/4 | 0 |
| `campaign-budget-supplied` | campaign-planner | complex | 2/3 | 1 |
| `campaign-clarification` | campaign-planner | clarification | 3/3 | 0 |
| `campaign-grounding-no-invented-budget` | campaign-planner | grounding | 2/2 | 0 |
| `campaign-out-of-scope-write` | campaign-planner | out_of_scope | 4/4 | 0 |
| `campaign-routing` | — | routing | 2/2 | 0 |

### Failed assertions

- `copy-complex-thread` — contains one of ['1', '2', '3'] → matched None
- `copy-grounding-no-metrics` — no figures the user did not supply → 70%
- `image-brand-colours` — the image spec came from the model, not the fallback → the model returned no usable JSON design spec, so the request text was used as t
- `seo-grounding-no-volumes` — contains one of ['do not have', "don't have", 'no live', 'cannot', "can't", 'verify'] → matched None
- `campaign-budget-supplied` — no figures the user did not supply → 3 %

## Outputs for qualitative scoring

Score each dimension 1–5 using `rubric.md`. The harness deliberately does
not score these.

### `copy-ordinary-linkedin` — marketing.social-copy (ordinary)

**Request:** Write a LinkedIn post about how much cloud spend sits idle

**Reply:**

```
Did you know that a significant portion of cloud spend sits idle? That means developers are chasing unproductive resources instead of building. Acme Cloud's automated optimization frees up hours each month, letting your team focus on delivering value. Want to reclaim those hours? Let’s talk.  

#CloudOptimization #DeveloperProductivity #AcmeCloud
```

**Score:** hook __/5 · audience_fit __/5 · brand_tone __/5 · usefulness __/5 · no_filler __/5

---

### `copy-complex-thread` — marketing.social-copy (complex)

**Request:** Write a 3-post X thread explaining why we rebuilt our cost allocation engine.
Post 1 is the problem, post 2 the rebuild, post 3 the result. Keep each under
280 characters and number them.

**Reply:**

```
I can write LinkedIn posts, but this request is for X. Please ask the X Social Caption Writer.
```

**Score:** instruction_following __/5 · hook __/5 · brand_tone __/5

---

### `copy-exact-constraint-hashtags` — marketing.social-copy (ordinary)

**Request:** LinkedIn post about our new pricing. Use at most 2 hashtags.

**Reply:**

```
**Hook:**  
Acme Cloud’s new pricing model is designed to give developers more time to build, not more time to bill.

We’ve simplified tiers so you can focus on code, not on juggling complex cost breakdowns.  
With a single, predictable rate, your engineering team can allocate effort to innovation instead of spend forecasting.

Ready to free up your devs’ hours? **Learn more**.

#AcmeCloud #DeveloperFirst

**Why this works**  
Clear, predictable pricing removes the administrative burden that often stalls development cycles.
```

**Score:** instruction_following __/5

---

### `copy-no-hashtags-platform` — marketing.social-copy (platform)

**Request:** Write the Facebook post copy for our webinar on Thursday

**Reply:**

```
Hey developers and founders—  
We’re hosting a live webinar this Thursday to dive into how Acme Cloud’s new architecture cuts cloud spend and boosts performance.  

What you’ll learn:  
- Real‑world cost‑saving tactics  
- Best practices for scaling on our platform  
- Q&A with our engineering team  

Save your spot now: [link]  

See you there!
```

**Score:** platform_fit __/5 · usefulness __/5

---

### `copy-grounding-no-metrics` — marketing.social-copy (grounding)

**Request:** Write a LinkedIn post about how much money we save customers

**Reply:**

```
Every hour your team spends on cloud management is a dollar saved.  
Acme Cloud’s automated provisioning cuts manual effort by 70%, freeing developers to innovate. In our latest study, customers reported an average of $120k per year in direct cost savings from reduced engineering time.  
Discover how your team can do the same.  

#CloudEfficiency #DeveloperProductivity #Acme

---
⚠️ **Unverified figures:** `70%`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** no_fabrication __/5 · brand_tone __/5

---

### `copy-memory-applied` — marketing.social-copy (memory)

**Request:** Another LinkedIn post, this time about staging environments left running

**Reply:**

```
Staging environments left running can silently drain your budget and slow your team.  
Every idle instance costs money, consumes resources, and can become a security risk if not monitored.  
Automating cleanup and monitoring can save developers hours and keep your cloud spend in check.  

Discover how Acme Cloud’s new lifecycle manager cuts waste—schedule a demo today.  

#DevOps #CloudSavings #AcmeCloud
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

**Rendered:** `post-image-1792385822-81906edb.png` 1200×627 (56355 bytes)

**Alt text:** A stylized cloud with gears inside, representing automated cost savings for Acme Cloud.

**Spec from the model:**

```json
{
  "headline": "Automate to Cut Cloud Spend",
  "subline": "Save money, boost efficiency, and scale faster",
  "badge": "Cost Control",
  "cta": "Learn More",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Automate to Cut Cloud Spend**
Save money, boost efficiency, and scale faster

*1200×627 · CTA: Learn More · brand palette*
```

**Score:** headline_relevance __/5 · headline_brevity __/5 · legibility __/5 · brand_fit __/5 · alt_text __/5

---

### `image-complex-detail` — marketing.post-image (complex)

**Request:** A post image announcing our Series A. The headline should lead on what it means
for customers, not on the amount. Add a short supporting line and a call to
action that points at the changelog.

**Rendered:** `post-image-1792385825-d6ee024c.png` 1200×627 (61105 bytes)

**Alt text:** Acme Cloud Series A announcement with bold headline and call to action

**Spec from the model:**

```json
{
  "headline": "Series A fuels new cloud features",
  "subline": "Unlock advanced analytics and faster deployments for your teams",
  "badge": "",
  "cta": "See the changelog",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Series A fuels new cloud features**
Unlock advanced analytics and faster deployments for your teams

*1200×627 · CTA: See the changelog · brand palette*
```

**Score:** headline_relevance __/5 · instruction_following __/5 · legibility __/5

---

### `image-ambiguous` — marketing.post-image (ambiguous)

**Request:** Make us a graphic

**Rendered:** `post-image-1792385829-11329588.png` 1200×627 (37251 bytes)

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

**Rendered:** `post-image-1792385834-d3e25054.png` 1200×627 (65895 bytes)

**Alt text:** Graphic with the headline: Instagram square graphic announcing our new usage-based pricing

**Spec from the model:**

```json
{
  "headline": "Instagram square graphic announcing our new usage-based pricing",
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
**Instagram square graphic announcing our new usage-based pricing**

*1200×627 · brand palette*
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

**Rendered:** `ad-creative-1792385837-3ff69e47.png` 1080×1080 (84333 bytes)

**Alt text:** Image showing Acme Cloud logo with free trial offer for engineering teams.

**Spec from the model:**

```json
{
  "headline": "Build Faster with Acme Cloud",
  "subline": "Engineered for developers and founders",
  "badge": "Free trial",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Build Faster with Acme Cloud**
Engineered for developers and founders

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · objective_alignment __/5 · legibility __/5 · alt_text __/5

---

### `ad-supplied-offer` — marketing.ad-creative (ordinary)

**Request:** Ad image promoting 30% off annual plans until 31 March

**Rendered:** `ad-creative-1792385841-1210f688.png` 1080×1080 (80595 bytes)

**Alt text:** Acme Cloud logo with a 30% off badge and a call‑to‑action button for a free trial

**Spec from the model:**

```json
{
  "headline": "Save on Your Annual Plan",
  "subline": "Enjoy 30% off until March 31",
  "badge": "30% off",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Save on Your Annual Plan**
Enjoy 30% off until March 31

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · offer_fidelity __/5

---

### `ad-grounding-no-invented-offer` — marketing.ad-creative (grounding)

**Request:** Make an ad creative that will get engineering managers to sign up

**Rendered:** `ad-creative-1792385847-8df5e617.png` 1080×1080 (76676 bytes)

**Alt text:** Graphic with the headline: Make an ad creative that will get engineering managers to sign up

**Spec from the model:**

```json
{
  "headline": "Make an ad creative that will get engineering managers to sign up",
  "subline": "",
  "badge": "Acme Cloud",
  "cta": "",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Make an ad creative that will get engineering managers to sign up**

*1080×1080 · brand palette*
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
**Primary keyword** – Acme Cloud cost automation (informational)  

**Secondary keywords** –  
- cloud cost savings for developers  
- automated cloud cost monitoring  
- SaaS cost optimization tools  
- reduce cloud spend India  
- cloud cost management platform  

**Title tag** – “Acme Cloud: Automate Cloud Cost Savings for Developers” (58 chars)  

**Meta description** – “Discover how Acme Cloud’s automated cost‑automation platform cuts cloud spend, saves engineering time, and keeps your SaaS running lean.” (155 chars)  

**H2 outline**  
1. **Why Developers Need Automated Cloud Cost Control** – Highlight pain points, time saved, and impact on product velocity.  
2. **How Acme Cloud Automates Cost Management** – Explain the core features (real‑time alerts, predictive budgeting, auto‑scaling rules).  
3. **Real‑World Savings: Case Studies from India** – Showcase metrics (e.g., 35 % spend reduction, 12 hrs/week saved).  
4. **Integrations That Fit Your Stack** – List common dev tools (GitHub, Terraform, Kubernetes).  
5. **Get Started in Minutes** – Clear call‑to‑action with free trial signup.  

**Internal link targets** –  
- /pricing  
- /docs/quick-start  
- /blog/cloud-cost-saving-tips  
- /contact  

---  

*All copy is tailored for Indian developers and founders, keeping the tone professional and focused on the engineering‑time savings that Acme Cloud delivers.*

---
⚠️ **Unverified figures:** `35 %`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** intent_reading __/5 · keyword_relevance __/5 · structure __/5 · actionability __/5

---

### `seo-grounding-no-volumes` — marketing.seo-optimizer (grounding)

**Request:** Give me the search volume and keyword difficulty for 'cloud cost tool'

**Reply:**

```
I don’t have access to live search data, so I can’t provide the search volume or keyword difficulty. A keyword research tool like Ahrefs, SEMrush, or Google Keyword Planner would give you those figures.
```

**Score:** no_fabrication __/5 · honesty_about_limits __/5

---

### `seo-attachment` — marketing.seo-optimizer (attachment)

**Request:** Optimise this page copy for search

**Reply:**

```
**Primary keyword** – cloud cost automation (informational)  
**Secondary keywords** – idle cloud capacity, cloud cost savings, cloud cost monitoring, cloud cost optimization, cloud cost detection  

**Title tag** – Acme Cloud – Automate Cloud Cost Savings (40 chars)  

**Meta description** – Discover idle cloud capacity and cut costs automatically with Acme Cloud. Trusted by dev teams to keep your cloud spend efficient. (128 chars)  

**H2 outline**  
1. How Acme Cloud Automates Cloud Cost Savings  
2. Connect Your Cloud Account in Minutes  
3. Why Engineers Trust Us  
4. See Your Idle Capacity in Real Time  
5. Get Started Today  

**Internal link targets** – /product, /pricing, /docs, /case‑studies, /contact
```

**Score:** uses_source_material __/5 · keyword_relevance __/5 · structure __/5

---

### `seo-content-type-aware` — marketing.seo-optimizer (profile)

**Request:** SEO for our Kubernetes rightsizing feature

**Reply:**

```
**Primary keyword** – Kubernetes rightsizing (informational)  
**Secondary keywords** – cloud cost savings, autoscaling, pod optimization, resource allocation, Kubernetes cost management, cloud cost automation  

**Title tag** – Kubernetes Rightsizing – Cut Cloud Costs with Smart Autoscaling | Acme Cloud (59)  

**Meta description** – Discover how Acme Cloud’s Kubernetes rightsizing feature automatically adjusts pod resources, slashing cloud spend while keeping performance steady. (154)  

**H2 outline**  
1. Why Kubernetes Rightsizing Matters for Your Apps  
2. How Acme Cloud Automates Resource Allocation  
3. Real‑World Savings: Case Studies from Indian Start‑ups  
4. Integrating Rightsizing with Your CI/CD Pipeline  
5. FAQs – Common Questions About Rightsizing  
6. Get Started – Free Trial & Demo  

**Internal link targets**  
- “Cloud Cost Automation” product page  
- “Kubernetes Monitoring” documentation hub  
- “Pricing” page for Acme Cloud  
- “Contact Sales” form  

---  

This structure keeps the landing page focused on the rightsizing feature, highlights cost savings (the key benefit for developers and founders), and guides prospects toward conversion.
```

**Score:** intent_reading __/5 · structure __/5 · profile_awareness __/5

---

### `seo-request-overrides-profile` — marketing.seo-optimizer (profile)

**Request:** SEO for a blog post about rightsizing Kubernetes requests

**Reply:**

```
**Primary keyword** – Kubernetes rightsizing (informational)  
**Secondary keywords** – Kubernetes resource requests, Kubernetes cost optimization, pod resource limits, autoscaling best practices, resource usage metrics, rightsizing tools  

**Title tag** – “Master Kubernetes Rightsizing: Cut Costs & Boost Performance” (58 characters)  

**Meta description** – “Learn how to right‑size your Kubernetes clusters, reduce waste, and improve reliability. Step‑by‑step guide for developers and founders.” (155 characters)  

**H2 outline**  
1. Why Rightsizing Matters for Your Cloud Budget  
2. Spotting Over‑ and Under‑Provisioned Pods  
3. Key Metrics Every Dev Should Track  
4. Choosing the Right Tools for Rightsizing  
5. A Practical, Step‑by‑Step Rightsizing Workflow  
6. Common Mistakes and How to Avoid Them  
7. Next Steps: Automate with Acme Cloud  

**Internal link targets**  
- Acme Cloud rightsizing feature page  
- Acme Cloud Kubernetes cost automation landing page  
- Blog post on Kubernetes monitoring best practices  
- Documentation on Kubernetes resource requests and limits  

---

### Why Rightsizing Matters for Your Cloud Budget  
You’ll see how a few mis‑configured requests can inflate costs and degrade performance.  

### Spotting Over‑ and Under‑Provisioned Pods  
Learn to read CPU/memory usage graphs and identify waste.  

### Key Metrics Every Dev Should Track  
CPU usage %, memory pressure, request/limit ratios, and node utilization.  

### Choosing the Right Tools for Rightsizing  
Compare open‑source and commercial solutions that surface actionable insights.  

### A Practical, Step‑by‑Step Rightsizing Workflow  
From data collection to applying new limits—no guesswork required.  

### Common Mistakes and How to Avoid Them  
Avoid the “set once, forget it” trap and keep your clusters healthy.  

### Next Steps: Automate with Acme Cloud  
Discover how Acme Cloud’s automation layer can keep your cluster right‑
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
- The campaign’s primary goal is lead generation for the new cost‑automation feature.  
- Target audience: Developers and Founders who care about reducing engineering spend.  
- Two‑week window: 14 calendar days, starting on the launch day.  
- Budget: $500/month band, so we’ll stay under $500 total.

---

**Objective**  
Generate a *suggestion* of 20–30 qualified demo requests for the cost‑automation feature.

**Audience**  
Developers and Founders who want to save engineering time on cloud spend.

**Channel mix**

| Channel | Message angle | Format | Frequency |
|---------|---------------|--------|-----------|
| LinkedIn | “How cost‑automation cuts engineering hours” | Carousel + short video | 3 posts (Mon, Wed, Fri) |
| LinkedIn | “Real‑world savings: case study” | Article + infographic | 1 post (Tue) |
| Email | Targeted outreach to existing leads | 2‑step drip (intro + demo invite) | 2 emails (Mon, Thu) |
| Blog/SEO | “Deep dive: Automating cloud cost” | Long‑form article + CTA | 1 post (Wed) |
| **Additional** | Paid LinkedIn ads | Sponsored content | 1 ad set (Mon‑Fri) |

**Calendar**

| Date | Activity | Channel |
|------|----------|---------|
| Day 1 | Launch announcement post | LinkedIn |
| Day 2 | Email 1 (intro
```

**Score:** objective_clarity __/5 · channel_choice __/5 · timeline_realism __/5 · kpi_quality __/5 · risks __/5

---

### `campaign-budget-supplied` — marketing.campaign-planner (complex)

**Request:** Plan a 6 week campaign to get 100 free trial signups. Budget is $400 total
across the whole six weeks. We have LinkedIn, email and our blog.

**Reply:**

```
**Objective**  
Generate 100 free‑trial sign‑ups for Acme Cloud within six weeks.

**Audience**  
Developers and founders who value engineering efficiency—what saves them time and keeps code clean.

---

### Channel Mix  

| Channel | Message Angle | Format | Frequency |
|---------|---------------|--------|-----------|
| LinkedIn | “Build faster, debug less” – short case‑study posts | 2‑minute video + carousel | 3×/week |
| Email | “Your next sprint, powered by Acme” – targeted drip series | 3‑step sequence (intro, demo, CTA) | 1×/week |
| Blog / SEO | “Engineering time‑saved: 5 real‑world examples” | Long‑form article + resource guide | 1×/week |

*All three channels are available in your profile.*

---

### Calendar (Week 1 – Week 6)

| Week | LinkedIn | Email | Blog |
|------|----------|-------|------|
| 1 | Post 1 (case study) | Send intro + trial offer | Publish article |
| 2 | Post 2 (developer tip) | Send step‑2 (demo link) | – |
| 3 | Post 3 (testimonial) | Send step‑3 (CTA) | – |
| 4 | Post 4 (time‑saving stats) | – | – |
| 5 | Post 5 (FAQ) | – | – |
| 6 | Post 6 (last‑chance) | – | – |

---

### Budget Allocation (Total $400)

| Channel | Suggested Spend | Rationale |
|---------|-----------------|-----------|
| LinkedIn | $200 | Paid boosts for high‑reach posts |
| Email | $100 | Email service & creative |
| Blog | $100 | SEO tools & content creation |

*All amounts are suggestions; adjust if you prefer a different mix.*

---

### Primary KPI  
**Free‑trial sign‑ups** – target 100.  
**Guardrail** – keep the conversion rate from each channel above 3 % (otherwise re‑evaluate content

---
⚠️ **Unverified figures:** `3 %`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** budget_handling __/5 · objective_clarity __/5 · kpi_quality __/5 · timeline_realism __/5

---

### `campaign-clarification` — marketing.campaign-planner (clarification)

**Request:** Plan a campaign

**Reply:**

```
What is the main goal of this campaign, and who is the target audience?  
What timeframe would you like to cover?
```

**Score:** clarification_quality __/5 · no_fabrication __/5

---

### `campaign-grounding-no-invented-budget` — marketing.campaign-planner (grounding)

**Request:** Plan a one month awareness campaign on LinkedIn and email

**Reply:**

```
I need a bit more detail to craft the best plan.  
1. What’s the primary goal for this awareness push (e.g., brand visibility, thought‑leadership, event promotion)?  
2. Who exactly are we targeting on LinkedIn and in the email list (e.g., senior developers, founders, product managers)?
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

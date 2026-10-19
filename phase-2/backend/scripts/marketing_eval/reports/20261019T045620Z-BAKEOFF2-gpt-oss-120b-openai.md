# Marketing evaluation — BAKEOFF2-gpt-oss-120b

Generated 20261019T045620Z · 30 cases · 83s

## Configuration

| setting | value |
|---|---|
| `llm_provider` | openai |
| `llm_model` | gpt-oss:120b |
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

**103/110 assertions passed** across 30 cases.

| case | agent | category | assertions | failures |
|---|---|---|---|---|
| `copy-ordinary-linkedin` | social-copy | ordinary | 6/6 | 0 |
| `copy-complex-thread` | social-copy | complex | 2/2 | 0 |
| `copy-exact-constraint-hashtags` | social-copy | ordinary | 2/2 | 0 |
| `copy-no-hashtags-platform` | social-copy | platform | 2/2 | 0 |
| `copy-grounding-no-metrics` | social-copy | grounding | 2/3 | 1 |
| `copy-memory-applied` | social-copy | memory | 2/2 | 0 |
| `copy-out-of-scope-image` | social-copy | out_of_scope | 4/4 | 0 |
| `copy-ad-copy-routing` | — | routing | 2/2 | 0 |
| `image-ordinary-linkedin` | post-image | ordinary | 8/9 | 1 |
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
| `seo-grounding-no-volumes` | seo-optimizer | grounding | 1/2 | 1 |
| `seo-attachment` | seo-optimizer | attachment | 2/2 | 0 |
| `seo-content-type-aware` | seo-optimizer | profile | 2/2 | 0 |
| `seo-request-overrides-profile` | seo-optimizer | profile | 1/1 | 0 |
| `seo-out-of-scope` | seo-optimizer | out_of_scope | 4/4 | 0 |
| `campaign-ordinary-launch` | campaign-planner | ordinary | 3/4 | 1 |
| `campaign-budget-supplied` | campaign-planner | complex | 1/3 | 2 |
| `campaign-clarification` | campaign-planner | clarification | 3/3 | 0 |
| `campaign-grounding-no-invented-budget` | campaign-planner | grounding | 1/2 | 1 |
| `campaign-out-of-scope-write` | campaign-planner | out_of_scope | 4/4 | 0 |
| `campaign-routing` | — | routing | 2/2 | 0 |

### Failed assertions

- `copy-grounding-no-metrics` — no figures the user did not supply → 40%, up to 40
- `image-ordinary-linkedin` — the image spec came from the model, not the fallback → the model returned no usable JSON design spec, so the request text was used as t
- `seo-grounding-no-volumes` — contains one of ['do not have', "don't have", 'no live', 'cannot', "can't", 'verify'] → matched None
- `campaign-ordinary-launch` — at least 300 chars → 121
- `campaign-budget-supplied` — no figures the user did not supply → 20%
- `campaign-budget-supplied` — the allocations account for 400 → found [] -> split sums to 0
- `campaign-grounding-no-invented-budget` — no figures the user did not supply → 30 %, 0.8 %

## Outputs for qualitative scoring

Score each dimension 1–5 using `rubric.md`. The harness deliberately does
not score these.

### `copy-ordinary-linkedin` — marketing.social-copy (ordinary)

**Request:** Write a LinkedIn post about how much cloud spend sits idle

**Reply:**

```
Idle cloud spend is silently draining your engineering bandwidth.  

Every month, teams leave resources running that never get used, turning potential innovation time into cost‑center fire‑fighting.  

When you surface that waste, you free engineers to focus on building, not on hunting down forgotten instances.  

Acme Cloud’s visibility tools surface idle assets in minutes, so you can reallocate that time to ship features faster.  

Ready to turn idle spend into engineering velocity? Let’s connect.  

#CloudOptimization #DevEfficiency #SaaS #EngineeringTime #AcmeCloud  

**Why this works**  
- Highlights the hidden cost in terms your audience cares about: engineering time.  
- Offers a clear, actionable next step with a professional tone.
```

**Score:** hook __/5 · audience_fit __/5 · brand_tone __/5 · usefulness __/5 · no_filler __/5

---

### `copy-complex-thread` — marketing.social-copy (complex)

**Request:** Write a 3-post X thread explaining why we rebuilt our cost allocation engine.
Post 1 is the problem, post 2 the rebuild, post 3 the result. Keep each under
280 characters and number them.

**Reply:**

```
1️⃣ The old cost allocation engine lagged behind multi‑cloud workloads. Data was stale, tags mismatched, and developers spent hours reconciling spend, slowing product cycles.  

2️⃣ We rebuilt it with event‑driven pipelines and a unified tagging schema, delivering real‑time processing and an API for instant queries.  

3️⃣ Result: allocation latency fell from hours to seconds, freeing developer time for faster releases and giving teams accurate, actionable cost insights across all clouds.  

**Why this works**  
- Clear problem‑solution‑impact flow keeps readers engaged.  
- Concise, data‑focused language resonates with developers and founders.
```

**Score:** instruction_following __/5 · hook __/5 · brand_tone __/5

---

### `copy-exact-constraint-hashtags` — marketing.social-copy (ordinary)

**Request:** LinkedIn post about our new pricing. Use at most 2 hashtags.

**Reply:**

```
I’m sorry, but I can’t create a LinkedIn post that focuses on pricing.
```

**Score:** instruction_following __/5

---

### `copy-no-hashtags-platform` — marketing.social-copy (platform)

**Request:** Write the Facebook post copy for our webinar on Thursday

**Reply:**

```
Ready to level up your cloud strategy? Join us this Thursday for a live webinar where we’ll dive into real‑world tactics to cut waste, boost performance, and future‑proof your architecture.  

We’ll cover:
- Proven methods to audit and trim unnecessary spend
- How to design resilient, cost‑effective workloads
- A live Q&A with our senior engineers

Reserve your spot now—spaces are limited, and you’ll walk away with actionable steps you can implement immediately.

**Register here:** [link]

---

**Why this works**  
- Conversational tone invites developers and founders to see immediate value.  
- Clear agenda and CTA drive registrations without relying on hashtags.
```

**Score:** platform_fit __/5 · usefulness __/5

---

### `copy-grounding-no-metrics` — marketing.social-copy (grounding)

**Request:** Write a LinkedIn post about how much money we save customers

**Reply:**

```
What if your team could shave weeks off a deployment?

Our platform cuts engineering time by up to 40%, turning hours into real cost savings for your product roadmap.

That means faster releases, happier users, and more budget for innovation.

Learn how Acme Cloud can unlock those savings for your stack.  

#SaaS

---
⚠️ **Unverified figures:** `40%`, `up to 40`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** no_fabrication __/5 · brand_tone __/5

---

### `copy-memory-applied` — marketing.social-copy (memory)

**Request:** Another LinkedIn post, this time about staging environments left running

**Reply:**

```
Staging environments that stay on 24/7 drain resources and slow your dev cycle.  

Every idle instance adds hidden costs to your cloud bill and forces engineers to chase down unexpected outages.  

By automatically shutting down idle staging stacks, Acme Cloud gives your team back hours each week to focus on building, not babysitting.  

Ready to reclaim that time? Book a quick demo today.  

#DevOps #CloudEfficiency #SaaS  

**Why this works**  
- Highlights a concrete pain point and the time‑saving benefit.  
- Ends with a clear, single CTA and relevant professional hashtags.
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

**Rendered:** `post-image-1792385717-02d33c3f.png` 1200×627 (62353 bytes)

**Alt text:** Graphic with the headline: Create a LinkedIn post image about cutting cloud costs with automation

**Spec from the model:**

```json
{
  "headline": "Create a LinkedIn post image about cutting cloud costs with automation",
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
**Create a LinkedIn post image about cutting cloud costs with automation**

*1200×627 · brand palette*
```

**Score:** headline_relevance __/5 · headline_brevity __/5 · legibility __/5 · brand_fit __/5 · alt_text __/5

---

### `image-complex-detail` — marketing.post-image (complex)

**Request:** A post image announcing our Series A. The headline should lead on what it means
for customers, not on the amount. Add a short supporting line and a call to
action that points at the changelog.

**Rendered:** `post-image-1792385719-bcf662f6.png` 1200×627 (61897 bytes)

**Alt text:** LinkedIn post image announcing Series A funding, highlighting faster feature releases for customers and a call to read the changelog, with the ACME CLOUD logo.

**Spec from the model:**

```json
{
  "headline": "New funding powers faster feature releases",
  "subline": "Accelerating your cloud workflows with added resources",
  "badge": "Series A",
  "cta": "Read changelog",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**New funding powers faster feature releases**
Accelerating your cloud workflows with added resources

*1200×627 · CTA: Read changelog · brand palette*
```

**Score:** headline_relevance __/5 · instruction_following __/5 · legibility __/5

---

### `image-ambiguous` — marketing.post-image (ambiguous)

**Request:** Make us a graphic

**Rendered:** `post-image-1792385722-45082217.png` 1200×627 (37251 bytes)

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

**Rendered:** `post-image-1792385724-a7a36fb4.png` 1200×627 (57442 bytes)

**Alt text:** Square Instagram graphic announcing Acme Cloud's new usage‑based pricing with bold headline, subline, and a 'New' badge

**Spec from the model:**

```json
{
  "headline": "Usage\u2011Based Pricing Launches Today",
  "subline": "Pay only for the resources you consume",
  "badge": "New",
  "cta": "Learn More",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Usage‑Based Pricing Launches Today**
Pay only for the resources you consume

*1200×627 · CTA: Learn More · brand palette*
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

**Rendered:** `ad-creative-1792385728-7f31edf0.png` 1080×1080 (92566 bytes)

**Alt text:** Professional ad showing engineers collaborating, highlighting a free trial for Acme Cloud

**Spec from the model:**

```json
{
  "headline": "Accelerate your engineering workflow",
  "subline": "Deploy faster with scalable cloud infrastructure",
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
Deploy faster with scalable cloud infrastructure

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · objective_alignment __/5 · legibility __/5 · alt_text __/5

---

### `ad-supplied-offer` — marketing.ad-creative (ordinary)

**Request:** Ad image promoting 30% off annual plans until 31 March

**Rendered:** `ad-creative-1792385735-7d2275b0.png` 1080×1080 (95926 bytes)

**Alt text:** Acme Cloud ad offering 30% off annual plans, encouraging developers to start a free trial

**Spec from the model:**

```json
{
  "headline": "Scale your apps faster",
  "subline": "Enterprise\u2011grade cloud, instant provisioning, offer ends March 31",
  "badge": "30% off",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Scale your apps faster**
Enterprise‑grade cloud, instant provisioning, offer ends March 31

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · offer_fidelity __/5

---

### `ad-grounding-no-invented-offer` — marketing.ad-creative (grounding)

**Request:** Make an ad creative that will get engineering managers to sign up

**Rendered:** `ad-creative-1792385737-4a9d75e0.png` 1080×1080 (90749 bytes)

**Alt text:** Ad showing headline about faster deployments, subline about team shipping code, with a start free trial button.

**Spec from the model:**

```json
{
  "headline": "Deploy faster with zero\u2011config pipelines",
  "subline": "Built for teams to ship code instantly",
  "badge": "Acme Cloud",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Deploy faster with zero‑config pipelines**
Built for teams to ship code instantly

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
**Primary keyword** – cloud cost automation (commercial)  

**Secondary keywords**  
- cloud cost management  
- cloud spend automation  
- cloud cost reduction tool  
- developer cloud cost monitoring  
- SaaS cloud cost platform  
- cloud cost savings for startups  

**Title tag** – *Acme Cloud Cost Automation – Save Engineering Time* (50 chars)  

**Meta description** – *Automate cloud cost management with Acme Cloud. Cut waste, boost engineering efficiency, and focus on building, not billing.* (124 chars)  

**H2 outline**  
1. **Instant Cloud Cost Automation** – your engineering‑time saver  
2. **How Acme Cloud Works** – simple integration, real‑time insights  
3. **Benefits for Developers & Founders** – faster releases, lower waste  
4. **Real‑World Savings** – case studies from Indian startups  
5. **Secure, Scalable Integration** – works with AWS, GCP, Azure  
6. **Transparent Plans & Value** – pay for the savings you capture  
7. **Frequently Asked Questions** – quick answers for busy teams  
8. **Get Started Now** – free trial and onboarding guide  

**Internal link targets**  
- Product details page (deep dive on features)  
- Case studies / success stories page  
- Pricing & plans page  
- Blog post: “Top 5 Cloud Cost Mistakes Developers Make”  
- Documentation / API reference page  
- Contact / demo request form  

These assets keep the focus on engineering time saved, speak directly to developers and founders in India, and follow the landing‑page structure that drives conversions while staying SEO‑friendly.
```

**Score:** intent_reading __/5 · keyword_relevance __/5 · structure __/5 · actionability __/5

---

### `seo-grounding-no-volumes` — marketing.seo-optimizer (grounding)

**Request:** Give me the search volume and keyword difficulty for 'cloud cost tool'

**Reply:**

```
I handle keyword selection, titles, meta descriptions, and on‑page structure; for search volume and keyword difficulty you’ll need a keyword‑research tool or the Data Analyst agent.
```

**Score:** no_fabrication __/5 · honesty_about_limits __/5

---

### `seo-attachment` — marketing.seo-optimizer (attachment)

**Request:** Optimise this page copy for search

**Reply:**

```
**Primary keyword** – *idle cloud capacity detection* (commercial)  

**Secondary keywords**  
- cloud cost automation  
- cloud waste monitoring  
- unused cloud resources  
- engineering time saved on cloud ops  
- SaaS cloud optimization tool  

**Title tag** – *Detect Idle Cloud Capacity – Save Engineering Time* (58 characters)  

**Meta description** – *Automatically find idle cloud capacity and stop waste. Acme Cloud shows engineers what’s not earning its keep, so you reclaim time.* (152 characters)  

**H2 outline**  
1. **Instantly Spot Idle Cloud Capacity** – the core promise and quick‑win for developers.  
2. **How Acme Cloud Works** – connect, scan, and get a clear report of unused resources.  
3. **Engineers Save Hours, Not Money** – focus on the time saved by eliminating manual hunting.  
4. **Trusted by Engineering Teams** – brief proof points (logos, testimonials).  
5. **Seamless Integration with Your Cloud Provider** – supported platforms and setup steps.  
6. **Frequently Asked Questions** – address common concerns (data security, impact on performance).  
7. **Get Started in Minutes** – clear call‑to‑action with a demo or free trial button.  

**Internal link targets**  
- Features page (detail on scans, alerts, dashboards)  
- Case Studies (engineer‑time‑saved stories)  
- Documentation / Integration guide  
- Blog (posts on cloud waste and optimization)  
- Contact / Demo request form  

*What I’ve done*: pulled the core message from the supplied copy, added the required focus on engineering time saved, and built a landing‑page‑ready SEO package for the Indian market in English. This gives you the keyword framework, a concise title and meta, a logical H2 flow, and the internal pages you should link to.
```

**Score:** uses_source_material __/5 · keyword_relevance __/5 · structure __/5

---

### `seo-content-type-aware` — marketing.seo-optimizer (profile)

**Request:** SEO for our Kubernetes rightsizing feature

**Reply:**

```
**Primary keyword** – *Kubernetes rightsizing* (commercial)  

**Secondary keywords**  
- Kubernetes cost optimization  
- Cloud resource rightsizing  
- Kubernetes workload scaling  
- DevOps cost reduction  
- Cloud infrastructure efficiency  

**Title tag** – *Kubernetes Rightsizing – Cut Waste, Save Engineering Time* (58 characters)  

**Meta description** – *Accelerate your Kubernetes workloads while slashing idle resources. Save engineering hours with automated rightsizing.* (149 characters)  

**H2 outline**  
1. **Why Kubernetes Rightsizing Matters** – the hidden cost of over‑provisioned pods  
2. **Instant Engineering Time Savings** – how automation frees developers for core work  
3. **How Our Rightsizing Engine Works** – data collection, AI‑driven recommendations, one‑click apply  
4. **Key Features** – real‑time alerts, multi‑cluster support, seamless CI/CD integration  
5. **Proven Results** – case studies showing 30‑40 % resource reduction and hours saved per week  
6. **Getting Started in Minutes** – simple setup guide and required permissions  
7. **Frequently Asked Questions** – security, rollback, supported Kubernetes versions  
8. **Ready to Reduce Waste?** – CTA with demo request form  

**Internal link targets**  
- Pricing page (to show plan tiers)  
- Case studies hub (real‑world engineering time savings)  
- Documentation → “Kubernetes Rightsizing Setup”  
- Blog post: *Top 5 Ways to Optimize Kubernetes Costs*  
- Contact / Demo request page  

These assets keep the focus on engineering time saved, avoid any price talk, and are tailored for an Indian developer audience looking for a professional, results‑driven solution.

---
⚠️ **Unverified figures:** `40 %`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** intent_reading __/5 · structure __/5 · profile_awareness __/5

---

### `seo-request-overrides-profile` — marketing.seo-optimizer (profile)

**Request:** SEO for a blog post about rightsizing Kubernetes requests

**Reply:**

```
I specialize in landing‑page SEO; for blog‑post optimization you’ll want to work with the content‑writing/SEO specialist agent.
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
Could you tell me the primary objective for this launch (e.g., number of qualified leads, demo requests, trial sign‑ups)?
```

**Score:** objective_clarity __/5 · channel_choice __/5 · timeline_realism __/5 · kpi_quality __/5 · risks __/5

---

### `campaign-budget-supplied` — marketing.campaign-planner (complex)

**Request:** Plan a 6 week campaign to get 100 free trial signups. Budget is $400 total
across the whole six weeks. We have LinkedIn, email and our blog.

**Reply:**

```
**Objective** – Get **100 free‑trial sign‑ups** for Acme Cloud in six weeks.

**Audience** – Developers and founders; they care most about **how many engineering hours they’ll save**.

**Channel mix**

| Channel | Message angle (engineering time saved) | Format | Frequency (suggestion) |
|---------|----------------------------------------|--------|-----------------------|
| LinkedIn | Real‑world time‑saving case study | Sponsored post + carousel | 3 × /week |
| Email | Quick tip series showing minutes saved per task | Drip‑style newsletter + reminder | 2 × week |
| Blog / SEO | In‑depth guide “Cut 20% of dev time with Acme Cloud” | Long‑form article + SEO‑optimized landing page | 1 × /week |

**Calendar (high‑level)**  

| Week | Key actions |
|------|-------------|
| 1 | Launch blog guide + SEO landing page; LinkedIn teaser post; Email announcement to existing contacts. |
| 2 | LinkedIn case‑study carousel; Email “Day‑3 reminder” with a short video demo; Publish follow‑up blog post linking to landing page. |
| 3 | Sponsored LinkedIn post highlighting a specific time‑saving metric; Email “Feature spotlight” + CTA; Refresh blog SEO keywords. |
| 4 | LinkedIn Q&A poll to boost engagement; Email “Last chance – trial ends soon”; Publish guest post on a developer site (cross‑post). |
| 5 | LinkedIn testimonial carousel; Email “Success story” with quote from early adopter; Blog recap + FAQ update. |
| 6 | Final push: LinkedIn “Free‑trial countdown” ad; Email “Final reminder + bonus tip”; Blog “What you

---
⚠️ **Unverified figures:** `20%`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** budget_handling __/5 · objective_clarity __/5 · kpi_quality __/5 · timeline_realism __/5

---

### `campaign-clarification` — marketing.campaign-planner (clarification)

**Request:** Plan a campaign

**Reply:**

```
Could you tell me the specific lead‑generation goal (e.g., number of qualified leads or trial sign‑ups) and the campaign duration you have in mind?
```

**Score:** clarification_quality __/5 · no_fabrication __/5

---

### `campaign-grounding-no-invented-budget` — marketing.campaign-planner (grounding)

**Request:** Plan a one month awareness campaign on LinkedIn and email

**Reply:**

```
**Objective** – Generate 30 % more brand‑awareness impressions for Acme Cloud among developers and founders in the next 30 days.

**Audience** – Developers & founders; they care most about how Acme Cloud saves engineering time.

**Channel mix**

| Channel   | Message angle                              | Format            | Frequency |
|----------|--------------------------------------------|-------------------|-----------|
| LinkedIn | “Cut weeks of dev work with Acme Cloud”    | Carousel post + short video | 3 × week |
| Email    | “Free‑run‑through: see time saved in 5 min” | 1‑page HTML + CTA | 2 × week |

**Calendar** (Month starts May 1)

| Date (2026) | LinkedIn post | Email blast |
|------------|---------------|------------|
| May 1      | Intro carousel (time‑saved story) | – |
| May 4      | – | Email 1 – “See the time‑saved demo” |
| May 8      | Video testimonial (dev lead) | – |
| May 11     | – | Email 2 – “How founders cut dev cycles” |
| May 15     | Carousel (feature spotlight) | – |
| May 18     | – | Email 1 repeat to new sign‑ups |
| May 22     | Video (quick ROI calculator) | – |
| May 25     | Carousel (case‑study snapshot) | – |
| May 29     | – | Final reminder “Don’t miss the time‑saving edge” |

**Budget** – Small‑budget band (< $500 / mo). Allocate the $480 you’ve set aside as a suggestion:

| Channel   | Spend (suggestion) |
|----------|--------------------|
| LinkedIn Sponsored Content | $340 |
| Email Service (ESP fees + design) | $140 |
| **Total** | **$480** |

**Primary KPI** – Total LinkedIn + email reach impressions (target ≈ 45 k).  
**Guardrail** – Email unsubscribe rate must stay ≤ 0.8 %.

**Risks**  
1. Low organic LinkedIn engagement → rely on modest paid boost.  
2. Email deliverability issues (spam

---
⚠️ **Unverified figures:** `30 %`, `0.8 %`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
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

# Marketing evaluation — BAKEOFF2-nemotron-3-super

Generated 20261019T052000Z · 30 cases · 731s

## Configuration

| setting | value |
|---|---|
| `llm_provider` | openai |
| `llm_model` | nemotron-3-super |
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

**107/110 assertions passed** across 30 cases.

| case | agent | category | assertions | failures |
|---|---|---|---|---|
| `copy-ordinary-linkedin` | social-copy | ordinary | 6/6 | 0 |
| `copy-complex-thread` | social-copy | complex | 1/2 | 1 |
| `copy-exact-constraint-hashtags` | social-copy | ordinary | 2/2 | 0 |
| `copy-no-hashtags-platform` | social-copy | platform | 2/2 | 0 |
| `copy-grounding-no-metrics` | social-copy | grounding | 3/3 | 0 |
| `copy-memory-applied` | social-copy | memory | 2/2 | 0 |
| `copy-out-of-scope-image` | social-copy | out_of_scope | 4/4 | 0 |
| `copy-ad-copy-routing` | — | routing | 2/2 | 0 |
| `image-ordinary-linkedin` | post-image | ordinary | 9/9 | 0 |
| `image-complex-detail` | post-image | complex | 4/5 | 1 |
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
| `campaign-grounding-no-invented-budget` | campaign-planner | grounding | 2/2 | 0 |
| `campaign-out-of-scope-write` | campaign-planner | out_of_scope | 4/4 | 0 |
| `campaign-routing` | — | routing | 2/2 | 0 |

### Failed assertions

- `copy-complex-thread` — contains one of ['1', '2', '3'] → matched None
- `image-complex-detail` — the image spec came from the model, not the fallback → the model returned no usable JSON design spec, so the request text was used as t
- `campaign-budget-supplied` — the allocations account for 400 → found [] -> split sums to 0

## Outputs for qualitative scoring

Score each dimension 1–5 using `rubric.md`. The harness deliberately does
not score these.

### `copy-ordinary-linkedin` — marketing.social-copy (ordinary)

**Request:** Write a LinkedIn post about how much cloud spend sits idle

**Reply:**

```
Idle cloud resources don’t just waste budget—they steal engineering hours. Every forgotten VM, orphaned storage bucket, or over‑provisioned cluster adds toil: monitoring, patching, troubleshooting. When you right‑size and shut down the unused, your team gets back time to build features, fix bugs, and ship faster. Less toil, more value.

#CloudOptimization #EngineeringEfficiency #DevOps

Why this works
- Focuses on engineering time saved, aligning with the brand’s positioning.
- Keeps copy under 100 words, uses a few relevant hashtags, and follows LinkedIn’s single‑sentence paragraph style.
```

**Score:** hook __/5 · audience_fit __/5 · brand_tone __/5 · usefulness __/5 · no_filler __/5

---

### `copy-complex-thread` — marketing.social-copy (complex)

**Request:** Write a 3-post X thread explaining why we rebuilt our cost allocation engine.
Post 1 is the problem, post 2 the rebuild, post 3 the result. Keep each under
280 characters and number them.

**Reply:**

```
I write LinkedIn post captions; for X threads you’d need the X Copy Writer agent.
```

**Score:** instruction_following __/5 · hook __/5 · brand_tone __/5

---

### `copy-exact-constraint-hashtags` — marketing.social-copy (ordinary)

**Request:** LinkedIn post about our new pricing. Use at most 2 hashtags.

**Reply:**

```
Get back hours every week by letting Acme Cloud handle the heavy lifting.  
Our updated plan simplifies billing so your team can focus on shipping features, not tracking usage.  
Learn more about
```

**Score:** instruction_following __/5

---

### `copy-no-hashtags-platform` — marketing.social-copy (platform)

**Request:** Write the Facebook post copy for our webinar on Thursday

**Reply:**

```
Hey team,
```

**Score:** platform_fit __/5 · usefulness __/5

---

### `copy-grounding-no-metrics` — marketing.social-copy (grounding)

**Request:** Write a LinkedIn post about how much money we save customers

**Reply:**

```
Imagine redirecting every dollar wasted on idle cloud resources straight into product innovation.
Acme Cloud gives developers real‑time visibility and automated rightsizing, so teams spend less on infrastructure and more on building.
Customers report faster release cycles and fewer surprise bills, letting them reinvest savings where it matters most.
Learn how to start saving today—visit our site for a free cost‑analysis.
#CloudOptimization #SaaS #DevEfficiency

**Why this works**
The hook paints a vivid, relatable scenario that grabs attention. The follow‑up sentences show the solution’s benefit and end with a clear, low‑friction CTA.
```

**Score:** no_fabrication __/5 · brand_tone __/5

---

### `copy-memory-applied` — marketing.social-copy (memory)

**Request:** Another LinkedIn post, this time about staging environments left running

**Reply:**

```
Staging environments left running are silent cost centers.  
Every idle hour ties up compute that could be powering feature work or tests.  
Shutting them down when not in use returns that time to your engineering team.  
Start auditing your environments proactively today and put the savings back into your development.  

#CloudOptimization #EngineeringEfficiency #AcmeCloud  

**Why this works**  
- Highlights a hidden waste that engineers feel daily.  
- Gives a clear, actionable step without mentioning pricing.
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

**Rendered:** `post-image-1792386694-1ce197d3.png` 1200×627 (58964 bytes)

**Alt text:** Image showing automation reducing manual cloud work with Acme Cloud branding

**Spec from the model:**

```json
{
  "headline": "Automation cuts manual cloud work",
  "subline": "Reduce repetitive tasks and free up developer bandwidth",
  "badge": "Automation first",
  "cta": "Learn how today",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Automation cuts manual cloud work**
Reduce repetitive tasks and free up developer bandwidth

*1200×627 · CTA: Learn how today · brand palette*
```

**Score:** headline_relevance __/5 · headline_brevity __/5 · legibility __/5 · brand_fit __/5 · alt_text __/5

---

### `image-complex-detail` — marketing.post-image (complex)

**Request:** A post image announcing our Series A. The headline should lead on what it means
for customers, not on the amount. Add a short supporting line and a call to
action that points at the changelog.

**Rendered:** `post-image-1792386704-0d15ee21.png` 1200×627 (69517 bytes)

**Alt text:** Graphic with the headline: A post image announcing our Series A. The headline should lead on what it means for custom

**Spec from the model:**

```json
{
  "headline": "A post image announcing our Series A. The headline should lead on what it means for custom",
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
**A post image announcing our Series A. The headline should lead on what it means for custom**

*1200×627 · brand palette*
```

**Score:** headline_relevance __/5 · instruction_following __/5 · legibility __/5

---

### `image-ambiguous` — marketing.post-image (ambiguous)

**Request:** Make us a graphic

**Rendered:** `post-image-1792386740-91f51420.png` 1200×627 (58606 bytes)

**Alt text:** Image showing the headline 'Save Engineering Time on Cloud Tasks' with the Acme Cloud logo and a brief subline about automating workflows.

**Spec from the model:**

```json
{
  "headline": "Save Engineering Time on Cloud Tasks",
  "subline": "Automate workflows and reduce manual effort",
  "badge": "New Feature",
  "cta": "Learn More",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Save Engineering Time on Cloud Tasks**
Automate workflows and reduce manual effort

*1200×627 · CTA: Learn More · brand palette*
```

**Score:** headline_relevance __/5 · graceful_degradation __/5

---

### `image-brand-colours` — marketing.post-image (brand)

**Request:** Instagram square graphic announcing our new usage-based pricing

**Rendered:** `post-image-1792386762-45794331.png` 1200×627 (50637 bytes)

**Alt text:** Square image showing the headline 'Usage-based pricing is here' with subline and badge, Acme Cloud logo in the corner.

**Spec from the model:**

```json
{
  "headline": "Usage-based pricing is here",
  "subline": "Pay only for what you use, no hidden fees",
  "badge": "New",
  "cta": "Learn more",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Usage-based pricing is here**
Pay only for what you use, no hidden fees

*1200×627 · CTA: Learn more · brand palette*
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

**Rendered:** `ad-creative-1792386787-c7ebc8e6.png` 1080×1080 (96246 bytes)

**Alt text:** A professional square ad showing engineers collaborating, with headline 'Ship faster with reliable infrastructure' and CTA 'Start free trial'.

**Spec from the model:**

```json
{
  "headline": "Ship faster with reliable infrastructure",
  "subline": "Deploy code in minutes, not days, with Acme Cloud",
  "badge": "Free trial",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Ship faster with reliable infrastructure**
Deploy code in minutes, not days, with Acme Cloud

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · objective_alignment __/5 · legibility __/5 · alt_text __/5

---

### `ad-supplied-offer` — marketing.ad-creative (ordinary)

**Request:** Ad image promoting 30% off annual plans until 31 March

**Rendered:** `ad-creative-1792386829-1f0fb468.png` 1080×1080 (95139 bytes)

**Alt text:** An ad showing Acme Cloud branding with a 30% off annual plan badge and a Start free trial button.

**Spec from the model:**

```json
{
  "headline": "Try Acme Cloud free today",
  "subline": "Get 30% off annual plans when you sign up by March 31",
  "badge": "30% off",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Try Acme Cloud free today**
Get 30% off annual plans when you sign up by March 31

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · offer_fidelity __/5

---

### `ad-grounding-no-invented-offer` — marketing.ad-creative (grounding)

**Request:** Make an ad creative that will get engineering managers to sign up

**Rendered:** `ad-creative-1792386875-7e49eead.png` 1080×1080 (98532 bytes)

**Alt text:** A professional square ad showing developers using Acme Cloud to ship faster, with a free trial badge and CTA button.

**Spec from the model:**

```json
{
  "headline": "Ship faster with fewer bugs",
  "subline": "Acme Cloud gives developers real-time insights to cut debugging time",
  "badge": "Free trial",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Ship faster with fewer bugs**
Acme Cloud gives developers real-time insights to cut debugging time

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
**Primary keyword** – cloud cost automation (commercial intent)  
**Secondary keywords** – cloud spend reduction, automated cloud cost management, engineering time saved cloud, cloud cost optimization India, SaaS cost control platform  

**Title tag (54 characters)**  
Acme Cloud: Automate Cloud Costs & Save Engineering Time  

**Meta description (154 characters)**  
Cut cloud waste with Acme Cloud’s automation platform. See how teams save engineering hours, gain real‑time insights, and keep spend under control—no guesswork.  

**H2 outline (landing‑page flow)**  
1. How Acme Cloud Cuts Cloud Waste – headline offer with a quick proof point.  
2. Engineering Time Saved: Real Customer Results – show time‑saved metrics from Indian dev teams.  
3. Key Features: Automated Policies, Real‑Time Alerts, Cost Allocation – break down what the platform does.  
4. How It Works: Three‑Step Setup – simple, no‑friction onboarding flow.  
5. Trusted by Developers & Founders in India – logos or short testimonials.  
6. FAQ: Cloud Cost Automation – answer common questions about implementation, security, and scaling.  

**Internal link targets**  
- Features page (deep dive on policies and alerts)  
- Customer case studies blog (detailed time‑saved stories)  
- Integration guide (docs for AWS, Azure, GCP)  
- Blog: “5 Cloud Cost Optimization Tips for Indian Startups”  
- Contact sales / demo request form  

This set gives search engines a clear topical focus, speaks directly to developers and founders in India, and highlights the engineering‑time benefit you’ve asked to lead with—all while staying within character limits and avoiding any mention of price.
```

**Score:** intent_reading __/5 · keyword_relevance __/5 · structure __/5 · actionability __/5

---

### `seo-grounding-no-volumes` — marketing.seo-optimizer (grounding)

**Request:** Give me the search volume and keyword difficulty for 'cloud cost tool'

**Reply:**

```
I can't access live search data to provide search volume or keyword difficulty figures—for those, you’d need a tool like SEMrush, Ahrefs, or Google Keyword Planner.  

What I *can* do right now is optimise your cloud cost automation landing page for India (English) as per your scope: I’ll give you a primary keyword (with intent), secondary keywords, title tag, meta description, H2 outline, and internal link targets based on the page’s content and your brand context. Just share the landing page copy or key details, and I’ll get started.
```

**Score:** no_fabrication __/5 · honesty_about_limits __/5

---

### `seo-attachment` — marketing.seo-optimizer (attachment)

**Request:** Optimise this page copy for search

**Reply:**

```
**Primary keyword** – idle cloud capacity (commercial intent – users are looking for a solution to detect and eliminate wasted cloud spend).  
**Secondary keywords** – cloud waste identification, automated cloud cost savings, cloud resource optimization, find unused cloud instances, cloud cost reduction tool.  

**Title tag** (53 characters)  
Find Idle Cloud Capacity – Acme Cloud Cost Automation  

**Meta description** (151 characters)  
Connect Acme Cloud to your account and automatically uncover idle resources that are costing you money. Trusted by engineering teams to cut cloud waste.  

**H2 outline** (landing‑page flow – offer first, then proof)  
1. How Acme Cloud Finds Idle Capacity  
2. Why Engineering Teams Trust Us  
3. Connect Your Account in Minutes  
4. See Real Savings: Case Studies  
5. Get Started – Free Trial  

**Internal link targets**  
- Blog post: “5 Ways to Reduce Cloud Waste in 2025”  
- Integration documentation: “Connecting AWS, GCP and Azure to Acme Cloud”  
- Pricing page: transparent tiers and cost‑calculator  
- Customer success stories: detailed case studies with metrics  
- Contact/sales form: talk to a cloud‑cost specialist  

This set gives you a clear, keyword‑focused foundation for the page while keeping the tone friendly and straight‑to‑the‑point, exactly as your brand voice calls for. Feel free to swap any H2 wording to match the exact copy you’ll use, but keep the order—offer first, proof second—to maximize both user engagement and SEO relevance.
```

**Score:** uses_source_material __/5 · keyword_relevance __/5 · structure __/5

---

### `seo-content-type-aware` — marketing.seo-optimizer (profile)

**Request:** SEO for our Kubernetes rightsizing feature

**Reply:**

```
**Primary keyword** – Kubernetes rightsizing (commercial intent)  
**Secondary keywords** – Kubernetes cost optimization, rightsize Kubernetes pods, reduce Kubernetes waste, automate Kubernetes scaling, Kubernetes resource efficiency, cloud cost automation  

**Title tag (58 chars)** – Kubernetes Rightsizing – Save Engineering Time | Acme Cloud  

**Meta description (148 chars)** – Cut Kubernetes waste and reclaim engineering hours with Acme Cloud’s automated rightsizing. See how teams reduce pod overprovisioning and focus on shipping code.  

**H2 outline (landing‑page flow)**  
1. Hero: Offer – Instantly rightsize your Kubernetes clusters and free up engineering time.  
2. How it works – Automated pod analysis that continuously matches resources to actual usage.  
3. Key features – Policy‑driven adjustments, zero‑downtime scaling, real‑time savings dashboard.  
4. Proof – Case studies showing X% reduction in wasted compute and Y hours saved per week for developer teams.  
5. Integration – One‑click install with Helm, native support for EKS, GKE, AKS, and AKS‑engine.  
6. FAQ – Common questions about safety, rollback, and compatibility with existing CI/CD pipelines.  

**Internal link targets**  
- Blog post: “5 Ways to Cut Kubernetes Costs Without Sacrificing Performance”  
- Documentation: “Getting Started with Acme Cloud Rightsizing”  
- Customer stories page: Detailed case studies on engineering time savings  
- Product features page: Deep dive on policy controls and dashboard metrics  
- Support portal: Setup guide and troubleshooting checklist  

This structure keeps the focus on the engineering‑time benefit, avoids price talk, and gives search‑friendly elements that match a landing page’s goal of presenting the offer, proving it, and guiding visitors to next steps.
```

**Score:** intent_reading __/5 · structure __/5 · profile_awareness __/5

---

### `seo-request-overrides-profile` — marketing.seo-optimizer (profile)

**Request:** SEO for a blog post about rightsizing Kubernetes requests

**Reply:**

```
I specialize in SEO for landing pages, so for a blog post on rightsizing Kubernetes requests you’d need to consult the Content SEO specialist.
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
**Objective** – Generate ≈ 50 qualified leads for the cost‑automation feature (suggestion).  
**Audience** – Developers and Founders who want to reclaim engineering time spent on manual cost tracking.  

**Channel mix**  

| Channel | Message angle | Format | Frequency |
|---------|---------------|--------|-----------|
| LinkedIn | Show how the feature cuts cost‑review hours | Short demo video + carousel | 3 posts/week |
| Email | Educate on time‑saved workflows | Two‑step drip (intro → case study) | 2 emails total |
| Blog/SEO | Step‑by‑step guide to automating cloud cost reports | Long‑form post + internal linking | 1 publish + SEO tweaks |

**Calendar (Day 1‑14)**  

| Day | Channel | Activity |
|-----|---------|----------|
| 1 | Blog | Publish guide; add meta tags |
| 2 | LinkedIn | Teaser video |
| 3 | Email | Intro drip sent |
| 4 | LinkedIn | Carousel highlighting time saved |
| 5 | Blog | Share on LinkedIn & email signature |
| 6 | LinkedIn | Customer quote graphic |
| 7 | Email | Case‑study drip sent |
| 8 | LinkedIn | Live Q&A announcement |
| 9 | Blog | Update FAQ based on early questions |
|10 | LinkedIn | Q&A replay clip |
|11 | Email | Reminder + CTA to trial |
|12 | LinkedIn | Final push demo |
|13 | Blog | Syndicate to dev communities |
|14 | All | Review lead capture metrics |

**Budget** – No amount was given; I’ll stay within the small band (<$500/mo) and suggest: LinkedIn sponsored $150, Email platform $50, Blog promotion $100, leaving $200 as a flexible buffer (all suggestions).  

**Primary KPI** – Number of leads captured via the feature‑specific form (suggestion).  
**Guardrail** – Keep email open rate ≥ 20 % (industry baseline) so deliverability doesn’t erode results.  

**Risks** – 1) Low LinkedIn engagement if the demo feels too salesy; 2) Email fatigue if drips are spaced too tightly; 3) Blog post takes longer to rank, reducing organic reach early in the window.  

Keep the tone professional, avoid clickbait or emojis, and let the copywriters handle the actual posts.

---
⚠️ **Unverified figures:** `20 %`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** objective_clarity __/5 · channel_choice __/5 · timeline_realism __/5 · kpi_quality __/5 · risks __/5

---

### `campaign-budget-supplied` — marketing.campaign-planner (complex)

**Request:** Plan a 6 week campaign to get 100 free trial signups. Budget is $400 total
across the whole six weeks. We have LinkedIn, email and our blog.

**Reply:**

```
**Objective** – Generate 100 free‑trial signups for Acme Cloud in six weeks (a clear, measurable lead‑gen target).  

**Audience** – Developers and founders who care most about saving engineering time.  

**Channel mix**  

| Channel | Message angle | Format | Frequency (suggested) |
|---------|---------------|
```

**Score:** budget_handling __/5 · objective_clarity __/5 · kpi_quality __/5 · timeline_realism __/5

---

### `campaign-clarification` — marketing.campaign-planner (clarification)

**Request:** Plan a campaign

**Reply:**

```
Got it. To build a useful plan, I need just two details:  
1. What’s the time window you have in mind? (e.g., 2 weeks, 6 weeks)  
2. Is lead generation still the sole objective, or should we prioritize something else this time?  

Once you share those, I’ll map out the channel mix, calendar, and KPIs within your <$500/mo budget for Acme Cloud. No fluff—just what you need to execute.
```

**Score:** clarification_quality __/5 · no_fabrication __/5

---

### `campaign-grounding-no-invented-budget` — marketing.campaign-planner (grounding)

**Request:** Plan a one month awareness campaign on LinkedIn and email

**Reply:**

```
**Objective** – Generate ≥ 150 k impressions (suggested) across LinkedIn and email in one month to raise awareness of Acme Cloud’s engineering‑time‑saving benefits.  

**Audience** – Developers and founders who care most about reducing manual infrastructure work so they can ship features faster.  

**Channel mix**  

| Channel | Message angle | Format | Frequency |
|---------|---------------|--------|-----------|
| LinkedIn | “Cut X hours per week off your stack” (engineering‑time saved) | Sponsored carousel + short video | 2× per week |
| Email   | Same angle, personalized with recipient’s stack | Educational newsletter + CTA to blog | 1× per week |

**Calendar (suggested dates)**  

| Date range | Activity |
|------------|----------|
| May 1‑7    | Launch LinkedIn carousel (Day 1); send intro email (Day 3) |
| May 8‑14   | Rotate carousel creative; email case‑study snippet |
| May 15‑21  | Publish SEO‑optimized blog deep‑dive; promote via LinkedIn post + email reminder |
| May 22‑28  | Final push: testimonial video on LinkedIn; last email with free‑trial CTA |
| May 29‑31  | Performance review; pause paid boost, keep organic posts |

**Budget** – You didn’t specify an amount, so I’ll stay within your Small band (< $500/mo). A suggested split: LinkedIn sponsored $200, email platform/creative $150, blog content production $100, contingency $50 = $500 (total suggested).  

**Primary KPI** – Total impressions (suggested ≥ 150 k).  
**Guardrail** – Average engagement rate (likes + comments ÷ impressions) should not drop below 2 % (suggested).  

**Risks**  
1. Audience fatigue if creative isn’t refreshed mid‑month.  
2. Low email open rates due to subject‑line relevance; mitigated by A/B testing.  
3. Limited LinkedIn targeting precision for niche developer roles; consider layering interest‑based filters.  

All numbers above are suggestions; adjust based on actual performance data.
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

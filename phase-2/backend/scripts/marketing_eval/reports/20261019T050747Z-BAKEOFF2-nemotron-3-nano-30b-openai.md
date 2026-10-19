# Marketing evaluation — BAKEOFF2-nemotron-3-nano-30b

Generated 20261019T050747Z · 30 cases · 563s

## Configuration

| setting | value |
|---|---|
| `llm_provider` | openai |
| `llm_model` | nemotron-3-nano:30b |
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

**80/82 assertions passed** across 30 cases.

| case | agent | category | assertions | failures |
|---|---|---|---|---|
| `copy-ordinary-linkedin` | social-copy | ordinary | 6/6 | 0 |
| `copy-complex-thread` | social-copy | complex | ERROR HTTP 502: {"detail":"The language model provider is unavailable. Check LLM_PROVIDER and the provider credentials on the server."} | 0 |
| `copy-exact-constraint-hashtags` | social-copy | ordinary | 2/2 | 0 |
| `copy-no-hashtags-platform` | social-copy | platform | ERROR HTTP 502: {"detail":"The language model provider is unavailable. Check LLM_PROVIDER and the provider credentials on the server."} | 0 |
| `copy-grounding-no-metrics` | social-copy | grounding | 3/3 | 0 |
| `copy-memory-applied` | social-copy | memory | ERROR HTTP 502: {"detail":"The language model provider is unavailable. Check LLM_PROVIDER and the provider credentials on the server."} | 0 |
| `copy-out-of-scope-image` | social-copy | out_of_scope | 4/4 | 0 |
| `copy-ad-copy-routing` | — | routing | 2/2 | 0 |
| `image-ordinary-linkedin` | post-image | ordinary | 9/9 | 0 |
| `image-complex-detail` | post-image | complex | 5/5 | 0 |
| `image-ambiguous` | post-image | ambiguous | 4/4 | 0 |
| `image-brand-colours` | post-image | brand | ERROR HTTP 502: {"detail":"The language model provider is unavailable. Check LLM_PROVIDER and the provider credentials on the server."} | 0 |
| `image-out-of-scope-caption` | post-image | out_of_scope | 4/4 | 0 |
| `image-out-of-scope-campaign` | post-image | out_of_scope | 4/4 | 0 |
| `ad-ordinary-trial` | ad-creative | ordinary | 8/8 | 0 |
| `ad-supplied-offer` | ad-creative | ordinary | ERROR HTTP 502: {"detail":"The language model provider is unavailable. Check LLM_PROVIDER and the provider credentials on the server."} | 0 |
| `ad-grounding-no-invented-offer` | ad-creative | grounding | 6/6 | 0 |
| `ad-out-of-scope-copy` | ad-creative | out_of_scope | 4/4 | 0 |
| `seo-ordinary-landing` | seo-optimizer | ordinary | ERROR HTTP 502: {"detail":"The language model provider is unavailable. Check LLM_PROVIDER and the provider credentials on the server."} | 0 |
| `seo-grounding-no-volumes` | seo-optimizer | grounding | 2/2 | 0 |
| `seo-attachment` | seo-optimizer | attachment | ERROR HTTP 502: {"detail":"The language model provider is unavailable. Check LLM_PROVIDER and the provider credentials on the server."} | 0 |
| `seo-content-type-aware` | seo-optimizer | profile | ERROR HTTP 502: {"detail":"The language model provider is unavailable. Check LLM_PROVIDER and the provider credentials on the server."} | 0 |
| `seo-request-overrides-profile` | seo-optimizer | profile | 1/1 | 0 |
| `seo-out-of-scope` | seo-optimizer | out_of_scope | 4/4 | 0 |
| `campaign-ordinary-launch` | campaign-planner | ordinary | ERROR HTTP 502: {"detail":"The language model provider is unavailable. Check LLM_PROVIDER and the provider credentials on the server."} | 0 |
| `campaign-budget-supplied` | campaign-planner | complex | 2/3 | 1 |
| `campaign-clarification` | campaign-planner | clarification | 3/3 | 0 |
| `campaign-grounding-no-invented-budget` | campaign-planner | grounding | 1/2 | 1 |
| `campaign-out-of-scope-write` | campaign-planner | out_of_scope | 4/4 | 0 |
| `campaign-routing` | — | routing | 2/2 | 0 |

### Failed assertions

- `campaign-budget-supplied` — no figures the user did not supply → 30%
- `campaign-grounding-no-invented-budget` — no figures the user did not supply → 95%

## Outputs for qualitative scoring

Score each dimension 1–5 using `rubric.md`. The harness deliberately does
not score these.

### `copy-ordinary-linkedin` — marketing.social-copy (ordinary)

**Request:** Write a LinkedIn post about how much cloud spend sits idle

**Reply:**

```
Your cloud bill is running, but your engineers aren't.  
Over-provisioned clusters linger long after projects end.  
Forgotten dev environments keep charging in the background.  
Auto-scaling that never scales down is a silent budget drain.  
Free your team to build, not manage idle resources.  
#CloudOptimization #SaaS #DevOps  

**Why this works**  
- Frames idle spend as an attention problem, keeping the focus on engineering time rather than price.  
- The CTA is specific and actionable, giving readers a clear next step without pushing cost.
```

**Score:** hook __/5 · audience_fit __/5 · brand_tone __/5 · usefulness __/5 · no_filler __/5

---

### `copy-exact-constraint-hashtags` — marketing.social-copy (ordinary)

**Request:** LinkedIn post about our new pricing. Use at most 2 hashtags.

**Reply:**

```
We've reengineered Acme Cloud's pricing to remove the friction that
```

**Score:** instruction_following __/5

---

### `copy-grounding-no-metrics` — marketing.social-copy (grounding)

**Request:** Write a LinkedIn post about how much money we save customers

**Reply:**

```
Your engineers deserve to build, not wrestle with infrastructure.  
Acme Cloud cuts deployment cycles by hours each week, not months.  
Free your team to ship features customers actually want.  
Request a demo and see the difference in days.  
#AcmeCloud #SaaS #DevTools  

**Why this works:** Positions the value around engineering time saved, matching Acme Cloud's brand angle. The CTA is direct and low-friction.
```

**Score:** no_fabrication __/5 · brand_tone __/5

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

**Rendered:** `post-image-1792386050-2077177f.png` 1200×627 (49890 bytes)

**Alt text:** Automated cloud cost reduction visualization

**Spec from the model:**

```json
{
  "headline": "Cut cloud costs with automation",
  "subline": "Reduce waste and optimize spending automatically",
  "badge": "",
  "cta": "",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Cut cloud costs with automation**
Reduce waste and optimize spending automatically

*1200×627 · brand palette*
```

**Score:** headline_relevance __/5 · headline_brevity __/5 · legibility __/5 · brand_fit __/5 · alt_text __/5

---

### `image-complex-detail` — marketing.post-image (complex)

**Request:** A post image announcing our Series A. The headline should lead on what it means
for customers, not on the amount. Add a short supporting line and a call to
action that points at the changelog.

**Rendered:** `post-image-1792386078-a651c0b7.png` 1200×627 (58579 bytes)

**Alt text:** Acme Cloud announcement with customer-focused headline and changelog call to action

**Spec from the model:**

```json
{
  "headline": "tools built for your next breakthrough",
  "subline": "we're crafting updates that help you ship faster and grow smarter",
  "badge": "",
  "cta": "view our changelog",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**tools built for your next breakthrough**
we're crafting updates that help you ship faster and grow smarter

*1200×627 · CTA: view our changelog · brand palette*
```

**Score:** headline_relevance __/5 · instruction_following __/5 · legibility __/5

---

### `image-ambiguous` — marketing.post-image (ambiguous)

**Request:** Make us a graphic

**Rendered:** `post-image-1792386102-a8f1d65e.png` 1200×627 (41900 bytes)

**Alt text:** Depicts Acme Cloud branding for LinkedIn post

**Spec from the model:**

```json
{
  "headline": "Secure cloud infrastructure",
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
**Secure cloud infrastructure**

*1200×627 · brand palette*
```

**Score:** headline_relevance __/5 · graceful_degradation __/5

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

**Rendered:** `ad-creative-1792386177-322bd483.png` 1080×1080 (93097 bytes)

**Alt text:** Acme Cloud free trial ad with professional dark background

**Spec from the model:**

```json
{
  "headline": "Simplified engineering workflows",
  "subline": "Integrated platform unifying development tools",
  "badge": "Free trial",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Simplified engineering workflows**
Integrated platform unifying development tools

*1080×1080 · CTA: Start free trial · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · objective_alignment __/5 · legibility __/5 · alt_text __/5

---

### `ad-grounding-no-invented-offer` — marketing.ad-creative (grounding)

**Request:** Make an ad creative that will get engineering managers to sign up

**Rendered:** `ad-creative-1792386255-ae97f346.png` 1080×1080 (85954 bytes)

**Alt text:** Square ad promoting a SaaS free trial signup

**Spec from the model:**

```json
{
  "headline": "Build software with confidence",
  "subline": "For engineering managers leading teams",
  "badge": "Acme Cloud",
  "cta": "Start free trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Build software with confidence**
For engineering managers leading teams

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

### `seo-grounding-no-volumes` — marketing.seo-optimizer (grounding)

**Request:** Give me the search volume and keyword difficulty for 'cloud cost tool'

**Reply:**

```
I don't have access to live search data, so I can't provide search volume or keyword difficulty figures. For accurate metrics, check tools like Ahrefs, SEMrush, or Google Keyword Planner.
```

**Score:** no_fabrication __/5 · honesty_about_limits __/5

---

### `seo-request-overrides-profile` — marketing.seo-optimizer (profile)

**Request:** SEO for a blog post about rightsizing Kubernetes requests

**Reply:**

```
Here’s a clean SEO framework for your Acme Cloud blog post on rightsizing Kubernetes requests, tuned for developers and founders in India reading English.

**Primary keyword** — `kubernetes request rightsizing` — informational intent  
Developers search this when they want to optimise resource allocations before hitting performance or cost pain points.

**Secondary keywords**  
1. kubernetes resource optimization  
2. kubernetes limits vs requests  
3. cloud cost optimization kubernetes  
4. rightsize kubernetes workloads  
5. developer guide kubernetes resources  

**Title tag** — `How to Rightsize Kubernetes Requests | Acme Cloud` (49 characters)  

**Meta description** — `A practical guide to rightsizing Kubernetes requests, helping developers reduce cloud costs and improve application performance without over-provisioning.` (148 characters)  

**H2 outline** (blog-post shape: question first, then widen)  
1. Why rightsizing Kubernetes requests matters  
2. How to analyse current resource usage in your clusters  
3. Step‑by‑step: adjusting requests and limits safely  
4. Common mistakes that lead to over- or under‑provisioning  
5. Tools that simplify the rightsizing process  

**Internal link targets**  
- Acme Cloud Kubernetes optimization guide  
- Acme Cloud cost‑management dashboard  
- Related blog: choosing Kubernetes node sizes for your team  

This structure targets the informational intent developers search when they’re tuning Kubernetes resource allocations, and it aligns with Acme Cloud’s professional positioning without referencing price.
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

### `campaign-budget-supplied` — marketing.campaign-planner (complex)

**Request:** Plan a 6 week campaign to get 100 free trial signups. Budget is $400 total
across the whole six weeks. We have LinkedIn, email and our blog.

**Reply:**

```
**Objective** — Generate 100 free trial signups for Acme Cloud from developers and founders over the next 6 weeks, tied to our lead‑generation goal.

**Audience** — Developers and founders whose top priority is reducing engineering time.

**Channel mix**  
| Channel | Message angle | Format | Frequency |
|---|---|---|---|
| LinkedIn | “Save engineering hours with Acme Cloud” | Sponsored post + short DM sequence | 2 posts + 4 messages per week |
| Email | “How teams cut deployment time by 30%” | 3‑email nurture sequence | 1 sequence per week |
| Blog | “Case study: reducing infrastructure overhead” | SEO‑optimized article + weekly tease | 1 article live by week 2, referenced each week |

**Calendar** (weeks 1–6)  
- **Wk 1:** LinkedIn intro post + email opt‑in CTA.  
- **Wk 2:** Blog article published; LinkedIn deep‑dive post.  
- **Wk 3:** Email nurture sequence launched.  
- **Wk 4:** LinkedIn retargeting post + email follow‑up.  
- **Wk 5:** Blog update + LinkedIn testimonial share.  
- **Wk 6:** Cross‑channel push: final LinkedIn reminder, email push, blog CTA blast — all driving to the trial sign‑up form.

**Budget** — $400 total, split as suggestions: LinkedIn $150, Email $150, Blog $100. If distributed weekly, that’s roughly $67 per channel per week. [All figures are suggestions; actual allocation may shift within the $400 cap.]

**Primary KPI** — Number of free trial signups. Guardrail metric: Cost per signup must stay ≤ $4 (suggestion; if it rises, we’ll re

---
⚠️ **Unverified figures:** `30%`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** budget_handling __/5 · objective_clarity __/5 · kpi_quality __/5 · timeline_realism __/5

---

### `campaign-clarification` — marketing.campaign-planner (clarification)

**Request:** Plan a campaign

**Reply:**

```
To get started, could you share:  
1) The specific objective you'd like this campaign to achieve?  
2) The time window or duration you're targeting?
```

**Score:** clarification_quality __/5 · no_fabrication __/5

---

### `campaign-grounding-no-invented-budget` — marketing.campaign-planner (grounding)

**Request:** Plan a one month awareness campaign on LinkedIn and email

**Reply:**

```
**Objective** — Build awareness of Acme Cloud among developers and founders, measured by 500+ qualified engagements (LinkedIn post interactions + email opens from target segment) within one month.  
**Audience** — Developers and founders who care most about reducing engineering time spent on infrastructure management.  
**Channel mix** —  
| Channel | Message angle | Format | Frequency |
|---------|--------------|--------|-----------|
| LinkedIn | Acme Cloud’s time-saving capabilities for dev teams | Text post + linked article | 3 posts/week |
| Email | Direct value proposition + trial invitation | HTML newsletter | 2 sends/week |

**Calendar** — 4-week window (Week 1–4):  
| Week | LinkedIn | Email |
|------|----------|-------|
| 1 | Intro post highlighting pain point + comment engagement | Intro newsletter, segment audience by role |
| 2 | Customer story / case study snapshot | Feature-benefit deep-dive, CTA to trial |
| 3 | Product tip carousel / quick win | Trial reminder + limited-time invite link |
| 4 | Social proof (quote + metrics) + clear CTA | Final push, recap of value, next-step CTA |

**Budget** — Planned within profile’s Small band (<$500/mo). Suggested split: LinkedIn $200, Email $300 (total $500). *These figures are my suggestion based on the band; the user has not provided a specific amount.*  
**Primary KPI** — Number of qualified engagements (LinkedIn interactions + email opens/clicks from target segment). Guardrail — Email deliverability rate must not drop below 95%.  
**Risks** — 1) LinkedIn organic reach limited by algorithm; 2) Email list fatigue if content feels repetitive; 3) Messaging misses the “engineering time saved” angle, reducing resonance.

---
⚠️ **Unverified figures:** `95%`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
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

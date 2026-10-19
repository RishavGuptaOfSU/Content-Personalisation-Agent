# Marketing evaluation — FINAL-with-grounding

Generated 20261017T085030Z · 29 cases · 1325s

## Configuration

| setting | value |
|---|---|
| `llm_provider` | ollama |
| `llm_model` | llama3.2:3b |
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

**105/108 assertions passed** across 29 cases.

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
| `campaign-clarification` | campaign-planner | clarification | 2/3 | 1 |
| `campaign-grounding-no-invented-budget` | campaign-planner | grounding | 1/2 | 1 |
| `campaign-out-of-scope-write` | campaign-planner | out_of_scope | 4/4 | 0 |
| `campaign-routing` | — | routing | 2/2 | 0 |

### Failed assertions

- `copy-grounding-no-metrics` — no figures the user did not supply → $100,000
- `campaign-clarification` — contains one of ['?', 'assum'] → matched None
- `campaign-grounding-no-invented-budget` — no figures the user did not supply → 20%, 2%

## Outputs for qualitative scoring

Score each dimension 1–5 using `rubric.md`. The harness deliberately does
not score these.

### `copy-ordinary-linkedin` — marketing.social-copy (ordinary)

**Request:** Write a LinkedIn post about how much cloud spend sits idle

**Reply:**

```
**The Hidden Opportunity in Your Cloud Spend**

Did you know that up to 85% of your cloud spend can be wasted on underutilized resources? This is often referred to as "idle" or "unallocated" spend. It's a common problem, but one that can be easily solved with the right strategy.

By optimizing your cloud usage and identifying areas where resources are being underutilized, you can unlock significant cost savings without sacrificing performance.

---
⚠️ **Unverified figures:** `85%`, `up to 85`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** hook __/5 · audience_fit __/5 · brand_tone __/5 · usefulness __/5 · no_filler __/5

---

### `copy-complex-thread` — marketing.social-copy (complex)

**Request:** Write a 3-post X thread explaining why we rebuilt our cost allocation engine.
Post 1 is the problem, post 2 the rebuild, post 3 the result. Keep each under
280 characters and number them.

**Reply:**

```
1/3 Our current cost allocation engine was flawed, leading to inaccurate billing for developers working on multiple projects simultaneously.

2/3 We rebuilt it from scratch, incorporating machine learning and automation to provide real-time visibility into project costs and optimize resource allocation.

3/3 The result is a more accurate and efficient cost allocation process, allowing us to better support our developer teams and provide a clearer picture of project expenses for founders.
```

**Score:** instruction_following __/5 · hook __/5 · brand_tone __/5

---

### `copy-exact-constraint-hashtags` — marketing.social-copy (ordinary)

**Request:** LinkedIn post about our new pricing. Use at most 2 hashtags.

**Reply:**

```
**Simplified Pricing for Your Cloud Success**

At Acme Cloud, we're committed to empowering your cloud journey. Our new pricing model is designed to help you optimize your spend and achieve more with less.

Say goodbye to hidden fees and surprise charges. With our transparent pricing, you'll know exactly what you're paying for every month.

**Why this works**
Our simplified pricing ensures clarity and confidence in your cloud investments.
By optimizing your spend, you can focus on what matters most – building innovative solutions.
```

**Score:** instruction_following __/5

---

### `copy-no-hashtags-platform` — marketing.social-copy (platform)

**Request:** Write the Facebook post copy for our webinar on Thursday

**Reply:**

```
Here's a conversational opener for your Facebook post:

"Are you tired of overpaying for cloud services? Join us this Thursday at 2 PM EST for our webinar to learn how Acme Cloud can help you optimize your cloud spend and unlock significant cost savings."

**Why this works**
This approach aims to grab the attention of developers and founders who are concerned about their cloud expenses, while also highlighting the benefits of using Acme Cloud.
```

**Score:** platform_fit __/5 · usefulness __/5

---

### `copy-grounding-no-metrics` — marketing.social-copy (grounding)

**Request:** Write a LinkedIn post about how much money we save customers

**Reply:**

```
**Unlocking Savings of Up to $100,000 with Acme Cloud**

By switching to our SaaS solution, developers and founders can significantly reduce their cloud spend. Our platform helps optimize resource allocation, eliminate waste, and streamline infrastructure management.

With Acme Cloud, you can expect substantial cost savings, often exceeding $100,000 annually. Say goodbye to unnecessary expenses and hello to a more predictable, budget-friendly cloud bill.

Discover how our innovative approach can transform your cloud economics. Learn more about our pricing model and start saving today!

---
⚠️ **Unverified figures:** `$100,000`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** no_fabrication __/5 · brand_tone __/5

---

### `copy-memory-applied` — marketing.social-copy (memory)

**Request:** Another LinkedIn post, this time about staging environments left running

**Reply:**

```
**The Hidden Cost of Staging Environments**

As developers, we're always looking for ways to speed up our workflows and improve efficiency. But have you ever stopped to think about the cost of leaving your staging environments running?

Idle staging environments can lead to unnecessary resource usage, increased costs, and even security risks.

At Acme Cloud, we've seen firsthand the impact of neglected staging environments on productivity and bottom line. That's why we're committed to helping you optimize your development workflow.

**Learn how to streamline your staging environment management with our latest guide** [link]
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

**Rendered:** `post-image-1792219296-c8035667.png` 1200×627 (62174 bytes)

**Alt text:** A stylized image of a cloud with gears and cogs, conveying automation and optimization

**Spec from the model:**

```json
{
  "headline": "Simplify Cloud Costs, Amplify Productivity",
  "subline": "Automate and Optimize Your Cloud Spend",
  "badge": "",
  "cta": "Learn More",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Simplify Cloud Costs, Amplify Productivity**
Automate and Optimize Your Cloud Spend

*1200×627 · CTA: Learn More · brand palette*
```

**Score:** headline_relevance __/5 · headline_brevity __/5 · legibility __/5 · brand_fit __/5 · alt_text __/5

---

### `image-complex-detail` — marketing.post-image (complex)

**Request:** A post image announcing our Series A. The headline should lead on what it means
for customers, not on the amount. Add a short supporting line and a call to
action that points at the changelog.

**Rendered:** `post-image-1792219323-a8b2ea30.png` 1200×627 (76360 bytes)

**Alt text:** Acme Cloud logo with a background of subtle grid patterns, symbolizing faster development

**Spec from the model:**

```json
{
  "headline": "New Capabilities for Faster, More Reliable Development",
  "subline": "Our Series A funding brings enhanced performance and support to your projects",
  "badge": "",
  "cta": "View Changelog for Full Details",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**New Capabilities for Faster, More Reliable Development**
Our Series A funding brings enhanced performance and support to your projects

*1200×627 · CTA: View Changelog for Full Details · brand palette*
```

**Score:** headline_relevance __/5 · instruction_following __/5 · legibility __/5

---

### `image-ambiguous` — marketing.post-image (ambiguous)

**Request:** Make us a graphic

**Rendered:** `post-image-1792219347-6d8ab358.png` 1200×627 (52254 bytes)

**Alt text:** A logo of a cloud with a gear inside, symbolizing efficiency

**Spec from the model:**

```json
{
  "headline": "Streamline Cloud Operations with ACME CLOUD",
  "subline": "Cutting-edge SaaS for Developers and Founders",
  "badge": "Cloud Efficiency Expert",
  "cta": "Discover How ACME CLOUD Can Help",
  "palette": "dark",
  "layout": "left",
  "style": "Bold type"
}
```

**Reply:**

```
**Streamline Cloud Operations with ACME CLOUD**
Cutting-edge SaaS for Developers and Founders

*1200×627 · CTA: Discover How ACME CLOUD Can Help · dark palette*
```

**Score:** headline_relevance __/5 · graceful_degradation __/5

---

### `image-brand-colours` — marketing.post-image (brand)

**Request:** Instagram square graphic announcing our new usage-based pricing

**Rendered:** `post-image-1792219367-bbd4cdc4.png` 1200×627 (53839 bytes)

**Alt text:** Acme Cloud usage-based pricing graphic with bold type

**Spec from the model:**

```json
{
  "headline": "Pay Only for What You Use",
  "subline": "No more hidden fees, just fair prices for Acme Cloud",
  "badge": "",
  "cta": "Learn More",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Pay Only for What You Use**
No more hidden fees, just fair prices for Acme Cloud

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

**Rendered:** `ad-creative-1792219423-5cc2485b.png` 1080×1080 (90386 bytes)

**Alt text:** Acme Cloud free trial for engineering teams

**Spec from the model:**

```json
{
  "headline": "Unlock Expertise in Your Team",
  "subline": "Effortless Collaboration, Streamlined Development",
  "badge": "Acme Cloud",
  "cta": "Get Started Today",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Unlock Expertise in Your Team**
Effortless Collaboration, Streamlined Development

*1080×1080 · CTA: Get Started Today · brand palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · objective_alignment __/5 · legibility __/5 · alt_text __/5

---

### `ad-supplied-offer` — marketing.ad-creative (ordinary)

**Request:** Ad image promoting 30% off annual plans until 31 March

**Rendered:** `ad-creative-1792219444-b6a0d02d.png` 1080×1080 (57834 bytes)

**Alt text:** Acme Cloud annual plan promotion

**Spec from the model:**

```json
{
  "headline": "Annual plans now 30% off",
  "subline": "Limited time offer until 31 March",
  "badge": "30% off",
  "cta": "Sign up now",
  "palette": "dark",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Annual plans now 30% off**
Limited time offer until 31 March

*1080×1080 · CTA: Sign up now · dark palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · offer_fidelity __/5

---

### `ad-grounding-no-invented-offer` — marketing.ad-creative (grounding)

**Request:** Make an ad creative that will get engineering managers to sign up

**Rendered:** `ad-creative-1792219468-f68ef75e.png` 1080×1080 (97455 bytes)

**Alt text:** Acme Cloud free trial for engineering managers

**Spec from the model:**

```json
{
  "headline": "Unlock Expertise for Your Team",
  "subline": "Get instant access to Acme Cloud's cutting-edge tools and support",
  "badge": "Acme Cloud",
  "cta": "Sign Up Free Trial",
  "palette": "brand",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Unlock Expertise for Your Team**
Get instant access to Acme Cloud's cutting-edge tools and support

*1080×1080 · CTA: Sign Up Free Trial · brand palette*
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
**Primary keyword** — Cloud Cost Automation
**Search intent** — Informational (explaining benefits and features of cloud cost automation)

**Secondary keywords**
- Cloud Cost Management
- Automated Cloud Pricing
- Cost Optimization Tools
- Scalable Cloud Solutions
- Efficient Cloud Deployment

**Title tag** — 54 characters
"Automate Your Cloud Costs with Acme Cloud's Expert Cost Automation Solution"

**Meta description** — 147 characters
"Discover how Acme Cloud's cloud cost automation tool helps you optimize your cloud expenses and improve resource utilization. Learn more about our scalable solution."

**H2 outline**
1. **Unlock Efficient Cloud Deployment**
	* Introduce the benefits of automated cloud cost management
	* Highlight Acme Cloud's expertise in scalable cloud solutions
2. **Maximize Resource Utilization**
	* Explain how our tool optimizes cloud resource allocation
	* Emphasize the importance of cost-effective cloud deployment
3. **Simplify Cloud Cost Management**
	* Describe the ease of use and intuitive interface of our automation tool
	* Showcase the features that simplify cloud cost management

**Internal link targets**
- Link to a product page for Acme Cloud's cloud cost automation solution
- Link to a blog post or resource on cloud cost optimization best practices
- Link to a case study or success story showcasing the benefits of using Acme Cloud's tool
```

**Score:** intent_reading __/5 · keyword_relevance __/5 · structure __/5 · actionability __/5

---

### `seo-grounding-no-volumes` — marketing.seo-optimizer (grounding)

**Request:** Give me the search volume and keyword difficulty for 'cloud cost tool'

**Reply:**

```
I cannot provide search volume or keyword difficulty data. Can I help you with something else?
```

**Score:** no_fabrication __/5 · honesty_about_limits __/5

---

### `seo-attachment` — marketing.seo-optimizer (attachment)

**Request:** Optimise this page copy for search

**Reply:**

```
**Primary keyword** — informational, Find idle cloud capacity automatically.
**Secondary keywords** — 4 to 6, as a list:
* trusted
* engineering
* cloud capacity
* idle resources
* automated reporting
**Title tag** — under 60 characters, character count shown: "Find Idle Cloud Capacity Automatically with Acme Cloud"
**Meta description** — under 155 characters, character count shown: "Discover how to optimize your cloud usage with our trusted automation solution for engineering teams."
**H2 outline**:
1. Find idle cloud capacity automatically
2. Trusted by engineering teams
3. Automated reporting and connection to your account
4. Optimize your cloud usage
5. Discover the benefits of idle resource management
**Internal link targets**: 
* Link to a page explaining how Acme Cloud connects to accounts
* Link to a page showcasing the features of automated reporting
* Link to a page highlighting the benefits of optimizing cloud usage
```

**Score:** uses_source_material __/5 · keyword_relevance __/5 · structure __/5

---

### `seo-content-type-aware` — marketing.seo-optimizer (profile)

**Request:** SEO for a blog post about rightsizing Kubernetes requests

**Reply:**

```
**Primary keyword** — Rightsizing Kubernetes Requests — Informational
**Secondary keywords** — 
* Kubernetes Request Optimization
* Cloud Cost Management
* Containerized Application Performance
* Scalability and Flexibility in Kubernetes
* Efficient Resource Allocation in Cloud Environments

**Title tag** — "Rightsizing Kubernetes Requests for Optimal Performance" (39/60)
**Meta description** — "Learn how to optimize your Kubernetes requests for better performance, scalability, and cost management. Discover the benefits of rightsizing your containerized applications." (146/155)

**H2 outline** 
1. **Understanding Kubernetes Request Optimization**
2. **Benefits of Rightsizing Kubernetes Requests**
3. **Factors Affecting Kubernetes Request Size**
4. **Best Practices for Optimizing Kubernetes Request Size**
5. **Real-World Examples and Case Studies**

**Internal link targets** 
* Link to relevant documentation on Acme Cloud's website, such as "Kubernetes Request Optimization Guide"
* Link to a blog post on "The Importance of Containerized Application Performance in the Cloud"
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
**Objective**
Acme Cloud to increase lead generation by 20% within the next 2 weeks, targeting developers and founders who have shown interest in cost optimization.

**Audience**
Developers and Founders interested in cost optimization, specifically those who have visited Acme Cloud's blog or engaged with our content on LinkedIn.

**Channel Mix**

| Channel | Message Angle | Format | Frequency |
| --- | --- | --- | --- |
| LinkedIn | Introduction to Cost Automation | Sponsored Post | 1 per day |
| Email | Exclusive Access to Cost Automation Demo | Newsletter | 1 per week |
| Blog / SEO | In-depth Guide to Cost Optimization | Article | 1 per week |

**Calendar**

| Date | Channel | Message Angle | Format |
| --- | --- | --- | --- |
| Mon, Day 1 | LinkedIn | Introduction to Cost Automation | Sponsored Post |
| Tue, Day 2 | Email | Exclusive Access to Cost Automation Demo | Newsletter |
| Wed, Day 3 | Blog / SEO | In-depth Guide to Cost Optimization | Article |
| Thu, Day 4 | LinkedIn | Success Stories from Early Adopters | Sponsored Post |
| Fri, Day 5 | Email | Reminder: Exclusive Access to Cost Automation Demo | Newsletter |

**Budget**
Allocate $300 across the channels:

* LinkedIn (80%): $240
* Email (15%): $45
* Blog / SEO (5%): $15

**Primary KPI**
Increase lead generation by 20% within the next 2 weeks.

**Risks**

1. Low engagement on sponsored posts.
2. Difficulty in getting early adopters to share their success stories.
3. Limited budget for email and blog optimization.

---
⚠️ **Unverified figures:** `20%`, `80%`, `15%`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
```

**Score:** objective_clarity __/5 · channel_choice __/5 · timeline_realism __/5 · kpi_quality __/5 · risks __/5

---

### `campaign-budget-supplied` — marketing.campaign-planner (complex)

**Request:** Plan a 6 week campaign to get 100 free trial signups. Budget is $400 total
across the whole six weeks. We have LinkedIn, email and our blog.

**Reply:**

```
**Objective**
Acquire 100 new free trial signups within the next 6 weeks.

**Audience**
Developers and Founders who are interested in improving their software development processes.

**Channel Mix**

| Channel | Message Angle | Format | Frequency |
| --- | --- | --- | --- |
| LinkedIn | Introduction to Acme Cloud's benefits for developers | Sponsored Post | Weekly (Thursdays) |
| Email | Exclusive offer for early adopters | Newsletter | Bi-Weekly (2nd and 4th Fridays) |
| Blog / SEO | In-depth guides on software development best practices | Article | Monthly (1st Wednesday) |

**Calendar**

| Week | Channel | Message Angle | Format | Frequency |
| --- | --- | --- | --- | --- |
| 1 | LinkedIn | Benefits of using Acme Cloud for agile development | Sponsored Post | Thursday |
| 2 | Email | Early Adopter Exclusive: Get started with a free trial | Newsletter | Friday (2nd) |
| 3 | Blog / SEO | "5 Ways to Improve Your Software Development Process" | Article | Wednesday (1st) |
| 4 | LinkedIn | Success stories from Acme Cloud customers | Sponsored Post | Thursday |
| 5 | Email | Limited Time Offer: Free trial for a limited time | Newsletter | Friday (2nd) |
| 6 | Blog / SEO | "Expert Insights: How to Choose the Right DevOps Tool" | Article | Wednesday (1st) |

**Budget Allocation**

* LinkedIn: $200
* Email: $150
* Blog / SEO: $50

**Primary KPI**
100 free trial signups within the next 6 weeks.

**Risks**
1. Low engagement on LinkedIn posts.
2. High bounce rate for email newsletters.
3. Poor article ranking on the blog.
```

**Score:** budget_handling __/5 · objective_clarity __/5 · kpi_quality __/5 · timeline_realism __/5

---

### `campaign-clarification` — marketing.campaign-planner (clarification)

**Request:** Plan a campaign

**Reply:**

```
**Objective**
Generate 50 leads for Acme Cloud's free trial within the next two weeks.

**Audience**
Developers and Founders of mid-sized to large software companies, who are interested in improving their cloud infrastructure and scalability.

**Channel mix**

| Channel | Message angle | Format | Frequency |
| --- | --- | --- | --- |
| LinkedIn | "Unlock the full potential of your cloud infrastructure" | Sponsored post | Daily |
| Email | Exclusive access to our free trial and expert insights on cloud optimization" | Newsletter | Weekly |
| Blog / SEO | "5 Ways to Optimize Your Cloud Infrastructure for Scalability" | Article | Bi-weekly |

**Calendar**

| Date | Channel | Message angle | Format | Frequency |
| --- | --- | --- | --- | --- |
| 2023-02-06 | LinkedIn | Unlock the full potential of your cloud infrastructure | Sponsored post | Daily |
| 2023-02-08 | Email | Exclusive access to our free trial and expert insights on cloud optimization | Newsletter | Weekly |
| 2023-02-10 | Blog / SEO | 5 Ways to Optimize Your Cloud Infrastructure for Scalability | Article | Bi-weekly |

**Budget**
Allocate $250 across the channels, with $150 on LinkedIn sponsored posts, $50 on email newsletters, and $50 on blog articles.

**Primary KPI**
Lead generation success rate (number of leads generated / total number of campaign impressions).

**Risks**

1. Ad fatigue on LinkedIn due to high competition.
2. Low open rates for email newsletters if the subject line is not optimized.
3. Difficulty in ranking for relevant SEO keywords due to high industry competition.
```

**Score:** clarification_quality __/5 · no_fabrication __/5

---

### `campaign-grounding-no-invented-budget` — marketing.campaign-planner (grounding)

**Request:** Plan a one month awareness campaign on LinkedIn and email

**Reply:**

```
**Objective**
Increase brand awareness among the target audience by 20% in the next three months, measured by LinkedIn engagement metrics.

**Audience**
Developers and Founders of SaaS companies, specifically those interested in cloud-based solutions, with a focus on the age range of 25-45 years old.

**Channel mix**

| Channel | Message angle | Format | Frequency |
| --- | --- | --- | --- |
| LinkedIn | Industry insights and thought leadership pieces | Article, Video | Bi-weekly (2 posts) |
| Email | Newsletters with updates and company news | Newsletter | Monthly (1 post) |

**Calendar**

| Week | Date | Channel | Message angle | Format | Frequency |
| --- | --- | --- | --- | --- | --- |
| 1 | 2023-02-01 | LinkedIn | Introduction to Acme Cloud's cloud-based solutions | Article, Video | Bi-weekly (1 post) |
| 2 | 2023-02-08 | Email | Newsletter with company updates and industry news | Newsletter | Monthly (1 post) |
| 3 | 2023-02-15 | LinkedIn | Thought leadership piece on cloud security best practices | Article, Video | Bi-weekly (1 post) |
| 4 | 2023-02-22 | Email | Newsletter with product updates and company news | Newsletter | Monthly (1 post) |

**Budget**
Allocate $200 across both channels, with a split of $100 each.

**Primary KPI**
Engagement rate on LinkedIn posts (>2% likes and comments)

**Risks**

1. Limited content creation capacity
2. Ad fatigue due to frequent posting
3. Inadequate targeting or messaging

---
⚠️ **Unverified figures:** `20%`, `2%`. You did not supply these, so they are the model's invention — replace them with real numbers or cut them before publishing.
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

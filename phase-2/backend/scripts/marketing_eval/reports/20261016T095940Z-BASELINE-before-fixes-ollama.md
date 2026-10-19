# Marketing evaluation — BASELINE-before-fixes

Generated 20261016T095940Z · 29 cases · 1233s

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

**102/105 assertions passed** across 29 cases.

| case | agent | category | assertions | failures |
|---|---|---|---|---|
| `copy-ordinary-linkedin` | social-copy | ordinary | 6/6 | 0 |
| `copy-complex-thread` | social-copy | complex | 2/2 | 0 |
| `copy-exact-constraint-hashtags` | social-copy | ordinary | 2/2 | 0 |
| `copy-no-hashtags-platform` | social-copy | platform | 2/2 | 0 |
| `copy-grounding-no-metrics` | social-copy | grounding | 3/3 | 0 |
| `copy-memory-applied` | social-copy | memory | 2/2 | 0 |
| `copy-out-of-scope-image` | social-copy | out_of_scope | 4/4 | 0 |
| `copy-ad-copy-routing` | — | routing | 1/2 | 1 |
| `image-ordinary-linkedin` | post-image | ordinary | 9/9 | 0 |
| `image-complex-detail` | post-image | complex | 5/5 | 0 |
| `image-ambiguous` | post-image | ambiguous | 4/4 | 0 |
| `image-brand-colours` | post-image | brand | 5/5 | 0 |
| `image-out-of-scope-caption` | post-image | out_of_scope | 4/4 | 0 |
| `image-out-of-scope-campaign` | post-image | out_of_scope | 4/4 | 0 |
| `ad-ordinary-trial` | ad-creative | ordinary | 7/7 | 0 |
| `ad-supplied-offer` | ad-creative | ordinary | 5/5 | 0 |
| `ad-grounding-no-invented-offer` | ad-creative | grounding | 7/7 | 0 |
| `ad-out-of-scope-copy` | ad-creative | out_of_scope | 4/4 | 0 |
| `seo-ordinary-landing` | seo-optimizer | ordinary | 4/4 | 0 |
| `seo-grounding-no-volumes` | seo-optimizer | grounding | 2/2 | 0 |
| `seo-attachment` | seo-optimizer | attachment | 2/2 | 0 |
| `seo-content-type-aware` | seo-optimizer | profile | 1/1 | 0 |
| `seo-out-of-scope` | seo-optimizer | out_of_scope | 4/4 | 0 |
| `campaign-ordinary-launch` | campaign-planner | ordinary | 4/4 | 0 |
| `campaign-budget-supplied` | campaign-planner | complex | 1/2 | 1 |
| `campaign-clarification` | campaign-planner | clarification | 1/2 | 1 |
| `campaign-grounding-no-invented-budget` | campaign-planner | grounding | 1/1 | 0 |
| `campaign-out-of-scope-write` | campaign-planner | out_of_scope | 4/4 | 0 |
| `campaign-routing` | — | routing | 2/2 | 0 |

### Failed assertions

- `copy-ad-copy-routing` — routes to social-copy → marketing.ad-creative (llm_router, 0.85)
- `campaign-budget-supplied` — contains one of ['400', '$400'] → matched None
- `campaign-clarification` — contains one of ['?', 'assum'] → matched None

## Outputs for qualitative scoring

Score each dimension 1–5 using `rubric.md`. The harness deliberately does
not score these.

### `copy-ordinary-linkedin` — marketing.social-copy (ordinary)

**Request:** Write a LinkedIn post about how much cloud spend sits idle

**Reply:**

```
**Up to 85% of cloud spend goes unused**

Many organizations are still struggling to optimize their cloud usage, leaving vast amounts of resources idle and unrecovered.

**What's the cost?**

According to recent studies, up to 85% of cloud spend can be wasted due to inefficient resource utilization. This translates to significant financial losses for businesses.

**Get ahead with Acme Cloud**

Our expert team helps you identify areas of inefficiency and optimize your cloud usage. With our solutions, you can unlock the full potential of your cloud infrastructure and make the most of every dollar spent.

#cloudoptimization #cloudwaste #acmecloud
```

**Score:** hook __/5 · audience_fit __/5 · brand_tone __/5 · usefulness __/5 · no_filler __/5

---

### `copy-complex-thread` — marketing.social-copy (complex)

**Request:** Write a 3-post X thread explaining why we rebuilt our cost allocation engine.
Post 1 is the problem, post 2 the rebuild, post 3 the result. Keep each under
280 characters and number them.

**Reply:**

```
1/3 Inaccurate cost allocation led to misinformed decision-making, resulting in wasted resources & missed opportunities for growth. Our cloud spend was a blind spot, hindering our ability to optimize.

2/3 We rebuilt our cost allocation engine from scratch, leveraging machine learning & real-time data to provide accurate & actionable insights. This new engine will empower our teams to make informed decisions that drive business value.

3/3 The result? Enhanced visibility into cloud spend, pinpointed inefficiencies, and targeted optimizations. Our developers can now focus on innovation, while our founders can confidently allocate resources to drive growth.
```

**Score:** instruction_following __/5 · hook __/5 · brand_tone __/5

---

### `copy-exact-constraint-hashtags` — marketing.social-copy (ordinary)

**Request:** LinkedIn post about our new pricing. Use at most 2 hashtags.

**Reply:**

```
**Our Pricing Just Got a Whole Lot Smarter**

At Acme Cloud, we're committed to helping you build and grow your business without breaking the bank. Our new pricing model is designed to give you more control over your cloud spend, so you can focus on what matters most - innovation and success.

With our transparent and tiered pricing structure, you'll only pay for what you use, when you need it. Say goodbye to surprise bills and hello to predictable costs.

Try Acme Cloud today and start optimizing your cloud spend.

#AcmeCloud #SaaSPricing
```

**Score:** instruction_following __/5

---

### `copy-no-hashtags-platform` — marketing.social-copy (platform)

**Request:** Write the Facebook post copy for our webinar on Thursday

**Reply:**

```
Here's a conversational opener for your Facebook post:

"Are you still paying for infrastructure you don't even use? Join us this Thursday at 2 PM EST as we explore how to optimize your cloud spend and save time on engineering."

**Why this works**
This opening line is designed to resonate with developers and founders who are likely familiar with the pain of unnecessary cloud costs. By framing it as a common problem, we're more likely to pique their interest and encourage them to join the webinar.
```

**Score:** platform_fit __/5 · usefulness __/5

---

### `copy-grounding-no-metrics` — marketing.social-copy (grounding)

**Request:** Write a LinkedIn post about how much money we save customers

**Reply:**

```
**Unlocking Savings of Up to $100K Per Year with Acme Cloud**

By switching to our cloud-based solution, many of our customers have seen significant reductions in their infrastructure costs. Our platform's automated optimization features and scalable architecture enable businesses like yours to cut through unnecessary expenses and allocate resources more efficiently.

Discover how Acme Cloud can help you unlock substantial savings and drive growth for your business.

#AcmeCloud #CloudSavings #Innovation
```

**Score:** no_fabrication __/5 · brand_tone __/5

---

### `copy-memory-applied` — marketing.social-copy (memory)

**Request:** Another LinkedIn post, this time about staging environments left running

**Reply:**

```
**"The Hidden Cost of Staging Environments: Why Left Running Matters"**

Staging environments are a crucial part of any development workflow, but did you know they can also be a costly mistake? Leaving them running in the background can lead to wasted resources and slow down your team's productivity.

At Acme Cloud, we've seen firsthand how this can happen. That's why we're committed to helping you optimize your environment setup. Our platform is designed to make it easy to manage staging environments and ensure they're always running efficiently.

Take control of your development workflow today and start saving time and resources. Learn more about our solutions for efficient environment management.

#AcmeCloud #DevOps #StagingEnvironments
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

**Rendered:** `post-image-1792143865-b1209372.png` 1200×627 (57634 bytes)

**Alt text:** A stylized illustration of a cloud with automated processes, highlighting cost savings

**Spec from the model:**

```json
{
  "headline": "Simplify Your Cloud Costs",
  "subline": "Automate and Optimize Your Cloud Expenses",
  "badge": "Expert Guidance",
  "cta": "Get Started Now",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Simplify Your Cloud Costs**
Automate and Optimize Your Cloud Expenses

*1200×627 · CTA: Get Started Now · brand palette*
```

**Score:** headline_relevance __/5 · headline_brevity __/5 · legibility __/5 · brand_fit __/5 · alt_text __/5

---

### `image-complex-detail` — marketing.post-image (complex)

**Request:** A post image announcing our Series A. The headline should lead on what it means
for customers, not on the amount. Add a short supporting line and a call to
action that points at the changelog.

**Rendered:** `post-image-1792143892-c2b4e36a.png` 1200×627 (71607 bytes)

**Alt text:** Graphic with the headline: Faster, Smarter Cloud Solutions for Your Next Project

**Spec from the model:**

```json
{
  "headline": "Faster, Smarter Cloud Solutions for Your Next Project",
  "subline": "Upgrade your development experience with our latest features",
  "badge": "Series A Funding",
  "cta": "View Our Latest Changelog",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Faster, Smarter Cloud Solutions for Your Next Project**
Upgrade your development experience with our latest features

*1200×627 · CTA: View Our Latest Changelog · brand palette*
```

**Score:** headline_relevance __/5 · instruction_following __/5 · legibility __/5

---

### `image-ambiguous` — marketing.post-image (ambiguous)

**Request:** Make us a graphic

**Rendered:** `post-image-1792143920-943c91e3.png` 1200×627 (63888 bytes)

**Alt text:** Acme Cloud logo on a clean, modern background

**Spec from the model:**

```json
{
  "headline": "Unlock Scalable Infrastructure with Acme Cloud",
  "subline": "Cutting-edge SaaS for Developers and Founders",
  "badge": "",
  "cta": "Learn More",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Unlock Scalable Infrastructure with Acme Cloud**
Cutting-edge SaaS for Developers and Founders

*1200×627 · CTA: Learn More · brand palette*
```

**Score:** headline_relevance __/5 · graceful_degradation __/5

---

### `image-brand-colours` — marketing.post-image (brand)

**Request:** Instagram square graphic announcing our new usage-based pricing

**Rendered:** `post-image-1792143946-28f3b328.png` 1200×627 (49325 bytes)

**Alt text:** Acme Cloud usage-based pricing graphic

**Spec from the model:**

```json
{
  "headline": "Pay only for what you use",
  "subline": "Simple pricing for a clear future",
  "badge": "",
  "cta": "Learn More",
  "palette": "brand",
  "layout": "centered",
  "style": "Bold type"
}
```

**Reply:**

```
**Pay only for what you use**
Simple pricing for a clear future

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

**Rendered:** `ad-creative-1792144009-d0b511d4.png` 1080×1080 (82498 bytes)

**Alt text:** A screenshot of the Acme Cloud dashboard, with various tools and features displayed

**Spec from the model:**

```json
{
  "headline": "Boost Productivity with Our Cloud-Hosted Dev Tools",
  "subline": "Save up to 80% of your time spent on infrastructure and management",
  "badge": "Acme Cloud",
  "cta": "Get Started Today",
  "palette": "dark",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Boost Productivity with Our Cloud-Hosted Dev Tools**
Save up to 80% of your time spent on infrastructure and management

*1080×1080 · CTA: Get Started Today · dark palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · objective_alignment __/5 · legibility __/5 · alt_text __/5

---

### `ad-supplied-offer` — marketing.ad-creative (ordinary)

**Request:** Ad image promoting 30% off annual plans until 31 March

**Rendered:** `ad-creative-1792144039-ef9613d0.png` 1080×1080 (79001 bytes)

**Alt text:** Acme Cloud annual plan promotion

**Spec from the model:**

```json
{
  "headline": "Unlock 30% off our annual plans",
  "subline": "Save time, boost productivity with Acme Cloud's scalable SaaS solution",
  "badge": "30% off",
  "cta": "Sign up now",
  "palette": "dark",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Unlock 30% off our annual plans**
Save time, boost productivity with Acme Cloud's scalable SaaS solution

*1080×1080 · CTA: Sign up now · dark palette*
```

**Score:** value_proposition __/5 · cta_quality __/5 · offer_fidelity __/5

---

### `ad-grounding-no-invented-offer` — marketing.ad-creative (grounding)

**Request:** Make an ad creative that will get engineering managers to sign up

**Rendered:** `ad-creative-1792144067-63e7870d.png` 1080×1080 (80885 bytes)

**Alt text:** Engineering managers streamline workflows

**Spec from the model:**

```json
{
  "headline": "Optimize Teams, Amplify Productivity",
  "subline": "Streamline workflows and boost development velocity with our cloud-based toolset",
  "badge": "Acme Cloud",
  "cta": "Get Started Today",
  "palette": "dark",
  "layout": "centered",
  "style": ""
}
```

**Reply:**

```
**Optimize Teams, Amplify Productivity**
Streamline workflows and boost development velocity with our cloud-based toolset

*1080×1080 · CTA: Get Started Today · dark palette*
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

- An ad creative for our free trial
- Make a Google Display ad for our analytics tool
- Ad image promoting 30% off annual plans
```

---

### `seo-ordinary-landing` — marketing.seo-optimizer (ordinary)

**Request:** Optimise our cloud cost automation landing page for search

**Reply:**

```
**Primary keyword** — Cloud Cost Automation
**Secondary keywords** — 
- Cost Optimization
- Cloud Management
- SaaS Cost Control
- Automated Budgeting
- Scalable Cloud Solutions

**Title tag** — "Automate Cloud Costs with Acme Cloud - Simplify Your SaaS Expenses"
**Meta description** — "Discover how Acme Cloud's cloud cost automation helps you optimize your SaaS expenses and scale your business with ease. Get started today."
**H2 outline** 
1. **Simplify Cloud Cost Management**
2. **Automate Budgeting for Scalable Growth**
3. **Reduce SaaS Expenses with Acme Cloud**

**Internal link targets** 
- Link to a page explaining the benefits of cost optimization in cloud computing.
- Link to a case study or success story of a developer/ founder who has successfully implemented cloud cost automation with Acme Cloud.

Note: To verify search volume and intent, you can use tools like Google Keyword Planner or Ahrefs, which provide insights into keyword search volume, competition, and content gaps.
```

**Score:** intent_reading __/5 · keyword_relevance __/5 · structure __/5 · actionability __/5

---

### `seo-grounding-no-volumes` — marketing.seo-optimizer (grounding)

**Request:** Give me the search volume and keyword difficulty for 'cloud cost tool'

**Reply:**

```
I don't have live search volume data. However, I can suggest ways to verify the keywords:

* Use tools like Google Keyword Planner or Ahrefs to estimate average monthly searches in India.
* Check the competition using tools like Moz Keyword Explorer or SEMrush.

As for keyword difficulty, it's not a direct metric provided by search engines. However, we can discuss the potential level of competition based on factors like search volume and industry relevance.

For 'cloud cost tool', here's an estimate:

* Average monthly searches in India: 2,900 - 4,300 (using Google Keyword Planner)
* Competition level: High to Very High (due to the popularity of cloud computing and cost optimization among developers and founders)

Please note that these are rough estimates and may vary based on your specific target audience and content strategy.
```

**Score:** no_fabrication __/5 · honesty_about_limits __/5

---

### `seo-attachment` — marketing.seo-optimizer (attachment)

**Request:** Optimise this page copy for search

**Reply:**

```
**Primary keyword** — "cloud cost automation"
**Secondary keywords** — 
* "idle cloud capacity"
* "engineering time saved"
* "cloud resource optimization"
* "account reporting"

**Title tag** — 53 characters ("Cloud Cost Automation - Acme Cloud")
**Meta description** — 147 characters ("Automate idle cloud capacity with Acme Cloud. Trusted by engineering teams for optimized resource utilization.")
 
**H2 outline** — 
1. **Streamline Cloud Costs**
2. **Maximize Idle Capacity**
3. **Trusted by Engineering Teams**

**Internal link targets** — 
* Link to a page about the benefits of cloud cost automation, e.g., "Why Optimize Your Cloud Resources?"
* Link to a page explaining how Acme Cloud's solution works, e.g., "How Our Automation Tool Connects to Your Account"

Note: To verify search volume and keyword difficulty, you can use tools like Google Keyword Planner or Ahrefs. For accurate data, visit the Google Keyword Planner website (https://ads.google.com/home/tools/keyword-planner) and enter your primary keyword ("cloud cost automation").
```

**Score:** uses_source_material __/5 · keyword_relevance __/5 · structure __/5

---

### `seo-content-type-aware` — marketing.seo-optimizer (profile)

**Request:** SEO for a blog post about rightsizing Kubernetes requests

**Reply:**

```
**Primary keyword** — Rightsizing Kubernetes Requests
**Secondary keywords** — Container optimization, Kubernetes efficiency, Cloud cost management, Resource allocation
**Title tag** — "Optimize Your Kubernetes Resources: A Guide to Rightsizing Requests" (44 characters)
**Meta description** — "Discover how to optimize your Kubernetes requests and reduce cloud costs. Learn the best practices for rightsizing container resources." (146 characters)

**H2 outline**
1. **Understanding Kubernetes Request Costs**
2. **Identifying Bottlenecks in Your Application**
3. **Strategies for Rightsizing Kubernetes Requests**
4. **Monitoring and Optimizing Resource Allocation**

**Internal link targets**
Link to a relevant blog post on "Kubernetes Best Practices" or "Cloud Cost Management Strategies".

To verify the keywords, you can use tools like Google Keyword Planner or Ahrefs to research search volume and competition. You can also analyze your existing content to identify relevant keywords and phrases.

Note: Since I don't have live search volume data, I've relied on general keyword research and provided a list of secondary keywords that may be relevant for this topic.
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
**Campaign Objective**
Increase brand awareness and drive lead generation for Acme Cloud's cost automation feature among developers and founders, with a focus on reducing engineering time spent on manual cost tracking.

**Audience**
Developers and Founders who manage cloud infrastructure and are interested in optimizing their costs to improve profitability and scalability.

**Channel Mix**

| Channel | Message Angle | Format | Frequency |
| --- | --- | --- | --- |
| LinkedIn | Expert Insights: Cost Optimization for Developers | Article, Video | 2 posts/week |
| Email | Cost Automation Benefits | Newsletter, Brief | Weekly |
| Blog / SEO | In-Depth Guide to Cost Automation | Comprehensive Guide | 1 post |

**Calendar**

| Date | Channel | Post Type |
| --- | --- | --- |
| Mon, Day 1 | LinkedIn | Article: "5 Ways Cloud Cost Optimization Can Boost Your Business" |
| Tue, Day 2 | Email | Newsletter: "Unlock the Power of Cost Automation for Developers" |
| Wed, Day 3 | Blog / SEO | Comprehensive Guide: "A Step-by-Step Guide to Implementing Cost Automation in Your Cloud Infrastructure" |
| Thu, Day 4 | LinkedIn | Video: "Expert Interview: How Acme Cloud's Cost Automation Feature Can Save You Time and Money" |
| Fri, Day 5 | Email | Brief: "Cost Automation Benefits for Founders: A Quick Overview" |

**Primary KPI**
Reduce time spent on manual cost tracking by at least 30% among target audience within the first 6 weeks of campaign launch.

**Risks**

1. Insufficient engagement with LinkedIn content, leading to decreased brand visibility.
2. Ineffective targeting in email campaigns, resulting in low open rates or unengaged leads.
3. Poorly optimized blog posts for SEO, hindering organic traffic acquisition.
```

**Score:** objective_clarity __/5 · channel_choice __/5 · timeline_realism __/5 · kpi_quality __/5 · risks __/5

---

### `campaign-budget-supplied` — marketing.campaign-planner (complex)

**Request:** Plan a 6 week campaign to get 100 free trial signups. Budget is $400 total
across the whole six weeks. We have LinkedIn, email and our blog.

**Reply:**

```
**Objective**
Acquire 100 free trial signups within the next 6 weeks, with a focus on converting engaged leads into paying customers.

**Audience**
Targeted towards developers and founders who are interested in Acme Cloud's software solutions, with a focus on those who have shown interest in similar products or technologies.

**Channel Mix**

| Channel | Message Angle | Format | Frequency |
| --- | --- | --- | --- |
| LinkedIn | Introduction to Acme Cloud's value proposition and benefits of using the software | Sponsored post | 1x/week |
| Email | Exclusive updates, success stories, and promotions for early adopters | Newsletter | Bi-weekly |
| Blog / SEO | In-depth guides, tutorials, and case studies showcasing Acme Cloud's capabilities | Article | Weekly |

**Calendar**

| Week | Date | LinkedIn | Email | Blog / SEO |
| --- | --- | --- | --- | --- |
| 1 | 2023-02-06 | Launch post: "Unlock Your Team's Full Potential with Acme Cloud" |  | "5 Ways to Boost Productivity with SaaS Tools" |
| 2 | 2023-02-13 | Success story: "Acme Cloud Helps XYZ Corporation Scale Their Operations" |  | "The Benefits of Using a Cloud-Based Project Management Tool" |
| 3 | 2023-02-20 | Exclusive webinar invitation: "Mastering SaaS Productivity with Acme Cloud" |  | "The Future of SaaS: Trends and Predictions" |
| 4 | 2023-02-27 | Promotional email: "Limited Time Offer: Get 10% Off Your First Year's Subscription" |  | "Case Study: How Acme Cloud Helped ABC Startups Achieve Success" |
| 5 | 2023-03-06 | LinkedIn poll: "What's the biggest challenge facing your development team?" |  | "The Importance of Collaboration in Software Development" |
| 6 | 2023-03-13 | Final push email: "Don't Miss Out! Last Chance to Sign Up for Our Free Trial" |  | "Acme Cloud: Your Partner in SaaS Success" |

**Primary KPI**
100 free trial signups within the next 6 weeks, with a guardrail metric of maintaining a conversion rate of at least 2% from engaged leads.

**Risks**

1. Low engagement on LinkedIn posts due to algorithm changes.
2. Difficulty in creating compelling email content that resonates with the target audience.
3. Insufficient blog content to support SEO efforts and drive organic traffic.
```

**Score:** budget_handling __/5 · objective_clarity __/5 · kpi_quality __/5 · timeline_realism __/5

---

### `campaign-clarification` — marketing.campaign-planner (clarification)

**Request:** Plan a campaign

**Reply:**

```
**Objective**
Acme Cloud to generate 50 new leads from developers and founders within the next two weeks, with a conversion rate of at least 20% into free trial sign-ups.

**Audience**
Developers and Founders who are interested in cloud-based software solutions for their businesses.

**Channel Mix**

| Channel | Message Angle | Format | Frequency |
| --- | --- | --- | --- |
| LinkedIn | Establish thought leadership, showcase expertise | Article + Video | 3 posts/week |
| Email | Nurture leads with valuable content and updates | Newsletter | Bi-weekly |
| Blog / SEO | Informative content on cloud computing best practices | Blog Post | Weekly |

**Calendar**

| Date | Channel | Message Angle | Format |
| --- | --- | --- | --- |
| Week 1, Mon-Thu | LinkedIn | Thought leadership | Article + Video |
| Week 1, Fri | Email | Lead nurturing | Newsletter |
| Week 2, Mon-Thu | Blog / SEO | Best practices | Blog Post |
| Week 2, Fri | LinkedIn | Success stories | Article + Video |

**Primary KPI**
Conversion rate of at least 20% into free trial sign-ups.

**Risks**

1. Insufficient engagement on LinkedIn posts.
2. Unresponsive or unengaged email list.
3. Poor blog post visibility due to search engine optimization (SEO) issues.
```

**Score:** clarification_quality __/5 · no_fabrication __/5

---

### `campaign-grounding-no-invented-budget` — marketing.campaign-planner (grounding)

**Request:** Plan a one month awareness campaign on LinkedIn and email

**Reply:**

```
**Objective**
Increase brand awareness among developers and founders by 20% in the next 30 days, measured by LinkedIn post engagement and email open rates.

**Audience**
Developers and Founders who have shown interest in SaaS solutions, with a focus on those working on cloud-based projects.

**Channel Mix**

| Channel | Message Angle | Format | Frequency |
| --- | --- | --- | --- |
| LinkedIn | "The Future of Cloud Computing" | Video (2-3 minutes) | 1 post/week |
| Email | "Acme Cloud: Expert Insights for Cloud-Native Developers" | Newsletter article | Bi-weekly |

**Calendar**

| Week | Date | Channel | Message Angle | Format | Frequency |
| --- | --- | --- | --- | --- | --- |
| 1 | 8-14 Mar | LinkedIn | "The Future of Cloud Computing" | Video (2-3 minutes) | 1 post/week |
| 1 | 13 Mar | Email | "Acme Cloud: Expert Insights for Cloud-Native Developers" | Newsletter article | Bi-weekly |
| 2 | 15-21 Mar | LinkedIn | "Cloud Security: Best Practices" | Infographic | 1 post/week |
| 2 | 20 Mar | Email | "The Benefits of Migrating to the Cloud" | Newsletter article | Bi-weekly |
| 3 | 22-28 Mar | LinkedIn | "Acme Cloud: Success Stories from Cloud-Native Developers" | Video (2-3 minutes) | 1 post/week |
| 3 | 27 Mar | Email | "Expert Q&A: Cloud Computing Trends and Insights" | Newsletter article | Bi-weekly |

**Primary KPI**
Increase LinkedIn post engagement by 30% and email open rates by 25% within the next 30 days.

**Risks**

1. Decreased engagement due to lack of relevance in content.
2. Email deliverability issues affecting newsletter reach.
3. Insufficient budget for ad spend on LinkedIn, limiting campaign reach.
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

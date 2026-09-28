"""Marketing domain.

Note the output kinds: ``post-image`` and ``ad-creative`` return a **rendered
image**, not prose. Asking the post generator for a caption is out of scope — the
Social Caption Writer owns that.
"""

from __future__ import annotations

from app.agents.schema import AgentSpec, DomainSpec, OutputKind, ProfileField

DOMAIN = DomainSpec(
    key="marketing",
    name="Marketing",
    tagline="Post images, captions, SEO and campaigns",
    description=(
        "Content production split by deliverable. The image agents render an actual "
        "graphic you can post; the writing agents produce the copy around it."
    ),
    icon="Megaphone",
    accent="fuchsia",
    setup_headline="Tell us about your brand",
    profile_fields=(
        ProfileField(
            key="brand_name",
            label="Brand / product name",
            kind="text",
            placeholder="e.g. Acme Cloud",
            required=True,
            help_text="Shared by every Marketing agent.",
        ),
        ProfileField(
            key="industry",
            label="Industry",
            kind="select",
            options=(
                "SaaS / Software",
                "E-commerce",
                "Education",
                "Healthcare",
                "Finance",
                "Food & Beverage",
                "Fitness",
                "Travel",
                "Agency / Consulting",
                "Other",
            ),
            default="SaaS / Software",
            required=True,
        ),
        ProfileField(
            key="audience",
            label="Target audience",
            kind="multiselect",
            options=(
                "Developers",
                "Founders",
                "Marketers",
                "Students",
                "Enterprises",
                "Small businesses",
                "Consumers",
                "Recruiters",
            ),
            required=True,
        ),
        ProfileField(
            key="tone",
            label="Brand tone",
            kind="select",
            options=("Professional", "Friendly", "Bold", "Witty", "Corporate", "Inspirational"),
            default="Professional",
            required=True,
        ),
        ProfileField(
            key="brand_colors",
            label="Brand colours",
            kind="text",
            placeholder="e.g. #4F46E5, #0F172A",
            help_text="Hex codes, used when rendering images.",
        ),
        ProfileField(
            key="avoid",
            label="Never use",
            kind="tags",
            placeholder="emojis, clickbait, jargon…",
        ),
    ),
)


POST_IMAGE = AgentSpec(
    slug="post-image",
    domain="marketing",
    name="Social Post Image Generator",
    tagline="Produces a ready-to-post graphic",
    description=(
        "Generates the actual post image — sized for the platform, in your brand "
        "colours, with the headline laid out on it. Returns a graphic, not prose."
    ),
    icon="Image",
    output_kind=OutputKind.IMAGE,
    scope=(
        "Producing a social post image: headline, supporting line and brand styling, "
        "rendered at the right size for the platform."
    ),
    out_of_scope=(
        "writing the caption or body copy for the post (use the Social Caption Writer)",
        "keyword research (use the SEO Optimizer)",
        "multi-week campaign planning (use the Campaign Planner)",
        "anything that is not a post graphic",
    ),
    instructions="""You design a social post GRAPHIC. You do not write captions.

Return ONLY a JSON object describing what to render, nothing else:
{
  "headline": "<max 8 words, the single idea, title case off>",
  "subline": "<max 14 words, optional supporting line, may be empty>",
  "badge": "<max 3 words, optional eyebrow/tag, may be empty>",
  "cta": "<max 4 words, optional call to action, may be empty>",
  "palette": "brand" | "dark" | "light" | "gradient",
  "layout": "centered" | "left" | "split",
  "alt_text": "<one sentence describing the image for accessibility>"
}

Rules:
- The headline carries the whole message. Make it concrete and specific — never
  "Boost Your Business" style filler.
- Respect the brand tone and never use anything in the brand's "never use" list.
- No hashtags, no emoji, no markdown, no explanation outside the JSON.
- Keep text short: long strings will be clipped when rendered.""",
    examples=(
        "Create a LinkedIn post image about AI automation",
        "Instagram graphic announcing our new pricing",
        "A post image for our webinar next Thursday",
    ),
    keywords=(
        "post image", "create a post", "social graphic", "post graphic", "banner",
        "instagram post", "linkedin post image", "generate an image", "make an image",
        "creative", "visual", "graphic", "thumbnail", "cover image", "carousel slide",
    ),
    setup_headline="Set up your post image style",
    profile_fields=(
        ProfileField(
            key="platform",
            label="Default platform",
            kind="select",
            options=("LinkedIn", "Instagram (square)", "Instagram (story)", "X / Twitter", "Facebook"),
            default="LinkedIn",
            required=True,
            help_text="Sets the output dimensions.",
        ),
        ProfileField(
            key="style",
            label="Visual style",
            kind="select",
            options=("Bold type", "Minimal", "Gradient", "Dark mode", "Editorial"),
            default="Bold type",
            required=True,
        ),
        ProfileField(
            key="include_logo_text",
            label="Logo text to stamp on the image",
            kind="text",
            placeholder="e.g. ACME CLOUD",
        ),
    ),
    options={
        "sizes": {
            "LinkedIn": [1200, 627],
            "Instagram (square)": [1080, 1080],
            "Instagram (story)": [1080, 1920],
            "X / Twitter": [1200, 675],
            "Facebook": [1200, 630],
        },
        "default_size": [1200, 627],
    },
)


AD_CREATIVE = AgentSpec(
    slug="ad-creative",
    domain="marketing",
    name="Ad Creative Generator",
    tagline="Renders ad variants to test",
    description=(
        "Produces a paid-ad creative image with a promise, an offer and a call to "
        "action laid out for conversion rather than engagement."
    ),
    icon="BadgePercent",
    output_kind=OutputKind.IMAGE,
    scope="Rendering a paid advertising creative image with offer and CTA.",
    out_of_scope=(
        "organic social post graphics (use the Social Post Image Generator)",
        "ad copy documents or keyword lists (use the SEO Optimizer)",
        "budget and channel planning (use the Campaign Planner)",
    ),
    instructions="""You design a paid AD creative image. Output JSON only:
{
  "headline": "<max 7 words, the promise or outcome>",
  "subline": "<max 12 words, the proof or mechanism>",
  "badge": "<the offer, e.g. '30% off' or 'Free trial', may be empty>",
  "cta": "<max 4 words, imperative, e.g. 'Start free trial'>",
  "palette": "brand" | "dark" | "light" | "gradient",
  "layout": "centered" | "left" | "split",
  "alt_text": "<one sentence description>"
}
Ad rules: lead with the outcome, not the product name. The CTA must be a verb.
Never invent statistics, discounts or claims the user has not given you.""",
    examples=(
        "An ad creative for our free trial",
        "Make a Google Display ad for our analytics tool",
        "Ad image promoting 30% off annual plans",
    ),
    keywords=(
        "ad creative", "advertisement", "ad image", "paid ad", "google ad",
        "display ad", "banner ad", "promo image", "offer creative", "ppc creative",
    ),
    profile_fields=(
        ProfileField(
            key="objective",
            label="Ad objective",
            kind="select",
            options=("Free trial signups", "Purchases", "Lead capture", "App installs", "Webinar signups"),
            default="Free trial signups",
            required=True,
        ),
        ProfileField(
            key="size",
            label="Ad size",
            kind="select",
            options=("Square 1080x1080", "Landscape 1200x628", "Story 1080x1920", "Leaderboard 728x90"),
            default="Landscape 1200x628",
            required=True,
        ),
    ),
    options={
        "sizes": {
            "Square 1080x1080": [1080, 1080],
            "Landscape 1200x628": [1200, 628],
            "Story 1080x1920": [1080, 1920],
            "Leaderboard 728x90": [728, 90],
        },
        "default_size": [1200, 628],
    },
)


SOCIAL_COPY = AgentSpec(
    slug="social-copy",
    domain="marketing",
    name="Social Caption Writer",
    tagline="Captions and post copy",
    description=(
        "Writes the words for a post — hook, body and call to action, formatted for "
        "the platform's conventions."
    ),
    icon="MessageSquareText",
    output_kind=OutputKind.TEXT,
    scope="Writing post captions and social copy.",
    out_of_scope=(
        "generating the post image (use the Social Post Image Generator)",
        "keyword and search optimisation (use the SEO Optimizer)",
        "campaign schedules (use the Campaign Planner)",
    ),
    instructions="""You write social copy and nothing else. Deliver the copy first,
with no preamble.
Platform rules:
- LinkedIn: a hook line that stands alone, single-sentence paragraphs, one CTA,
  at most 5 hashtags at the end.
- X: under 280 characters per post; number them if it is a thread.
- Instagram: caption, line break, then a hashtag block.
- Facebook: conversational opener, short paragraphs, explicit CTA.
After the copy add at most two lines under **Why this works**.
Never fabricate metrics, testimonials or customer names.""",
    examples=(
        "Write a LinkedIn caption about AI automation",
        "Instagram caption for our product launch",
        "A 3-post X thread on why we rebuilt our API",
    ),
    keywords=(
        "caption", "post copy", "write a post", "linkedin post", "tweet", "thread",
        "social copy", "hook", "cta", "hashtags", "instagram caption", "copywriting",
    ),
    profile_fields=(
        ProfileField(
            key="platforms",
            label="Platforms you post on",
            kind="multiselect",
            options=("LinkedIn", "Instagram", "X / Twitter", "Facebook", "Threads", "YouTube"),
            required=True,
        ),
        ProfileField(
            key="length",
            label="Preferred length",
            kind="select",
            options=("Very short (<50 words)", "Short (50-120)", "Medium (120-250)", "Long-form"),
            default="Short (50-120)",
            required=True,
        ),
        ProfileField(
            key="use_hashtags",
            label="Hashtags",
            kind="select",
            options=("Yes, a few", "Yes, many", "No hashtags"),
            default="Yes, a few",
        ),
    ),
)


SEO_OPTIMIZER = AgentSpec(
    slug="seo-optimizer",
    domain="marketing",
    name="SEO Optimizer",
    tagline="Keywords, titles and meta",
    description=(
        "Produces search-oriented assets — primary and secondary keywords, title "
        "tags, meta descriptions and heading outlines."
    ),
    icon="Search",
    output_kind=OutputKind.TEXT,
    scope="Search optimisation: keywords, titles, meta descriptions, on-page structure.",
    out_of_scope=(
        "social captions (use the Social Caption Writer)",
        "images (use the image agents)",
        "paid advertising strategy (use the Campaign Planner)",
    ),
    instructions="""You produce SEO assets in this exact structure:
**Primary keyword** — one, with the search intent named.
**Secondary keywords** — 4 to 6, as a list.
**Title tag** — under 60 characters, character count shown.
**Meta description** — under 155 characters, character count shown.
**H2 outline** — the sections the page needs, in order.
**Internal link targets** — what this page should link to.
Be honest that you do not have live search volume data; describe how to verify
the keywords rather than inventing numbers.""",
    examples=(
        "SEO for a blog post about DevOps automation",
        "Title and meta for our pricing page",
        "Keyword ideas for a beginner Python course",
    ),
    keywords=(
        "seo", "keyword", "keywords", "meta description", "title tag", "serp",
        "search intent", "rank", "backlink", "on page", "search engine",
        "organic traffic", "slug", "h1", "h2",
    ),
    profile_fields=(
        ProfileField(
            key="content_type",
            label="What are you optimising?",
            kind="select",
            options=("Blog post", "Landing page", "Product page", "Documentation", "Category page"),
            default="Blog post",
            required=True,
        ),
        ProfileField(
            key="region",
            label="Target region / language",
            kind="text",
            placeholder="e.g. India, English",
        ),
    ),
)


CAMPAIGN_PLANNER = AgentSpec(
    slug="campaign-planner",
    domain="marketing",
    name="Campaign Planner",
    tagline="Calendars and channel plans",
    description=(
        "Plans a campaign — objective, channels, message per channel, a dated "
        "content calendar and the single metric that defines success."
    ),
    icon="CalendarRange",
    output_kind=OutputKind.TEXT,
    scope="Planning marketing campaigns: objectives, channels, calendar, KPIs.",
    out_of_scope=(
        "writing the individual posts (use the Social Caption Writer)",
        "creating images (use the image agents)",
        "keyword research (use the SEO Optimizer)",
    ),
    instructions="""You plan campaigns. Always output:
**Objective** — one measurable sentence.
**Audience** — who, and the one thing they care about.
**Channel mix** — a table: Channel | Message angle | Format | Frequency.
**Calendar** — a dated table for the campaign window.
**Primary KPI** — the single number that decides success, plus the guardrail
metric that must not get worse.
**Risks** — two or three things most likely to make this fail.
Do not write the actual posts; reference what each slot needs instead.""",
    examples=(
        "Plan a 2 week launch campaign for our app",
        "Campaign to get 100 webinar signups",
        "A monthly content calendar for LinkedIn",
    ),
    keywords=(
        "campaign", "launch plan", "content calendar", "channel mix", "go to market",
        "gtm", "funnel", "kpi", "marketing plan", "schedule posts", "strategy",
        "budget allocation", "awareness", "retargeting",
    ),
    profile_fields=(
        ProfileField(
            key="goal",
            label="Primary goal",
            kind="select",
            options=(
                "Brand awareness",
                "Lead generation",
                "Product launch",
                "Community growth",
                "Retention",
                "Event signups",
            ),
            default="Lead generation",
            required=True,
        ),
        ProfileField(
            key="channels",
            label="Channels available",
            kind="multiselect",
            options=("LinkedIn", "Instagram", "X / Twitter", "Email", "Blog / SEO", "YouTube", "Paid ads", "Partnerships"),
            required=True,
        ),
        ProfileField(
            key="budget",
            label="Budget band",
            kind="select",
            options=("Organic only", "Small (<$500/mo)", "Medium ($500-5k/mo)", "Large ($5k+/mo)"),
            default="Organic only",
        ),
    ),
)


AGENTS = (POST_IMAGE, AD_CREATIVE, SOCIAL_COPY, SEO_OPTIMIZER, CAMPAIGN_PLANNER)

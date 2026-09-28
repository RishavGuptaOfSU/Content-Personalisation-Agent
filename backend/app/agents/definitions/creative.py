"""Creative domain. ``poster-image`` renders a graphic rather than prose."""

from __future__ import annotations

from app.agents.schema import AgentSpec, DomainSpec, OutputKind, ProfileField

DOMAIN = DomainSpec(
    key="creative",
    name="Creative",
    tagline="Stories, scripts, ideas, copy and posters",
    description=(
        "Creative production split by form. Each agent writes one kind of thing — "
        "and the poster agent renders an actual image."
    ),
    icon="Sparkles",
    accent="rose",
    setup_headline="Tell us about your creative work",
    profile_fields=(
        ProfileField(
            key="voice",
            label="Your voice",
            kind="select",
            options=("Minimal", "Descriptive", "Punchy", "Poetic", "Cinematic", "Conversational"),
            default="Descriptive",
            required=True,
            help_text="Shared by every Creative agent.",
        ),
        ProfileField(
            key="tone",
            label="Default tone",
            kind="select",
            options=("Light", "Serious", "Dark", "Humorous", "Inspirational", "Satirical"),
            default="Serious",
            required=True,
        ),
        ProfileField(
            key="influences",
            label="Influences",
            kind="tags",
            placeholder="Ted Chiang, Black Mirror…",
        ),
        ProfileField(
            key="avoid",
            label="Never include",
            kind="tags",
            placeholder="gore, romance, cliffhangers…",
        ),
    ),
)


STORY_WRITER = AgentSpec(
    slug="story-writer",
    domain="creative",
    name="Short Story Writer",
    tagline="Fiction, finished",
    description=(
        "Writes complete short fiction with a real turn and an ending that lands — "
        "delivered as the story itself, not an outline."
    ),
    icon="BookMarked",
    output_kind=OutputKind.TEXT,
    scope="Writing short fiction and prose narrative.",
    out_of_scope=(
        "screenplays and dialogue-formatted scripts (use the Script Writer)",
        "brainstorming lists of premises (use the Idea Generator)",
        "marketing or ad copy (use the Copywriter or the Marketing domain)",
    ),
    instructions="""You write finished short fiction.
Rules:
- Deliver the story. No preamble, no summary of what you are about to write, no
  explanation of the theme afterwards unless asked.
- Open in a concrete moment with a specific sensory detail — never with
  world-building exposition.
- There must be a genuine turn: something the reader re-reads the opening for.
- End on an image or line that lands. Do not explain the ending.
- Concrete nouns over abstraction. Cut adverbs that prop up weak verbs.
- Respect the requested length and genre; honour the profile's voice and tone.
- If the profile lists things to avoid, never include them.
After the story you may add at most three lines under **Craft notes**.""",
    examples=(
        "Write a short sci-fi story about a silent relay tower",
        "A 300 word story about a last phone call",
        "Literary fiction about a locksmith who forgets a door",
    ),
    keywords=(
        "story", "short story", "fiction", "write a story", "narrative", "tale",
        "sci-fi story", "fantasy story", "flash fiction", "prose", "novel excerpt",
        "character study",
    ),
    profile_fields=(
        ProfileField(
            key="genres",
            label="Preferred genres",
            kind="multiselect",
            options=(
                "Sci-fi",
                "Fantasy",
                "Thriller",
                "Literary",
                "Horror",
                "Mystery",
                "Romance",
                "Historical",
                "Comedy",
            ),
            required=True,
        ),
        ProfileField(
            key="length",
            label="Default length",
            kind="select",
            options=("Micro (<150 words)", "Flash (150-500)", "Short (500-1500)", "Long (1500+)"),
            default="Flash (150-500)",
            required=True,
        ),
        ProfileField(
            key="pov",
            label="Point of view",
            kind="select",
            options=("First person", "Third limited", "Third omniscient", "Second person", "Whatever fits"),
            default="Whatever fits",
        ),
    ),
)


SCRIPT_WRITER = AgentSpec(
    slug="script-writer",
    domain="creative",
    name="Script Writer",
    tagline="Screenplay format",
    description=(
        "Writes properly formatted scripts — scene headings, action lines and "
        "dialogue — for film, video or ads."
    ),
    icon="Clapperboard",
    output_kind=OutputKind.TEXT,
    scope="Writing scripts and screenplays in industry format.",
    out_of_scope=(
        "prose fiction (use the Short Story Writer)",
        "social captions (Marketing → Social Caption Writer)",
        "idea lists (use the Idea Generator)",
    ),
    instructions="""You write scripts in correct screenplay format:
- Scene headings in caps: `INT. KITCHEN - NIGHT`
- Action lines in present tense, active voice, no camera directions unless asked.
- CHARACTER names above their dialogue, parentheticals only when the delivery is
  not obvious from context.
- For video/ad scripts, add a timing column or bracketed timestamps, and keep to
  the requested duration — roughly 150 spoken words per minute.
Dialogue rules: people interrupt, evade and understate. No character should
explain the plot to another character who already knows it.
Deliver the script itself with no preamble.""",
    examples=(
        "A 30 second video script for a product teaser",
        "Write a two-character scene in a stalled lift",
        "60 second explainer script for our app",
    ),
    keywords=(
        "script", "screenplay", "scene", "dialogue", "monologue", "voiceover",
        "voice over", "video script", "ad script", "storyboard", "int.", "ext.",
        "explainer script", "podcast script",
    ),
    profile_fields=(
        ProfileField(
            key="formats",
            label="Script formats you write",
            kind="multiselect",
            options=("Short film", "Ad / commercial", "Explainer video", "YouTube", "Podcast", "Stage play"),
            required=True,
        ),
        ProfileField(
            key="default_duration",
            label="Typical duration",
            kind="select",
            options=("15 seconds", "30 seconds", "60 seconds", "2-5 minutes", "Short film (10+ min)"),
            default="30 seconds",
        ),
    ),
)


IDEA_GENERATOR = AgentSpec(
    slug="idea-generator",
    domain="creative",
    name="Idea Generator",
    tagline="Distinct concepts, not variations",
    description=(
        "Brainstorms genuinely different concepts on a theme, each with a one-line "
        "hook — never five rewordings of the same idea."
    ),
    icon="Zap",
    output_kind=OutputKind.TEXT,
    scope="Generating lists of distinct creative concepts, premises or angles.",
    out_of_scope=(
        "writing the finished piece (use the Story or Script Writer)",
        "marketing campaign planning (Marketing → Campaign Planner)",
    ),
    instructions="""You generate distinct ideas. Output a numbered list.
Each entry:
**<Title>** — a one-line hook, then one line on the angle that makes it different.
Hard rule: no two entries may share the same core conflict or mechanism. If two
ideas are variations of each other, replace one. Cover a genuine spread — vary
the scale, the tone and the point of view across the list.
Give exactly the number requested; default to 8 if unspecified.
Do not write any of them out in full — that is another agent's job.""",
    examples=(
        "10 story ideas about memory loss",
        "Brainstorm 8 angles for a developer tool launch",
        "Give me 5 concepts for a short film about routine",
    ),
    keywords=(
        "ideas", "idea", "brainstorm", "concepts", "angles", "premises", "prompts",
        "give me options", "suggestions for", "come up with", "pitches", "themes",
    ),
    profile_fields=(
        ProfileField(
            key="default_count",
            label="Default number of ideas",
            kind="select",
            options=("5", "8", "10", "15", "20"),
            default="8",
        ),
        ProfileField(
            key="risk",
            label="How experimental?",
            kind="select",
            options=("Safe and commercial", "Balanced", "Weird and experimental"),
            default="Balanced",
        ),
    ),
)


COPYWRITER = AgentSpec(
    slug="copywriter",
    domain="creative",
    name="Tagline & Copy Writer",
    tagline="Short-form copy",
    description=(
        "Writes taglines, headlines, product names and microcopy — short lines that "
        "have to work hard."
    ),
    icon="Type",
    output_kind=OutputKind.TEXT,
    scope="Short-form copy: taglines, headlines, names, microcopy, slogans.",
    out_of_scope=(
        "long-form social posts (Marketing → Social Caption Writer)",
        "SEO metadata (Marketing → SEO Optimizer)",
        "stories or scripts (use those agents)",
    ),
    instructions="""You write short-form copy.
Give the strongest option first, then at most three alternatives. Label each with
the angle it takes (e.g. *outcome*, *contrast*, *provocation*, *plain*).
Rules:
- Under 12 words unless asked otherwise.
- No puns that sacrifice clarity. No abstract nouns doing the work of a verb.
- Never use: "revolutionise", "seamless", "unlock", "game-changing", "empower",
  "leverage", "next-generation". They are noise.
- For naming: check the name is pronounceable, spellable from hearing it, and say
  what to verify (domain, trademark) — do not claim availability.
Close with one line on which option you would ship and why.""",
    examples=(
        "Taglines for a personal finance app",
        "Headline for our pricing page",
        "Name ideas for a code review tool",
    ),
    keywords=(
        "tagline", "slogan", "headline", "name for", "naming", "microcopy",
        "button text", "one liner", "strapline", "product name", "catchy",
        "punchline", "value proposition",
    ),
    profile_fields=(
        ProfileField(
            key="register",
            label="Register",
            kind="select",
            options=("Plain and clear", "Clever", "Premium", "Playful", "Technical"),
            default="Plain and clear",
            required=True,
        ),
        ProfileField(
            key="options_count",
            label="How many options?",
            kind="select",
            options=("2", "3", "4", "6"),
            default="3",
        ),
    ),
)


POSTER_IMAGE = AgentSpec(
    slug="poster-image",
    domain="creative",
    name="Poster Image Generator",
    tagline="Renders a poster graphic",
    description=(
        "Produces a poster or title-card image — title, subtitle and credit line "
        "laid out as a graphic. Returns an image, not prose."
    ),
    icon="ImagePlus",
    output_kind=OutputKind.IMAGE,
    scope="Rendering poster and title-card images with typographic layout.",
    out_of_scope=(
        "marketing post graphics (Marketing → Social Post Image Generator)",
        "writing the story or script itself (use those agents)",
        "data charts (Analytics → Chart Builder)",
    ),
    instructions="""You design a POSTER image. Output ONLY JSON:
{
  "headline": "<the title, max 6 words>",
  "subline": "<tagline or subtitle, max 14 words, may be empty>",
  "badge": "<genre, festival laurel text or date, may be empty>",
  "cta": "<credit or release line, may be empty>",
  "palette": "brand" | "dark" | "light" | "gradient",
  "layout": "centered" | "left" | "split",
  "alt_text": "<one sentence description of the poster>"
}
Poster craft: the title dominates; the tagline creates intrigue without
explaining the plot. Match the genre's visual convention through the palette
choice (horror/thriller → dark, comedy → light, sci-fi → gradient).
No markdown, no commentary outside the JSON.""",
    examples=(
        "A poster for my sci-fi short 'The Quiet Hour'",
        "Title card for a horror anthology",
        "Poster for a poetry night on Friday",
    ),
    keywords=(
        "poster", "title card", "cover art", "movie poster", "book cover",
        "flyer", "album art", "event poster", "make a poster",
    ),
    profile_fields=(
        ProfileField(
            key="size",
            label="Poster size",
            kind="select",
            options=("Portrait 1080x1350", "A4 portrait 1240x1754", "Square 1080x1080", "Landscape 1600x900"),
            default="Portrait 1080x1350",
            required=True,
        ),
        ProfileField(
            key="mood",
            label="Visual mood",
            kind="select",
            options=("Dark & moody", "Bright & bold", "Minimal", "Retro", "Gradient"),
            default="Dark & moody",
            required=True,
        ),
    ),
    options={
        "sizes": {
            "Portrait 1080x1350": [1080, 1350],
            "A4 portrait 1240x1754": [1240, 1754],
            "Square 1080x1080": [1080, 1080],
            "Landscape 1600x900": [1600, 900],
        },
        "default_size": [1080, 1350],
    },
)


AGENTS = (STORY_WRITER, SCRIPT_WRITER, IDEA_GENERATOR, COPYWRITER, POSTER_IMAGE)

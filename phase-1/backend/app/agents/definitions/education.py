"""Education domain: one agent per study need."""

from __future__ import annotations

from app.agents.schema import AgentSpec, DomainSpec, OutputKind, ProfileField

DOMAIN = DomainSpec(
    key="education",
    name="Education",
    tagline="Subject tutors, homework, exams and quizzes",
    description=(
        "Curriculum-aligned study help. Pick the tutor for the exact class and "
        "subject you are studying, or a task agent for homework, revision or quizzes."
    ),
    icon="GraduationCap",
    accent="emerald",
    setup_headline="Tell us about your studies",
    profile_fields=(
        ProfileField(
            key="board",
            label="Board / curriculum",
            kind="select",
            options=("CBSE", "ICSE", "State Board", "IB", "IGCSE", "University", "Other"),
            default="CBSE",
            required=True,
            help_text="Shared by every Education agent.",
        ),
        ProfileField(
            key="language",
            label="Explanation language",
            kind="select",
            options=("English", "Hindi", "Hinglish", "Tamil", "Telugu", "Bengali", "Marathi"),
            default="English",
        ),
        ProfileField(
            key="learning_style",
            label="How do you learn best?",
            kind="multiselect",
            options=(
                "Step-by-step working",
                "Real-world examples",
                "Diagrams / visual",
                "Practice questions",
                "Analogies",
                "Summary first",
            ),
        ),
        ProfileField(
            key="exam_target",
            label="What are you preparing for?",
            kind="text",
            placeholder="e.g. Class 10 board exam, March 2027",
        ),
    ),
)


_MATHS_STEPS = """
How you answer:
- Always show the full working, numbered line by line. Never just the final answer.
- State the formula or theorem being used before applying it.
- Keep units and signs visible at every step.
- Put the final answer on its own line as **Answer: …**
- End with one short "common mistake" note for this type of problem.
""".strip()


CLASS10_MATHS = AgentSpec(
    slug="class10-maths",
    domain="education",
    name="Class 10 Maths Tutor",
    tagline="Class 10 · Mathematics",
    description=(
        "Teaches and solves Class 10 mathematics only — real numbers, polynomials, "
        "linear equations, trigonometry, circles, surface areas, statistics and probability."
    ),
    icon="Sigma",
    output_kind=OutputKind.TEXT,
    scope="Class 10 mathematics topics and problems, following the Class 10 syllabus.",
    out_of_scope=(
        "physics, chemistry or biology questions",
        "mathematics clearly beyond Class 10 (calculus, matrices, complex numbers)",
        "programming or software questions",
        "essay writing or general knowledge",
    ),
    instructions=f"""You are a Class 10 mathematics tutor.
Only Class 10 maths. Keep vocabulary and methods within the Class 10 syllabus —
never introduce calculus, matrices or other higher-class tools.

{_MATHS_STEPS}
Use the board named in the domain profile for terminology and marking style.""",
    examples=(
        "Solve: find the roots of x² - 5x + 6 = 0",
        "Explain the section formula with an example",
        "Prove that the tangent at any point of a circle is perpendicular to the radius",
    ),
    keywords=(
        "class 10 maths", "class 10 math", "quadratic", "polynomial", "trigonometry",
        "arithmetic progression", "section formula", "circle theorem", "surface area",
        "mensuration", "probability", "statistics", "real numbers", "linear equations",
        "similar triangles", "pythagoras", "roots", "discriminant",
    ),
    profile_fields=(
        ProfileField(
            key="weak_chapters",
            label="Chapters you find hard",
            kind="multiselect",
            options=(
                "Real Numbers",
                "Polynomials",
                "Linear Equations",
                "Quadratic Equations",
                "Arithmetic Progressions",
                "Triangles",
                "Coordinate Geometry",
                "Trigonometry",
                "Circles",
                "Surface Areas & Volumes",
                "Statistics",
                "Probability",
            ),
            help_text="The tutor slows down and adds extra practice on these.",
        ),
        ProfileField(
            key="detail_level",
            label="Working detail",
            kind="select",
            options=("Every single step", "Normal steps", "Only the key steps"),
            default="Every single step",
        ),
    ),
)


CLASS10_SCIENCE = AgentSpec(
    slug="class10-science",
    domain="education",
    name="Class 10 Science Tutor",
    tagline="Class 10 · Physics, Chemistry, Biology",
    description=(
        "Teaches Class 10 science only — light, electricity, chemical reactions, "
        "acids and bases, carbon compounds, life processes, heredity and environment."
    ),
    icon="FlaskConical",
    output_kind=OutputKind.TEXT,
    scope="Class 10 science topics across physics, chemistry and biology.",
    out_of_scope=(
        "mathematics problem solving (use the Class 10 Maths Tutor)",
        "science beyond Class 10 (organic mechanisms, calculus-based physics)",
        "programming, career or marketing questions",
    ),
    instructions="""You are a Class 10 science tutor.
Only Class 10 science. Structure every explanation as:
1. **Definition** — one precise sentence.
2. **How it works** — the mechanism, in the order the syllabus presents it.
3. **Diagram to draw** — describe what to label (examiners award label marks).
4. **Exam point** — the specific thing that earns the mark.
For numericals, show the formula, substitution and units line by line.
For chemistry, always give balanced equations with state symbols.""",
    examples=(
        "Explain the refraction of light through a glass slab",
        "Write the balanced equation for the reaction of zinc with HCl",
        "Explain the human digestive system with the parts to label",
    ),
    keywords=(
        "class 10 science", "photosynthesis", "refraction", "reflection", "lens",
        "electricity", "ohm's law", "chemical reaction", "acid", "base", "salt",
        "carbon compound", "life process", "heredity", "evolution", "respiration",
        "digestion", "periodic table", "metals and non-metals", "magnetic effect",
    ),
    profile_fields=(
        ProfileField(
            key="focus_subject",
            label="Which part needs most help?",
            kind="select",
            options=("Physics", "Chemistry", "Biology", "All equally"),
            default="All equally",
        ),
        ProfileField(
            key="weak_chapters",
            label="Chapters you find hard",
            kind="tags",
            placeholder="Light, Electricity, Life Processes…",
        ),
    ),
)


CLASS12_PHYSICS = AgentSpec(
    slug="class12-physics",
    domain="education",
    name="Class 12 Physics Tutor",
    tagline="Class 12 · Physics",
    description=(
        "Teaches Class 12 physics only — electrostatics, current electricity, magnetism, "
        "optics, dual nature, atoms and nuclei, semiconductors."
    ),
    icon="Atom",
    output_kind=OutputKind.TEXT,
    scope="Class 12 physics theory and numerical problems.",
    out_of_scope=(
        "Class 10 or lower physics (use the Class 10 Science Tutor)",
        "chemistry or biology",
        "engineering or programming questions",
    ),
    instructions="""You are a Class 12 physics tutor.
Only Class 12 physics. For derivations, state the assumptions, derive line by
line, and box the final expression. For numericals: given → formula →
substitution with units → result → a sanity check on the magnitude.
Flag the two or three derivations most likely to appear in the exam when a
chapter is discussed.""",
    examples=(
        "Derive the expression for the electric field due to a dipole on its axis",
        "Solve: find the equivalent resistance of this network",
        "Explain the working of a p-n junction diode",
    ),
    keywords=(
        "class 12 physics", "electrostatics", "gauss", "capacitor", "dipole",
        "drift velocity", "kirchhoff", "biot savart", "ampere", "faraday",
        "alternating current", "electromagnetic wave", "interference",
        "diffraction", "photoelectric", "de broglie", "bohr model", "semiconductor",
        "transistor", "nuclei", "radioactivity",
    ),
    profile_fields=(
        ProfileField(
            key="weak_chapters",
            label="Chapters you find hard",
            kind="tags",
            placeholder="Electrostatics, Ray Optics…",
        ),
        ProfileField(
            key="derivations",
            label="Include full derivations?",
            kind="select",
            options=("Always", "Only when asked", "Never — results only"),
            default="Always",
        ),
    ),
)


HOMEWORK_SOLVER = AgentSpec(
    slug="homework-solver",
    domain="education",
    name="Homework Solver",
    tagline="Worked solutions, any school subject",
    description=(
        "Solves a specific homework question you paste in, showing the full working "
        "so you can follow the method — not just the answer."
    ),
    icon="PencilRuler",
    output_kind=OutputKind.TEXT,
    scope="Solving a specific homework or textbook question that the user supplies.",
    out_of_scope=(
        "teaching a whole chapter from scratch (use the subject tutor)",
        "writing exams or quizzes (use the Quiz Generator)",
        "non-academic requests",
    ),
    instructions="""You solve one homework question at a time.
Format every answer exactly as:
**Given** — what the question provides.
**To find** — what is asked.
**Solution** — numbered steps with the reasoning for each.
**Answer** — the final result on its own line.
**Check** — one line verifying the result is plausible.
If the question is ambiguous or incomplete, say precisely what is missing and
solve the most likely interpretation anyway.""",
    examples=(
        "A train travels 240 km in 3 hours. Find its average speed in m/s.",
        "Balance: Fe + O2 → Fe2O3",
        "Find the mean of 12, 15, 18, 21, 24",
    ),
    keywords=(
        "homework", "solve this", "solve the following", "my assignment", "question 5",
        "exercise", "sum", "textbook question", "find the value", "calculate",
    ),
    profile_fields=(
        ProfileField(
            key="subjects",
            label="Subjects you get homework in",
            kind="multiselect",
            options=(
                "Mathematics",
                "Physics",
                "Chemistry",
                "Biology",
                "English",
                "Social Science",
                "Computer Science",
                "Accountancy",
                "Economics",
            ),
            required=True,
        ),
        ProfileField(
            key="class_level",
            label="Your class",
            kind="select",
            options=(
                "Class 6", "Class 7", "Class 8", "Class 9", "Class 10",
                "Class 11", "Class 12", "Undergraduate",
            ),
            required=True,
        ),
    ),
)


EXAM_PLANNER = AgentSpec(
    slug="exam-planner",
    domain="education",
    name="Exam Revision Planner",
    tagline="Timetables and revision strategy",
    description=(
        "Builds a dated revision timetable for an exam, prioritised by chapter "
        "weightage and the topics you are weakest in."
    ),
    icon="CalendarClock",
    output_kind=OutputKind.TEXT,
    scope="Planning revision schedules and exam strategy.",
    out_of_scope=(
        "teaching or explaining subject content (use the subject tutors)",
        "solving individual problems (use the Homework Solver)",
    ),
    instructions="""You build revision plans, you do not teach content.
Always output a table with columns: Date | Chapter/Topic | Hours | Why this
priority. Order by expected weightage and the user's weak areas. Then add:
- **Weekly rhythm** — study/revise/test split.
- **Last 3 days** — exactly what to do, and what to stop doing.
- **Do not bother with** — the low-yield topics to skip if time is short.
Use the exam date from the profile to make the plan dated and concrete.""",
    examples=(
        "Make a 6 week revision plan for my Class 10 boards",
        "I have 10 days left for physics — what do I do?",
        "Plan my weekend study for maths and science",
    ),
    keywords=(
        "revision plan", "timetable", "study plan", "how many days", "prepare for exam",
        "weightage", "syllabus coverage", "time table", "schedule", "last minute",
    ),
    profile_fields=(
        ProfileField(
            key="exam_date",
            label="Exam date (or how long you have)",
            kind="text",
            placeholder="e.g. 15 March 2027, or 6 weeks",
            required=True,
        ),
        ProfileField(
            key="subjects",
            label="Subjects in this exam",
            kind="tags",
            placeholder="Maths, Science, English…",
            required=True,
        ),
        ProfileField(
            key="hours_per_day",
            label="Study hours available per day",
            kind="select",
            options=("1-2", "2-4", "4-6", "6-8", "8+"),
            default="2-4",
        ),
        ProfileField(
            key="weak_areas",
            label="Weakest areas",
            kind="tags",
            placeholder="Trigonometry, Organic chemistry…",
        ),
    ),
)


QUIZ_GENERATOR = AgentSpec(
    slug="quiz-generator",
    domain="education",
    name="Quiz Generator",
    tagline="Practice papers with answer keys",
    description=(
        "Generates practice questions on a topic you name, with a marking scheme "
        "and a separate answer key."
    ),
    icon="ListChecks",
    output_kind=OutputKind.TEXT,
    scope="Generating quizzes, practice questions and mock papers with answer keys.",
    out_of_scope=(
        "explaining concepts in depth (use the subject tutor)",
        "solving the user's own homework (use the Homework Solver)",
    ),
    instructions="""You generate practice questions only.
Structure:
### Questions
Numbered, each with its mark value in brackets. Mix the difficulty unless told
otherwise. For MCQs give four plausible options.

### Answer Key
The answer for each number, plus a one-line reason. Never mix answers into the
questions section — the user needs to attempt them first.
Respect the requested count exactly. Follow the board's question style.""",
    examples=(
        "Give me 10 MCQs on trigonometry with answers",
        "Make a 20 mark practice paper on Light",
        "5 short answer questions on the French Revolution",
    ),
    keywords=(
        "quiz", "mcq", "practice questions", "test me", "mock paper", "worksheet",
        "question paper", "sample questions", "multiple choice", "objective questions",
    ),
    profile_fields=(
        ProfileField(
            key="default_count",
            label="Default number of questions",
            kind="select",
            options=("5", "10", "15", "20", "25"),
            default="10",
        ),
        ProfileField(
            key="question_types",
            label="Preferred question types",
            kind="multiselect",
            options=(
                "MCQ",
                "One word",
                "Short answer (2-3 marks)",
                "Long answer (5 marks)",
                "Numerical",
                "Assertion-Reason",
                "Case study",
            ),
            default=["MCQ", "Short answer (2-3 marks)"],
        ),
        ProfileField(
            key="difficulty",
            label="Difficulty",
            kind="select",
            options=("Easy", "Board level", "Challenging", "Mixed"),
            default="Board level",
        ),
    ),
)


AGENTS = (
    CLASS10_MATHS,
    CLASS10_SCIENCE,
    CLASS12_PHYSICS,
    HOMEWORK_SOLVER,
    EXAM_PLANNER,
    QUIZ_GENERATOR,
)

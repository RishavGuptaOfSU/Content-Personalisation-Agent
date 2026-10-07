# Content Personalisation Agent — Fortnightly Project Report

**Report Date:** September 27, 2026
**Project Name:** Content Personalisation Agent
**Report Type:** Fortnightly Progress & Technical Overview

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [What Problem Does It Solve?](#2-what-problem-does-it-solve)
3. [How It Works — The Big Picture](#3-how-it-works--the-big-picture)
4. [The 7 Domains and 34 Agents](#4-the-7-domains-and-34-agents)
5. [Key Features & Functionality](#5-key-features--functionality)
6. [Tech Stack](#6-tech-stack)
7. [System Architecture](#7-system-architecture)
8. [The Personalization Engine](#8-the-personalization-engine)
9. [AI & Model Support](#9-ai--model-support)
10. [Security](#10-security)
11. [Project Structure](#11-project-structure)
12. [Current Status & Verified Results](#12-current-status--verified-results)

---

## 1. Project Overview

The **Content Personalisation Agent** is a full-stack, AI-powered web application that provides **deeply personalised content and assistance** across 7 different subject areas (called "domains"). Instead of one general chatbot that does everything, the system uses **34 narrow, specialised AI agents** — each designed to do exactly one job extremely well.

Think of it like having a team of 34 dedicated experts, where each expert knows only their own job — and if you ask the wrong expert, they politely direct you to the right one.

> **Core Idea:** Personalisation is *per need*, not *per subject*. If you're a Class 10 student studying maths, you get a *Class 10 Maths Tutor* — not a generic education assistant.

---

## 2. What Problem Does It Solve?

Most AI chatbots are "one-size-fits-all" — they try to do everything but personalise nothing. This project solves three key problems:

| Problem | How This Project Solves It |
|---|---|
| **Generic responses** | Every reply is customised using 3 levels of user profile (global → domain → agent-specific) |
| **No memory of preferences** | A dedicated memory system remembers your preferences, corrections, and recurring needs across sessions |
| **Scope creep in AI** | Each agent has a strict "scope" — if you ask it something outside its job, it refuses and redirects you to the correct agent instantly |

---

## 3. How It Works — The Big Picture

Here is the simplified flow of what happens when a user sends a message:

```
You log in
   ↓
You browse 7 Domains (e.g., Education, Marketing, Technical)
   ↓
You pick a Domain → See the Agents inside it
   ↓
You select an Agent (e.g., Class 10 Maths Tutor)
   ↓
First time? → Quick 2-step setup to personalise the agent for you
   ↓
You type your message
   ↓
┌─────────────────────────────────────────────────────┐
│              BEHIND THE SCENES                      │
│                                                     │
│  1. Router  → Picks the right agent (if not chosen) │
│  2. Scope Guard → Checks if request fits the agent  │
│  3. Personalisation Engine → Loads your 3 profiles  │
│  4. Memory Retrieval → Finds relevant past memories │
│  5. AI Agent → Generates the response               │
│  6. Output → Text / Image / Chart                   │
│  7. Feedback → You rate it → System learns          │
└─────────────────────────────────────────────────────┘
   ↓
You get a personalised, accurate answer
```

---

## 4. The 7 Domains and 34 Agents

The system is organised into **7 domains**, each containing multiple **narrow agents**:

### 🎓 Education Domain (6 agents)
Shared profile: board, language, learning style, exam target

| Agent | What It Does |
|---|---|
| Class 10 Maths Tutor | Teaches Class 10 maths concepts, solves problems |
| Class 10 Science Tutor | Science concepts for Class 10 |
| Class 12 Physics Tutor | Physics for Class 12 |
| Homework Solver | Solves homework problems step by step |
| Exam Planner | Creates study plans and revision schedules |
| Quiz Generator | Generates practice quizzes |

### 💻 Technical Domain (6 agents)
Shared profile: experience level, explanation style, project context

| Agent | What It Does |
|---|---|
| Python Engineer | Python programming help, concepts, debugging |
| React Developer | React.js front-end development |
| SQL Expert | Database queries and optimisation |
| DSA Coach | Data Structures and Algorithms |
| Debugger | Finds and explains bugs in code |
| Code Reviewer | Reviews code quality and best practices |

### 💼 Career Domain (4 agents)
Shared profile: current role, target roles, years of experience, skills, location

| Agent | What It Does |
|---|---|
| Resume Writer | Writes and improves resumes |
| Interview Coach | Prepares for job interviews |
| Job Search Advisor | Job search strategies and tips |
| Skill Roadmap Planner | Suggests learning paths for career goals |

### 📣 Marketing Domain (5 agents)
Shared profile: brand name, industry, audience, tone, brand colours

| Agent | What It Does | Output |
|---|---|---|
| Social Post Image Generator 🖼 | Creates branded social media images | **PNG Image** |
| Ad Creative Generator 🖼 | Creates advertisement visuals | **PNG Image** |
| Social Caption Writer | Writes social media captions | Text |
| SEO Optimiser | Optimises content for search engines | Text |
| Campaign Planner | Plans marketing campaigns | Text |

### 📊 Analytics Domain (4 agents)
Shared profile: experience level, tools used, data context

| Agent | What It Does | Output |
|---|---|---|
| Chart Builder 📊 | Builds charts from real user data | **Chart PNG** |
| EDA Planner | Plans exploratory data analysis | Text |
| SQL Analytics Expert | Analytical SQL queries | Text |
| Insight Writer | Turns data into written insights | Text |

### 🔬 Research Domain (4 agents)
Shared profile: field, depth of interest, background

| Agent | What It Does |
|---|---|
| Concept Explainer | Explains complex concepts simply |
| Summariser | Summarises documents or topics |
| Literature Brief | Gives a research literature overview |
| Source Finder | Suggests research sources |

### 🎨 Creative Domain (5 agents)
Shared profile: voice, tone, influences, things to avoid

| Agent | What It Does | Output |
|---|---|---|
| Story Writer | Writes creative stories | Text |
| Script Writer | Writes scripts for video/films | Text |
| Idea Generator | Brainstorms creative ideas | Text |
| Copywriter | Writes persuasive marketing copy | Text |
| Poster Image Generator 🖼 | Creates artistic poster images | **PNG Image** |

> **🖼 = Returns an actual image file (PNG)**
> **📊 = Returns a rendered chart image**
> **Everything else = Returns text**

---

## 5. Key Features & Functionality

### 5.1 Three-Level Personalisation

Every AI response is personalised using **three layers of your profile**:

1. **Global Profile** — Basic info about you (name, occupation, interests, preferred response style, skill level)
2. **Domain Profile** — Info shared across all agents in a domain (e.g., your brand name is used by all Marketing agents)
3. **Agent Profile** — Specific info for that one agent (e.g., which platform you post on for the Social Post Image Generator)

This means you **set up your brand name once** for Marketing, and every marketing agent automatically knows it — you don't repeat yourself.

### 5.2 Smart Memory System

The system remembers things you teach it:

- **Durable memories** — Preferences like "keep answers concise" are stored permanently
- **Reinforcement** — If you repeat the same correction twice, the system promotes it to a permanent profile update
- **Three memory scopes** — A memory can apply to: only one specific agent, all agents in a domain, or all agents globally
- **Semantic search** — Memories are retrieved based on meaning, not just keywords (powered by vector embeddings)

**Example:** If you tell the Maths Tutor "keep explanations short", that preference stays in memory for all future maths queries — but it does NOT leak into your Python or Marketing sessions.

### 5.3 Scope Guard — Agents Stay in Their Lane

Each agent knows exactly what it does and **refuses to do anything else**:

```
You → Class 10 Maths Tutor: "Explain Python decorators"
Agent: "That is outside what I do. I am the Class 10 Maths Tutor.
        Python Engineer handles this. [Switch to Python Engineer →]"
```

This happens **instantly with zero AI model cost** — a deterministic rule-based guard checks the request and redirects you before even calling the AI.

### 5.4 Smart Router Agent

If you don't explicitly pick an agent, the **Router Agent** picks the best one for you automatically using:

1. Keyword/phrase scoring across all 34 agents
2. If still unclear → Two-step AI classification (first picks domain, then picks agent inside that domain)
3. Falls back to the most relevant default

### 5.5 Image Generation (No GPU Required!)

Four agents produce actual **image files** instead of text. The clever part: the AI doesn't draw the image — it generates a structured specification (JSON), and a local renderer creates the PNG. This means:

- Works on any machine (no GPU needed)
- Brand colours from your profile are automatically applied
- Results are consistent and predictable
- Optional: Can be switched to use OpenAI's `gpt-image-1` for photographic quality

### 5.6 Chart Generation (Real Data Only)

The Chart Builder agent creates charts from **your actual numbers**. It refuses to invent data — if you don't provide numbers, it asks for them rather than making them up.

### 5.7 Real-Time Streaming

Because local AI models can be slow, responses **stream token by token** — you see text appearing as it's generated, rather than waiting for the whole response. A "Stop" button and elapsed timer are also shown.

### 5.8 Feedback Loop

You can give a thumbs up or down (and optionally explain why) after any response:

- A one-off correction → Stored as a memory immediately
- The same correction twice → Permanently updates your profile
- A thumbs-down alone → Recorded but no automatic changes (avoids false positives)

### 5.9 Two-Step Agent Setup

The first time you use an agent, a guided setup collects the info it needs:

- **Step 1:** Domain-level questions (shared across all agents in the domain)
- **Step 2:** Agent-specific questions (unique to that one job)

Once set up, the agent is fully personalised for all future sessions.

---

## 6. Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| **React 18** | UI framework |
| **Vite** | Fast build tool and dev server |
| **Tailwind CSS** | Styling |
| **React Router** | Page navigation |
| **Axios** | API communication |
| **Lucide Icons** | Icons |
| **react-markdown** | Renders AI responses with formatting |

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.12+** | Programming language |
| **FastAPI** | Web API framework |
| **Pydantic v2** | Data validation |
| **SQLAlchemy 2** | Database ORM |
| **Alembic** | Database migrations |
| **LangGraph** | AI agent orchestration (multi-step pipeline) |
| **PyJWT + bcrypt** | Authentication and security |

### Database
| Technology | Purpose |
|---|---|
| **PostgreSQL 16** | Main database (recommended) |
| **pgvector** | Extension for storing and searching AI embeddings (vector similarity search) |
| **SQLite** | Offline/dev fallback (no setup needed) |

### AI / Models
| Technology | Purpose |
|---|---|
| **Ollama** | Run AI models locally (free, no API key) |
| **OpenAI-compatible API** | Connect to OpenAI, Groq, Together AI, Mistral, etc. |
| **AWS Bedrock** | Enterprise cloud AI (Claude, Titan) |
| **Mock Provider** | Local dev mode — runs entire stack with no AI model |

### Media Generation
| Technology | Purpose |
|---|---|
| **Pillow (PIL)** | Renders branded image cards (social posts, ads, posters) |
| **Matplotlib** | Renders data charts |
| **gpt-image-1** (optional) | Photographic image generation via OpenAI |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Docker + Docker Compose** | Containerised deployment |
| **pgvector Docker image** | PostgreSQL with vector extension pre-installed |

---

## 7. System Architecture

### Backend Architecture

```
backend/app/
├── agents/
│   ├── definitions/     ← All 34 agents defined as data (not as separate classes)
│   ├── router.py        ← Picks the right agent for each request
│   ├── scope.py         ← Scope guard — enforces agent boundaries
│   ├── runtime.py       ← TextAgent, ImageAgent, ChartAgent (3 generic runners)
│   └── graph.py         ← 10-step LangGraph pipeline
│
├── llm/                 ← AI model providers (Ollama, OpenAI, Bedrock, Mock)
├── memory/              ← Memory extraction, storage, and retrieval
├── media/               ← Image and chart rendering
├── models/              ← Database table definitions
├── services/            ← Personalization engine, profiles, feedback
├── api/                 ← REST API routes
└── main.py              ← Application entry point
```

### The LangGraph Pipeline (10 Steps)

Every chat message goes through this exact pipeline:

```
Step 1:  load_user           → Load who is sending the message
Step 2:  router              → Decide which agent handles this
Step 3:  scope_guard         → Check if the request fits the agent
Step 4:  load_global_profile → Load your general preferences
Step 5:  load_domain_profile → Load domain-specific settings
Step 6:  load_agent_profile  → Load agent-specific settings
Step 7:  retrieve_memory     → Find relevant memories from past sessions
Step 8:  build_context       → Assemble everything into a prompt
Step 9:  generate_response   → Call the AI model (or scope guard, or image renderer)
Step 10: store_message       → Save the conversation and any new memories
```

### Database Schema

```
users ──1:1── global_profiles
  ├──1:N── domain_profiles     (one per domain, shared by all agents in it)
  ├──1:N── agent_profiles      (one per agent, specific to that job)
  ├──1:N── conversations ──1:N── messages ──1:N── feedback
  ├──1:N── memories            (with vector embeddings for semantic search)
  └──1:N── feedback
```

### Frontend Architecture

```
frontend/src/
├── pages/         ← Auth, Dashboard, Domain, AgentSetup, Chat, Profile, Settings
├── components/    ← Sidebar, ChatMessage, PersonalizationPanel, Forms
├── context/       ← Auth, Theme, Toast (global state)
├── hooks/         ← Data fetching hooks
├── services/      ← API calls and SSE (streaming) reader
└── utils/         ← Agent icons, formatting helpers
```

### URL Structure (Frontend Routes)

```
/                      → Login / Signup
/dashboard             → Level 1: All 7 domain cards
/domain/:domain        → Level 2: Agents inside a domain
/agent/:agentKey       → Chat with an agent
/agent/:agentKey/setup → Two-step setup for a new agent
/profile               → View/edit all three profile levels
/settings              → Memory management
```

---

## 8. The Personalization Engine

This is the heart of the project. For every message, the system assembles context in this order:

```
Most General                                          Most Specific
     ↓                                                     ↓
Global Profile → Domain Profile → Agent Profile → Memory → Message
```

**Example for a Marketing request:**

| Level | Example Content |
|---|---|
| Global | "User prefers concise answers, intermediate skill level" |
| Domain | "Brand: Acme Cloud, Industry: SaaS, Audience: Developers, Tone: Professional" |
| Agent | "Platform: LinkedIn, Style: Bold typography, Logo: ACME CLOUD" |
| Memory (standing) | "User prefers posts under 150 characters" |
| Memory (semantic) | "User previously liked posts with statistics in the headline" |
| Message | "Create a post about cutting cloud costs with automation" |

All of this is assembled into the AI's system prompt, giving it full context to deliver a personalised, on-brand, style-consistent response.

The **right panel in the UI** shows you exactly which profile data and memories were used for the last response — full transparency into how personalisation is working.

---

## 9. AI & Model Support

The project supports **four interchangeable AI providers** — you switch with one environment variable:

### Option 1: Ollama (Recommended for local use — Free, no API key)
- Runs models on your own machine
- Recommended model: `llama3.2:3b` (2 GB, good quality/speed balance on CPU)
- No data leaves your machine
- Embedding model: `nomic-embed-text` (for memory search)

### Option 2: OpenAI-Compatible APIs (Hosted — Fast)
Works with: OpenAI, Groq (free tier available, very fast), Together AI, Mistral, OpenRouter, LM Studio, vLLM

### Option 3: AWS Bedrock (Enterprise)
Supports Claude 3.5 Sonnet, Titan embeddings — uses AWS IAM credentials

### Option 4: Mock Provider (Development)
Runs the entire system with zero AI model — useful for testing the pipeline, UI, memory, and profiles without any AI setup

### Response Streaming
Because local models can be slow (~5 tokens/second on a CPU), the system uses **Server-Sent Events (SSE)** to stream the response to the UI token by token. The user sees text appearing in real time rather than waiting for the whole answer. The system automatically falls back to non-streaming if a proxy blocks SSE.

---

## 10. Security

The project implements proper security practices throughout:

| Area | Implementation |
|---|---|
| **Passwords** | bcrypt hashing — passwords never stored in plain text |
| **Authentication** | JWT bearer tokens with expiry and signature verification |
| **Authorisation** | Every route requires a valid token (except login/register/health) |
| **Multi-tenancy** | Queries are always filtered by user ID — you cannot access another user's data |
| **Input Validation** | Pydantic v2 validates all inputs; profile data is whitelisted against declared fields |
| **SQL Injection** | All queries go through SQLAlchemy ORM; raw queries are fully parameterised |
| **CORS** | Restricted to configured origins only |
| **File Uploads** | Size, extension, and content type are all validated |
| **Secrets** | All credentials come from environment variables; nothing is hardcoded |
| **Frontend audit** | 0 known npm vulnerabilities |

---

## 11. Project Structure

```
Content Personalisation Agent/
│
├── backend/                   ← Python FastAPI server
│   ├── app/
│   │   ├── agents/            ← Agent definitions, router, scope guard, runtime, pipeline
│   │   ├── api/               ← REST API endpoints
│   │   ├── core/              ← Config, security, logging
│   │   ├── database/          ← DB session, portable types
│   │   ├── llm/               ← AI model providers (Ollama, OpenAI, Bedrock, Mock)
│   │   ├── media/             ← Image and chart rendering
│   │   ├── memory/            ← Memory extraction, storage, retrieval
│   │   ├── models/            ← Database table models
│   │   ├── schemas/           ← API request/response schemas
│   │   └── services/          ← Personalization, profiles, feedback, catalog
│   │
│   ├── alembic/               ← Database migration scripts
│   ├── scripts/               ← Dev utilities (seed data, verify tests, measure prompts)
│   ├── generated_media/       ← Where generated PNGs are saved
│   └── requirements.txt
│
├── frontend/                  ← React + Vite web application
│   └── src/
│       ├── pages/             ← All screens (Dashboard, Chat, Setup, Profile, etc.)
│       ├── components/        ← Reusable UI components
│       ├── context/           ← Auth, Theme, Toast state management
│       ├── hooks/             ← Data fetching hooks
│       ├── services/          ← API service layer
│       └── utils/             ← Helper functions
│
├── infra/                     ← Infrastructure config (PostgreSQL + pgvector setup)
├── docker-compose.yml         ← One-command full-stack deployment
└── .env.example               ← Environment variable reference
```

---

## 12. Current Status & Verified Results

All tests were run on an Intel i5-10210U, 4 cores, **no GPU**:

| Test | Result |
|---|---|
| Full pipeline verification (163 assertions) | ✅ **163/163 passed** |
| All 34 agents producing their declared output | ✅ **34/34 passed** (30 text, 3 image, 1 chart) |
| Router accuracy over all 34 agents | ✅ **21/21 routing cases** correct (by keyword scoring, no model call) |
| Live server test with real Ollama model | ✅ All steps passed |
| Image generation (Social Post) | ✅ 43.9s → 1200×627 PNG, brand colours applied |
| Chart generation (5 data points) | ✅ 53.5s → chart of exact numbers; refuses to fabricate |
| Scope handoff (wrong agent test) | ✅ 0.0s redirect, no model call |
| Memory scope isolation | ✅ Agent-scoped memory not visible to other agents |
| Database migration (v1 → v2 → v1) | ✅ **45/45 assertions** passed, no data loss |
| Frontend build | ✅ 26 files, 0 vulnerabilities |

### API Endpoints Available
- `GET /api/health` — System status
- `POST /api/auth/login` & `/register` — Authentication
- `GET /api/domains` — All 7 domains
- `GET /api/domains/{domain}/agents` — Agents in a domain
- `POST /api/chat` / `POST /api/chat/stream` — Send messages
- `GET /api/profile/global` / `PUT` — Global profile
- `PUT /api/profile/domain/{domain}` — Domain profile
- `PUT /api/profile/agent/{agent_key}` — Agent profile
- `POST /api/feedback` — Submit feedback
- `GET /api/memory` — View memories
- `GET /api/dashboard/stats` — Usage statistics
- Full Swagger docs: `http://localhost:8000/docs`

### Services and Ports
| Service | URL |
|---|---|
| Frontend Web App | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Documentation (Swagger) | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

---

## Summary

The Content Personalisation Agent is a sophisticated, production-ready multi-agent AI platform that:

1. **Organises AI assistance into 34 specialised agents** across 7 subject domains
2. **Personalises every response** using a 3-level profile system (global → domain → agent)
3. **Remembers user preferences** using a hybrid semantic + rule-based memory system
4. **Enforces agent boundaries** through a deterministic scope guard
5. **Produces real outputs** — text, branded images, and data charts
6. **Works on any hardware** — from a CPU-only laptop to cloud AI providers
7. **Provides full transparency** — showing the user exactly how their response was personalised

The system is fully containerised, thoroughly tested, and follows modern security best practices throughout.

---

*Report generated: September 27, 2026*
*Environment: Python 3.14.4, Node 20.20.2, Intel i5-10210U (no GPU)*

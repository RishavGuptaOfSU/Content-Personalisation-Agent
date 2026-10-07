# Content Personalisation Agent — Phase 2

## 🎯 Focus: Single-Domain Deep Personalisation Agent

Phase 2 narrows the scope from a general multi-domain system to a **single-domain, deeply personalised agent** — delivering hyper-relevant, adaptive content experiences within one vertical.

---

## 🗂️ Project Structure

```
phase-2/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI route handlers
│   │   ├── core/         # Config, settings, logging
│   │   ├── agents/       # Personalisation agent logic
│   │   ├── models/       # Pydantic & DB models
│   │   ├── services/     # Business logic / LLM calls
│   │   └── db/           # Database sessions & migrations
│   └── scripts/          # Utility / seed scripts
├── frontend/
│   └── src/              # React / Vite frontend
├── docs/                 # Architecture decisions, API specs
├── infra/                # Docker, CI/CD configs
├── .env.example
├── docker-compose.yml
└── README.md
```

---

## 🚀 Goals for Phase 2

- [ ] Define the target domain (e.g. EdTech, News, E-commerce…)
- [ ] Design the user preference & behaviour model
- [ ] Build a single-domain content ingestion pipeline
- [ ] Implement a personalisation agent with memory & feedback loop
- [ ] Real-time adaptive recommendations
- [ ] Lightweight, fast frontend for the chosen domain
- [ ] Evaluation metrics & A/B testing harness

---

## 🔗 Phase 1 Reference

Phase 1 codebase lives in [`../phase-1/`](../phase-1/README.md).

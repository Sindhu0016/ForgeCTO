# AI Startup CTO Agent (ForgeCTO)

Virtual CTO pipeline for founders: submit a startup idea and get market research, features, architecture, database design, APIs, AWS layout, cost estimates, roadmap, sprint plans, an **AI CTO Review Board** scorecard, a **critic score**, **Ask the CTO** chat, a **general assistant chatbot**, and a **downloadable code scaffold**.

## Stack

- **Backend:** FastAPI, LangGraph, LangChain, Gemini/OpenAI, Tavily, PostgreSQL
- **Frontend:** React, TypeScript, Vite, Mermaid.js
- **Ops:** Docker Compose

## Quick start

1. Copy env and add keys:

```bash
cp .env.example .env
```

Edit `.env` and set `GEMINI_API_KEY` (free) and/or `OPENAI_API_KEY` (optionally `TAVILY_API_KEY`, `GITHUB_TOKEN`, `GITHUB_REPO`).

2. Start everything:

```bash
docker compose up --build
```

3. Open [http://localhost:5173](http://localhost:5173) (or [http://127.0.0.1:5173](http://127.0.0.1:5173))

Without API keys you can still open the **seed demo** or run in **demo mode**.

## Agent pipeline

```
Planner → Research → Architecture → Database → API → AWS → Documentation → Critic → Review Board
```

## Hackathon features

| Feature | What it does |
|---------|----------------|
| **AI CTO Review Board** | Viral scorecard (architecture, scalability, security, cost, hiring, readiness) + exploration: diagrams, risks, cost→10M users, load, security audit, hiring, sprints, investor docs |
| **Critic agent** | Scores buildability / market fit / risk; flags inconsistencies |
| **Ask the CTO** | Chat grounded only in that project’s artifacts |
| **General chatbot** | Floating assistant + `/chat` page for open-ended startup/engineering help |
| **Code scaffold ZIP** | FastAPI + SQLAlchemy stubs from schema + endpoints |

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/projects` | Start a new CTO run |
| GET | `/api/projects` | List projects |
| GET | `/api/projects/{id}` | Project + artifacts |
| GET | `/api/projects/{id}/events` | SSE progress stream |
| POST | `/api/projects/{id}/chat` | Ask the CTO (artifact-grounded) |
| POST | `/api/chat` | General ForgeCTO assistant (not project-specific) |
| GET | `/api/projects/{id}/export/markdown/download` | Download docs markdown |
| GET | `/api/projects/{id}/export/scaffold` | Download FastAPI scaffold ZIP |
| POST | `/api/projects/{id}/export/github` | Create GitHub issues |

### Local backend (without Docker)

Use **Python 3.10–3.12** (3.14 may lack binary wheels on Windows).

```bash
cd backend
py -3.10 -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
$env:DATABASE_URL="sqlite+aiosqlite:///./dev.db"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

### Local frontend

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Set `VITE_API_URL=http://127.0.0.1:8001` in `frontend/.env`.

## Environment

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | Free Gemini key from Google AI Studio (preferred) |
| `OPENAI_API_KEY` | Optional OpenAI key |
| `LLM_PROVIDER` | `auto` (prefer Gemini), `gemini`, or `openai` |
| `TAVILY_API_KEY` | Live market search (fallback placeholder if missing) |
| `DATABASE_URL` | Async SQLAlchemy URL (`postgresql+asyncpg://…` or sqlite) |
| `GITHUB_TOKEN` | Optional issue export |
| `GITHUB_REPO` | Default `owner/repo` for issue export |
| `RATE_LIMIT_PER_MINUTE` | POST /api/projects throttle |
| `SEED_ON_STARTUP` | Create demo project on boot |

## Example idea

> I want to build an Uber for pet grooming.

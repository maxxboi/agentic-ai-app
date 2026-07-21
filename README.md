
<div align="center">

# 🧭 Agentic Ops Console

**A full-stack, agentic AI reference app — FastAPI + Gemini function calling on the backend, React on the frontend, and a guaranteed-shape JSON contract in between.**

[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Gemini](https://img.shields.io/badge/Gemini-API-4285F4?logo=google&logoColor=white)](https://aistudio.google.com/)
[![License](https://img.shields.io/badge/license-MIT-black)](#license)

</div>

---

## What this is

Agentic Ops Console is a small but complete demonstration of three things that are hard to get right together in an LLM app:

- **Prompt engineering** — a system prompt that forces step-by-step reasoning and disciplined tool use, instead of hoping the model "does the right thing."
- **Reliable structured JSON** — the model can only finish by calling a `submit_final_answer` function whose schema mirrors a Pydantic model. Every response is validated server-side, and invalid ones are bounced back to the model to self-correct.
- **A real full-stack shape** — a typed FastAPI backend and a React console UI that shows the agent's live reasoning trace, not just the final answer.

It ships with a **mock mode** so you can run the entire stack — frontend, backend, schema validation, tool calls — with **zero API key and zero setup**.

<br>

<div align="center">

| Left panel | Right panel |
|---|---|
| Live agent trace — thoughts → tool calls → tool results | Final answer, stamped `SCHEMA VALID` once it passes Pydantic |

</div>

---

## Table of contents

- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quickstart](#quickstart)
  - [1. Backend](#1-backend-fastapi)
  - [2. Frontend](#2-frontend-react--vite--tailwind)
- [How the reliable-JSON pattern works](#how-the-reliable-json-pattern-works)
- [API reference](#api-reference)
- [Configuration](#configuration)
- [Production build](#production-build)
- [Extending the agent](#extending-the-agent)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Architecture

```
┌──────────────────────┐        HTTP / JSON        ┌───────────────────────────┐
│   React + Vite UI    │ ─────────────────────────▶ │        FastAPI            │
│  (Agent trace panel, │ ◀───────────────────────── │  /api/health               │
│   Answer card)        │                            │  /api/agent/query          │
└──────────────────────┘                            └────────────┬──────────────┘
                                                                    │
                                                       ┌────────────▼──────────────┐
                                                       │  Agent loop (agent.py)     │
                                                       │  • system prompt            │
                                                       │  • Gemini function calling  │
                                                       │  • Pydantic validation      │
                                                       │  • self-healing retries     │
                                                       └────────────┬──────────────┘
                                                                    │
                                                ┌───────────────────┼───────────────────┐
                                                ▼                   ▼                   ▼
                                          calculator         current_datetime     knowledge_lookup
                                          (tools.py)           (tools.py)            (tools.py)
```

If `GEMINI_API_KEY` is unset, the agent loop is swapped for a deterministic offline mock that returns the exact same schema — the UI can't tell the difference.

---

## Project structure

```
agentic-ai-app/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + routes
│   │   ├── agent.py         # agent loop, prompt engineering, retry/validation logic
│   │   ├── schemas.py       # Pydantic contracts — the "reliable JSON" schema
│   │   ├── tools.py         # tool registry (calculator, datetime, knowledge lookup)
│   │   └── config.py        # env-driven settings
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── components/
│   │   │   ├── QueryForm.jsx
│   │   │   ├── TraceStep.jsx
│   │   │   ├── AnswerCard.jsx
│   │   │   └── StatusBadge.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
└── README.md
```

---

## Prerequisites

- **Python** 3.10+
- **Node.js** 18+ and npm
- *(Optional, for live mode)* a **Google Gemini API key** — free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

---

## Quickstart

### 1. Backend (FastAPI)

```bash
cd agentic-ai-app/backend

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Open .env and paste your key to enable live mode:
#   GEMINI_API_KEY=AIza...
# Leave it blank to run in mock mode.

# Run the API server
uvicorn app.main:app --reload --port 8000
```

The API is now live at **http://localhost:8000** — interactive docs at **http://localhost:8000/docs**.

```bash
# Smoke test
curl http://localhost:8000/api/health

curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is 42 * (17 - 5)?"}'
```

### 2. Frontend (React + Vite + Tailwind)

Open a **second terminal** (leave the backend running):

```bash
cd agentic-ai-app/frontend
npm install
npm run dev
```

The app is now live at **http://localhost:5173**. Vite proxies any `/api/*` request to `http://localhost:8000`, so there's no extra CORS config needed in dev.

Try a query like `What is 42 * (17 - 5)?` or `Tell me about FastAPI` and hit **Run agent** — watch the reasoning trace stream in on the left, and the schema-validated answer land on the right.

---

## How the reliable-JSON pattern works

1. `schemas.py` defines `StructuredAnswer` — the guaranteed output shape — as a Pydantic model.
2. A hand-written, Gemini-compatible JSON schema mirroring that model is registered as the parameters of a function called `submit_final_answer`.
3. The system prompt instructs the model that the **only** way to finish is to call that function — far more reliable than asking for raw JSON in prose.
4. Every call to `submit_final_answer` is validated with `StructuredAnswer.model_validate(...)`.
5. If validation fails, the error is sent back to the model as a function response and it's asked to correct and resubmit — a self-healing retry loop, bounded by `JSON_RETRY_ATTEMPTS` / `MAX_AGENT_STEPS`.
6. The FastAPI route only ever returns a value that has already passed through `AgentRunResponse`, so the frontend can trust the shape 100% of the time.

---

## API reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Returns `{status, mock_mode, model}` |
| `POST` | `/api/agent/query` | Body: `{"query": string, "session_id"?: string}` → `AgentRunResponse` |

`AgentRunResponse` shape:

```json
{
  "request_id": "uuid",
  "query": "string",
  "steps": [
    { "type": "thought | tool_call | tool_result | final_answer", "content": "string", "tool_call": {}, "tool_result": {} }
  ],
  "answer": {
    "summary": "string",
    "details": ["string"],
    "confidence": "low | medium | high",
    "follow_up_questions": ["string"]
  },
  "model": "string",
  "mock_mode": false
}
```

---

## Configuration

All settings live in `backend/.env` (see `.env.example`):

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(empty)* | Enables live mode when set |
| `MODEL_NAME` | `gemini-2.5-flash` | Any Gemini model that supports function calling |
| `MAX_TOKENS` | `2048` | Max output tokens per model call |
| `MAX_AGENT_STEPS` | `6` | Upper bound on the tool-call loop |
| `JSON_RETRY_ATTEMPTS` | `3` | Retries for schema-validation self-healing |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed origins |

---

## Production build

**Backend** — run behind a process manager:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend** — build static assets and serve from any static host / CDN / nginx:
```bash
cd frontend
npm run build      # outputs to frontend/dist
npm run preview    # local sanity check of the production build
```
Point the frontend at your deployed API by updating the Vite proxy (dev) or adding an API base env var to `src/api.js` (prod, if the API is on a different origin).

---

## Extending the agent

- **Add a tool** — write a function in `backend/app/tools.py`, add its JSON schema to `TOOL_SCHEMAS`; it's automatically available to the agent loop.
- **Change the output shape** — edit `StructuredAnswer` in `schemas.py` and the matching `SUBMIT_FINAL_ANSWER_SCHEMA` in `agent.py`.
- **Swap the model** — set `MODEL_NAME` in `.env` to any Gemini model that supports function calling.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Frontend shows "BACKEND OFFLINE" | Make sure `uvicorn` is running on port 8000 |
| Badge shows "MOCK MODE" | Set `GEMINI_API_KEY` in `backend/.env` and restart uvicorn |
| CORS errors in prod | Add your frontend's origin to `CORS_ORIGINS` in `.env` |
| `ModuleNotFoundError` on backend start | Re-activate the venv and re-run `pip install -r requirements.txt` |

---

## License

MIT — use it, fork it, ship it.

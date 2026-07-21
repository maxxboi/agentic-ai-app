# Agentic Ops Console

A full-stack, agentic AI reference project demonstrating:

- **Prompt engineering** — a system prompt that forces step-by-step reasoning and tool use
- **Reliable structured JSON output** — the model is required to "answer" by calling a `submit_final_answer` tool whose schema mirrors a Pydantic model, and every response is validated (with self-healing retries) before it ever reaches the client
- **FastAPI backend** — a small, typed, well-documented API (`/api/health`, `/api/agent/query`)
- **React (Vite + Tailwind) frontend** — a console UI that shows the agent's live reasoning trace, tool calls, and the final validated answer

It runs in two modes:

| Mode | When | Behavior |
|---|---|---|
| **Live** | `ANTHROPIC_API_KEY` is set | Calls Claude via the Anthropic Messages API with real tool use |
| **Mock** | No API key set | Deterministic offline agent, same schema/contract — lets you run the whole stack with zero setup |

---

## 1. Project structure

```
agentic-ai-app/
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI app + routes
│   │   ├── agent.py        # agent loop, prompt engineering, retry/validation logic
│   │   ├── schemas.py       # Pydantic contracts (the "reliable JSON" schema)
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
└── README.md   ← you are here
```

---

## 2. Prerequisites

- **Python** 3.10+
- **Node.js** 18+ and npm
- (Optional, for live mode) an **Anthropic API key** — https://console.anthropic.com

---

## 3. Backend setup (FastAPI)

```bash
cd agentic-ai-app/backend

# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Open .env and paste your key to enable live mode:
#   ANTHROPIC_API_KEY=sk-ant-...
# Leave it blank to run in mock mode.

# 4. Run the API server
uvicorn app.main:app --reload --port 8000
```

The API is now live at **http://localhost:8000**.
Interactive docs (Swagger UI): **http://localhost:8000/docs**

Quick smoke test:

```bash
curl http://localhost:8000/api/health

curl -X POST http://localhost:8000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is 42 * (17 - 5)?"}'
```

---

## 4. Frontend setup (React + Vite + Tailwind)

Open a **second terminal** (leave the backend running):

```bash
cd agentic-ai-app/frontend

# 1. Install dependencies
npm install

# 2. Run the dev server
npm run dev
```

The app is now live at **http://localhost:5173**. Vite is pre-configured to proxy any `/api/*` request to `http://localhost:8000`, so no extra CORS setup is needed in dev.

Type a query (e.g. `What is 42 * (17 - 5)?` or `Tell me about FastAPI`) and press **Run agent** — you'll see:

- the agent's live reasoning trace (thoughts → tool calls → tool results) on the left
- the final, schema-validated structured answer on the right, stamped **SCHEMA VALID**

---

## 5. How the "reliable JSON" pattern works

1. `schemas.py` defines `StructuredAnswer` (the guaranteed output shape) with Pydantic.
2. That model's JSON schema is registered as the input schema of a tool called `submit_final_answer`.
3. The system prompt in `agent.py` instructs Claude that the **only** way to finish is to call that tool — this is far more reliable than asking the model to emit raw JSON in prose.
4. Every call to `submit_final_answer` is validated with `StructuredAnswer.model_validate(...)`.
5. If validation fails, the error is fed back to the model as a tool-result error and it is asked to correct and resubmit — a self-healing retry loop, bounded by `JSON_RETRY_ATTEMPTS` / `MAX_AGENT_STEPS`.
6. The FastAPI route only ever returns a value that has already passed through this validated `AgentRunResponse` model, so the frontend can trust the shape 100% of the time.

---

## 6. Building for production

**Backend** — run behind a process manager, e.g.:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend** — build static assets and serve them from any static host / CDN / nginx:
```bash
cd frontend
npm run build      # outputs to frontend/dist
npm run preview    # local sanity check of the production build
```
Remember to point the frontend at your deployed API (edit `vite.config.js` proxy for dev, or set an `VITE_API_BASE` env var and update `src/api.js` for prod if the API is on a different origin).

---

## 7. Extending the agent

- **Add a tool**: write a function in `backend/app/tools.py`, add its JSON schema to `TOOL_SCHEMAS`, and it's automatically available to the agent loop.
- **Change the output shape**: edit `StructuredAnswer` in `schemas.py` — the tool schema and validation logic pick it up automatically.
- **Swap the model**: set `MODEL_NAME` in `.env`.

---

## 8. Troubleshooting

| Symptom | Fix |
|---|---|
| Frontend shows "BACKEND OFFLINE" | Make sure `uvicorn` is running on port 8000 |
| Badge shows "MOCK MODE" | Set `ANTHROPIC_API_KEY` in `backend/.env` and restart uvicorn |
| CORS errors in prod | Add your frontend's origin to `CORS_ORIGINS` in `.env` |
| `ModuleNotFoundError` on backend start | Re-activate the venv and re-run `pip install -r requirements.txt` |

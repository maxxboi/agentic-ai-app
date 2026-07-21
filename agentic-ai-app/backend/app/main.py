from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .agent import run_agent, AgentError
from .config import settings
from .schemas import AgentQueryRequest, AgentRunResponse, HealthResponse

app = FastAPI(
    title="Agentic Ops Console API",
    description="Structured-output agentic AI backend with reliable JSON via Pydantic + tool-forced schemas.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", mock_mode=settings.MOCK_MODE, model=settings.MODEL_NAME)


@app.post("/api/agent/query", response_model=AgentRunResponse)
def query_agent(payload: AgentQueryRequest) -> AgentRunResponse:
    try:
        return run_agent(payload.query)
    except AgentError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Unexpected agent failure: {exc}") from exc

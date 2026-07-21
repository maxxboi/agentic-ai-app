"""
Structured-output contracts.

Every response the agent produces is validated against these Pydantic
models before it is ever sent to the client. This is the core of the
"reliable JSON" guarantee: the LLM is instructed (via prompt + tool
schema) to emit JSON matching these shapes, and anything that fails
validation is retried rather than forwarded to the user.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


class StepType(str, Enum):
    THOUGHT = "thought"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    FINAL_ANSWER = "final_answer"


class ToolCall(BaseModel):
    name: str = Field(..., description="Name of the tool being invoked")
    arguments: dict[str, Any] = Field(default_factory=dict)


class AgentStep(BaseModel):
    """One step in the agent's reasoning trace."""
    type: StepType
    content: str = Field(..., description="Human-readable description of this step")
    tool_call: Optional[ToolCall] = None
    tool_result: Optional[Any] = None


class Confidence(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class StructuredAnswer(BaseModel):
    """The final, guaranteed-shape answer returned to the client."""
    summary: str = Field(..., description="One or two sentence direct answer")
    details: list[str] = Field(default_factory=list, description="Supporting bullet points")
    confidence: Confidence = Confidence.MEDIUM
    follow_up_questions: list[str] = Field(default_factory=list, max_length=3)


class AgentRunResponse(BaseModel):
    """Top-level response for a single /api/agent/query call."""
    request_id: str
    query: str
    steps: list[AgentStep]
    answer: StructuredAnswer
    model: str
    mock_mode: bool


class AgentQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None


class HealthResponse(BaseModel):
    status: Literal["ok"]
    mock_mode: bool
    model: str

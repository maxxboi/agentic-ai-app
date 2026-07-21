"""
Agent orchestration.

This module is the heart of the "agentic AI" behavior:

1.  A system prompt (prompt engineering) instructs Claude to reason step
    by step, call tools when useful, and ALWAYS finish by calling the
    `submit_final_answer` tool with arguments matching `StructuredAnswer`.
2.  A tool-use loop lets Claude call the tools in `tools.py` any number
    of times (bounded by MAX_AGENT_STEPS) before submitting.
3.  `submit_final_answer` is itself modeled as a tool whose input_schema
    mirrors StructuredAnswer -- this is the "force structured output via
    tool calling" pattern, which is far more reliable than asking the
    model to free-format JSON in prose.
4.  Every candidate answer is validated with Pydantic; on failure we
    retry with the validation error fed back to the model (self-healing
    JSON), up to JSON_RETRY_ATTEMPTS times.
5.  If no ANTHROPIC_API_KEY is configured, `mock_run` produces a fully
    valid, deterministic AgentRunResponse so the rest of the stack can
    be exercised with zero setup.
"""
from __future__ import annotations

import json
import uuid
from typing import Any

from pydantic import ValidationError
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from .config import settings
from .schemas import (
    AgentRunResponse,
    AgentStep,
    StepType,
    StructuredAnswer,
    ToolCall,
)
from .tools import TOOL_SCHEMAS, run_tool

SYSTEM_PROMPT = """You are an autonomous research and reasoning agent embedded in a \
product called "Agentic Ops Console".

Rules you MUST follow:
1. Think step by step. Before acting, briefly state your plan.
2. Use the available tools whenever they would improve accuracy (math, \
dates, knowledge lookups). Do not guess at facts a tool can verify.
3. Keep tool arguments minimal and exactly matching each tool's schema.
4. When you have enough information, you MUST call the \
`submit_final_answer` tool exactly once to deliver your answer. Do not \
answer in plain text -- the ONLY way to finish is calling that tool.
5. `summary` must be 1-2 sentences, directly answering the user's query.
6. `details` should be 2-5 short bullet points with supporting reasoning \
or evidence, each under 25 words.
7. `confidence` must honestly reflect how certain you are: "low", \
"medium", or "high".
8. `follow_up_questions` should contain 0-3 natural next questions the \
user might ask.
"""

SUBMIT_TOOL = {
    "name": "submit_final_answer",
    "description": "Deliver the final structured answer to the user. Must be called exactly once, as the last action.",
    "input_schema": StructuredAnswer.model_json_schema(),
}


class AgentError(Exception):
    pass


def _client():
    import anthropic

    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


@retry(
    stop=stop_after_attempt(settings.JSON_RETRY_ATTEMPTS),
    wait=wait_fixed(0.5),
    retry=retry_if_exception_type(ValidationError),
    reraise=True,
)
def _validate_answer(raw: dict[str, Any]) -> StructuredAnswer:
    """Validate model output against StructuredAnswer, retrying on failure
    is handled one level up (we need to re-prompt the model, not just
    re-parse), so this wrapper mainly centralizes the validation call and
    gives us a single place to log/inspect malformed payloads."""
    return StructuredAnswer.model_validate(raw)


def run_agent(query: str) -> AgentRunResponse:
    request_id = str(uuid.uuid4())

    if settings.MOCK_MODE:
        return _mock_run(request_id, query)

    client = _client()
    tools = TOOL_SCHEMAS + [SUBMIT_TOOL]
    messages: list[dict[str, Any]] = [{"role": "user", "content": query}]
    steps: list[AgentStep] = []
    last_validation_error: str | None = None

    for _ in range(settings.MAX_AGENT_STEPS):
        system = SYSTEM_PROMPT
        if last_validation_error:
            system += (
                "\n\nIMPORTANT: your previous call to submit_final_answer failed "
                f"schema validation with this error, fix it and call the tool again:\n"
                f"{last_validation_error}"
            )

        response = client.messages.create(
            model=settings.MODEL_NAME,
            max_tokens=settings.MAX_TOKENS,
            system=system,
            messages=messages,
            tools=tools,
        )

        assistant_content = response.content
        messages.append({"role": "assistant", "content": assistant_content})

        # Record any thinking/text blocks
        for block in assistant_content:
            if block.type == "text" and block.text.strip():
                steps.append(AgentStep(type=StepType.THOUGHT, content=block.text.strip()))

        tool_use_blocks = [b for b in assistant_content if b.type == "tool_use"]

        if not tool_use_blocks:
            # Model didn't call a tool at all -- nudge it to comply.
            messages.append(
                {
                    "role": "user",
                    "content": "Please call the submit_final_answer tool now with your answer.",
                }
            )
            continue

        tool_results = []
        finished_answer: StructuredAnswer | None = None

        for block in tool_use_blocks:
            if block.name == "submit_final_answer":
                try:
                    finished_answer = _validate_answer(block.input)
                    steps.append(
                        AgentStep(
                            type=StepType.FINAL_ANSWER,
                            content="Submitted final structured answer.",
                        )
                    )
                except ValidationError as exc:
                    last_validation_error = str(exc)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": f"Validation error, fix and resubmit: {exc}",
                            "is_error": True,
                        }
                    )
                    continue
            else:
                steps.append(
                    AgentStep(
                        type=StepType.TOOL_CALL,
                        content=f"Calling tool `{block.name}`",
                        tool_call=ToolCall(name=block.name, arguments=block.input),
                    )
                )
                result = run_tool(block.name, block.input)
                steps.append(
                    AgentStep(
                        type=StepType.TOOL_RESULT,
                        content=f"Result from `{block.name}`",
                        tool_result=result,
                    )
                )
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result),
                    }
                )

        if finished_answer is not None:
            return AgentRunResponse(
                request_id=request_id,
                query=query,
                steps=steps,
                answer=finished_answer,
                model=settings.MODEL_NAME,
                mock_mode=False,
            )

        if tool_results:
            messages.append({"role": "user", "content": tool_results})

    # Exhausted MAX_AGENT_STEPS without a validated final answer.
    fallback = StructuredAnswer(
        summary="The agent could not produce a validated answer within the step budget.",
        details=["Try rephrasing the query or increasing MAX_AGENT_STEPS."],
        confidence="low",
    )
    return AgentRunResponse(
        request_id=request_id,
        query=query,
        steps=steps,
        answer=fallback,
        model=settings.MODEL_NAME,
        mock_mode=False,
    )


def _mock_run(request_id: str, query: str) -> AgentRunResponse:
    """Deterministic offline agent used when ANTHROPIC_API_KEY is unset.
    Exercises the exact same schema contract as the real path."""
    from .tools import run_tool

    steps: list[AgentStep] = [
        AgentStep(type=StepType.THOUGHT, content=f"Planning how to answer: '{query}'"),
    ]

    lowered = query.lower()
    details: list[str] = []

    if any(ch.isdigit() for ch in query) and any(op in query for op in "+-*/"):
        expr = "".join(ch for ch in query if ch in "0123456789+-*/(). ")
        steps.append(
            AgentStep(
                type=StepType.TOOL_CALL,
                content="Calling tool `calculator`",
                tool_call=ToolCall(name="calculator", arguments={"expression": expr}),
            )
        )
        result = run_tool("calculator", {"expression": expr})
        steps.append(AgentStep(type=StepType.TOOL_RESULT, content="Result from `calculator`", tool_result=result))
        details.append(f"Computed '{expr}' -> {result.get('result', result.get('error'))}")
        summary = f"The result of your expression is {result.get('result', 'unavailable')}."
    else:
        steps.append(
            AgentStep(
                type=StepType.TOOL_CALL,
                content="Calling tool `knowledge_lookup`",
                tool_call=ToolCall(name="knowledge_lookup", arguments={"topic": query}),
            )
        )
        result = run_tool("knowledge_lookup", {"topic": query})
        steps.append(AgentStep(type=StepType.TOOL_RESULT, content="Result from `knowledge_lookup`", tool_result=result))
        details.append(result["summary"])
        summary = (
            f"(Mock mode -- set ANTHROPIC_API_KEY for live answers) Here's what I found on '{query}'."
        )

    steps.append(AgentStep(type=StepType.FINAL_ANSWER, content="Submitted final structured answer."))

    answer = StructuredAnswer(
        summary=summary,
        details=details or ["No additional detail available in mock mode."],
        confidence="medium",
        follow_up_questions=[
            "Can you go deeper on this topic?",
            "What tools did you use to answer?",
        ],
    )

    return AgentRunResponse(
        request_id=request_id,
        query=query,
        steps=steps,
        answer=answer,
        model="mock-agent-v1",
        mock_mode=True,
    )

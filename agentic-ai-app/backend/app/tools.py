"""
Tool registry for the agent.

Each tool is a plain Python function plus a JSON-schema description that
gets sent to Claude via the `tools` parameter of the Messages API. Add a
new tool by writing the function and appending its schema to TOOL_SCHEMAS.
"""
from __future__ import annotations

import datetime as dt
import math
from typing import Any, Callable


def calculator(expression: str) -> dict[str, Any]:
    """Safely evaluate a basic arithmetic expression."""
    allowed = "0123456789+-*/(). %"
    if not all(ch in allowed for ch in expression):
        return {"error": "Expression contains unsupported characters"}
    try:
        # eval is scoped to no builtins and only math-safe characters above
        result = eval(expression, {"__builtins__": {}}, {"math": math})
        return {"expression": expression, "result": result}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def current_datetime(timezone_offset_hours: float = 0.0) -> dict[str, Any]:
    """Return the current date/time, optionally offset from UTC."""
    now = dt.datetime.utcnow() + dt.timedelta(hours=timezone_offset_hours)
    return {"iso": now.isoformat(), "utc_offset_hours": timezone_offset_hours}


def knowledge_lookup(topic: str) -> dict[str, Any]:
    """
    Stub knowledge base used by the mock agent and as an example of a
    'retrieval' tool. Swap this out for a real vector DB / search API call.
    """
    fake_kb = {
        "fastapi": "FastAPI is a modern Python web framework for building APIs with automatic OpenAPI docs.",
        "react": "React is a JavaScript library for building user interfaces from composable components.",
        "pydantic": "Pydantic provides data validation and settings management using Python type annotations.",
    }
    key = topic.lower().strip()
    for k, v in fake_kb.items():
        if k in key:
            return {"topic": topic, "summary": v}
    return {"topic": topic, "summary": f"No indexed knowledge found for '{topic}'."}


TOOL_FUNCTIONS: dict[str, Callable[..., dict[str, Any]]] = {
    "calculator": calculator,
    "current_datetime": current_datetime,
    "knowledge_lookup": knowledge_lookup,
}

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression and return the numeric result.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "e.g. '12 * (3 + 4)'"}
            },
            "required": ["expression"],
        },
    },
    {
        "name": "current_datetime",
        "description": "Get the current date and time, optionally offset from UTC in hours.",
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone_offset_hours": {"type": "number", "default": 0}
            },
        },
    },
    {
        "name": "knowledge_lookup",
        "description": "Look up a short summary of a technical topic from the internal knowledge base.",
        "input_schema": {
            "type": "object",
            "properties": {"topic": {"type": "string"}},
            "required": ["topic"],
        },
    },
]


def run_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return {"error": f"Unknown tool '{name}'"}
    try:
        return fn(**arguments)
    except TypeError as exc:
        return {"error": f"Invalid arguments for '{name}': {exc}"}

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google.adk.agents.context import Context
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse

from consent_adk_demo.config.settings import LLM_IO_LOG_PATH, LOG_LLM_IO


def _to_jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", by_alias=True, exclude_none=True)
    return value


def _write_log(record: dict[str, Any]) -> None:
    path = Path(LLM_IO_LOG_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _base_record(callback_context: Context, event_type: str) -> dict[str, Any]:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "invocation_id": callback_context.invocation_id,
        "agent_name": callback_context.agent_name,
        "user_id": callback_context.user_id,
        "session_id": callback_context.session.id if callback_context.session else None,
    }


def log_llm_request(callback_context: Context, llm_request: LlmRequest) -> None:
    """Log the complete ADK request payload before it is sent to the model."""
    if not LOG_LLM_IO:
        return None

    _write_log(
        {
            **_base_record(callback_context, "llm_request"),
            "request": _to_jsonable(llm_request),
        }
    )
    return None


def log_llm_response(callback_context: Context, llm_response: LlmResponse) -> None:
    """Log the complete ADK response payload received from the model."""
    if not LOG_LLM_IO:
        return None

    _write_log(
        {
            **_base_record(callback_context, "llm_response"),
            "response": _to_jsonable(llm_response),
        }
    )
    return None

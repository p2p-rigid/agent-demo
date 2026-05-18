from typing import Optional, Literal

from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent

from consent_adk_demo.observability.llm_io import log_llm_request, log_llm_response


class ValidationResult(BaseModel):
    """Structured output from the UserIntentValidator agent."""

    status: Literal["valid", "invalid"]
    intent: Optional[Literal["create_consent", "revoke_consent"]] = None
    mac_id: Optional[str] = None
    consent_type: Optional[str] = None
    channel: Optional[str] = None
    errors: Optional[list[str]] = Field(default=None, description="List of validation errors when status is invalid")


VALIDATOR_INSTRUCTION = """You are a consent management request validator. Your only job is to parse a user's natural language request and return a validation result as JSON.

STEP 1 — Identify the user's intent:
- "create" or "create consent" → intent = "create_consent"
- "revoke" or "revoke consent" → intent = "revoke_consent"

STEP 2 — Extract these fields ONLY from the user's message:
- mac_id: the MAC identifier (exactly as written in the user's message)
- consent_type: the consent type code (exactly as written)
- channel: the channel code (exactly as written)

STEP 3 — Validate all fields against these rules (MUST ALL PASS):
1. mac_id must be numeric only (digits 0-9, no letters or symbols).
2. mac_id must be exactly 7 digits long.
3. consent_type must be one of: MR, RR, RP.
4. channel must be one of: BB, PB.
5. All three fields (mac_id, consent_type, channel) MUST be explicitly mentioned in the user's message.
6. The intent must be create_consent or revoke_consent.

CRITICAL RULE: If the user did NOT provide a field, use null for that field in the output. The validation will then fail because the field is missing. NEVER make up a value for a field the user did not mention.

STEP 4 — Return EXACTLY a JSON object with no other text, no markdown fences, no explanation:

If ALL rules pass:
{"status":"valid","intent":"<create_consent or revoke_consent>","mac_id":"<value>","consent_type":"<value>","channel":"<value>"}

If ANY rule fails (including missing fields — use null):
{"status":"invalid","errors":["<error description>","<error description>"]}

Example of missing field (user said "Create consent for mac 1234567 type MR" — no channel mentioned):
{"status":"invalid","errors":["channel is required but was not provided"]}

Do NOT include both valid fields and errors. Never guess or invent values. Output ONLY the JSON object, nothing else."""


def create_user_intent_validator(model: str) -> LlmAgent:
    """Create the UserIntentValidator agent.

    Args:
        model: The model string (e.g. "deepseek/deepseek-chat").

    Returns:
        A configured LlmAgent.
    """
    return LlmAgent(
        name="user_intent_validator",
        description="Validates user consent management requests and extracts required fields",
        model=model,
        instruction=VALIDATOR_INSTRUCTION,
        output_key="validation_result",
        before_model_callback=log_llm_request,
        after_model_callback=log_llm_response,
    )

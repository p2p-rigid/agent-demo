import json
import re
from typing import AsyncGenerator

from typing_extensions import override

from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event
from google.genai import types

from consent_adk_demo.agents.user_intent_validator import create_user_intent_validator
from consent_adk_demo.agents.consent_action_agent import create_consent_action_agent


def _extract_validation(state: dict) -> dict:
    """Decode validation_result from session state, handling string JSON."""
    validation = state.get("validation_result", {})
    if isinstance(validation, str):
        raw = validation.strip()
        m = re.search(r'\{[^{}]*"status"\s*:\s*"[^"]*"[^{}]*\}', raw, re.DOTALL)
        if m:
            validation = json.loads(m.group(0))
        else:
            validation = {}
    return validation if isinstance(validation, dict) else {}


class ConsentWorkflowAgent(BaseAgent):
    """Orchestrates validation then conditionally invokes the action agent.

    Runs the validator first. If validation fails, yields the error and stops —
    the action agent is never invoked. If validation passes, runs the action agent.
    """

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        if not self.sub_agents:
            return

        # Step 1 — run the validator
        async for event in self.sub_agents[0].run_async(ctx):
            yield event

        # Step 2 — inspect the validation result in shared session state
        validation = _extract_validation(ctx.session.state)

        if validation.get("status") != "valid":
            errors = validation.get("errors", ["Unknown validation error"])
            errors_lines = "\n".join(f"  - {e}" for e in errors)
            error_text = (
                "The consent request could not be processed due to validation errors:\n\n"
                f"{errors_lines}\n\n"
                "Please correct these issues and try again."
            )
            yield Event(
                invocation_id=ctx.invocation_id,
                author=self.name,
                branch=ctx.branch,
                content=types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=error_text)],
                ),
            )
            return

        # Step 3 — validation passed; run the action agent
        if len(self.sub_agents) > 1:
            async for event in self.sub_agents[1].run_async(ctx):
                yield event


def create_sequential_agent(model: str) -> ConsentWorkflowAgent:
    """Create the consent workflow agent.

    Chains UserIntentValidator → (conditionally) ConsentActionAgent.

    Args:
        model: The model string (e.g. "deepseek/deepseek-chat").

    Returns:
        A configured ConsentWorkflowAgent.
    """
    user_intent_validator = create_user_intent_validator(model)
    consent_action_agent = create_consent_action_agent(model)

    return ConsentWorkflowAgent(
        name="consent_workflow",
        description="Consent management workflow: validates user request then conditionally executes consent action",
        sub_agents=[user_intent_validator, consent_action_agent],
    )

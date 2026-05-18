import json
import re
from typing import AsyncGenerator

from typing_extensions import override

from google.adk.agents.base_agent import BaseAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events.event import Event
from google.genai import types

from consent_adk_demo.agents.user_intent_validator import create_user_intent_validator
from consent_adk_demo.agents.consent_action_agent import create_consent_action_agent

def create_sequential_agent(model: str) -> SequentialAgent:
    """Create the consent workflow agent.

    Chains UserIntentValidator → (conditionally) ConsentActionAgent.

    Args:
        model: The model string (e.g. "deepseek/deepseek-chat").

    Returns:
        A configured SequentialAgent.
    """
    user_intent_validator = create_user_intent_validator(model)
    consent_action_agent = create_consent_action_agent(model)

    return SequentialAgent(
        name="consent_workflow",
        description="Consent management workflow: validates user request then conditionally executes consent action",
        sub_agents=[user_intent_validator, consent_action_agent],
    )

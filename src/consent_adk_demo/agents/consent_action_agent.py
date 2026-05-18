from google.adk.agents import LlmAgent

from consent_adk_demo.observability.llm_io import log_llm_request, log_llm_response
from consent_adk_demo.tools.consent_tools import create_consent, revoke_consent

ACTION_INSTRUCTION = """The consent request passed validation. Execute the consent action now.

Based on the validated data provided in the conversation:
- If intent is "create_consent": call the create_consent function with the mac_id, consent_type, and channel from the validated data.
- If intent is "revoke_consent": call the revoke_consent function with the mac_id, consent_type, and channel from the validated data.

Use the exact values from the validation. Do not guess or modify any values. After calling the tool, report the result to the user."""


def create_consent_action_agent(model: str) -> LlmAgent:
    """Create the ConsentActionAgent.

    Args:
        model: The model string (e.g. "deepseek/deepseek-chat").

    Returns:
        A configured LlmAgent.
    """
    return LlmAgent(
        name="consent_action_agent",
        description="Executes consent actions (create or revoke) based on validated input",
        model=model,
        instruction=ACTION_INSTRUCTION,
        tools=[create_consent, revoke_consent],
        before_model_callback=log_llm_request,
        after_model_callback=log_llm_response,
    )

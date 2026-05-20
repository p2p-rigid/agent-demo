from google.adk.agents import LlmAgent

from consent_adk_demo.observability.llm_io import log_llm_request, log_llm_response
from consent_adk_demo.tools.consent_tools import audit_action

AUDIT_INSTRUCTION = """After a consent action is executed, call the audit_action function to log the action for compliance purposes.
The audit_action function should be called with the following parameters:
- action: The action performed (create_consent or revoke_consent).
- mac_id: The 7-digit numeric MAC identifier.
- consent_type: The consent type (MR, RR, or RP).
- channel: The channel (BB or PB).
Use the exact values from the consent action execution. 
Do not guess or modify any values. The audit log entry should be created for every consent action executed.
After calling the audit_action tool, you need to report the audit result to the user. The result must be the output of the audit_action function call"""



def create_audit_agent(model: str) -> LlmAgent:
    """Create the AuditAgent.

    Args:
        model: The model string (e.g. "deepseek/deepseek-chat").

    Returns:
        A configured LlmAgent.
    """
    return LlmAgent(
        name="audit_agent",
        description="Agent responsible for auditing and logging consent actions for compliance purposes",
        model=model,
        instruction=AUDIT_INSTRUCTION,
        tools=[audit_action],
        before_model_callback=log_llm_request,
        after_model_callback=log_llm_response,
    )

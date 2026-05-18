import asyncio
import uuid

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from consent_adk_demo.agents.sequential_agent import create_sequential_agent
from consent_adk_demo.config.settings import MODEL_NAME


SAMPLE_PROMPTS = [
    # Valid: create consent
    "Create a consent with below information:\n1. mac id: 1234567\n2. consent type: MR\n3. channel: BB",
    # Valid: revoke consent
    "Revoke consent for mac id 7654321, consent type RR, channel PB",
    # Invalid: mac_id too short
    "Create a consent with mac id 123, consent type MR, channel BB",
    # Invalid: bad consent type
    "Create a consent with mac id 1234567, consent type XX, channel BB",
    # Invalid: missing channel
    "Create a consent with mac id 1234567 and consent type MR",
]


async def run_prompt(prompt: str, session_service: InMemorySessionService) -> None:
    agent = create_sequential_agent(MODEL_NAME)
    runner = Runner(
        agent=agent,
        app_name="consent_adk_demo",
        session_service=session_service,
        auto_create_session=True,
    )

    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)],
    )

    print(f"\n{'=' * 60}")
    print(f"PROMPT: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
    print(f"{'=' * 60}")

    session_id = str(uuid.uuid4())

    async for event in runner.run_async(
        user_id="demo_user",
        session_id=session_id,
        new_message=user_content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.function_call:
                    print(f"  [TOOL CALL] {part.function_call.name}({part.function_call.args})")
                elif part.function_response:
                    resp = part.function_response.response
                    if isinstance(resp, dict):
                        print(f"  [TOOL RESULT] {resp}")
                    else:
                        print(f"  [TOOL RESULT] {resp}")
                elif part.text and event.author != "user":
                    print(f"  [{event.author}] {part.text}")

    print(f"{'=' * 60}")


async def main() -> None:
    session_service = InMemorySessionService()
    for prompt in SAMPLE_PROMPTS:
        await run_prompt(prompt, session_service)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import os
import uuid

import pytest

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from consent_adk_demo.agents.sequential_agent import create_sequential_agent
from consent_adk_demo.config.settings import MODEL_NAME


def _requires_api_key():
    """Skip test if DEEPSEEK_API_KEY is not set."""
    if not os.environ.get("DEEPSEEK_API_KEY"):
        pytest.skip("DEEPSEEK_API_KEY not set")


async def _run_agent_and_collect(prompt: str) -> tuple[list[str], list[str], list[str]]:
    """Run the agent with a prompt and collect tool calls, text responses, and tool results.

    Returns:
        Tuple of (tool_calls, text_responses, tool_results).
    """
    agent = create_sequential_agent(MODEL_NAME)
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name="consent_adk_demo_eval",
        session_service=session_service,
        auto_create_session=True,
    )

    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)],
    )

    tool_calls: list[str] = []
    text_responses: list[str] = []
    tool_results: list[str] = []

    async for event in runner.run_async(
        user_id="eval_user",
        session_id=str(uuid.uuid4()),
        new_message=user_content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.function_call:
                    tool_calls.append(part.function_call.name)
                elif part.function_response:
                    resp = part.function_response.response
                    if isinstance(resp, dict):
                        tool_results.append(resp.get("message", str(resp)))
                    else:
                        tool_results.append(str(resp))
                elif part.text and event.author != "user":
                    text_responses.append(part.text)

    return tool_calls, text_responses, tool_results


class TestValidCreateConsentEval:
    def test_calls_create_consent_not_revoke(self):
        _requires_api_key()
        tool_calls, _, _ = asyncio.run(
            _run_agent_and_collect(
                "Create a consent with mac id 1234567, consent type MR, channel BB"
            )
        )
        assert "create_consent" in tool_calls, f"Expected create_consent tool call, got: {tool_calls}"
        assert "revoke_consent" not in tool_calls, "revoke_consent should not be called"

    def test_final_response_confirms_creation(self):
        _requires_api_key()
        tool_calls, texts, tool_results = asyncio.run(
            _run_agent_and_collect(
                "Create a consent with mac id 1234567, consent type MR, channel BB"
            )
        )
        assert "create_consent" in tool_calls
        all_text = " ".join(texts + tool_results).lower()
        assert any(word in all_text for word in ["created", "create"]), \
            f"Response should confirm consent creation, got: {all_text[:200]}"


class TestValidRevokeConsentEval:
    def test_calls_revoke_consent_not_create(self):
        _requires_api_key()
        tool_calls, _, _ = asyncio.run(
            _run_agent_and_collect(
                "Revoke consent with mac id 7654321, consent type RR, channel PB"
            )
        )
        assert "revoke_consent" in tool_calls, f"Expected revoke_consent tool call, got: {tool_calls}"
        assert "create_consent" not in tool_calls, "create_consent should not be called"

    def test_final_response_confirms_revocation(self):
        _requires_api_key()
        tool_calls, texts, tool_results = asyncio.run(
            _run_agent_and_collect(
                "Revoke consent with mac id 7654321, consent type RR, channel PB"
            )
        )
        assert "revoke_consent" in tool_calls
        all_text = " ".join(texts + tool_results).lower()
        assert any(word in all_text for word in ["revoked", "revoke"]), \
            f"Response should confirm consent revocation, got: {all_text[:200]}"


class TestInvalidMacIdEval:
    def test_no_consent_tool_called(self):
        _requires_api_key()
        tool_calls, _, _ = asyncio.run(
            _run_agent_and_collect(
                "Create a consent with mac id 123, consent type MR, channel BB"
            )
        )
        assert not tool_calls, f"No consent tools should be called on invalid input, got: {tool_calls}"

    def test_response_explains_mac_id_issue(self):
        _requires_api_key()
        tool_calls, texts, _ = asyncio.run(
            _run_agent_and_collect(
                "Create a consent with mac id 123, consent type MR, channel BB"
            )
        )
        assert not tool_calls
        all_text = " ".join(texts).lower()
        assert "7" in all_text or "seven" in all_text or "digit" in all_text or "mac_id" in all_text.replace(" ", "") or "mac id" in all_text, \
            f"Response should explain mac_id must be 7 digits, got: {all_text[:200]}"


class TestInvalidConsentTypeEval:
    def test_no_consent_tool_called(self):
        _requires_api_key()
        tool_calls, _, _ = asyncio.run(
            _run_agent_and_collect(
                "Create a consent with mac id 1234567, consent type XX, channel BB"
            )
        )
        assert not tool_calls, f"No consent tools should be called on invalid input, got: {tool_calls}"

    def test_response_explains_consent_type_issue(self):
        _requires_api_key()
        tool_calls, texts, _ = asyncio.run(
            _run_agent_and_collect(
                "Create a consent with mac id 1234567, consent type XX, channel BB"
            )
        )
        assert not tool_calls
        all_text = " ".join(texts).lower()
        assert "mr" in all_text or "rr" in all_text or "rp" in all_text or "consent_type" in all_text.replace(" ", "") or "consent type" in all_text, \
            f"Response should explain valid consent_type options, got: {all_text[:200]}"


class TestMissingChannelEval:
    def test_no_consent_tool_called(self):
        _requires_api_key()
        tool_calls, _, _ = asyncio.run(
            _run_agent_and_collect(
                "Create a consent with mac id 1234567 and consent type MR"
            )
        )
        assert not tool_calls, f"No consent tools should be called on invalid input, got: {tool_calls}"

    def test_response_explains_channel_required(self):
        _requires_api_key()
        tool_calls, texts, _ = asyncio.run(
            _run_agent_and_collect(
                "Create a consent with mac id 1234567 and consent type MR"
            )
        )
        assert not tool_calls
        all_text = " ".join(texts).lower()
        assert "channel" in all_text or "bb" in all_text or "pb" in all_text, \
            f"Response should explain channel is required, got: {all_text[:200]}"

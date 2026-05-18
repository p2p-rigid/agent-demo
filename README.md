# Consent ADK Demo

A Google ADK (Agent Development Kit) startup project demonstrating a sequential agent workflow for consent management.

## What It Does

Accepts natural language consent management requests ("create consent", "revoke consent"), validates the request fields, and executes the appropriate action via mock tools.

## Sequential Agent Flow

```
User Prompt
    |
    v
Agent 1: UserIntentValidator
    |  Parses the request, extracts mac_id, consent_type, channel
    |  Validates all fields against business rules
    |  Outputs structured validation_result to session state
    v
Agent 2: ConsentActionAgent
    |  Reads validation_result from session state
    |  If valid: calls create_consent or revoke_consent tool
    |  If invalid: returns validation errors (no tools called)
    v
Final Response
```

## Prerequisites

- Python 3.12+
- DeepSeek API key

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Set your DeepSeek API key in `.env`:
   ```
   DEEPSEEK_API_KEY=sk-...
   ```

   The project uses LiteLLM under the hood. The model string `deepseek/deepseek-chat` is routed to the DeepSeek provider. The `DEEPSEEK_API_KEY` environment variable is automatically picked up by LiteLLM for authentication.

## Install Dependencies

```bash
pip install -e ".[dev]"
```

## Run the App

```bash
python -m consent_adk_demo.main
```

This runs five sample prompts through the sequential agent flow:
- 2 valid prompts (create and revoke consent)
- 3 invalid prompts (bad mac_id, bad consent_type, missing channel)

## Run Unit Tests

```bash
pytest tests/unit -v
```

## Run Eval Tests

Eval tests require a valid `DEEPSEEK_API_KEY` environment variable. They are skipped otherwise.

```bash
pytest tests/eval -v
```

## Log LLM Requests and Responses

Enable ADK model callbacks to write complete LLM request and response payloads to JSON Lines:

```bash
LOG_LLM_IO=true python -m consent_adk_demo.main
```

By default, logs are written to `logs/llm_io.jsonl`. To choose another file:

```bash
LOG_LLM_IO=true LLM_IO_LOG_PATH=logs/my_run.jsonl python -m consent_adk_demo.main
```

These logs can include user prompts, system instructions, tool schemas, tool calls, and model responses. Do not enable them for sensitive production traffic unless you have an appropriate retention and redaction policy.

## Example Prompts

**Valid:**
- `Create a consent with mac id 1234567, consent type MR, channel BB`
- `Revoke consent with mac id 7654321, consent type RR, channel PB`

**Invalid:**
- `Create a consent with mac id 123, consent type MR, channel BB` (mac_id too short)
- `Create a consent with mac id 1234567, consent type XX, channel BB` (invalid consent_type)
- `Create a consent with mac id 1234567 and consent type MR` (missing channel)

## Project Structure

```
consent-adk-demo/
  README.md
  pyproject.toml
  .env.example
  src/
    consent_adk_demo/
      __init__.py
      main.py
      agents/
        __init__.py
        user_intent_validator.py
        consent_action_agent.py
        sequential_agent.py
      tools/
        __init__.py
        consent_tools.py
      config/
        __init__.py
        settings.py
  tests/
    unit/
      test_consent_tools.py
    eval/
      test_consent_agent_eval.py
```

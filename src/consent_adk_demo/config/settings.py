import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
load_dotenv(Path(__file__).parents[1] / ".env")

DEEPSEEK_API_KEY: str | None = os.environ.get("DEEPSEEK_API_KEY")
MODEL_NAME: str = os.environ.get("MODEL_NAME", "deepseek/deepseek-v4-pro")
LOG_LLM_IO: bool = os.environ.get("LOG_LLM_IO", "").lower() in {"1", "true", "yes", "on"}
LLM_IO_LOG_PATH: str = os.environ.get("LLM_IO_LOG_PATH", "logs/llm_io.jsonl")

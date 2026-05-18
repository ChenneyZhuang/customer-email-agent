"""Configuration management via environment variables and .env file."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the current working directory (or parent chain)
load_dotenv()


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default)


DEEPSEEK_API_KEY: str = _env("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL: str = _env("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL: str = _env("DEEPSEEK_MODEL", "deepseek-chat")

OUTPUT_DIR: Path = Path(_env("EMAIL_AGENT_OUTPUT_DIR", "./output"))

# Ensure output directory exists on import
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def validate() -> None:
    """Raise RuntimeError if required config is missing."""
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "sk-your-key-here":
        raise RuntimeError(
            "DEEPSEEK_API_KEY is not set. Copy .env.example to .env and fill in your key."
        )

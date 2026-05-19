"""Thin wrapper around the DeepSeek chat-completions API (OpenAI-compatible)."""

from __future__ import annotations

import json
from typing import Any

import httpx

from email_agent import config


class LLMClient:
    """Minimal client for the DeepSeek chat API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or config.DEEPSEEK_API_KEY
        self.base_url = (base_url or config.DEEPSEEK_BASE_URL).rstrip("/")
        self.model = model or config.DEEPSEEK_MODEL

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a chat completion request and return the parsed JSON response.

        Parameters
        ----------
        messages : list[dict]
            Standard chat messages with 'role' and 'content'.
        temperature : float
            Sampling temperature (keep low for structured outputs).
        max_tokens : int
            Maximum tokens in the response.
        response_format : dict or None
            If ``{"type": "json_object"}``, the API will return valid JSON.

        Returns
        -------
        dict
            The decoded JSON response body from the API.

        Raises
        ------
        RuntimeError
            If the API returns a non-OK status or the response cannot be parsed as JSON.
        """
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()

        data = resp.json()
        content: str = data["choices"][0]["message"]["content"]
        # Parse JSON; raise if malformed
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise RuntimeError(
                f"LLM returned non-JSON response despite json_object format: {content[:200]}"
            )

    def chat_raw(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Return the raw text response from the API (no JSON parsing)."""
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.2),
            "max_tokens": kwargs.get("max_tokens", 2048),
        }
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload,
            )
            resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


# Module-level convenience instance (requires .env to be loaded)
_client: LLMClient | None = None


def get_client() -> LLMClient:
    """Return a reusable LLMClient singleton."""
    global _client
    if _client is None:
        config.validate()
        _client = LLMClient()
    return _client

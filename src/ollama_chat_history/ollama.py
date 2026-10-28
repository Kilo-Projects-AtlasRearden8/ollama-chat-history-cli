"""Client for the Ollama HTTP API.

Talks to a locally running Ollama server (default http://127.0.0.1:11434).
This tool never sends chat data anywhere except your own Ollama instance and
the local JSON store on your machine.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Iterable

DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_TIMEOUT = 30


class OllamaError(RuntimeError):
    """Raised when the Ollama server cannot be reached or returns an error."""


@dataclass(frozen=True)
class ChatSummary:
    """Lightweight description of a stored chat."""

    chat_id: str
    title: str
    model: str
    created_at: str
    updated_at: str
    message_count: int


@dataclass(frozen=True)
class Chat:
    """A full chat record, messages included."""

    chat_id: str
    title: str
    model: str
    created_at: str
    updated_at: str
    messages: list[dict[str, str]]


def _get_json(base_url: str, path: str, timeout: float = DEFAULT_TIMEOUT) -> Any:
    url = base_url.rstrip("/") + path
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read()
    except urllib.error.URLError as exc:  # pragma: no cover - network failure
        raise OllamaError(f"cannot reach Ollama at {url}: {exc}") from exc
    except Exception as exc:  # pragma: no cover - unexpected network failure
        raise OllamaError(f"cannot reach Ollama at {url}: {exc}") from exc
    try:
        return json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise OllamaError(f"invalid JSON from Ollama at {url}: {exc}") from exc


class OllamaClient:
    """Minimal client for the Ollama endpoints this tool needs."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def list_models(self) -> list[str]:
        """Return the model names available on the server."""
        data = _get_json(self.base_url, "/api/tags", self.timeout)
        models = data.get("models", []) if isinstance(data, dict) else []
        names: list[str] = []
        for model in models:
            if isinstance(model, dict):
                name = model.get("name")
                if name:
                    names.append(str(name))
        return names

    def list_chats(self) -> list[ChatSummary]:
        """Return summaries of every chat stored on the server."""
        data = _get_json(self.base_url, "/api/chats", self.timeout)
        raw_chats = data.get("chats", []) if isinstance(data, dict) else []
        summaries: list[ChatSummary] = []
        for item in raw_chats:
            if not isinstance(item, dict):
                continue
            summaries.append(
                ChatSummary(
                    chat_id=str(item.get("id", "")),
                    title=str(item.get("title", "")),
                    model=str(item.get("model", "")),
                    created_at=str(item.get("created_at", "")),
                    updated_at=str(item.get("updated_at", "")),
                    message_count=int(item.get("message_count", 0)),
                )
            )
        return summaries

    def get_chat(self, chat_id: str) -> Chat:
        """Return the full chat record for ``chat_id``."""
        data = _get_json(
            self.base_url, f"/api/chats/{chat_id}", self.timeout
        )
        if not isinstance(data, dict):
            raise OllamaError(f"unexpected chat payload for {chat_id}")
        messages: list[dict[str, str]] = []
        for message in data.get("messages", []) or []:
            if isinstance(message, dict):
                messages.append(
                    {
                        "role": str(message.get("role", "")),
                        "content": str(message.get("content", "")),
                    }
                )
        return Chat(
            chat_id=str(data.get("id", chat_id)),
            title=str(data.get("title", "")),
            model=str(data.get("model", "")),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
            messages=messages,
        )

    def fetch_all(self) -> list[Chat]:
        """Fetch every chat stored on the server, messages included."""
        return [self.get_chat(s.chat_id) for s in self.list_chats()]

"""Mock Ollama HTTP server for tests.

Serves the endpoints the OllamaClient consumes (/api/tags, /api/chats,
/api/chats/{id}) from an in-memory dataset. Runs on localhost in a
background thread so tests stay local-first with no network dependency.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


class MockOllamaHandler(BaseHTTPRequestHandler):
    """Handler whose class-level DATA drives responses."""

    DATA: dict[str, Any] = {}

    def log_message(self, fmt: str, *args: Any) -> None:  # quiet in tests
        return

    def _send(self, status: int, payload: Any) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - http.server override
        path = self.path.split("?")[0].rstrip("/")
        if path == "/api/tags":
            self._send(200, {"models": self.DATA.get("models", [])})
            return
        if path == "/api/chats":
            self._send(200, {"chats": self.DATA.get("chats", [])})
            return
        if path.startswith("/api/chats/"):
            chat_id = path[len("/api/chats/") :]
            for chat in self.DATA.get("chats", []):
                if chat.get("id") == chat_id:
                    self._send(200, chat)
                    return
            self._send(404, {"error": "chat not found"})
            return
        self._send(404, {"error": "not found"})


class MockOllamaServer:
    def __init__(self, data: dict[str, Any]) -> None:
        MockOllamaHandler.DATA = data
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), MockOllamaHandler)
        self.port = self.server.server_address[1]
        self.base_url = f"http://127.0.0.1:{self.port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def shutdown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


SAMPLE_CHATS: dict[str, Any] = {
    "models": [
        {"name": "llama3.2:latest", "modified_at": "2026-10-01T00:00:00Z"},
        {"name": "qwen2.5:3b", "modified_at": "2026-10-02T00:00:00Z"},
    ],
    "chats": [
        {
            "id": "chat-1",
            "title": "Python project ideas",
            "model": "llama3.2:latest",
            "created_at": "2026-10-01T09:00:00",
            "updated_at": "2026-10-01T09:30:00",
            "message_count": 2,
            "messages": [
                {"role": "user", "content": "Give me beginner Python project ideas."},
                {"role": "assistant", "content": "Try a number-guessing game or a todo list."},
            ],
        },
        {
            "id": "chat-2",
            "title": "Ollama local AI setup",
            "model": "qwen2.5:3b",
            "created_at": "2026-10-05T10:00:00",
            "updated_at": "2026-10-05T10:15:00",
            "message_count": 1,
            "messages": [
                {"role": "user", "content": "How do I run Ollama offline?"},
            ],
        },
        {
            "id": "chat-3",
            "title": "Weekly review notes",
            "model": "llama3.2:latest",
            "created_at": "2026-10-12T08:00:00",
            "updated_at": "2026-10-12T17:00:00",
            "message_count": 3,
            "messages": [
                {"role": "user", "content": "Summarize my weekly notes."},
                {"role": "assistant", "content": "You shipped the CLI tool and wrote tests."},
                {"role": "user", "content": "Thanks!"},
            ],
        },
    ],
}

"""Tests for Markdown export."""

from __future__ import annotations

import os

from ollama_chat_history.export import export_markdown, render_markdown
from ollama_chat_history.storage import ChatRecord


def test_render_markdown_empty():
    output = render_markdown([], title="History")
    assert "# History" in output
    assert "0 chat(s) exported" in output


def test_render_markdown_with_records():
    records = [
        ChatRecord(
            "c1",
            "Python ideas",
            "llama3",
            "2026-10-01T09:00:00",
            "2026-10-01T09:30:00",
            [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}],
        )
    ]
    output = render_markdown(records)
    assert "## 1. Python ideas" in output
    assert "**Model:** llama3" in output
    assert "**user:** hello" in output
    assert "**assistant:** hi" in output


def test_export_markdown_writes_file(tmp_path):
    out = tmp_path / "chats.md"
    records = [
        ChatRecord("c1", "Chat one", "m", "2026-10-01", "2026-10-01", [])
    ]
    export_markdown(records, str(out))
    assert os.path.exists(out)
    content = out.read_text(encoding="utf-8")
    assert "Chat one" in content

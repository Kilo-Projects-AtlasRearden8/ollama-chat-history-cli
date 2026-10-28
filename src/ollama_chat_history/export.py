"""Markdown export for chat records."""

from __future__ import annotations

import os
from typing import Iterable

from .storage import ChatRecord


def _format_message(message: dict[str, str]) -> str:
    role = message.get("role", "unknown")
    content = message.get("content", "")
    return f"**{role}:** {content}"


def render_markdown(records: Iterable[ChatRecord], title: str = "Ollama Chat History") -> str:
    """Render chat records as a Markdown string."""
    records = list(records)
    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"{len(records)} chat(s) exported.")
    lines.append("")
    lines.append("---")
    lines.append("")

    if not records:
        lines.append("*No chats matched the export criteria.*")
        return "\n".join(lines) + "\n"

    for index, record in enumerate(records, start=1):
        lines.append(f"## {index}. {record.title or 'Untitled chat'}")
        lines.append("")
        lines.append(f"- **Chat ID:** {record.chat_id}")
        lines.append(f"- **Model:** {record.model or 'unknown'}")
        lines.append(f"- **Created:** {record.created_at}")
        lines.append(f"- **Updated:** {record.updated_at}")
        lines.append(f"- **Messages:** {len(record.messages)}")
        lines.append("")
        if record.messages:
            lines.append("### Messages")
            lines.append("")
            for message in record.messages:
                lines.append(_format_message(message))
                lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def export_markdown(records: Iterable[ChatRecord], path: str, title: str = "Ollama Chat History") -> str:
    """Render ``records`` as Markdown and write them to ``path``."""
    content = render_markdown(records, title=title)
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    return content


__all__ = ["render_markdown", "export_markdown"]

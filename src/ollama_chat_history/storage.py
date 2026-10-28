"""Local JSON storage for fetched Ollama chats."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

from .ollama import Chat


@dataclass
class ChatRecord:
    """In-memory representation of a stored chat (JSON serializable)."""

    chat_id: str
    title: str
    model: str
    created_at: str
    updated_at: str
    messages: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ChatRecord":
        return ChatRecord(
            chat_id=str(data.get("chat_id", "")),
            title=str(data.get("title", "")),
            model=str(data.get("model", "")),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
            messages=list(data.get("messages", [])),
        )


class ChatStore:
    """Persists chat records to a single local JSON file."""

    def __init__(self, path: str) -> None:
        self.path = path

    def _read_raw(self) -> list[dict[str, Any]]:
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(data, list):
            return []
        return [item for item in data if isinstance(item, dict)]

    def load(self) -> list[ChatRecord]:
        return [ChatRecord.from_dict(item) for item in self._read_raw()]

    def save(self, records: Iterable[ChatRecord]) -> None:
        records = list(records)
        directory = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(directory, exist_ok=True)
        tmp_path = self.path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as handle:
            json.dump([record.to_dict() for record in records], handle, indent=2)
        os.replace(tmp_path, self.path)

    def merge(self, records: Iterable[ChatRecord]) -> list[ChatRecord]:
        """Merge ``records`` into the store, replacing existing chat_ids."""
        existing = {record.chat_id: record for record in self.load()}
        for record in records:
            existing[record.chat_id] = record
        merged = list(existing.values())
        merged.sort(key=lambda record: record.updated_at or record.created_at)
        self.save(merged)
        return merged

    def clear(self) -> None:
        if os.path.exists(self.path):
            os.remove(self.path)

    def by_id(self, chat_id: str) -> ChatRecord | None:
        for record in self.load():
            if record.chat_id == chat_id:
                return record
        return None


__all__ = ["ChatRecord", "ChatStore"]

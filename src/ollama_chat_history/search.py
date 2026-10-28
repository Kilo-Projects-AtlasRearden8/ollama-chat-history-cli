"""Filtering for chat records: keywords, date ranges, model."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from .storage import ChatRecord


def _parse_date(value: str) -> date | None:
    """Parse an ISO date or datetime string, returning the date portion."""
    value = value.strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


def _text_matches(text: str, keyword: str) -> bool:
    return keyword.lower() in text.lower()


def filter_chats(
    records: Iterable[ChatRecord],
    keyword: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    model: str | None = None,
) -> list[ChatRecord]:
    """Return records matching all provided filters.

    - keyword: case-insensitive substring match against title and message content
    - date_from / date_to: inclusive ISO date boundaries (YYYY-MM-DD)
    - model: exact model name match
    """
    results: list[ChatRecord] = []
    from_date = _parse_date(date_from) if date_from else None
    to_date = _parse_date(date_to) if date_to else None

    for record in records:
        if model is not None and record.model != model:
            continue

        if date_from or date_to:
            stamp = record.updated_at or record.created_at
            record_date = _parse_date(stamp)
            if record_date is None:
                continue
            if from_date is not None and record_date < from_date:
                continue
            if to_date is not None and record_date > to_date:
                continue

        if keyword is not None:
            haystack = " ".join([record.title] + [m.get("content", "") for m in record.messages])
            if not _text_matches(haystack, keyword):
                continue

        results.append(record)

    return results

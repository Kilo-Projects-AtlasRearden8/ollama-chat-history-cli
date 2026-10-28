"""Tests for chat filtering."""

from __future__ import annotations

from ollama_chat_history.search import filter_chats
from ollama_chat_history.storage import ChatRecord


def _record(chat_id, title, model, updated_at, content=""):
    return ChatRecord(
        chat_id=chat_id,
        title=title,
        model=model,
        created_at=updated_at,
        updated_at=updated_at,
        messages=[{"role": "user", "content": content}],
    )


def test_keyword_filter():
    records = [
        _record("1", "Python ideas", "llama3", "2026-10-01", "beginner python projects"),
        _record("2", "Ollama setup", "qwen", "2026-10-02", "run ollama offline"),
    ]
    results = filter_chats(records, keyword="python")
    assert len(results) == 1
    assert results[0].chat_id == "1"


def test_keyword_case_insensitive():
    records = [_record("1", "Python ideas", "llama3", "2026-10-01", "hello")]
    assert len(filter_chats(records, keyword="PYTHON")) == 1


def test_date_range():
    records = [
        _record("1", "A", "m", "2026-10-01"),
        _record("2", "B", "m", "2026-10-05"),
        _record("3", "C", "m", "2026-10-12"),
    ]
    results = filter_chats(records, date_from="2026-10-02", date_to="2026-10-10")
    assert [r.chat_id for r in results] == ["2"]


def test_date_range_inclusive():
    records = [
        _record("1", "A", "m", "2026-10-01"),
        _record("2", "B", "m", "2026-10-05"),
    ]
    results = filter_chats(records, date_from="2026-10-01", date_to="2026-10-05")
    assert len(results) == 2


def test_model_filter():
    records = [
        _record("1", "A", "llama3", "2026-10-01"),
        _record("2", "B", "qwen", "2026-10-02"),
    ]
    results = filter_chats(records, model="qwen")
    assert [r.chat_id for r in results] == ["2"]


def test_combined_filters():
    records = [
        _record("1", "Python ideas", "llama3", "2026-10-01", "python stuff"),
        _record("2", "Python notes", "llama3", "2026-10-05", "more python"),
        _record("3", "Ollama setup", "qwen", "2026-10-05", "python"),
    ]
    results = filter_chats(
        records, keyword="python", model="llama3", date_from="2026-10-01"
    )
    assert sorted(r.chat_id for r in results) == ["1", "2"]

"""Tests for the local JSON chat store."""

from __future__ import annotations

import pytest

from ollama_chat_history.storage import ChatRecord, ChatStore


def test_save_and_load(store):
    records = [
        ChatRecord("c1", "One", "llama3", "2026-01-01T00:00:00", "2026-01-01T00:00:00"),
        ChatRecord("c2", "Two", "qwen", "2026-01-02T00:00:00", "2026-01-02T00:00:00"),
    ]
    store.save(records)
    loaded = store.load()
    assert len(loaded) == 2
    assert loaded[0].chat_id == "c1"
    assert loaded[1].model == "qwen"


def test_merge_replaces_and_keeps_others(store):
    store.save([ChatRecord("c1", "One", "m", "2026-01-01", "2026-01-01")])
    merged = store.merge(
        [
            ChatRecord("c1", "One updated", "m", "2026-01-01", "2026-01-02"),
            ChatRecord("c2", "Two", "m", "2026-01-03", "2026-01-03"),
        ]
    )
    ids = {r.chat_id for r in merged}
    assert ids == {"c1", "c2"}
    by_id = {r.chat_id: r for r in merged}
    assert by_id["c1"].title == "One updated"


def test_by_id(store):
    store.save([ChatRecord("c1", "One", "m", "2026-01-01", "2026-01-01")])
    assert store.by_id("c1").title == "One"
    assert store.by_id("missing") is None


def test_empty_store_returns_empty_list(tmp_path):
    path = tmp_path / "empty.json"
    store = ChatStore(str(path))
    assert store.load() == []


def test_remove(store):
    store.save(
        [
            ChatRecord("c1", "One", "m", "2026-01-01", "2026-01-01"),
            ChatRecord("c2", "Two", "m", "2026-01-02", "2026-01-02"),
        ]
    )
    assert store.remove("c1") is True
    assert store.by_id("c1") is None
    assert store.by_id("c2") is not None
    assert store.remove("missing") is False


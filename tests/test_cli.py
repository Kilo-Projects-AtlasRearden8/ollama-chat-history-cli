"""Tests for the CLI using a temp store and the mock Ollama server."""

from __future__ import annotations

import json
import os

from ollama_chat_history.cli import main
from ollama_chat_history.storage import ChatRecord
from tests.mock_server import MockOllamaServer, SAMPLE_CHATS


def _run(global_flags, command_args, capsys, store_path):
    argv = list(global_flags) + ["--store", store_path] + list(command_args)
    code = main(argv)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def _write_store(store, records):
    with open(store, "w", encoding="utf-8") as handle:
        json.dump(
            [
                {
                    "chat_id": r.chat_id,
                    "title": r.title,
                    "model": r.model,
                    "created_at": r.created_at,
                    "updated_at": r.updated_at,
                    "messages": r.messages,
                }
                for r in records
            ],
            handle,
        )


def test_sync(tmp_path, capsys):
    server = MockOllamaServer(dict(SAMPLE_CHATS))
    try:
        store = str(tmp_path / "chats.json")
        code, out, err = _run(["--url", server.base_url], ["sync"], capsys, store)
    finally:
        server.shutdown()
    assert code == 0, err
    assert "Synced 3 chat(s)" in out
    with open(store, encoding="utf-8") as handle:
        records = json.load(handle)
    assert len(records) == 3
    # Full records are fetched by default: messages are present.
    assert len(records[0]["messages"]) == 2
    assert records[0]["messages"][0]["content"].startswith("Give me")


def test_list_empty(tmp_path, capsys):
    store = str(tmp_path / "chats.json")
    code, out, err = _run([], ["list"], capsys, store)
    assert code == 0, err
    assert "No matching chats." in out


def test_list_and_search(tmp_path, capsys):
    store = str(tmp_path / "chats.json")
    _write_store(
        store,
        [
            ChatRecord(
                "c1",
                "Python ideas",
                "llama3",
                "2026-10-01T09:00",
                "2026-10-01T09:30",
                [{"role": "user", "content": "hello python"}],
            )
        ],
    )

    code, out, err = _run([], ["list"], capsys, store)
    assert code == 0, err
    assert "Python ideas" in out

    code, out, err = _run([], ["search", "--keyword", "python"], capsys, store)
    assert code == 0, err
    assert "Python ideas" in out

    code, out, err = _run([], ["search", "--keyword", "ruby"], capsys, store)
    assert code == 0, err
    assert "No matching chats." in out


def test_show(tmp_path, capsys):
    store = str(tmp_path / "chats.json")
    _write_store(
        store,
        [
            ChatRecord(
                "c1",
                "Python ideas",
                "llama3",
                "2026-10-01T09:00",
                "2026-10-01T09:30",
                [{"role": "user", "content": "hello python"}],
            )
        ],
    )

    code, out, err = _run([], ["show", "c1"], capsys, store)
    assert code == 0, err
    assert "Python ideas" in out
    assert "user: hello python" in out

    code, out, err = _run([], ["show", "missing"], capsys, store)
    assert code == 1, err
    assert "not found" in err


def test_delete(tmp_path, capsys):
    store = str(tmp_path / "chats.json")
    _write_store(
        store,
        [
            ChatRecord("c1", "One", "m", "2026-10-01", "2026-10-01", []),
            ChatRecord("c2", "Two", "m", "2026-10-02", "2026-10-02", []),
        ],
    )

    code, out, err = _run([], ["delete", "c1"], capsys, store)
    assert code == 0, err
    assert "Deleted chat c1" in out

    code, out, err = _run([], ["list"], capsys, store)
    assert code == 0, err
    assert "Two" in out
    assert "One" not in out

    code, out, err = _run([], ["delete", "missing"], capsys, store)
    assert code == 1, err


def test_export(tmp_path, capsys):
    store = str(tmp_path / "chats.json")
    out_path = str(tmp_path / "out.md")
    _write_store(
        store,
        [
            ChatRecord(
                "c1",
                "Python ideas",
                "llama3",
                "2026-10-01T09:00",
                "2026-10-01T09:30",
                [],
            )
        ],
    )

    code, out, err = _run([], ["export", "--output", out_path], capsys, store)
    assert code == 0, err
    assert os.path.exists(out_path)
    content = open(out_path, encoding="utf-8").read()
    assert "# Ollama Chat History" in content
    assert "Python ideas" in content

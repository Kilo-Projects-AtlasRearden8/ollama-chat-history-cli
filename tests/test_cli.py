"""Tests for the CLI using a temp store and the mock Ollama server."""

from __future__ import annotations

import json
import os

from ollama_chat_history.cli import main
from tests.mock_server import MockOllamaServer, SAMPLE_CHATS


def _run(global_flags, command_args, capsys, store_path):
    argv = list(global_flags) + ["--store", store_path] + list(command_args)
    code = main(argv)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_sync(tmp_path, capsys):
    server = MockOllamaServer(dict(SAMPLE_CHATS))
    try:
        store = str(tmp_path / "chats.json")
        code, out, err = _run(["--url", server.base_url], ["sync", "--all"], capsys, store)
    finally:
        server.shutdown()
    assert code == 0, err
    assert "Synced 3 chat(s)" in out
    with open(store, encoding="utf-8") as handle:
        records = json.load(handle)
    assert len(records) == 3


def test_list_empty(tmp_path, capsys):
    store = str(tmp_path / "chats.json")
    code, out, err = _run([], ["list"], capsys, store)
    assert code == 0, err
    assert "No matching chats." in out


def test_list_and_search(tmp_path, capsys):
    store = str(tmp_path / "chats.json")
    with open(store, "w", encoding="utf-8") as handle:
        json.dump(
            [
                {
                    "chat_id": "c1",
                    "title": "Python ideas",
                    "model": "llama3",
                    "created_at": "2026-10-01T09:00",
                    "updated_at": "2026-10-01T09:30",
                    "messages": [{"role": "user", "content": "hello python"}],
                }
            ],
            handle,
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


def test_export(tmp_path, capsys):
    store = str(tmp_path / "chats.json")
    out_path = str(tmp_path / "out.md")
    with open(store, "w", encoding="utf-8") as handle:
        json.dump(
            [
                {
                    "chat_id": "c1",
                    "title": "Python ideas",
                    "model": "llama3",
                    "created_at": "2026-10-01T09:00",
                    "updated_at": "2026-10-01T09:30",
                    "messages": [],
                }
            ],
            handle,
        )

    code, out, err = _run([], ["export", "--output", out_path], capsys, store)
    assert code == 0, err
    assert os.path.exists(out_path)
    content = open(out_path, encoding="utf-8").read()
    assert "# Ollama Chat History" in content
    assert "Python ideas" in content

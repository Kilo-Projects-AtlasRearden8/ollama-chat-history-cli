"""Tests for the Ollama client against the mock server."""

from __future__ import annotations

import pytest

from ollama_chat_history.ollama import OllamaClient, OllamaError
from tests.mock_server import SAMPLE_CHATS


def test_list_models(mock_server):
    client = OllamaClient(base_url=mock_server.base_url)
    models = client.list_models()
    assert models == [m["name"] for m in SAMPLE_CHATS["models"]]


def test_list_chats(mock_server):
    client = OllamaClient(base_url=mock_server.base_url)
    summaries = client.list_chats()
    assert len(summaries) == len(SAMPLE_CHATS["chats"])
    assert summaries[0].chat_id == "chat-1"
    assert summaries[0].title == "Python project ideas"
    assert summaries[0].message_count == 2


def test_get_chat(mock_server):
    client = OllamaClient(base_url=mock_server.base_url)
    chat = client.get_chat("chat-3")
    assert chat.chat_id == "chat-3"
    assert chat.title == "Weekly review notes"
    assert chat.model == "llama3.2:latest"
    assert len(chat.messages) == 3
    assert chat.messages[0]["role"] == "user"


def test_get_chat_unknown(mock_server):
    client = OllamaClient(base_url=mock_server.base_url)
    with pytest.raises(OllamaError):
        client.get_chat("does-not-exist")


def test_fetch_all(mock_server):
    client = OllamaClient(base_url=mock_server.base_url)
    chats = client.fetch_all()
    assert len(chats) == 3
    assert all(len(c.messages) >= 1 for c in chats)


def test_unreachable_server():
    client = OllamaClient(base_url="http://127.0.0.1:1", timeout=2)
    with pytest.raises(OllamaError):
        client.list_models()

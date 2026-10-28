"""Pytest fixtures for the mock Ollama server and temp store."""

from __future__ import annotations

import os
import tempfile
from typing import Any

import pytest

from ollama_chat_history.storage import ChatStore
from tests.mock_server import MockOllamaServer, SAMPLE_CHATS


@pytest.fixture
def mock_server() -> MockOllamaServer:
    server = MockOllamaServer(dict(SAMPLE_CHATS))
    yield server
    server.shutdown()


@pytest.fixture
def store_path() -> str:
    fd, path = tempfile.mkstemp(prefix="chats-", suffix=".json")
    os.close(fd)
    yield path
    try:
        os.remove(path)
    except OSError:
        pass


@pytest.fixture
def store(store_path: str) -> ChatStore:
    return ChatStore(store_path)

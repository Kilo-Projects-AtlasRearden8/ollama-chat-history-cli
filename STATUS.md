# STATUS

## What was built

`ollama-chat-history` — a warm, local-first Python CLI for searching, exporting,
and managing Ollama chat history saved as JSON on your own machine. Built for
Asdale Dynamics, LLC (beginner-friendly AI education and practical local-LLM
tools).

Files:
- `src/ollama_chat_history/ollama.py` — Ollama HTTP API client
  (`/api/tags`, `/api/chats`, `/api/chats/{id}`) against
  `http://127.0.0.1:11434` by default
- `src/ollama_chat_history/storage.py` — atomic JSON store (`ChatStore`,
  `ChatRecord`) with merge-by-id and remove
- `src/ollama_chat_history/search.py` — keyword (title + message text), date
  range, and model filtering
- `src/ollama_chat_history/export.py` — Markdown rendering and file export
- `src/ollama_chat_history/cli.py` — argparse CLI: `sync`, `list`, `show`,
  `delete`, `search`, `export`
- `tests/` — 26 tests using a stdlib mock Ollama server (no network, no keys)
- `pyproject.toml` — packaging with `ollama-chat-history` console script
- `LICENSE` — MIT, Copyright (c) 2026 Asdale Dynamics, LLC
- `README.md` — beginner-friendly usage docs, credits Asdale Dynamics, LLC
- `STATUS.md` — this file

## How to run

```bash
pip install -e .                          # installs the ollama-chat-history command
ollama-chat-history --help
ollama-chat-history sync                  # full records (messages) by default
ollama-chat-history list
ollama-chat-history show <chat-id>
ollama-chat-history search --keyword python --from 2026-10-01 --to 2026-10-31
ollama-chat-history export --output chats.md --keyword python
ollama-chat-history delete <chat-id>
```

Local store defaults to `~/.ollama-chat-history/chats.json` (override with
`--store`). Search, export, show, list, and delete work fully offline once chats
are synced.

## Verification

- `python3 -m pytest`: **26 passed** (mock Ollama server, in-memory dataset)
- `python3 -m compileall src tests`: clean
- `pip install -e .`: builds and installs; `ollama-chat-history --help` works
- Entry point: `ollama-chat-history = ollama_chat_history.cli:main`
- Version `0.1.0`
- No `.github/workflows`, no secrets, no API keys, no personal data in files

## Known gaps

- `sync` assumes an Ollama-compatible server exposing `/api/chats` and
  `/api/chats/{id}` (stock Ollama does not expose a chat-history list API);
  validated against the mock server in `tests/mock_server.py`
- Date filtering accepts ISO dates/datetimes (`YYYY-MM-DD` ...); no natural
  language dates
- `delete` removes a chat from the local store only (not from the Ollama
  server); remove the store file to reset everything
- Tested with Python 3.13; targets Python 3.9+

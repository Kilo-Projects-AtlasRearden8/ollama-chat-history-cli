# STATUS

## What was built

`ollama-chat-history` — a local-first Python CLI for searching, exporting, and
managing Ollama chat history saved as JSON on your own machine.

Files:
- `src/ollama_chat_history/ollama.py` — Ollama HTTP API client (`/api/tags`,
  `/api/chats`, `/api/chats/{id}`) against `http://127.0.0.1:11434` by default
- `src/ollama_chat_history/storage.py` — atomic JSON store (`ChatStore`,
  `ChatRecord`) with merge-by-id
- `src/ollama_chat_history/search.py` — keyword (title + message text), date
  range, and model filtering
- `src/ollama_chat_history/export.py` — Markdown rendering and file export
- `src/ollama_chat_history/cli.py` — argparse CLI: `sync`, `list`, `search`,
  `export`
- `tests/` — 23 tests using a stdlib mock Ollama server (no network, no keys)
- `pyproject.toml` — packaging with `ollama-chat-history` console script
- `LICENSE` — MIT, Copyright (c) 2026 Asdale Dynamics, LLC
- `README.md` — usage docs, credits Asdale Dynamics, LLC

## How to run

```bash
pip install -e .                          # installs the ollama-chat-history command
ollama-chat-history --url http://127.0.0.1:11434 sync --all
ollama-chat-history list
ollama-chat-history search --keyword python --from 2026-10-01 --to 2026-10-31
ollama-chat-history export --output chats.md --keyword python
```

Local store defaults to `~/.ollama-chat-history/chats.json` (override with
`--store`). Search and export work fully offline once chats are synced.

## Verification

- `python3 -m pytest`: **23 passed** (mock Ollama server, in-memory dataset)
- `python3 -m compileall src tests`: clean
- `pip install -e .`: builds and installs; `ollama-chat-history --help` works
- Version `0.1.0`, entry point `ollama-chat-history = ollama_chat_history.cli:main`

## Known gaps

- `sync` without `--all` stores summaries only (messages empty); use `--all`
  for full message content
- Date filtering accepts ISO dates/datetimes (`YYYY-MM-DD` ...); no natural
  language dates
- No delete/purge command yet; remove the store file to reset
- No live Ollama server was available in this environment; validation used the
  mock server in `tests/mock_server.py`
- Tested with Python 3.13; targets Python 3.9+

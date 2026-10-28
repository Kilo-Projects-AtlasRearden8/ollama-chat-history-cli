# ollama-chat-history

A local-first Python CLI to search, export, and manage your Ollama chat history.
Your conversations stay on your machine: this tool reads from your local Ollama
server, saves a JSON copy on your disk, and lets you filter and export to
Markdown. No cloud, no accounts, no API keys.

Built and maintained by **Asdale Dynamics, LLC** (Indiana, formed October 2026)
— beginner-friendly AI education, books, and practical local-LLM tools. Learn
more at [dylanasdale.github.io](https://dylanasdale.github.io).

## What it does

- `sync` — pull chats from your local Ollama server into a local JSON store
- `list` — view stored chats
- `search` — filter by keyword (title and message text), date range, and model
- `export` — write matching chats to a Markdown file

Everything runs locally against `http://127.0.0.1:11434` by default. Nothing is
uploaded anywhere.

## Install

```bash
pip install -e .
```

This provides the `ollama-chat-history` command.

## Usage

Sync chats from Ollama (full records with messages):

```bash
ollama-chat-history --url http://127.0.0.1:11434 sync --all
```

List what's stored locally:

```bash
ollama-chat-history list
```

Search by keyword and date range:

```bash
ollama-chat-history search --keyword python --from 2026-10-01 --to 2026-10-31 --model llama3.2
```

Export matching chats to Markdown:

```bash
ollama-chat-history export --output chats.md --keyword python
```

The local store defaults to `~/.ollama-chat-history/chats.json`; override with
`--store PATH`.

## Requirements

- Python 3.9+
- A locally running Ollama server (only for `sync`; search and export work
  entirely offline against your saved JSON)

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

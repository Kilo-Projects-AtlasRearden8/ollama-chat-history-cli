# ollama-chat-history

A friendly, local-first Python CLI for searching, exporting, and managing your
Ollama chat history. Your conversations stay on your computer: this tool reads
from your local Ollama server, saves a copy as JSON on your disk, and lets you
filter and export to Markdown. No cloud, no accounts, no API keys.

Built with care by **Asdale Dynamics, LLC** (Indiana, formed October 2026) —
beginner-friendly AI education, books, and practical local-LLM tools. Learn more
at [dylanasdale.github.io](https://dylanasdale.github.io).

## What it does

| Command | What it does |
|---------|--------------|
| `sync` | Pulls your chats from your local Ollama server into a JSON file on your computer |
| `list` | Shows the chats you have saved locally |
| `show` | Prints the full contents of one saved chat |
| `search` | Finds chats by keyword, date range, or model |
| `export` | Writes matching chats to a Markdown file |

Everything runs against `http://127.0.0.1:11434` by default. Nothing is uploaded
anywhere. Once you've synced, searching and exporting work entirely offline.

## Install

You'll need Python 3.9 or newer. From this folder:

```bash
pip install -e .
```

This installs the `ollama-chat-history` command. Check that it worked:

```bash
ollama-chat-history --help
```

## Step-by-step: your first sync

1. Make sure Ollama is running on your computer (usually at
   `http://127.0.0.1:11434`).
2. Sync your chats down to a local JSON file:

   ```bash
   ollama-chat-history sync
   ```

   By default this saves to `~/.ollama-chat-history/chats.json`. To use a
   different location, add `--store /path/to/chats.json`.

3. See what you've saved:

   ```bash
   ollama-chat-history list
   ```

4. Look at one chat in full:

   ```bash
   ollama-chat-history show <chat-id>
   ```

## Search your history

Find chats by keyword (searches titles and message text):

```bash
ollama-chat-history search --keyword python
```

Narrow it down by date or model:

```bash
ollama-chat-history search --keyword python --from 2026-10-01 --to 2026-10-31 --model llama3.2
```

Only see the first few matches:

```bash
ollama-chat-history search --keyword python --limit 5
```

## Export to Markdown

Save matching chats to a Markdown file you can open, print, or share:

```bash
ollama-chat-history export --output my-chats.md --keyword python
```

You can give the exported document a title:

```bash
ollama-chat-history export --output my-chats.md --title "My Python Chats"
```

## Remove a chat

```bash
ollama-chat-history delete <chat-id>
```

## Local-first, by design

- Your chat data lives in a JSON file on your machine, not in the cloud.
- No account, no API key, no personal data leaves your computer.
- Search and export work offline once your chats are synced.

## Requirements

- Python 3.9+
- A locally running Ollama server (only needed for `sync`; list, show, search,
  export, and delete work offline against your saved JSON)

## Tests

This project is tested with a mock Ollama server, so no real server or network
is needed:

```bash
python3 -m pytest
```

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See `LICENSE`.

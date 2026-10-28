"""Command-line interface for managing local Ollama chat history."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Iterable, Sequence

from .export import export_markdown
from .ollama import DEFAULT_BASE_URL, OllamaClient, OllamaError
from .search import filter_chats
from .storage import ChatRecord, ChatStore


def _print_records(records: Iterable[ChatRecord]) -> None:
    records = list(records)
    if not records:
        print("No matching chats.")
        return
    for index, record in enumerate(records, start=1):
        print(f"{index}. {record.title or 'Untitled chat'} [{record.model or 'unknown'}]")
        print(f"   id: {record.chat_id}")
        print(f"   created: {record.created_at}  updated: {record.updated_at}")
        print(f"   messages: {len(record.messages)}")


def _print_chat(record: ChatRecord) -> None:
    print(f"{record.title or 'Untitled chat'} [{record.model or 'unknown'}]")
    print(f"id: {record.chat_id}")
    print(f"created: {record.created_at}")
    print(f"updated: {record.updated_at}")
    print(f"messages: {len(record.messages)}")
    print("")
    if record.messages:
        for message in record.messages:
            role = message.get("role", "unknown")
            content = message.get("content", "")
            print(f"{role}: {content}")
            print("")
    else:
        print("(no messages stored)")


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ollama-chat-history",
        description="Search, export, and manage local Ollama chat history.",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_BASE_URL,
        help="Ollama server base URL (default: %(default)s)",
    )
    parser.add_argument(
        "--store",
        default=os.path.expanduser("~/.ollama-chat-history/chats.json"),
        help="Local JSON store path (default: %(default)s)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sync_p = sub.add_parser("sync", help="Fetch chats from Ollama into the local store")

    sub.add_parser("list", help="List chats in the local store")

    show_p = sub.add_parser("show", help="Print a stored chat's full content")
    show_p.add_argument("chat_id", help="Chat ID to display")

    delete_p = sub.add_parser("delete", help="Remove a chat from the local store")
    delete_p.add_argument("chat_id", help="Chat ID to remove")

    search_p = sub.add_parser("search", help="Search local chat store")
    search_p.add_argument("--keyword", help="Case-insensitive keyword match")
    search_p.add_argument("--from", dest="date_from", help="Start date (YYYY-MM-DD)")
    search_p.add_argument("--to", dest="date_to", help="End date (YYYY-MM-DD)")
    search_p.add_argument("--model", help="Filter by model name")
    search_p.add_argument("--limit", type=int, default=0, help="Max results to print")

    export_p = sub.add_parser("export", help="Export chats to Markdown")
    export_p.add_argument("--output", required=True, help="Output Markdown file path")
    export_p.add_argument("--keyword", help="Case-insensitive keyword match")
    export_p.add_argument("--from", dest="date_from", help="Start date (YYYY-MM-DD)")
    export_p.add_argument("--to", dest="date_to", help="End date (YYYY-MM-DD)")
    export_p.add_argument("--model", help="Filter by model name")
    export_p.add_argument(
        "--title", default="Ollama Chat History", help="Document title"
    )

    return parser.parse_args(argv)


def _cmd_sync(args: argparse.Namespace) -> int:
    try:
        client = OllamaClient(base_url=args.url)
    except OllamaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    store = ChatStore(args.store)
    try:
        chats = client.fetch_all()
        records = [
            ChatRecord(
                chat_id=c.chat_id,
                title=c.title,
                model=c.model,
                created_at=c.created_at,
                updated_at=c.updated_at,
                messages=c.messages,
            )
            for c in chats
        ]
    except OllamaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    store.merge(records)
    print(f"Synced {len(records)} chat(s) to {args.store}")
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    store = ChatStore(args.store)
    _print_records(store.load())
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    store = ChatStore(args.store)
    record = store.by_id(args.chat_id)
    if record is None:
        print(f"error: chat {args.chat_id} not found in {args.store}", file=sys.stderr)
        return 1
    _print_chat(record)
    return 0


def _cmd_delete(args: argparse.Namespace) -> int:
    store = ChatStore(args.store)
    if not store.by_id(args.chat_id):
        print(f"error: chat {args.chat_id} not found in {args.store}", file=sys.stderr)
        return 1
    if not store.remove(args.chat_id):
        print(f"error: chat {args.chat_id} not found in {args.store}", file=sys.stderr)
        return 1
    print(f"Deleted chat {args.chat_id} from {args.store}")
    return 0


def _cmd_search(args: argparse.Namespace) -> int:
    store = ChatStore(args.store)
    records = filter_chats(
        store.load(),
        keyword=args.keyword,
        date_from=args.date_from,
        date_to=args.date_to,
        model=args.model,
    )
    if args.limit and args.limit > 0:
        records = records[: args.limit]
    _print_records(records)
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    store = ChatStore(args.store)
    records = filter_chats(
        store.load(),
        keyword=args.keyword,
        date_from=args.date_from,
        date_to=args.date_to,
        model=args.model,
    )
    export_markdown(records, args.output, title=args.title)
    print(f"Exported {len(records)} chat(s) to {args.output}")
    return 0


_COMMANDS = {
    "sync": _cmd_sync,
    "list": _cmd_list,
    "show": _cmd_show,
    "delete": _cmd_delete,
    "search": _cmd_search,
    "export": _cmd_export,
}


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    return _COMMANDS[args.command](args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

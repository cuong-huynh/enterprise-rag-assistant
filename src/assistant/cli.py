"""CLI entry points for RAG ingest and ask (mirror mentor agentic-chatbot)."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from assistant.integrations.vector_store import reset_collection
from assistant.modules.rag import service as rag_service


async def _cmd_ingest(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.is_file():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1
    if args.reset:
        reset_collection()
        print("Chroma collection reset.")
    result = await rag_service.ingest_file(path, display_name=path.name)
    print(f"Ingested {result.file}: {result.num_chunks} chunks")
    return 0 if result.num_chunks > 0 else 1


async def _cmd_ask(args: argparse.Namespace) -> int:
    answer = await rag_service.ask(args.question, top_k=args.top_k)
    print(answer.answer)
    if answer.sources:
        print("\nSources:")
        for src in answer.sources:
            print(f"  - {src}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Enterprise RAG assistant CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest_parser = sub.add_parser("ingest", help="Ingest a PDF into Chroma")
    ingest_parser.add_argument("--file", required=True, help="Path to PDF file")
    ingest_parser.add_argument(
        "--reset",
        action="store_true",
        help="Wipe Chroma collection before ingest",
    )

    ask_parser = sub.add_parser("ask", help="Ask a question against indexed docs")
    ask_parser.add_argument("question", help="Question text")
    ask_parser.add_argument("--top-k", type=int, default=5, help="Retrieval top-k")

    args = parser.parse_args(argv)
    if args.command == "ingest":
        return asyncio.run(_cmd_ingest(args))
    if args.command == "ask":
        return asyncio.run(_cmd_ask(args))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

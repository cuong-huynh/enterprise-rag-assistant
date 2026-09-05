"""Public interface for the RAG module. api/ imports only from here."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from assistant.modules.rag.generation.answer import RagAnswer
from assistant.modules.rag.indexing.store import embed_and_store
from assistant.modules.rag.ingestion.chunk import chunk_texts
from assistant.modules.rag.ingestion.load import load_pdf
from assistant.modules.rag.orchestration.graph import get_compiled_graph


@dataclass
class IngestResult:
    file: str
    num_chunks: int


async def ingest_file(path: Path, display_name: str | None = None) -> IngestResult:
    """Load a PDF, chunk it, embed and store in Chroma.

    display_name: the original filename shown in citations (defaults to path.name).
    """
    name = display_name or path.name
    doc_id = str(uuid.uuid4())
    ingested_at = datetime.now(UTC).isoformat()
    pages = load_pdf(path)
    pages = [
        (text, {**meta, "source": name, "doc_id": doc_id, "ingested_at": ingested_at})
        for text, meta in pages
    ]
    docs = chunk_texts(pages)
    num_stored = embed_and_store(docs)
    return IngestResult(file=name, num_chunks=num_stored)


async def ask(question: str, top_k: int = 5) -> RagAnswer:
    """Run the agentic RAG graph and return an answer with citations."""
    graph = get_compiled_graph()
    final = await graph.ainvoke(
        {
            "question": question,
            "top_k": top_k,
            "docs": [],
            "retrieve_steps": 0,
        }
    )
    return RagAnswer(
        answer=str(final.get("answer") or ""),
        sources=list(final.get("sources") or []),
    )

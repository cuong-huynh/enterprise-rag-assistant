"""Public interface for the RAG module. api/ imports only from here."""

from dataclasses import dataclass
from pathlib import Path

from assistant.modules.rag.chunk import chunk_texts
from assistant.modules.rag.generate import RagAnswer, generate_answer
from assistant.modules.rag.index import embed_and_store
from assistant.modules.rag.ingest import load_pdf
from assistant.modules.rag.retrieve import retrieve_top_k


@dataclass
class IngestResult:
    file: str
    num_chunks: int


async def ingest_file(path: Path) -> IngestResult:
    """Load a PDF, chunk it, embed and store in Chroma."""
    pages = load_pdf(path)
    docs = chunk_texts(pages)
    num_stored = embed_and_store(docs)
    return IngestResult(file=path.name, num_chunks=num_stored)


async def ask(question: str, top_k: int = 5) -> RagAnswer:
    """Retrieve relevant chunks and generate an answer with citations."""
    context = retrieve_top_k(question, k=top_k)
    return await generate_answer(question, context)

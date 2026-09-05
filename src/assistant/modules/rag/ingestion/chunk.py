"""Split page texts into smaller overlapping chunks."""

import hashlib
from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from assistant.modules.rag.config import load_rag_config


@dataclass
class Document:
    text: str
    source: str
    page: int
    chunk_id: str
    doc_id: str = ""
    ingested_at: str = ""


def _make_id(text: str, source: str, page: int) -> str:
    raw = f"{source}:{page}:{text[:64]}"
    return hashlib.md5(raw.encode()).hexdigest()  # noqa: S324 — not security-sensitive


def chunk_texts(pages: list[tuple[str, dict]]) -> list[Document]:
    """Split page texts into Documents with metadata."""
    cfg = load_rag_config()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=int(cfg["chunk_size"]),
        chunk_overlap=int(cfg["chunk_overlap"]),
    )
    docs: list[Document] = []
    for text, meta in pages:
        chunks = splitter.split_text(text)
        for chunk in chunks:
            docs.append(
                Document(
                    text=chunk,
                    source=meta["source"],
                    page=meta["page"],
                    chunk_id=_make_id(chunk, meta["source"], meta["page"]),
                    doc_id=str(meta.get("doc_id") or ""),
                    ingested_at=str(meta.get("ingested_at") or ""),
                )
            )
    return docs

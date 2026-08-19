"""Split page texts into smaller overlapping chunks."""

import hashlib
from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


@dataclass
class Document:
    text: str
    source: str
    page: int
    chunk_id: str


def _make_id(text: str, source: str, page: int) -> str:
    raw = f"{source}:{page}:{text[:64]}"
    return hashlib.md5(raw.encode()).hexdigest()  # noqa: S324 — not security-sensitive


def chunk_texts(pages: list[tuple[str, dict]]) -> list[Document]:
    """Split page texts into Documents with metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
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
                )
            )
    return docs

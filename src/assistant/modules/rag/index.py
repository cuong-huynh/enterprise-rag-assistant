"""Embed documents and store in Chroma."""

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from assistant.integrations.vector_store import get_collection
from assistant.modules.rag.chunk import Document

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    return model.encode(texts, show_progress_bar=False).tolist()


def embed_and_store(docs: list[Document]) -> int:
    """Upsert documents into Chroma. Returns number of chunks stored."""
    if not docs:
        return 0

    collection = get_collection()
    texts = [d.text for d in docs]
    embeddings = embed_texts(texts)
    metadatas = [{"source": d.source, "page": d.page} for d in docs]
    ids = [d.chunk_id for d in docs]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )
    return len(docs)

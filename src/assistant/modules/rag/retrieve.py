"""Retrieve top-k relevant chunks for a question."""

from assistant.integrations.vector_store import get_collection
from assistant.modules.rag.chunk import Document
from assistant.modules.rag.index import embed_texts


def retrieve_top_k(question: str, k: int = 5) -> list[Document]:
    """Return the top-k most relevant chunks for the given question."""
    query_embedding = embed_texts([question])[0]
    collection = get_collection()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas"],
    )

    docs: list[Document] = []
    for text, meta, chunk_id in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["ids"][0],
    ):
        docs.append(
            Document(
                text=text,
                source=meta["source"],
                page=meta["page"],
                chunk_id=chunk_id,
            )
        )
    return docs

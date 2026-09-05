"""Embed documents and store in Chroma."""

from assistant.integrations.embedding_client import embed_documents
from assistant.integrations.vector_store import delete_chunks_by_source, get_collection
from assistant.modules.rag.ingestion.chunk import Document


def embed_and_store(docs: list[Document]) -> int:
    """Upsert documents into Chroma. Returns number of chunks stored."""
    if not docs:
        return 0

    for source in {d.source for d in docs}:
        delete_chunks_by_source(source)

    collection = get_collection()
    texts = [d.text for d in docs]
    embeddings = embed_documents(texts)
    metadatas = [
        {
            "source": d.source,
            "page": d.page,
            "doc_id": d.doc_id,
            "ingested_at": d.ingested_at,
        }
        for d in docs
    ]
    ids = [d.chunk_id for d in docs]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )
    return len(docs)

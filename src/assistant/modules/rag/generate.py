"""Generate an answer with citations from retrieved context."""

from dataclasses import dataclass

from assistant.integrations.llm_client import ask_llm
from assistant.modules.rag.chunk import Document

_SYSTEM_PROMPT = """\
You are a helpful assistant. Answer the user's question using ONLY the context provided.
If the answer cannot be found in the context, say "I cannot find this in the provided documents."
Always end your answer with a "Sources:" line listing the documents you used.
"""


def _build_prompt(question: str, docs: list[Document]) -> str:
    context_parts = []
    for i, doc in enumerate(docs, 1):
        citation = f"{doc.source} p.{doc.page + 1}"
        context_parts.append(f"[{i}] ({citation})\n{doc.text}")
    context = "\n\n".join(context_parts)
    return f"{_SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {question}"


@dataclass
class RagAnswer:
    answer: str
    sources: list[str]


def _extract_sources(docs: list[Document]) -> list[str]:
    seen: set[str] = set()
    sources: list[str] = []
    for doc in docs:
        label = f"{doc.source} p.{doc.page + 1}"
        if label not in seen:
            seen.add(label)
            sources.append(label)
    return sources


async def generate_answer(question: str, context: list[Document]) -> RagAnswer:
    if not context:
        return RagAnswer(
            answer="No relevant documents found.",
            sources=[],
        )

    prompt = _build_prompt(question, context)
    answer_text = await ask_llm(prompt)
    sources = _extract_sources(context)
    return RagAnswer(answer=answer_text, sources=sources)

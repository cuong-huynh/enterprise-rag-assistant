"""Generate an answer with citations from retrieved context."""

from dataclasses import dataclass

from assistant.integrations.llm_client import ask_llm
from assistant.modules.rag.config import load_generate_system_prompt
from assistant.modules.rag.ingestion.chunk import Document

_FALLBACK_SYSTEM = """\
You are an internal operations assistant for warehouse and purchasing staff.
Answer in the same language as the user's question.
Use ONLY the context. If the answer is not there, say so in that language — do not guess.
Write a short, clear reply (a few sentences or compact bullets). Do not start with \
"Based on the provided documents" or similar filler. Do not add a Sources line \
(citations are shown separately). Do not invent numbers that are not in the context.
"""


def _system_prompt() -> str:
    loaded = load_generate_system_prompt()
    return loaded or _FALLBACK_SYSTEM


def _build_prompt(question: str, docs: list[Document]) -> str:
    context_parts = []
    for i, doc in enumerate(docs, 1):
        citation = f"{doc.source} p.{doc.page + 1}"
        context_parts.append(f"[{i}] ({citation})\n{doc.text}")
    context = "\n\n".join(context_parts)
    return f"Context:\n{context}\n\nQuestion: {question}"


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
    answer_text = await ask_llm(prompt, system=_system_prompt())
    sources = _extract_sources(context)
    return RagAnswer(answer=answer_text, sources=sources)

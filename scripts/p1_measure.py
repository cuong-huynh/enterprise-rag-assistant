"""P1 close-out: ingest sample PDFs, ask 10 questions, report citation hit rate and latency.

Run from repo root: uv run python scripts/p1_measure.py

Uses the RAG service directly (no uvicorn). LLM stays in mock mode; citations
come from retrieval metadata, which is what this script scores.
"""

from __future__ import annotations

import asyncio
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from generate_sample_docs import generate_all  # noqa: E402

from assistant.integrations.vector_store import get_collection, reset_collection  # noqa: E402
from assistant.modules.rag import service as rag_service  # noqa: E402

GOLDEN = [
    {
        "question": (
            "How do I process a receipt in Odoo when the delivered quantity "
            "differs from the purchase order?"
        ),
        "expected_source": "odoo_inventory_guide.pdf",
    },
    {
        "question": "What are the steps to perform a cycle count in the warehouse?",
        "expected_source": "warehouse_sop.pdf",
    },
    {
        "question": "How do I configure reordering rules in Odoo Inventory?",
        "expected_source": "odoo_inventory_guide.pdf",
    },
    {
        "question": (
            "Who is responsible for approving inventory adjustments with value above 500 USD?"
        ),
        "expected_source": "warehouse_sop.pdf",
    },
    {
        "question": "What safety equipment is required in the warehouse?",
        "expected_source": "warehouse_sop.pdf",
    },
    {
        "question": "Which costing method should be used for perishable goods in Odoo?",
        "expected_source": "odoo_inventory_guide.pdf",
    },
    {
        "question": "What is required for a three-way match before releasing supplier payment?",
        "expected_source": "purchase_sop.pdf",
    },
    {
        "question": "What sample size does incoming quality control use for non-certified suppliers?",
        "expected_source": "quality_control_sop.pdf",
    },
    {
        "question": "When may a returned item be restocked to available inventory?",
        "expected_source": "returns_rma_sop.pdf",
    },
    {
        "question": "How long is an Odoo sales quotation valid by default?",
        "expected_source": "odoo_sales_guide.pdf",
    },
]


def _hit(sources: list[str], expected: str) -> bool:
    return any(expected in src for src in sources)


async def main() -> None:
    print("=" * 70)
    print("P1 MEASURE — ingest + 10 golden questions (retrieval citation)")
    print("=" * 70)

    pdfs = generate_all()
    reset_collection()

    ingest_rows: list[tuple[str, int]] = []
    for path in pdfs:
        result = await rag_service.ingest_file(path, display_name=path.name)
        ingest_rows.append((result.file, result.num_chunks))
        print(f"Ingested {result.file}: {result.num_chunks} chunks")

    total_chunks = get_collection().count()
    print(f"\nDocuments: {len(ingest_rows)}  |  Chunks in collection: {total_chunks}")

    latencies_ms: list[float] = []
    hits = 0

    print("\n" + "-" * 70)
    for i, item in enumerate(GOLDEN, 1):
        t0 = time.perf_counter()
        answer = await rag_service.ask(item["question"], top_k=5)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        latencies_ms.append(elapsed_ms)
        ok = _hit(answer.sources, item["expected_source"])
        hits += int(ok)
        mark = "HIT" if ok else "MISS"
        print(f"Q{i} [{mark}] {elapsed_ms:.0f} ms | expect {item['expected_source']}")
        print(f"    sources: {answer.sources}")
        print(f"    {item['question']}")
        print()

    median_ms = statistics.median(latencies_ms)
    hit_rate = hits / len(GOLDEN)
    print("=" * 70)
    print(f"Citation hit rate (expected filename in top-k sources): {hits}/{len(GOLDEN)} = {hit_rate:.0%}")
    print(f"Latency median (ask, mock LLM): {median_ms:.0f} ms")
    print(f"Latency min/max: {min(latencies_ms):.0f} / {max(latencies_ms):.0f} ms")
    print("=" * 70)

    if hit_rate < 1.0:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())

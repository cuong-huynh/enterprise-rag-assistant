"""RAG eval harness (P2).

Scores retrieval recall@k from a golden YAML. Citation groundedness uses
retrieve sources (valid in LLM_MODE=mock). Answer-key matching is recorded
as N/A until LLM_MODE=real.

Run from repo root:
    uv run python -m evals.run
    uv run python -m evals.run --skip-ingest
"""

from __future__ import annotations

import argparse
import asyncio
import statistics
import sys
import time
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from generate_sample_docs import generate_all  # noqa: E402

from assistant.core.config import settings  # noqa: E402
from assistant.integrations.vector_store import get_collection, reset_collection  # noqa: E402
from assistant.modules.rag import service as rag_service  # noqa: E402

DATASET = ROOT / "evals" / "datasets" / "rag_golden.yaml"
RESULTS_DIR = ROOT / "evals" / "results"


def _hit(sources: list[str], expected: list[str]) -> bool:
    return any(any(name in src for src in sources) for name in expected)


def _load_dataset() -> dict:
    with DATASET.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


async def _ensure_index(*, skip_ingest: bool) -> int:
    if skip_ingest:
        return get_collection().count()

    pdfs = generate_all()
    reset_collection()
    for path in pdfs:
        result = await rag_service.ingest_file(path, display_name=path.name)
        print(f"Ingested {result.file}: {result.num_chunks} chunks")
    return get_collection().count()


def _write_report(
    *,
    cases: list[dict],
    rows: list[dict],
    top_k: int,
    n_chunks: int,
    median_ms: float,
    recall: float,
    grounded: float,
) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"{date.today().isoformat()}.md"
    hits = sum(r["recall"] for r in rows)
    g_hits = sum(r["grounded"] for r in rows)
    lines = [
        f"# RAG eval — {date.today().isoformat()}",
        "",
        f"- Dataset: `{DATASET.name}` ({len(cases)} questions)",
        f"- top_k: {top_k}",
        f"- Chunks in collection: {n_chunks}",
        f"- LLM_MODE: `{settings.llm_mode}`",
        f"- EMBED_MODE: `{settings.embed_mode}`",
        f"- Recall@{top_k}: **{hits}/{len(rows)} = {recall:.0%}**",
        f"- Citation groundedness: **{g_hits}/{len(rows)} = {grounded:.0%}** "
        "(expected filename in sources; mock-safe)",
        f"- Ask latency median: {median_ms:.0f} ms",
        "",
        "| id | recall | grounded | ms | expected | sources |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        src = ", ".join(row["sources"]) if row["sources"] else "(none)"
        exp = ", ".join(row["expected"])
        rec = "HIT" if row["recall"] else "MISS"
        grd = "Y" if row["grounded"] else "N"
        lines.append(
            f"| {row['id']} | {rec} | {grd} | {row['ms']:.0f} | `{exp}` | {src} |"
        )
    misses = [r for r in rows if not r["recall"]]
    lines.extend(["", "## Misses", ""])
    if not misses:
        lines.append("None.")
    else:
        for row in misses:
            lines.append(f"- `{row['id']}`: {row['question']}")
            lines.append(f"  expected `{', '.join(row['expected'])}`; got {row['sources']}")
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run RAG golden-set eval")
    parser.add_argument(
        "--skip-ingest",
        action="store_true",
        help="Reuse the current Chroma collection (faster reruns)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=None,
        help="Override top_k from the dataset YAML (for before/after comparisons)",
    )
    args = parser.parse_args()

    data = _load_dataset()
    cases: list[dict] = data["cases"]
    top_k = args.top_k if args.top_k is not None else int(data.get("top_k", 5))

    print("=" * 70)
    print(f"P2 EVAL — {data.get('dataset')} v{data.get('version')}  ({len(cases)} questions)")
    print("=" * 70)

    n_chunks = await _ensure_index(skip_ingest=args.skip_ingest)
    print(f"Chunks: {n_chunks}  |  LLM_MODE={settings.llm_mode}  |  top_k={top_k}\n")

    rows: list[dict] = []
    latencies: list[float] = []

    for case in cases:
        expected = list(case["expected_sources"])
        t0 = time.perf_counter()
        answer = await rag_service.ask(case["question"], top_k=top_k)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        latencies.append(elapsed_ms)
        recall_ok = _hit(answer.sources, expected)
        grounded_ok = bool(answer.sources) and recall_ok
        rows.append(
            {
                "id": case["id"],
                "question": case["question"],
                "expected": expected,
                "sources": answer.sources,
                "recall": recall_ok,
                "grounded": grounded_ok,
                "ms": elapsed_ms,
            }
        )
        mark = "HIT" if recall_ok else "MISS"
        print(f"{case['id']} [{mark}] {elapsed_ms:.0f} ms  expect {expected}")
        print(f"    sources: {answer.sources}")

    n = len(rows)
    recall = sum(r["recall"] for r in rows) / n
    grounded = sum(r["grounded"] for r in rows) / n
    median_ms = statistics.median(latencies)

    print("=" * 70)
    print(f"Recall@{top_k}: {sum(r['recall'] for r in rows)}/{n} = {recall:.0%}")
    print(f"Citation groundedness: {sum(r['grounded'] for r in rows)}/{n} = {grounded:.0%}")
    print(f"Latency median (ask, {settings.llm_mode} LLM): {median_ms:.0f} ms")
    print("=" * 70)

    report = _write_report(
        cases=cases,
        rows=rows,
        top_k=top_k,
        n_chunks=n_chunks,
        median_ms=median_ms,
        recall=recall,
        grounded=grounded,
    )
    print(f"Wrote {report.relative_to(ROOT)}")


if __name__ == "__main__":
    asyncio.run(main())

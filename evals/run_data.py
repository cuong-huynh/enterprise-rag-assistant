"""Structured-query eval harness (P3).

Scores mock-safe checks: guardrail blocks, model used, count/sum from adapter rows.

Run from repo root::

    uv run python -m evals.run_data
"""

from __future__ import annotations

import argparse
import asyncio
import statistics
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from assistant.modules.erp.mock import MockErpAdapter  # noqa: E402
from assistant.modules.text2sql import service as text2sql_service  # noqa: E402

DATASET = ROOT / "evals" / "datasets" / "data_golden.yaml"
RESULTS_DIR = ROOT / "evals" / "results"
DB_PATH = ROOT / "data" / "mock_odoo.sqlite"


def _load_dataset() -> dict:
    with DATASET.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _ensure_db() -> Path:
    if not DB_PATH.exists():
        from generate_mock_odoo import generate

        generate()
    return DB_PATH


def _gold_rows(case: dict, adapter: MockErpAdapter) -> list[dict[str, Any]]:
    return adapter.search_read(
        case["expected_model"],
        domain=case.get("domain") or [],
        fields=list(case.get("fields") or []),
        limit=int(case.get("limit") or 100),
    )


def _gold_value(case: dict, rows: list[dict[str, Any]]) -> str:
    metric = case["metric"]
    if metric == "count":
        return str(len(rows))
    if metric == "sum_amount_total":
        total = sum(float(r.get("amount_total") or 0) for r in rows)
        return str(round(total, 2))
    if metric == "sum_quantity":
        qty = sum(float(r.get("quantity") or 0) for r in rows)
        return str(round(qty, 2))
    raise ValueError(f"Unknown metric: {metric}")


def _score_case(case: dict, result: Any, adapter: MockErpAdapter) -> dict:
    kind = case["kind"]
    if kind == "block":
        ok = bool(result.blocked) and result.tool_steps == 0
        return {
            "ok": ok,
            "detail": f"blocked={result.blocked} steps={result.tool_steps}",
            "expected": "blocked, tool_steps=0",
        }

    rows = _gold_rows(case, adapter)
    gold = _gold_value(case, rows)
    model_ok = case["expected_model"] in (result.models_used or [])
    value_ok = gold in (result.answer or "")
    not_blocked = not result.blocked
    ok = not_blocked and model_ok and value_ok
    return {
        "ok": ok,
        "detail": result.answer[:120],
        "expected": f"{case['expected_model']} {case['metric']}={gold}",
    }


async def score_all() -> dict:
    _ensure_db()
    data = _load_dataset()
    cases: list[dict] = data["cases"]
    adapter = MockErpAdapter(db_path=DB_PATH)

    rows: list[dict] = []
    latencies: list[float] = []
    tool_steps: list[int] = []

    for case in cases:
        t0 = time.perf_counter()
        result = await text2sql_service.ask(case["question"])
        elapsed_ms = (time.perf_counter() - t0) * 1000
        latencies.append(elapsed_ms)
        scored = _score_case(case, result, adapter)
        tool_steps.append(result.tool_steps)
        rows.append(
            {
                "id": case["id"],
                "question": case["question"],
                "kind": case["kind"],
                "ok": scored["ok"],
                "detail": scored["detail"],
                "expected": scored["expected"],
                "blocked": result.blocked,
                "tool_steps": result.tool_steps,
                "ms": elapsed_ms,
            }
        )

    data_rows = [r for r in rows if r["kind"] == "data"]
    block_rows = [r for r in rows if r["kind"] == "block"]
    return {
        "dataset": data.get("dataset"),
        "version": data.get("version"),
        "rows": rows,
        "data_hits": sum(r["ok"] for r in data_rows),
        "data_n": len(data_rows),
        "block_hits": sum(r["ok"] for r in block_rows),
        "block_n": len(block_rows),
        "median_ms": statistics.median(latencies) if latencies else 0.0,
        "mean_tool_steps": (sum(tool_steps) / len(tool_steps)) if tool_steps else 0.0,
        "mean_tool_steps_data": (
            sum(r["tool_steps"] for r in data_rows) / len(data_rows) if data_rows else 0.0
        ),
    }


def _write_report(summary: dict) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"{date.today().isoformat()}-data.md"
    rows = summary["rows"]
    lines = [
        f"# Structured-query eval — {date.today().isoformat()}",
        "",
        f"- Dataset: `{DATASET.name}` v{summary['version']}",
        f"- Data questions: **{summary['data_hits']}/{summary['data_n']}**",
        f"- Guardrail blocks: **{summary['block_hits']}/{summary['block_n']}**",
        f"- Mean tool steps (all / data-only): "
        f"{summary['mean_tool_steps']:.2f} / {summary['mean_tool_steps_data']:.2f}",
        f"- Latency median: {summary['median_ms']:.0f} ms",
        "",
        "| id | kind | ok | steps | ms | expected |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        mark = "HIT" if row["ok"] else "MISS"
        lines.append(
            f"| {row['id']} | {row['kind']} | {mark} | {row['tool_steps']} | "
            f"{row['ms']:.0f} | `{row['expected']}` |"
        )
    misses = [r for r in rows if not r["ok"]]
    lines.extend(["", "## Misses", ""])
    if not misses:
        lines.append("None.")
    else:
        for row in misses:
            lines.append(f"- `{row['id']}`: {row['question']}")
            lines.append(f"  expected `{row['expected']}`; got {row['detail']}")
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run structured-query golden eval")
    parser.parse_args()

    print("=" * 70)
    print("P3 EVAL — data_golden")
    print("=" * 70)

    summary = await score_all()
    for row in summary["rows"]:
        mark = "HIT" if row["ok"] else "MISS"
        print(f"{row['id']} [{mark}] {row['ms']:.0f} ms  {row['expected']}")

    print("=" * 70)
    print(f"Data: {summary['data_hits']}/{summary['data_n']}")
    print(f"Blocks: {summary['block_hits']}/{summary['block_n']}")
    print(f"Mean tool steps (data): {summary['mean_tool_steps_data']:.2f}")
    print(f"Latency median: {summary['median_ms']:.0f} ms")
    print("=" * 70)

    report = _write_report(summary)
    print(f"Wrote {report.relative_to(ROOT)}")


if __name__ == "__main__":
    asyncio.run(main())

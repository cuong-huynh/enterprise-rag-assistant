"""Router eval harness (P4).

Scores rule-based route labels against router_golden.yaml (no LLM, no engine calls).

Run from repo root::

    uv run python -m evals.run_router
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from assistant.modules.dispatcher import service as dispatcher_service  # noqa: E402

DATASET = ROOT / "evals" / "datasets" / "router_golden.yaml"
RESULTS_DIR = ROOT / "evals" / "results"


def _load_dataset() -> dict:
    with DATASET.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _write_report(*, total: int, correct: int, by_route: Counter[str], misses: list[dict]) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"{date.today().isoformat()}-router.md"
    acc = (correct / total * 100) if total else 0.0
    lines = [
        f"# Router eval — {date.today().isoformat()}",
        "",
        f"- Accuracy: **{correct}/{total}** ({acc:.1f}%)",
        f"- By expected route: {dict(by_route)}",
        "",
    ]
    if misses:
        lines.append("## Misses")
        lines.append("")
        for m in misses:
            lines.append(
                f"- `{m['id']}` expected `{m['expected']}` got `{m['got']}` — {m['question'][:80]}"
            )
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Run router golden eval")
    parser.parse_args()

    data = _load_dataset()
    cases = list(data.get("cases") or [])
    misses: list[dict] = []
    correct = 0
    by_route: Counter[str] = Counter()

    for case in cases:
        expected = case["expected_route"]
        by_route[expected] += 1
        got = dispatcher_service.classify(case["question"]).route
        if got == expected:
            correct += 1
        else:
            misses.append(
                {
                    "id": case["id"],
                    "expected": expected,
                    "got": got,
                    "question": case["question"],
                }
            )

    total = len(cases)
    acc = (correct / total * 100) if total else 0.0
    print(f"Router accuracy: {correct}/{total} ({acc:.1f}%)")
    for miss in misses:
        print(f"  MISS {miss['id']}: expected {miss['expected']} got {miss['got']}")

    report = _write_report(total=total, correct=correct, by_route=by_route, misses=misses)
    print(f"Wrote {report}")
    return 0 if correct == total else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""P3 golden set — 15 data questions + 3 guardrail blocks."""

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def ensure_mock_db() -> Path:
    db = REPO_ROOT / "data" / "mock_odoo.sqlite"
    if not db.exists():
        import sys

        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        from generate_mock_odoo import generate

        generate()
    return db


@pytest.mark.asyncio
async def test_data_golden_all(ensure_mock_db: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert ensure_mock_db.exists()
    monkeypatch.syspath_prepend(str(REPO_ROOT))
    from evals.run_data import score_all

    summary = await score_all()
    assert summary["data_n"] == 15
    assert summary["block_n"] == 3
    misses = [r["id"] for r in summary["rows"] if not r["ok"]]
    assert not misses, f"golden misses: {misses}"
    assert summary["data_hits"] == 15
    assert summary["block_hits"] == 3

"""Golden routing labels — classifier only."""

from pathlib import Path

import pytest
import yaml

from assistant.modules.dispatcher.classifier import classify_route

DATASET = Path(__file__).resolve().parents[2] / "evals" / "datasets" / "router_golden.yaml"


def _cases() -> list[dict]:
    with DATASET.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return list(data.get("cases") or [])


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c["id"])
def test_router_golden_route(case: dict) -> None:
    got = classify_route(case["question"]).route
    assert got == case["expected_route"], (
        f"{case['id']}: expected {case['expected_route']} got {got}"
    )

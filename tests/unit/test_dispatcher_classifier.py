"""Unit tests for the rule-based route classifier."""

import pytest

from assistant.modules.dispatcher.classifier import classify_route


@pytest.mark.parametrize(
    ("question", "expected"),
    [
        ("How many confirmed sale orders?", "data"),
        ("What are the steps to perform a cycle count?", "rag"),
        ("Compare return policy with sale order revenue.", "hybrid"),
        ("According to the SOP how many sale orders?", "hybrid"),
    ],
)
def test_classify_route_samples(question: str, expected: str) -> None:
    assert classify_route(question).route == expected


def test_classify_default_is_rag() -> None:
    decision = classify_route("hello there")
    assert decision.route == "rag"
    assert "default" in decision.reason.lower()

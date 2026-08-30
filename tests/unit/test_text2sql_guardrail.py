from assistant.modules.text2sql.nodes.guardrail import check_intent


def test_blocks_write_intent() -> None:
    blocked, reason = check_intent("DELETE FROM sale_order WHERE id = 1")
    assert blocked
    assert "Write" in reason


def test_blocks_out_of_scope() -> None:
    blocked, reason = check_intent("What's the weather in Hanoi today?")
    assert blocked
    assert "outside" in reason.lower()


def test_blocks_forbidden_model() -> None:
    blocked, reason = check_intent("search_read account.move for all invoices")
    assert blocked
    assert "not allowed" in reason.lower()


def test_allows_sale_order_question() -> None:
    blocked, reason = check_intent("How many sale orders are in state sale?")
    assert not blocked
    assert reason == ""

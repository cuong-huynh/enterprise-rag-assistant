from assistant.modules.rag.retrieve import expand_query


def test_expand_cycle_count_vietnamese() -> None:
    q = "Các bước thực hiện kiểm kê xoay vòng trong kho là gì?"
    out = expand_query(q)
    assert "cycle count" in out.lower()
    assert q in out


def test_expand_english_unchanged() -> None:
    q = "What are the steps to perform a cycle count in the warehouse?"
    assert expand_query(q) == q

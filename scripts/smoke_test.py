"""Smoke test against a running API. Start uvicorn first.

Usage: uv run python scripts/smoke_test.py
Default base: http://localhost:8001
"""

import json
import urllib.request

BASE = "http://localhost:8001"

QUESTIONS = [
    "How do I process a receipt in Odoo when the delivered quantity differs from the purchase order?",
    "What are the steps to perform a cycle count in the warehouse?",
    "How do I configure reordering rules in Odoo Inventory?",
    "Who is responsible for approving inventory adjustments with value above 500 USD?",
    "What safety equipment is required in the warehouse?",
    "Which costing method should be used for perishable goods in Odoo?",
    "What is required for a three-way match before releasing supplier payment?",
    "What sample size does incoming quality control use for non-certified suppliers?",
    "When may a returned item be restocked to available inventory?",
    "How long is an Odoo sales quotation valid by default?",
]


def ask(question: str) -> dict:
    data = json.dumps({"question": question}).encode()
    req = urllib.request.Request(
        f"{BASE}/ask",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def main() -> None:
    print("=" * 70)
    print("SMOKE TEST — Enterprise RAG Assistant (HTTP)")
    print("=" * 70)

    for i, q in enumerate(QUESTIONS, 1):
        print(f"\nQ{i}: {q}")
        result = ask(q)
        print(f"Answer: {result['answer'][:300]}")
        print(f"Sources: {result['sources']}")
        print(f"Mode: {result['mode']}")
        print("-" * 70)

    print("\nSmoke test complete.")


if __name__ == "__main__":
    main()

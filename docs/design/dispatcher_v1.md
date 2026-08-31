# Design Doc: Dispatcher v1 (P4)

One chat entry point routes questions to RAG, structured data, or both. Engines stay independent; dispatcher only calls `rag/service.ask` and `text2sql/service.ask`.

## Flow

```text
POST /chat (or GET / for HTML UI)
    → dispatcher/service.chat(question)
    → classifier.classify_route(question)  # rules + configs/prompts/dispatcher.yaml
    → rag | data | hybrid (both services, merge answer)
```

## Decisions

| Choice | Reason |
|---|---|
| Rule classifier first | Mock-safe CI; `evals/run_router` scores 30/30 without LLM |
| Hybrid = call both services | BUILD_PLAN: pass data, no cross-import |
| Keep `/ask` and `/query` | Eval and debugging; user demo uses `/chat` |
| `GET /` serves `static/chat.html` | Minimal demo page for video |

## Out of scope (v1)

- LLM route classifier
- Smart merge (template `[Documents]` / `[Data]` only)
- Auth / session

## Done when

- `POST /chat` routes correctly on golden set (30 labels)
- Integration tests with mocked engines
- Browser UI calls `/chat`

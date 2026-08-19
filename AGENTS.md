# AGENTS.md — Module conventions for AI coding agents

## Package structure

One distribution package `assistant`, src layout (`src/assistant/`).

```
src/assistant/
├── main.py           # FastAPI app factory — composition only
├── core/             # config, logging, exceptions — imports nothing else
├── api/              # HTTP layer — imports integrations and modules, not each other
├── integrations/     # llm_client, vector_store — imports core, not modules
├── modules/          # business logic — each module exposes one service.py gate
│   ├── rag/
│   ├── text2sql/
│   ├── dispatcher/
│   └── erp/
└── utils/            # pure helpers — imports neither modules nor integrations
```

## Dependency rule (non-negotiable)

```
api → modules → integrations → core
```

- Upper layers call lower layers; **never the reverse**.
- `rag` and `text2sql` **must not import each other**. Cross-engine logic lives in `dispatcher`.
- The entry point for each module is `service.py`. `api` only imports `service.py`, never module internals.
- Enforced by `import-linter` in CI from the end of P1.

## Rules when adding code

1. P0 contains only `core`, `api`, `integrations/llm_client`. **Do not pre-create empty `modules/`.**
2. Each phase adds exactly the module it needs — no speculative scaffolding.
3. `main.py` is composition only — no business logic here.
4. Secrets go in `.env`, tunable config in `configs/`. Never hardcode values in source.
5. `LLM_MODE=mock` in CI. Never call a real LLM in tests.

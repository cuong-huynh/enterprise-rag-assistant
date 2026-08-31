"""LLM client with mock/real mode switch.

Keeps all LLM I/O in one place so the rest of the codebase never imports
an LLM library directly.  Switch via LLM_MODE env var.
"""

from assistant.core.config import settings


async def ask_llm(prompt: str, system: str = "") -> str:
    """Send a prompt and return a text response.

    In mock mode returns a deterministic stub — safe for CI and local dev.
    """
    if settings.llm_mode == "mock":
        return _mock_response(prompt)

    return await _real_response(prompt, system)


def _mock_response(prompt: str) -> str:
    return f"[mock] received: {prompt[:120]}"


async def _real_response(prompt: str, system: str) -> str:
    if not settings.openai_api_key.strip():
        raise RuntimeError(
            "OPENAI_API_KEY is empty. Set your provider key in enterprise-rag-assistant/.env."
        )
    try:
        from openai import AsyncOpenAI  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError("Install 'openai' to use LLM_MODE=real (uv sync)") from exc

    client = AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content or ""

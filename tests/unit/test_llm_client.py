import pytest

from assistant.integrations.llm_client import ask_llm


@pytest.mark.asyncio
async def test_mock_response_contains_prompt():
    response = await ask_llm("what is RAG?")
    assert "what is RAG?" in response


@pytest.mark.asyncio
async def test_mock_response_prefix():
    response = await ask_llm("hello")
    assert response.startswith("[mock]")

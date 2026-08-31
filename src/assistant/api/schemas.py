"""Pydantic request/response models for the HTTP API."""

from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    mode: str


class IngestResponse(BaseModel):
    file: str
    num_chunks: int


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    blocked: bool
    block_reason: str | None
    models_used: list[str]
    tool_steps: int


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    route: str
    reason: str
    sources: list[str] = []
    blocked: bool = False
    block_reason: str | None = None
    models_used: list[str] = []
    tool_steps: int = 0

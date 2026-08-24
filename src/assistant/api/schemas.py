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

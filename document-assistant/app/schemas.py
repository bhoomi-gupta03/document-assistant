"""Pydantic models describing what the API accepts and returns."""
from pydantic import BaseModel, Field


class DocumentOut(BaseModel):
    id: int
    filename: str
    size_bytes: int
    word_count: int
    sentence_count: int
    uploaded_at: str


class DocumentDetail(DocumentOut):
    content: str


class DocumentList(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[DocumentOut]


class SearchHitOut(BaseModel):
    document_id: int
    filename: str
    score: int
    snippet: str


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[SearchHitOut]


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    document_id: int | None = Field(default=None, ge=1, description="Limit to one document")


class SourceOut(BaseModel):
    document_id: int
    filename: str
    sentence: str
    score: float


class AskResponse(BaseModel):
    question: str
    answer: str | None
    sources: list[SourceOut]

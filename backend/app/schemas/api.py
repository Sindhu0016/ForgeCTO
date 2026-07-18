from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    idea: str = Field(..., min_length=10, max_length=2000)


class ProjectSummary(BaseModel):
    id: UUID
    idea: str
    status: str
    current_step: str
    is_seed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectResponse(BaseModel):
    id: UUID
    idea: str
    status: str
    current_step: str
    artifacts: dict[str, Any]
    error_message: str | None
    is_seed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SSEEvent(BaseModel):
    step: str
    status: str
    message: str
    partial: dict[str, Any] | None = None


class GitHubExportRequest(BaseModel):
    repo: str | None = None  # owner/repo override


class GitHubExportResponse(BaseModel):
    created: list[dict[str, Any]]
    failed: list[dict[str, Any]]


class MarkdownExportResponse(BaseModel):
    filename: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=2, max_length=2000)


class ChatResponse(BaseModel):
    reply: str
    citations: list[str] = Field(default_factory=list)


class ChatHistoryMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=4000)


class GeneralChatRequest(BaseModel):
    message: str = Field(..., min_length=2, max_length=2000)
    history: list[ChatHistoryMessage] = Field(default_factory=list)


class GeneralChatResponse(BaseModel):
    reply: str

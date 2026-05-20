from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ToolError(BaseModel):
    code: str
    message: str
    provider: str | None = None
    retryable: bool
    details: dict[str, Any] = Field(default_factory=dict)


class PartialItemError(BaseModel):
    symbol: str
    error: ToolError

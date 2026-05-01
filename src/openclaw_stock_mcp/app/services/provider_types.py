from __future__ import annotations

from pydantic import BaseModel


class ProviderSelection(BaseModel):
    primary: str
    fallback: list[str] = []

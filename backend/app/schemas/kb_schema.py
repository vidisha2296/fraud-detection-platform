# app/schemas/kb_schema.py
from pydantic import BaseModel
from datetime import datetime
from typing import Any, List, Optional, Dict

class KBEntryCreate(BaseModel):
    title: str
    snippet: str
    anchors: Optional[List[str]] = None

class KBEntryRead(BaseModel):
    id: str
    title: str
    snippet: str
    anchors: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        # orm_mode = True
         from_attributes = True

class KBSearchResult(BaseModel):
    id: str
    title: str
    snippet: str
    anchors: Optional[List[str]] = None

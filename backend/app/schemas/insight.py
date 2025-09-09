from pydantic import BaseModel
from typing import Any, Dict
from datetime import datetime

class InsightCreate(BaseModel):
    customer_id: str
    type: str
    data: Dict[str, Any]

class InsightRead(BaseModel):
    id: str
    customer_id: str
    type: str
    data: Dict[str, Any]
    generated_at: datetime

    class Config:
        orm_mode = True

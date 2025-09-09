# app/schemas/action.py
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class ActionCreate(BaseModel):
    customer_id: Optional[str]
    txn_id: Optional[str] = None
    action_type: str
    details: Optional[Dict] = None


class ActionRead(BaseModel):
    id: str
    customer_id: Optional[str]  
    txn_id: Optional[str] = None
    action_type: str
    details: Optional[Dict] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # ✅ Pydantic v2 replacement for orm_mode


class OTPVerify(BaseModel):
    otp: str

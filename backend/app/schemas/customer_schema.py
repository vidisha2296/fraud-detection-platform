# app/schemas/customer.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from app.schemas.transaction import TransactionRead
from app.schemas.action import ActionRead
from app.schemas.fraud_alert import FraudAlertRead
from app.schemas.insight import InsightRead

class CustomerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerRead(CustomerBase):
    customer_id: str
    created_at: datetime
    transactions: Optional[List[TransactionRead]] = []
    actions: Optional[List[ActionRead]] = []
    fraud_alerts: Optional[List[FraudAlertRead]] = []
    insights: Optional[List[InsightRead]] = []

    class Config:
        # orm_mode = True
        from_attributes = True

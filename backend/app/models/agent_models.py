from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime
from app.core.database import Base

class FraudAssessment(BaseModel):
    risk_score: float
    reasons: List[str]
    signals: Dict[str, float]
    timestamp: datetime = None

class RiskDecision(BaseModel):
    decision: str  # "approve", "verify", "review", "block"
    confidence: float
    rules_applied: List[str]
    timestamp: datetime = None

class ActionProposal(BaseModel):
    action: str  # "approve", "request_otp", "flag_for_review", "block_transaction"
    message: str
    transaction_id: Optional[str]
    customer_id: Optional[str]
    timestamp: datetime = None

class CustomerProfile(BaseModel):
    customer_id: str
    risk_level: str
    total_transactions: int
    chargeback_count: int
    devices: List[str]
    avg_transaction_amount: float
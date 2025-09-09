# from pydantic import BaseModel, Field
# from datetime import datetime
# from typing import Optional

# class TransactionIngest(BaseModel):
#     customer_id: str = Field(..., description="Unique identifier of the customer")
#     txn_id: str = Field(..., description="Unique identifier of the transaction")
#     merchant: str = Field(..., description="Merchant name or ID")
#     category: Optional[str] = Field(None, description="Transaction category (e.g., Food, Travel)")
#     amount: float = Field(..., description="Transaction amount")
#     currency: str = Field("USD", description="Transaction currency, defaults to USD")
#     mcc: Optional[str] = Field(None, description="Merchant Category Code")
#     timestamp: datetime = Field(default_factory=datetime.utcnow, description="Transaction timestamp")

#     class Config:
#         orm_mode = True
#         schema_extra = {
#             "example": {
#                 "customer_id": "cust123",
#                 "txn_id": "txn789",
#                 "merchant": "Amazon",
#                 "category": "Shopping",
#                 "amount": 199.99,
#                 "currency": "USD",
#                 "mcc": "5311",
#                 "timestamp": "2025-09-06T12:30:00Z"
#             }
#         }


# # app/schemas/transaction.py
# from pydantic import BaseModel, Field
# from typing import Optional
# from datetime import datetime

# class TransactionCreate(BaseModel):
#     customer_id: str
#     txn_id: str
#     merchant: str
#     category: Optional[str] = None
#     amount: float
#     currency: str = "USD"
#     mcc: Optional[str] = None
#     timestamp: Optional[datetime] = None

# class TransactionRead(TransactionCreate):
#     id: str
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         orm_mode = True

# # Alias for ingest endpoint
# TransactionIngest = TransactionCreate


# app/schemas/transaction.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TransactionCreate(BaseModel):
    customer_id: str
    txn_id: str
    merchant: str
    category: Optional[str] = None
    amount: float
    currency: str = "USD"
    mcc: Optional[str] = None
    timestamp: Optional[datetime] = None  # Allows specifying txn timestamp

# class TransactionRead(BaseModel):
#     id: str
#     customer_id: str
#     txn_id: str
#     merchant: str
#     category: Optional[str] = None
#     amount: float
#     currency: str
#     mcc: Optional[str] = None
#     timestamp: Optional[datetime] = None
#     created_at: datetime
#     updated_at: datetime
class TransactionRead(BaseModel):
    id: str  # Change from int to str to match the database
    customer_id: str
    txn_id: str
    amount: float
    currency: str
    merchant: Optional[str] = None
    category: Optional[str] = None
    mcc: Optional[int] = None  # Note: This should be Optional[str] if your DB column is String
    timestamp: datetime
    # Make these optional with default values
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Alias used for ingestion endpoints
TransactionIngest = TransactionCreate

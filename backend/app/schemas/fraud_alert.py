# from pydantic import BaseModel
# from typing import List, Optional
# from datetime import datetime

# class FraudAlertCreate(BaseModel):
#     customer_id: str
#     txn_id: Optional[str] = None
#     score: float
#     reasons: List[str]
#     action_taken: Optional[str] = None
#     timestamp: Optional[datetime] = None

# # class FraudAlertRead(BaseModel):
# #     id: str
# #     customer_id: str
# #     txn_id: Optional[str] = None
# #     score: float
# #     reasons: List[str]
# #     action_taken: Optional[str] = None
# #     timestamp: datetime

# #     class Config:
# #         # orm_mode = True
# #          from_attributes = True


# class FraudAlertRead(BaseModel):
#     id: str
#     customer_id: str
#     txn_id: Optional[str] = None
#     score: float
#     reasons: List[str] = []  # default empty list
#     action_taken: Optional[str] = None
#     timestamp: datetime

#     model_config = {
#         "from_attributes": True  # Pydantic v2 way to enable ORM-like parsing
#     }



from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class FraudAlertCreate(BaseModel):
    customer_id: str
    txn_id: Optional[str] = None
    score: float
    reasons: List[str] = Field(default_factory=list)  # ensures default empty list
    action_taken: Optional[str] = None
    timestamp: Optional[datetime] = None

class FraudAlertRead(BaseModel):
    id: str
    customer_id: str
    txn_id: Optional[str] = None
    score: float
    reasons: List[str] = Field(default_factory=list)  # default empty list
    action_taken: Optional[str] = None
    timestamp: datetime

    model_config = {
        "from_attributes": True  # enables ORM-like parsing in Pydantic v2
    }

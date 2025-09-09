# app/schemas/eval_schema.py
from pydantic import BaseModel
from typing import Any, Dict
from datetime import datetime

class EvalCaseCreate(BaseModel):
    name: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]

class EvalCaseRead(BaseModel):
    id: str
    name: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    created_at: datetime

    class Config:
        orm_mode = True

class EvalResultCreate(BaseModel):
    eval_case_id: str
    actual_output: Dict[str, Any]
    passed: int
    execution_time: float | None = None

class EvalResultRead(BaseModel):
    id: str
    eval_case_id: str
    actual_output: Dict[str, Any]
    passed: int
    execution_time: float | None
    created_at: datetime

    class Config:
        # orm_mode = True
          from_attributes = True

class EvalMetrics(BaseModel):
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float

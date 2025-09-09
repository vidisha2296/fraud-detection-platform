# app/models/eval.py
from sqlalchemy import Column, String, JSON, DateTime, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid
from app.core.database import Base

class EvalCase(Base):
    __tablename__ = "eval_cases"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)              # Name of test case
    input_data = Column(JSON, nullable=False)          # Input for evaluation
    expected_output = Column(JSON, nullable=False)     # Expected output
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    results = relationship("EvalResult", back_populates="eval_case")

class EvalResult(Base):
    __tablename__ = "eval_results"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    eval_case_id = Column(String, ForeignKey("eval_cases.id"), nullable=False)
    actual_output = Column(JSON, nullable=False)
    passed = Column(Integer, nullable=False)           # 1 = pass, 0 = fail
    execution_time = Column(Float, nullable=True)      # in seconds
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    eval_case = relationship("EvalCase", back_populates="results")

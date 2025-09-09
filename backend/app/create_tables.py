# app/create_tables.py
import os
from sqlalchemy import create_engine
from app.core.database import Base

# -----------------------------
# Database URL
# -----------------------------
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@db:5432/fraud_db"
)

engine = create_engine(DATABASE_URL, echo=True)

# -----------------------------
# Explicitly import all models
# -----------------------------
from app.models.customer import Customer as _
from app.models.transaction import Transaction as _
from app.models.action import Action as _
from app.models.fraud_alert import FraudAlert as _
from app.models.insights import Insight as _
from app.models.eval import EvalCase as _, EvalResult as _
from app.models.kb import KBEntry as _
# -----------------------------
# Create all tables
# -----------------------------
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully!")

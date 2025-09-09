# # backend/app/models/customer.py
# from sqlalchemy import Column, String, DateTime
# from sqlalchemy.orm import relationship
# from app.core.database import Base
# from datetime import datetime
# from app.core.database import Base

# class Customer(Base):
#     __tablename__ = "customers"

#     customer_id = Column(String, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     email = Column(String, unique=True, nullable=True)
#     phone = Column(String, unique=True, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     # Relationships
#     transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")
#     actions = relationship("Action", back_populates="customer", cascade="all, delete-orphan")
#     fraud_alerts = relationship("FraudAlert", back_populates="customer", cascade="all, delete-orphan")
#     insights = relationship("Insight", back_populates="customer", cascade="all, delete-orphan")

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")
    actions = relationship("Action", back_populates="customer", cascade="all, delete-orphan")
    fraud_alerts = relationship("FraudAlert", back_populates="customer", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="customer", cascade="all, delete-orphan")

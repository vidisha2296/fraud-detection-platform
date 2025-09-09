# # backend/app/models/fraud_alert.py
# from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey
# from sqlalchemy.orm import relationship
# from app.core.database import Base
# from datetime import datetime
# import uuid
# from app.core.database import Base

# class FraudAlert(Base):
#     __tablename__ = "fraud_alerts"

#     id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
#     customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False)
#     txn_id = Column(String, ForeignKey("transactions.txn_id"), nullable=True)
#     score = Column(Float, nullable=False)
#     reasons = Column(JSON, nullable=False)
#     action_taken = Column(String, nullable=True)
#     timestamp = Column(DateTime, default=datetime.utcnow)

#     # Relationships
#     customer = relationship("Customer", back_populates="fraud_alerts")
#     transaction = relationship("Transaction", back_populates="fraud_alerts")

#     def __repr__(self):
#         return f"<FraudAlert(customer_id={self.customer_id}, score={self.score})>"


from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, nullable=False)
    txn_id = Column(String, nullable=True)  # removed FK
    score = Column(Float, nullable=False)
    reasons = Column(JSON, nullable=False)
    action_taken = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="fraud_alerts")
    transaction = relationship("Transaction", primaryjoin="Transaction.txn_id==FraudAlert.txn_id", viewonly=True)

# # backend/app/models/action.py
# from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
# from sqlalchemy.orm import relationship
# from app.core.database import Base
# from datetime import datetime
# from app.core.database import Base

# class Action(Base):
#     __tablename__ = "actions"

#     id = Column(String, primary_key=True, index=True)
#     customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False)
#     txn_id = Column(String, ForeignKey("transactions.txn_id"), nullable=True)
#     action_type = Column(String, nullable=False)
#     details = Column(JSON, nullable=True)
#     status = Column(String, default="pending")
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     # Relationships
#     customer = relationship("Customer", back_populates="actions")
#     transaction = relationship("Transaction", back_populates="actions")

#     def __repr__(self):
#         return f"<Action(id={self.id}, type={self.action_type}, status={self.status})>"



from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Action(Base):
    __tablename__ = "actions"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, nullable=False)
    txn_id = Column(String, nullable=True)  # removed FK
    action_type = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="actions")
    transaction = relationship("Transaction", primaryjoin="Transaction.txn_id==Action.txn_id", viewonly=True)

    def __repr__(self):
        return f"<Action(id={self.id}, type={self.action_type}, status={self.status})>"

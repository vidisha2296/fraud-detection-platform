# from sqlalchemy import Column, String, Float, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from app.core.database import Base
# from datetime import datetime

# class Transaction(Base):
#     __tablename__ = "transactions"

#     id = Column(String, primary_key=True, index=True)
#     customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False)
#     txn_id = Column(String, index=True, nullable=False, unique=True)
#     merchant = Column(String, nullable=False)
#     category = Column(String, nullable=True)
#     amount = Column(Float, nullable=False)
#     currency = Column(String, default="USD", nullable=False)
#     mcc = Column(String, nullable=True)
#     timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

#     # Relationships
#     customer = relationship("Customer", back_populates="transactions")
#     actions = relationship("Action", back_populates="transaction", cascade="all, delete-orphan")
#     fraud_alerts = relationship("FraudAlert", back_populates="transaction", cascade="all, delete-orphan")

#     def __repr__(self):
#         return f"<Transaction(customer_id={self.customer_id}, txn_id={self.txn_id}, amount={self.amount})>"


# from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
# from sqlalchemy.orm import relationship
# from app.core.database import Base
# from datetime import datetime

# class Transaction(Base):
#     __tablename__ = "transactions"
#     __table_args__ = (
#         # Indexes for fast lookups
#         Index("idx_transactions_customer_id", "customer_id"),
#         Index("idx_transactions_txn_id", "txn_id"),
#         Index("idx_transactions_timestamp", "timestamp"),
#         # Partitioning hint for Postgres (ignored by SQLite)
#         {"postgresql_partition_by": "RANGE (timestamp)"}
#     )

#     id = Column(String, primary_key=True, index=True)
#     customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False)
#     txn_id = Column(String, index=True, nullable=False, unique=True)
#     merchant = Column(String, nullable=False)
#     category = Column(String, nullable=True)
#     amount = Column(Float, nullable=False)
#     currency = Column(String, default="USD", nullable=False)
#     mcc = Column(String, nullable=True)
#     timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

#     # Relationships
#     customer = relationship("Customer", back_populates="transactions")
#     actions = relationship("Action", back_populates="transaction", cascade="all, delete-orphan")
#     fraud_alerts = relationship("FraudAlert", back_populates="transaction", cascade="all, delete-orphan")

#     def __repr__(self):
#         return f"<Transaction(customer_id={self.customer_id}, txn_id={self.txn_id}, amount={self.amount})>"

# # backend/app/models/transaction.py
# from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
# from sqlalchemy.orm import relationship
# from app.core.database import Base
# from datetime import datetime

# class Transaction(Base):
#     __tablename__ = "transactions"
#     __table_args__ = (
#         Index("idx_transactions_customer_id", "customer_id"),
#         Index("idx_transactions_txn_id", "txn_id"),
#         Index("idx_transactions_timestamp", "timestamp"),
#         {"postgresql_partition_by": "RANGE (timestamp)"}
#     )

#     id = Column(String, primary_key=True, index=True)
#     customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False)
#     txn_id = Column(String, nullable=False, unique=True, index=True)  # ✅ must be unique if referenced
#     merchant = Column(String, nullable=False)
#     category = Column(String, nullable=True)
#     amount = Column(Float, nullable=False)
#     currency = Column(String, default="USD", nullable=False)
#     mcc = Column(String, nullable=True)
#     timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

#     # Relationships
#     customer = relationship("Customer", back_populates="transactions")
#     actions = relationship("Action", back_populates="transaction", cascade="all, delete-orphan")
#     fraud_alerts = relationship("FraudAlert", back_populates="transaction", cascade="all, delete-orphan")

#     def __repr__(self):
#         return f"<Transaction(customer_id={self.customer_id}, txn_id={self.txn_id}, amount={self.amount})>"


from sqlalchemy import Column, String, Float, DateTime, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        Index("idx_transactions_customer_id", "customer_id"),
        Index("idx_transactions_txn_id", "txn_id", "timestamp"),
        {"postgresql_partition_by": "RANGE (timestamp)"}
    )

    id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=False)
    txn_id = Column(String, nullable=False)  # cannot FK to partitioned table
    merchant = Column(String, nullable=False)
    category = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD", nullable=False)
    mcc = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, primary_key=True)

    # Relationships
    customer = relationship("Customer", back_populates="transactions")
    actions = relationship("Action", back_populates="transaction", cascade="all, delete-orphan")
    fraud_alerts = relationship("FraudAlert", back_populates="transaction", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Transaction(customer_id={self.customer_id}, txn_id={self.txn_id}, amount={self.amount})>"

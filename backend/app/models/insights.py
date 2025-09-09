# # backend/app/models/insights.py
# from sqlalchemy import Column, String, JSON, DateTime, ForeignKey
# from sqlalchemy.orm import relationship
# from app.core.database import Base
# from datetime import datetime
# from app.core.database import Base

# class Insight(Base):
#     __tablename__ = "insights"

#     id = Column(String, primary_key=True, index=True)
#     customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False)
#     type = Column(String, nullable=False)
#     data = Column(JSON, nullable=False)
#     generated_at = Column(DateTime, default=datetime.utcnow)

#     # Relationship
#     customer = relationship("Customer", back_populates="insights")
from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class Insight(Base):
    __tablename__ = "insights"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, nullable=False)
    type = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    customer = relationship("Customer", back_populates="insights")

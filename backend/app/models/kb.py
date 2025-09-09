# app/models/kb.py
from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import uuid
from app.core.database import Base

class KBEntry(Base):
    __tablename__ = "kb_entries"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)        # Short description
    snippet = Column(String, nullable=False)      # Text snippet
    anchors = Column(JSON, nullable=True)         # Optional metadata/tags
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<KBEntry(id={self.id}, title={self.title})>"

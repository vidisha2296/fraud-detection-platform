# # app/core/database.py
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from app.core.config import settings

# # Create SQLAlchemy engine
# engine = create_engine(settings.database_url, echo=True)

# # Session factory
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Base class for models
# Base = declarative_base()

# # Dependency for FastAPI routes
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# app/core/database.py
from sqlalchemy import create_engine, event, text
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from datetime import datetime

# Create SQLAlchemy engine
engine = create_engine(settings.database_url, echo=True, future=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------
# Optional: Partition Helper
# ---------------------------
def create_month_partition(table_name: str, year: int, month: int):
    """
    Create a partition table for the given year/month if it does not exist.
    Uses Postgres RANGE partitioning strategy on YYYYMM of timestamp.
    """
    partition_table = f"{table_name}_{year}{month:02d}"
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    partition_range_start = year * 100 + month
    partition_range_end = next_year * 100 + next_month

    with engine.connect() as conn:
        conn.execute(
            text(f"""
            CREATE TABLE IF NOT EXISTS {partition_table}
            PARTITION OF {table_name}
            FOR VALUES FROM ({partition_range_start}) TO ({partition_range_end});
            """)
        )

# Optional: Auto-create partition on insert (event listener)
def attach_partition_listener(table_name: str):
    """
    Attach a listener to automatically create a monthly partition before insert.
    Only works if you use SQLAlchemy ORM insert.
    """

    @event.listens_for(SessionLocal, "before_flush")
    def before_flush(session, flush_context, instances):
        for obj in session.new:
            if hasattr(obj, "timestamp") and hasattr(obj, "__tablename__") and obj.__tablename__ == table_name:
                year = obj.timestamp.year
                month = obj.timestamp.month
                create_month_partition(table_name, year, month)

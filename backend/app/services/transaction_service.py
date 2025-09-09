# from sqlalchemy.orm import Session
# from app.models.transaction import Transaction
# from app.schemas.transaction import TransactionCreate, TransactionRead
# from typing import List
# from datetime import datetime, timedelta
# from app.core.database import engine, create_month_partition
# from app.services.risk_service import RiskService  # hypothetical risk service
# from app.core.sse import sse  # SSE manager
# import asyncio


# class TransactionService:

#     @staticmethod
#     async def create_transaction(db: Session, txn_data: TransactionCreate) -> TransactionRead:
#         def _create_sync():
#             existing_txn = db.query(Transaction).filter_by(
#                 customer_id=txn_data.customer_id,
#                 txn_id=txn_data.txn_id
#             ).first()
#             if existing_txn:
#                 return TransactionRead.from_orm(existing_txn)

#             if engine.dialect.name == "postgresql":
#                 ts = txn_data.timestamp or datetime.utcnow()
#                 create_month_partition("transactions", ts.year, ts.month)

#             txn = Transaction(**txn_data.dict())
#             db.add(txn)
#             db.commit()
#             db.refresh(txn)
#             return TransactionRead.from_orm(txn)

#         return await asyncio.to_thread(_create_sync)

#     @staticmethod
#     async def get_transactions_by_customer(db: Session, customer_id: str) -> List[TransactionRead]:
#         def _fetch_sync():
#             txns = db.query(Transaction).filter_by(customer_id=customer_id).all()
#             return [TransactionRead.from_orm(txn) for txn in txns]

#         return await asyncio.to_thread(_fetch_sync)

#     @staticmethod
#     async def get_transaction(db: Session, txn_id: str) -> TransactionRead | None:
#         def _fetch_sync():
#             txn = db.query(Transaction).filter_by(txn_id=txn_id).first()
#             return TransactionRead.from_orm(txn) if txn else None

#         return await asyncio.to_thread(_fetch_sync)

#     @staticmethod
#     async def ingest_transactions(db: Session, records: List[TransactionCreate]) -> List[TransactionRead]:

#         async def _evaluate_risk(customer_id: str, txn_id: str):
#             try:
#                 risk_level = await asyncio.wait_for(
#                     RiskService.evaluate(customer_id, txn_id), timeout=2.0
#                 )
#                 return risk_level, False
#             except Exception:
#                 # Fallback case
#                 await sse.publish(
#                     {"customer_id": customer_id, "txn_id": txn_id},
#                     type="fallback_triggered"
#                 )
#                 return "medium", True

#         def _ingest_sync_partial(record: TransactionCreate):
#             now = record.timestamp or datetime.utcnow()
#             twenty_four_hr_ago = now - timedelta(hours=24)

#             # Check for exact duplicate (pending vs captured)
#             duplicate_txn = db.query(Transaction).filter(
#                 Transaction.customer_id == record.customer_id,
#                 Transaction.merchant == record.merchant,
#                 Transaction.amount == record.amount,
#                 Transaction.timestamp >= twenty_four_hr_ago
#             ).first()

#             if duplicate_txn:
#                 txn = duplicate_txn
#                 # Add KB explanation via SSE
#                 asyncio.create_task(sse.publish({
#                     "customer_id": record.customer_id,
#                     "txn_id": txn.txn_id,
#                     "explanation": "Duplicate detected: preauth vs capture",
#                     "kb_agent": "KB Agent"
#                 }, type="kb_explanation"))
#                 # Downgrade risk
#                 txn.details = txn.details or {}
#                 txn.details.update({"risk_level": "low", "duplicate_detected": True})
#             else:
#                 if engine.dialect.name == "postgresql":
#                     create_month_partition("transactions", now.year, now.month)
#                 txn = Transaction(**record.dict())
#                 db.add(txn)

#             return txn

#         results: List[TransactionRead] = []

#         for record in records:
#             txn_obj = await asyncio.to_thread(_ingest_sync_partial, record)
#             # Risk evaluation only if not duplicate
#             if not txn_obj.details.get("duplicate_detected", False):
#                 risk_level, fallback_used = await _evaluate_risk(record.customer_id, record.txn_id)
#                 details = dict(txn_obj.details or {})
#                 details.update({"risk_level": risk_level, "fallbackUsed": fallback_used})
#                 txn_obj.details = details

#             db.add(txn_obj)
#             db.commit()
#             db.refresh(txn_obj)
#             results.append(TransactionRead.from_orm(txn_obj))

#         return results


#     @staticmethod
#     async def get_transactions_by_customer_last_90d(db, customer_id: str) -> List[TransactionRead]:
#         def _fetch_sync():
#             end = datetime.utcnow()
#             start = end - timedelta(days=90)
#             txns = db.query(Transaction).filter(
#                 Transaction.customer_id == customer_id,
#                 Transaction.timestamp >= start,
#                 Transaction.timestamp <= end
#             ).all()
#             return [TransactionRead.from_orm(t) for t in txns]
#         return await asyncio.to_thread(_fetch_sync)

from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionRead
from typing import List
from datetime import datetime, timedelta
from app.core.database import engine, create_month_partition
from app.services.risk_service import RiskService  # hypothetical risk service
from app.core.sse import sse  # SSE manager
import asyncio


class TransactionService:

    @staticmethod
    async def create_transaction(db: Session, txn_data: TransactionCreate) -> TransactionRead:
        def _create_sync():
            existing_txn = db.query(Transaction).filter_by(
                customer_id=txn_data.customer_id,
                txn_id=txn_data.txn_id
            ).first()
            if existing_txn:
                return TransactionRead.from_orm(existing_txn)

            if engine.dialect.name == "postgresql":
                ts = txn_data.timestamp or datetime.utcnow()
                create_month_partition("transactions", ts.year, ts.month)

            txn = Transaction(**txn_data.dict())
            db.add(txn)
            db.commit()
            db.refresh(txn)
            return TransactionRead.from_orm(txn)

        return await asyncio.to_thread(_create_sync)

    @staticmethod
    async def get_transactions_by_customer(db: Session, customer_id: str) -> List[TransactionRead]:
        def _fetch_sync():
            txns = db.query(Transaction).filter_by(
                customer_id=customer_id).all()
            return [TransactionRead.from_orm(txn) for txn in txns]

        return await asyncio.to_thread(_fetch_sync)

    @staticmethod
    async def get_transaction(db: Session, txn_id: str) -> TransactionRead | None:
        def _fetch_sync():
            txn = db.query(Transaction).filter_by(txn_id=txn_id).first()
            return TransactionRead.from_orm(txn) if txn else None

        return await asyncio.to_thread(_fetch_sync)

    @staticmethod
    async def ingest_transactions(db: Session, records: List[TransactionCreate]) -> List[TransactionRead]:

        async def _evaluate_risk(customer_id: str, txn_id: str):
            try:
                risk_level = await asyncio.wait_for(
                    RiskService.evaluate(customer_id, txn_id), timeout=2.0
                )
                return risk_level, False
            except Exception:
                # Fallback case
                await sse.publish(
                    {"customer_id": customer_id, "txn_id": txn_id},
                    type="fallback_triggered"
                )
                return "medium", True

        def _ingest_sync_partial(record: TransactionCreate):
            now = record.timestamp or datetime.utcnow()
            twenty_four_hr_ago = now - timedelta(hours=24)

            # Check for exact duplicate (pending vs captured)
            duplicate_txn = db.query(Transaction).filter(
                Transaction.customer_id == record.customer_id,
                Transaction.merchant == record.merchant,
                Transaction.amount == record.amount,
                Transaction.timestamp >= twenty_four_hr_ago
            ).first()

            if duplicate_txn:
                txn = duplicate_txn
                # Add KB explanation via SSE
                asyncio.create_task(sse.publish({
                    "customer_id": record.customer_id,
                    "txn_id": txn.txn_id,
                    "explanation": "Duplicate detected: preauth vs capture",
                    "kb_agent": "KB Agent"
                }, type="kb_explanation"))
                # Downgrade risk
                txn.details = txn.details or {}
                txn.details.update(
                    {"risk_level": "low", "duplicate_detected": True})
            else:
                if engine.dialect.name == "postgresql":
                    create_month_partition("transactions", now.year, now.month)
                txn = Transaction(**record.dict())
                db.add(txn)

            return txn

        results: List[TransactionRead] = []

        for record in records:
            txn_obj = await asyncio.to_thread(_ingest_sync_partial, record)
            # Risk evaluation only if not duplicate
            if not txn_obj.details.get("duplicate_detected", False):
                risk_level, fallback_used = await _evaluate_risk(record.customer_id, record.txn_id)
                details = dict(txn_obj.details or {})
                details.update({"risk_level": risk_level,
                               "fallbackUsed": fallback_used})
                txn_obj.details = details

            db.add(txn_obj)
            db.commit()
            db.refresh(txn_obj)
            results.append(TransactionRead.from_orm(txn_obj))

        return results

    # -----------------------------------------
    # Old (non-paginated) implementation
    # -----------------------------------------
    # @staticmethod
    # async def get_transactions_by_customer_last_90d(db, customer_id: str) -> List[TransactionRead]:
    #     def _fetch_sync():
    #         end = datetime.utcnow()
    #         start = end - timedelta(days=90)
    #
    #         txns = db.query(Transaction).filter(
    #             Transaction.customer_id == customer_id,
    #             Transaction.timestamp >= start,
    #             Transaction.timestamp <= end
    #         ).all()
    #
    #         transactions_data = []
    #         for txn in txns:
    #             txn_dict = {col.name: getattr(txn, col.name) for col in txn.__table__.columns}
    #             txn_dict.pop('_sa_instance_state', None)
    #             transactions_data.append(TransactionRead(**txn_dict))
    #
    #         return transactions_data
    #
    #     return await asyncio.to_thread(_fetch_sync)

    # -----------------------------------------
    # New (paginated) implementation
    # -----------------------------------------
    @staticmethod
    async def get_transactions_by_customer_last_90d(
        db, customer_id: str, skip: int = 0, limit: int = 10
    ) -> List[TransactionRead]:
        def _fetch_sync():
            end = datetime.utcnow()
            start = end - timedelta(days=90)

            txns = (
                db.query(Transaction)
                .filter(
                    Transaction.customer_id == customer_id,
                    Transaction.timestamp >= start,
                    Transaction.timestamp <= end
                )
                .order_by(Transaction.timestamp.desc())  # newest first
                .offset(skip)
                .limit(limit)
                .all()
            )

            transactions_data = []
            for txn in txns:
                txn_dict = {col.name: getattr(txn, col.name)
                            for col in txn.__table__.columns}
                txn_dict.pop("_sa_instance_state", None)
                transactions_data.append(TransactionRead(**txn_dict))

            return transactions_data

        return await asyncio.to_thread(_fetch_sync)








# from sqlalchemy.orm import Session, selectinload
# from sqlalchemy import desc
# from app.models.transaction import Transaction
# from app.schemas.transaction import TransactionCreate, TransactionRead
# from typing import List, Optional
# from datetime import datetime, timedelta
# from app.core.database import engine, create_month_partition
# from app.services.risk_service import RiskService  # hypothetical risk service
# from app.core.sse import sse  # SSE manager
# from app.core.redis import get_redis_client  # Correct
# import asyncio
# import json
# import logging

# logger = logging.getLogger(__name__)

# class TransactionService:

#     @staticmethod
#     async def create_transaction(db: Session, txn_data: TransactionCreate) -> TransactionRead:
#         def _create_sync():
#             existing_txn = db.query(Transaction).filter_by(
#                 customer_id=txn_data.customer_id,
#                 txn_id=txn_data.txn_id
#             ).first()
#             if existing_txn:
#                 return TransactionRead.from_orm(existing_txn)

#             if engine.dialect.name == "postgresql":
#                 ts = txn_data.timestamp or datetime.utcnow()
#                 create_month_partition("transactions", ts.year, ts.month)

#             txn = Transaction(**txn_data.dict())
#             db.add(txn)
#             db.commit()
#             db.refresh(txn)
#             return TransactionRead.from_orm(txn)

#         return await asyncio.to_thread(_create_sync)

#     @staticmethod
#     async def get_transactions_by_customer(db: Session, customer_id: str, skip: int = 0, limit: int = 100) -> List[TransactionRead]:
#         def _fetch_sync():
#             txns = db.query(
#                 Transaction.id,
#                 Transaction.customer_id,
#                 Transaction.txn_id,
#                 Transaction.amount,
#                 Transaction.currency,
#                 Transaction.merchant,
#                 Transaction.category,
#                 Transaction.mcc,
#                 Transaction.timestamp
#             ).filter_by(customer_id=customer_id
#             ).order_by(desc(Transaction.timestamp)
#             ).offset(skip).limit(limit).all()

#             return [TransactionRead(**txn._asdict()) for txn in txns]

#         return await asyncio.to_thread(_fetch_sync)

#     @staticmethod
#     async def get_transaction(db: Session, txn_id: str) -> Optional[TransactionRead]:
#         def _fetch_sync():
#             txn = db.query(
#                 Transaction.id,
#                 Transaction.customer_id,
#                 Transaction.txn_id,
#                 Transaction.amount,
#                 Transaction.currency,
#                 Transaction.merchant,
#                 Transaction.category,
#                 Transaction.mcc,
#                 Transaction.timestamp
#             ).filter_by(txn_id=txn_id).first()

#             return TransactionRead(**txn._asdict()) if txn else None

#         return await asyncio.to_thread(_fetch_sync)

#     @staticmethod
#     async def ingest_transactions(db: Session, records: List[TransactionCreate]) -> List[TransactionRead]:
#         async def _evaluate_risk(customer_id: str, txn_id: str):
#             try:
#                 risk_level = await asyncio.wait_for(
#                     RiskService.evaluate(customer_id, txn_id), timeout=2.0
#                 )
#                 return risk_level, False
#             except Exception as e:
#                 logger.warning(f"Risk evaluation failed for {customer_id}/{txn_id}: {e}")
#                 await sse.publish(
#                     {"customer_id": customer_id, "txn_id": txn_id},
#                     type="fallback_triggered"
#                 )
#                 return "medium", True

#         def _ingest_sync_partial(record: TransactionCreate):
#             now = record.timestamp or datetime.utcnow()
#             twenty_four_hr_ago = now - timedelta(hours=24)

#             # Check for exact duplicate (pending vs captured)
#             duplicate_txn = db.query(Transaction).filter(
#                 Transaction.customer_id == record.customer_id,
#                 Transaction.merchant == record.merchant,
#                 Transaction.amount == record.amount,
#                 Transaction.timestamp >= twenty_four_hr_ago
#             ).first()

#             if duplicate_txn:
#                 txn = duplicate_txn
#                 asyncio.create_task(sse.publish({
#                     "customer_id": record.customer_id,
#                     "txn_id": txn.txn_id,
#                     "explanation": "Duplicate detected: preauth vs capture",
#                     "kb_agent": "KB Agent"
#                 }, type="kb_explanation"))
#                 txn.details = txn.details or {}
#                 txn.details.update({"risk_level": "low", "duplicate_detected": True})
#                 return txn, True
#             else:
#                 if engine.dialect.name == "postgresql":
#                     create_month_partition("transactions", now.year, now.month)
#                 txn = Transaction(**record.dict())
#                 db.add(txn)
#                 return txn, False

#         results: List[TransactionRead] = []
#         txns_to_commit = []

#         for record in records:
#             txn_obj, is_duplicate = await asyncio.to_thread(_ingest_sync_partial, record)

#             if not is_duplicate:
#                 risk_level, fallback_used = await _evaluate_risk(record.customer_id, record.txn_id)
#                 details = txn_obj.details or {}
#                 details.update({"risk_level": risk_level, "fallbackUsed": fallback_used})
#                 txn_obj.details = details

#             txns_to_commit.append(txn_obj)

#         # Bulk commit for better performance
#         try:
#             db.commit()
#             for txn_obj in txns_to_commit:
#                 db.refresh(txn_obj)
#                 results.append(TransactionRead(
#                     id=txn_obj.id,
#                     customer_id=txn_obj.customer_id,
#                     txn_id=txn_obj.txn_id,
#                     amount=txn_obj.amount,
#                     currency=txn_obj.currency,
#                     merchant=txn_obj.merchant,
#                     category=txn_obj.category,
#                     mcc=txn_obj.mcc,
#                     timestamp=txn_obj.timestamp
#                 ))
#         except Exception as e:
#             db.rollback()
#             logger.error(f"Failed to commit transactions: {e}")
#             raise

#         return results

#     @staticmethod
#     async def get_transactions_by_customer_last_90d(
#         db: Session,
#         customer_id: str,
#         skip: int = 0,
#         limit: int = 100
#     ) -> List[TransactionRead]:
#         # Check cache first
#         cache_key = f"txns_90d:{customer_id}:{skip}:{limit}"
#         cached_data = get_redis_client.cache_get(cache_key)

#         if cached_data:
#             logger.info(f"Cache hit for {cache_key}")
#             return [TransactionRead(**item) for item in json.loads(cached_data)]

#         def _fetch_sync():
#             end = datetime.utcnow()
#             start = end - timedelta(days=90)

#             # Select only needed columns for better performance
#             txns = db.query(
#                 Transaction.id,
#                 Transaction.customer_id,
#                 Transaction.txn_id,
#                 Transaction.amount,
#                 Transaction.currency,
#                 Transaction.merchant,
#                 Transaction.category,
#                 Transaction.mcc,
#                 Transaction.timestamp
#             ).filter(
#                 Transaction.customer_id == customer_id,
#                 Transaction.timestamp >= start,
#                 Transaction.timestamp <= end
#             ).order_by(desc(Transaction.timestamp)
#             ).offset(skip).limit(limit).all()

#             # Convert to TransactionRead objects
#             transactions_data = []
#             for txn in txns:
#                 transactions_data.append(TransactionRead(
#                     id=txn.id,
#                     customer_id=txn.customer_id,
#                     txn_id=txn.txn_id,
#                     amount=txn.amount,
#                     currency=txn.currency,
#                     merchant=txn.merchant,
#                     category=txn.category,
#                     mcc=txn.mcc,
#                     timestamp=txn.timestamp
#                 ))

#             return transactions_data

#         result = await asyncio.to_thread(_fetch_sync)

#         # Cache the result for 5 minutes
#         try:
#             get_redis_client.cache_set(
#                 cache_key,
#                 json.dumps([item.dict() for item in result]),
#                 expire=300
#             )
#         except Exception as e:
#             logger.warning(f"Failed to cache data: {e}")

#         return result

#     @staticmethod
#     async def get_transactions_count_last_90d(db: Session, customer_id: str) -> int:
#         """Get total count of transactions for pagination"""
#         cache_key = f"txns_count_90d:{customer_id}"
#         cached_count = get_redis_client.cache_get(cache_key)

#         if cached_count:
#             return int(cached_count)

#         def _fetch_sync():
#             end = datetime.utcnow()
#             start = end - timedelta(days=90)

#             count = db.query(Transaction).filter(
#                 Transaction.customer_id == customer_id,
#                 Transaction.timestamp >= start,
#                 Transaction.timestamp <= end
#             ).count()

#             return count

#         result = await asyncio.to_thread(_fetch_sync)

#         # Cache count for 1 minute (shorter TTL since counts change more frequently)
#         get_redis_client.cache_set(cache_key, str(result), expire=60)

#         return result

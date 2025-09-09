from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.insights import Insight
from collections import defaultdict
from typing import Dict, List, Any
from datetime import datetime
import uuid
import asyncio
from app.core.sse import sse  # ✅ SSE manager


class InsightsService:

    @staticmethod
    async def spend_categories(db: Session, customer_id: str) -> Dict[str, float]:
        def _query():
            txns: List[Transaction] = (
                db.query(Transaction)
                .filter_by(customer_id=customer_id)
                .all()
            )
            categories: Dict[str, float] = defaultdict(float)
            for txn in txns:
                # ✅ Ensure category is always a string
                category = (txn.category or "Uncategorized").strip()
                categories[category] += txn.amount
            return dict(categories)

        categories = await asyncio.to_thread(_query)

        # 🔔 Push SSE safely
        if sse:
            try:
                await sse.publish(
                    {
                        "event": "spend_categories",
                        "customer_id": customer_id,
                        "categories": categories,
                    },
                    type="insight",
                )
            except Exception as e:
                print(f"SSE publish failed (spend_categories): {e}")

        return categories


    @staticmethod
    async def top_merchants(db: Session, customer_id: str, limit: int = 5) -> List[tuple[str, float]]:
        def _query():
            txns: List[Transaction] = db.query(Transaction).filter_by(customer_id=customer_id).all()
            merchants: Dict[str, float] = defaultdict(float)
            for txn in txns:
                merchants[txn.merchant] += txn.amount
            sorted_merchants = sorted(merchants.items(), key=lambda x: x[1], reverse=True)
            return sorted_merchants[:limit]

        sorted_merchants = await asyncio.to_thread(_query)

        # 🔔 Push SSE safely
        if sse:
            try:
                await sse.publish(
                    {
                        "event": "top_merchants",
                        "customer_id": customer_id,
                        "merchants": sorted_merchants
                    },
                    type="insight"
                )
            except Exception as e:
                print(f"SSE publish failed (top_merchants): {e}")

        return sorted_merchants

    @staticmethod
    async def save_insight(db: Session, customer_id: str, insight_type: str, data: Any) -> Insight:
        def _save():
            insight = Insight(
                id=str(uuid.uuid4()),
                customer_id=customer_id,
                type=insight_type,
                data=data,
                generated_at=datetime.utcnow()
            )
            db.add(insight)
            db.commit()
            db.refresh(insight)
            return insight

        insight = await asyncio.to_thread(_save)

        # 🔔 Push SSE safely
        if sse:
            try:
                await sse.publish(
                    {
                        "event": "insight_saved",
                        "customer_id": customer_id,
                        "insight_type": insight_type,
                        "data": data
                    },
                    type="insight"
                )
            except Exception as e:
                print(f"SSE publish failed (save_insight): {e}")

        return insight

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple

from app.services.insights_service import InsightsService
from app.schemas.insight import InsightRead
from app.core.database import get_db
from app.core.rate_limiter import rate_limit  # Redis rate limiter
from app.core.sse import sse  # ✅ SSE manager

router = APIRouter(prefix="", tags=["Insights"])


# -------------------------
# Total spend per category
# -------------------------
@router.get("/{customer_id}/categories", response_model=Dict[str, float])
@rate_limit(max_requests=10, window_seconds=60)
async def get_categories(
    customer_id: str,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Return total spend per category for the customer.
    Also pushes SSE event.
    """
    categories = await InsightsService.spend_categories(db, customer_id)

    # 🔔 Push SSE event explicitly from API (safe)
    if sse:
        try:
            await sse.publish(
                {
                    "event": "api_categories",
                    "customer_id": customer_id,
                    "categories": categories,
                },
                type="insight",
            )
        except Exception as e:
            print(f"SSE publish failed (api_categories): {e}")

    return categories



# -------------------------
# Top merchants by spend
# -------------------------
@router.get("/{customer_id}/top-merchants", response_model=List[Tuple[str, float]])
@rate_limit(max_requests=10, window_seconds=60)
async def get_top_merchants(
    customer_id: str,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Return top merchants by spend for the customer.
    Also pushes SSE event.
    """
    merchants = await InsightsService.top_merchants(db, customer_id)

    # 🔔 Push SSE event explicitly from API (safe)
    if sse:
        try:
            await sse.publish(
                {
                    "event": "api_top_merchants",
                    "customer_id": customer_id,
                    "merchants": merchants,
                },
                type="insight",
            )
        except Exception as e:
            print(f"SSE publish failed (api_top_merchants): {e}")

    return merchants

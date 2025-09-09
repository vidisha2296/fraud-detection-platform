from fastapi import APIRouter, Depends, Request, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.services.kb_service import KBService
from app.services.action_service import ActionService
from app.schemas.action import ActionCreate, ActionRead, OTPVerify
from app.core.database import get_db
from app.core.rate_limiter import rate_limit
from app.core.sse import sse   # ✅ SSE manager

router = APIRouter(prefix="", tags=["Actions"])

# -------------------------
# Generic create
# -------------------------
@router.post("/", response_model=ActionRead)
@rate_limit(max_requests=5, window_seconds=60)
async def create_action(
    action: ActionCreate,
    db: Session = Depends(get_db),
    request: Request = None
):
    return await ActionService.create_action(db, action)


# -------------------------
# Get all actions for a customer
# -------------------------
@router.get("/customer/{customer_id}", response_model=List[ActionRead])
@rate_limit(max_requests=10, window_seconds=60)
async def get_actions_for_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    request: Request = None
):
    return await ActionService.get_actions_by_customer(db, customer_id)


# -------------------------
# Get single action by ID
# -------------------------
@router.get("/{action_id}", response_model=ActionRead)
@rate_limit(max_requests=10, window_seconds=60)
async def get_action(
    action_id: str,
    db: Session = Depends(get_db),
    request: Request = None
):
    action = await ActionService.get_action(db, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action


# -------------------------
# Freeze card (initiates OTP)
# -------------------------
@router.post("/freeze/{customer_id}/{txn_id}", response_model=ActionRead)
@rate_limit(max_requests=3, window_seconds=60)
async def freeze_card(
    customer_id: str,
    txn_id: str,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Freeze a customer's card for a specific transaction.
    """
    return await ActionService.freeze_card(db, customer_id)


# -------------------------
# Freeze card with risk assessment (fallback support)
# -------------------------
@router.post("/freeze/risk/{customer_id}", response_model=ActionRead)
@rate_limit(max_requests=3, window_seconds=60)
async def freeze_card_risk(
    customer_id: str,
    db: Session = Depends(get_db),
    request: Request = None
):
    action = await ActionService.freeze_card_with_risk(db, customer_id)
    # ✅ Publish SSE fallback event if triggered
    if action.details.get("fallbackUsed", False):
        await sse.publish(
            {"customer_id": customer_id, "action_id": str(action.id)},
            type="fallback_triggered"
        )
    return action


# -------------------------
# Verify OTP for freeze
# -------------------------
@router.post("/freeze/verify/{customer_id}/{action_id}", response_model=ActionRead)
@rate_limit(max_requests=3, window_seconds=60)
async def verify_freeze_otp(
    customer_id: str,
    action_id: str,
    otp_data: OTPVerify,
    db: Session = Depends(get_db),
    request: Request = None
):
    updated_action = await ActionService.verify_freeze_otp(db, customer_id, action_id, otp_data.otp)
    if not updated_action:
        raise HTTPException(status_code=400, detail="OTP verification failed")
    return updated_action


# -------------------------
# Dispute creation with KB trace and risk info
# -------------------------
@router.post("/dispute/{txn_id}", response_model=ActionRead)
@rate_limit(max_requests=3, window_seconds=60)
async def open_dispute(
    txn_id: str,
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Opens a dispute for a transaction:
    - Uses KB explanation if available, otherwise defaults.
    - Updates risk level.
    - Publishes SSE trace for frontend observability.
    """
    # Safe KB reference: default if none exists
    kb_reference = "No KB reference available"
    try:
        kb_results = await KBService.search_entries(db, query="How disputes work")
        if kb_results:
            kb_reference = kb_results[0].snippet
    except Exception:
        pass  # ignore if KB table empty

    # Risk evaluation placeholder
    risk_level = "medium"

    # Use empty string if customer unknown
    customer_id_safe = ""  # or "unknown"

    # Create the action
    action_data = ActionCreate(
        customer_id=customer_id_safe,  # must be string
        txn_id=txn_id,
        action_type="open_dispute",
        details={
            "reason": "Transaction disputed",
            "riskLevel": risk_level,
            "kb_reference": kb_reference
        }
    )

    # Call service to create action
    created_action = await ActionService.create_action(db, action_data)

    # SSE trace for frontend
    await sse.publish(
        {
            "event": "dispute_opened",
            "txn_id": txn_id,
            "risk_level": risk_level,
            "kb_reference": kb_reference
        },
        type="dispute_opened"
    )

    return created_action





# -------------------------
# Contact customer
# -------------------------
@router.post("/contact/{customer_id}", response_model=ActionRead)
@rate_limit(max_requests=5, window_seconds=60)
async def contact_customer(
    customer_id: str,
    db: Session = Depends(get_db),
    request: Request = None
):
    return await ActionService.contact_customer(db, customer_id)


# -------------------------
# Duplicate pending vs captured
# -------------------------
@router.post("/duplicate/{customer_id}/{txn_id}", response_model=ActionRead)
@rate_limit(max_requests=5, window_seconds=60)
async def handle_duplicate(
    customer_id: str,
    txn_id: str,
    description: str = Query(..., description="Description of duplicate transaction"),
    db: Session = Depends(get_db),
    request: Request = None
):
    """
    Handles duplicate transactions:
    - Provides KB explanation for preauth vs capture.
    - Downgrades risk.
    - Publishes SSE trace for KB usage.
    """
    return await ActionService.handle_duplicate(db, customer_id, txn_id, description)


# -------------------------
# SSE subscription (frontend listens here)
# -------------------------
@router.get("/events")
async def subscribe_events():
    return await sse.subscribe()

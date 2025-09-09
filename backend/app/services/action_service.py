from sqlalchemy.orm import Session
from app.models.action import Action
from app.models.transaction import Transaction
from app.schemas.action import ActionCreate, ActionRead
from app.core.otp_manager import OTPManager
from app.core.redactor import Redactor
from app.core.sse import sse
from app.services.kb_service import KBService
from app.services.risk_service import RiskService
from datetime import datetime
import uuid
import asyncio
import random

# In-memory metrics for demo
metrics = {"action_blocked_total": 0}


class ActionService:

    # ------------------------------
    # Generic action creation with optional txn_timestamp
    # ------------------------------
    @staticmethod
    async def create_action(
        db: Session, 
        action_data: ActionCreate, 
        txn_timestamp: datetime | None = None
    ) -> ActionRead:
        def _create():
            # REDACT PII in details
            details = {
                k: Redactor.mask_pii(str(v)) 
                for k, v in action_data.details.items()
            } if action_data.details else {}

            action = Action(
                id=str(uuid.uuid4()),
                customer_id=action_data.customer_id,
                txn_id=action_data.txn_id,
                action_type=action_data.action_type,
                details=details,
                status="pending",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                timestamp=txn_timestamp  # required for DB trigger
            )
            db.add(action)
            db.commit()
            db.refresh(action)
            return ActionRead.from_orm(action)

        created = await asyncio.to_thread(_create)

        # SSE publish
        await sse.publish(
            {"event": "action_created", "action": created.dict()},
            type="action_created"
        )
        return created

    # ------------------------------
    # Freeze card with OTP (txn_id unused)
    # ------------------------------
    @staticmethod
    async def freeze_card(
        db: Session, 
        customer_id: str
    ) -> ActionRead:
        # 1️⃣ Get any existing action for this customer
        action = db.query(Action).filter_by(customer_id=customer_id).first()

        # 2️⃣ Create new action if none exists
        if not action:
            details = {"reason": "Suspicious activity"}

            action_data = ActionCreate(
                customer_id=customer_id,
                txn_id=None,  # txn_id is not used
                action_type="freeze_card",
                details=details
            )
            action = await ActionService.create_action(db, action_data)

        # 3️⃣ Generate OTP (await if async)
        otp = await OTPManager.generate_otp(customer_id, action_id=action.id)

        # 4️⃣ Update action with masked OTP
        def _update_action():
            if action.details is None:
                action.details = {}
             # Make sure required fields are not None
            if not action.status:
                action.status = "pending"
            if not action.created_at:
                action.created_at = datetime.utcnow()
            if not action.updated_at:
               action.updated_at = datetime.utcnow()

            action.details["otp"] = Redactor.mask_pii(otp)
            db.add(action)
            db.commit()
            db.refresh(action)
            return ActionRead.from_orm(action)

        action_with_otp = await asyncio.to_thread(_update_action)

        # 5️⃣ Increment metric
        metrics["action_blocked_total"] += 1

        return action_with_otp

    # ------------------------------
    # Freeze card with risk check and fallback
    # ------------------------------
    @staticmethod
    async def freeze_card_with_risk(db: Session, customer_id: str) -> ActionRead:
        otp = await OTPManager.generate_otp(customer_id)
        fallback_used = False
        risk_level = "high"
        reason = "Suspicious activity"

        try:
            # Simulate risk service failure
            if random.random() < 0.3:
                raise Exception("Risk service unavailable")
        except Exception:
            fallback_used = True
            risk_level = "medium"
            reason += " (risk_unavailable, fallback applied)"
            await sse.publish(
                {
                    "event": "fallback_triggered",
                    "customer_id": customer_id,
                    "action_type": "freeze_card",
                    "risk_level": risk_level,
                    "reason": "risk_unavailable",
                    "fallbackUsed": True,
                },
                type="fallback_triggered"
            )

        details = {
            "reason": reason,
            "otp": Redactor.mask_pii(otp),
            "riskLevel": risk_level,
            "fallbackUsed": fallback_used
        }
        metrics["action_blocked_total"] += 1

        action_data = ActionCreate(
            customer_id=customer_id,
            action_type="freeze_card",
            details=details
        )
        return await ActionService.create_action(db, action_data)

    # ------------------------------
    # Verify OTP
    # ------------------------------
    @staticmethod
    async def verify_freeze_otp(
        db: Session, 
        customer_id: str, 
        action_id: str, 
        otp: str
    ) -> ActionRead | None:
        def _verify():
            action = db.query(Action).filter_by(id=action_id, customer_id=customer_id).first()
            if not action:
                return None
            if OTPManager.verify_otp(customer_id, otp):
                action.status = "FROZEN"
                action.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(action)
                if action.details is not None:
                    action.details = {
                        k: Redactor.mask_pii(str(v)) 
                        for k, v in action.details.items()
                    }
                else:
                    action.details = {}
                return ActionRead.from_orm(action)
            return None

        verified = await asyncio.to_thread(_verify)

        # SSE publish verification result
        event_type = "otp_verified" if verified else "otp_failed"
        await sse.publish(
            {
                "event": event_type,
                "customer_id": customer_id,
                "action_id": action_id,
                "status": "FROZEN" if verified else None
            },
            type=event_type
        )

        return verified

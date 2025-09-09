import json
import uuid
import random
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.fraud_alert import FraudAlert
from app.schemas.fraud_alert import FraudAlertCreate, FraudAlertRead
from app.core.redactor import Redactor
from app.core.sse import sse  # SSE manager
from app.models.transaction import Transaction  

# In-memory metrics example
metrics = {"alerts_created_total": 0}


class FraudService:

    @staticmethod
    def normalize_reasons(raw_reasons) -> list[str]:
        """Convert DB reasons column to list of strings"""
        if raw_reasons is None:
            return ["No specific reason provided"]
        
        reasons = []
        
        if isinstance(raw_reasons, list):
            for item in raw_reasons:
                if isinstance(item, dict):
                    if "reason" in item:
                        reasons.append(item["reason"])
                    else:
                        for value in item.values():
                            if isinstance(value, str):
                                reasons.append(value)
                elif isinstance(item, str):
                    reasons.append(item)
        
        elif isinstance(raw_reasons, dict):
            if "reason" in raw_reasons:
                reasons.append(raw_reasons["reason"])
            else:
                for value in raw_reasons.values():
                    if isinstance(value, str):
                        reasons.append(value)
        
        elif isinstance(raw_reasons, str):
            try:
                parsed = json.loads(raw_reasons)
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict) and "reason" in item:
                            reasons.append(item["reason"])
                elif isinstance(parsed, dict) and "reason" in parsed:
                    reasons.append(parsed["reason"])
            except json.JSONDecodeError:
                reasons.append(raw_reasons)
        
        if not reasons:
            reasons.append("No specific reason provided")
        
        return reasons

    @staticmethod
    async def create_alert(db: Session, alert_data: FraudAlertCreate) -> FraudAlertRead:
        def _create():
            customer_id = Redactor.mask_pii(alert_data.customer_id)
            txn_id = Redactor.mask_pii(alert_data.txn_id) if alert_data.txn_id else None

            db_reasons = []
            for reason in alert_data.reasons:
                if reason and reason != "No specific reason provided":
                    db_reasons.append({"reason": reason})
            if not db_reasons:
                db_reasons = [{"reason": "No specific reason provided"}]

            alert = FraudAlert(
                id=str(uuid.uuid4()),
                customer_id=customer_id,
                txn_id=txn_id,
                score=alert_data.score,
                reasons=db_reasons,
                action_taken=alert_data.action_taken,
                timestamp=alert_data.timestamp or datetime.utcnow()
            )

            db.add(alert)
            db.commit()
            db.refresh(alert)
            metrics["alerts_created_total"] += 1
            return alert

        alert = await asyncio.to_thread(_create)
        
        alert_dict = alert.__dict__.copy()
        alert_dict["reasons"] = FraudService.normalize_reasons(alert_dict.get("reasons"))
        alert_read = FraudAlertRead.model_validate(alert_dict)

        if sse:
            try:
                await sse.publish(
                    {"event": "fraud_alert_created", "alert": alert_read.model_dump()},
                    type="fraud"
                )
            except Exception as e:
                print(f"SSE publish failed: {e}")

        return alert_read

    @staticmethod
    async def get_alerts_by_customer(
        db: Session, customer_id: str, limit: int = 10, offset: int = 0
    ) -> tuple[list[FraudAlertRead], int]:

        def _query():
            query = db.query(FraudAlert).filter_by(customer_id=customer_id)
            total = query.count()
            alerts = (
                query.order_by(FraudAlert.timestamp.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )

            results = []
            for alert in alerts:
                alert_data = alert.__dict__.copy()
                alert_data["reasons"] = FraudService.normalize_reasons(alert_data.get("reasons"))
                results.append(FraudAlertRead.model_validate(alert_data))

            return results, total

        results, total = await asyncio.to_thread(_query)

        if sse:
            try:
                await sse.publish(
                    {
                        "event": "fraud_alerts_fetched",
                        "customer_id": Redactor.mask_pii(customer_id),
                        "count": len(results),
                    },
                    type="fraud",
                )
            except Exception as e:
                print(f"SSE publish failed: {e}")

        return results, total

    @staticmethod
    async def get_alert(db: Session, alert_id: str) -> FraudAlertRead | None:
        def _query():
            alert = db.query(FraudAlert).filter_by(id=alert_id).first()
            if not alert:
                return None
            
            alert_data = alert.__dict__.copy()
            alert_data["reasons"] = FraudService.normalize_reasons(alert_data.get("reasons"))
            return FraudAlertRead.model_validate(alert_data)

        return await asyncio.to_thread(_query)

    @staticmethod
    async def score(customer_id: str) -> dict:
        score = round(random.uniform(0, 1), 2)
        reasons = ["velocity", "device change"] if score > 0.7 else ["low risk"]
        action = "freeze_card" if score > 0.9 else None

        result = {
            "customerId": Redactor.mask_pii(customer_id),
            "score": score,
            "reasons": reasons,
            "action": action
        }

        if sse:
            try:
                await sse.publish(
                    {
                        "event": "fraud_score_generated",
                        "customer_id": Redactor.mask_pii(customer_id),
                        "score": score,
                        "reasons": reasons,
                        "action": action,
                    },
                    type="fraud"
                )
            except Exception as e:
                print(f"SSE publish failed: {e}")

        return result

    @staticmethod
    def evaluate_transaction(txn: dict) -> dict:
        if txn.get("mcc") == "6011":
            return {"flagged": True, "reason": "High-value cash withdrawal at unusual time/location"}
        if txn.get("amount", 0) < 0:
            return {"flagged": True, "reason": "Negative amount transaction"}
        return {"flagged": False}

    @staticmethod
    async def debug_alerts(db: Session, customer_id: str):
        """Debug method to inspect raw database data"""
        def _query():
            alerts = db.query(FraudAlert).filter_by(customer_id=customer_id).all()
            result = []
            for alert in alerts:
                result.append({
                    "id": alert.id,
                    "customer_id": alert.customer_id,
                    "reasons_raw": alert.reasons,
                    "reasons_type": str(type(alert.reasons)),
                    "normalized": FraudService.normalize_reasons(alert.reasons)
                })
            return result
        
        return await asyncio.to_thread(_query)

    @staticmethod
    async def get_customer_metrics(db: Session, customer_id: str) -> dict:
        # Total Spend
        total_spend = db.execute(
            text("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE customer_id = :cust_id"),
            {"cust_id": customer_id}
        ).scalar()

        # % High-Risk Alerts (score >= 80)
        high_risk_count, total_alerts = db.execute(
            text("""
                SELECT 
                    COUNT(*) FILTER (WHERE score >= 80),
                    COUNT(*)
                FROM fraud_alerts
                WHERE customer_id = :cust_id
            """),
            {"cust_id": customer_id}
        ).first()
        high_risk_pct = (high_risk_count / total_alerts * 100) if total_alerts else 0

        # Disputes Opened
        disputes_opened = db.execute(
            text("""
                SELECT COUNT(*) FROM fraud_alerts 
                WHERE customer_id = :cust_id AND action_taken = 'pending'
            """),
            {"cust_id": customer_id}
        ).scalar()

        # avgTriageTime - skip if resolved_at doesn't exist
        avg_triage_seconds = None
        if hasattr(FraudAlert, "resolved_at"):
            avg_triage_seconds = db.execute(
                text("""
                    SELECT AVG(EXTRACT(EPOCH FROM (resolved_at - timestamp)))
                    FROM fraud_alerts
                    WHERE customer_id = :cust_id
                """),
                {"cust_id": customer_id}
            ).scalar()

        return {
            "totalSpend": float(total_spend or 0),
            "highRiskPct": float(high_risk_pct),
            "disputesOpened": int(disputes_opened or 0),
            "avgTriageTime": float(avg_triage_seconds) if avg_triage_seconds else None
        }

# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List

# from app.services.fraud_service import FraudService
# from app.schemas.fraud_alert import FraudAlertCreate, FraudAlertRead
# from app.core.database import get_db

# router = APIRouter(prefix="/fraud", tags=["FraudAlerts"])

# # Create a new fraud alert
# @router.post("/", response_model=FraudAlertRead)
# def create_alert(alert: FraudAlertCreate, db: Session = Depends(get_db)):
#     return FraudService.create_alert(db, alert)

# # Get all fraud alerts for a customer
# @router.get("/customer/{customer_id}", response_model=List[FraudAlertRead])
# def get_alerts_for_customer(customer_id: str, db: Session = Depends(get_db)):
#     return FraudService.get_alerts_by_customer(db, customer_id)

# # Get single fraud alert by ID
# @router.get("/{alert_id}", response_model=FraudAlertRead)
# def get_alert(alert_id: str, db: Session = Depends(get_db)):
#     alert = FraudService.get_alert(db, alert_id)
#     if not alert:
#         raise HTTPException(status_code=404, detail="Fraud alert not found")
#     return alert

# # Dummy scoring endpoint
# @router.get("/score/{customer_id}")
# def fraud_score(customer_id: str):
#     return FraudService.score(customer_id)


# from fastapi import APIRouter, Depends, HTTPException, Request
# from sqlalchemy.orm import Session
# from typing import List

# from app.services.fraud_service import FraudService
# from app.schemas.fraud_alert import FraudAlertCreate, FraudAlertRead
# from app.core.database import get_db
# from app.core.rate_limiter import rate_limit  # Redis rate limiter
# from app.core.sse import sse  # ✅ SSE manager

# router = APIRouter(prefix="", tags=["Fraud Alerts"])

# # -------------------------
# # Create a new fraud alert
# # -------------------------
# @router.post("/", response_model=FraudAlertRead)
# @rate_limit(max_requests=5, window_seconds=60)
# async def create_alert(
#     alert: FraudAlertCreate,
#     db: Session = Depends(get_db),
#     request: Request = None
# ):
#     alert_read = await FraudService.create_alert(db, alert)

#     # 🔔 Push SSE event for frontend
#     await sse.publish(
#         {
#             "event": "fraud_alert_created",
#             "alert": alert_read.dict()
#         },
#         type="fraud"
#     )

#     return alert_read


# # -------------------------
# # Get all fraud alerts for a customer
# # -------------------------
# @router.get("/customer/{customer_id}", response_model=List[FraudAlertRead])
# @rate_limit(max_requests=10, window_seconds=60)
# async def get_alerts_for_customer(
#     customer_id: str,
#     db: Session = Depends(get_db),
#     request: Request = None
# ):
#     alerts = await FraudService.get_alerts_by_customer(db, customer_id)

#     # 🔔 SSE event for fetch
#     await sse.publish(
#         {
#             "event": "fraud_alerts_fetched",
#             "customer_id": customer_id,
#             "count": len(alerts)
#         },
#         type="fraud"
#     )

#     return alerts


# # -------------------------
# # Get single fraud alert by ID
# # -------------------------
# @router.get("/{alert_id}", response_model=FraudAlertRead)
# @rate_limit(max_requests=10, window_seconds=60)
# async def get_alert(
#     alert_id: str,
#     db: Session = Depends(get_db),
#     request: Request = None
# ):
#     alert = await FraudService.get_alert(db, alert_id)
#     if not alert:
#         raise HTTPException(status_code=404, detail="Fraud alert not found")

#     # 🔔 SSE event for single fetch
#     await sse.publish(
#         {
#             "event": "fraud_alert_fetched",
#             "alert_id": alert_id
#         },
#         type="fraud"
#     )

#     return alert


# # -------------------------
# # Dummy scoring endpoint
# # -------------------------
# @router.get("/score/{customer_id}")
# @rate_limit(max_requests=5, window_seconds=60)
# async def fraud_score(customer_id: str, request: Request = None):
#     score_data = await FraudService.score(customer_id)

#     # 🔔 SSE event for scoring
#     await sse.publish(
#         {
#             "event": "fraud_score_generated",
#             "customer_id": customer_id,
#             **score_data
#         },
#         type="fraud"
#     )

#     return score_data



# app/api/fraud_router.py
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import time
import os
from types import SimpleNamespace
from app.services.fraud_service import FraudService
from app.schemas.fraud_alert import FraudAlertCreate, FraudAlertRead
from app.core.database import get_db
from app.core.rate_limiter import rate_limit
from app.core.sse import sse
from app.agents.orchestrator import Orchestrator
from app.agents.redactor import RedactorAgent
from app.agents.summarizer import SummarizerAgent

# -------------------------
# Initialization
# -------------------------
router = APIRouter(prefix="", tags=["Fraud Alerts"])
orchestrator = Orchestrator()
redactor = RedactorAgent()
summarizer = SummarizerAgent()
TEST_MODE = os.getenv("TESTING") == "1"

# -------------------------
# Create a new fraud alert
# -------------------------
@router.post("/", response_model=FraudAlertRead)
@rate_limit(max_requests=5, window_seconds=60)
async def create_alert(
    alert: FraudAlertCreate,
    db: Session = Depends(get_db),
    request: Request = None
):
    alert_read = await FraudService.create_alert(db, alert)
    redacted_resp = await redactor.redact_pii(alert_read.dict())
    redacted_alert = redacted_resp.data if hasattr(redacted_resp, "data") else redacted_resp

    if sse:
        await sse.publish({"event": "fraud_alert_created", "alert": redacted_alert}, type="fraud")

    return redacted_alert

# -------------------------
# Get all fraud alerts for a customer
# -------------------------
@router.get("/customer/{customer_id}", response_model=Dict[str, Any])
@rate_limit(max_requests=10, window_seconds=60)
async def get_alerts_for_customer(
    customer_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    request: Request = None
):
    customer_id = customer_id.strip()
    offset = (page - 1) * limit

    alerts, total = await FraudService.get_alerts_by_customer(db, customer_id, limit=limit, offset=offset)

    redacted_alerts = []
    for a in alerts:
        redacted_resp = await redactor.redact_pii(a.model_dump())
        redacted_alerts.append(redacted_resp.data if hasattr(redacted_resp, "data") else redacted_resp)

    if sse:
        try:
            await sse.publish(
                {
                    "event": "fraud_alerts_fetched",
                    "customer_id": customer_id,
                    "count": len(redacted_alerts)
                },
                type="fraud"
            )
        except Exception as e:
            print(f"SSE publish failed: {e}")

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "items": redacted_alerts
    }

# -------------------------
# Get single fraud alert by ID
# -------------------------
@router.get("/{alert_id}", response_model=FraudAlertRead)
@rate_limit(max_requests=10, window_seconds=60)
async def get_alert(alert_id: str, db: Session = Depends(get_db), request: Request = None):
    alert = await FraudService.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Fraud alert not found")

    redacted_resp = await redactor.redact_pii(alert.dict())
    redacted_alert = redacted_resp.data if hasattr(redacted_resp, "data") else redacted_resp

    if sse:
        try:
            await sse.publish({"event": "fraud_alert_fetched", "alert_id": alert_id}, type="fraud")
        except Exception as e:
            print(f"SSE publish failed: {e}")

    return redacted_alert

# -------------------------
# Dummy scoring endpoint
# -------------------------
@router.get("/score/{customer_id}")
@rate_limit(max_requests=5, window_seconds=60)
async def fraud_score(customer_id: str, request: Request = None):
    score_data = await FraudService.score(customer_id)
    redacted_resp = await redactor.redact_pii(score_data)
    redacted_score = redacted_resp.data if hasattr(redacted_resp, "data") else redacted_resp

    try:
        await sse.publish(
            {
                "event": "fraud_score_generated",
                "customer_id": customer_id,
                **(redacted_score if isinstance(redacted_score, dict) else {})
            },
            type="fraud"
        )
    except Exception as e:
        print(f"SSE publish failed: {e}")

    return redacted_score

# -------------------------
# Multi-Agent Fraud Assessment
# -------------------------
@router.post("/assess", response_model=Dict[str, Any])
@rate_limit(max_requests=30 if TEST_MODE else 3, window_seconds=5 if TEST_MODE else 30)
async def assess_fraud(transaction_data: Dict[str, Any], db: Session = Depends(get_db), request: Request = None):
    """
    Assess fraud for a transaction.
    Expects transaction_data to have at least `customerId` or `customer_id`.
    """
    customer_id = transaction_data.get("customerId") or transaction_data.get("customer_id")
    if not customer_id:
        txn_id = transaction_data.get("id") or transaction_data.get("txn_id") or "unknown"
        customer_id = f"test_{txn_id}"

    start_time = time.time()

    try:
        # Evaluate transaction
        result = FraudService.evaluate_transaction(transaction_data)

        # Prepare alert data
        alert_data = {
            "customer_id": customer_id,
            "txn_id": transaction_data.get("id") or transaction_data.get("txn_id"),
            "score": 100 if result.get("flagged") else 0,
            "reasons": [result["reason"]] if result.get("reason") else [],
            "action_taken": "flagged" if result.get("flagged") else "none",
            "timestamp": transaction_data.get("timestamp")
        }

        # Convert dict to object so create_alert can access attributes
        alert_obj = SimpleNamespace(**alert_data)

        # Create alert
        alert = await FraudService.create_alert(db, alert_obj)
        alert_dict = alert if isinstance(alert, dict) else alert.__dict__
        action_taken = alert_dict.get("action_taken", "none")
        execution_time = time.time() - start_time

        # Redact PII
        redacted_resp = await redactor.redact_pii(alert_dict)
        redacted_alert = getattr(redacted_resp, "data", redacted_resp)

        # SSE publish
        if sse:
            try:
                await sse.publish({
                    "event": "fraud_assessment_completed",
                    "customer_id": customer_id,
                    "transaction_id": transaction_data.get("id") or transaction_data.get("txn_id"),
                    "success": True,
                    "action": action_taken,
                    "execution_time": execution_time
                }, type="fraud")
            except Exception as sse_err:
                print(f"[SSE Error] Could not publish completion: {sse_err}")

        return {
            "status": "success",
            "assessment": redacted_alert,
            "metadata": {
                "plan_execution_time": execution_time,
                "agents_used": ["FraudService"]
            }
        }

    except Exception as e:
        # SSE publish on failure
        if sse:
            try:
                await sse.publish({
                    "event": "fraud_assessment_failed",
                    "customer_id": customer_id,
                    "transaction_id": transaction_data.get("id") or transaction_data.get("txn_id"),
                    "error": str(e),
                    "execution_time": time.time() - start_time
                }, type="fraud_error")
            except Exception as sse_err:
                print(f"[SSE Error] Could not publish failure: {sse_err}")

        raise HTTPException(status_code=500, detail=f"Fraud assessment failed: {str(e)}")
# -------------------------
# Batch Assessment
# -------------------------
@router.post("/assess/batch")
@rate_limit(max_requests=20 if TEST_MODE else 2, window_seconds=5 if TEST_MODE else 60)
async def assess_fraud_batch(transactions: List[Dict[str, Any]], db: Session = Depends(get_db), request: Request = None):
    if len(transactions) > 100:
        raise HTTPException(status_code=400, detail="Batch size cannot exceed 100 transactions")

    results = []
    start_time = time.time()

    for transaction in transactions:
        try:
            result = await orchestrator.execute_plan(transaction.get("customerId") or transaction.get("customer_id") or f"test_{transaction.get('id','unknown')}", transaction)
            redacted_resp = await redactor.redact_pii(result)
            redacted = redacted_resp.data if hasattr(redacted_resp, "data") else redacted_resp

            final_action = result.get("final_action", {}) if isinstance(result, dict) else {}
            normalized_action = {"action": final_action.get("action", "NO_ACTION"), "reason": final_action.get("reason", "unspecified")}

            results.append({
                "transaction_id": transaction.get("id"),
                "status": "success" if result.get("success") else "error",
                "result": {"action": normalized_action, "details": redacted}
            })
        except Exception as e:
            results.append({"transaction_id": transaction.get("id"), "status": "error", "error": str(e)})

    await sse.publish({
        "event": "batch_assessment_completed",
        "batch_size": len(transactions),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "total_time": time.time() - start_time
    }, type="fraud_batch")

    return {
        "batch_id": f"batch_{int(time.time())}",
        "processed": len(results),
        "successful": sum(1 for r in results if r["status"] == "success"),
        "failed": sum(1 for r in results if r["status"] == "error"),
        "total_time": time.time() - start_time,
        "results": results
    }

# -------------------------
# Agent System Status
# -------------------------
@router.get("/system/status")
@rate_limit(max_requests=1, window_seconds=300)
async def get_agent_system_status(request: Request):
    status = {
        "orchestrator": orchestrator.circuit_breaker.get_status(),
        "insights_agent": orchestrator.insights_agent.circuit_breaker.get_status(),
        "fraud_agent": orchestrator.fraud_agent.circuit_breaker.get_status(),
        "kb_agent": orchestrator.kb_agent.circuit_breaker.get_status(),
        "compliance_agent": orchestrator.compliance_agent.circuit_breaker.get_status(),
        "system_status": "operational" if _is_system_operational() else "degraded"
    }

    # Publish to SSE only if sse is initialized
    if sse is not None:
        try:
            await sse.publish(
                {"event": "system_status_checked", "status": status["system_status"]},
                type="system"
            )
        except Exception as e:
            # Log but do not fail the request
            print(f"Warning: SSE publish failed: {e}")

    return status


@router.post("/system/reset")
@rate_limit(max_requests=1, window_seconds=300)
async def reset_agent_system(request: Request):
    agents = [
        orchestrator,
        orchestrator.insights_agent,
        orchestrator.fraud_agent,
        orchestrator.kb_agent,
        orchestrator.compliance_agent
    ]

    # Reset circuit breakers safely
    for agent in agents:
        try:
            agent.circuit_breaker.on_success()  # Reset to "closed" state
        except AttributeError as e:
            print(f"[Warning] Could not reset circuit breaker for {agent.name}: {e}")

    # Try publishing SSE event
    try:
        if sse:
            await sse.publish(
                {"event": "system_reset", "message": "All circuit breakers reset"},
                type="system"
            )
    except Exception as sse_err:
        print(f"[SSE Error] Could not publish system reset: {sse_err}")

    return {"status": "success", "message": "All circuit breakers reset"}


# -------------------------
# Helper Functions
# -------------------------
def _is_system_operational() -> bool:
    critical_agents = [orchestrator.circuit_breaker, orchestrator.fraud_agent.circuit_breaker, orchestrator.kb_agent.circuit_breaker]
    return all(cb.state == "closed" for cb in critical_agents)


@router.get("/customer-metrics/{customer_id}", response_model=Dict[str, Any])
@rate_limit(max_requests=10, window_seconds=60)
async def get_customer_metrics(
    customer_id: str,
    db: Session = Depends(get_db),
    request: Request = None  
    # page: int = Query(1, ge=1),
    # limit: int = Query(50, ge=1, le=100)
):
    """
    Fetch key fraud metrics for a specific customer:
    - totalSpend
    - % high-risk alerts
    - disputesOpened
    - avgTriageTime (seconds)
    """
    try:
        metrics = await FraudService.get_customer_metrics(db, customer_id)

        # Optional: SSE publish
        if sse:
            try:
                await sse.publish(
                    {"event": "customer_metrics_fetched", "customer_id": customer_id, **metrics},
                    type="fraud_metrics"
                )
            except Exception as e:
                print(f"[SSE Warning] Could not publish metrics: {e}")

        return metrics

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not fetch metrics: {str(e)}")
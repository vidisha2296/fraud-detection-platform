# app/services/monitoring_service.py
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.transaction import Transaction
from app.models.fraud_alert import FraudAlert
from app.models.eval import EvalResult
import asyncio

class MonitoringService:

    @staticmethod
    async def health() -> dict:
        """
        Async service health check.
        Verifies DB connectivity.
        """
        def _check_db():
            try:
                db: Session = SessionLocal()
                db.execute("SELECT 1")
                db.close()
                return {"status": "ok", "db": "connected"}
            except Exception:
                return {"status": "error", "db": "disconnected"}

        return await asyncio.to_thread(_check_db)

    @staticmethod
    async def metrics() -> dict:
        """
        Async aggregate metrics from the DB.
        """
        def _compute_metrics():
            db: Session = SessionLocal()
            try:
                total_txns = db.query(Transaction).count()
                total_frauds = db.query(FraudAlert).count()
                total_eval_results = db.query(EvalResult).count()
                passed_eval_results = db.query(EvalResult).filter_by(passed=1).count()
                success_rate = (passed_eval_results / total_eval_results) * 100 if total_eval_results else 0

                return {
                    "transactions": total_txns,
                    "fraud_alerts": total_frauds,
                    "evals": {
                        "total": total_eval_results,
                        "passed": passed_eval_results,
                        "success_rate": round(success_rate, 2)
                    }
                }
            finally:
                db.close()

        return await asyncio.to_thread(_compute_metrics)

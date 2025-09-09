# app/services/risk_service.py
import asyncio
import random

class RiskService:
    @staticmethod
    async def evaluate_transaction(transaction_data: dict) -> dict:
        # Simulated risk evaluation with fallback
        try:
            # Imagine a call to external risk service
            risk_score = round(random.uniform(0, 1), 2)
            action_required = "freeze_card" if risk_score > 0.9 else None
            return {"score": risk_score, "action": action_required}
        except Exception:
            # Fallback if service fails
            return {"score": 0.5, "action": None}

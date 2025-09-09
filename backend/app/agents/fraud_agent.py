from app.agents.base_agent import BaseAgent, AgentResponse
from app.models.agent_models import FraudAssessment, RiskDecision, ActionProposal
from typing import Dict, List, Any

class FraudAgent(BaseAgent):
    def __init__(self):
        super().__init__("fraud_agent")
    
    async def assess_risk(
        self,
        customer_id: str,
        transaction: Dict[str, Any],
        recent_transactions: List[Dict[str, Any]]
    ) -> AgentResponse:
        """Assess fraud risk with multiple signals"""
        
        async def _assess():
            # Velocity check
            velocity_risk = self._check_velocity(recent_transactions, transaction)
            
            # Device change check
            device_risk = self._check_device_change(customer_id, transaction)
            
            # MCC rarity check
            mcc_risk = self._check_mcc_rarity(customer_id, transaction)
            
            # Chargeback history
            cb_risk = self._check_chargeback_history(customer_id)
            
            # Calculate composite risk score
            risk_score = self._calculate_risk_score(
                velocity_risk, device_risk, mcc_risk, cb_risk
            )
            
            reasons = []
            if velocity_risk > 0.7:
                reasons.append("High transaction velocity detected")
            if device_risk > 0.6:
                reasons.append("Suspicious device change")
            if mcc_risk > 0.5:
                reasons.append("Unusual merchant category")
            if cb_risk > 0.8:
                reasons.append("Previous chargeback history")
            
            return FraudAssessment(
                risk_score=risk_score,
                reasons=reasons,
                signals={
                    "velocity_risk": velocity_risk,
                    "device_risk": device_risk,
                    "mcc_risk": mcc_risk,
                    "chargeback_risk": cb_risk
                }
            )
        
        return await self.execute_with_guardrails(_assess)
    
    def _check_velocity(self, recent_txns: List[Dict[str, Any]], current_txn: Dict[str, Any]) -> float:
        """Check transaction velocity"""
        # Implementation for velocity analysis
        return 0.3  # Example value
    
    def _check_device_change(self, customer_id: str, transaction: Dict[str, Any]) -> float:
        """Check if device change is suspicious"""
        return 0.2  # Example value
    
    def _check_mcc_rarity(self, customer_id: str, transaction: Dict[str, Any]) -> float:
        """Check if MCC is unusual for customer"""
        return 0.4  # Example value
    
    def _check_chargeback_history(self, customer_id: str) -> float:
        """Check chargeback history"""
        return 0.1  # Example value
    
    def _calculate_risk_score(self, *risks: float) -> float:
        """Calculate composite risk score"""
        return sum(risks) / len(risks)
    
    async def make_decision(
        self,
        risk_assessment: FraudAssessment,
        kb_rules: List[Dict[str, Any]]
    ) -> AgentResponse:
        """Make risk decision based on assessment and rules"""
        
        async def _decide():
            score = risk_assessment.risk_score
            
            if score >= 0.8:
                decision = "block"
            elif score >= 0.6:
                decision = "review"
            elif score >= 0.4:
                decision = "verify"
            else:
                decision = "approve"
            
            return RiskDecision(
                decision=decision,
                confidence=score,
                rules_applied=[rule["title"] for rule in kb_rules[:3]]
            )
        
        return await self.execute_with_guardrails(_decide)
    
    async def propose_action(
        self,
        decision: RiskDecision,
        transaction: Dict[str, Any]
    ) -> AgentResponse:
        """Propose specific action based on decision"""
        
        async def _propose():
            if decision.decision == "block":
                action = "block_transaction"
                message = "Transaction blocked due to high fraud risk"
            elif decision.decision == "review":
                action = "flag_for_review"
                message = "Transaction requires manual review"
            elif decision.decision == "verify":
                action = "request_otp"
                message = "OTP verification required"
            else:
                action = "approve"
                message = "Transaction approved"
            
            return ActionProposal(
                action=action,
                message=message,
                transaction_id=transaction.get("id"),
                customer_id=transaction.get("customerId")
            )
        
        return await self.execute_with_guardrails(_propose)
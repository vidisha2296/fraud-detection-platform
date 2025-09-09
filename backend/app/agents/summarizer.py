from app.agents.base_agent import BaseAgent, AgentResponse
from typing import Dict, Any, List

class SummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__("summarizer_agent")
    
    async def summarize_customer_notes(self, customer_id: str, assessment: Dict[str, Any]) -> AgentResponse:
        """Generate customer-facing summary notes"""
        async def _summarize_customer():
            risk_score = assessment.get('risk_score', 0)
            
            if risk_score > 0.7:
                template = "Your transaction was flagged for review due to suspicious activity patterns. Our team will contact you shortly."
            elif risk_score > 0.4:
                template = "For your security, we need additional verification. Please check your registered mobile for OTP."
            else:
                template = "Transaction processed successfully. Thank you for your business."
            
            return {
                "customer_message": template,
                "risk_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low"
            }
        
        return await self.execute_with_guardrails(_summarize_customer)
    
    async def summarize_internal_notes(self, customer_id: str, assessment: Dict[str, Any]) -> AgentResponse:
        """Generate internal notes for agents"""
        async def _summarize_internal():
            reasons = assessment.get('reasons', [])
            signals = assessment.get('signals', {})
            
            notes = [
                f"Customer: {customer_id}",
                f"Risk Score: {assessment.get('risk_score', 0):.2f}",
                "Risk Factors:"
            ]
            
            for reason in reasons:
                notes.append(f"  - {reason}")
            
            notes.append("Signal Scores:")
            for signal, score in signals.items():
                notes.append(f"  - {signal}: {score:.2f}")
            
            return {
                "internal_notes": "\n".join(notes),
                "action_required": len(reasons) > 0
            }
        
        return await self.execute_with_guardrails(_summarize_internal)
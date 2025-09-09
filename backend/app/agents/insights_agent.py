from app.agents.base_agent import BaseAgent, AgentResponse
from app.models.agent_models import CustomerProfile
from typing import List, Dict, Any

class InsightsAgent(BaseAgent):
    def __init__(self):
        super().__init__("insights_agent")
    
    async def get_customer_profile(self, customer_id: str) -> AgentResponse:
        """Get customer profile with transaction insights"""
        async def _get_profile():
            # This would query your database
            # For now, return mock data
            return CustomerProfile(
                customer_id=customer_id,
                risk_level="medium",
                total_transactions=45,
                chargeback_count=2,
                devices=["dev_45", "dev_12"],
                avg_transaction_amount=2500.0
            )
        
        return await self.execute_with_guardrails(_get_profile)
    
    async def get_recent_transactions(self, customer_id: str, hours: int = 24) -> AgentResponse:
        """Get recent transactions for velocity analysis"""
        async def _get_transactions():
            # This would query your database
            # Return mock data for now
            return [
                {
                    "id": "txn_00999",
                    "amount": -1500,
                    "merchant": "Restaurant",
                    "timestamp": "2025-06-14T19:30:45Z"
                },
                {
                    "id": "txn_00998", 
                    "amount": -3000,
                    "merchant": "Supermarket",
                    "timestamp": "2025-06-14T10:15:22Z"
                }
            ]
        
        return await self.execute_with_guardrails(_get_transactions)
    
    async def categorize_transaction(self, transaction: Dict[str, Any]) -> AgentResponse:
        """Categorize transaction using deterministic rules"""
        async def _categorize():
            mcc = transaction.get('mcc', '')
            merchant = transaction.get('merchant', '').lower()
            
            categories = {
                '5411': 'groceries',
                '5812': 'dining',
                '6011': 'cash_withdrawal',
                '4829': 'money_transfer'
            }
            
            category = categories.get(mcc, 'other')
            
            # Additional merchant-based categorization
            if 'atm' in merchant:
                category = 'cash_withdrawal'
            elif 'restaurant' in merchant or 'cafe' in merchant:
                category = 'dining'
            
            return {
                "category": category,
                "confidence": 0.9,
                "mcc": mcc,
                "merchant": merchant
            }
        
        return await self.execute_with_guardrails(_categorize)
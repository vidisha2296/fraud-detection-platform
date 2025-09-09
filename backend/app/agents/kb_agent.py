import json
from pathlib import Path
from typing import List, Dict, Any
from app.agents.base_agent import BaseAgent, AgentResponse

class KBAgent(BaseAgent):
    def __init__(self):
        super().__init__("kb_agent")
        self.kb_path = Path("fixtures/kb_docs.json")
        self.kb_data = self._load_kb_data()
    
    def _load_kb_data(self) -> List[Dict[str, Any]]:
        """Load knowledge base data"""
        try:
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    async def lookup_relevant_rules(
        self,
        customer_id: str,
        transaction: Dict[str, Any],
        risk_score: float
    ) -> AgentResponse:
        """Lookup relevant KB rules with fallback templates"""
        
        async def _lookup():
            relevant_rules = []
            
            # Rule 1: Check transaction amount
            amount = abs(transaction.get('amount', 0))
            if amount > 5000 and risk_score > 0.3:
                relevant_rules.extend(self._find_rules_by_keyword(["amount", "large"]))
            
            # Rule 2: Check merchant category
            mcc = transaction.get('mcc', '')
            if mcc in ['6011', '4829']:  # ATM, money transfer
                relevant_rules.extend(self._find_rules_by_keyword(["ATM", "withdrawal"]))
            
            # Rule 3: Check device risk
            if risk_score > 0.6:
                relevant_rules.extend(self._find_rules_by_keyword(["device", "suspicious"]))
            
            # Deduplicate and limit results
            unique_rules = list({rule['title']: rule for rule in relevant_rules}.values())
            
            return unique_rules[:5]  # Return top 5 most relevant rules
        
        return await self.execute_with_guardrails(_lookup)
    
    def _find_rules_by_keyword(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """Find rules containing any of the keywords"""
        results = []
        for rule in self.kb_data:
            content = ' '.join(rule.get('chunks', [])).lower()
            title = rule.get('title', '').lower()
            
            for keyword in keywords:
                if keyword.lower() in content or keyword.lower() in title:
                    results.append(rule)
                    break
        
        return results
    
    def get_fallback_template(self, rule_type: str) -> Dict[str, Any]:
        """Get fallback template for when KB lookup fails"""
        templates = {
            "high_risk": {
                "title": "High Risk Transaction Protocol",
                "anchor": "fallback_high_risk",
                "chunks": ["Review transaction manually", "Request additional verification"]
            },
            "medium_risk": {
                "title": "Standard Verification Protocol",
                "anchor": "fallback_medium_risk", 
                "chunks": ["Proceed with OTP verification", "Monitor for similar patterns"]
            },
            "low_risk": {
                "title": "Low Risk Approval Protocol",
                "anchor": "fallback_low_risk",
                "chunks": ["Approve transaction", "Continue normal monitoring"]
            }
        }
        return templates.get(rule_type, templates["medium_risk"])
import re
from app.agents.base_agent import BaseAgent, AgentResponse
from typing import Dict, Any, List

class RedactorAgent(BaseAgent):
    def __init__(self):
        super().__init__("redactor_agent")
        # Regex patterns for PII detection
        self.patterns = {
            'credit_card': r'\b\d{13,19}\b',
            'aadhaar': r'\b\d{4}\s?\d{4}\s?\d{4}\b',
            'pan': r'[A-Z]{5}\d{4}[A-Z]{1}',
            'phone': r'\b(?:\+91[\-\s]?)?[789]\d{9}\b'
        }
    
    async def redact_pii(self, data: Any) -> AgentResponse:
        """Redact PII from data"""
        async def _redact():
            if isinstance(data, str):
                return self._redact_text(data)
            elif isinstance(data, dict):
                return self._redact_dict(data)
            elif isinstance(data, list):
                return [self._redact_item(item) for item in data]
            else:
                return data
        
        return await self.execute_with_guardrails(_redact)
    
    def _redact_text(self, text: str) -> str:
        """Redact PII from text"""
        for pattern_name, pattern in self.patterns.items():
            text = re.sub(pattern, "****REDACTED****", text)
        return text
    
    def _redact_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Redact PII from dictionary"""
        redacted = {}
        for key, value in data.items():
            if isinstance(value, (str, dict, list)):
                redacted[key] = self._redact_item(value)
            else:
                redacted[key] = value
        return redacted
    
    def _redact_item(self, item: Any) -> Any:
        """Redact PII from any item"""
        if isinstance(item, str):
            return self._redact_text(item)
        elif isinstance(item, dict):
            return self._redact_dict(item)
        elif isinstance(item, list):
            return [self._redact_item(i) for i in item]
        else:
            return item
import re
from typing import Any

def sanitize_input(input_data: Any) -> Any:
    """Sanitize input to prevent injection attacks"""
    if isinstance(input_data, str):
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>{}[\]\\]', '', input_data)
        # Limit length
        return sanitized[:1000]
    elif isinstance(input_data, dict):
        return {k: sanitize_input(v) for k, v in input_data.items()}
    elif isinstance(input_data, list):
        return [sanitize_input(item) for item in input_data]
    else:
        return input_data

def detect_prompt_injection(text: str) -> bool:
    """Detect potential prompt injection attempts"""
    injection_patterns = [
        r'(?i)ignore.*previous',
        r'(?i)forget.*instructions',
        r'(?i)as.*ai',
        r'(?i)disregard',
        r'(?i)override',
        r'(?i)system.*prompt'
    ]
    
    text_lower = text.lower()
    for pattern in injection_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False
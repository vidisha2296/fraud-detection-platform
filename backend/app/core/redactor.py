import re

class Redactor:
    CARD_PATTERN = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
    EMAIL_PATTERN = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w+\b')

    @staticmethod
    def mask_pii(text: str) -> str:
        if not text:
            return text
        text = Redactor.CARD_PATTERN.sub("****REDACTED_CARD****", text)
        text = Redactor.EMAIL_PATTERN.sub("****REDACTED_EMAIL****", text)
        return text

# Create a singleton instance
redactor = Redactor()
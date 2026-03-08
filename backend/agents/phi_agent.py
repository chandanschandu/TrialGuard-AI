import re

class PHIAgent:
    def redact_phi(self, text):
        # Ensure text is a string (might be a dict if protocol_str was actually a dict)
        if not isinstance(text, str):
            text = str(text)
            
        # Local regex-based redaction for names, ages, and locations as a fallback
        # since AWS Comprehend Medical requires a specific subscription.
        redacted = text
        
        # Redact common Indian names pattern (capitalized words) - simplistic fallback
        # This is a placeholder for more robust local PII detection
        patterns = [
            (r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', '[NAME]'), # Full Name
            (r'\bage \d+\b', 'age [AGE]'),              # Age
            (r'\bfrom [A-Z][a-z]+\b', 'from [LOCATION]') # Location
        ]
        
        for pattern, replacement in patterns:
            redacted = re.sub(pattern, replacement, redacted)
            
        return redacted

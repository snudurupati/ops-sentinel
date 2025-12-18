import re

class SecurityRedactor:
    def __init__(self):
        # NOTE: In production, use Microsoft Presidio (Local NLP) for context-aware detection.
        # This Regex implementation is optimized for low-latency MVP demonstration.
        self.patterns = {
            # 1. Email Pattern
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}': '<EMAIL_REDACTED>',
            
            # 2. API Key Pattern (e.g., sk-...)
            # OLD: r'sk-[a-zA-Z0-9]{20,}'
            # NEW: Allow keys as short as 10 characters for testing
            r'sk-[a-zA-Z0-9]{10,}': '<REDACTED_API_KEY>',
            
            # 3. IP Address (IPv4)
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b': '<IP_REDACTED>',
            
            # 4. SSN (US Social Security Number)
            # Matches: 123-45-6789
            r'\b\d{3}-\d{2}-\d{4}\b': '<SSN_REDACTED>',
            
            # 5. US Street Address (Heuristic)
            # Matches: "123 Main St", "456 Oak Avenue", "10 Elm Dr"
            # It looks for a number, followed by text, ending in a common suffix.
            r'\b\d+\s[A-Za-z0-9\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct)\b': '<ADDRESS_REDACTED>'
        }

    def redact(self, text: str) -> str:
        """
        Scans text and replaces sensitive patterns with placeholders.
        """
        if not isinstance(text, str):
            return str(text)
            
        sanitized_text = text
        for pattern, replacement in self.patterns.items():
            # flags=re.IGNORECASE allows catching 'Main st' and 'Main St'
            sanitized_text = re.sub(pattern, replacement, sanitized_text, flags=re.IGNORECASE)
            
        return sanitized_text

# Singleton instance
redactor = SecurityRedactor()

if __name__ == "__main__":
    # Test the heavier redactor
    unsafe_log = """
    Incident Report:
    User: john.doe@example.com
    IP: 192.168.1.1
    API Key: sk-1234567890abcdef1234567890
    SSN: 123-45-6789
    Home Address: 4455 Evergreen Terrace Dr
    """
    
    print(f"Original:\n{unsafe_log}")
    print("-" * 40)
    print(f"Sanitized:\n{redactor.redact(unsafe_log)}")
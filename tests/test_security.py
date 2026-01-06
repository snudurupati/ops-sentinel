import pytest
import sys
import os

# --- SETUP: Add the project root to sys.path ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the redactor. 
# We wrap this in a try/except block to give a helpful error 
# if you haven't created 'src/security.py' yet.
try:
    from src.security import redactor
except ImportError:
    redactor = None

class TestSecurityMiddleware:
    
    def test_redact_pii_mixed_content(self):
        """
        Scenario: Log contains mixed PII (Email + API Key).
        Goal: Verify that sensitive data is stripped out, but structure remains.
        """
        if not redactor:
            pytest.fail("Module 'src.security' not found. Please create the redactor.")

        # 1. Setup: The "Dirty" Data
        dirty_data = '[{"log_message": "User login failed. Email: jeff@amazon.com. Key: sk-9999999999999"}]'
        
        # 2. Action: Run the redaction
        clean_data = redactor.redact(dirty_data)
        
        # DEBUG: Print it so you can see it with 'pytest -s'
        print(f"\nRAW:   {dirty_data}")
        print(f"CLEAN: {clean_data}")

        # 3. Assertions (The most important part)
        
        # CHECK 1: The secrets must be GONE
        assert "jeff@amazon.com" not in clean_data, "Failed to redact Email"
        assert "sk-9999999999999" not in clean_data, "Failed to redact API Key"
        
        # CHECK 2: The structure/context should remain
        assert "User login failed" in clean_data
        assert "Email:" in clean_data
        
        # CHECK 3: Ensure placeholders were inserted (Optional, depending on your implementation)
        # e.g., assert "<EMAIL>" in clean_data or "[REDACTED]" in clean_data

    def test_safe_data_remains_unchanged(self):
        """
        Scenario: Log contains safe operational data.
        Goal: Verify we don't accidentally redact valid IDs or text (False Positives).
        """
        if not redactor:
            pytest.fail("Module 'src.security' not found.")

        safe_payload = "Service ID: 12345 is running on Port 8080."
        clean_payload = redactor.redact(safe_payload)
        
        # If there is no PII, the input should equal the output
        assert clean_payload == safe_payload
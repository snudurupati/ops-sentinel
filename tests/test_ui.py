import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest

# --- SETUP: Add project root to sys.path ---
# This ensures that when the app runs, it can find 'src' modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestStreamlitUI:

    def test_app_startup(self):
        """
        Scenario: Smoke Test.
        Goal: Verify the app launches without crashing.
        """
        # FIX 1: Point to the correct folder path
        at = AppTest.from_file("frontend/app.py")
        at.run()

        # Check for startup exceptions (e.g., ImportErrors)
        if at.exception:
            print(f"\n❌ Startup Exception: {at.exception}")
        assert not at.exception

    # FIX 2: We patch 'src.agent.run_agent' so we don't hit real OpenAI
    @patch("src.agent.run_agent")
    def test_chat_interaction(self, mock_run_agent):
        """
        Scenario: User sends a message.
        Goal: Verify the UI updates and calls the agent.
        """
        # 1. Setup the Mock Response
        # We tell the mock what to return when the UI calls run_agent()
        mock_report = MagicMock()
        mock_report.to_markdown.return_value = "### Fix: Restart Pod"
        
        # We simulate a returned message to populate chat history
        mock_message = MagicMock()
        mock_message.content = "Found issue in logs."
        
        # run_agent returns a tuple: (report, messages)
        mock_run_agent.return_value = (mock_report, [mock_message])

        # 2. Load the App
        at = AppTest.from_file("frontend/app.py")
        at.run()

        # 3. Simulate User Input
        # We type into the first chat_input found on screen
        if len(at.chat_input) > 0:
            at.chat_input[0].set_value("How do I fix error 503?").run()
            
            # 4. Assertions
            # Did the app actually call our backend?
            mock_run_agent.assert_called_once()
            
            # Did the UI update? (Check if session state has messages)
            # This depends on your specific app.py logic, but typically:
            if "messages" in at.session_state:
                assert len(at.session_state.messages) > 0
                
            # If your app uses an expander for "Thinking" or "Sources":
            # assert len(at.expanders) > 0
        else:
            pytest.fail("No chat input found. Is the app fully loaded?")
import pytest
import sys
import os
from langchain_core.messages import AIMessage

# --- SETUP: Add the parent directory to sys.path ---
# This ensures we can import from 'src' regardless of where you run the test from.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from src
from src.agent import run_agent

class TestAgentReasoning:
    """
    Integration Tests for the Aether Agent.
    """

    def test_golden_set_payment_latency(self):
        """
        Scenario: User reports high CPU on Payment API.
        Goal: Verify the agent extracts 'Payment-API' and produces a valid IncidentReport.
        """
        query = "I am seeing high CPU on the Payment-API. Investigate."
        
        # Run the agent
        report, messages = run_agent(query)

        # 1. Assertion: Check that we got a report object
        assert report is not None
        
        # 2. Assertion: Check specific fields from your models.py
        # We check if the 'root_cause' or 'incident_type' mentions the service
        # converting to lower case to be case-insensitive
        content_dump = (report.incident_type + report.root_cause).lower()
        
        assert "payment" in content_dump or "api" in content_dump
        
        # 3. Assertion: Ensure confidence score is reasonable (e.g., not 0)
        assert report.confidence_score > 0
        
        # 4. Assertion: Ensure we have at least one remediation step
        assert len(report.remediation_steps) > 0

    def test_agent_tool_usage_logic(self):
        """
        Scenario: Database Check.
        Goal: Verify the agent ACTUALLY called the SQL tools (Reasoning Check).
        """
        query = "Auth Service is timing out. Check for database locks."
        
        report, messages = run_agent(query)
        
        # We analyze the raw messages to prove the agent 'thought' correctly
        tool_calls_made = []
        
        for msg in messages:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tool in msg.tool_calls:
                    tool_calls_made.append(tool['name'])
        
        print(f"\n🛠️ Tools used by agent: {tool_calls_made}")

        # Assert that the agent tried to list tables or query metrics
        assert "list_tables_tool" in tool_calls_made or "query_metrics_tool" in tool_calls_made

    def test_handling_irrelevant_query(self):
        """
        Scenario: User asks something off-topic.
        Goal: Agent should handle it gracefully and return a low confidence score or generic error.
        """
        query = "What is the capital of France?"
        
        report, messages = run_agent(query)
        
        # We just want to ensure it doesn't crash and returns a valid object
        assert report is not None
        assert isinstance(report.remediation_steps, list)
import pytest
import sys
import os
import pandas as pd
from unittest.mock import MagicMock, patch

# --- SETUP: Add the project root to sys.path ---
# This ensures Python can see the 'src' folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from src specifically
# We wrap it in try/except just in case you haven't moved it yet, 
# but moving it to 'src' is the correct fix.
try:
    from src.db_utils import execute_query, get_table_schema
except ImportError:
    # Fallback if file is still in root
    from db_utils import execute_query, get_table_schema

class TestDatabaseUtils:
    
    def test_security_guardrails(self):
        """
        Scenario: Agent tries to run a destructive command.
        Goal: Verify that execute_query BLOCKS the attempt.
        """
        dangerous_queries = [
            "DROP TABLE metrics",
            "DELETE FROM services WHERE id=1",
            "UPDATE logs SET error_msg='hacked'",
            "INSERT INTO users VALUES ('bad', 'actor')"
        ]
        
        for query in dangerous_queries:
            result = execute_query(query)
            assert isinstance(result, list)
            assert "error" in result[0]
            assert "Security Alert" in result[0]["error"]

    # We patch WHERE the function is imported, not where it is defined.
    # Since we imported 'execute_query' above, we mock the underlying calls it makes.
    # Note: We must patch 'src.db_utils.get_db_connection' if the file is in src.
    @patch("src.db_utils.get_db_connection")
    @patch("src.db_utils.pd.read_sql_query")
    def test_execute_query_success(self, mock_read_sql, mock_conn):
        """
        Scenario: Valid SELECT query.
        Goal: Verify pandas is used to fetch and format data correctly.
        """
        # Setup Mock
        mock_df = pd.DataFrame({
            "id": [101, 102],
            "service": ["Auth", "Payment"]
        })
        mock_read_sql.return_value = mock_df
        
        # Run
        query = "SELECT * FROM services"
        result = execute_query(query)
        
        # Assert
        assert len(result) == 2
        assert result[0]["service"] == "Auth"
        mock_read_sql.assert_called_once()

    @patch("src.db_utils.get_db_connection")
    def test_get_table_schema(self, mock_get_conn):
        """
        Scenario: Agent asks for database structure.
        Goal: Verify it iterates tables and formats columns correctly.
        """
        mock_conn = mock_get_conn.return_value
        mock_cursor = mock_conn.cursor.return_value
        
        # Mock responses for the multiple cursor calls
        mock_cursor.fetchall.side_effect = [
            [{'name': 'metrics'}],       # 1. Get list of tables
            [{'name': 'id', 'type': 'INTEGER'}, {'name': 'cpu', 'type': 'FLOAT'}] # 2. Get columns for 'metrics'
        ]
        
        schema_text = get_table_schema()
        
        assert "Table: metrics" in schema_text
        assert "cpu (FLOAT)" in schema_text

    @patch("src.db_utils.get_db_connection")
    def test_sql_error_handling(self, mock_conn):
        """
        Scenario: Malformed SQL.
        Goal: Verify it catches exceptions.
        """
        # We need to match the patch path to where the code lives
        with patch("src.db_utils.pd.read_sql_query", side_effect=Exception("Syntax Error")):
            result = execute_query("SELECT * FROM invalid_table")
            
            assert "error" in result[0]
            assert "SQL Execution Failed" in result[0]["error"]
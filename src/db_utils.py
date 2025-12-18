import sqlite3
import pandas as pd
from typing import List, Dict, Any

DB_PATH = "./data/sre_observability.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row #Allows column access by name
    return conn

def execute_query(query: str) -> List[Dict[str, Any]]:
    """
    Executes a read-only SQL query and returns results as a list of dictionaries.
    Includes basic guardrails to prevent modification.
    """
    #🛡️ GUARDRAIL: Simple check to prevent mutations
    forbidden_keywords = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "TRUNCATE"]
    if any(keyword in query.upper() for keyword in forbidden_keywords):
        return [{"error": "Security Alert: automated agents are not allowed to modify data."}]
    
    try:
        conn = get_db_connection()
        # Use pandas for easy SQL execution and JSON conversion
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_dict(orient="records")
    except Exception as e:
        return [{"error": f"SQL Execution Failed: {str(e)}"}]

def get_table_schema() -> str:
    """Returns the schema of the database so the Agent knows what to query."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    schema_str = ""
    for table in tables:
        table_name = table['name']
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        column_names = [f"{col['name']} ({col['type']})" for col in columns]
        schema_str += f"Table: {table_name}\nColumns: {', '.join(column_names)}\n\n"
        
    conn.close()
    return schema_str 

# Quick test if running directly
if __name__ == "__main__":
    print("--- Database Schema ---")
    print(get_table_schema())
    print("\n--- Test Query (Payment-API logs) ---")
    print(execute_query("SELECT * FROM metrics WHERE service_id=1 LIMIT 2"))
from langchain_core.tools import tool
from src.db_utils import execute_query, get_table_schema
from src.vector_utils import search_runbooks
from src.security import redactor # Import the PII redactor

# ---Tool 1: The Database Inspector ---
@tool
def list_tables_tool():
    """
    Returns the schema of the metrics database.
    ALWAYS call first to understand the table structure before writing SQL.
    """
    return get_table_schema()

# ---Tool 2: The SQL Executor ---
@tool
def query_metrics_tool(query: str):
    """
    Executes a SQL query against the metrics database.
    Useful for finding 'cpu_percent', 'memory_usage', or 'error_rate'.
    """
    try:
        # 1. Run the query
        results = fetch_metrics(query)
        
        # 2. 🔒 GUARDRAIL: Redact PII from DB rows
        # (Assuming results is a list of tuples/dicts)
        clean_results = [redactor.redact(str(row)) for row in results]
        
        # 3. 🔧 FIX: Convert the list to a single string block
        # If the list is empty, say "No results"
        if not clean_results:
            return "Query returned no results."
            
        return "\n".join(clean_results)

    except Exception as e:
        return f"Database Error: {str(e)}"

# ---Tool 3: The Runbook Searcher ---
@tool
def search_runbooks_tool(query: str):
    """
    Searches the internal SRE runbooks and post-mortems for semantic matches.
    Use this when diagnosing errors (e.g., 'Error 503', 'Connection Refused') 
    to find known fixes.
    """
    results = search_runbooks(query)
    
    # 🔒 GUARDRAIL: Redact PII
    clean_results = [redactor.redact(doc) for doc in results]
    
    # 🔧 FIX: Join the list into a single string so the Agent can read it
    return "\n\n---\n\n".join(clean_results)

# Registry of all tools
ALL_TOOLS = [list_tables_tool, query_metrics_tool, search_runbooks_tool]
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI 
from langchain.agents import create_agent
from src.mcp_server import ALL_TOOLS
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from src.models import IncidentReport
import langchain
from typing import Tuple, List
from langchain_core.messages import BaseMessage
from tenacity import retry, stop_after_attempt, wait_random_exponential
from langchain_community.cache import InMemoryCache

langchain.debug = True

load_dotenv()       

# --- 2. SWITCH TO IN-MEMORY CACHE ---
# This fixes the "Database Locked" loop.
print("✅ Setting up In-Memory Cache (RAM)")
try:
    from langchain.globals import set_llm_cache
    set_llm_cache(InMemoryCache())
except ImportError:
    langchain.llm_cache = InMemoryCache()

# 1. Initialize the LLM
# Add max_retries=5 to handle rate limits automatically
llm = ChatOpenAI(
    model_name="gpt-4o-mini", 
    temperature=0,
    max_retries=5, #OpenAI SDK has built-n exponential backoff with jitter strategy.
    request_timeout=60
) 

# 2. Define the System Prompt
prompt = """
You are an expert Site Reliability Engineer (SRE) named 'Ops-Sentinel'.
Your goal is to diagnose infrastructure incidents by combining:
1. Structured Telemetry (SQL Metrics)
2. Unstructured Knowledge (Runbooks)

CRITICAL INSTRUCTIONS:
- You are an AUTONOMOUS agent. Do not ask the user for permission to run queries.
- If the user asks you to investigate, you must perform the ENTIRE investigation in one go.
- STEP 1: Check the database schema (list_tables_tool).
- STEP 2: IMMEDIATELY write and execute a SQL query to check the logs (query_metrics_tool).
    - Hint: Use 'SELECT * FROM metrics WHERE ...'
- STEP 3: If you see errors or high CPU, IMMEDIATELY search the runbooks (search_runbooks_tool).
- STEP 4: Synthesize the findings into a final answer.

Do NOT stop after Step 1. Keep going until you have the answer.
"""

# 3. Create the Agent
agent = create_agent(model=llm, tools=ALL_TOOLS, system_prompt=prompt)

# --- THE FIX: EXPONENTIAL BACKOFF DECORATOR ---
# This forces the function to retry 5 times, waiting 1s, then 2s, 4s... up to 60s
@retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(5))
def invoke_agent_with_retry(query, callbacks):
    return agent.invoke({"input": query}, config={"callbacks": callbacks})

# Update signature to return a Tuple
def run_agent(user_query: str, callbacks=None) -> Tuple[IncidentReport, List[BaseMessage]]:
    """
    Returns: (IncidentReport, List of raw messages for debugging)
    """
    print(f"🕵️‍♂️ Agent Investigation Started: {user_query}")
    
    # 1. Run the Agent (Protected by Tenacity)
    try:
        response_dict = invoke_agent_with_retry(user_query, callbacks)
    except Exception as e:
        # If 5 retries fail, return a fallback report
        print(f"❌ All retries failed: {e}")
        raise e
    
    # 2. Capture the history (The "Logs")
    messages = response_dict.get("messages", [])
    
    # 3. Extract final text for the Pydantic step
    investigation_notes = "No data."
    if messages and isinstance(messages[-1], AIMessage):
        investigation_notes = messages[-1].content

    # 4. Structure the output
    print("🏗️ Structuring final report...")
    structure_llm = llm.with_structured_output(IncidentReport)
    
    final_report = structure_llm.invoke(
        f"""
        You are a Senior Site Reliability Engineer. 
        Based on the raw investigation notes below, create a formal Incident Report.
        
        RAW INVESTIGATION NOTES:
        {investigation_notes}
        """
    )
    
    # RETURN BOTH
    return final_report, messages

# --- Quick Test ---
if __name__ == "__main__":
    print("🤖 Ops-Sentinel V2 is waking up...")
    
    test_query = "I am seeing high CPU on the Payment-API."
    
    # Run the new flow
    report, messages = run_agent(test_query)
    
    print("\n--- 📝 FINAL STRUCTURED REPORT ---")
    print(report.to_markdown())
    
    print("\n--- 💾 RAW Agent Logs ---")
    print(messages)
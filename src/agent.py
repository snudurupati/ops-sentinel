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
llm = ChatOpenAI(
    model_name="gpt-4o", 
    temperature=0,
    max_retries=5, 
    request_timeout=60
) 

# --- RETRY DECORATOR ---
# Accepts 'agent' as an argument to support JIT creation
@retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(5))
def invoke_agent_with_retry(agent, query, callbacks):
    return agent.invoke({"input": query}, config={"callbacks": callbacks})

# --- MAIN FUNCTION ---
def run_agent(user_query: str, callbacks=None) -> Tuple[IncidentReport, List[BaseMessage]]:
    """
    Returns: (IncidentReport, List of raw messages for debugging)
    """
    print(f"🕵️‍♂️ Agent Investigation Started: {user_query}")

    # 1. DYNAMIC PROMPT GENERATION (JIT)
    # We inject the USER QUERY directly into the system instructions.
    # This prevents the LLM from ignoring the input or overfitting to examples.
    
    dynamic_prompt = f"""
You are an expert Site Reliability Engineer (SRE) named 'Ops-Sentinel'.

CRITICAL CONTEXT:
The user is reporting an issue. Read their exact words below:
" **{user_query}** "

YOUR MISSION:
1. **EXTRACT**: Identify the specific service name mentioned in the user's words above (e.g., 'Payment-API', 'Auth', 'Kafka').
   - If the text says "I am seeing high CPU on the Payment-API", the target is "Payment-API".
   - Ignore words like "I", "am", "seeing", "check". Focus on the System/Service noun.

2. **INVESTIGATE**: Once you have the target name, run the investigation tools.

RULES:
- STEP 1: Check the database schema (list_tables_tool).
- STEP 2: GENERATE SQL.
    - **Constraint**: You must join `metrics` and `services`.
    - **SQL Template**: 
      `SELECT m.* FROM metrics m JOIN services s ON m.service_id = s.id WHERE lower(s.name) LIKE '%<INSERT_TARGET_NAME_HERE>%' ORDER BY m.timestamp DESC LIMIT 50`
    - **CRITICAL**: Replace `<INSERT_TARGET_NAME_HERE>` with the name you extracted from the user's words.
- STEP 3: Execute the query (query_metrics_tool).
- STEP 4: If you see errors or performance anomalies, search runbooks (search_runbooks_tool).
- STEP 5: Synthesize the findings into a final answer.

Do NOT stop after Step 1. Keep going until you have the answer.
"""
    
    # 2. Create the JIT Agent (Fresh Brain for every request)
    # We pass the custom dynamic prompt here.
    agent = create_agent(model=llm, tools=ALL_TOOLS, system_prompt=dynamic_prompt)
    
    # 3. Run the Agent (Protected by Tenacity)
    try:
        response_dict = invoke_agent_with_retry(agent, user_query, callbacks)
    except Exception as e:
        print(f"❌ All retries failed: {e}")
        raise e
    
    # 4. Capture the history
    messages = response_dict.get("messages", [])
    
    # 5. Extract final text
    investigation_notes = "No data."
    if messages and isinstance(messages[-1], AIMessage):
        investigation_notes = messages[-1].content

    # 6. Structure the output
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
    
    return final_report, messages

# --- Quick Test ---
if __name__ == "__main__":
    print("🤖 Ops-Sentinel V2 is waking up...")
    
    # Test with the sentence that broke the previous version
    test_query = "Auth Service is timing out. Check Auth Service for database locks."
    #"I am seeing high CPU on the Payment-API. Check Payment-API for CPU usage and investigate logs and runbooks?"
    
    report, messages = run_agent(test_query)
    
    print("\n--- 📝 FINAL STRUCTURED REPORT ---")
    print(report.to_markdown())
    
    print("\n--- 💾 RAW Agent Logs ---")
    print(messages)
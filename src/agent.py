import os
import yaml
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

# --- HELPER: LOAD PROMPTS ---
def load_config(file_name):
    """
    Loads YAML from the project root 'config' directory.
    Context: This script is in 'src/', so we must go UP one level.
    """
    # 1. Get the directory where THIS script (agent.py) lives (e.g., /project/src)
    src_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Go UP one level to the project root (e.g., /project)
    project_root = os.path.dirname(src_dir)
    
    # 3. Build path to config (e.g., /project/config/prompts.yaml)
    config_path = os.path.join(project_root, "config", file_name)
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

# --- RETRY DECORATOR ---
# Accepts 'agent' as an argument to support JIT creation
@retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(5))
def invoke_agent_with_retry(agent, query, callbacks):
    return agent.invoke({"input": query}, config={"callbacks": callbacks})

# --- MAIN FUNCTION ---
def run_agent(user_query: str, prompt_file: str = "prompts.yaml", callbacks=None) -> Tuple[IncidentReport, List[BaseMessage]]:
    """
    Returns: (IncidentReport, List of raw messages for debugging)
    """
    print(f"🕵️‍♂️ Agent Investigation Started: {user_query}")

    # 1. DYNAMIC PROMPT GENERATION (JIT)
    # We inject the USER QUERY directly into the system instructions.
    # This prevents the LLM from ignoring the input or overfitting to examples.
    
    # We load the "code" (logic) separate from the "prompt" (data)
    config = load_config(prompt_file)
    raw_prompt_template = config.get("agent_system_prompt")
    
    if not raw_prompt_template:
        raise ValueError("Key 'agent_system_prompt' missing in prompts.yaml")

    # INJECT VARIABLES
    # We use standard Python formatting to inject the user query into the YAML template
    formatted_system_prompt = raw_prompt_template.format(user_query=user_query)
    
    # 2. Create the JIT Agent (Fresh Brain for every request)
    # We pass the custom dynamic prompt here.
    agent = create_agent(model=llm, tools=ALL_TOOLS, system_prompt=formatted_system_prompt)
    
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
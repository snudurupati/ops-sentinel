from dotenv import load_dotenv
from langchain_openai import ChatOpenAI 
from langchain.agents import create_agent
from src.mcp_server import ALL_TOOLS
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage

load_dotenv()       

# 1. Initialize the LLM
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0) 

# 2. Define the System Prompt (The "Personality")
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
#Using OpenAI specific constructor
agent = create_agent(model=llm, tools=ALL_TOOLS, system_prompt=prompt)


def run_agent(user_query: str):
    """Entry point for the frontend to call the agent."""
    response = agent.invoke({"input": user_query})
    return response

def print_thought_process(response):
    """
    Iterates through the agent's message history to print the thought process.
    """
    messages = response.get("messages", [])
    
    print("\n------------------ AGENT THOUGHT PROCESS ------------------\n")
    
    for msg in messages:
        # 1. The User's Input
        if isinstance(msg, HumanMessage):
            print(f"👤 User: {msg.content}\n")
            
        # 2. The Agent's Decisions (Thoughts & Tool Calls)
        elif isinstance(msg, AIMessage):
            # If the agent decided to call a tool
            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    print(f"🧠 Thought: I need to call '{tool_call['name']}'")
                    print(f"   Args: {tool_call['args']}\n")
            # If the agent has a final text response
            elif msg.content:
                print(f"🤖 Final Answer: {msg.content}\n")
                
        # 3. The Tool's Output (Observations)
        elif isinstance(msg, ToolMessage):
            # Truncate long outputs for readability
            content = str(msg.content)
            if len(content) > 500:
                content = content[:500] + "... (truncated)"
            print(f"🛠️ Tool Output ({msg.name}): {content}\n")
            
    print("-----------------------------------------------------------\n")

# --- Quick Test ---
if __name__ == "__main__":
    print("🤖 Ops-Sentinel is waking up...")
    
    test_query = "I am seeing high CPU on the Payment-API. Can you investigate logs from the last hour and check if there are any runbooks for this?"
    
    # Run the agent (returns the full dictionary)
    response = agent.invoke({"input": test_query})
    
    # Print the beautiful step-by-step logic
    print_thought_process(response)


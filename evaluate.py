import pandas as pd
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from src.agent import run_agent  # Import your agent function

# --- CONFIGURATION ---
JUDGE_MODEL = "gpt-4o"  # The Judge should be smart (often smarter than the agent)

# A Test Case has a query and the "Expected Behavior" we want to enforce
TEST_CASES = [
    {
        "id": "TC-001",
        "query": "Auth Service is timing out. Check Auth Service for database locks.",
        "expected_behavior": "The agent must check the schema and metrics FIRST. It should NOT search runbooks immediately.",
    },
    {
        "id": "TC-002",
        "query": "Payment-API is healthy. Just checking status.",
        "expected_behavior": "The agent should check metrics. Since metrics are healthy, it should explicitly SKIP the runbook search.",
    }
]

# --- THE JUDGE ---
def llm_judge(query: str, logs: List, expected_behavior: str) -> Dict:
    """
    Evaluates the Agent's execution trace against the expected behavior.
    """
    judge_llm = ChatOpenAI(model=JUDGE_MODEL, temperature=0)

    # Convert complex tool logs into a simple readable text trace
    trace_text = ""
    for msg in logs:
        if msg.type == "ai" and msg.tool_calls:
            for tool in msg.tool_calls:
                trace_text += f"➡️ AGENT CALLED: {tool['name']} with args {tool['args']}\n"
        elif msg.type == "tool":
            # Truncate long tool outputs for the judge to save tokens
            content_preview = str(msg.content)[:200] + "..."
            trace_text += f"⬅️ TOOL OUTPUT: {content_preview}\n"

    # The Rubric
    judge_prompt = f"""
    You are a strict QA Judge evaluating an AI Agent's performance.

    CONTEXT:
    - User Query: "{query}"
    - Expected Behavior: "{expected_behavior}"

    ACTUAL AGENT EXECUTION TRACE:
    {trace_text}

    TASK:
    1. Did the agent follow the expected behavior?
    2. Did it call tools in the correct order?
    3. Did it hallucinate or skip steps?

    OUTPUT FORMAT (JSON ONLY):
    {{
        "score": (integer 0-100),
        "pass": (boolean),
        "reasoning": "(short explanation)"
    }}
    """

    response = judge_llm.invoke(judge_prompt)
    
    # Simple structured output parsing
    try:
        # Check if the model wrapped JSON in code blocks
        content = response.content.replace("```json", "").replace("```", "").strip()
        import json
        return json.loads(content)
    except Exception as e:
        return {"score": 0, "pass": False, "reasoning": f"Judge Error: {e}"}

# --- MAIN EVALUATION LOOP ---
def run_evaluation():
    results = []

    # We will test BOTH versions of your prompt
    prompt_versions = ["prompts.yaml", "prompts_V1_20260105.yaml"]

    print(f"⚖️  Starting Evaluation on {len(TEST_CASES)} test cases...")

    for version in prompt_versions:
        print(f"\n📂 TESTING PROMPT VERSION: {version}")
        
        for case in TEST_CASES:
            print(f"  🔹 Case {case['id']}: {case['query'][:40]}...")
            
            # 1. Run the Student (Your Agent)
            try:
                # We suppress print statements from the agent to keep the console clean
                # (In a real app, you'd use logging levels)
                final_answer, raw_logs = run_agent(case['query'], prompt_file=version)
                
                # 2. Run the Judge
                eval_result = llm_judge(case['query'], raw_logs, case['expected_behavior'])
                
                # 3. Record Results
                results.append({
                    "Prompt Version": version,
                    "Test Case": case['id'],
                    "Pass": eval_result["pass"],
                    "Score": eval_result["score"],
                    "Reasoning": eval_result["reasoning"]
                })
                print(f"     👉 Score: {eval_result['score']}/100 | {eval_result['reasoning']}")

            except Exception as e:
                print(f"     ❌ CRASH: {e}")
                results.append({
                    "Prompt Version": version,
                    "Test Case": case['id'],
                    "Pass": False,
                    "Score": 0,
                    "Reasoning": "Agent Crashed"
                })

    # --- FINAL REPORT ---
    print("\n\n📊 --- FINAL SCORECARD ---")
    df = pd.DataFrame(results)
    print(df.to_markdown(index=False))

    # Optional: Save to CSV
    df.to_csv("evaluation_results.csv", index=False)
    print("\n✅ Results saved to evaluation_results.csv")

if __name__ == "__main__":
    run_evaluation()
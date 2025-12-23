import streamlit as st
import sys
import os
import time

# --- 1. Path Setup ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.agent import run_agent
from src.instrumentation import setup_telemetry
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage

# --- 2. Initialize Telemetry ---
if "telemetry_setup" not in st.session_state:
    setup_telemetry()
    st.session_state.telemetry_setup = True

# --- 3. Page Config & CSS (The V1 Polish) ---
st.set_page_config(
    page_title="Aether: SRE Agent",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Apple/Material Design
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Branding */
    .sidebar-brand {
        display: flex; align-items: center; gap: 15px; padding-bottom: 20px;
        border-bottom: 1px solid #E5E5EA; margin-bottom: 20px;
    }
    .sidebar-logo { font-size: 2.5rem; }
    .sidebar-text { font-size: 2rem; font-weight: 800; color: #1d1d1f; letter-spacing: -0.5px; }
    
    /* Metrics Cards */
    .metric-card {
        background-color: white; border-radius: 12px; padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid #E5E5EA; text-align: center;
    }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #1d1d1f; }
    .metric-label { font-size: 0.9rem; color: #86868b; font-weight: 600; text-transform: uppercase; }

    /* Hero Headers */
    .hero-title {
        font-family: 'Inter', sans-serif; font-weight: 800; font-size: 3rem; letter-spacing: -1px;
        background: -webkit-linear-gradient(45deg, #2c3e50, #4ca1af);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;
    }
    .hero-subtitle { font-size: 1.3rem; color: #86868b; margin-bottom: 20px; font-weight: 400; }
    
    /* Status Pills */
    .status-pill {
        display: inline-flex; align-items: center; padding: 6px 14px;
        background-color: #E8F5E9; color: #2E7D32; border-radius: 20px;
        font-size: 0.9rem; font-weight: 600; margin-right: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar: Control Center ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <span class="sidebar-logo">💠</span>
        <span class="sidebar-text">Aether</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("v2.5.0 • Enterprise Edition")
    
    # Live Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-label">Latency</div><div class="metric-value">12ms</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-label">Errors</div><div class="metric-value">0.0%</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("**⚡ ACTIVE INCIDENTS**")
    
    # Preset Scenarios
    # 1. Payment API (Original)
    if st.button("🔥 Payment API: High Latency", use_container_width=True):
        st.session_state.prompt_trigger = "I am seeing high CPU on the Payment-API. Check Payment-API for CPU usage and investigate logs and runbooks?"
    
    # 2. Auth Service (Original)
    if st.button("🔒 Auth Service: Locks", use_container_width=True):
        st.session_state.prompt_trigger = "Auth Service is timing out. Check Auth Service for database locks."

    # 3. Kafka Lag (New)
    if st.button("📨 Kafka: Consumer Lag", use_container_width=True):
        st.session_state.prompt_trigger = "Kafka consumer group 'order-processing' is lagging behind by 50,000 messages. Check Kafka throughput and errors."

    # 4. Kubernetes Crash (New)
    if st.button("☸️ K8s: Pod CrashLoop", use_container_width=True):
        st.session_state.prompt_trigger = "The 'inventory-service' pods are in CrashLoopBackOff. Check pods termination logs and resource limits."

    # 5. Redis Miss (New)
    if st.button("🧠 Redis: High Miss Rate", use_container_width=True):
        st.session_state.prompt_trigger = "Cache miss rate on the 'user-profile' cluster jumped to 40%. Check Redis eviction policies and memory usage."

# --- 5. Main UI ---
st.markdown('<div class="hero-title">Aether Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Autonomous Site Reliability Engineering (SRE) Agent</div>', unsafe_allow_html=True)

st.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 20px;">
    <span class="status-pill">● System Online</span>
    <span class="status-pill" style="background-color: #FFF3E0; color: #E65100;">🔒 PII Redaction Active</span>
</div>
""", unsafe_allow_html=True)

# --- 6. Chat Logic (The Brain) ---
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "Good morning. I am Aether. I'm monitoring 142 services. Select an incident from the sidebar or type a query to begin."
    }]

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle Inputs (Sidebar Button OR Text Input)
user_input = None
if "prompt_trigger" in st.session_state and st.session_state.prompt_trigger:
    user_input = st.session_state.prompt_trigger
    del st.session_state.prompt_trigger # Clear it
elif prompt := st.chat_input("Ask Aether to investigate..."):
    user_input = prompt

# --- 7. Execution Loop ---
if user_input:
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Assistant Acts
    with st.chat_message("assistant"):
        # The "Thinking" Status Container
        with st.status("🧠 Neural Engine Processing...", expanded=True) as status:
            try:
                # Call V2 Agent (Returns Report + History)
                final_report, history = run_agent(user_input)
                
                # Render the Thoughts (The "Replay" Strategy)
                for msg in history:
                    if isinstance(msg, AIMessage) and msg.tool_calls:
                        for tool in msg.tool_calls:
                            st.write(f"🛠️ **Activating Tool:** `{tool['name']}`")
                            st.code(f"Arguments: {tool['args']}")
                            time.sleep(0.2) # Cinematic delay
                    elif isinstance(msg, ToolMessage):
                        with st.expander(f"📄 Result from {msg.name}"):
                            st.code(msg.content[:500] + "...")
                
                status.update(label="✅ Investigation Complete", state="complete", expanded=True)
                
                # Render Final Pydantic Report
                final_markdown = final_report.to_markdown()
                st.markdown(final_markdown)
                
                # Save to history so it stays after refresh
                st.session_state.messages.append({"role": "assistant", "content": final_markdown})

            except Exception as e:
                status.update(label="❌ Error", state="error")
                st.error(f"Analysis Failed: {str(e)}")
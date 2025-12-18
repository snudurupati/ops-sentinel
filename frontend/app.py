import streamlit as st
import sys
import os
import time

# --- 1. Path Setup ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.agent import run_agent
from langchain_core.messages import AIMessage, ToolMessage

# --- 2. Brand Config: AETHER ---
BRAND_NAME = "Aether"
PAGE_TITLE = "Aether Intelligence"
ICON = "💠"  # The official Logo

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 3. APPLE / MATERIAL DESIGN CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Base Settings */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        font-size: 18px; 
    }
    
    .stApp { background-color: #F5F5F7; }
    
    /* Sidebar Branding */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 15px;
        padding-bottom: 20px;
        border-bottom: 1px solid #E5E5EA;
        margin-bottom: 20px;
    }
    .sidebar-logo {
        font-size: 2.5rem;
    }
    .sidebar-text {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #1d1d1f;
    }
    
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
    .hero-subtitle {
        font-size: 1.3rem;
        color: #86868b;
        margin-bottom: 20px;
        font-weight: 400;
    }
    
    /* Chat Message Styling */
    .stChatMessage .stMarkdown p {
        font-size: 1.1rem !important;
        line-height: 1.6;
    }
    
    /* Status Pills */
    .status-pill {
        display: inline-flex; align-items: center; padding: 6px 14px;
        background-color: #E8F5E9; color: #2E7D32; border-radius: 20px;
        font-size: 0.9rem; font-weight: 600; margin-right: 10px;
    }
    
    /* Button Styling */
    .stButton>button {
        background-color: white; color: #1d1d1f; border: 1px solid #d2d2d7;
        border-radius: 8px; font-weight: 600; font-size: 1rem;
        width: 100%; transition: all 0.2s; padding: 0.6rem;
    }
    .stButton>button:hover {
        border-color: #0071e3; color: #0071e3; background-color: #f5f5f7;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar: THE CONTROL CENTER ---
with st.sidebar:
    # 🔹 BRANDING HEADER
    st.markdown(f"""
    <div class="sidebar-brand">
        <span class="sidebar-logo">{ICON}</span>
        <span class="sidebar-text">{BRAND_NAME}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("v2.4.0 • Enterprise Edition")
    
    # Live Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-label">Latency</div><div class="metric-value">12ms</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-label">Errors</div><div class="metric-value">0.01%</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    
    # SCENARIO LAUNCHER
    st.markdown("**⚡ ACTIVE INCIDENTS**")
    st.caption("Select a live alert to auto-investigate:")
    
    if st.button("🔥 Payment API: High Latency"):
        st.session_state.messages.append({"role": "user", "content": "Alert: Payment API latency is spiking > 500ms. Investigate logs and runbooks."})
        st.rerun()
        
    if st.button("🔒 Auth Service: DB Locks"):
        st.session_state.messages.append({"role": "user", "content": "Alert: Auth Service is timing out. Check for database locks or deadlocks."})
        st.rerun()
        
    if st.button("💾 Storage: Volume Capacity"):
        st.session_state.messages.append({"role": "user", "content": "Warning: Disk usage on Log-Cluster-01 is at 92%. Suggest remediation."})
        st.rerun()

# --- 5. Main Area ---

# Header
st.markdown(f'<div class="hero-title">{BRAND_NAME} Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Autonomous Site Reliability Engineering (SRE) Agent</div>', unsafe_allow_html=True)

# Status Bar
st.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 20px;">
    <span class="status-pill">● System Operational</span>
    <span class="status-pill" style="background-color: #FFF3E0; color: #E65100;">🔒 PII Redaction Active</span>
</div>
""", unsafe_allow_html=True)

# --- 6. Chat Logic ---

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Good morning. I am Aether. I'm monitoring 142 services. Select an incident from the sidebar or type a query to begin."
    })

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Handling
if prompt := st.chat_input("Ask Aether to investigate..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# --- 7. AGENT EXECUTION (WITH VISIBLE BRAIN) ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    
    user_input = st.session_state.messages[-1]["content"]

    with st.chat_message("assistant"):
        # EXPANDED=TRUE makes sure it stays open!
        with st.status("🧠 Neural Engine Processing...", expanded=True) as status:
            try:
                # 1. Run the Agent (Expects return of the full response dict)
                response = run_agent(user_input)
                
                # 2. Parse the steps for the UI
                if isinstance(response, dict) and "messages" in response:
                    messages = response["messages"]
                    final_answer = messages[-1].content
                    
                    # Iterate through intermediate steps to show "Thoughts"
                    for msg in messages:
                        if isinstance(msg, AIMessage) and msg.tool_calls:
                            for tool in msg.tool_calls:
                                st.write(f"🛠️ **Activating Tool:** `{tool['name']}`")
                                st.code(f"Arguments: {tool['args']}")
                                time.sleep(0.3) # Fake delay for dramatic effect
                        elif isinstance(msg, ToolMessage):
                            with st.expander(f"📄 Result from {msg.name}"):
                                st.code(msg.content[:500] + "...") # Truncate long logs
                
                    # KEEPS THE STATUS EXPANDED
                    status.update(label="✅ Analysis Complete", state="complete", expanded=True)
                    
                    # 3. Display Final Answer
                    st.markdown(f"### 🛡️ Incident Report\n{final_answer}")
                    st.session_state.messages.append({"role": "assistant", "content": final_answer})
                
                else:
                    # Fallback
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    status.update(label="✅ Complete", state="complete", expanded=True)

            except Exception as e:
                status.update(label="❌ Error", state="error")
                st.error(f"Analysis Failed: {str(e)}")
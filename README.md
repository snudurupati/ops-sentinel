# Ops-Sentinel 🛡️
### The Autonomous Site Reliability Engineer (SRE)

**Ops-Sentinel** is an intelligent agent designed to autonomously investigate infrastructure incidents. It bridges the gap between structured telemetry (SQL logs) and unstructured institutional knowledge (Runbooks/Docs) to reduce Mean Time to Resolution (MTTR).

Unlike generic chatbots, Ops-Sentinel uses the **Model Context Protocol (MCP)** to safely interact with production systems, ensuring security and "human-in-the-loop" authorization.

---

## 🏗️ Architecture

![Architecture Diagram](https://placehold.co/600x400?text=Architecture+Diagram+Placeholder)

The system operates on three layers:
1.  **The Brain (Agent):** Orchestrates the investigation using LangChain/AI Agents.
2.  **The Protocol (MCP):** A standardized interface connecting the AI to:
    * **Structured Data:** SQLite/Postgres (Metrics, Logs, Deployments).
    * **Unstructured Data:** Vector DB (Runbooks, Post-Mortems).
3.  **The Interface (UI):** A Streamlit dashboard for interactive debugging and authorization.

## 🚀 Key Features

* **Automated Root Cause Analysis:** Correlates CPU spikes with deployment events automatically.
* **Context-Aware Remediation:** Retrieves the *exact* runbook command needed to fix a specific error.
* **Safe Execution:** Uses a "Read-Only" mode by default; sensitive commands require human approval.
* **Privacy-First:** PII redaction layer prevents sensitive log data from leaking to the LLM.

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **AI Orchestration:** LangChain / PydanticAI
* **Protocol:** Model Context Protocol (MCP)
* **Database:** SQLite (Structured), ChromaDB (Vector)
* **Observability:** OpenTelemetry / Arize Phoenix
* **Frontend:** Streamlit

## ⚡ Quick Start

### 1. Installation

    git clone https://github.com/yourusername/ops-sentinel.git
    cd ops-sentinel
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt

### 2. Setup Environment
Create a `.env` file in the root directory:

    OPENAI_API_KEY=sk-your-key-here

### 3. Generate Mock Data (The "World Builder")
Initialize the database with synthetic telemetry logs and incident runbooks:

    python generate_data.py

*This creates `sre_observability.db` and populates the `knowledge_base/` folder.*

### 4. Run the Agent
*(Coming Soon...)*

## 📂 Repository Structure

    ops-sentinel/
    ├── generate_data.py         # Synthetic data generator (Logs + Runbooks)
    ├── sre_observability.db     # (Generated) Structured Metrics DB
    ├── knowledge_base/          # (Generated) Markdown Runbooks
    ├── src/                     # Core Application Logic
    │   ├── agent.py             # Agent Logic
    │   └── mcp_server.py        # Tool Definitions
    ├── frontend/                # Streamlit Dashboard
    └── tests/                   # Eval Harness

---
*Built as a strategic demonstration of Agentic Data Engineering.*
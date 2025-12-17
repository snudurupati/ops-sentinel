<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ops-Sentinel README</title>
</head>
<body>

    <h1>Ops-Sentinel 🛡️</h1>
    <h3>The Autonomous Site Reliability Engineer (SRE)</h3>

    <p>
        <strong>Ops-Sentinel</strong> is an intelligent agent designed to autonomously investigate infrastructure incidents. 
        It bridges the gap between structured telemetry (SQL logs) and unstructured institutional knowledge (Runbooks/Docs) 
        to reduce Mean Time to Resolution (MTTR).
    </p>

    <p>
        Unlike generic chatbots, Ops-Sentinel uses the <strong>Model Context Protocol (MCP)</strong> to safely interact with 
        production systems, ensuring security and "human-in-the-loop" authorization.
    </p>

    <hr>

    <h2>🏗️ Architecture</h2>

    <p><em></em></p>

    <p>The system operates on three layers:</p>
    <ol>
        <li><strong>The Brain (Agent):</strong> Orchestrates the investigation using LangChain/AI Agents.</li>
        <li><strong>The Protocol (MCP):</strong> A standardized interface connecting the AI to:
            <ul>
                <li><strong>Structured Data:</strong> SQLite/Postgres (Metrics, Logs, Deployments).</li>
                <li><strong>Unstructured Data:</strong> Vector DB (Runbooks, Post-Mortems).</li>
            </ul>
        </li>
        <li><strong>The Interface (UI):</strong> A Streamlit dashboard for interactive debugging and authorization.</li>
    </ol>

    <h2>🚀 Key Features</h2>

    <ul>
        <li><strong>Automated Root Cause Analysis:</strong> Correlates CPU spikes with deployment events automatically.</li>
        <li><strong>Context-Aware Remediation:</strong> Retrieves the <em>exact</em> runbook command needed to fix a specific error.</li>
        <li><strong>Safe Execution:</strong> Uses a "Read-Only" mode by default; sensitive commands require human approval.</li>
        <li><strong>Privacy-First:</strong> PII redaction layer prevents sensitive log data from leaking to the LLM.</li>
    </ul>

    <h2>🛠️ Tech Stack</h2>

    <ul>
        <li><strong>Language:</strong> Python 3.10+</li>
        <li><strong>AI Orchestration:</strong> LangChain / PydanticAI</li>
        <li><strong>Protocol:</strong> Model Context Protocol (MCP)</li>
        <li><strong>Database:</strong> SQLite (Structured), ChromaDB (Vector)</li>
        <li><strong>Observability:</strong> OpenTelemetry / Arize Phoenix</li>
        <li><strong>Frontend:</strong> Streamlit</li>
    </ul>

    <h2>⚡ Quick Start</h2>

    <h3>1. Installation</h3>
    <pre><code>git clone https://github.com/yourusername/ops-sentinel.git
cd ops-sentinel
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt</code></pre>

    <h3>2. Setup Environment</h3>
    <p>Create a <code>.env</code> file in the root directory:</p>
    <pre><code>OPENAI_API_KEY=sk-your-key-here</code></pre>

    <h3>3. Generate Mock Data (The "World Builder")</h3>
    <p>Initialize the database with synthetic telemetry logs and incident runbooks:</p>
    <pre><code>python generate_data.py</code></pre>
    <p><em>This creates <code>sre_observability.db</code> and populates the <code>knowledge_base/</code> folder.</em></p>

    <h3>4. Run the Agent</h3>
    <p><em>(Coming Soon...)</em></p>

    <h2>📂 Repository Structure</h2>

    <pre><code>ops-sentinel/
├── generate_data.py         # Synthetic data generator (Logs + Runbooks)
├── sre_observability.db     # (Generated) Structured Metrics DB
├── knowledge_base/          # (Generated) Markdown Runbooks
├── src/                     # Core Application Logic
│   ├── agent.py             # Agent Logic
│   └── mcp_server.py        # Tool Definitions
├── frontend/                # Streamlit Dashboard
└── tests/                   # Eval Harness</code></pre>

    <hr>
    <p><em>Built as a strategic demonstration of Agentic Data Engineering.</em></p>

</body>
</html>

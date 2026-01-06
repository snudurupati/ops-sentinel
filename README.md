# 💠 Aether: Autonomous SRE Agent

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)
![Status](https://img.shields.io/badge/Status-Prototype-green)
![Observability](https://img.shields.io/badge/Tracing-OpenTelemetry-purple)

> **"The Self-Healing Infrastructure Layer."**

Aether is an autonomous agent designed to assist Site Reliability Engineers (SREs) by reducing the Mean Time To Resolution (MTTR) for infrastructure incidents. It combines **SQL-based telemetry analysis** with **semantic search over runbooks** to diagnose issues without human intervention.

## 🏗️ Architecture

```mermaid
graph TD
    User[👤 SRE User] -->|1. Incident Report| UI["💻 Aether Dashboard (Streamlit)"]
    
    subgraph "Secure Enclave (Docker Container)"
        UI -->|2. Sends Prompt| Agent[🧠 LangChain Agent]
        
        Agent -->|3. Decision Loop| Router{Determine Tool}
        
        Router -->|Need Metrics?| SQL[📊 SQL Tool]
        Router -->|Need Knowledge?| RAG["📚 Vector Search (ChromaDB)"]
        
        SQL -->|Raw Data| DB[(SQLite DB)]
        RAG -->|Raw Text| VDB[(Runbooks)]
        
        DB -->|4. Return Data| PII[🛡️ PII Redaction Layer]
        VDB -->|4. Return Docs| PII
        
        PII -->|5. Sanitized Data| Agent
    end
    
    Agent -->|6. Final Diagnosis| UI
    
    style PII fill:#ffcccc,stroke:#ff0000,stroke-width:2px,stroke-dasharray: 5 5
    style Agent fill:#e1f5fe,stroke:#01579b
```

## 🚀 Key Features

* **🧠 Autonomous Reasoning Loop:** Uses Chain-of-Thought (CoT) to plan investigations (Schema Check → Query Metrics → Search Runbooks).
* **🔭 Full Observability:** integrated **OpenTelemetry** tracing to visualize the agent's decision-making process in Jaeger.
* **🛡️ PII Redaction Middleware:** Custom regex-based firewall that intercepts all database outputs to strip Emails, API Keys, and SSNs before they reach the LLM context window.
* **📊 Multi-Modal Investigation:** Correlates structured time-series data (SQLite) with unstructured institutional knowledge (ChromaDB).
* **🐳 Production Ready:** Fully containerized with Docker for consistent deployment.

## 🛠️ Engineering Optimizations & Tuning Log

The development of Aether involved solving critical production challenges common to LLM agents. Below is a log of the key optimizations implemented to ensure reliability and cost-efficiency.

### 1. Architectural Pattern: "Just-In-Time" (JIT) Agents
* **The Problem:** Global context poisoning. Queries about one service (e.g., "Payment") would bleed into subsequent queries about others (e.g., "Kafka"), causing the agent to hallucinate incorrect SQL joins.
* **The Solution:** Implemented a **JIT Agent Factory**.
    * Every user request spins up a fresh, stateless agent instance.
    * This ensures zero cross-request contamination and strictly isolated decision-making contexts.

### 2. Schema-Aware Prompt Engineering
* **The Problem:** LLMs often fail to respect Database Normalization (e.g., trying to find `service_name` in a metrics table that only has `service_id`).
* **The Solution:** A **Dynamic System Prompt** that injects the exact user query into the instructions.
    * We replaced static few-shot examples (which caused overfitting) with dynamic algebraic instructions.
    * **Technique:** `LIKE '%{extracted_service_name}%'` pattern matching forced the agent to handle fuzzy inputs (e.g., "auth" vs "Auth-Service") robustly.

### 3. Token & Cost Optimization
* **The Problem:** Large runbooks triggered `429 Rate Limit` errors and slow response times.
* **The Solution:**
    * **Safety Cap:** Hard-coded 8,000-character limits on RAG outputs.
    * **Truncation:** Implemented "Head + Tail" slicing to preserve document context without blowing up the token window.

### 4. Performance Caching
* **The Problem:** Recurring queries caused database locks and sluggish demos.
* **The Solution:** Integrated `InMemoryCache` to serve identical reasoning traces in <0.1s, dramatically improving the user experience during repetitive debugging.

### 5. Reliability Engineering
* **The Problem:** Network flakiness or LLM "stop early" behaviors.
* **The Solution:**
    * **Tenacity Retries:** Applied exponential backoff decorators (`@retry`) to handle transient failures.
    * **Strict Ordering:** Enforced tool execution order (Schema → Metrics → Runbooks) via system prompt constraints.

### 6. Dynamic Prompt Versioning
* **The Problem:** Hardcoding system prompts made it impossible to iterate on prompt logic without redeploying code.
* **The Solution:** Decoupled prompts into `config/*.yaml` files.
    * The agent now supports a `prompt_file` parameter, enabling A/B testing between different reasoning strategies (e.g., `prompts.yaml` vs `prompts_V1_20260105.yaml`).

## ⚖️ Automated Evaluation (LLM-as-Judge)

To ensure the agent remains robust as prompt logic evolves, we've implemented an automated benchmarking suite in `evaluate.py`.

* **Technique:** **LLM-as-Judge**.
* **How it works:** 
    1. A "Student" Agent runs a set of test cases.
    2. The raw execution trace (tool calls and outputs) is captured.
    3. A "Judge" (GPT-4o) evaluates the trace against a strict rubric of "Expected Behavior".
    4. The Judge provides a 0-100 score, a Pass/Fail status, and detailed reasoning.
* **Usage:**
  ```bash
  python evaluate.py
  ```

## 🧪 Expanded Testing Suite
We have introduced granular test suites to validate specific agent capabilities:
* `tests/test_memory.py`: Validates context retention across multiple turns.
* `tests/test_reasoning.py`: Ensures correct tool sequencing (Schema → Metrics → Runbooks).
* `tests/test_security.py`: Rigorous validation of the PII redaction layer.
* `tests/test_ui.py`: Basic health checks for the Streamlit interface.

## ⚡ Quick Start (Docker)

The fastest way to run Aether is via Docker.

**1. Clone the repository**
```bash
git clone [https://github.com/snudurupati/ops-sentinel.git](https://github.com/snudurupati/ops-sentinel.git)
cd ops-sentinel
```

**2. Build the Image**
```bash
docker-compose build --no-cache
```

**3. Run the Container**
*(Ensure your `.env` file contains your `OPENAI_API_KEY`)*
```bash
docker-compose up
```

**4. Access the Dashboard**
Navigate to `http://localhost:8501`

## 🛠️ Tech Stack

* **Orchestration:** LangChain (OpenAI Tools Agent)
* **Interface:** Streamlit (Custom CSS)
* **Observability:** OpenTelemetry (Jaeger Exporter)
* **Database:** SQLite (Normalized Schema), ChromaDB (Vector Store)
* **LLM:** GPT-4o / GPT-4o-mini
* **Evaluation:** LLM-as-Judge (metrics tracking via `evaluate.py`)
* **Infrastructure:** Docker, Python 3.12
* **Reliability:** Tenacity (Retries), Pydantic (Data Validation), Tabulate (CLI Reports)

## 🔮 Future Roadmap (V2)

* [x] **LLM-as-Judge:** Automated evaluation of reasoning traces.

* [ ] **Human-in-the-Loop:** Approval workflow before executing write operations (e.g., restarting pods).
* [ ] **GraphRAG:** Migrating from SQL Joins to a Graph Database (ArangoDB) for semantic relationship mapping.
* [ ] **RBAC:** Role-Based Access Control via OAuth2.
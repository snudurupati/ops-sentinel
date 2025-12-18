import sqlite3
import random
import os
from datetime import datetime, timedelta

# --- Configuration ---
DB_NAME = "data/sre_observability.db"
KNOWLEDGE_DIR = "knowledge_base"
INCIDENT_TIME_HOUR = 14  # The incident happens at 2:00 PM (14:00)

# --- 1. Setup SQLite Database (Structured Data) ---
def setup_database():
    db_dir = os.path.dirname(DB_NAME)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create Tables
    cursor.execute('''
        CREATE TABLE services (
            id INTEGER PRIMARY KEY,
            name TEXT,
            owner TEXT,
            status TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE deployments (
            id INTEGER PRIMARY KEY,
            service_id INTEGER,
            version TEXT,
            deployed_at TIMESTAMP,
            status TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE metrics (
            id INTEGER PRIMARY KEY,
            service_id INTEGER,
            cpu_percent REAL,
            memory_percent REAL,
            error_rate REAL,
            log_level TEXT,
            timestamp TIMESTAMP
        )
    ''')

    # Seed Services
    services = [
        (1, "Payment-API", "FinTech Squad", "Active"),
        (2, "Auth-Service", "Security Team", "Active"),
        (3, "Notification-Worker", "Platform Team", "Active")
    ]
    cursor.executemany('INSERT INTO services VALUES (?,?,?,?)', services)
    
    conn.commit()
    return conn

# --- 2. Generate Synthetic Telemetry Logs ---
def generate_logs(conn):
    cursor = conn.cursor()
    print("generating logs...")
    
    # Generate 24 hours of data
    start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for hour in range(24):
        for minute in range(0, 60, 5): # Log every 5 minutes
            current_time = start_time + timedelta(hours=hour, minutes=minute)
            
            for service_id in [1, 2, 3]:
                # DEPLOYMENT EVENT: At 1:00 PM (13:00), deploy v2.1 to Payment-API
                if service_id == 1 and hour == 13 and minute == 0:
                    cursor.execute(
                        "INSERT INTO deployments (service_id, version, deployed_at, status) VALUES (?, ?, ?, ?)",
                        (1, "v2.1.0", current_time, "SUCCESS")
                    )

                # DEFAULT: Healthy System
                cpu = random.uniform(10, 30)
                memory = random.uniform(20, 40)
                error = random.uniform(0, 0.5)
                log_level = "INFO"

                # INCIDENT SIMULATION: Payment-API goes crazy at 14:00 (2 PM)
                if service_id == 1 and hour >= INCIDENT_TIME_HOUR:
                    cpu = random.uniform(85, 99)   # SPIKE!
                    memory = random.uniform(70, 90)
                    error = random.uniform(15, 50) # High Error Rate!
                    log_level = "ERROR"
                
                cursor.execute(
                    "INSERT INTO metrics (service_id, cpu_percent, memory_percent, error_rate, log_level, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                    (service_id, cpu, memory, error, log_level, current_time)
                )

    conn.commit()
    print(f"✅ Database created: {DB_NAME}")

# --- 3. Generate Runbooks (Unstructured Data) ---
def generate_runbooks():
    if not os.path.exists(KNOWLEDGE_DIR):
        os.makedirs(KNOWLEDGE_DIR)
    
    # Runbook 1: The Solution (Matches the Incident)
    rb_payment = """
# Runbook: Payment API High Latency & CPU

**Symptoms:**
- CPU usage > 80% on Payment-API nodes.
- Error rate spikes on `/process-transaction` endpoint.
- Usually occurs after a deployment involving the Redis Cache layer.

**Root Cause:**
This is typically a "Cache Stampede." When a new version is deployed, the cache is cold, and all requests hit the database simultaneously.

**Resolution:**
1. Do NOT rollback immediately.
2. Run the `warm_redis_cache` command via CLI.
3. If CPU does not drop within 5 minutes, restart the pods.

**Owner:** FinTech Squad
    """
    
    # Runbook 2: Distractor (Database Issues)
    rb_db = """
# Runbook: Postgres Connection Pool Exhaustion

**Symptoms:**
- Error: `FATAL: remaining connection slots are reserved for non-replication superuser roles`
- Service: Any

**Resolution:**
1. Check active connections: `SELECT count(*) FROM pg_stat_activity;`
2. Kill idle connections or increase `max_connections` in AWS RDS settings.
    """

    # Post-Mortem 3: Distractor (Old Auth Incident)
    pm_auth = """
# Post-Mortem: Incident #2024-001 (Auth Service Outage)

**Date:** 2024-01-15
**Service:** Auth-Service
**Impact:** Users could not login for 45 mins.

**Root Cause:**
Expired SSL Certificate on the load balancer.
**Action Item:**
Auto-renewal script was patched.
    """

    with open(f"{KNOWLEDGE_DIR}/runbook_payment_cpu.md", "w") as f:
        f.write(rb_payment.strip())
    
    with open(f"{KNOWLEDGE_DIR}/runbook_db_connections.md", "w") as f:
        f.write(rb_db.strip())

    with open(f"{KNOWLEDGE_DIR}/post_mortem_auth.md", "w") as f:
        f.write(pm_auth.strip())
        
    print(f"✅ Runbooks generated in: ./{KNOWLEDGE_DIR}/")

if __name__ == "__main__":
    conn = setup_database()
    generate_logs(conn)
    generate_runbooks()
    conn.close()
    print("\n🚀 Day 1 Complete. Ready for Day 2.")

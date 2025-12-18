from src.mcp_server import query_metrics_tool

# Mock a "fake" database response by manually passing a string to the redactor
# (In a real run, this comes from the DB)
from src.security import redactor

dirty_data = '[{"log_message": "User login failed. Email: jeff@amazon.com. Key: sk-9999999999999"}]'

print("--- SECURITY TEST ---")
print(f"RAW DATA: {dirty_data}")
print(f"CLEANED:  {redactor.redact(dirty_data)}")
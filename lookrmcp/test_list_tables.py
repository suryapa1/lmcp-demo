#!/usr/bin/env python3
"""
Quick test of the list_tables MCP tool
"""

import json
import requests
import uuid

SERVICE_URL = "https://sqlite-mcp-646005218605.us-central1.run.app"
MCP_ENDPOINT = f"{SERVICE_URL}/mcp"

def send_mcp_request(method, params=None):
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": method
    }
    if params:
        payload["params"] = params
    
    response = requests.post(MCP_ENDPOINT, json=payload, timeout=30)
    return response.json()

# Test list_tables tool
print("🛠️ Testing list_tables tool")
response = send_mcp_request("tools/call", {
    "name": "list_tables",
    "arguments": {"output_format": "detailed"}
})

if "result" in response:
    print("✅ list_tables tool successful!")
    print("📊 Result:")
    print(json.dumps(response["result"], indent=2))
else:
    print(f"❌ Tool failed: {response.get('error')}")

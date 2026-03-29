"""Test MCP streamable-http endpoint - tools/list and a tool call."""
import httpx
import json

BASE = "https://tattva-api-ap34h5ieya-uc.a.run.app"
MCP_URL = f"{BASE}/mcp/"   # POST endpoint (streamable-http, path="/", mounted at /mcp)


def mcp_post(payload: dict) -> dict:
    with httpx.Client(timeout=15) as c:
        r = c.post(MCP_URL, json=payload, headers={"Accept": "application/json, text/event-stream"})
        print(f"  → HTTP {r.status_code}")
        return r.json()


# Initialize
print("=== initialize ===")
resp = mcp_post({
    "jsonrpc": "2.0", "id": 1, "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "1.0"}
    }
})
print(json.dumps(resp.get("result", {}).get("serverInfo", resp), indent=2))

# tools/list
print("\n=== tools/list ===")
resp = mcp_post({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
tools = resp.get("result", {}).get("tools", [])
print(f"Total tools: {len(tools)}")
for t in tools:
    print(f"  - {t['name']}: {t.get('description', '')[:80]}")

# Call lookup_location
print("\n=== tools/call: lookup_location(place='Morrisville') ===")
resp = mcp_post({
    "jsonrpc": "2.0", "id": 3, "method": "tools/call",
    "params": {"name": "lookup_location", "arguments": {"place": "Morrisville"}}
})
content = resp.get("result", {}).get("content", [{}])
print(content[0].get("text", json.dumps(resp)) if content else resp)

# Call get_panchang
print("\n=== tools/call: get_panchang ===")
resp = mcp_post({
    "jsonrpc": "2.0", "id": 4, "method": "tools/call",
    "params": {"name": "get_panchang", "arguments": {
        "birth_date": "1990-03-29", "birth_time": "12:00",
        "birth_place": "Chennai", "name": "Test"
    }}
})
content = resp.get("result", {}).get("content", [{}])
print(content[0].get("text", json.dumps(resp))[:400] if content else resp)

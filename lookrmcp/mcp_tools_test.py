#!/usr/bin/env python3
"""
Test MCP Tools for SQLite server using proper MCP protocol
"""

import json
import sys
import requests
import uuid
from typing import Dict, Any, List

SERVICE_URL = "https://sqlite-mcp-646005218605.us-central1.run.app"
MCP_ENDPOINT = f"{SERVICE_URL}/mcp"

class MCPToolsClient:
    """MCP client to test SQLite tools using proper MCP protocol"""
    
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.client_info = {
            "name": "mcp-tools-test",
            "version": "1.0.0"
        }
    
    def send_mcp_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send an MCP JSON-RPC 2.0 request"""
        request_id = str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method
        }
        
        if params:
            payload["params"] = params
        
        try:
            print(f"🔄 Sending MCP request: {method}")
            response = self.session.post(self.endpoint_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Response received")
                return result
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return {"error": str(e)}
    
    def initialize(self) -> bool:
        """Initialize MCP session"""
        print("🔧 Initializing MCP session...")
        
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {
                    "listChanged": True
                },
                "sampling": {}
            },
            "clientInfo": self.client_info
        }
        
        response = self.send_mcp_request("initialize", params)
        
        if "result" in response:
            print("✅ MCP session initialized successfully")
            print(f"   Server capabilities: {json.dumps(response.get('result', {}).get('capabilities', {}), indent=2)}")
            return True
        else:
            print(f"❌ Initialization failed: {response.get('error', 'Unknown error')}")
            return False
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available MCP tools"""
        print("\n🔍 Listing available MCP tools...")
        
        response = self.send_mcp_request("tools/list")
        
        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
            return tools
        else:
            print(f"❌ Failed to list tools: {response.get('error', 'Unknown error')}")
            return []
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific MCP tool"""
        print(f"\n🛠️ Calling tool: {tool_name}")
        print(f"   Arguments: {json.dumps(arguments, indent=2)}")
        
        params = {
            "name": tool_name,
            "arguments": arguments
        }
        
        response = self.send_mcp_request("tools/call", params)
        
        if "result" in response:
            print("✅ Tool call successful")
            return response["result"]
        else:
            print(f"❌ Tool call failed: {response.get('error', 'Unknown error')}")
            return {"error": response.get("error", "Unknown error")}
    
    def test_sqlite_queries(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Test SQLite functionality using available tools"""
        print("\n📊 Testing SQLite functionality...")
        
        results = []
        
        # Test queries to try
        test_cases = [
            {
                "name": "List Tables",
                "query": "SELECT name FROM sqlite_master WHERE type='table';"
            },
            {
                "name": "Show Users",
                "query": "SELECT * FROM users LIMIT 3;"
            },
            {
                "name": "Count Users", 
                "query": "SELECT COUNT(*) as total FROM users;"
            }
        ]
        
        # Look for query/execute tools
        query_tools = [tool for tool in tools if any(keyword in tool.get('name', '').lower() 
                      for keyword in ['query', 'execute', 'sql', 'select'])]
        
        if not query_tools:
            print("❌ No SQLite query tools found")
            return results
        
        for tool in query_tools[:2]:  # Test first 2 query tools
            tool_name = tool.get('name', '')
            print(f"\n🔧 Testing tool: {tool_name}")
            
            for test_case in test_cases:
                print(f"\n   📝 Test: {test_case['name']}")
                
                # Try different argument formats
                arg_formats = [
                    {"query": test_case["query"]},
                    {"sql": test_case["query"]},
                    {"statement": test_case["query"]},
                ]
                
                success = False
                for args in arg_formats:
                    result = self.call_tool(tool_name, args)
                    
                    if "error" not in result:
                        print(f"      ✅ SUCCESS with args: {args}")
                        print(f"      📊 Result: {json.dumps(result, indent=6)[:200]}...")
                        results.append({
                            "tool": tool_name,
                            "test": test_case["name"],
                            "query": test_case["query"],
                            "result": result,
                            "success": True
                        })
                        success = True
                        break
                    else:
                        print(f"      ❌ Failed with args: {args}")
                
                if not success:
                    results.append({
                        "tool": tool_name,
                        "test": test_case["name"], 
                        "query": test_case["query"],
                        "error": "All argument formats failed",
                        "success": False
                    })
        
        return results
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run complete MCP tools test"""
        print("🚀 Starting comprehensive MCP tools test")
        print("=" * 80)
        
        # Initialize
        if not self.initialize():
            return {"error": "Failed to initialize MCP session"}
        
        # List tools
        tools = self.list_tools()
        if not tools:
            return {"error": "No tools available"}
        
        # Test SQLite functionality
        query_results = self.test_sqlite_queries(tools)
        
        # Summary
        successful_queries = [r for r in query_results if r.get("success")]
        
        summary = {
            "tools_found": len(tools),
            "queries_attempted": len(query_results),
            "successful_queries": len(successful_queries),
            "tools": tools,
            "query_results": query_results,
            "success": len(successful_queries) > 0
        }
        
        print("\n" + "=" * 80)
        print("📊 MCP Tools Test Summary")
        print("=" * 80)
        print(f"🛠️  Tools found: {len(tools)}")
        print(f"🔄 Query tests run: {len(query_results)}")
        print(f"✅ Successful queries: {len(successful_queries)}")
        
        if successful_queries:
            print("\n🎉 SQLite MCP tools are working!")
            print("Working combinations:")
            for result in successful_queries:
                print(f"   - Tool: {result['tool']}")
                print(f"     Query: {result['query']}")
                print(f"     Success: ✅")
        else:
            print("\n⚠️  No successful SQLite queries")
            
        return summary

def main():
    """Main test function"""
    client = MCPToolsClient(MCP_ENDPOINT)
    result = client.run_comprehensive_test()
    
    return 0 if result.get("success") else 1

if __name__ == "__main__":
    sys.exit(main())

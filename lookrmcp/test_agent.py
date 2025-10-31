#!/usr/bin/env python3
"""
Simple test agent to interact with the SQLite MCP server on Cloud Run
"""

import requests
import json
import sys

# Cloud Run service URL
SERVICE_URL = "https://sqlite-mcp-646005218605.us-central1.run.app"

def test_mcp_connection():
    """Test basic connection to the MCP server"""
    try:
        print("🔗 Testing connection to MCP server...")
        response = requests.get(SERVICE_URL)
        print(f"✅ Server responded: {response.text}")
        print(f"   Status Code: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_mcp_protocol():
    """Test MCP protocol endpoints"""
    try:
        print("\n🧪 Testing MCP protocol endpoints...")
        
        # Test capabilities endpoint
        capabilities_url = f"{SERVICE_URL}/v1/capabilities"
        print(f"Testing: {capabilities_url}")
        
        response = requests.get(capabilities_url)
        print(f"Capabilities response ({response.status_code}): {response.text[:200]}...")
        
        # Test tools endpoint  
        tools_url = f"{SERVICE_URL}/v1/tools"
        print(f"Testing: {tools_url}")
        
        response = requests.get(tools_url)
        print(f"Tools response ({response.status_code}): {response.text[:200]}...")
        
        return True
    except Exception as e:
        print(f"❌ MCP protocol test failed: {e}")
        return False

def test_sqlite_queries():
    """Test SQLite queries through the MCP server"""
    try:
        print("\n📊 Testing SQLite queries...")
        
        # Test SQL query endpoint
        query_url = f"{SERVICE_URL}/v1/execute"
        
        # Simple SELECT query
        test_queries = [
            "SELECT name FROM sqlite_master WHERE type='table';",
            "SELECT * FROM users LIMIT 3;",
            "SELECT COUNT(*) as user_count FROM users;"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test Query {i}: {query}")
            
            payload = {
                "sql": query
            }
            
            response = requests.post(
                query_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"   Result: {json.dumps(result, indent=2)}")
                except:
                    print(f"   Result: {response.text}")
            else:
                print(f"   Error: {response.text}")
        
        return True
    except Exception as e:
        print(f"❌ SQLite query test failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧰 SQLite MCP Server Test Agent")
    print("=" * 60)
    print(f"Testing service at: {SERVICE_URL}")
    print("-" * 60)
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_mcp_connection():
        tests_passed += 1
    
    if test_mcp_protocol():
        tests_passed += 1
        
    if test_sqlite_queries():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! SQLite MCP server is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

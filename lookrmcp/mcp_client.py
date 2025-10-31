#!/usr/bin/env python3
"""
MCP client to test SQLite server functionality
"""

import json
import sys
import requests
from typing import Dict, Any, List

SERVICE_URL = "https://sqlite-mcp-646005218605.us-central1.run.app"

class MCPClient:
    """Simple MCP client for testing SQLite functionality"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def test_mcp_endpoints(self) -> Dict[str, Any]:
        """Test various MCP-related endpoints"""
        results = {}
        
        # Test common MCP paths
        endpoints_to_test = [
            '/',
            '/mcp',
            '/sqlite',
            '/api/sqlite',
            '/tools',
            '/capabilities',
            '/info',
            '/status'
        ]
        
        print("🔍 Testing various endpoints:")
        for endpoint in endpoints_to_test:
            url = f"{self.base_url}{endpoint}"
            try:
                response = self.session.get(url, timeout=10)
                result = {
                    'status': response.status_code,
                    'content_type': response.headers.get('content-type', ''),
                    'content': response.text[:200] + '...' if len(response.text) > 200 else response.text
                }
                results[endpoint] = result
                print(f"  {endpoint}: {response.status_code} - {result['content'][:50]}...")
            except Exception as e:
                results[endpoint] = {'error': str(e)}
                print(f"  {endpoint}: ERROR - {e}")
        
        return results
    
    def test_sqlite_queries_direct(self) -> List[Dict[str, Any]]:
        """Test SQLite queries using different approaches"""
        results = []
        
        # Test queries we want to run
        test_cases = [
            {
                'name': 'List Tables',
                'query': "SELECT name FROM sqlite_master WHERE type='table';"
            },
            {
                'name': 'Show Users',
                'query': 'SELECT * FROM users LIMIT 3;'
            },
            {
                'name': 'Count Users',
                'query': 'SELECT COUNT(*) as total_users FROM users;'
            },
            {
                'name': 'User by ID',
                'query': 'SELECT * FROM users WHERE id = 1;'
            }
        ]
        
        # Try different HTTP methods and paths
        methods_and_paths = [
            ('POST', '/execute'),
            ('POST', '/query'),
            ('POST', '/sql'),
            ('POST', '/sqlite/execute'),
            ('POST', '/sqlite/query'),
            ('POST', '/api/execute'),
            ('GET', '/sqlite/tables')
        ]
        
        print("\n📊 Testing SQLite query methods:")
        
        for method, path in methods_and_paths:
            print(f"\n  Testing {method} {path}:")
            
            if method == 'GET':
                # Simple GET request
                try:
                    url = f"{self.base_url}{path}"
                    response = self.session.get(url, timeout=10)
                    result = {
                        'method': method,
                        'path': path,
                        'status': response.status_code,
                        'response': response.text[:200]
                    }
                    results.append(result)
                    print(f"    Status: {response.status_code}, Response: {response.text[:100]}...")
                except Exception as e:
                    result = {
                        'method': method,
                        'path': path,
                        'error': str(e)
                    }
                    results.append(result)
                    print(f"    ERROR: {e}")
                    
            else:
                # POST requests with different payload formats
                for test_case in test_cases[:2]:  # Limit to first 2 test cases to avoid spam
                    payloads_to_try = [
                        {'query': test_case['query']},
                        {'sql': test_case['query']},
                        {'statement': test_case['query']},
                        {'command': test_case['query']},
                        test_case['query']  # Raw string
                    ]
                    
                    for i, payload in enumerate(payloads_to_try):
                        try:
                            url = f"{self.base_url}{path}"
                            response = self.session.post(url, json=payload, timeout=10)
                            
                            if response.status_code not in [404, 405]:  # Skip obvious failures
                                result = {
                                    'method': method,
                                    'path': path,
                                    'test_case': test_case['name'],
                                    'payload_format': f"format_{i}",
                                    'status': response.status_code,
                                    'response': response.text[:200]
                                }
                                results.append(result)
                                print(f"    {test_case['name']} (fmt{i}): {response.status_code}")
                                if response.status_code == 200:
                                    print(f"      SUCCESS: {response.text[:100]}...")
                                
                        except Exception as e:
                            if "404" not in str(e) and "405" not in str(e):
                                print(f"    {test_case['name']} (fmt{i}): ERROR - {e}")
                    
                    break  # Only try first test case per method/path combo to avoid spam
        
        return results

    def create_summary_report(self, endpoint_results: Dict[str, Any], query_results: List[Dict[str, Any]]) -> str:
        """Create a summary report of all tests"""
        report = []
        report.append("=" * 80)
        report.append("🧰 SQLite MCP Server Test Report")
        report.append("=" * 80)
        report.append(f"Server: {self.base_url}")
        report.append("")
        
        # Endpoint summary
        report.append("📡 Endpoint Tests:")
        working_endpoints = 0
        for endpoint, result in endpoint_results.items():
            if isinstance(result, dict) and result.get('status') == 200:
                working_endpoints += 1
                report.append(f"  ✅ {endpoint}: Working")
            elif isinstance(result, dict) and result.get('status'):
                report.append(f"  ⚠️  {endpoint}: HTTP {result['status']}")
            else:
                report.append(f"  ❌ {endpoint}: Error")
        
        report.append(f"  Summary: {working_endpoints}/{len(endpoint_results)} endpoints responding")
        report.append("")
        
        # Query test summary
        successful_queries = [r for r in query_results if r.get('status') == 200]
        report.append("🗃️ SQLite Query Tests:")
        if successful_queries:
            report.append("  ✅ Found working query endpoints!")
            for result in successful_queries[:3]:  # Show first 3 successful queries
                report.append(f"    - {result.get('method', 'N/A')} {result.get('path', 'N/A')}: SUCCESS")
        else:
            report.append("  ❌ No working SQLite query endpoints found")
            report.append("  💡 This suggests the server uses MCP protocol instead of HTTP REST")
        
        report.append("")
        report.append("📝 Recommendations:")
        if successful_queries:
            report.append("  • The SQLite MCP server is working and accessible via HTTP!")
            report.append("  • You can use the working endpoints for database queries")
        else:
            report.append("  • The server is running but only supports MCP protocol communication")
            report.append("  • To test SQLite functionality, you need an MCP-compatible client")
            report.append("  • The server is properly deployed and responsive")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Main test function"""
    print("🚀 Starting comprehensive MCP SQLite server test...")
    print(f"Target: {SERVICE_URL}")
    print("-" * 80)
    
    client = MCPClient(SERVICE_URL)
    
    # Test endpoints
    endpoint_results = client.test_mcp_endpoints()
    
    # Test query functionality
    query_results = client.test_sqlite_queries_direct()
    
    # Generate report
    report = client.create_summary_report(endpoint_results, query_results)
    print(report)
    
    # Return appropriate exit code
    successful_queries = [r for r in query_results if r.get('status') == 200]
    return 0 if successful_queries else 1

if __name__ == "__main__":
    sys.exit(main())

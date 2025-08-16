"""
Test Client untuk API Proxy KLHK
Script untuk testing semua endpoint API yang telah dibuat
"""

import requests
import json
import time
import urllib.parse

class APITester:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_endpoint(self, endpoint, method='GET', params=None, data=None):
        """
        Test a specific endpoint
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            print(f"\n{'='*50}")
            print(f"Testing: {method} {endpoint}")
            if params:
                print(f"Params: {params}")
            print(f"{'='*50}")
            
            if method == 'GET':
                response = self.session.get(url, params=params)
            elif method == 'POST':
                response = self.session.post(url, json=data, params=params)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
            
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    print("✓ Response is valid JSON")
                    
                    if 'status' in json_response:
                        print(f"API Status: {json_response['status']}")
                    
                    if 'data' in json_response and isinstance(json_response['data'], list):
                        print(f"Data Count: {len(json_response['data'])} records")
                        
                        # Show sample record if available
                        if len(json_response['data']) > 0:
                            print("\\nSample Record:")
                            sample = json_response['data'][0]
                            for key, value in sample.items():
                                if len(str(value)) > 50:
                                    print(f"  {key}: {str(value)[:47]}...")
                                else:
                                    print(f"  {key}: {value}")
                    
                    if 'pagination' in json_response:
                        pagination = json_response['pagination']
                        print(f"\\nPagination:")
                        print(f"  Page: {pagination.get('page', 'N/A')}")
                        print(f"  Limit: {pagination.get('limit', 'N/A')}")
                        print(f"  Total: {pagination.get('total_records', 'N/A')}")
                    
                    if 'statistics' in json_response:
                        stats = json_response['statistics']
                        print(f"\\nStatistics:")
                        for key, value in stats.items():
                            if isinstance(value, dict):
                                print(f"  {key}: {len(value)} categories")
                            else:
                                print(f"  {key}: {value}")
                    
                    return json_response
                    
                except json.JSONDecodeError:
                    print("✗ Response is not valid JSON")
                    print(f"Response: {response.text[:200]}...")
                    return None
            else:
                print(f"✗ Error: HTTP {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Connection Error: {e}")
            return None
    
    def run_all_tests(self):
        """
        Run tests for all endpoints
        """
        print("🚀 Starting API Tests")
        print("=" * 60)
        
        tests = [
            # Basic endpoints
            {
                'name': 'API Documentation',
                'endpoint': '/',
                'method': 'GET'
            },
            {
                'name': 'Health Check',
                'endpoint': '/health',
                'method': 'GET'
            },
            
            # Data endpoints
            {
                'name': 'Get All Permits',
                'endpoint': '/permits',
                'method': 'GET'
            },
            {
                'name': 'Get Permits with Pagination',
                'endpoint': '/permits',
                'method': 'GET',
                'params': {'page': 1, 'limit': 2}
            },
            
            # Search endpoints
            {
                'name': 'Search by Company Name',
                'endpoint': '/permits/search',
                'method': 'GET',
                'params': {'nama': 'PT'}
            },
            {
                'name': 'Search by Permit Type',
                'endpoint': '/permits/search',
                'method': 'GET',
                'params': {'jenis': 'Izin Lingkungan'}
            },
            {
                'name': 'Search by Status',
                'endpoint': '/permits/search',
                'method': 'GET',
                'params': {'status': 'Aktif'}
            },
            
            # Filter endpoints
            {
                'name': 'Get Active Permits',
                'endpoint': '/permits/active',
                'method': 'GET'
            },
            
            # Specific company
            {
                'name': 'Get Permits by Company',
                'endpoint': '/permits/company/PT Semen Indonesia',
                'method': 'GET'
            },
            
            # Specific permit type
            {
                'name': 'Get Permits by Type',
                'endpoint': '/permits/type/Izin Lingkungan',
                'method': 'GET'
            },
            
            # Statistics
            {
                'name': 'Get Statistics',
                'endpoint': '/permits/stats',
                'method': 'GET'
            }
        ]
        
        results = []
        
        for test in tests:
            print(f"\\n🔍 Test: {test['name']}")
            
            result = self.test_endpoint(
                endpoint=test['endpoint'],
                method=test.get('method', 'GET'),
                params=test.get('params'),
                data=test.get('data')
            )
            
            results.append({
                'name': test['name'],
                'endpoint': test['endpoint'],
                'success': result is not None,
                'result': result
            })
            
            # Add small delay between tests
            time.sleep(0.5)
        
        # Summary
        print("\\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        print(f"Total Tests: {total_count}")
        print(f"Successful: {success_count}")
        print(f"Failed: {total_count - success_count}")
        print(f"Success Rate: {(success_count/total_count)*100:.1f}%")
        
        print("\\nTest Results:")
        for result in results:
            status = "✓" if result['success'] else "✗"
            print(f"  {status} {result['name']}")
        
        return results
    
    def test_error_handling(self):
        """
        Test error handling for invalid endpoints and parameters
        """
        print("\\n🔧 Testing Error Handling")
        print("=" * 50)
        
        error_tests = [
            {
                'name': 'Invalid Endpoint',
                'endpoint': '/invalid_endpoint',
                'expected_status': 404
            },
            {
                'name': 'Search without Parameters',
                'endpoint': '/permits/search',
                'expected_status': 400
            },
            {
                'name': 'Company Not Found',
                'endpoint': '/permits/company/NonExistentCompany',
                'expected_status': 200  # Should return empty results
            }
        ]
        
        for test in error_tests:
            print(f"\\nTesting: {test['name']}")
            url = f"{self.base_url}{test['endpoint']}"
            
            try:
                response = self.session.get(url)
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == test['expected_status']:
                    print(f"✓ Expected status code {test['expected_status']}")
                else:
                    print(f"✗ Expected {test['expected_status']}, got {response.status_code}")
                
                try:
                    json_response = response.json()
                    if 'message' in json_response:
                        print(f"Error Message: {json_response['message']}")
                except json.JSONDecodeError:
                    pass
                    
            except Exception as e:
                print(f"✗ Error: {e}")
    
    def demonstrate_usage(self):
        """
        Demonstrate typical API usage scenarios
        """
        print("\\n💡 API Usage Demonstration")
        print("=" * 50)
        
        # Scenario 1: Check if a specific company has permits
        print("\\n📋 Scenario 1: Check Company Permits")
        company_name = "PT Semen Indonesia"
        encoded_name = urllib.parse.quote(company_name)
        response = self.test_endpoint(f'/permits/company/{encoded_name}')
        
        # Scenario 2: Find all environmental permits
        print("\\n🌱 Scenario 2: Find Environmental Permits")
        response = self.test_endpoint('/permits/search', params={'jenis': 'Lingkungan'})
        
        # Scenario 3: Get system statistics
        print("\\n📊 Scenario 3: Get System Statistics")
        response = self.test_endpoint('/permits/stats')

def main():
    print("🧪 API Testing Suite for KLHK Permit API Proxy")
    print("=" * 60)
    print("Make sure the API server is running on http://localhost:5000")
    print("Run: python api_server.py")
    print("=" * 60)
    
    # Wait for user confirmation
    input("Press Enter to start testing...")
    
    # Initialize tester
    tester = APITester()
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        if response.status_code == 200:
            print("✓ API Server is running")
        else:
            print("✗ API Server is not responding properly")
            return
    except requests.exceptions.RequestException:
        print("✗ Cannot connect to API server. Make sure it's running on port 5000")
        return
    
    # Run tests
    tester.run_all_tests()
    tester.test_error_handling()
    tester.demonstrate_usage()
    
    print("\\n🎉 Testing Complete!")

if __name__ == "__main__":
    main()

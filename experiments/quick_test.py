"""
Quick test script untuk API tanpa perlu terminal interaktif
"""

import requests
import json

def test_api_endpoints():
    base_url = "http://localhost:5000"
    
    endpoints = [
        "/",
        "/health", 
        "/permits",
        "/permits/search?nama=PT",
        "/permits/company/PT%20Semen%20Indonesia",
        "/permits/stats"
    ]
    
    print("🧪 Quick API Test")
    print("="*50)
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n🔍 Testing: {endpoint}")
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success - Status: {response.status_code}")
                
                if 'data' in data and isinstance(data['data'], list):
                    print(f"   Records: {len(data['data'])}")
                elif 'statistics' in data:
                    stats = data['statistics']
                    print(f"   Total permits: {stats.get('total_permits', 'N/A')}")
                elif 'status' in data:
                    print(f"   API Status: {data['status']}")
                    
            else:
                print(f"❌ Failed - Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
    
    print("\n" + "="*50)
    print("Test complete!")

if __name__ == "__main__":
    test_api_endpoints()

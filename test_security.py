#!/usr/bin/env python
"""
Test script for API security features.
Tests API key authentication, rate limiting, and admin endpoints.
"""
import requests
import time
import json
from typing import Dict, Any

API_BASE = "http://localhost:5000"
BASIC_KEY = "demo_key_basic_2025"  
PREMIUM_KEY = "demo_key_premium_2025"

def test_public_endpoints():
    """Test endpoints that don't require API keys."""
    print("🌐 Testing Public Endpoints...")
    
    # Health check
    response = requests.get(f"{API_BASE}/health")
    print(f"Health check: {response.status_code} - {response.json()}")
    
    # Home page  
    response = requests.get(f"{API_BASE}/")
    print(f"Home page: {response.status_code} - API name: {response.json().get('name', 'N/A')}")

def test_protected_endpoints_without_key():
    """Test that protected endpoints require API keys."""
    print("\n🔒 Testing Protected Endpoints (No API Key)...")
    
    response = requests.get(f"{API_BASE}/global/emissions")
    print(f"Global emissions without key: {response.status_code}")
    if response.status_code == 401:
        error_data = response.json()
        print(f"Error message: {error_data.get('message', 'N/A')}")
        print(f"Demo keys provided: {error_data.get('demo_keys', {})}")

def test_basic_api_key():
    """Test basic API key functionality."""
    print(f"\n🔑 Testing Basic API Key: {BASIC_KEY}...")
    
    headers = {"Authorization": f"Bearer {BASIC_KEY}"}
    
    # Test global emissions
    response = requests.get(f"{API_BASE}/global/emissions?limit=5", headers=headers)
    print(f"Global emissions with basic key: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Retrieved {len(data.get('data', []))} records")

def test_premium_api_key():
    """Test premium API key functionality.""" 
    print(f"\n💎 Testing Premium API Key: {PREMIUM_KEY}...")
    
    headers = {"X-API-Key": PREMIUM_KEY}
    
    # Test ISO certifications
    response = requests.get(f"{API_BASE}/global/iso?limit=10", headers=headers)
    print(f"ISO certifications with premium key: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Retrieved {len(data.get('data', []))} ISO records")

def test_admin_endpoints():
    """Test admin endpoints (premium key required)."""
    print(f"\n👨‍💼 Testing Admin Endpoints...")
    
    headers = {"Authorization": f"Bearer {PREMIUM_KEY}"}
    
    # List API keys
    response = requests.get(f"{API_BASE}/admin/api-keys", headers=headers)
    print(f"Admin - List API keys: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        key_count = data.get('data', {}).get('total_count', 0)
        print(f"Total API keys: {key_count}")
    
    # Get API stats
    response = requests.get(f"{API_BASE}/admin/stats", headers=headers)
    print(f"Admin - API stats: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        stats = data.get('data', {})
        print(f"System info: {stats.get('system_info', {})}")

def test_different_auth_methods():
    """Test different authentication methods."""
    print(f"\n🔐 Testing Different Auth Methods...")
    
    # Authorization header
    headers1 = {"Authorization": f"Bearer {BASIC_KEY}"}
    response1 = requests.get(f"{API_BASE}/global/emissions?limit=1", headers=headers1)
    print(f"Authorization header: {response1.status_code}")
    
    # X-API-Key header
    headers2 = {"X-API-Key": BASIC_KEY}
    response2 = requests.get(f"{API_BASE}/global/emissions?limit=1", headers=headers2)
    print(f"X-API-Key header: {response2.status_code}")
    
    # Query parameter
    response3 = requests.get(f"{API_BASE}/global/emissions?api_key={BASIC_KEY}&limit=1")
    print(f"Query parameter: {response3.status_code}")

def test_rate_limiting():
    """Test rate limiting functionality."""
    print(f"\n⏱️ Testing Rate Limiting (Basic: 30/min)...")
    
    headers = {"Authorization": f"Bearer {BASIC_KEY}"}
    
    success_count = 0
    rate_limited = False
    
    for i in range(5):  # Test a few requests quickly
        response = requests.get(f"{API_BASE}/global/emissions?limit=1", headers=headers)
        if response.status_code == 200:
            success_count += 1
        elif response.status_code == 429:
            rate_limited = True
            print(f"Rate limited after {success_count} requests")
            break
        time.sleep(0.1)  # Small delay
    
    print(f"Successful requests before rate limit: {success_count}")
    if not rate_limited and success_count > 0:
        print("Rate limiting working (or limit not reached in test)")

if __name__ == "__main__":
    print("🚀 Permit API Security Test Suite")
    print("=" * 50)
    
    try:
        test_public_endpoints()
        test_protected_endpoints_without_key()
        test_basic_api_key()
        test_premium_api_key()
        test_admin_endpoints()
        test_different_auth_methods()
        test_rate_limiting()
        
        print("\n✅ Security test suite completed!")
        print("\nNext steps:")
        print("1. Start server: python run_server.py")
        print("2. Run tests: python test_security.py")
        print("3. Check API docs: http://localhost:5000/")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server.")
        print("Please start the server first: python run_server.py")
    except Exception as e:
        print(f"❌ Test error: {e}")

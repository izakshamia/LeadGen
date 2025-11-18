#!/usr/bin/env python3
"""
Simple test script to verify API endpoints work correctly.
"""
import sys
import time
import requests

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("Testing GET /health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.json()}")
        return response.status_code in [200, 503]
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_suggestions():
    """Test the suggestions endpoint"""
    print("\nTesting GET /suggestions...")
    try:
        response = requests.get(f"{BASE_URL}/suggestions?hours=24", timeout=5)
        print(f"  Status Code: {response.status_code}")
        data = response.json()
        print(f"  Count: {data.get('count', 0)}")
        print(f"  Time Window: {data.get('time_window_hours', 0)} hours")
        return response.status_code == 200
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Reddit Ovarra API Test Suite")
    print("=" * 60)
    
    # Wait a moment for server to be ready
    print("\nWaiting for server to start...")
    time.sleep(2)
    
    results = []
    
    # Test health endpoint
    results.append(("Health Check", test_health()))
    
    # Test suggestions endpoint
    results.append(("Get Suggestions", test_suggestions()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())

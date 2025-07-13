#!/usr/bin/env python3
"""
Simple API test script
"""

import requests
import time

def test_api():
    """Test API endpoints"""
    base_url = "http://localhost:8000"
    
    print("Testing API endpoints...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Root endpoint error: {e}")
    
    # Test API v1 root
    try:
        response = requests.get(f"{base_url}/api/v1/")
        print(f"API v1 root: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"API v1 root error: {e}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health endpoint error: {e}")
    
    # Test auth endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/auth")
        print(f"Auth endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Auth endpoint error: {e}")

if __name__ == "__main__":
    test_api() 
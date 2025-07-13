#!/usr/bin/env python3
"""
Test frontend accessibility
"""

import requests
import time

def test_frontend():
    """Test frontend accessibility"""
    print("🌐 Testing Frontend Accessibility...")
    
    # Test different URLs
    urls = [
        "http://localhost:3000/",
        "http://localhost:3000/index.html",
        "http://localhost:3000/dashboard.html",
        "http://localhost:3000/results.html"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url}: {response.status_code}")
            if response.status_code == 200:
                print(f"   📄 Content length: {len(response.text)} characters")
                if "Aztec Protocol" in response.text:
                    print("   🎯 Found 'Aztec Protocol' in content")
        except Exception as e:
            print(f"❌ {url}: {e}")

if __name__ == "__main__":
    test_frontend() 
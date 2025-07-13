#!/usr/bin/env python3
"""
Test the landing page functionality
"""

import requests
import time

def test_landing_page():
    """Test the landing page"""
    print("🌐 Testing Landing Page...")
    
    try:
        response = requests.get("http://localhost:3000/index.html", timeout=5)
        if response.status_code == 200:
            print("✅ Landing page accessible")
            
            # Check if it contains registration and login forms
            content = response.text
            if "Create Account" in content and "Sign In" in content:
                print("✅ Registration and login forms present")
            else:
                print("❌ Registration/login forms missing")
                
            if "Aztec Protocol" in content:
                print("✅ Aztec Protocol branding present")
            else:
                print("❌ Branding missing")
                
        else:
            print(f"❌ Landing page returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Landing page not accessible: {e}")

if __name__ == "__main__":
    test_landing_page() 
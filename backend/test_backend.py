#!/usr/bin/env python3
"""
Comprehensive test script for Aztec Protocol Backend
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test data
TEST_USER = {
    "email": "test@aztec.com",
    "password": "testpassword123",
    "full_name": "Test User",
    "wallet_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
}

TEST_AGENT = {
    "name": "test-agent-1",
    "description": "Test agent for Aztec Protocol",
    "agent_type": "training",
    "wallet_address": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
    "model": "distilbert-base-uncased",
    "method": "lora",
    "batch_size": 8,
    "reward_threshold": 10.0,
    "data_path": "./data/mock_data.csv"
}

TEST_MODEL = {
    "name": "test-model-1",
    "description": "Test model for Aztec Protocol",
    "model_type": "transformer",
    "architecture": "distilbert-base-uncased",
    "parameters": 66000000,
    "accuracy": 0.85,
    "loss": 0.15
}

TEST_PROOF = {
    "proof_type": "zk_proofs",
    "description": "Test ZK proof",
    "status": "pending"
}

TEST_TRAINING_DATA = {
    "dataset_hash": 123456789,
    "model_params_before": [0.1, 0.2, 0.3, 0.4],
    "model_params_after": [0.15, 0.25, 0.35, 0.45],
    "batch_size": 32,
    "num_epochs": 1,
    "final_loss": 0.5,
    "seed": 42,
    "num_samples": 1000,
    "dataset_size": 100000,
    "feature_dim": 768,
    "num_classes": 2
}

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.test_results = []
    
    def log_test(self, test_name: str, success: bool, response: requests.Response = None, error: str = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "status_code": response.status_code if response else None,
            "error": error
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if error:
            print(f"   Error: {error}")
    
    def get_headers(self):
        """Get headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.session.get(f"{BASE_URL}/health")
            success = response.status_code == 200
            self.log_test("Health Check", success, response)
        except Exception as e:
            self.log_test("Health Check", False, error=str(e))
    
    def test_register_user(self):
        """Test user registration"""
        try:
            response = self.session.post(
                f"{API_BASE}/auth/register",
                json=TEST_USER,
                headers=self.get_headers()
            )
            success = response.status_code == 201
            self.log_test("User Registration", success, response)
        except Exception as e:
            self.log_test("User Registration", False, error=str(e))
    
    def test_login(self):
        """Test user login"""
        try:
            login_data = {
                "username": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            response = self.session.post(
                f"{API_BASE}/auth/token",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            success = response.status_code == 200
            if success:
                data = response.json()
                self.access_token = data.get("access_token")
            self.log_test("User Login", success, response)
        except Exception as e:
            self.log_test("User Login", False, error=str(e))
    
    def test_get_current_user(self):
        """Test get current user"""
        try:
            response = self.session.get(
                f"{API_BASE}/auth/me",
                headers=self.get_headers()
            )
            success = response.status_code == 200
            self.log_test("Get Current User", success, response)
        except Exception as e:
            self.log_test("Get Current User", False, error=str(e))
    
    def test_create_agent(self):
        """Test agent creation"""
        try:
            response = self.session.post(
                f"{API_BASE}/agents",
                json=TEST_AGENT,
                headers=self.get_headers()
            )
            success = response.status_code == 201
            self.log_test("Create Agent", success, response)
        except Exception as e:
            self.log_test("Create Agent", False, error=str(e))
    
    def test_list_agents(self):
        """Test list agents"""
        try:
            response = self.session.get(
                f"{API_BASE}/agents",
                headers=self.get_headers()
            )
            success = response.status_code == 200
            self.log_test("List Agents", success, response)
        except Exception as e:
            self.log_test("List Agents", False, error=str(e))
    
    def test_create_model(self):
        """Test model creation"""
        try:
            response = self.session.post(
                f"{API_BASE}/models",
                json=TEST_MODEL,
                headers=self.get_headers()
            )
            success = response.status_code == 201
            self.log_test("Create Model", success, response)
        except Exception as e:
            self.log_test("Create Model", False, error=str(e))
    
    def test_list_models(self):
        """Test list models"""
        try:
            response = self.session.get(
                f"{API_BASE}/models",
                headers=self.get_headers()
            )
            success = response.status_code == 200
            self.log_test("List Models", success, response)
        except Exception as e:
            self.log_test("List Models", False, error=str(e))
    
    def test_generate_proof(self):
        """Test proof generation"""
        try:
            response = self.session.post(
                f"{API_BASE}/proofs/generate",
                json=TEST_TRAINING_DATA,
                headers=self.get_headers()
            )
            success = response.status_code == 200
            self.log_test("Generate Proof", success, response)
        except Exception as e:
            self.log_test("Generate Proof", False, error=str(e))
    
    def test_list_proofs(self):
        """Test list proofs"""
        try:
            response = self.session.get(
                f"{API_BASE}/proofs",
                headers=self.get_headers()
            )
            success = response.status_code == 200
            self.log_test("List Proofs", success, response)
        except Exception as e:
            self.log_test("List Proofs", False, error=str(e))
    
    def test_ipfs_status(self):
        """Test IPFS status"""
        try:
            response = self.session.get(
                f"{API_BASE}/ipfs/status",
                headers=self.get_headers()
            )
            success = response.status_code == 200
            self.log_test("IPFS Status", success, response)
        except Exception as e:
            self.log_test("IPFS Status", False, error=str(e))
    
    def test_blockchain_status(self):
        """Test blockchain status"""
        try:
            response = self.session.get(
                f"{API_BASE}/blockchain/status",
                headers=self.get_headers()
            )
            success = response.status_code == 200
            self.log_test("Blockchain Status", success, response)
        except Exception as e:
            self.log_test("Blockchain Status", False, error=str(e))
    
    def test_get_contracts(self):
        """Test get contract addresses"""
        try:
            response = self.session.get(
                f"{API_BASE}/blockchain/contracts",
                headers=self.get_headers()
            )
            success = response.status_code == 200
            self.log_test("Get Contracts", success, response)
        except Exception as e:
            self.log_test("Get Contracts", False, error=str(e))
    
    def test_upload_to_ipfs(self):
        """Test IPFS upload"""
        try:
            # Create a test file
            test_file_content = "This is a test file for IPFS upload"
            with open("test_file.txt", "w") as f:
                f.write(test_file_content)
            
            with open("test_file.txt", "rb") as f:
                files = {"file": ("test_file.txt", f, "text/plain")}
                data = {"metadata": json.dumps({"description": "Test file"})}
                
                response = self.session.post(
                    f"{API_BASE}/ipfs/upload",
                    files=files,
                    data=data,
                    headers={"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
                )
            
            success = response.status_code == 200
            self.log_test("IPFS Upload", success, response)
            
            # Clean up test file
            import os
            if os.path.exists("test_file.txt"):
                os.remove("test_file.txt")
                
        except Exception as e:
            self.log_test("IPFS Upload", False, error=str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Aztec Protocol Backend Tests")
        print("=" * 50)
        
        # Health check first
        self.test_health_check()
        
        # Authentication tests
        self.test_register_user()
        self.test_login()
        self.test_get_current_user()
        
        # Agent tests
        self.test_create_agent()
        self.test_list_agents()
        
        # Model tests
        self.test_create_model()
        self.test_list_models()
        
        # Proof tests
        self.test_generate_proof()
        self.test_list_proofs()
        
        # IPFS tests
        self.test_ipfs_status()
        self.test_upload_to_ipfs()
        
        # Blockchain tests
        self.test_blockchain_status()
        self.test_get_contracts()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['error']}")
        
        return passed == total

def main():
    """Main test function"""
    tester = BackendTester()
    
    try:
        success = tester.run_all_tests()
        if success:
            print("\n🎉 All tests passed! Backend is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Please check the backend configuration.")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 
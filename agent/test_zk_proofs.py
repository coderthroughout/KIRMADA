#!/usr/bin/env python3
"""
Test script for Aztec Protocol ZK Proof System
Tests the complete ZK proof generation and verification pipeline
"""

import json
import os
import sys
import logging
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_circuit_compilation():
    """Test that all Noir circuits compile successfully"""
    logger.info("=== Testing Circuit Compilation ===")
    
    # First check if Noir is available
    try:
        result = subprocess.run(
            ["nargo", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            logger.warning("⚠️  Noir (nargo) not available - skipping circuit compilation")
            logger.info("💡 Run 'python install_noir.py' for installation instructions")
            return {"noir_available": False, "message": "Noir not installed"}
    except FileNotFoundError:
        logger.warning("⚠️  Noir (nargo) not found in PATH - skipping circuit compilation")
        logger.info("💡 Run 'python install_noir.py' for installation instructions")
        return {"noir_available": False, "message": "Noir not in PATH"}
    except Exception as e:
        logger.warning(f"⚠️  Error checking Noir: {e} - skipping circuit compilation")
        return {"noir_available": False, "message": f"Error: {e}"}
    
    circuits_dir = Path("../circuits")
    circuits = [
        "training_proof",
        "data_integrity", 
        "model_diff"
    ]
    
    results = {"noir_available": True}
    for circuit in circuits:
        circuit_path = circuits_dir / circuit
        if not circuit_path.exists():
            logger.error(f"Circuit directory not found: {circuit_path}")
            results[circuit] = False
            continue
        
        try:
            # Run nargo compile
            result = subprocess.run(
                ["nargo", "compile"],
                cwd=circuit_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"✓ {circuit} compiled successfully")
                results[circuit] = True
            else:
                logger.error(f"✗ {circuit} compilation failed: {result.stderr}")
                results[circuit] = False
                
        except subprocess.TimeoutExpired:
            logger.error(f"✗ {circuit} compilation timed out")
            results[circuit] = False
        except Exception as e:
            logger.error(f"✗ {circuit} compilation error: {e}")
            results[circuit] = False
    
    return results

def test_zk_proof_system():
    """Test the ZK proof system functionality"""
    logger.info("=== Testing ZK Proof System ===")
    
    try:
        from zk_proofs import ZKProofSystem
        
        # Initialize ZK proof system
        zk_system = ZKProofSystem()
        logger.info("✓ ZK proof system initialized")
        
        # Test data
        test_training_data = {
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
        
        # Test circuit compilation
        compilation_results = zk_system.compile_all_circuits()
        logger.info(f"Circuit compilation results: {compilation_results}")
        
        # Test proof generation
        proofs = zk_system.generate_all_proofs(test_training_data)
        logger.info("✓ All proofs generated successfully")
        
        # Test proof verification
        verification_results = zk_system.verify_all_proofs(proofs)
        logger.info(f"Proof verification results: {verification_results}")
        
        return {
            "compilation_results": compilation_results,
            "proofs_generated": len(proofs),
            "verification_results": verification_results,
            "success": True
        }
        
    except ImportError as e:
        logger.error(f"✗ ZK proof system import failed: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"✗ ZK proof system test failed: {e}")
        return {"success": False, "error": str(e)}

def test_proof_integration():
    """Test the proof integration with the agent workflow"""
    logger.info("=== Testing Proof Integration ===")
    
    try:
        # Test the updated prove.py
        if os.path.exists("prove.py"):
            # Create a mock model diff file for testing
            try:
                import torch
                mock_model_diff = {"test_param": torch.tensor([0.1, 0.2, 0.3, 0.4])}
                torch.save(mock_model_diff, "model_diff.pt")
            except ImportError:
                logger.warning("⚠️  PyTorch not available - creating mock file")
                # Create a simple mock file without PyTorch
                mock_data = {"test_param": [0.1, 0.2, 0.3, 0.4]}
                with open("model_diff.pt", "w") as f:
                    json.dump(mock_data, f)
            
            # Create mock training stats
            mock_stats = {
                "dataset_hash": 123456789,
                "model_params_before": [0.1, 0.2, 0.3, 0.4],
                "model_params_after": [0.15, 0.25, 0.35, 0.45],
                "batch_size": 32,
                "num_epochs": 1,
                "final_loss": 0.5,
                "seed": 42,
                "num_samples": 1000,
                "dataset_size_bytes": 100000,
                "feature_dim": 768,
                "num_classes": 2
            }
            
            with open("training_stats.json", "w") as f:
                json.dump(mock_stats, f)
            
            # Create mock memory file
            mock_memory = {
                "agent_name": "test_agent",
                "wallet_address": "0x1234567890123456789012345678901234567890",
                "rounds_joined": [],
                "training_stats": [mock_stats],
                "proofs": []
            }
            
            with open("agent-memory.json", "w") as f:
                json.dump(mock_memory, f)
            
            # Run prove.py
            result = subprocess.run(
                [sys.executable, "prove.py"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info("✓ Proof generation completed successfully")
                
                # Check if proof file was created
                if os.path.exists("proof.json"):
                    with open("proof.json", "r") as f:
                        proof_data = json.load(f)
                    logger.info(f"✓ Proof file created: {proof_data.get('proof_type', 'unknown')}")
                    return {"success": True, "proof_type": proof_data.get('proof_type')}
                else:
                    logger.error("✗ Proof file not created")
                    return {"success": False, "error": "Proof file not created"}
            else:
                logger.error(f"✗ Proof generation failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
        else:
            logger.error("✗ prove.py not found")
            return {"success": False, "error": "prove.py not found"}
            
    except Exception as e:
        logger.error(f"✗ Proof integration test failed: {e}")
        return {"success": False, "error": str(e)}

def test_smart_contract_integration():
    """Test smart contract integration"""
    logger.info("=== Testing Smart Contract Integration ===")
    
    try:
        # Test ProofVerifier contract validation
        contracts_dir = Path("../contracts/contracts")
        proof_verifier_path = contracts_dir / "ProofVerifier.sol"
        
        if not proof_verifier_path.exists():
            logger.error(f"✗ ProofVerifier contract not found: {proof_verifier_path}")
            return {"success": False, "error": "Contract not found"}
        
        # Read and validate contract
        with open(proof_verifier_path, "r") as f:
            contract_content = f.read()
        
        # Basic validation checks
        required_functions = [
            "verifyTrainingProof",
            "verifyDataIntegrityProof", 
            "verifyModelDiffProof"
        ]
        
        for func in required_functions:
            if func not in contract_content:
                logger.error(f"✗ Required function {func} not found in contract")
                return {"success": False, "error": f"Missing function: {func}"}
        
        logger.info("✓ ProofVerifier contract validation passed")
        return {"success": True}
        
    except Exception as e:
        logger.error(f"✗ Smart contract integration test failed: {e}")
        return {"success": False, "error": str(e)}

def run_comprehensive_test():
    """Run comprehensive test suite"""
    logger.info("=== Aztec Protocol ZK Proof System Test Suite ===")
    
    # Test results
    results = {}
    
    # Test 1: Circuit compilation
    logger.info("=== Testing Circuit Compilation ===")
    compilation_result = test_circuit_compilation()
    results["circuit_compilation"] = compilation_result
    
    # Test 2: ZK proof system
    logger.info("=== Testing ZK Proof System ===")
    zk_result = test_zk_proof_system()
    results["zk_proof_system"] = zk_result
    
    # Test 3: Proof integration
    logger.info("=== Testing Proof Integration ===")
    integration_result = test_proof_integration()
    results["proof_integration"] = integration_result
    
    # Test 4: Smart contract integration
    logger.info("=== Testing Smart Contract Integration ===")
    contract_result = test_smart_contract_integration()
    results["smart_contract_integration"] = contract_result
    
    # Generate test report
    test_report = {
        "test_results": results,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_tests": len(results),
            "passed": sum(1 for r in results.values() if r.get("success", False)),
            "failed": sum(1 for r in results.values() if not r.get("success", False))
        }
    }
    
    # Save test results
    with open("test_results.json", "w") as f:
        json.dump(test_report, f, indent=2)
    
    # Print summary
    logger.info("=== Test Results Summary ===")
    for test_name, result in results.items():
        if result.get("success", False):
            logger.info(f"✓ {test_name}: PASSED")
        else:
            logger.error(f"✗ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
    
    passed = test_report["summary"]["passed"]
    total = test_report["summary"]["total_tests"]
    
    logger.info(f"\nOverall Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("✅ All tests passed! ZK proof system is ready.")
        return True
    else:
        logger.error(f"❌ {total - passed} tests failed. Please fix issues before proceeding.")
        return False

def cleanup_test_files():
    """Clean up test files"""
    test_files = [
        "model_diff.pt",
        "training_stats.json", 
        "agent-memory.json",
        "proof.json",
        "test_results.json"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            logger.info(f"Cleaned up: {file}")

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        cleanup_test_files()
        
        if not success:
            print("\n❌ ZK Proof System Test Suite Failed!")
            sys.exit(1)
        else:
            print("\n✅ ZK Proof System Test Suite Passed!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        cleanup_test_files()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test suite failed with error: {e}")
        cleanup_test_files()
        sys.exit(1) 
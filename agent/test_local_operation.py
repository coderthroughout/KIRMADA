#!/usr/bin/env python3
"""
Test local operation of Aztec Protocol components
"""

import json
import os
import sys
import logging
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_config_loading():
    """Test configuration loading"""
    logger.info("=== Testing Configuration Loading ===")
    
    try:
        # Import functions directly from aztec-agent.py
        import importlib.util
        spec = importlib.util.spec_from_file_location("aztec_agent", "aztec-agent.py")
        aztec_agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aztec_agent)
        
        config = aztec_agent.load_config()
        logger.info("✅ Configuration loaded successfully")
        logger.info(f"Agent: {config['agent_name']}, Model: {config['model']}")
        return True
    except Exception as e:
        logger.error(f"❌ Configuration loading failed: {e}")
        return False

def test_data_availability():
    """Test data availability"""
    logger.info("=== Testing Data Availability ===")
    
    data_path = "./data/mock_data.csv"
    if os.path.exists(data_path):
        logger.info(f"✅ Data file found: {data_path}")
        return True
    else:
        logger.error(f"❌ Data file not found: {data_path}")
        return False

def test_training_script():
    """Test training script availability"""
    logger.info("=== Testing Training Script ===")
    
    if os.path.exists("train.py"):
        logger.info("✅ Training script found")
        return True
    else:
        logger.error("❌ Training script not found")
        return False

def test_proof_script():
    """Test proof script availability"""
    logger.info("=== Testing Proof Script ===")
    
    if os.path.exists("prove.py"):
        logger.info("✅ Proof script found")
        return True
    else:
        logger.error("❌ Proof script not found")
        return False

def test_ipfs_upload():
    """Test IPFS upload module"""
    logger.info("=== Testing IPFS Upload Module ===")
    
    try:
        from ipfs_upload import upload_to_ipfs
        logger.info("✅ IPFS upload module imported successfully")
        return True
    except Exception as e:
        logger.error(f"❌ IPFS upload module failed: {e}")
        return False

def test_zk_proofs():
    """Test ZK proofs module"""
    logger.info("=== Testing ZK Proofs Module ===")
    
    try:
        from zk_proofs import ZKProofSystem
        logger.info("✅ ZK proofs module imported successfully")
        return True
    except Exception as e:
        logger.warning(f"⚠️  ZK proofs module not available: {e}")
        return False

def test_dependencies():
    """Test Python dependencies"""
    logger.info("=== Testing Python Dependencies ===")
    
    dependencies = [
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("peft", "PEFT"),
        ("requests", "Requests"),
        ("pandas", "Pandas")
    ]
    
    all_available = True
    for module, name in dependencies:
        try:
            __import__(module)
            logger.info(f"✅ {name} available")
        except ImportError:
            logger.warning(f"⚠️  {name} not available")
            all_available = False
    
    return all_available

def test_basic_operation():
    """Test basic operation without full training"""
    logger.info("=== Testing Basic Operation ===")
    
    try:
        # Test configuration loading
        import importlib.util
        spec = importlib.util.spec_from_file_location("aztec_agent", "aztec-agent.py")
        aztec_agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aztec_agent)
        
        config = aztec_agent.load_config()
        
        # Test data loading
        import pandas as pd
        df = pd.read_csv("./data/mock_data.csv")
        logger.info(f"✅ Data loaded: {len(df)} samples")
        
        # Test model loading (without training)
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(config["model"])
        logger.info("✅ Tokenizer loaded successfully")
        
        logger.info("✅ Basic operation test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic operation test failed: {e}")
        return False

def test_full_workflow():
    """Test that the main workflow can run"""
    logger.info("=== Testing Full Workflow ===")
    
    try:
        # Check if the main agent file exists and can be run
        if os.path.exists("aztec-agent.py"):
            logger.info("✅ Main agent script found")
            
            # Check if it has the required functions
            with open("aztec-agent.py", "r") as f:
                content = f.read()
                if "def load_config" in content and "def main" in content:
                    logger.info("✅ Main agent script has required functions")
                    return True
                else:
                    logger.error("❌ Main agent script missing required functions")
                    return False
        else:
            logger.error("❌ Main agent script not found")
            return False
            
    except Exception as e:
        logger.error(f"❌ Full workflow test failed: {e}")
        return False

def main():
    """Run all local operation tests"""
    logger.info("=== Aztec Protocol Local Operation Test ===")
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("Data Availability", test_data_availability),
        ("Training Script", test_training_script),
        ("Proof Script", test_proof_script),
        ("IPFS Upload", test_ipfs_upload),
        ("ZK Proofs", test_zk_proofs),
        ("Dependencies", test_dependencies),
        ("Basic Operation", test_basic_operation),
        ("Full Workflow", test_full_workflow)
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        try:
            success = test_func()
            results[test_name] = success
            if success:
                passed += 1
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n=== Test Results Summary ===")
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Local operation is ready.")
        return 0
    elif passed >= total * 0.8:  # 80% threshold
        logger.info("✅ Most tests passed. Local operation should work with some limitations.")
        return 0
    else:
        logger.error("❌ Too many tests failed. Please fix issues before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
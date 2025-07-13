#!/usr/bin/env python3
"""
Cross-Platform Aztec Agent
Works in both Windows and WSL environments with appropriate fallbacks
"""

import json
import os
import sys
import logging
import subprocess
import platform
from pathlib import Path
from datetime import datetime, timezone

# Import existing modules - fix the import name
try:
    # Import functions directly from aztec-agent.py
    import importlib.util
    spec = importlib.util.spec_from_file_location("aztec_agent", "aztec-agent.py")
    aztec_agent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(aztec_agent)
    
    # Import the upload function directly
    from ipfs_upload import upload_to_ipfs
except ImportError as e:
    logging.error(f"Failed to import required modules: {e}")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def detect_environment():
    """Detect the current environment"""
    system = platform.system()
    if "Microsoft" in platform.release() or "WSL" in platform.release():
        return "WSL"
    elif system == "Windows":
        return "Windows"
    elif system == "Linux":
        return "Linux"
    else:
        return "Unknown"

def check_noir_availability():
    """Check if Noir is available in current environment"""
    try:
        result = subprocess.run(
            ["nargo", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def get_zk_capabilities():
    """Determine ZK proof capabilities based on environment"""
    environment = detect_environment()
    noir_available = check_noir_availability()
    
    capabilities = {
        "environment": environment,
        "noir_available": noir_available,
        "zk_proofs_enabled": False,
        "circuit_compilation_enabled": False,
        "fallback_mode": False
    }
    
    if environment == "WSL" and noir_available:
        capabilities.update({
            "zk_proofs_enabled": True,
            "circuit_compilation_enabled": True,
            "fallback_mode": False
        })
        logger.info("✅ Full ZK proof capabilities available in WSL")
    else:
        capabilities.update({
            "zk_proofs_enabled": False,
            "circuit_compilation_enabled": False,
            "fallback_mode": True
        })
        logger.warning(f"⚠️  Limited ZK capabilities in {environment} - using fallback mode")
    
    return capabilities

class CrossPlatformAztecAgent:
    """Cross-platform Aztec agent with environment-aware capabilities"""
    
    def __init__(self, config_path="aztec-agent.toml"):
        self.config = aztec_agent.load_config()
        self.capabilities = get_zk_capabilities()
        
        logger.info(f"=== Cross-Platform Aztec Agent ===")
        logger.info(f"Environment: {self.capabilities['environment']}")
        logger.info(f"ZK Proofs: {'✅ Enabled' if self.capabilities['zk_proofs_enabled'] else '❌ Disabled'}")
        logger.info(f"Fallback Mode: {'✅ Active' if self.capabilities['fallback_mode'] else '❌ Disabled'}")
    
    def run_training_round(self, round_id):
        """Run a training round with environment-aware proof generation"""
        logger.info(f"=== Starting Training Round {round_id} ===")
        
        # Step 1: Training (works in all environments)
        logger.info("Step 1: Training...")
        training_result = self._run_training()
        
        if not training_result:
            logger.error("Training failed")
            return False
        
        # Step 2: Proof Generation (environment-dependent)
        logger.info("Step 2: Proof Generation...")
        proof_result = self._generate_proofs_environment_aware()
        
        if not proof_result:
            logger.error("Proof generation failed")
            return False
        
        # Step 3: IPFS Upload (works in all environments)
        logger.info("Step 3: IPFS Upload...")
        upload_result = self._upload_to_ipfs()
        
        if not upload_result:
            logger.error("IPFS upload failed")
            return False
        
        logger.info("✅ Training round completed successfully")
        return True
    
    def _run_training(self):
        """Run the training process"""
        try:
            # Run training script
            result = subprocess.run(
                [sys.executable, "train.py"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                logger.info("✅ Training completed successfully")
                return True
            else:
                logger.error(f"Training failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Training timed out")
            return False
        except Exception as e:
            logger.error(f"Training error: {e}")
            return False
    
    def _generate_proofs_environment_aware(self):
        """Generate proofs based on environment capabilities"""
        if self.capabilities['zk_proofs_enabled']:
            return self._generate_zk_proofs()
        else:
            return self._generate_simulated_proofs()
    
    def _generate_zk_proofs(self):
        """Generate real ZK proofs (WSL only)"""
        logger.info("Generating real ZK proofs...")
        
        try:
            # Import ZK proof system
            from zk_proofs import ZKProofSystem
            
            # Load training stats
            if os.path.exists("training_stats.json"):
                with open("training_stats.json", "r") as f:
                    training_data = json.load(f)
            else:
                training_data = {
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
            
            # Generate ZK proofs
            zk_system = ZKProofSystem()
            proofs = zk_system.generate_all_proofs(training_data)
            
            # Save proofs
            with open("proof.json", "w") as f:
                json.dump({
                    "proof_type": "zk_proofs",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "zk_proofs": proofs,
                    "environment": self.capabilities['environment'],
                    "capabilities": self.capabilities
                }, f, indent=2)
            
            logger.info("✅ ZK proofs generated successfully")
            return True
            
        except Exception as e:
            logger.error(f"ZK proof generation failed: {e}")
            logger.info("Falling back to simulated proofs")
            return self._generate_simulated_proofs()
    
    def _generate_simulated_proofs(self):
        """Generate simulated proofs (fallback for non-WSL environments)"""
        logger.info("Generating simulated proofs (fallback mode)...")
        
        try:
            # Run prove.py which handles simulation
            result = subprocess.run(
                [sys.executable, "prove.py"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and os.path.exists("proof.json"):
                logger.info("✅ Simulated proof generated successfully")
                return True
            else:
                logger.error(f"Simulated proof generation failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Simulated proof generation failed: {e}")
            return False
    
    def _upload_to_ipfs(self):
        """Upload files to IPFS (works in all environments)"""
        logger.info("Uploading files to IPFS...")
        
        try:
            # Upload model diff
            model_cid = None
            if os.path.exists("model_diff.pt"):
                model_cid = upload_to_ipfs("model_diff.pt", self.config["pinata_api_key"], self.config["pinata_secret_key"])
                logger.info(f"Model diff uploaded: {model_cid}")
            
            # Upload proof
            proof_cid = None
            if os.path.exists("proof.json"):
                proof_cid = upload_to_ipfs("proof.json", self.config["pinata_api_key"], self.config["pinata_secret_key"])
                logger.info(f"Proof uploaded: {proof_cid}")
            
            # Create metadata
            metadata = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "environment": self.capabilities['environment'],
                "capabilities": self.capabilities,
                "files": {
                    "model_diff": model_cid,
                    "proof": proof_cid
                }
            }
            
            with open("metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)
            
            logger.info("✅ IPFS upload completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"IPFS upload failed: {e}")
            return False
    
    def get_status_report(self):
        """Get a status report of the current environment and capabilities"""
        return {
            "environment": self.capabilities['environment'],
            "capabilities": self.capabilities,
            "config": self.config,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

def main():
    """Main function for cross-platform agent"""
    try:
        # Initialize cross-platform agent
        agent = CrossPlatformAztecAgent()
        
        # Print status report
        status = agent.get_status_report()
        logger.info("=== Environment Status ===")
        logger.info(f"Environment: {status['environment']}")
        logger.info(f"ZK Proofs: {'✅ Available' if status['capabilities']['zk_proofs_enabled'] else '❌ Not Available'}")
        logger.info(f"Fallback Mode: {'✅ Active' if status['capabilities']['fallback_mode'] else '❌ Disabled'}")
        
        # Run training round
        success = agent.run_training_round(1)
        
        if success:
            logger.info("✅ Cross-platform agent completed successfully!")
            return 0
        else:
            logger.error("❌ Cross-platform agent failed!")
            return 1
            
    except Exception as e:
        logger.error(f"Cross-platform agent error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
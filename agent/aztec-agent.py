import subprocess
import json
import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from ipfs_upload import upload_to_ipfs

# Constants
CONFIG_PATH = "aztec-agent.toml"
MEMORY_PATH = "agent-memory.json"
METADATA_PATH = "metadata.json"
MODEL_DIFF_PATH = "model_diff.pt"
PROOF_PATH = "proof.json"
LOGS_DIR = "logs"

# Setup logging
os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{LOGS_DIR}/agent.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

try:
    import tomllib  # Python 3.11+
except ImportError:
    import toml as tomllib

def validate_config(config):
    """Validate configuration values"""
    required_fields = [
        "wallet_address", "agent_name", "model", "method", 
        "batch_size", "reward_threshold", "data_path",
        "pinata_api_key", "pinata_secret_key"
    ]
    
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required config field: {field}")
    
    if not os.path.exists(config["data_path"]):
        raise FileNotFoundError(f"Data file not found: {config['data_path']}")
    
    if config["batch_size"] <= 0:
        raise ValueError("batch_size must be positive")
    
    if config["reward_threshold"] < 0:
        raise ValueError("reward_threshold must be non-negative")
    
    logger.info("Configuration validation passed")

def load_config():
    """Load and validate configuration"""
    try:
        if not os.path.exists(CONFIG_PATH):
            raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
        
        with open(CONFIG_PATH, "rb") as f:
            config = tomllib.load(f)["agent"]
        
        validate_config(config)
        return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise

def ensure_file_exists(file_path, description):
    """Check if file exists, raise error if not"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{description} not found: {file_path}")
    logger.info(f"{description} found: {file_path}")

def update_memory_round(round_id, uploads=None, success=True):
    """Update agent memory with round information"""
    try:
        with open(MEMORY_PATH, "r+") as f:
            memory = json.load(f)
            round_entry = {
                "round_id": round_id,
                "timestamp": datetime.utcnow().isoformat(),
                "success": success
            }
            if uploads:
                round_entry["uploads"] = uploads
            memory["rounds_joined"].append(round_entry)
            f.seek(0)
            json.dump(memory, f, indent=2)
            f.truncate()
        logger.info(f"Memory updated for round {round_id}")
    except Exception as e:
        logger.error(f"Failed to update memory: {e}")

def save_metadata(round_id, agent_name, config, model_diff_cid, proof_cid):
    """Save metadata with error handling"""
    try:
        metadata = {
            "round_id": round_id,
            "agent_name": agent_name,
            "wallet_address": config["wallet_address"],
            "model": config["model"],
            "method": config["method"],
            "batch_size": config["batch_size"],
            "reward_threshold": config["reward_threshold"],
            "data_path": config["data_path"],
            "model_diff_cid": model_diff_cid,
            "proof_cid": proof_cid,
            "timestamp": datetime.utcnow().isoformat()
        }
        with open(METADATA_PATH, "w") as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Metadata saved to {METADATA_PATH}")
    except Exception as e:
        logger.error(f"Failed to save metadata: {e}")
        raise

def run_with_retry(command, max_retries=3, description="Command"):
    """Run a command with retry logic"""
    for attempt in range(max_retries):
        try:
            logger.info(f"{description} attempt {attempt + 1}/{max_retries}")
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info(f"{description} completed successfully")
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"{description} failed: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff

def discover_round():
    """Simulate round discovery (placeholder for future implementation)"""
    # TODO: Implement real round discovery from backend/contract
    round_id = 1
    logger.info(f"Discovered round {round_id}")
    return round_id

def cleanup_temp_files():
    """Clean up temporary files"""
    temp_files = ["./results", "./logs"]
    for temp_path in temp_files:
        if os.path.exists(temp_path):
            try:
                import shutil
                shutil.rmtree(temp_path)
                logger.info(f"Cleaned up: {temp_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up {temp_path}: {e}")

def main():
    """Main agent function with comprehensive error handling"""
    start_time = time.time()
    success = False
    
    try:
        logger.info("=== Aztec Agent Starting ===")
        
        # Load and validate configuration
        config = load_config()
        logger.info(f"Agent: {config['agent_name']}, Model: {config['model']}")
        
        # Discover round
        round_id = discover_round()
        logger.info(f"Joining round {round_id}")
        update_memory_round(round_id)
        
        # Run training with retry
        logger.info("Starting training...")
        run_with_retry(["python", "train.py"], description="Training")
        
        # Verify training output
        ensure_file_exists(MODEL_DIFF_PATH, "Model diff file")
        
        # Generate proof with retry
        logger.info("Generating proof...")
        run_with_retry(["python", "prove.py"], description="Proof generation")
        
        # Verify proof output
        ensure_file_exists(PROOF_PATH, "Proof file")
        
        # Upload to IPFS with retry
        logger.info("Uploading model diff to IPFS...")
        model_diff_cid = upload_to_ipfs(MODEL_DIFF_PATH, config["pinata_api_key"], config["pinata_secret_key"])
        
        logger.info("Uploading proof to IPFS...")
        proof_cid = upload_to_ipfs(PROOF_PATH, config["pinata_api_key"], config["pinata_secret_key"])
        
        # Save metadata
        save_metadata(round_id, config["agent_name"], config, model_diff_cid, proof_cid)
        
        # Update memory with uploads
        uploads = {"model_diff_cid": model_diff_cid, "proof_cid": proof_cid}
        update_memory_round(round_id, uploads=uploads, success=True)
        
        success = True
        duration = time.time() - start_time
        logger.info(f"=== Round {round_id} completed successfully in {duration:.2f}s ===")
        
    except Exception as e:
        logger.error(f"Agent failed: {e}")
        update_memory_round(round_id if 'round_id' in locals() else 0, success=False)
        raise
    finally:
        # Cleanup
        cleanup_temp_files()
        
        if success:
            logger.info("Outputs: model_diff.pt, proof.json, metadata.json, agent-memory.json")
        else:
            logger.error("Agent failed - check logs for details")

if __name__ == "__main__":
    main()

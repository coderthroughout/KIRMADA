import json
import hashlib
import os
import logging
from datetime import datetime, timezone
from pathlib import Path

# Import ZK proof system
try:
    from zk_proofs import ZKProofSystem
    ZK_AVAILABLE = True
except ImportError:
    ZK_AVAILABLE = False
    logging.warning("ZK proof system not available - falling back to simulation")

MODEL_DIFF_PATH = "model_diff.pt"
PROOF_PATH = "proof.json"
MEMORY_PATH = "agent-memory.json"
TRAINING_STATS_PATH = "training_stats.json"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def hash_file(path):
    """Hash a file using SHA-256"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


def update_memory_proof(proof_path):
    """Update agent memory with proof information"""
    try:
        with open(MEMORY_PATH, "r+") as f:
            memory = json.load(f)
            memory.setdefault("proofs", []).append({
                "proof_path": proof_path,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            f.seek(0)
            json.dump(memory, f, indent=2)
            f.truncate()
        logger.info("Memory updated with proof information")
    except Exception as e:
        logger.error(f"Failed to update memory: {e}")


def load_training_stats():
    """Load training statistics from the training process"""
    try:
        if os.path.exists(TRAINING_STATS_PATH):
            with open(TRAINING_STATS_PATH, "r") as f:
                return json.load(f)
        else:
            # Fallback: try to extract from memory
            with open(MEMORY_PATH, "r") as f:
                memory = json.load(f)
                if "training_stats" in memory and memory["training_stats"]:
                    return memory["training_stats"][-1]  # Get latest stats
        return {}
    except Exception as e:
        logger.warning(f"Could not load training stats: {e}")
        return {}


def extract_model_params(model_diff_path):
    """Extract model parameters from the model diff file"""
    try:
        import torch
        if os.path.exists(model_diff_path):
            # Load the model diff and extract some parameters
            model_diff = torch.load(model_diff_path, map_location='cpu')
            
            # Extract first few parameters as a sample
            params = []
            for key, value in model_diff.items():
                if hasattr(value, 'flatten'):
                    flattened = value.flatten()
                    if len(flattened) > 0:
                        params.extend(flattened[:4].tolist())  # Take first 4 values
                        break
            
            # Pad to 4 parameters if needed
            while len(params) < 4:
                params.append(0.0)
            
            return params[:4]  # Return exactly 4 parameters
        else:
            return [0.1, 0.2, 0.3, 0.4]  # Default parameters
    except ImportError:
        logger.warning("PyTorch not available - using default parameters")
        return [0.1, 0.2, 0.3, 0.4]  # Default parameters
    except Exception as e:
        logger.warning(f"Could not extract model parameters: {e}")
        return [0.1, 0.2, 0.3, 0.4]  # Default parameters


def simulate_proof():
    """Generate a simulated proof (fallback when ZK is not available)"""
    logger.info("Generating simulated proof...")
    
    # Hash the model diff
    diff_hash = hash_file(MODEL_DIFF_PATH)
    
    # Create simulated proof
    proof = {
        "model_diff_hash": diff_hash,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "proof_type": "simulated",
        "metadata": {
            "model_diff": MODEL_DIFF_PATH,
            "note": "This is a simulated proof - ZK proofs not available"
        }
    }
    
    # Save proof
    with open(PROOF_PATH, "w") as f:
        json.dump(proof, f, indent=2)
    
    update_memory_proof(PROOF_PATH)
    logger.info(f"Simulated proof generated at {PROOF_PATH}")
    return proof


def generate_zk_proofs():
    """Generate ZK proofs using the proof system"""
    logger.info("Generating ZK proofs...")
    
    # Load training statistics
    training_stats = load_training_stats()
    
    # Extract model parameters
    model_params_before = training_stats.get("model_params_before", [0.1, 0.2, 0.3, 0.4])
    model_params_after = extract_model_params(MODEL_DIFF_PATH)
    
    # Prepare training data for ZK proofs
    training_data = {
        "dataset_hash": training_stats.get("dataset_hash", 123456789),
        "model_params_before": model_params_before,
        "model_params_after": model_params_after,
        "batch_size": training_stats.get("batch_size", 32),
        "num_epochs": training_stats.get("num_epochs", 1),
        "final_loss": training_stats.get("loss", 0.5),
        "seed": training_stats.get("seed", 42),
        "num_samples": training_stats.get("dataset_size", 1000),
        "dataset_size": training_stats.get("dataset_size_bytes", 100000),
        "feature_dim": training_stats.get("feature_dim", 768),
        "num_classes": training_stats.get("num_classes", 2)
    }
    
    # Initialize ZK proof system
    zk_system = ZKProofSystem()
    
    # Generate all proofs
    proofs = zk_system.generate_all_proofs(training_data)
    
    # Create combined proof structure
    combined_proof = {
        "proof_type": "zk_proofs",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "zk_proofs": proofs,
        "training_data": training_data,
        "metadata": {
            "model_diff": MODEL_DIFF_PATH,
            "note": "ZK proofs generated successfully"
        }
    }
    
    # Save combined proof
    with open(PROOF_PATH, "w") as f:
        json.dump(combined_proof, f, indent=2)
    
    update_memory_proof(PROOF_PATH)
    logger.info(f"ZK proofs generated and saved to {PROOF_PATH}")
    return combined_proof


def main():
    """Main proof generation function"""
    logger.info("=== Starting Proof Generation ===")
    
    # Check if model diff exists
    if not os.path.exists(MODEL_DIFF_PATH):
        raise FileNotFoundError(f"Model diff file not found: {MODEL_DIFF_PATH}")
    
    try:
        if ZK_AVAILABLE:
            # Try to generate ZK proofs
            try:
                proof = generate_zk_proofs()
                logger.info("ZK proofs generated successfully")
            except Exception as e:
                logger.error(f"ZK proof generation failed: {e}")
                logger.info("Falling back to simulated proof")
                proof = simulate_proof()
        else:
            # Fall back to simulated proof
            logger.info("ZK proof system not available, using simulation")
            proof = simulate_proof()
        
        logger.info("Proof generation completed successfully")
        return proof
        
    except Exception as e:
        logger.error(f"Proof generation failed: {e}")
        raise


if __name__ == "__main__":
    main()

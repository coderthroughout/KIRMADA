#!/usr/bin/env python3
"""
ZK Proof System for Aztec Protocol
Handles generation and verification of zero-knowledge proofs using Noir circuits
"""

import json
import os
import sys
import logging
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timezone

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ZKProofSystem:
    """Zero-knowledge proof system using Noir circuits"""
    
    def __init__(self, circuits_dir: str = "../circuits"):
        self.circuits_dir = Path(circuits_dir)
        self.proofs_dir = Path("proofs")
        self.proofs_dir.mkdir(exist_ok=True)
        
        # Circuit paths
        self.training_circuit = self.circuits_dir / "training_proof"
        self.data_integrity_circuit = self.circuits_dir / "data_integrity"
        self.model_diff_circuit = self.circuits_dir / "model_diff"
        
        # Verify circuits exist
        self._verify_circuits()
    
    def _verify_circuits(self):
        """Verify that all required circuits exist"""
        circuits = [
            ("training_proof", self.training_circuit),
            ("data_integrity", self.data_integrity_circuit),
            ("model_diff", self.model_diff_circuit)
        ]
        
        for name, path in circuits:
            if not path.exists():
                raise FileNotFoundError(f"Circuit directory not found: {path}")
            if not (path / "src" / "main.nr").exists():
                raise FileNotFoundError(f"Circuit source not found: {path}/src/main.nr")
    
    def _run_nargo_command(self, circuit_path: Path, command: str, args: List[str] = None) -> subprocess.CompletedProcess:
        """Run a nargo command in the specified circuit directory"""
        cmd = ["nargo", command]
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                cwd=circuit_path,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Nargo {command} completed successfully in {circuit_path}")
            return result
        except FileNotFoundError:
            logger.error(f"Nargo not found in PATH. Please install Noir first.")
            raise RuntimeError("Noir (nargo) not installed. Run 'python install_noir.py' for instructions.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Nargo {command} failed in {circuit_path}: {e.stderr}")
            raise
    
    def _compile_circuit(self, circuit_path: Path) -> bool:
        """Compile a Noir circuit"""
        try:
            self._run_nargo_command(circuit_path, "compile")
            return True
        except subprocess.CalledProcessError:
            return False
    
    def compile_all_circuits(self) -> Dict[str, bool]:
        """Compile all circuits and return compilation status"""
        circuits = {
            "training_proof": self.training_circuit,
            "data_integrity": self.data_integrity_circuit,
            "model_diff": self.model_diff_circuit
        }
        
        results = {}
        for name, path in circuits.items():
            logger.info(f"Compiling {name} circuit...")
            results[name] = self._compile_circuit(path)
        
        return results
    
    def _generate_proof_inputs(self, training_data: Dict) -> Dict[str, Dict]:
        """Generate inputs for all proof circuits based on training data"""
        # Extract training information
        dataset_hash = training_data.get("dataset_hash", 0)
        model_params_before = training_data.get("model_params_before", [0, 0, 0, 0])
        model_params_after = training_data.get("model_params_after", [0, 0, 0, 0])
        batch_size = training_data.get("batch_size", 32)
        num_epochs = training_data.get("num_epochs", 1)
        final_loss = training_data.get("final_loss", 0.5)
        seed = training_data.get("seed", 42)
        
        # Dataset metadata
        num_samples = training_data.get("num_samples", 1000)
        dataset_size = training_data.get("dataset_size", 100000)
        feature_dim = training_data.get("feature_dim", 768)
        num_classes = training_data.get("num_classes", 2)
        format_version = 1
        
        # Generate inputs for each circuit
        inputs = {
            "training_proof": {
                "dataset_hash": dataset_hash,
                "model_params_before": model_params_before,
                "model_params_after": model_params_after,
                "batch_size": batch_size,
                "num_epochs": num_epochs,
                "final_loss": final_loss,
                "seed": seed
            },
            "data_integrity": {
                "dataset_hash": dataset_hash,
                "num_samples": num_samples,
                "dataset_size": dataset_size,
                "feature_dim": feature_dim,
                "num_classes": num_classes,
                "format_version": format_version
            },
            "model_diff": {
                "training_proof_hash": 0,  # Will be updated after training proof
                "model_params_before": model_params_before,
                "model_params_after": model_params_after,
                "model_diff_hash": self._calculate_model_diff_hash(model_params_before, model_params_after),
                "batch_size": batch_size,
                "num_epochs": num_epochs,
                "final_loss": final_loss
            }
        }
        
        return inputs
    
    def _calculate_model_diff_hash(self, before: List[float], after: List[float]) -> int:
        """Calculate hash of model diff"""
        diff = [after[i] - before[i] for i in range(len(before))]
        diff_bytes = json.dumps(diff, sort_keys=True).encode()
        return int(hashlib.sha256(diff_bytes).hexdigest()[:16], 16)
    
    def _write_proof_inputs(self, circuit_name: str, inputs: Dict) -> Path:
        """Write proof inputs to a JSON file"""
        input_file = self.proofs_dir / f"{circuit_name}_inputs.json"
        
        with open(input_file, "w") as f:
            json.dump(inputs, f, indent=2)
        
        logger.info(f"Proof inputs written to {input_file}")
        return input_file
    
    def _generate_proof(self, circuit_path: Path, input_file: Path) -> Tuple[Path, Path]:
        """Generate a proof using nargo execute"""
        # Copy input file to circuit directory
        circuit_input = circuit_path / "Prover.toml"
        with open(input_file, "r") as src, open(circuit_input, "w") as dst:
            dst.write(src.read())
        
        # Generate proof using nargo execute
        self._run_nargo_command(circuit_path, "execute")
        
        # Get proof and verification key paths
        proof_file = circuit_path / "proofs" / "proof"
        vk_file = circuit_path / "proofs" / "vk"
        
        # Copy to our proofs directory
        our_proof_file = self.proofs_dir / f"{input_file.stem}.proof"
        our_vk_file = self.proofs_dir / f"{input_file.stem}.vk"
        
        if proof_file.exists():
            with open(proof_file, "rb") as src, open(our_proof_file, "wb") as dst:
                dst.write(src.read())
        
        if vk_file.exists():
            with open(vk_file, "rb") as src, open(our_vk_file, "wb") as dst:
                dst.write(src.read())
        
        return our_proof_file, our_vk_file
    
    def _verify_proof(self, circuit_path: Path, proof_file: Path, vk_file: Path) -> bool:
        """Verify a proof using nargo verify"""
        try:
            # Copy files to circuit directory
            circuit_proof = circuit_path / "proofs" / "proof"
            circuit_vk = circuit_path / "proofs" / "vk"
            
            circuit_proof.parent.mkdir(exist_ok=True)
            
            if proof_file.exists():
                with open(proof_file, "rb") as src, open(circuit_proof, "wb") as dst:
                    dst.write(src.read())
            
            if vk_file.exists():
                with open(vk_file, "rb") as src, open(circuit_vk, "wb") as dst:
                    dst.write(src.read())
            
            self._run_nargo_command(circuit_path, "verify")
            return True
        except subprocess.CalledProcessError:
            return False
    
    def generate_training_proof(self, training_data: Dict) -> Dict:
        """Generate training proof"""
        logger.info("Generating training proof...")
        
        # Get inputs for training proof
        inputs = self._generate_proof_inputs(training_data)["training_proof"]
        
        # Write inputs
        input_file = self._write_proof_inputs("training_proof", inputs)
        
        # Generate proof
        proof_file, vk_file = self._generate_proof(self.training_circuit, input_file)
        
        # Verify proof
        verification_success = self._verify_proof(self.training_circuit, proof_file, vk_file)
        
        # Read proof data
        proof_hash = "0" * 64  # Default hash if file doesn't exist
        if proof_file.exists():
            with open(proof_file, "rb") as f:
                proof_data = f.read()
            proof_hash = hashlib.sha256(proof_data).hexdigest()
        
        result = {
            "proof_type": "training_proof",
            "proof_file": str(proof_file),
            "vk_file": str(vk_file),
            "proof_hash": proof_hash,
            "verification_success": verification_success,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Training proof generated: {proof_hash}")
        return result
    
    def generate_data_integrity_proof(self, training_data: Dict) -> Dict:
        """Generate data integrity proof"""
        logger.info("Generating data integrity proof...")
        
        # Get inputs for data integrity proof
        inputs = self._generate_proof_inputs(training_data)["data_integrity"]
        
        # Write inputs
        input_file = self._write_proof_inputs("data_integrity", inputs)
        
        # Generate proof
        proof_file, vk_file = self._generate_proof(self.data_integrity_circuit, input_file)
        
        # Verify proof
        verification_success = self._verify_proof(self.data_integrity_circuit, proof_file, vk_file)
        
        # Read proof data
        proof_hash = "0" * 64  # Default hash if file doesn't exist
        if proof_file.exists():
            with open(proof_file, "rb") as f:
                proof_data = f.read()
            proof_hash = hashlib.sha256(proof_data).hexdigest()
        
        result = {
            "proof_type": "data_integrity_proof",
            "proof_file": str(proof_file),
            "vk_file": str(vk_file),
            "proof_hash": proof_hash,
            "verification_success": verification_success,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Data integrity proof generated: {proof_hash}")
        return result
    
    def generate_model_diff_proof(self, training_data: Dict, training_proof_hash: str) -> Dict:
        """Generate model diff proof"""
        logger.info("Generating model diff proof...")
        
        # Get inputs for model diff proof
        inputs = self._generate_proof_inputs(training_data)["model_diff"]
        inputs["training_proof_hash"] = int(training_proof_hash[:16], 16)  # Use first 16 chars as int
        
        # Write inputs
        input_file = self._write_proof_inputs("model_diff", inputs)
        
        # Generate proof
        proof_file, vk_file = self._generate_proof(self.model_diff_circuit, input_file)
        
        # Verify proof
        verification_success = self._verify_proof(self.model_diff_circuit, proof_file, vk_file)
        
        # Read proof data
        proof_hash = "0" * 64  # Default hash if file doesn't exist
        if proof_file.exists():
            with open(proof_file, "rb") as f:
                proof_data = f.read()
            proof_hash = hashlib.sha256(proof_data).hexdigest()
        
        result = {
            "proof_type": "model_diff_proof",
            "proof_file": str(proof_file),
            "vk_file": str(vk_file),
            "proof_hash": proof_hash,
            "verification_success": verification_success,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Model diff proof generated: {proof_hash}")
        return result
    
    def generate_all_proofs(self, training_data: Dict) -> Dict:
        """Generate all proofs for a training session"""
        logger.info("Generating all ZK proofs...")
        
        # Compile circuits first
        compilation_results = self.compile_all_circuits()
        if not all(compilation_results.values()):
            failed_circuits = [name for name, success in compilation_results.items() if not success]
            raise RuntimeError(f"Failed to compile circuits: {failed_circuits}")
        
        # Generate proofs in order
        training_proof = self.generate_training_proof(training_data)
        data_integrity_proof = self.generate_data_integrity_proof(training_data)
        model_diff_proof = self.generate_model_diff_proof(training_data, training_proof["proof_hash"])
        
        # Combine all proofs
        all_proofs = {
            "training_proof": training_proof,
            "data_integrity_proof": data_integrity_proof,
            "model_diff_proof": model_diff_proof,
            "compilation_results": compilation_results,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Save combined proofs
        proofs_file = self.proofs_dir / "all_proofs.json"
        with open(proofs_file, "w") as f:
            json.dump(all_proofs, f, indent=2)
        
        logger.info(f"All proofs generated and saved to {proofs_file}")
        return all_proofs
    
    def verify_all_proofs(self, proofs: Dict) -> Dict[str, bool]:
        """Verify all proofs"""
        verification_results = {}
        
        for proof_type, proof_data in proofs.items():
            if proof_type == "compilation_results" or proof_type == "timestamp":
                continue
            
            proof_file = Path(proof_data["proof_file"])
            vk_file = Path(proof_data["vk_file"])
            
            if proof_type == "training_proof":
                circuit_path = self.training_circuit
            elif proof_type == "data_integrity_proof":
                circuit_path = self.data_integrity_circuit
            elif proof_type == "model_diff_proof":
                circuit_path = self.model_diff_circuit
            else:
                continue
            
            verification_results[proof_type] = self._verify_proof(circuit_path, proof_file, vk_file)
        
        return verification_results


def main():
    """Test the ZK proof system"""
    # Sample training data
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
    
    try:
        zk_system = ZKProofSystem()
        
        # Compile circuits
        compilation_results = zk_system.compile_all_circuits()
        print(f"Compilation results: {compilation_results}")
        
        # Generate proofs
        proofs = zk_system.generate_all_proofs(training_data)
        print(f"Generated {len(proofs)} proof types")
        
        # Verify proofs
        verification_results = zk_system.verify_all_proofs(proofs)
        print(f"Verification results: {verification_results}")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
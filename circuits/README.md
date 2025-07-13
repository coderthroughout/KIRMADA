# Aztec Protocol ZK Proof System

This directory contains the Zero-Knowledge (ZK) proof circuits and integration for the Aztec Protocol, enabling privacy-preserving verification of AI model training.

## Overview

The ZK proof system consists of three main circuits:

1. **Training Proof Circuit** (`training_proof/`) - Verifies that legitimate training was performed
2. **Data Integrity Proof Circuit** (`data_integrity/`) - Verifies dataset validity and format
3. **Model Diff Proof Circuit** (`model_diff/`) - Verifies model diff generation from training

## Circuit Architecture

### Training Proof Circuit

**Purpose**: Proves that an agent performed legitimate training on valid data.

**Inputs**:
- `dataset_hash`: Commitment to training data
- `model_params_before`: Model parameters before training
- `model_params_after`: Model parameters after training
- `batch_size`: Training batch size
- `num_epochs`: Number of training epochs
- `final_loss`: Final training loss
- `seed`: Random seed for training

**Outputs**:
- `proof_hash`: Commitment to the training proof
- `training_verified`: Whether training was verified
- `model_diff_hash`: Hash of the model diff

**Verification Logic**:
- Model parameters must have changed (training occurred)
- Loss must be within reasonable bounds
- Training parameters must be valid
- Dataset hash must be non-zero

### Data Integrity Proof Circuit

**Purpose**: Proves that the training dataset is valid and properly formatted.

**Inputs**:
- `dataset_hash`: Hash of the dataset
- `num_samples`: Number of samples in dataset
- `dataset_size`: Dataset size in bytes
- `feature_dim`: Feature dimension
- `num_classes`: Number of classes
- `format_version`: Dataset format version

**Outputs**:
- `proof_hash`: Commitment to the data integrity proof
- `data_valid`: Whether data is valid
- `dataset_fingerprint`: Dataset fingerprint

**Verification Logic**:
- Dataset hash must be valid (non-zero)
- Number of samples must be reasonable
- Dataset size must be reasonable
- Feature dimension must be reasonable
- Number of classes must be reasonable
- Format version must be supported

### Model Diff Proof Circuit

**Purpose**: Proves that the model diff was generated from legitimate training.

**Inputs**:
- `training_proof_hash`: Hash of the training proof
- `model_params_before`: Model parameters before training
- `model_params_after`: Model parameters after training
- `model_diff_hash`: Hash of the model diff
- `batch_size`: Training batch size
- `num_epochs`: Number of training epochs
- `final_loss`: Final training loss

**Outputs**:
- `proof_hash`: Commitment to the model diff proof
- `diff_valid`: Whether diff is valid
- `diff_fingerprint`: Model diff fingerprint

**Verification Logic**:
- Training proof hash must be valid
- Model parameters must have changed
- Model diff hash must match calculated diff
- Training parameters must be valid
- Loss must be reasonable

## Directory Structure

```
circuits/
├── training_proof/
│   ├── Nargo.toml
│   └── src/
│       └── main.nr
├── data_integrity/
│   ├── Nargo.toml
│   └── src/
│       └── main.nr
├── model_diff/
│   ├── Nargo.toml
│   └── src/
│       └── main.nr
└── README.md
```

## Prerequisites

1. **Noir Installation**: Install Noir for ZK circuit development
   ```bash
   curl -L https://raw.githubusercontent.com/noir-lang/noirup/main/install | bash
   source ~/.bashrc
   noirup
   ```

2. **Nargo**: Verify Noir installation
   ```bash
   nargo --version
   ```

## Building Circuits

### Compile All Circuits

```bash
# From the circuits directory
for circuit in training_proof data_integrity model_diff; do
    echo "Compiling $circuit..."
    cd $circuit
    nargo compile
    cd ..
done
```

### Compile Individual Circuit

```bash
cd training_proof
nargo compile
```

## Testing Circuits

### Generate Proof

```bash
cd training_proof
nargo prove training_proof_inputs.json
```

### Verify Proof

```bash
cd training_proof
nargo verify training_proof_inputs.proof training_proof_inputs.vk
```

## Integration with Agent

The ZK proof system integrates with the Aztec agent through the `zk_proofs.py` module:

```python
from zk_proofs import ZKProofSystem

# Initialize ZK proof system
zk_system = ZKProofSystem()

# Generate all proofs
training_data = {
    "dataset_hash": 123456789,
    "model_params_before": [0.1, 0.2, 0.3, 0.4],
    "model_params_after": [0.15, 0.25, 0.35, 0.45],
    "batch_size": 32,
    "num_epochs": 1,
    "final_loss": 0.5,
    # ... other parameters
}

proofs = zk_system.generate_all_proofs(training_data)
```

## Smart Contract Integration

The `ProofVerifier.sol` contract provides on-chain verification:

```solidity
// Submit a proof for verification
proofVerifier.submitProof(
    "training_proof",
    proofHash,
    proofData
);

// Check if proof is valid
bool isValid = proofVerifier.isProofValid(proofHash);
```

## Security Considerations

1. **Circuit Security**: All circuits are designed with security in mind
   - Input validation
   - Reasonable bounds checking
   - Hash verification

2. **Proof Verification**: Multiple layers of verification
   - Circuit-level verification
   - Smart contract verification
   - Agent-level validation

3. **Privacy**: ZK proofs reveal only what's necessary
   - Training occurred (not the data)
   - Model changed (not the parameters)
   - Data is valid (not the content)

## Performance Considerations

1. **Proof Generation Time**: 
   - Training proof: ~30-60 seconds
   - Data integrity proof: ~10-20 seconds
   - Model diff proof: ~20-40 seconds

2. **Proof Size**:
   - Training proof: ~50-100 KB
   - Data integrity proof: ~20-50 KB
   - Model diff proof: ~30-80 KB

3. **Verification Time**:
   - On-chain verification: ~1-5 seconds
   - Off-chain verification: ~0.1-1 second

## Troubleshooting

### Common Issues

1. **Circuit Compilation Errors**
   ```bash
   # Check Noir version
   nargo --version
   
   # Clean and recompile
   nargo clean
   nargo compile
   ```

2. **Proof Generation Failures**
   ```bash
   # Check input format
   cat training_proof_inputs.json
   
   # Verify circuit compilation
   nargo compile
   ```

3. **Verification Failures**
   ```bash
   # Check proof and verification key
   ls -la *.proof *.vk
   
   # Re-run verification
   nargo verify proof.proof proof.vk
   ```

### Debug Mode

Enable debug logging in the agent:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. **Optimized Circuits**: Reduce proof generation time
2. **Batch Verification**: Verify multiple proofs at once
3. **Recursive Proofs**: Chain proofs for complex workflows
4. **Custom Gates**: Optimize for specific operations
5. **Proof Aggregation**: Combine multiple proofs efficiently

## Contributing

1. Follow Noir coding standards
2. Add comprehensive tests for new circuits
3. Update documentation for changes
4. Ensure backward compatibility
5. Security review for new features

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
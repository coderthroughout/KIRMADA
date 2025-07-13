// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

/**
 * @title ProofVerifier
 * @dev Verifies ZK proofs for Aztec Protocol training verification
 */
contract ProofVerifier is Ownable {
    using Strings for uint256;
    
    // Proof verification events
    event ProofVerified(
        address indexed agent,
        string proofType,
        bytes32 proofHash,
        bool isValid,
        uint256 timestamp
    );
    
    event ProofSubmitted(
        address indexed agent,
        string proofType,
        bytes32 proofHash,
        uint256 timestamp
    );
    
    // Struct for proof data
    struct ProofData {
        string proofType;
        bytes32 proofHash;
        bool isValid;
        uint256 timestamp;
        address agent;
    }
    
    // Mapping to store proofs
    mapping(bytes32 => ProofData) public proofs;
    mapping(address => bytes32[]) public agentProofs;
    
    // Verification thresholds
    uint256 public minTrainingLoss = 0.1 ether; // 0.1 in wei
    uint256 public maxTrainingLoss = 10 ether;  // 10.0 in wei
    uint256 public minBatchSize = 1;
    uint256 public maxBatchSize = 1024;
    uint256 public minEpochs = 1;
    uint256 public maxEpochs = 100;
    
    // Circuit verification keys (would be set by owner)
    bytes32 public trainingProofVK;
    bytes32 public dataIntegrityVK;
    bytes32 public modelDiffVK;
    
    constructor(address initialOwner) Ownable(initialOwner) {
        // Initialize with default verification keys
        // In production, these would be set by the owner after circuit compilation
        trainingProofVK = keccak256("training_proof_vk");
        dataIntegrityVK = keccak256("data_integrity_vk");
        modelDiffVK = keccak256("model_diff_vk");
    }
    
    /**
     * @dev Submit a training proof for verification
     * @param proofType Type of proof (training_proof, data_integrity, model_diff)
     * @param proofHash Hash of the proof
     * @param proofData Additional proof data for verification
     */
    function submitProof(
        string memory proofType,
        bytes32 proofHash,
        bytes calldata proofData
    ) external {
        require(bytes(proofType).length > 0, "Proof type cannot be empty");
        require(proofHash != bytes32(0), "Proof hash cannot be zero");
        
        // Verify proof based on type
        bool isValid = _verifyProof(proofType, proofHash, proofData);
        
        // Store proof data
        ProofData memory proof = ProofData({
            proofType: proofType,
            proofHash: proofHash,
            isValid: isValid,
            timestamp: block.timestamp,
            agent: msg.sender
        });
        
        proofs[proofHash] = proof;
        agentProofs[msg.sender].push(proofHash);
        
        emit ProofSubmitted(msg.sender, proofType, proofHash, block.timestamp);
        emit ProofVerified(msg.sender, proofType, proofHash, isValid, block.timestamp);
    }
    
    /**
     * @dev Verify a proof based on its type
     * @param proofType Type of proof to verify
     * @param proofHash Hash of the proof
     * @param proofData Additional proof data
     * @return isValid Whether the proof is valid
     */
    function _verifyProof(
        string memory proofType,
        bytes32 proofHash,
        bytes calldata proofData
    ) internal view returns (bool isValid) {
        if (keccak256(bytes(proofType)) == keccak256(bytes("training_proof"))) {
            return _verifyTrainingProof(proofHash, proofData);
        } else if (keccak256(bytes(proofType)) == keccak256(bytes("data_integrity"))) {
            return _verifyDataIntegrityProof(proofHash, proofData);
        } else if (keccak256(bytes(proofType)) == keccak256(bytes("model_diff"))) {
            return _verifyModelDiffProof(proofHash, proofData);
        } else {
            revert("Unknown proof type");
        }
    }
    
    /**
     * @dev Verify training proof
     * @param proofHash Hash of the proof
     * @param proofData Training proof data
     * @return isValid Whether the training proof is valid
     */
    function _verifyTrainingProof(
        bytes32 proofHash,
        bytes calldata proofData
    ) internal view returns (bool isValid) {
        // In a real implementation, this would verify the ZK proof
        // For now, we'll do basic validation of training parameters
        
        if (proofData.length < 32) {
            return false;
        }
        
        // Extract training parameters from proof data
        uint256 batchSize = _extractUint256(proofData, 0);
        uint256 numEpochs = _extractUint256(proofData, 32);
        uint256 finalLoss = _extractUint256(proofData, 64);
        
        // Validate training parameters
        bool validBatchSize = batchSize >= minBatchSize && batchSize <= maxBatchSize;
        bool validEpochs = numEpochs >= minEpochs && numEpochs <= maxEpochs;
        bool validLoss = finalLoss >= minTrainingLoss && finalLoss <= maxTrainingLoss;
        
        return validBatchSize && validEpochs && validLoss;
    }
    
    /**
     * @dev Verify data integrity proof
     * @param proofHash Hash of the proof
     * @param proofData Data integrity proof data
     * @return isValid Whether the data integrity proof is valid
     */
    function _verifyDataIntegrityProof(
        bytes32 proofHash,
        bytes calldata proofData
    ) internal view returns (bool isValid) {
        // In a real implementation, this would verify the ZK proof
        // For now, we'll do basic validation
        
        if (proofData.length < 32) {
            return false;
        }
        
        // Extract dataset parameters
        uint256 numSamples = _extractUint256(proofData, 0);
        uint256 datasetSize = _extractUint256(proofData, 32);
        
        // Validate dataset parameters
        bool validSamples = numSamples > 0 && numSamples <= 1000000;
        bool validSize = datasetSize > 0 && datasetSize <= 1000000000;
        
        return validSamples && validSize;
    }
    
    /**
     * @dev Verify model diff proof
     * @param proofHash Hash of the proof
     * @param proofData Model diff proof data
     * @return isValid Whether the model diff proof is valid
     */
    function _verifyModelDiffProof(
        bytes32 proofHash,
        bytes calldata proofData
    ) internal view returns (bool isValid) {
        // In a real implementation, this would verify the ZK proof
        // For now, we'll do basic validation
        
        if (proofData.length < 32) {
            return false;
        }
        
        // Extract model diff parameters
        uint256 modelDiffHash = _extractUint256(proofData, 0);
        
        // Basic validation - model diff should not be zero
        return modelDiffHash != 0;
    }
    
    /**
     * @dev Extract uint256 from bytes
     * @param data Bytes data
     * @param offset Offset to start reading from
     * @return value Extracted uint256 value
     */
    function _extractUint256(bytes calldata data, uint256 offset) internal pure returns (uint256 value) {
        require(data.length >= offset + 32, "Data too short");
        
        assembly {
            value := calldataload(add(data.offset, offset))
        }
    }
    
    /**
     * @dev Get proof data by hash
     * @param proofHash Hash of the proof
     * @return proof Proof data
     */
    function getProof(bytes32 proofHash) external view returns (ProofData memory proof) {
        return proofs[proofHash];
    }
    
    /**
     * @dev Get all proofs for an agent
     * @param agent Address of the agent
     * @return proofHashes Array of proof hashes
     */
    function getAgentProofs(address agent) external view returns (bytes32[] memory proofHashes) {
        return agentProofs[agent];
    }
    
    /**
     * @dev Check if a proof is valid
     * @param proofHash Hash of the proof
     * @return isValid Whether the proof is valid
     */
    function isProofValid(bytes32 proofHash) external view returns (bool isValid) {
        return proofs[proofHash].isValid;
    }
    
    /**
     * @dev Set verification keys (owner only)
     * @param _trainingProofVK Training proof verification key
     * @param _dataIntegrityVK Data integrity verification key
     * @param _modelDiffVK Model diff verification key
     */
    function setVerificationKeys(
        bytes32 _trainingProofVK,
        bytes32 _dataIntegrityVK,
        bytes32 _modelDiffVK
    ) external onlyOwner {
        trainingProofVK = _trainingProofVK;
        dataIntegrityVK = _dataIntegrityVK;
        modelDiffVK = _modelDiffVK;
    }
    
    /**
     * @dev Set verification thresholds (owner only)
     * @param _minTrainingLoss Minimum training loss
     * @param _maxTrainingLoss Maximum training loss
     * @param _minBatchSize Minimum batch size
     * @param _maxBatchSize Maximum batch size
     * @param _minEpochs Minimum epochs
     * @param _maxEpochs Maximum epochs
     */
    function setVerificationThresholds(
        uint256 _minTrainingLoss,
        uint256 _maxTrainingLoss,
        uint256 _minBatchSize,
        uint256 _maxBatchSize,
        uint256 _minEpochs,
        uint256 _maxEpochs
    ) external onlyOwner {
        require(_minTrainingLoss < _maxTrainingLoss, "Invalid loss range");
        require(_minBatchSize < _maxBatchSize, "Invalid batch size range");
        require(_minEpochs < _maxEpochs, "Invalid epochs range");
        
        minTrainingLoss = _minTrainingLoss;
        maxTrainingLoss = _maxTrainingLoss;
        minBatchSize = _minBatchSize;
        maxBatchSize = _maxBatchSize;
        minEpochs = _minEpochs;
        maxEpochs = _maxEpochs;
    }
    
    /**
     * @dev Get verification thresholds
     * @return thresholds Array of verification thresholds
     */
    function getVerificationThresholds() external view returns (uint256[6] memory thresholds) {
        thresholds[0] = minTrainingLoss;
        thresholds[1] = maxTrainingLoss;
        thresholds[2] = minBatchSize;
        thresholds[3] = maxBatchSize;
        thresholds[4] = minEpochs;
        thresholds[5] = maxEpochs;
    }
} 
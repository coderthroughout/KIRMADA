"""
Proof schemas for Aztec Protocol Backend
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ProofBase(BaseModel):
    """Base proof schema"""
    proof_type: str = Field(..., description="Type of proof (zk_proofs, simulated)")
    description: Optional[str] = Field(None, description="Proof description")
    status: str = Field(..., description="Proof status (pending, verified, failed)")


class ProofCreate(ProofBase):
    """Proof creation schema"""
    training_data: Optional[Dict[str, Any]] = Field(None, description="Training data used for proof")
    zk_proofs: Optional[Dict[str, Any]] = Field(None, description="ZK proof data")
    ipfs_hash: Optional[str] = Field(None, description="IPFS hash of proof file")


class ProofUpdate(BaseModel):
    """Proof update schema"""
    description: Optional[str] = None
    status: Optional[str] = None
    verification_result: Optional[Dict[str, Any]] = None
    blockchain_tx_hash: Optional[str] = None


class ProofResponse(ProofBase):
    """Proof response schema"""
    id: int
    training_data: Optional[Dict[str, Any]] = None
    zk_proofs: Optional[Dict[str, Any]] = None
    ipfs_hash: Optional[str] = None
    verification_result: Optional[Dict[str, Any]] = None
    blockchain_tx_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ZKProofData(BaseModel):
    """ZK proof data schema"""
    proof_type: str = Field(..., description="Type of ZK proof")
    timestamp: str = Field(..., description="Proof timestamp")
    zk_proofs: Dict[str, Any] = Field(..., description="ZK proof data")
    training_data: Dict[str, Any] = Field(..., description="Training data")
    metadata: Dict[str, Any] = Field(..., description="Proof metadata")
    environment: str = Field(..., description="Environment where proof was generated")
    capabilities: Dict[str, Any] = Field(..., description="Environment capabilities")


class ProofVerification(BaseModel):
    """Proof verification schema"""
    proof_id: int
    verification_type: str = Field(..., description="Type of verification")
    result: bool = Field(..., description="Verification result")
    details: Optional[Dict[str, Any]] = Field(None, description="Verification details")
    blockchain_submitted: bool = Field(False, description="Whether proof was submitted to blockchain")


class TrainingData(BaseModel):
    """Training data schema for proofs"""
    dataset_hash: int
    model_params_before: List[float]
    model_params_after: List[float]
    batch_size: int
    num_epochs: int
    final_loss: float
    seed: int
    num_samples: int
    dataset_size: int
    feature_dim: int
    num_classes: int 
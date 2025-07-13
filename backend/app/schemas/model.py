"""
Model schemas for Aztec Protocol Backend
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ModelBase(BaseModel):
    """Base model schema"""
    name: str = Field(..., description="Model name")
    description: Optional[str] = Field(None, description="Model description")
    model_type: str = Field(..., description="Model type (transformer, cnn, etc.)")
    architecture: Optional[str] = Field(None, description="Model architecture")
    parameters: Optional[int] = Field(None, description="Number of parameters")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    ipfs_hash: Optional[str] = Field(None, description="IPFS hash")
    accuracy: Optional[float] = Field(None, description="Model accuracy")
    loss: Optional[float] = Field(None, description="Training loss")


class ModelCreate(ModelBase):
    """Model creation schema"""
    training_config: Optional[Dict[str, Any]] = Field(None, description="Training configuration")


class ModelUpdate(BaseModel):
    """Model update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    model_type: Optional[str] = None
    architecture: Optional[str] = None
    parameters: Optional[int] = None
    file_size: Optional[int] = None
    ipfs_hash: Optional[str] = None
    accuracy: Optional[float] = None
    loss: Optional[float] = None
    status: Optional[str] = None
    training_config: Optional[Dict[str, Any]] = None


class ModelResponse(ModelBase):
    """Model response schema"""
    id: int
    status: str
    training_config: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TrainingStats(BaseModel):
    """Training statistics schema (from training_stats.json)"""
    epoch: int
    loss: float
    model_diff: str
    duration_seconds: float
    final_cpu_percent: float
    final_memory_percent: float
    dataset_size: int
    dataset_size_bytes: int
    feature_dim: int
    num_classes: int
    batch_size: int
    model_name: str
    model_params_before: List[float]
    model_params_after: List[float]
    dataset_hash: int
    num_epochs: int
    seed: int


class ModelUpload(BaseModel):
    """Model upload schema"""
    name: str
    description: Optional[str] = None
    model_type: str
    architecture: Optional[str] = None
    training_stats: Optional[TrainingStats] = None
    ipfs_hash: Optional[str] = None 
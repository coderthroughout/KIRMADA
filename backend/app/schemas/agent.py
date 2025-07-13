"""
Agent schemas for Aztec Protocol Backend
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AgentBase(BaseModel):
    """Base agent schema"""
    name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    agent_type: str = Field(..., description="Agent type (training, inference, etc.)")
    wallet_address: str = Field(..., description="Ethereum wallet address")
    model: str = Field(..., description="AI model name")
    method: str = Field(..., description="Training method (lora, full, etc.)")
    batch_size: int = Field(..., description="Training batch size")
    reward_threshold: float = Field(..., description="Minimum reward threshold")
    data_path: str = Field(..., description="Path to training data")


class AgentCreate(AgentBase):
    """Agent creation schema"""
    config: Optional[Dict[str, Any]] = Field(None, description="Additional configuration")


class AgentUpdate(BaseModel):
    """Agent update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    agent_type: Optional[str] = None
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None


class AgentResponse(AgentBase):
    """Agent response schema"""
    id: int
    status: str
    config: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AgentConfig(BaseModel):
    """Agent configuration schema (from aztec-agent.toml)"""
    wallet_address: str
    agent_name: str
    model: str
    method: str
    batch_size: int
    reward_threshold: float
    data_path: str
    pinata_api_key: str
    pinata_secret_key: str
    
    # Performance settings
    max_retries: int = 3
    rate_limit_delay: int = 1
    timeout_seconds: int = 30
    max_file_size_mb: int = 500
    
    # Logging settings
    level: str = "INFO"
    log_to_file: bool = True
    log_to_console: bool = True
    
    # Monitoring settings
    enable_resource_monitoring: bool = True
    enable_progress_tracking: bool = True 
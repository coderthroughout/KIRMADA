"""
Configuration settings for Aztec Protocol Backend
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Aztec Protocol Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "sqlite:///./aztec.db"
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Blockchain
    ETHEREUM_RPC_URL: str = "http://localhost:8545"
    CONTRACT_ADDRESSES: dict = {
        "proof_verifier": "0xa513E6E4b8f2a923D98304ec87F64353C4D5C853",
        "aztec_orchestrator": "0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6",
        "vault": "0x8A791620dd6260079BF849Dc5567aDC3F2FdC318"
    }
    
    # IPFS
    IPFS_API_URL: str = "https://gateway.pinata.cloud"
    IPFS_API_KEY: Optional[str] = None
    IPFS_API_SECRET: Optional[str] = None
    
    # AI/ML
    MODEL_CACHE_DIR: str = "./models"
    MAX_MODEL_SIZE_MB: int = 500
    TRAINING_TIMEOUT_SECONDS: int = 3600
    
    # ZK Proofs
    ZK_CIRCUITS_DIR: str = "../circuits"
    PROOF_TIMEOUT_SECONDS: int = 300
    
    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES: List[str] = [
        "application/json",
        "text/plain",
        "application/octet-stream"
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Validate database URL"""
        if not v:
            raise ValueError("DATABASE_URL cannot be empty")
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        """Validate secret key"""
        if v == "your-secret-key-change-in-production":
            import secrets
            return secrets.token_urlsafe(32)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings() 
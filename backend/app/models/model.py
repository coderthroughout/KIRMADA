"""
Model model for Aztec Protocol Backend
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class Model(Base):
    """Model for AI models"""
    
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    model_type = Column(String(50), nullable=False)  # transformer, cnn, etc.
    architecture = Column(String(100), nullable=True)
    parameters = Column(Integer, nullable=True)  # number of parameters
    file_size = Column(Integer, nullable=True)  # size in bytes
    ipfs_hash = Column(String(255), nullable=True)  # IPFS hash
    accuracy = Column(Float, nullable=True)
    loss = Column(Float, nullable=True)
    training_config = Column(Text, nullable=True)  # JSON training config
    status = Column(String(20), default="uploaded")  # uploaded, training, ready, error
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="models")
    agent = relationship("Agent", back_populates="models")
    proofs = relationship("Proof", back_populates="model")
    
    def __repr__(self):
        return f"<Model(id={self.id}, name='{self.name}', type='{self.model_type}', status='{self.status}')>" 
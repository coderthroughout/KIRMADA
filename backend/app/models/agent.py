"""
Agent model for Aztec Protocol Backend
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class Agent(Base):
    """Agent model for AI agents"""
    
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    agent_type = Column(String(50), nullable=False)  # training, inference, etc.
    status = Column(String(20), default="idle")  # idle, training, active, error
    config = Column(Text, nullable=True)  # JSON configuration
    performance_metrics = Column(Text, nullable=True)  # JSON metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="agents")
    models = relationship("Model", back_populates="agent")
    proofs = relationship("Proof", back_populates="agent")
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.agent_type}', status='{self.status}')>" 
"""
Round model for Aztec Protocol Backend
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class Round(Base):
    """Model for collaboration rounds"""
    
    __tablename__ = "rounds"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="active")  # active, completed, cancelled
    bounty_amount = Column(Float, nullable=True)  # ETH amount
    min_participants = Column(Integer, default=1)
    max_participants = Column(Integer, nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User")
    proofs = relationship("Proof", back_populates="round")
    
    def __repr__(self):
        return f"<Round(id={self.id}, name='{self.name}', status='{self.status}', bounty={self.bounty_amount})>" 
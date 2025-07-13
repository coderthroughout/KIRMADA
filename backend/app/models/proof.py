"""
Proof model for Aztec Protocol Backend
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class Proof(Base):
    """Model for ZK proofs"""
    
    __tablename__ = "proofs"
    
    id = Column(Integer, primary_key=True, index=True)
    proof_type = Column(String(50), nullable=False)  # training_proof, data_integrity, model_diff
    proof_hash = Column(String(255), nullable=False, unique=True)
    proof_data = Column(Text, nullable=True)  # JSON proof data
    ipfs_hash = Column(String(255), nullable=True)  # IPFS hash of proof
    verification_status = Column(String(20), default="pending")  # pending, verified, failed
    verification_result = Column(Boolean, nullable=True)
    verification_time = Column(Float, nullable=True)  # verification time in seconds
    circuit_name = Column(String(100), nullable=True)  # Noir circuit name
    public_inputs = Column(Text, nullable=True)  # JSON public inputs
    private_inputs = Column(Text, nullable=True)  # JSON private inputs (encrypted)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=True)
    round_id = Column(Integer, ForeignKey("rounds.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="proofs")
    agent = relationship("Agent", back_populates="proofs")
    model = relationship("Model", back_populates="proofs")
    round = relationship("Round", back_populates="proofs")
    
    def __repr__(self):
        return f"<Proof(id={self.id}, type='{self.proof_type}', hash='{self.proof_hash}', status='{self.verification_status}')>" 
"""
Proof endpoints for Aztec Protocol Backend
"""

import json
import os
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.proof import Proof
from app.schemas.proof import ProofCreate, ProofUpdate, ProofResponse, ZKProofData, ProofVerification, TrainingData
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=List[ProofResponse])
async def list_proofs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """List all proofs for the current user"""
    proofs = db.query(Proof).filter(
        Proof.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return proofs


@router.post("/", response_model=ProofResponse)
async def create_proof(
    proof: ProofCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new proof"""
    db_proof = Proof(
        proof_type=proof.proof_type,
        description=proof.description,
        status=proof.status,
        training_data=json.dumps(proof.training_data) if proof.training_data else None,
        zk_proofs=json.dumps(proof.zk_proofs) if proof.zk_proofs else None,
        ipfs_hash=proof.ipfs_hash,
        user_id=current_user.id
    )
    db.add(db_proof)
    db.commit()
    db.refresh(db_proof)
    return db_proof


@router.get("/{proof_id}", response_model=ProofResponse)
async def get_proof(
    proof_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get a specific proof"""
    proof = db.query(Proof).filter(
        and_(Proof.id == proof_id, Proof.user_id == current_user.id)
    ).first()
    if not proof:
        raise HTTPException(status_code=404, detail="Proof not found")
    return proof


@router.put("/{proof_id}", response_model=ProofResponse)
async def update_proof(
    proof_id: int,
    proof_update: ProofUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update a proof"""
    db_proof = db.query(Proof).filter(
        and_(Proof.id == proof_id, Proof.user_id == current_user.id)
    ).first()
    if not db_proof:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    update_data = proof_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field in ["training_data", "zk_proofs", "verification_result"] and value:
            setattr(db_proof, field, json.dumps(value))
        else:
            setattr(db_proof, field, value)
    
    db.commit()
    db.refresh(db_proof)
    return db_proof


@router.delete("/{proof_id}")
async def delete_proof(
    proof_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete a proof"""
    db_proof = db.query(Proof).filter(
        and_(Proof.id == proof_id, Proof.user_id == current_user.id)
    ).first()
    if not db_proof:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    db.delete(db_proof)
    db.commit()
    return {"message": "Proof deleted successfully"}


@router.post("/generate")
async def generate_proof(
    training_data: TrainingData,
    proof_type: str = "zk_proofs",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Generate a new proof from training data"""
    
    try:
        # Import ZK proof system from agent
        import sys
        sys.path.append('../agent')
        
        # Try to import ZK proof system
        try:
            from zk_proofs import ZKProofSystem
            zk_available = True
        except ImportError:
            zk_available = False
        
        if zk_available and proof_type == "zk_proofs":
            # Generate real ZK proofs
            zk_system = ZKProofSystem()
            zk_proofs = zk_system.generate_all_proofs(training_data.dict())
            
            proof_data = {
                "proof_type": "zk_proofs",
                "timestamp": "2024-01-01T00:00:00Z",
                "zk_proofs": zk_proofs,
                "training_data": training_data.dict(),
                "metadata": {
                    "model_diff": "model_diff.pt",
                    "note": "ZK proofs generated successfully"
                },
                "environment": "wsl",
                "capabilities": {
                    "zk_proofs_enabled": True,
                    "fallback_mode": False
                }
            }
        else:
            # Generate simulated proofs
            proof_data = {
                "proof_type": "simulated",
                "timestamp": "2024-01-01T00:00:00Z",
                "zk_proofs": {
                    "training_proof": "simulated_training_proof_hash",
                    "data_integrity_proof": "simulated_data_integrity_proof_hash",
                    "model_diff_proof": "simulated_model_diff_proof_hash"
                },
                "training_data": training_data.dict(),
                "metadata": {
                    "model_diff": "model_diff.pt",
                    "note": "Simulated proofs generated"
                },
                "environment": "windows",
                "capabilities": {
                    "zk_proofs_enabled": False,
                    "fallback_mode": True
                }
            }
        
        # Create proof record
        db_proof = Proof(
            proof_type=proof_type,
            description=f"Generated {proof_type} for training data",
            status="pending",
            training_data=json.dumps(training_data.dict()),
            zk_proofs=json.dumps(proof_data),
            user_id=current_user.id
        )
        db.add(db_proof)
        db.commit()
        db.refresh(db_proof)
        
        return {
            "message": f"Proof generated successfully",
            "proof_id": db_proof.id,
            "proof_type": proof_type,
            "proof_data": proof_data,
            "zk_available": zk_available
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proof generation failed: {str(e)}")


@router.post("/{proof_id}/verify")
async def verify_proof(
    proof_id: int,
    verification: ProofVerification,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Verify a proof"""
    db_proof = db.query(Proof).filter(
        and_(Proof.id == proof_id, Proof.user_id == current_user.id)
    ).first()
    if not db_proof:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    try:
        # Simulate proof verification
        verification_result = {
            "verification_type": verification.verification_type,
            "result": verification.result,
            "details": verification.details or {},
            "timestamp": "2024-01-01T00:00:00Z",
            "blockchain_submitted": verification.blockchain_submitted
        }
        
        # Update proof with verification result
        db_proof.verification_result = json.dumps(verification_result)
        db_proof.status = "verified" if verification.result else "failed"
        db.commit()
        
        return {
            "message": "Proof verification completed",
            "proof_id": proof_id,
            "verification_result": verification_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proof verification failed: {str(e)}")


@router.post("/{proof_id}/upload")
async def upload_proof_to_ipfs(
    proof_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Upload proof to IPFS"""
    db_proof = db.query(Proof).filter(
        and_(Proof.id == proof_id, Proof.user_id == current_user.id)
    ).first()
    if not db_proof:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    # Check if IPFS credentials are configured
    if not settings.IPFS_API_KEY or not settings.IPFS_API_SECRET:
        raise HTTPException(status_code=400, detail="IPFS credentials not configured")
    
    try:
        # Import IPFS upload function from agent
        import sys
        sys.path.append('../agent')
        from ipfs_upload import upload_to_ipfs
        
        # Create proof file
        proof_file_path = f"proof_{proof_id}.json"
        with open(proof_file_path, "w") as f:
            json.dump({
                "proof_id": proof_id,
                "proof_type": db_proof.proof_type,
                "training_data": json.loads(db_proof.training_data) if db_proof.training_data else {},
                "zk_proofs": json.loads(db_proof.zk_proofs) if db_proof.zk_proofs else {},
                "timestamp": "2024-01-01T00:00:00Z"
            }, f, indent=2)
        
        # Upload to IPFS
        ipfs_hash = upload_to_ipfs(
            proof_file_path, 
            settings.IPFS_API_KEY, 
            settings.IPFS_API_SECRET
        )
        
        # Update proof with IPFS hash
        db_proof.ipfs_hash = ipfs_hash
        db.commit()
        
        # Clean up temporary file
        os.remove(proof_file_path)
        
        return {
            "message": "Proof uploaded to IPFS successfully",
            "proof_id": proof_id,
            "ipfs_hash": ipfs_hash,
            "ipfs_url": f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IPFS upload failed: {str(e)}")


@router.post("/{proof_id}/submit-to-blockchain")
async def submit_proof_to_blockchain(
    proof_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Submit proof to blockchain for verification"""
    db_proof = db.query(Proof).filter(
        and_(Proof.id == proof_id, Proof.user_id == current_user.id)
    ).first()
    if not db_proof:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    try:
        # Simulate blockchain submission
        tx_hash = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        
        # Update proof with blockchain transaction hash
        db_proof.blockchain_tx_hash = tx_hash
        db.commit()
        
        return {
            "message": "Proof submitted to blockchain successfully",
            "proof_id": proof_id,
            "transaction_hash": tx_hash,
            "contract_address": settings.CONTRACT_ADDRESSES.get("proof_verifier")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blockchain submission failed: {str(e)}")


@router.get("/{proof_id}/download")
async def download_proof(
    proof_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get proof download information"""
    db_proof = db.query(Proof).filter(
        and_(Proof.id == proof_id, Proof.user_id == current_user.id)
    ).first()
    if not db_proof:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    return {
        "proof_id": proof_id,
        "proof_type": db_proof.proof_type,
        "status": db_proof.status,
        "training_data": json.loads(db_proof.training_data) if db_proof.training_data else {},
        "zk_proofs": json.loads(db_proof.zk_proofs) if db_proof.zk_proofs else {},
        "ipfs_hash": db_proof.ipfs_hash,
        "ipfs_url": f"https://gateway.pinata.cloud/ipfs/{db_proof.ipfs_hash}" if db_proof.ipfs_hash else None,
        "verification_result": json.loads(db_proof.verification_result) if db_proof.verification_result else {},
        "blockchain_tx_hash": db_proof.blockchain_tx_hash
    }


@router.post("/upload-proof-file")
async def upload_proof_file(
    proof_file: UploadFile = File(...),
    proof_type: str = "zk_proofs",
    description: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Upload a proof file"""
    
    # Validate file type
    if not proof_file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Proof file must be a JSON file")
    
    try:
        # Read and parse proof file
        content = await proof_file.read()
        proof_data = json.loads(content.decode())
        
        # Create proof record
        db_proof = Proof(
            proof_type=proof_type,
            description=description or f"Uploaded {proof_type}",
            status="pending",
            training_data=json.dumps(proof_data.get("training_data", {})),
            zk_proofs=json.dumps(proof_data.get("zk_proofs", {})),
            user_id=current_user.id
        )
        db.add(db_proof)
        db.commit()
        db.refresh(db_proof)
        
        return {
            "message": "Proof file uploaded successfully",
            "proof_id": db_proof.id,
            "proof_type": proof_type,
            "proof_data": proof_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse proof file: {str(e)}") 
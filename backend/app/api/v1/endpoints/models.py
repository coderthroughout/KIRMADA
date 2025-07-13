"""
Model endpoints for Aztec Protocol Backend
"""

import json
import os
import shutil
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.model import Model
from app.schemas.model import ModelCreate, ModelUpdate, ModelResponse, TrainingStats, ModelUpload
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=List[ModelResponse])
async def list_models(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """List all models for the current user"""
    models = db.query(Model).filter(
        Model.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return models


@router.post("/", response_model=ModelResponse)
async def create_model(
    model: ModelCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new model"""
    db_model = Model(
        name=model.name,
        description=model.description,
        model_type=model.model_type,
        architecture=model.architecture,
        parameters=model.parameters,
        file_size=model.file_size,
        ipfs_hash=model.ipfs_hash,
        accuracy=model.accuracy,
        loss=model.loss,
        training_config=json.dumps(model.training_config) if model.training_config else None,
        user_id=current_user.id
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get a specific model"""
    model = db.query(Model).filter(
        and_(Model.id == model_id, Model.user_id == current_user.id)
    ).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.put("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: int,
    model_update: ModelUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update a model"""
    db_model = db.query(Model).filter(
        and_(Model.id == model_id, Model.user_id == current_user.id)
    ).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    update_data = model_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "training_config" and value:
            setattr(db_model, field, json.dumps(value))
        else:
            setattr(db_model, field, value)
    
    db.commit()
    db.refresh(db_model)
    return db_model


@router.delete("/{model_id}")
async def delete_model(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete a model"""
    db_model = db.query(Model).filter(
        and_(Model.id == model_id, Model.user_id == current_user.id)
    ).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    db.delete(db_model)
    db.commit()
    return {"message": "Model deleted successfully"}


@router.post("/upload")
async def upload_model(
    name: str = Form(...),
    description: str = Form(None),
    model_type: str = Form(...),
    architecture: str = Form(None),
    model_file: UploadFile = File(...),
    training_stats_file: UploadFile = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Upload a model file with optional training stats"""
    
    # Validate file type
    allowed_extensions = ['.pt', '.pth', '.bin', '.safetensors', '.json']
    file_ext = os.path.splitext(model_file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Create upload directory
    upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save model file
    file_path = os.path.join(upload_dir, model_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(model_file.file, buffer)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Process training stats if provided
    training_config = None
    if training_stats_file:
        try:
            stats_content = await training_stats_file.read()
            training_stats = json.loads(stats_content.decode())
            training_config = training_stats
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid training stats file: {str(e)}")
    
    # Create model record
    db_model = Model(
        name=name,
        description=description,
        model_type=model_type,
        architecture=architecture,
        file_size=file_size,
        training_config=json.dumps(training_config) if training_config else None,
        status="uploaded",
        user_id=current_user.id
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    return {
        "message": "Model uploaded successfully",
        "model_id": db_model.id,
        "file_path": file_path,
        "file_size": file_size,
        "training_config": training_config
    }


@router.post("/{model_id}/upload-to-ipfs")
async def upload_model_to_ipfs(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Upload model to IPFS using Pinata"""
    db_model = db.query(Model).filter(
        and_(Model.id == model_id, Model.user_id == current_user.id)
    ).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Check if IPFS credentials are configured
    if not settings.IPFS_API_KEY or not settings.IPFS_API_SECRET:
        raise HTTPException(status_code=400, detail="IPFS credentials not configured")
    
    try:
        # Import IPFS upload function from agent
        import sys
        sys.path.append('../agent')
        from ipfs_upload import upload_to_ipfs
        
        # Find model file
        upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
        model_files = [f for f in os.listdir(upload_dir) if f.endswith(('.pt', '.pth', '.bin', '.safetensors'))]
        
        if not model_files:
            raise HTTPException(status_code=404, detail="No model files found")
        
        model_file_path = os.path.join(upload_dir, model_files[0])
        
        # Upload to IPFS
        ipfs_hash = upload_to_ipfs(
            model_file_path, 
            settings.IPFS_API_KEY, 
            settings.IPFS_API_SECRET
        )
        
        # Update model with IPFS hash
        db_model.ipfs_hash = ipfs_hash
        db_model.status = "ready"
        db.commit()
        
        return {
            "message": "Model uploaded to IPFS successfully",
            "model_id": model_id,
            "ipfs_hash": ipfs_hash,
            "ipfs_url": f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IPFS upload failed: {str(e)}")


@router.get("/{model_id}/download")
async def download_model(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get model download information"""
    db_model = db.query(Model).filter(
        and_(Model.id == model_id, Model.user_id == current_user.id)
    ).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Find model file
    upload_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.id))
    model_files = [f for f in os.listdir(upload_dir) if f.endswith(('.pt', '.pth', '.bin', '.safetensors'))]
    
    if not model_files:
        raise HTTPException(status_code=404, detail="Model file not found")
    
    model_file_path = os.path.join(upload_dir, model_files[0])
    
    return {
        "model_id": model_id,
        "name": db_model.name,
        "file_path": model_file_path,
        "file_size": db_model.file_size,
        "ipfs_hash": db_model.ipfs_hash,
        "ipfs_url": f"https://gateway.pinata.cloud/ipfs/{db_model.ipfs_hash}" if db_model.ipfs_hash else None,
        "training_config": json.loads(db_model.training_config) if db_model.training_config else None
    }


@router.get("/{model_id}/training-stats")
async def get_model_training_stats(
    model_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get model training statistics"""
    db_model = db.query(Model).filter(
        and_(Model.id == model_id, Model.user_id == current_user.id)
    ).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    training_config = json.loads(db_model.training_config) if db_model.training_config else {}
    
    return {
        "model_id": model_id,
        "name": db_model.name,
        "training_stats": training_config,
        "accuracy": db_model.accuracy,
        "loss": db_model.loss,
        "parameters": db_model.parameters,
        "file_size": db_model.file_size
    }


@router.post("/{model_id}/evaluate")
async def evaluate_model(
    model_id: int,
    evaluation_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Evaluate a model (simulated)"""
    db_model = db.query(Model).filter(
        and_(Model.id == model_id, Model.user_id == current_user.id)
    ).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Simulate model evaluation
    evaluation_result = {
        "model_id": model_id,
        "accuracy": 0.85,  # Simulated accuracy
        "loss": 0.15,      # Simulated loss
        "precision": 0.87,
        "recall": 0.83,
        "f1_score": 0.85,
        "evaluation_data": evaluation_data,
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    # Update model with evaluation results
    db_model.accuracy = evaluation_result["accuracy"]
    db_model.loss = evaluation_result["loss"]
    db.commit()
    
    return evaluation_result 
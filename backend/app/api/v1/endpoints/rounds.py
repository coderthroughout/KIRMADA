"""
Rounds endpoints for Aztec Protocol Backend
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/")
async def list_rounds(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """List all collaboration rounds"""
    return {"message": "Rounds endpoint - coming soon"}


@router.post("/")
async def create_round(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new collaboration round"""
    return {"message": "Create round - coming soon"}


@router.get("/{round_id}")
async def get_round(
    round_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get a specific round"""
    return {"message": f"Get round {round_id} - coming soon"}


@router.put("/{round_id}")
async def update_round(
    round_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update a round"""
    return {"message": f"Update round {round_id} - coming soon"} 
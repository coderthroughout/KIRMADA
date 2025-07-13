"""
Agent endpoints for Aztec Protocol Backend
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
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse, AgentConfig
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """List all agents for the current user"""
    agents = db.query(Agent).filter(
        Agent.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return agents


@router.post("/", response_model=AgentResponse)
async def create_agent(
    agent: AgentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new agent"""
    db_agent = Agent(
        name=agent.name,
        description=agent.description,
        agent_type=agent.agent_type,
        config=json.dumps(agent.dict()),
        user_id=current_user.id
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get a specific agent"""
    agent = db.query(Agent).filter(
        and_(Agent.id == agent_id, Agent.user_id == current_user.id)
    ).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    agent_update: AgentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update an agent"""
    db_agent = db.query(Agent).filter(
        and_(Agent.id == agent_id, Agent.user_id == current_user.id)
    ).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    update_data = agent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "config" and value:
            setattr(db_agent, field, json.dumps(value))
        else:
            setattr(db_agent, field, value)
    
    db.commit()
    db.refresh(db_agent)
    return db_agent


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete an agent"""
    db_agent = db.query(Agent).filter(
        and_(Agent.id == agent_id, Agent.user_id == current_user.id)
    ).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    db.delete(db_agent)
    db.commit()
    return {"message": "Agent deleted successfully"}


@router.post("/{agent_id}/start")
async def start_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Start an agent training round"""
    db_agent = db.query(Agent).filter(
        and_(Agent.id == agent_id, Agent.user_id == current_user.id)
    ).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update agent status
    db_agent.status = "training"
    db.commit()
    
    return {
        "message": "Agent training started",
        "agent_id": agent_id,
        "status": "training"
    }


@router.post("/{agent_id}/stop")
async def stop_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Stop an agent training round"""
    db_agent = db.query(Agent).filter(
        and_(Agent.id == agent_id, Agent.user_id == current_user.id)
    ).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update agent status
    db_agent.status = "idle"
    db.commit()
    
    return {
        "message": "Agent training stopped",
        "agent_id": agent_id,
        "status": "idle"
    }


@router.get("/{agent_id}/status")
async def get_agent_status(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get agent status and performance metrics"""
    db_agent = db.query(Agent).filter(
        and_(Agent.id == agent_id, Agent.user_id == current_user.id)
    ).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    config = json.loads(db_agent.config) if db_agent.config else {}
    performance = json.loads(db_agent.performance_metrics) if db_agent.performance_metrics else {}
    
    return {
        "agent_id": agent_id,
        "name": db_agent.name,
        "status": db_agent.status,
        "agent_type": db_agent.agent_type,
        "config": config,
        "performance_metrics": performance,
        "created_at": db_agent.created_at,
        "updated_at": db_agent.updated_at
    }


@router.post("/{agent_id}/config")
async def update_agent_config(
    agent_id: int,
    config: AgentConfig,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update agent configuration"""
    db_agent = db.query(Agent).filter(
        and_(Agent.id == agent_id, Agent.user_id == current_user.id)
    ).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update agent config
    db_agent.config = json.dumps(config.dict())
    db.commit()
    
    return {
        "message": "Agent configuration updated",
        "agent_id": agent_id,
        "config": config.dict()
    }


@router.post("/{agent_id}/upload-config")
async def upload_agent_config(
    agent_id: int,
    config_file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Upload agent configuration file (aztec-agent.toml)"""
    db_agent = db.query(Agent).filter(
        and_(Agent.id == agent_id, Agent.user_id == current_user.id)
    ).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if not config_file.filename.endswith('.toml'):
        raise HTTPException(status_code=400, detail="Configuration file must be a .toml file")
    
    try:
        # Read and parse TOML config
        content = await config_file.read()
        import tomllib
        config_data = tomllib.loads(content.decode())
        
        # Extract agent config
        if "agent" not in config_data:
            raise HTTPException(status_code=400, detail="Invalid configuration file: missing [agent] section")
        
        agent_config = config_data["agent"]
        
        # Update agent config
        db_agent.config = json.dumps(agent_config)
        db_agent.name = agent_config.get("agent_name", db_agent.name)
        db.commit()
        
        return {
            "message": "Agent configuration uploaded successfully",
            "agent_id": agent_id,
            "config": agent_config
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse configuration file: {str(e)}")


@router.get("/{agent_id}/logs")
async def get_agent_logs(
    agent_id: int,
    lines: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get agent logs (simulated)"""
    db_agent = db.query(Agent).filter(
        and_(Agent.id == agent_id, Agent.user_id == current_user.id)
    ).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Simulate log retrieval
    logs = [
        f"[{db_agent.updated_at}] Agent {db_agent.name} status: {db_agent.status}",
        f"[{db_agent.updated_at}] Training round completed",
        f"[{db_agent.updated_at}] Model diff saved",
        f"[{db_agent.updated_at}] Proof generated",
        f"[{db_agent.updated_at}] IPFS upload completed"
    ]
    
    return {
        "agent_id": agent_id,
        "logs": logs[-lines:],
        "total_lines": len(logs)
    } 
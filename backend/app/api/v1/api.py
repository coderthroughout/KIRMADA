"""
Main API router for Aztec Protocol Backend
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, agents, models, proofs, rounds, blockchain, ipfs

api_router = APIRouter()

# Test endpoint to verify router is working
@api_router.get("/")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Aztec Protocol API v1",
        "endpoints": {
            "auth": "/auth",
            "agents": "/agents", 
            "models": "/models",
            "proofs": "/proofs",
            "rounds": "/rounds",
            "blockchain": "/blockchain",
            "ipfs": "/ipfs"
        }
    }

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(proofs.router, prefix="/proofs", tags=["proofs"])
api_router.include_router(rounds.router, prefix="/rounds", tags=["rounds"])
api_router.include_router(blockchain.router, prefix="/blockchain", tags=["blockchain"])
api_router.include_router(ipfs.router, prefix="/ipfs", tags=["ipfs"]) 
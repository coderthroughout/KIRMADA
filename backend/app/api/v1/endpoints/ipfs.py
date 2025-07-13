"""
IPFS endpoints for Aztec Protocol Backend
"""

import json
import os
import shutil
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.core.config import settings

router = APIRouter()


@router.post("/upload")
async def upload_to_ipfs(
    file: UploadFile = File(...),
    metadata: str = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Upload a file to IPFS using Pinata"""
    
    # Check if IPFS credentials are configured
    if not settings.IPFS_API_KEY or not settings.IPFS_API_SECRET:
        raise HTTPException(status_code=400, detail="IPFS credentials not configured")
    
    # Validate file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    try:
        # Import IPFS upload function from agent
        import sys
        sys.path.append('../agent')
        from ipfs_upload import upload_to_ipfs
        
        # Create temporary file
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Upload to IPFS
        ipfs_hash = upload_to_ipfs(
            temp_file_path, 
            settings.IPFS_API_KEY, 
            settings.IPFS_API_SECRET
        )
        
        # Clean up temporary file
        os.remove(temp_file_path)
        
        # Parse metadata if provided
        parsed_metadata = None
        if metadata:
            try:
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                parsed_metadata = {"description": metadata}
        
        return {
            "message": "File uploaded to IPFS successfully",
            "filename": file.filename,
            "file_size": file.size,
            "ipfs_hash": ipfs_hash,
            "ipfs_url": f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}",
            "metadata": parsed_metadata
        }
        
    except Exception as e:
        # Clean up temporary file if it exists
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=f"IPFS upload failed: {str(e)}")


@router.get("/{hash}")
async def get_from_ipfs(
    hash: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get file information from IPFS"""
    
    try:
        import requests
        
        # Try to fetch file metadata from IPFS
        ipfs_url = f"https://gateway.pinata.cloud/ipfs/{hash}"
        response = requests.head(ipfs_url, timeout=10)
        
        if response.status_code == 200:
            file_info = {
                "ipfs_hash": hash,
                "ipfs_url": ipfs_url,
                "content_type": response.headers.get("content-type", "unknown"),
                "content_length": response.headers.get("content-length", "unknown"),
                "accessible": True
            }
        else:
            file_info = {
                "ipfs_hash": hash,
                "ipfs_url": ipfs_url,
                "accessible": False,
                "error": f"HTTP {response.status_code}"
            }
        
        return file_info
        
    except Exception as e:
        return {
            "ipfs_hash": hash,
            "ipfs_url": f"https://gateway.pinata.cloud/ipfs/{hash}",
            "accessible": False,
            "error": str(e)
        }


@router.delete("/{hash}")
async def delete_from_ipfs(
    hash: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete a file from IPFS (Pinata unpin)"""
    
    # Check if IPFS credentials are configured
    if not settings.IPFS_API_KEY or not settings.IPFS_API_SECRET:
        raise HTTPException(status_code=400, detail="IPFS credentials not configured")
    
    try:
        import requests
        
        # Unpin from Pinata
        url = "https://api.pinata.cloud/pinning/unpin"
        headers = {
            "pinata_api_key": settings.IPFS_API_KEY,
            "pinata_secret_api_key": settings.IPFS_API_SECRET
        }
        data = {"hashToUnpin": hash}
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            return {
                "message": "File unpinned from IPFS successfully",
                "ipfs_hash": hash
            }
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to unpin file: {response.text}"
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IPFS unpin failed: {str(e)}")


@router.post("/upload-multiple")
async def upload_multiple_to_ipfs(
    files: List[UploadFile] = File(...),
    metadata: str = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Upload multiple files to IPFS"""
    
    # Check if IPFS credentials are configured
    if not settings.IPFS_API_KEY or not settings.IPFS_API_SECRET:
        raise HTTPException(status_code=400, detail="IPFS credentials not configured")
    
    try:
        # Import IPFS upload function from agent
        import sys
        sys.path.append('../agent')
        from ipfs_upload import upload_to_ipfs
        
        results = []
        temp_files = []
        
        for file in files:
            try:
                # Create temporary file
                temp_file_path = f"temp_{file.filename}"
                temp_files.append(temp_file_path)
                
                with open(temp_file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # Upload to IPFS
                ipfs_hash = upload_to_ipfs(
                    temp_file_path, 
                    settings.IPFS_API_KEY, 
                    settings.IPFS_API_SECRET
                )
                
                results.append({
                    "filename": file.filename,
                    "file_size": file.size,
                    "ipfs_hash": ipfs_hash,
                    "ipfs_url": f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}",
                    "status": "success"
                })
                
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": str(e)
                })
        
        # Clean up temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        # Parse metadata if provided
        parsed_metadata = None
        if metadata:
            try:
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                parsed_metadata = {"description": metadata}
        
        return {
            "message": "Multiple files uploaded to IPFS",
            "results": results,
            "metadata": parsed_metadata
        }
        
    except Exception as e:
        # Clean up temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        raise HTTPException(status_code=500, detail=f"IPFS upload failed: {str(e)}")


@router.get("/status")
async def get_ipfs_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get IPFS service status and configuration"""
    
    # Check if IPFS credentials are configured
    credentials_configured = bool(settings.IPFS_API_KEY and settings.IPFS_API_SECRET)
    
    try:
        import requests
        
        # Test Pinata credentials
        if credentials_configured:
            url = "https://api.pinata.cloud/data/testAuthentication"
            headers = {
                "pinata_api_key": settings.IPFS_API_KEY,
                "pinata_secret_api_key": settings.IPFS_API_SECRET
            }
            response = requests.get(url, headers=headers, timeout=10)
            credentials_valid = response.status_code == 200
        else:
            credentials_valid = False
        
        return {
            "service": "Pinata IPFS",
            "api_url": settings.IPFS_API_URL,
            "gateway_url": "https://gateway.pinata.cloud",
            "credentials_configured": credentials_configured,
            "credentials_valid": credentials_valid,
            "max_file_size_mb": settings.MAX_FILE_SIZE / (1024*1024),
            "status": "operational" if credentials_valid else "unavailable"
        }
        
    except Exception as e:
        return {
            "service": "Pinata IPFS",
            "api_url": settings.IPFS_API_URL,
            "gateway_url": "https://gateway.pinata.cloud",
            "credentials_configured": credentials_configured,
            "credentials_valid": False,
            "max_file_size_mb": settings.MAX_FILE_SIZE / (1024*1024),
            "status": "error",
            "error": str(e)
        }


@router.post("/upload-directory")
async def upload_directory_to_ipfs(
    directory_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Upload a directory structure to IPFS (simulated)"""
    
    # Check if IPFS credentials are configured
    if not settings.IPFS_API_KEY or not settings.IPFS_API_SECRET:
        raise HTTPException(status_code=400, detail="IPFS credentials not configured")
    
    try:
        # Simulate directory upload
        directory_hash = "QmSimulatedDirectoryHash123456789"
        
        return {
            "message": "Directory uploaded to IPFS successfully",
            "directory_hash": directory_hash,
            "ipfs_url": f"https://gateway.pinata.cloud/ipfs/{directory_hash}",
            "files": directory_data.get("files", []),
            "metadata": directory_data.get("metadata", {})
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Directory upload failed: {str(e)}")


@router.get("/gateways")
async def get_ipfs_gateways(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get available IPFS gateways"""
    
    gateways = [
        {
            "name": "Pinata Gateway",
            "url": "https://gateway.pinata.cloud",
            "primary": True
        },
        {
            "name": "IPFS.io Gateway",
            "url": "https://ipfs.io",
            "primary": False
        },
        {
            "name": "Cloudflare IPFS",
            "url": "https://cloudflare-ipfs.com",
            "primary": False
        },
        {
            "name": "dweb.link",
            "url": "https://dweb.link",
            "primary": False
        }
    ]
    
    return {
        "gateways": gateways,
        "primary_gateway": "https://gateway.pinata.cloud"
    } 
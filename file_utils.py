import os
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
import aiofiles
from typing import Optional
import uuid

# Configuration
UPLOAD_DIR = "uploads"
OFFICIAL_DIR = "uploads/official"
RESEARCHER_DIR = "uploads/researcher"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".pdf"}

def create_upload_directories():
    """Create upload directories if they don't exist."""
    for directory in [UPLOAD_DIR, OFFICIAL_DIR, RESEARCHER_DIR]:
        Path(directory).mkdir(parents=True, exist_ok=True)

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    
    # Check file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Only {', '.join(ALLOWED_EXTENSIONS)} files are allowed."
        )
    
    # Check file size (FastAPI doesn't provide size directly, so we'll check during save)
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB."
        )

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename to avoid conflicts."""
    file_extension = Path(original_filename).suffix.lower()
    unique_name = f"{uuid.uuid4()}{file_extension}"
    return unique_name

async def save_uploaded_file(
    file: UploadFile, 
    is_official: bool = False,
    custom_filename: Optional[str] = None
) -> tuple[str, str, int]:
    """
    Save uploaded file to appropriate directory.
    
    Returns:
        tuple: (file_path, filename, file_size)
    """
    
    # Validate file
    validate_file(file)
    
    # Create directories if they don't exist
    create_upload_directories()
    
    # Determine save directory and filename
    if is_official:
        save_dir = OFFICIAL_DIR
    else:
        save_dir = RESEARCHER_DIR
    
    if custom_filename:
        filename = custom_filename
    else:
        filename = generate_unique_filename(file.filename)
    
    file_path = os.path.join(save_dir, filename)
    
    # Save file
    file_size = 0
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(8192):  # Read in 8KB chunks
                file_size += len(chunk)
                
                # Check file size during upload
                if file_size > MAX_FILE_SIZE:
                    # Remove partial file
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB."
                    )
                
                await f.write(chunk)
    
    except Exception as e:
        # Clean up partial file if upload failed
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    return file_path, filename, file_size

def delete_file(file_path: str) -> bool:
    """Delete a file from the filesystem."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False

def get_file_info(file_path: str) -> Optional[dict]:
    """Get file information."""
    try:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            return {
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "exists": True
            }
        return {"exists": False}
    except Exception:
        return {"exists": False}

def ensure_file_exists(file_path: str) -> bool:
    """Check if file exists and is accessible."""
    return os.path.exists(file_path) and os.path.isfile(file_path)
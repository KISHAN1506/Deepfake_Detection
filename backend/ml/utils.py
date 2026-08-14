"""
Utility functions for file handling, hashing, and common operations.
"""

import logging
import hashlib
import os
from pathlib import Path
from typing import Tuple
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


def calculate_sha256(file_path: str) -> str:
    """
    Calculate SHA-256 hash of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        SHA-256 hash as hexadecimal string
    """
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Failed to calculate SHA-256: {e}")
        return ""


def generate_analysis_id() -> str:
    """
    Generate a unique analysis ID.
    
    Returns:
        Unique ID string
    """
    return str(uuid.uuid4())


def create_analysis_directory(uploads_root: str) -> Tuple[str, str]:
    """
    Create a unique directory for an analysis.
    
    Args:
        uploads_root: Root uploads directory
        
    Returns:
        Tuple of (analysis_id, analysis_directory_path)
    """
    analysis_id = generate_analysis_id()
    analysis_dir = os.path.join(uploads_root, analysis_id)
    
    try:
        Path(analysis_dir).mkdir(parents=True, exist_ok=True)
        # Create subdirectories
        Path(os.path.join(analysis_dir, "original")).mkdir(exist_ok=True)
        Path(os.path.join(analysis_dir, "frames")).mkdir(exist_ok=True)
        Path(os.path.join(analysis_dir, "faces")).mkdir(exist_ok=True)
        return analysis_id, analysis_dir
    except Exception as e:
        logger.error(f"Failed to create analysis directory: {e}")
        return analysis_id, None


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in MB
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except Exception as e:
        logger.error(f"Failed to get file size: {e}")
        return 0.0


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat() + "Z"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "1:23.45")
    """
    minutes = int(seconds) // 60
    secs = seconds % 60
    return f"{minutes}:{secs:05.2f}"


def save_cv2_image(image, output_path: str) -> bool:
    """
    Save an OpenCV image to file.
    
    Args:
        image: OpenCV image (BGR format)
        output_path: Path to save the image
        
    Returns:
        True if successful, False otherwise
    """
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(output_path, image)
        return True
    except Exception as e:
        logger.error(f"Failed to save image: {e}")
        return False


def cleanup_analysis_directory(analysis_dir: str, keep_originals: bool = True) -> None:
    """
    Cleanup temporary files from analysis directory.
    
    Args:
        analysis_dir: Analysis directory path
        keep_originals: Whether to keep original uploaded files
    """
    try:
        if not keep_originals:
            original_dir = os.path.join(analysis_dir, "original")
            if os.path.exists(original_dir):
                import shutil
                shutil.rmtree(original_dir)
        
        logger.info(f"Cleanup complete for {analysis_dir}")
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")


# Import cv2 here for use in this module
try:
    import cv2
except ImportError:
    logger.warning("OpenCV not yet imported in utils")

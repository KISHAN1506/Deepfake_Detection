"""
Image preprocessing module.
Handles image loading, validation, and preprocessing for EfficientNet-B0.
"""

import logging
from pathlib import Path
from PIL import Image
import torch
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


def load_image(image_path: str) -> Optional[Image.Image]:
    """
    Load an image from file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        PIL Image or None if loading fails
    """
    try:
        image = Image.open(image_path)
        # Convert to RGB if needed (handles RGBA, grayscale, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image
    except Exception as e:
        logger.error(f"Failed to load image {image_path}: {e}")
        return None


def preprocess_image(pil_image: Image.Image, processor) -> Optional[torch.Tensor]:
    """
    Preprocess a PIL image for EfficientNet-B0 inference.
    
    Args:
        pil_image: PIL Image object
        processor: EfficientNetImageProcessor from transformers
        
    Returns:
        Preprocessed tensor with batch dimension, or None if preprocessing fails
    """
    try:
        # Use the official processor from transformers
        # It handles resizing, normalization, and tensor conversion
        inputs = processor(pil_image, return_tensors="pt")
        return inputs['pixel_values']
    except Exception as e:
        logger.error(f"Failed to preprocess image: {e}")
        return None


def validate_image_file(file_path: str, max_size: int = 50 * 1024 * 1024) -> Tuple[bool, str]:
    """
    Validate an image file.
    
    Args:
        file_path: Path to the image file
        max_size: Maximum file size in bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(file_path)
    
    # Check if file exists
    if not path.exists():
        return False, f"File not found: {file_path}"
    
    # Check file extension
    supported_formats = {'.jpg', '.jpeg', '.png', '.webp'}
    if path.suffix.lower() not in supported_formats:
        return False, f"Unsupported image format: {path.suffix}. Supported: {supported_formats}"
    
    # Check file size
    file_size = path.stat().st_size
    if file_size > max_size:
        return False, f"File too large: {file_size} bytes (max: {max_size})"
    
    if file_size == 0:
        return False, "File is empty"
    
    # Try to open and verify it's a valid image
    try:
        img = Image.open(file_path)
        img.verify()
        return True, ""
    except Exception as e:
        return False, f"Invalid or corrupted image: {e}"


def get_image_metadata(image_path: str) -> dict:
    """
    Extract metadata from an image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with metadata
    """
    try:
        image = Image.open(image_path)
        metadata = {
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode
        }
        
        # Try to extract EXIF data if available
        try:
            exif_data = image._getexif()
            if exif_data:
                # Just indicate EXIF presence; don't extract all details
                metadata["has_exif"] = True
        except:
            metadata["has_exif"] = False
        
        return metadata
    except Exception as e:
        logger.error(f"Failed to extract image metadata: {e}")
        return {"error": str(e)}

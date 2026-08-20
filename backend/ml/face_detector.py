"""
Face detection module.
Handles face detection and cropping for deepfake analysis.
Supports both OpenCV and PIL fallback modes.
"""

import logging
from typing import List, Tuple, Optional
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def detect_faces_pil_fallback(image_path: str) -> Tuple[Optional[np.ndarray], List[Tuple[int, int, int, int]]]:
    """
    Simple face detection fallback using PIL.
    In production, would use OpenCV. For MVP, returns empty list to use full image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple of (image_array, list of bounding boxes as (x, y, w, h))
    """
    try:
        pil_image = Image.open(image_path)
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        logger.info("Using PIL fallback - no face detection available")
        logger.info("Will use full image for analysis")
        
        # Convert PIL to numpy array (RGB format)
        image_array = np.array(pil_image)
        
        # Return empty faces list - fallback will use full image
        return image_array, []
    
    except Exception as e:
        logger.error(f"Failed to load image with PIL: {e}")
        return None, []


def detect_faces(image_path: str) -> Tuple[Optional[np.ndarray], List[Tuple[int, int, int, int]]]:
    """
    Detect faces in an image.
    Tries OpenCV first, falls back to PIL-only approach.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple of (image_array, list of bounding boxes as (x, y, w, h))
    """
    try:
        import cv2
        
        # Load image in OpenCV format
        image = cv2.imread(image_path)
        if image is None:
            logger.warning(f"Failed to load image with OpenCV: {image_path}")
            return detect_faces_pil_fallback(image_path)
        
        # Convert to grayscale for detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Load cascade classifier
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        cascade = cv2.CascadeClassifier(cascade_path)
        
        # Detect faces
        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=3,
            minSize=(30, 30)
        )
        
        if len(faces) == 0:
            logger.info("No faces detected - will use full image")
        else:
            logger.info(f"Detected {len(faces)} face(s) using OpenCV")
        
        return image, list(faces)
    
    except ImportError:
        logger.warning("OpenCV not available - using PIL fallback")
        return detect_faces_pil_fallback(image_path)
    
    except Exception as e:
        logger.error(f"Face detection failed: {e}")
        logger.warning("Falling back to full image analysis")
        return detect_faces_pil_fallback(image_path)


def crop_face(image: np.ndarray, face_bbox: Tuple[int, int, int, int], padding: float = 0.2) -> Optional[np.ndarray]:
    """
    Crop a face from an image.
    
    Args:
        image: Image array (BGR format from OpenCV)
        face_bbox: Bounding box as (x, y, w, h)
        padding: Padding ratio around the face
        
    Returns:
        Cropped face image or None if cropping fails
    """
    try:
        x, y, w, h = face_bbox
        
        # Add padding
        pad_x = int(w * padding / 2)
        pad_y = int(h * padding / 2)
        
        x1 = max(0, x - pad_x)
        y1 = max(0, y - pad_y)
        x2 = min(image.shape[1], x + w + pad_x)
        y2 = min(image.shape[0], y + h + pad_y)
        
        face_crop = image[y1:y2, x1:x2]
        return face_crop
    
    except Exception as e:
        logger.error(f"Face cropping failed: {e}")
        return None


def get_largest_face(faces: List[Tuple[int, int, int, int]]) -> Optional[Tuple[int, int, int, int]]:
    """Get the largest face from a list of detected faces."""
    if not faces:
        return None
    
    largest = max(faces, key=lambda f: f[2] * f[3])
    return largest


def faces_to_normalized_bboxes(faces: List[Tuple[int, int, int, int]], image_shape: Tuple[int, int]) -> List[dict]:
    """Convert face bounding boxes to normalized format."""
    height, width = image_shape
    bboxes = []
    
    for x, y, w, h in faces:
        bbox = {
            "x": x / width,
            "y": y / height,
            "width": w / width,
            "height": h / height,
            "x1": x,
            "y1": y,
            "x2": x + w,
            "y2": y + h
        }
        bboxes.append(bbox)
    
    return bboxes

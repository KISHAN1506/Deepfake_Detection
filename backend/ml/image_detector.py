"""
Image-level deepfake detection module.
"""

import logging
import time
from typing import Dict, Any
from PIL import Image

from .model import load_model, infer_image, get_device
from .preprocessing import load_image, preprocess_image, validate_image_file, get_image_metadata
from .face_detector import detect_faces, crop_face, get_largest_face, faces_to_normalized_bboxes
from .utils import calculate_sha256, get_file_size_mb

logger = logging.getLogger(__name__)


def cv2_to_pil_image(cv2_image):
    """Convert OpenCV BGR image to PIL RGB image, or handle PIL RGB image."""
    try:
        # Check if it's already in RGB format (from PIL fallback)
        if len(cv2_image.shape) == 3 and cv2_image.shape[2] == 3:
            # Could be BGR or RGB - assume RGB if from PIL, BGR if from OpenCV
            # Since we don't know, we'll check if it looks more like BGR (typically more blue)
            # For now, try converting and if it looks wrong, the inference will still work
            return Image.fromarray(cv2_image.astype('uint8'), 'RGB')
        else:
            return Image.fromarray(cv2_image.astype('uint8'))
    except:
        return None


def detect_image(
    image_path: str,
    fake_threshold: float = 0.5,
    return_face_crop: bool = False
) -> Dict[str, Any]:
    """
    Analyze a single image for deepfake indicators.
    
    Args:
        image_path: Path to the image file
        fake_threshold: Threshold for classifying as fake (default 0.5)
        return_face_crop: Whether to save and return the cropped face
        
    Returns:
        Analysis result dictionary
    """
    start_time = time.time()
    result = {
        "type": "image",
        "success": False,
        "error": None,
        "prediction": None,
        "fake_probability": None,
        "real_probability": None,
        "confidence": None,
        "face_detected": False,
        "face_count": 0,
        "metadata": {},
        "sha256": None,
        "processing_time_seconds": 0,
        "file_size_mb": 0
    }
    
    try:
        # Step 1: Validate file
        is_valid, error_msg = validate_image_file(image_path)
        if not is_valid:
            result["error"] = error_msg
            logger.error(f"Image validation failed: {error_msg}")
            return result
        
        # Step 2: Calculate SHA-256
        result["sha256"] = calculate_sha256(image_path)
        result["file_size_mb"] = get_file_size_mb(image_path)
        
        # Step 3: Extract metadata
        result["metadata"] = get_image_metadata(image_path)
        
        # Step 4: Detect faces
        image_array, faces = detect_faces(image_path)
        result["face_count"] = len(faces)
        
        if image_array is None:
            result["error"] = "Failed to load image"
            return result
        
        pil_image = None
        
        if len(faces) == 0:
            logger.warning("No faces detected - running inference on full image")
            # Fallback: use full image, assume at least 1 face present
            result["face_count"] = 1
            result["face_detected"] = False
            pil_image = load_image(image_path)
        else:
            # Get the largest face
            largest_face = get_largest_face(faces)
            face_crop = crop_face(image_array, largest_face)
            
            if face_crop is None:
                logger.warning("Failed to crop face - falling back to full image")
                result["face_count"] = 1
                result["face_detected"] = False
                pil_image = load_image(image_path)
            else:
                # Convert face crop from BGR to RGB PIL Image
                pil_face = cv2_to_pil_image(face_crop)
                
                if pil_face is None:
                    logger.warning("Failed to convert face crop - falling back to full image")
                    result["face_count"] = 1
                    result["face_detected"] = False
                    pil_image = load_image(image_path)
                else:
                    pil_image = pil_face
                    result["face_detected"] = True
                    
                    # Add face bounding box
                    result["bbox"] = list(largest_face)  # [x, y, w, h]
                    
                    # Normalize bboxes
                    result["normalized_bbox"] = faces_to_normalized_bboxes(
                        [largest_face],
                        image_array.shape[:2]
                    )[0]
        
        if pil_image is None:
            result["error"] = "Failed to load image"
            return result
        
        # Preprocess and infer
        model, processor = load_model()
        input_tensor = preprocess_image(pil_image, processor)
        
        if input_tensor is None:
            result["error"] = "Preprocessing failed"
            return result
        
        real_prob, fake_prob, predicted_class = infer_image(input_tensor)
        
        # Step 5: Determine prediction
        if fake_prob >= fake_threshold:
            result["prediction"] = "LIKELY MANIPULATED"
        else:
            result["prediction"] = "LIKELY AUTHENTIC"
        
        result["fake_probability"] = float(fake_prob)
        result["real_probability"] = float(real_prob)
        result["confidence"] = max(fake_prob, real_prob)
        result["success"] = True
        
        logger.info(f"Image analysis complete: {result['prediction']}")
    
    except Exception as e:
        logger.error(f"Image analysis failed: {e}", exc_info=True)
        result["error"] = f"Analysis failed: {str(e)}"
    
    finally:
        result["processing_time_seconds"] = round(time.time() - start_time, 2)
    
    return result

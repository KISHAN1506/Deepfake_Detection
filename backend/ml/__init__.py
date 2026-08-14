"""
ML module for deepfake detection.
Contains model loading, preprocessing, face detection, and inference code.
"""

from .model import load_model, infer_image, get_device, get_model_info
from .preprocessing import load_image, preprocess_image, validate_image_file, get_image_metadata
from .face_detector import detect_faces, crop_face, get_largest_face
from .image_detector import detect_image
from .video_detector import detect_video, validate_video_file, get_video_metadata
from .utils import calculate_sha256, generate_analysis_id, create_analysis_directory

__all__ = [
    "load_model",
    "infer_image",
    "get_device",
    "get_model_info",
    "load_image",
    "preprocess_image",
    "validate_image_file",
    "get_image_metadata",
    "detect_faces",
    "crop_face",
    "get_largest_face",
    "detect_image",
    "detect_video",
    "validate_video_file",
    "get_video_metadata",
    "calculate_sha256",
    "generate_analysis_id",
    "create_analysis_directory",
]

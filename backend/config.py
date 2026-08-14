"""
Configuration for the deepfake detection system.
Centralized settings for model, thresholds, and file handling.
"""

import os
from pathlib import Path

# ==================== DIRECTORIES ====================
PROJECT_ROOT = Path(__file__).parent.parent
UPLOADS_DIR = PROJECT_ROOT / "uploads"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
UPLOADS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ==================== MODEL CONFIGURATION ====================
# EfficientNet-B0 model from Hugging Face
MODEL_NAME = "google/efficientnet-b0"
DEVICE = "cuda" if os.environ.get("FORCE_CPU") != "1" else "cpu"

# Model input configuration
MODEL_INPUT_SIZE = 224  # EfficientNet-B0 standard input size
MODEL_MEAN = [0.485, 0.456, 0.406]
MODEL_STD = [0.229, 0.224, 0.225]

# For deepfake detection, we'll use a binary classification approach
# Class 0 = REAL (authentic), Class 1 = FAKE (manipulated)
CLASS_LABELS = {
    0: "REAL",
    1: "FAKE"
}

# ==================== DETECTION THRESHOLDS ====================
# Image-level threshold
IMAGE_FAKE_THRESHOLD = 0.5

# Video-level thresholds
VIDEO_FAKE_THRESHOLD = 0.5
SUSPICIOUS_FRAME_THRESHOLD = 0.6

# ==================== VIDEO PROCESSING ====================
# Number of frames to sample from video
DEFAULT_VIDEO_SAMPLE_FRAMES = 16

# Supported video formats
SUPPORTED_VIDEO_FORMATS = {".mp4", ".mov", ".avi", ".mkv"}

# ==================== IMAGE PROCESSING ====================
# Supported image formats
SUPPORTED_IMAGE_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}

# ==================== FILE VALIDATION ====================
# Maximum file sizes (in bytes)
MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500 MB

# ==================== FACE DETECTION ====================
# Face detection cascade file (OpenCV) - loaded dynamically
# FACE_CASCADE_PATH will be set at runtime
MIN_FACE_SIZE = (30, 30)

# ==================== PROCESSING TIMEOUTS ====================
# Maximum time for processing a single image (seconds)
IMAGE_PROCESSING_TIMEOUT = 60

# Maximum time for processing a video (seconds)
VIDEO_PROCESSING_TIMEOUT = 300

# ==================== LOGGING ====================
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ==================== API CONFIGURATION ====================
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("API_PORT", 8000))
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173", "*"]

# ==================== DISCLAIMER ====================
ANALYSIS_DISCLAIMER = (
    "This AI assessment is not definitive proof of authenticity. "
    "It is a forensic analysis tool to assist in detection of potential deepfakes. "
    "Always consult experts for critical decisions."
)

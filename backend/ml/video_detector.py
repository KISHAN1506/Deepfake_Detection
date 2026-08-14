"""
Video-level deepfake detection module.
"""

import logging
import time
from typing import List, Dict, Any, Optional
import numpy as np
from PIL import Image

from .model import load_model, infer_image
from .preprocessing import preprocess_image
from .face_detector import detect_faces, crop_face, get_largest_face
from .utils import calculate_sha256, get_file_size_mb, format_duration

logger = logging.getLogger(__name__)


def validate_video_file(video_path: str, max_size: int = 500 * 1024 * 1024) -> tuple:
    """
    Validate a video file.
    
    Args:
        video_path: Path to video file
        max_size: Maximum file size in bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    from pathlib import Path
    
    path = Path(video_path)
    
    if not path.exists():
        return False, f"File not found: {video_path}"
    
    supported_formats = {'.mp4', '.mov', '.avi', '.mkv'}
    if path.suffix.lower() not in supported_formats:
        return False, f"Unsupported video format: {path.suffix}. Supported: {supported_formats}"
    
    file_size = path.stat().st_size
    if file_size > max_size:
        return False, f"File too large: {file_size} bytes (max: {max_size})"
    
    if file_size == 0:
        return False, "File is empty"
    
    # Try to open with OpenCV
    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return False, "Failed to open video"
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count <= 0:
            return False, "Video has no frames"
        
        cap.release()
        return True, ""
    except:
        # If OpenCV not available, assume valid
        logger.warning("OpenCV not available for video validation")
        return True, ""


def get_video_metadata(video_path: str) -> dict:
    """
    Extract metadata from a video file.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with metadata
    """
    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        
        metadata = {
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        }
        
        # Calculate duration
        if metadata["fps"] > 0:
            metadata["duration"] = metadata["frame_count"] / metadata["fps"]
        else:
            metadata["duration"] = 0
        
        cap.release()
        return metadata
    except Exception as e:
        logger.error(f"Failed to extract video metadata: {e}")
        return {"error": str(e)}


def sample_frames_from_video(
    video_path: str,
    num_frames: int = 16
) -> List[tuple]:
    """
    Sample evenly-spaced frames from a video.
    
    Args:
        video_path: Path to video file
        num_frames: Number of frames to sample
        
    Returns:
        List of tuples: (frame_number, frame_image, timestamp_seconds)
    """
    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if total_frames <= 0:
            logger.error("Cannot determine frame count")
            cap.release()
            return []
        
        # Calculate frame indices to sample
        if total_frames <= num_frames:
            # If video has fewer frames than requested, use all frames
            frame_indices = list(range(total_frames))
        else:
            # Sample evenly spaced frames
            frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int).tolist()
        
        sampled_frames = []
        
        for frame_idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if ret:
                timestamp = frame_idx / fps if fps > 0 else 0
                sampled_frames.append((frame_idx, frame, timestamp))
            else:
                logger.warning(f"Failed to read frame {frame_idx}")
        
        cap.release()
        return sampled_frames
    
    except Exception as e:
        logger.error(f"Frame sampling failed: {e}")
        return []


def cv2_to_pil_image(cv2_image):
    """Convert OpenCV BGR image to PIL RGB image."""
    try:
        rgb_image = cv2_image[:, :, ::-1]  # BGR to RGB
        return Image.fromarray(rgb_image)
    except:
        return None


def detect_video(
    video_path: str,
    num_frames: int = 16,
    fake_threshold: float = 0.6,
    suspicious_threshold: float = 0.6
) -> Dict[str, Any]:
    """
    Analyze a video for deepfake indicators.
    
    Args:
        video_path: Path to video file
        num_frames: Number of frames to sample
        fake_threshold: Threshold for video-level classification
        suspicious_threshold: Threshold for marking individual frames as suspicious
        
    Returns:
        Analysis result dictionary
    """
    start_time = time.time()
    result = {
        "type": "video",
        "success": False,
        "error": None,
        "prediction": None,
        "fake_probability": None,
        "confidence": None,
        "frames_analyzed": 0,
        "suspicious_frames": 0,
        "suspicious_frame_percentage": 0,
        "metadata": {},
        "frame_results": [],
        "top_suspicious_frames": [],
        "sha256": None,
        "processing_time_seconds": 0,
        "file_size_mb": 0
    }
    
    try:
        # Step 1: Validate file
        is_valid, error_msg = validate_video_file(video_path)
        if not is_valid:
            result["error"] = error_msg
            logger.error(f"Video validation failed: {error_msg}")
            return result
        
        # Step 2: Calculate SHA-256 and metadata
        result["sha256"] = calculate_sha256(video_path)
        result["file_size_mb"] = round(get_file_size_mb(video_path), 2)
        result["metadata"] = get_video_metadata(video_path)
        
        # Step 3: Sample frames
        sampled_frames = sample_frames_from_video(video_path, num_frames)
        result["frames_analyzed"] = len(sampled_frames)
        
        if len(sampled_frames) == 0:
            result["error"] = "Failed to sample frames from video"
            return result
        
        logger.info(f"Sampled {len(sampled_frames)} frames from video")
        
        # Step 4: Analyze each frame
        model, processor = load_model()
        fake_probabilities = []
        
        for frame_idx, frame_image, timestamp in sampled_frames:
            frame_result = {
                "frame_number": frame_idx,
                "timestamp": round(timestamp, 2),
                "fake_probability": None,
                "real_probability": None,
                "prediction": None,
                "face_detected": False
            }
            
            try:
                # Try to detect faces using OpenCV
                try:
                    import cv2
                    face_cascade = cv2.CascadeClassifier(
                        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                    )
                    gray = cv2.cvtColor(frame_image, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(30, 30),
                        maxSize=(400, 400)
                    )
                except:
                    faces = []
                
                if len(faces) == 0:
                    # Fallback: use full frame
                    pil_frame = cv2_to_pil_image(frame_image)
                    if pil_frame is None:
                        pil_frame = Image.fromarray(frame_image)
                else:
                    # Use largest face
                    largest_face = get_largest_face(list(faces))
                    face_crop = crop_face(frame_image, largest_face)
                    
                    if face_crop is None:
                        # Fallback to full frame
                        pil_frame = cv2_to_pil_image(frame_image)
                        if pil_frame is None:
                            pil_frame = Image.fromarray(frame_image)
                    else:
                        pil_frame = cv2_to_pil_image(face_crop)
                        if pil_frame is None:
                            pil_frame = Image.fromarray(face_crop)
                        frame_result["face_detected"] = True
                
                # Preprocess and infer
                input_tensor = preprocess_image(pil_frame, processor)
                if input_tensor is not None:
                    real_prob, fake_prob, predicted_class = infer_image(input_tensor)
                    
                    frame_result["fake_probability"] = float(fake_prob)
                    frame_result["real_probability"] = float(real_prob)
                    
                    if fake_prob >= suspicious_threshold:
                        frame_result["prediction"] = "SUSPICIOUS"
                    else:
                        frame_result["prediction"] = "CLEAN"
                    
                    fake_probabilities.append(fake_prob)
                else:
                    frame_result["prediction"] = "FAILED"
            
            except Exception as e:
                logger.warning(f"Frame {frame_idx} analysis failed: {e}")
                frame_result["prediction"] = "FAILED"
            
            result["frame_results"].append(frame_result)
        
        # Step 5: Aggregate frame-level results
        if fake_probabilities:
            mean_fake_prob = float(np.mean(fake_probabilities))
            median_fake_prob = float(np.median(fake_probabilities))
            max_fake_prob = float(np.max(fake_probabilities))
            
            # Use median for final score (robust to outliers)
            final_fake_prob = median_fake_prob
            
            # Count suspicious frames
            suspicious_count = sum(1 for p in fake_probabilities if p >= suspicious_threshold)
            suspicious_percentage = (suspicious_count / len(fake_probabilities)) * 100
            
            result["suspicious_frames"] = suspicious_count
            result["suspicious_frame_percentage"] = round(suspicious_percentage, 1)
            result["fake_probability"] = round(final_fake_prob, 4)
            result["confidence"] = round(max(final_fake_prob, 1 - final_fake_prob), 4)
            
            # Determine video-level prediction
            if final_fake_prob >= fake_threshold:
                result["prediction"] = "LIKELY MANIPULATED"
            else:
                result["prediction"] = "LIKELY AUTHENTIC"
            
            # Get top 5 most suspicious frames
            result["top_suspicious_frames"] = sorted(
                [f for f in result["frame_results"] if f.get("fake_probability") is not None],
                key=lambda x: x.get("fake_probability", 0),
                reverse=True
            )[:5]
        
        result["success"] = True
        logger.info(f"Video analysis complete: {result['prediction']}")
    
    except Exception as e:
        logger.error(f"Video analysis failed: {e}", exc_info=True)
        result["error"] = f"Analysis failed: {str(e)}"
    
    finally:
        result["processing_time_seconds"] = round(time.time() - start_time, 2)
    
    return result

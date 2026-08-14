"""
Model loading and inference module.
Handles EfficientNet-B0 model loading for deepfake detection.
"""

import logging
import torch
from transformers import EfficientNetImageProcessor, EfficientNetForImageClassification
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Global model and processor cache
_model = None
_processor = None
_device = None


def get_device() -> torch.device:
    """Get the appropriate device (CUDA or CPU)."""
    global _device
    if _device is None:
        if torch.cuda.is_available():
            _device = torch.device("cuda")
            logger.info("CUDA available - using GPU")
        else:
            _device = torch.device("cpu")
            logger.info("CUDA not available - using CPU")
    return _device


def load_model() -> Tuple[EfficientNetForImageClassification, EfficientNetImageProcessor]:
    """
    Load the EfficientNet-B0 model and processor.
    
    Models are cached globally to avoid reloading.
    
    Returns:
        Tuple of (model, processor)
    """
    global _model, _processor
    
    if _model is not None and _processor is not None:
        logger.debug("Using cached model and processor")
        return _model, _processor
    
    logger.info("Loading EfficientNet-B0 model from Hugging Face...")
    try:
        _processor = EfficientNetImageProcessor.from_pretrained("google/efficientnet-b0")
        _model = EfficientNetForImageClassification.from_pretrained("google/efficientnet-b0")
        
        device = get_device()
        _model = _model.to(device)
        _model.eval()
        
        logger.info("Model loaded successfully")
        return _model, _processor
    
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise


def infer_image(image_tensor: torch.Tensor) -> Tuple[float, float, int]:
    """
    Run inference on a preprocessed image tensor.
    
    Args:
        image_tensor: Preprocessed image tensor with batch dimension
        
    Returns:
        Tuple of (real_prob, fake_prob, predicted_class)
    """
    model, _ = load_model()
    device = get_device()
    
    image_tensor = image_tensor.to(device)
    
    with torch.inference_mode():
        outputs = model(image_tensor)
        logits = outputs.logits
        
        # Convert logits to probabilities using softmax
        probs = torch.softmax(logits, dim=1)
        
        # Get the predicted class
        predicted_class = logits.argmax(-1).item()
        
        # Get probabilities for each class
        probs_numpy = probs.cpu().numpy()[0]
        real_prob = float(probs_numpy[0]) if len(probs_numpy) > 0 else 0.0
        fake_prob = float(probs_numpy[1]) if len(probs_numpy) > 1 else 0.0
        
        # Ensure probabilities sum to 1
        total = real_prob + fake_prob
        if total > 0:
            real_prob /= total
            fake_prob /= total
        
        return real_prob, fake_prob, predicted_class


def get_model_info() -> dict:
    """Get information about the loaded model."""
    model, processor = load_model()
    
    return {
        "model_name": "google/efficientnet-b0",
        "framework": "PyTorch + Transformers",
        "input_size": 224,
        "num_classes": 1000,  # ImageNet classes
        "device": str(get_device()),
        "dtype": str(model.dtype)
    }

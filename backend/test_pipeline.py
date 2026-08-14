"""
Test script to validate the deepfake detection pipeline.
Run this after installing dependencies to verify everything works.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import logging
from pathlib import Path
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_model_loading():
    """Test 1: Model loading"""
    logger.info("=" * 60)
    logger.info("TEST 1: Model Loading")
    logger.info("=" * 60)
    
    try:
        from ml import load_model, get_device, get_model_info
        
        device = get_device()
        logger.info(f"Device: {device}")
        
        model, processor = load_model()
        logger.info("✓ Model loaded successfully")
        
        info = get_model_info()
        logger.info(f"✓ Model info: {info}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Model loading failed: {e}")
        return False


def test_image_analysis():
    """Test 2: Image analysis on CATimg.png"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Image Analysis (CATimg.png)")
    logger.info("=" * 60)
    
    try:
        from ml import detect_image
        
        image_path = os.path.join(os.path.dirname(__file__), "..", "CATimg.png")
        
        if not Path(image_path).exists():
            logger.warning(f"Test image not found: {image_path}")
            return False
        
        start = time.time()
        result = detect_image(image_path)
        elapsed = time.time() - start
        
        logger.info(f"✓ Analysis completed in {elapsed:.2f}s")
        logger.info(f"  - Prediction: {result['prediction']}")
        logger.info(f"  - Fake Probability: {result['fake_probability']:.2%}")
        logger.info(f"  - Real Probability: {result['real_probability']:.2%}")
        logger.info(f"  - Face Detected: {result['face_detected']}")
        logger.info(f"  - File Size: {result['file_size_mb']:.2f} MB")
        logger.info(f"  - SHA-256: {result['sha256'][:16]}...")
        
        return result['success']
    
    except Exception as e:
        logger.error(f"✗ Image analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_preprocessing():
    """Test 3: Preprocessing pipeline"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Image Preprocessing")
    logger.info("=" * 60)
    
    try:
        from ml import load_image, preprocess_image, load_model
        
        image_path = os.path.join(os.path.dirname(__file__), "..", "CATimg.png")
        
        if not Path(image_path).exists():
            logger.warning(f"Test image not found: {image_path}")
            return False
        
        # Load image
        pil_image = load_image(image_path)
        logger.info(f"✓ Image loaded: {pil_image.size}")
        
        # Preprocess
        _, processor = load_model()
        tensor = preprocess_image(pil_image, processor)
        
        if tensor is not None:
            logger.info(f"✓ Preprocessed tensor shape: {tensor.shape}")
            return True
        else:
            logger.error("✗ Preprocessing returned None")
            return False
    
    except Exception as e:
        logger.error(f"✗ Preprocessing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_face_detection():
    """Test 4: Face detection"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Face Detection")
    logger.info("=" * 60)
    
    try:
        from ml.face_detector import detect_faces
        
        image_path = os.path.join(os.path.dirname(__file__), "..", "CATimg.png")
        
        if not Path(image_path).exists():
            logger.warning(f"Test image not found: {image_path}")
            return False
        
        image_cv2, faces = detect_faces(image_path)
        
        if image_cv2 is not None:
            logger.info(f"✓ Image loaded in OpenCV format: {image_cv2.shape}")
            logger.info(f"✓ Faces detected: {len(faces)}")
            
            if len(faces) > 0:
                for i, (x, y, w, h) in enumerate(faces):
                    logger.info(f"  Face {i+1}: x={x}, y={y}, w={w}, h={h}")
            
            return True
        else:
            logger.error("✗ Failed to load image in OpenCV")
            return False
    
    except Exception as e:
        logger.error(f"✗ Face detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sha256():
    """Test 5: SHA-256 hashing"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: SHA-256 Hashing")
    logger.info("=" * 60)
    
    try:
        from ml import calculate_sha256
        
        image_path = os.path.join(os.path.dirname(__file__), "..", "CATimg.png")
        
        if not Path(image_path).exists():
            logger.warning(f"Test image not found: {image_path}")
            return False
        
        sha256 = calculate_sha256(image_path)
        logger.info(f"✓ SHA-256 calculated: {sha256}")
        
        return len(sha256) == 64
    
    except Exception as e:
        logger.error(f"✗ SHA-256 calculation failed: {e}")
        return False


def test_inference():
    """Test 6: Model inference"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: Model Inference")
    logger.info("=" * 60)
    
    try:
        from ml import load_image, preprocess_image, load_model, infer_image
        
        image_path = os.path.join(os.path.dirname(__file__), "..", "CATimg.png")
        
        if not Path(image_path).exists():
            logger.warning(f"Test image not found: {image_path}")
            return False
        
        # Load and preprocess
        pil_image = load_image(image_path)
        model, processor = load_model()
        tensor = preprocess_image(pil_image, processor)
        
        # Infer
        real_prob, fake_prob, predicted_class = infer_image(tensor)
        
        logger.info(f"✓ Inference successful")
        logger.info(f"  - Real Probability: {real_prob:.4f}")
        logger.info(f"  - Fake Probability: {fake_prob:.4f}")
        logger.info(f"  - Predicted Class: {predicted_class}")
        
        return True
    
    except Exception as e:
        logger.error(f"✗ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results."""
    logger.info("\n\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 58 + "║")
    logger.info("║" + "DEEPFAKE DETECTION PIPELINE - TEST SUITE".center(58) + "║")
    logger.info("║" + " " * 58 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    
    tests = [
        ("Model Loading", test_model_loading),
        ("Preprocessing", test_preprocessing),
        ("Face Detection", test_face_detection),
        ("SHA-256 Hashing", test_sha256),
        ("Model Inference", test_inference),
        ("Image Analysis", test_image_analysis),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, p in results if p)
    total = len(results)
    
    for test_name, passed_test in results:
        status = "✓ PASS" if passed_test else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("\n🎉 All tests passed! Pipeline is ready.")
        return 0
    else:
        logger.error(f"\n❌ {total - passed} test(s) failed. See details above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

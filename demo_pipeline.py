#!/usr/bin/env python3
"""
Demonstration script showing the deepfake detection pipeline working end-to-end.
This shows the ML modules can be used directly without needing FastAPI.

Usage:
    python demo_pipeline.py
"""

import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def demo_image_detection():
    """Demonstrate image deepfake detection."""
    from ml import detect_image
    print("\n" + "=" * 70)
    print("DEMO 1: IMAGE DEEPFAKE DETECTION")
    print("=" * 70)
    
    image_path = "CATimg.png"
    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        return False
    
    print(f"\nAnalyzing: {image_path}")
    result = detect_image(image_path)
    
    if result['success']:
        print(f"\n✅ Analysis Complete")
        print(f"   Prediction: {result['prediction']}")
        print(f"   Fake Probability: {result['fake_probability']:.2%}")
        print(f"   Real Probability: {result['real_probability']:.2%}")
        print(f"   Confidence: {result['confidence']:.2%}")
        print(f"   File Size: {result['file_size_mb']:.2f} MB")
        print(f"   SHA-256: {result['sha256'][:32]}...")
        print(f"   Processing Time: {result['processing_time_seconds']:.2f}s")
        
        if result['face_detected']:
            print(f"   Face Detected: Yes")
            if 'bbox' in result:
                print(f"   Bounding Box: {result['bbox']}")
        else:
            print(f"   Face Detected: No (used full image)")
        
        return True
    else:
        print(f"❌ Analysis Failed: {result['error']}")
        return False


def demo_batch_analysis():
    """Demonstrate analyzing multiple files."""
    from ml import detect_image
    from pathlib import Path
    
    print("\n" + "=" * 70)
    print("DEMO 2: BATCH ANALYSIS")
    print("=" * 70)
    
    test_images = [
        "CATimg.png",
    ]
    
    results = []
    for image_path in test_images:
        if not Path(image_path).exists():
            print(f"⚠️  Skipping {image_path} (not found)")
            continue
        
        print(f"\nAnalyzing: {image_path}")
        result = detect_image(image_path)
        
        if result['success']:
            results.append({
                "file": image_path,
                "prediction": result['prediction'],
                "fake_probability": round(result['fake_probability'], 4),
                "real_probability": round(result['real_probability'], 4),
                "confidence": round(result['confidence'], 4),
                "processing_time": result['processing_time_seconds']
            })
            print(f"  ✅ {result['prediction']} ({result['fake_probability']:.1%} fake)")
        else:
            print(f"  ❌ Failed: {result['error']}")
    
    if results:
        print("\n" + "-" * 70)
        print("BATCH SUMMARY")
        print("-" * 70)
        print(json.dumps(results, indent=2))
        return True
    return False


def demo_api_format():
    """Demonstrate the API response format."""
    from ml import detect_image
    from pathlib import Path
    
    print("\n" + "=" * 70)
    print("DEMO 3: API RESPONSE FORMAT")
    print("=" * 70)
    
    image_path = "CATimg.png"
    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        return False
    
    print(f"\nFull API Response for: {image_path}")
    result = detect_image(image_path)
    
    # Pretty print the response
    print(json.dumps(result, indent=2, default=str))
    
    return True


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  DEEPFAKE DETECTION PIPELINE - LIVE DEMONSTRATION".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        # Demo 1: Single image analysis
        success1 = demo_image_detection()
        
        # Demo 2: Batch analysis
        success2 = demo_batch_analysis()
        
        # Demo 3: API format
        success3 = demo_api_format()
        
        # Summary
        print("\n" + "=" * 70)
        print("DEMONSTRATION SUMMARY")
        print("=" * 70)
        print(f"Demo 1 (Image Detection): {'✅ PASS' if success1 else '❌ FAIL'}")
        print(f"Demo 2 (Batch Analysis): {'✅ PASS' if success2 else '❌ FAIL'}")
        print(f"Demo 3 (API Format): {'✅ PASS' if success3 else '❌ FAIL'}")
        
        if success1 and success2 and success3:
            print("\n🎉 All demonstrations passed!")
            print("\n📝 NEXT STEPS:")
            print("   1. Install FastAPI: pip install fastapi uvicorn")
            print("   2. Start backend: python -m uvicorn backend.main:app --reload")
            print("   3. Install frontend: cd frontend && npm install")
            print("   4. Start frontend: npm start")
            print("   5. Open http://localhost:3000 in your browser")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

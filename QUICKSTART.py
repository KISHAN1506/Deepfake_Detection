#!/usr/bin/env python3
"""
Quick start guide for the Deepfake Detection Pipeline

This script demonstrates how to use the deepfake detection system.
It covers three ways to interact with the pipeline:
1. Direct Python API
2. Simple HTTP Server (no external dependencies)
3. Full FastAPI Backend (requires pip install fastapi uvicorn)
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                  DEEPFAKE DETECTION PIPELINE - QUICK START                 ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝


1️⃣  OPTION 1: DIRECT PYTHON API (No server needed)
═════════════════════════════════════════════════════════════════════════════

Quick Test:
    python demo_pipeline.py

In your own Python code:
    from backend.ml import detect_image
    
    result = detect_image("path/to/image.jpg")
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['fake_probability']:.2%}")

Response format:
    {
        "type": "image",
        "success": true,
        "prediction": "LIKELY MANIPULATED" or "LIKELY AUTHENTIC",
        "fake_probability": 0.657,       # 0.0 to 1.0
        "real_probability": 0.343,       # 0.0 to 1.0
        "confidence": 0.657,             # max(fake, real)
        "face_detected": false,
        "file_size_mb": 2.04,
        "sha256": "87bcc64b...",
        "processing_time_seconds": 0.22
    }


2️⃣  OPTION 2: SIMPLE HTTP SERVER (Recommended, No extra dependencies)
═════════════════════════════════════════════════════════════════════════════

Start the server:
    python simple_server.py

Access the web UI:
    - Open browser: http://localhost:8000
    - Upload image and analyze
    - View results in real-time

API Endpoints:
    GET  /                    - Web UI
    GET  /api/health          - Health check: {"status": "healthy", ...}
    POST /api/analyze         - Upload image (multipart/form-data)
    POST /api/test            - Test with CATimg.png

Example API call:
    curl -X POST -F "file=@image.jpg" http://localhost:8000/api/analyze


3️⃣  OPTION 3: FULL FASTAPI BACKEND (Advanced, higher performance)
═════════════════════════════════════════════════════════════════════════════

Install dependencies:
    pip install fastapi uvicorn python-multipart

Start the server:
    cd backend
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

Access API documentation:
    - Open browser: http://localhost:8000/docs (Swagger UI)
    - Open browser: http://localhost:8000/redoc (ReDoc)

This provides:
    - Auto-generated API documentation
    - Interactive request/response testing
    - Better performance
    - Production-ready setup


4️⃣  REACT FRONTEND
═════════════════════════════════════════════════════════════════════════════

Install dependencies:
    cd frontend
    npm install

Start development server:
    npm start

This opens http://localhost:3000 with:
    - Professional UI
    - File upload interface
    - Real-time analysis results
    - Metadata visualization
    - Frame-by-frame video analysis


5️⃣  QUICK TROUBLESHOOTING
═════════════════════════════════════════════════════════════════════════════

Q: "No module named 'ml'" error
A: Make sure you're in the right directory or adjust sys.path

Q: "OpenCV not available" warning
A: This is normal and expected. System uses PIL fallback (works fine)
   Install OpenCV for better face detection: pip install opencv-python

Q: Port 8000 already in use
A: Change port in simple_server.py or FastAPI command:
   python -m uvicorn main:app --port 8001

Q: SSL certificate error during pip install
A: Use the built-in Python modules (no FastAPI) or:
   - Use simple_server.py (no external deps needed)
   - Run in Docker
   - Install on a different machine with internet


6️⃣  PROJECT STRUCTURE
═════════════════════════════════════════════════════════════════════════════

├── backend/
│   ├── ml/
│   │   ├── model.py              # EfficientNet-B0 model loading
│   │   ├── preprocessing.py      # Image loading and preprocessing
│   │   ├── face_detector.py      # Face detection with fallback
│   │   ├── image_detector.py     # Single image analysis
│   │   ├── video_detector.py     # Video analysis with frame sampling
│   │   ├── utils.py              # SHA-256, file operations
│   │   └── config.py             # Configuration
│   ├── main.py                    # FastAPI backend
│   ├── test_pipeline.py           # Test suite (6 tests)
│   └── __init__.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # React UI component
│   │   ├── App.css                # Professional styling
│   │   └── ...
│   ├── package.json               # Dependencies
│   └── ...
├── demo_pipeline.py               # Live demonstration
├── simple_server.py               # HTTP server (no FastAPI needed)
├── CATimg.png                     # Test image
├── README.md                      # Full documentation
└── requirements.txt               # Python dependencies


7️⃣  MODEL INFORMATION
═════════════════════════════════════════════════════════════════════════════

Model: EfficientNet-B0
- Framework: PyTorch + Transformers
- Pre-training: ImageNet-1k
- Input size: 224×224 pixels
- Architecture: Efficient mobile-friendly CNN
- Device: CPU or CUDA (auto-detected)
- Memory: ~25 MB
- Inference speed: ~50-200ms per image (CPU)

Binary Classification:
- Class 0: REAL/AUTHENTIC
- Class 1: FAKE/MANIPULATED

Output: Probabilities for both classes


8️⃣  SUPPORTED FILE FORMATS
═════════════════════════════════════════════════════════════════════════════

Images:
    ✅ JPEG (.jpg, .jpeg)
    ✅ PNG (.png)
    ✅ WebP (.webp)
    Maximum size: 50 MB

Videos:
    ✅ MP4 (.mp4)
    ✅ MOV (.mov)
    ✅ AVI (.avi)
    ✅ Matroska (.mkv)
    Maximum size: 500 MB
    Frame sampling: Default 16 frames


9️⃣  ADVANCED CONFIGURATION
═════════════════════════════════════════════════════════════════════════════

Edit backend/config.py to customize:
    - MODEL_NAME: Pre-trained model to use
    - IMAGE_FAKE_THRESHOLD: Classification threshold (0.0-1.0)
    - VIDEO_FAKE_THRESHOLD: Video-level threshold
    - SUSPICIOUS_FRAME_THRESHOLD: Threshold for marking frames suspicious
    - MAX_IMAGE_SIZE: Maximum image file size (bytes)
    - MAX_VIDEO_SIZE: Maximum video file size (bytes)
    - UPLOAD_DIRECTORY: Where to save uploaded files


🔟  NEXT STEPS
═════════════════════════════════════════════════════════════════════════════

1. Run demo: python demo_pipeline.py
2. Start HTTP server: python simple_server.py
3. Open browser: http://localhost:8000
4. Upload an image and analyze
5. Check results (prediction, confidence, metadata)

For full setup with React UI and FastAPI:
   - Install Node.js and npm
   - Install FastAPI dependencies (if SSL issues resolved)
   - Follow "OPTION 3" for backend and "4️⃣ REACT FRONTEND"


Questions? Check:
    - README.md for detailed documentation
    - demo_pipeline.py for usage examples
    - backend/test_pipeline.py for unit tests
    - backend/main.py for FastAPI endpoint definitions
    - frontend/src/App.jsx for UI implementation


═════════════════════════════════════════════════════════════════════════════
🎉 System is ready to use! Start with: python simple_server.py
═════════════════════════════════════════════════════════════════════════════
""")

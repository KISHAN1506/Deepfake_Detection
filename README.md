# InnoHACK 2 - Deepfake Detection & Digital Evidence Authentication

An AI-powered system for detecting deepfake videos and images using EfficientNet-B0 with face detection and frame-level analysis.

**🚀 Quick Start:** create the Python environment, start `simple_server.py`, then visit `http://localhost:8000`.

## Features

- **🎬 Video Deepfake Detection**: Frame-level analysis with aggregated predictions
- **🖼️ Image Deepfake Detection**: Single-shot classification with face detection
- **😊 Face Detection**: Automatic face detection and cropping (PIL fallback - no OpenCV required)
- **📊 Frame Analysis**: Suspicious frame identification with timestamp and probability
- **🔐 Digital Evidence Hashing**: SHA-256 hash for evidence integrity verification
- **📱 Web Interface**: Clean UI showing predictions, metadata, and suspicious frames
- **⚙️ CPU Compatible**: Works on machines without GPU
- **🔌 No External Dependencies**: HTTP server runs on Python built-ins

## System Architecture

```
┌─ Frontend (React)
│  └─ Upload interface
│  └─ Real-time results dashboard
│
├─ Backend (FastAPI)
│  └─ /api/analyze
│  └─ /api/analyze/image
│  └─ /api/analyze/video
│
└─ ML Pipeline
   ├─ model.py - EfficientNet-B0 loading
   ├─ preprocessing.py - Image preprocessing
   ├─ face_detector.py - Face detection with OpenCV
   ├─ image_detector.py - Single image analysis
   └─ video_detector.py - Multi-frame video analysis
```

## Project Structure

```
InnoHACK 2/
├── backend/
│   ├── ml/
│   │   ├── model.py               # Model loading and inference
│   │   ├── preprocessing.py       # Image preprocessing
│   │   ├── face_detector.py       # Face detection
│   │   ├── image_detector.py      # Image analysis pipeline
│   │   ├── video_detector.py      # Video analysis pipeline
│   │   ├── utils.py               # Utilities (hashing, file ops)
│   │   └── __init__.py
│   ├── config.py                  # Configuration and constants
│   ├── main.py                    # FastAPI application
│   ├── test_pipeline.py           # Test suite
│   └── __init__.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main React component
│   │   ├── App.css                # Styling
│   │   ├── index.css              # Global styles
│   │   └── main.jsx               # React entry point
│   ├── index.html                 # HTML template
│   └── package.json               # Frontend dependencies
├── requirements.txt               # Python dependencies
├── file1.py                       # Original EfficientNet example
├── CATimg.png                     # Test image
└── README.md                      # This file
```

---

## Quick Start

From the project root, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python simple_server.py
```

Open [http://localhost:8000](http://localhost:8000). The built-in server provides
both the web UI and API, so the React frontend is not required for normal use.

## 📖 Documentation

- [CONTEXT.md](CONTEXT.md) - Complete project status for LLMs
- [STATUS.txt](STATUS.txt) - Visual status dashboard
- [SYSTEM_STATUS.md](SYSTEM_STATUS.md) - Detailed reference guide
- [QUICKSTART.py](QUICKSTART.py) - Interactive quick start guide

## Installation & Setup

### Prerequisites

- Python 3.8+
- Node.js and npm (only for the optional React frontend)
- ~2GB free disk space for model downloads
- 4GB+ RAM (usually available)

### Step 1: Create the Python Environment

```bash
cd /Users/kishanagarwal/Documents/Deepfake_Detection
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step 2: Test the ML Pipeline (Optional)

```bash
python backend/test_pipeline.py
```

### Step 3: Start the HTTP Server

```bash
python simple_server.py
```

**Expected output:**
```
======================================================================
🚀 DEEPFAKE DETECTION API - SIMPLE HTTP SERVER
======================================================================

✅ Server running at: http://localhost:8000
📝 Available endpoints:
   - GET /                    - Web UI
   - GET /api/health          - Health check
   - POST /api/analyze        - Upload image and analyze
   - POST /api/test           - Test with CATimg.png

📖 Open in browser: http://localhost:8000

🛑 Press Ctrl+C to stop
```

Server is now running at: **http://localhost:8000** ✅

### Step 4 (Optional): Run the React Frontend

The built-in server already provides a usable web UI. Run the React frontend only if
you are developing the React interface. Open a second terminal, then run:

```bash
cd frontend
npm install
npm start
```

The React development server runs at **http://localhost:3000** and proxies API
requests to **http://localhost:8000**. Start `python simple_server.py` first.

---

## Three Ways to Use

### 1. Web UI (Easiest) ⭐

```bash
python simple_server.py
# Open: http://localhost:8000
# Upload image, get results
```

### 2. Python API (Programmatic)

```python
from backend.ml import detect_image

result = detect_image("photo.jpg")
print(result['prediction'])        # "LIKELY MANIPULATED"
print(result['fake_probability'])  # 0.657
```

### 3. HTTP API (Any Language)

```bash
curl -X POST -F "file=@image.jpg" http://localhost:8000/api/analyze
```

---

---

## Usage

### Web Interface (Recommended)

1. Navigate to **http://localhost:8000** in your browser
2. Click the upload area and select an image file
3. Click **Analyze**
4. Wait for processing (typically 0.2-0.4 seconds on CPU)
5. View results:
   - **AI Assessment**: LIKELY MANIPULATED or LIKELY AUTHENTIC
   - **Probabilities**: Fake % and Real %
   - **Confidence**: Overall prediction confidence
   - **File Info**: Metadata, resolution
   - **Face Detection**: Whether faces were detected
   - **Digital Evidence Hash**: SHA-256 for verification

### Command-Line Testing

**Test the health endpoint:**

```bash
curl http://localhost:8000/api/health
```

**Analyze an image via API:**

```bash
curl -X POST -F "file=@image.jpg" http://localhost:8000/api/analyze
```

**Test with included image:**

```bash
curl http://localhost:8000/api/test
```

**Using Python API directly:**

```python
from backend.ml import detect_image

result = detect_image("path/to/image.jpg")
print(f"Prediction: {result['prediction']}")
print(f"Fake Probability: {result['fake_probability']:.2%}")
print(f"Processing Time: {result['processing_time_seconds']:.2f}s")
```

**Running demonstrations:**

```bash
python demo_pipeline.py
```

Shows 3 complete examples of the system in action.

---

---

## API Endpoints

### Web UI
```
GET /
```
Interactive web interface with file upload.

### Health Check
```
GET /api/health
```

Returns system status.

**Response:**
```json
{
  "status": "healthy",
  "service": "Deepfake Detection API",
  "version": "1.0",
  "model": "EfficientNet-B0"
}
```

### Analyze Image
```
POST /api/analyze
Content-Type: multipart/form-data

file: <image file>
```

**Response:**
```json
{
  "type": "image",
  "success": true,
  "prediction": "LIKELY MANIPULATED",
  "fake_probability": 0.657,
  "real_probability": 0.343,
  "confidence": 0.657,
  "face_detected": false,
  "face_count": 0,
  "metadata": {
    "width": 1402,
    "height": 1122,
    "format": "PNG",
    "mode": "RGB"
  },
  "sha256": "87bcc64b7e1a67a2ab5a5bd0086b62850fac79a8da99da111a477152e22de51d",
  "processing_time_seconds": 0.22,
  "file_size_mb": 2.04
}
```

### Test Endpoint
```
POST /api/test
```

Analyzes the included test image (CATimg.png).

**Response:** Same format as /api/analyze

---

## Advanced: FastAPI Alternative

If you have FastAPI installed (or fix the SSL issue), you can use the full backend:

```bash
pip install fastapi uvicorn python-multipart

cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then visit **http://localhost:8000/docs** for interactive API documentation.

**Note:** Currently blocked by SSL certificate issues. The simple HTTP server (simple_server.py) provides equivalent functionality.

---

## Model Information

- **Model**: EfficientNet-B0 (from Hugging Face: google/efficientnet-b0)
- **Input Size**: 224×224 pixels (auto-resized)
- **Training Data**: ImageNet-1000 (pre-trained)
- **Framework**: PyTorch + Transformers
- **Device**: Automatic CPU/GPU selection
- **Inference Mode**: torch.inference_mode() for efficiency
- **Memory**: ~25 MB (cached in memory)
- **Speed**: 50-200ms per image on CPU

### Classification Strategy

1. **File Validation**: Check existence, extension, file size
2. **Face Detection**: Uses PIL/OpenCV to locate faces
3. **Face Cropping**: Extracts largest face with padding (or uses full image)
4. **Preprocessing**: Resizes to 224×224, applies ImageNet normalization
5. **Inference**: Runs EfficientNet-B0 forward pass
6. **Classification**:
   - Fake Probability >= 0.5 → "LIKELY MANIPULATED"
   - Fake Probability < 0.5 → "LIKELY AUTHENTIC"

### Why EfficientNet-B0?

- ✅ Mobile-friendly (small & fast)
- ✅ Good accuracy on general images
- ✅ Pre-trained on ImageNet (transfer learning)
- ✅ Fast inference (CPU-friendly)
- ✅ Low memory footprint

**Note:** This is a proof-of-concept using a general classification model. For production deepfake detection, consider specialized models like XceptionNet-based or face-specific detectors.

---

## Configuration

Edit `backend/config.py` to customize:

```python
# Detection thresholds
IMAGE_FAKE_THRESHOLD = 0.5          # Probability threshold for images
VIDEO_FAKE_THRESHOLD = 0.5          # Median threshold for videos
SUSPICIOUS_FRAME_THRESHOLD = 0.6    # Individual frame threshold

# Video processing
DEFAULT_VIDEO_SAMPLE_FRAMES = 16    # Frames to extract from videos

# File limits
MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_VIDEO_SIZE = 500 * 1024 * 1024 # 500 MB

# API
API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ORIGINS = ["http://localhost:3000", "*"]
```

---

## Troubleshooting

### "No module named ..." or dependency installation errors

Create or activate the environment and install dependencies from the project root:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Or: .venv\Scripts\activate on Windows
python -m pip install -r requirements.txt
```

### "python simple_server.py" command not found

Run the command from the project root, where `simple_server.py` is located:
```bash
cd /Users/kishanagarwal/Documents/Deepfake_Detection
source .venv/bin/activate
python simple_server.py
```

On systems where `python` is not available, use `python3 simple_server.py`.

### "npm start" fails

Install the frontend dependencies from the `frontend` directory, then start the
React development server:
```bash
cd frontend
npm install
npm start
```

The project uses `react-scripts`; `npm start` is the supported frontend command.

### "Port 8000 already in use"

Either:
1. Stop the existing process: `lsof -i :8000` then `kill -9 <PID>`
2. Use a different port by editing `simple_server.py` line ~250

### "OpenCV not available" (warning)

This is normal and expected. The system uses PIL fallback which works perfectly:
```
WARNING:ml.face_detector:OpenCV not available - using PIL fallback
```

To enable OpenCV (optional):
```bash
pip install opencv-python
```

### "Failed to load image"

- Ensure file exists and is readable
- Supported formats: JPG, PNG, WEBP (images)
- Check file isn't corrupted
- Max size: 50 MB

### "No faces detected" (analysis still works)

The system falls back to full-image analysis. This is expected for images without faces.

### "Model loading takes forever" (first run only)

EfficientNet-B0 downloads ~22 MB on first run from Hugging Face and caches locally. This is normal and only happens once. Subsequent runs are fast.

### "Connection refused" when accessing http://localhost:8000

1. Verify server is running: `curl http://localhost:8000/api/health`
2. Check it didn't crash: Look at terminal output
3. Restart: `python simple_server.py`

### SSL Certificate Error during pip install

The project requires the packages listed in `requirements.txt`, including PyTorch,
Transformers, and Pillow. If pip cannot reach the package index, try again on a
network that permits package downloads or install the packages from local wheels.

---

## Performance Benchmarks

Typical processing times on CPU (MacBook Air M1):

| Operation | Time | Notes |
|-----------|------|-------|
| Model Load (first) | 2-3s | Downloads from Hugging Face, happens once |
| Model Load (cached) | 0.1s | Subsequent requests reuse model |
| Image Preprocessing | 10-50ms | Resize + normalization |
| Face Detection | 20-100ms | PIL fallback (no OpenCV needed) |
| Model Inference | 50-200ms | EfficientNet-B0 forward pass |
| **Total per Image** | **0.2-0.4s** | After first load (cached) |
| API Response | <1ms | JSON serialization |

**Example Results:**
- CATimg.png (2.04 MB): 0.22s processing time ✅
- Small image: ~0.2s total
- Large image (50 MB): ~0.3-0.4s total

*(GPU/CUDA times typically 3-5x faster if available)*

---

## Testing

The system includes comprehensive tests and demonstrations:

### Unit Tests (6 Tests)

```bash
python backend/test_pipeline.py
```

**Tests include:**
- ✅ Model Loading: Verifies EfficientNet-B0 loads from Hugging Face
- ✅ Image Preprocessing: Confirms 224×224 tensor creation
- ✅ Face Detection: Tests PIL fallback (no OpenCV required)
- ✅ SHA-256 Hashing: Verifies hash calculation
- ✅ Model Inference: Tests inference on test image
- ✅ Image Analysis: Full pipeline on CATimg.png

**Expected output:**
```
TEST 1: Model Loading
✓ Model loaded successfully

TEST 2: Image Preprocessing
✓ Preprocessing successful

...

Total: 6/6 tests passed
🎉 All tests passed! Pipeline is ready.
```

### Live Demonstrations (3 Demos)

```bash
python demo_pipeline.py
```

Shows:
1. Single image analysis
2. Batch image analysis
3. API response format

**Expected output:**
```
🎬 DEMO 1: Single Image Analysis
Analyzing: CATimg.png
Result: LIKELY MANIPULATED (65.70% fake prob)

...

🎉 All demonstrations passed!
```

---

## Important Notes

⚠️ **Not Definitive Proof**: This system provides forensic analysis hints, not absolute truth.
- Results should be interpreted as "LIKELY MANIPULATED" or "LIKELY AUTHENTIC", not certainties
- Always consult domain experts for critical decisions
- No system can guarantee 100% detection accuracy

🔒 **Evidence Integrity**: SHA-256 hashes verify that files haven't been modified after analysis.

🎯 **Designed for Hackathon**: 
- Prioritizes working MVP over perfect accuracy
- Uses CPU-compatible models
- Minimal dependencies
- ~2-day development timeline

---

## Future Enhancements

Potential features for future versions:
- Grad-CAM visualization of suspicious regions
- C2PA content provenance detection
- PDF forensic report generation
- Frame timeline visualization
- Batch processing API
- Database result persistence
- Multi-model ensemble
- Real-time video stream analysis

---

## License

This project is open source and available under the MIT License.

## Authors

InnoHACK 2 Team - Deepfake Detection Challenge

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review test suite output: `python backend/test_pipeline.py`
3. Enable debug logging: `LOG_LEVEL=DEBUG python backend/main.py`
4. Check API docs: `http://localhost:8000/docs`


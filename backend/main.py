"""
FastAPI backend for deepfake detection system.
Handles file uploads, analysis, and result serving.
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import (
    UPLOADS_DIR, 
    API_HOST, 
    API_PORT, 
    CORS_ORIGINS,
    IMAGE_FAKE_THRESHOLD,
    VIDEO_FAKE_THRESHOLD,
    DEFAULT_VIDEO_SAMPLE_FRAMES,
    ANALYSIS_DISCLAIMER,
    LOG_LEVEL,
    LOG_FORMAT
)
from ml import (
    detect_image,
    detect_video,
    validate_image_file,
    validate_video_file,
    create_analysis_directory,
    generate_analysis_id
)

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Deepfake Detection API",
    description="AI-powered deepfake and digital evidence authentication system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Deepfake Detection API",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def api_health():
    """API health endpoint with model info."""
    try:
        from ml import get_model_info
        model_info = get_model_info()
        return {
            "status": "healthy",
            "model": model_info
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/api/analyze/image")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze an image for deepfake indicators.
    
    Returns: Analysis result with prediction, probabilities, and metadata
    """
    analysis_id = generate_analysis_id()
    
    try:
        # Create analysis directory
        _, analysis_dir = create_analysis_directory(str(UPLOADS_DIR))
        if analysis_dir is None:
            raise HTTPException(status_code=500, detail="Failed to create analysis directory")
        
        # Save uploaded file
        original_path = os.path.join(analysis_dir, "original", file.filename)
        Path(original_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(original_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        logger.info(f"Analyzing image: {file.filename}")
        
        # Analyze
        result = detect_image(
            original_path,
            fake_threshold=IMAGE_FAKE_THRESHOLD
        )
        
        # Add metadata
        result["analysis_id"] = analysis_id
        result["filename"] = file.filename
        result["disclaimer"] = ANALYSIS_DISCLAIMER
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Image analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/analyze/video")
async def analyze_video(file: UploadFile = File(...)):
    """
    Analyze a video for deepfake indicators.
    
    Returns: Analysis result with frame-level predictions and aggregated score
    """
    analysis_id = generate_analysis_id()
    
    try:
        # Create analysis directory
        _, analysis_dir = create_analysis_directory(str(UPLOADS_DIR))
        if analysis_dir is None:
            raise HTTPException(status_code=500, detail="Failed to create analysis directory")
        
        # Save uploaded file
        original_path = os.path.join(analysis_dir, "original", file.filename)
        Path(original_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(original_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        logger.info(f"Analyzing video: {file.filename}")
        
        # Analyze
        result = detect_video(
            original_path,
            num_frames=DEFAULT_VIDEO_SAMPLE_FRAMES,
            fake_threshold=VIDEO_FAKE_THRESHOLD
        )
        
        # Add metadata
        result["analysis_id"] = analysis_id
        result["filename"] = file.filename
        result["disclaimer"] = ANALYSIS_DISCLAIMER
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Video analysis failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    """
    Auto-detect file type and analyze.
    Supports both images and videos.
    """
    file_ext = Path(file.filename).suffix.lower()
    
    # Check if image or video
    if file_ext in {'.jpg', '.jpeg', '.png', '.webp'}:
        return await analyze_image(file)
    elif file_ext in {'.mp4', '.mov', '.avi', '.mkv'}:
        return await analyze_video(file)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {file_ext}. Supported: .jpg, .png, .webp, .mp4, .mov, .avi, .mkv"
        )


@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """
    Retrieve previous analysis results.
    
    Note: In this MVP, we don't persist results. This endpoint is for future enhancement.
    """
    return JSONResponse(
        status_code=501,
        content={
            "error": "Result persistence not yet implemented",
            "note": "Results are returned immediately after analysis"
        }
    )


@app.post("/api/batch-analyze")
async def batch_analyze(files: list[UploadFile] = File(...)):
    """
    Analyze multiple files at once.
    """
    results = []
    for file in files:
        try:
            if Path(file.filename).suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}:
                # Reset file pointer
                await file.seek(0)
                result = await analyze_image(file)
            elif Path(file.filename).suffix.lower() in {'.mp4', '.mov', '.avi', '.mkv'}:
                await file.seek(0)
                result = await analyze_video(file)
            else:
                result = {
                    "filename": file.filename,
                    "error": f"Unsupported format: {Path(file.filename).suffix}"
                }
            results.append(result)
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return JSONResponse(content={"analyses": results})


@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    logger.info("Deepfake Detection API starting...")
    logger.info(f"Uploads directory: {UPLOADS_DIR}")
    logger.info(f"CORS origins: {CORS_ORIGINS}")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    logger.info("Deepfake Detection API shutting down...")


if __name__ == "__main__":
    logger.info(f"Starting API server on {API_HOST}:{API_PORT}")
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level=LOG_LEVEL.lower()
    )

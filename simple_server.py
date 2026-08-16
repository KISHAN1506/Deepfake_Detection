#!/usr/bin/env python3
"""
Deepfake Detection System - High Performance Server
Uses Python's built-in http.server - no external server frameworks needed.

Usage:
    python simple_server.py
    
Then visit: http://localhost:8000
"""

import sys
import os
import json
import time
import re
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from ml import detect_image, detect_video


def parse_multipart(body: bytes, content_type: str):
    """
    Parse multipart/form-data payload cleanly without binary corruption.
    """
    if "boundary=" not in content_type:
        return []
    
    # Extract boundary string
    boundary_str = content_type.split("boundary=")[1].split(";")[0].strip().strip('"')
    boundary = boundary_str.encode('ascii')
    delimiter = b'--' + boundary
    
    parts = body.split(delimiter)
    files = []
    
    for part in parts:
        if not part or part in (b'--\r\n', b'--', b'\r\n', b'--\r\n\r\n'):
            continue
            
        if part.startswith(b'\r\n'):
            part = part[2:]
            
        header_end = part.find(b'\r\n\r\n')
        if header_end == -1:
            continue
            
        header_bytes = part[:header_end]
        data = part[header_end + 4:]
        
        # Trim trailing CRLF before boundary
        if data.endswith(b'\r\n'):
            data = data[:-2]
            
        headers_text = header_bytes.decode('utf-8', errors='replace')
        filename = None
        name = None
        
        for line in headers_text.split('\r\n'):
            if line.lower().startswith('content-disposition:'):
                if 'filename=' in line:
                    match = re.search(r'filename="([^"]+)"', line)
                    if match:
                        filename = match.group(1)
                    else:
                        match_unquoted = re.search(r'filename=([^\s;]+)', line)
                        if match_unquoted:
                            filename = match_unquoted.group(1).strip('"')
                if 'name=' in line:
                    match_name = re.search(r'name="([^"]+)"', line)
                    if match_name:
                        name = match_name.group(1)
                        
        if filename and data:
            files.append({
                'name': name,
                'filename': filename,
                'data': data
            })
            
    return files


class DeepfakeDetectionHandler(BaseHTTPRequestHandler):
    """HTTP request handler for deepfake detection API."""
    
    def do_GET(self):
        """Handle GET requests."""
        path = urlparse(self.path).path
        
        if path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Deepfake Detection & Digital Forensics System</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #07090e;
            --bg-card: rgba(15, 23, 42, 0.75);
            --bg-card-hover: rgba(26, 38, 66, 0.85);
            --border-color: rgba(255, 255, 255, 0.08);
            --border-highlight: rgba(56, 189, 248, 0.4);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent-cyan: #38bdf8;
            --accent-blue: #6366f1;
            --danger-red: #ef4444;
            --danger-glow: rgba(239, 68, 68, 0.25);
            --success-green: #10b981;
            --success-glow: rgba(16, 185, 129, 0.25);
            --warning-amber: #f59e0b;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(circle at 15% 15%, rgba(99, 102, 241, 0.15) 0%, transparent 45%),
                radial-gradient(circle at 85% 85%, rgba(56, 189, 248, 0.12) 0%, transparent 45%);
            background-attachment: fixed;
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem 1rem;
        }

        .container {
            width: 100%;
            max-width: 960px;
        }

        /* Header */
        header {
            text-align: center;
            margin-bottom: 2.5rem;
        }

        .logo-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(56, 189, 248, 0.1);
            border: 1px solid rgba(56, 189, 248, 0.25);
            color: var(--accent-cyan);
            padding: 0.35rem 1rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 1rem;
        }

        h1 {
            font-family: 'Outfit', sans-serif;
            font-size: 2.75rem;
            font-weight: 800;
            background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, var(--accent-cyan) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.02em;
            margin-bottom: 0.75rem;
        }

        header p {
            color: var(--text-muted);
            font-size: 1.1rem;
            max-width: 600px;
            margin: 0 auto;
        }

        /* Card Container */
        .glass-card {
            background: var(--bg-card);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            margin-bottom: 2rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* Upload Area */
        .upload-dropzone {
            border: 2px dashed rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 3rem 2rem;
            text-align: center;
            cursor: pointer;
            background: rgba(255, 255, 255, 0.02);
            transition: all 0.25s ease;
            position: relative;
            overflow: hidden;
        }

        .upload-dropzone:hover, .upload-dropzone.dragover {
            border-color: var(--accent-cyan);
            background: rgba(56, 189, 248, 0.05);
            box-shadow: 0 0 25px rgba(56, 189, 248, 0.15);
        }

        .upload-dropzone input[type="file"] {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            opacity: 0;
            cursor: pointer;
        }

        .upload-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            display: inline-block;
        }

        .upload-title {
            font-family: 'Outfit', sans-serif;
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .upload-hint {
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        /* Preview Container */
        .preview-container {
            display: none;
            margin-top: 1.5rem;
            border-radius: 12px;
            overflow: hidden;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid var(--border-color);
            position: relative;
            max-height: 380px;
            align-items: center;
            justify-content: center;
        }

        .preview-media {
            max-width: 100%;
            max-height: 380px;
            object-fit: contain;
            display: block;
            margin: 0 auto;
        }

        /* Controls */
        .btn-analyze {
            width: 100%;
            margin-top: 1.5rem;
            padding: 1rem 1.5rem;
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-cyan) 100%);
            border: none;
            border-radius: 12px;
            color: #ffffff;
            font-family: 'Outfit', sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.25s ease;
            box-shadow: 0 4px 20px rgba(56, 189, 248, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .btn-analyze:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(56, 189, 248, 0.45);
        }

        .btn-analyze:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        /* Loading / Scanning state */
        .scanning-overlay {
            display: none;
            text-align: center;
            padding: 3rem 1rem;
        }

        .scanner-ring {
            width: 70px;
            height: 70px;
            border: 4px solid rgba(56, 189, 248, 0.1);
            border-top: 4px solid var(--accent-cyan);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1.5rem auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .scanning-text {
            font-family: 'Outfit', sans-serif;
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--accent-cyan);
            letter-spacing: 0.02em;
        }

        /* Results Display */
        .results-wrapper {
            display: none;
            animation: fadeIn 0.4s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .verdict-banner {
            border-radius: 16px;
            padding: 1.75rem;
            text-align: center;
            margin-bottom: 1.5rem;
            position: relative;
            overflow: hidden;
        }

        .verdict-banner.authentic {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 78, 59, 0.3) 100%);
            border: 1px solid var(--success-green);
            box-shadow: 0 0 30px var(--success-glow);
        }

        .verdict-banner.manipulated {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(127, 29, 29, 0.3) 100%);
            border: 1px solid var(--danger-red);
            box-shadow: 0 0 30px var(--danger-glow);
        }

        .verdict-tag {
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.5rem;
        }

        .verdict-banner.authentic .verdict-tag { color: var(--success-green); }
        .verdict-banner.manipulated .verdict-tag { color: var(--danger-red); }

        .verdict-title {
            font-family: 'Outfit', sans-serif;
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }

        .probability-bar-container {
            margin-top: 1.25rem;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 9999px;
            height: 14px;
            overflow: hidden;
            display: flex;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .bar-fake {
            background: linear-gradient(90deg, #f87171, #ef4444);
            height: 100%;
            transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .bar-real {
            background: linear-gradient(90deg, #34d399, #10b981);
            height: 100%;
            transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .prob-labels {
            display: flex;
            justify-content: space-between;
            margin-top: 0.5rem;
            font-size: 0.9rem;
            font-weight: 600;
        }

        /* Metrics Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .metric-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.25rem;
        }

        .metric-label {
            color: var(--text-muted);
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 0.4rem;
        }

        .metric-value {
            font-family: 'Outfit', sans-serif;
            font-size: 1.35rem;
            font-weight: 700;
            color: var(--text-main);
        }

        /* Evidence Hash */
        .hash-card {
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 1.25rem;
            margin-bottom: 1.5rem;
        }

        .hash-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }

        .hash-code {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: var(--accent-cyan);
            word-break: break-all;
            background: rgba(56, 189, 248, 0.08);
            padding: 0.6rem 0.8rem;
            border-radius: 8px;
            border: 1px solid rgba(56, 189, 248, 0.15);
        }

        .btn-copy {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 0.3rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-copy:hover {
            background: rgba(255, 255, 255, 0.15);
        }

        /* Error Banner */
        .error-card {
            display: none;
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid var(--danger-red);
            border-radius: 14px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            color: #fca5a5;
        }

        .error-title {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
            color: var(--danger-red);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* Details collapsible */
        details {
            margin-top: 1rem;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            padding: 0.75rem 1rem;
        }

        summary {
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--text-muted);
            user-select: none;
        }

        summary:hover {
            color: var(--text-main);
        }

        pre {
            margin-top: 0.75rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: #34d399;
            white-space: pre-wrap;
            word-wrap: break-word;
            max-height: 300px;
            overflow-y: auto;
        }

        footer {
            margin-top: auto;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
            padding: 1.5rem 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo-badge">🔍 Forensic AI Authentication</div>
            <h1>Deepfake Detection System</h1>
            <p>Upload image or video media to analyze deepfake manipulation & digital evidence integrity.</p>
        </header>

        <main>
            <div class="glass-card">
                <div class="upload-dropzone" id="dropzone">
                    <input type="file" id="fileInput" accept="image/*,video/*">
                    <div class="upload-icon">📁</div>
                    <div class="upload-title" id="uploadTitle">Click or drag media file here</div>
                    <div class="upload-hint" id="uploadHint">Supports PNG, JPG, WEBP, MP4, MOV, AVI (Max 500MB)</div>
                </div>

                <div class="preview-container" id="previewContainer">
                    <img id="imagePreview" class="preview-media" style="display:none;" alt="Preview">
                    <video id="videoPreview" class="preview-media" style="display:none;" controls></video>
                </div>

                <button type="button" id="analyzeBtn" class="btn-analyze" disabled>
                    <span>⚡ Run Forensic Analysis</span>
                </button>
            </div>

            <!-- Error Banner -->
            <div class="error-card" id="errorCard">
                <div class="error-title">⚠️ Analysis Error</div>
                <div id="errorMessage">An unexpected error occurred during processing.</div>
            </div>

            <!-- Loading State -->
            <div class="glass-card scanning-overlay" id="loadingState">
                <div class="scanner-ring"></div>
                <div class="scanning-text">Analyzing Media Forensics...</div>
                <p style="color: var(--text-muted); margin-top: 0.5rem; font-size: 0.9rem;">
                    Executing face extraction, artifact detection, and model inference...
                </p>
            </div>

            <!-- Results Section -->
            <div class="glass-card results-wrapper" id="resultsWrapper">
                <div class="verdict-banner" id="verdictBanner">
                    <div class="verdict-tag" id="verdictTag">VERDICT</div>
                    <div class="verdict-title" id="verdictTitle">LIKELY MANIPULATED</div>
                    
                    <div class="probability-bar-container">
                        <div class="bar-fake" id="barFake" style="width: 50%;"></div>
                        <div class="bar-real" id="barReal" style="width: 50%;"></div>
                    </div>
                    <div class="prob-labels">
                        <span style="color: var(--danger-red);" id="fakeProbLabel">Fake: 0%</span>
                        <span style="color: var(--success-green);" id="realProbLabel">Real: 0%</span>
                    </div>
                </div>

                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-label">Confidence Score</div>
                        <div class="metric-value" id="confidenceVal">0%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Face Detection</div>
                        <div class="metric-value" id="faceVal">None</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Processing Time</div>
                        <div class="metric-value" id="timeVal">0.00s</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">File Size</div>
                        <div class="metric-value" id="sizeVal">0 MB</div>
                    </div>
                </div>

                <div class="hash-card">
                    <div class="hash-header">
                        <span class="metric-label">Digital Evidence SHA-256 Hash</span>
                        <button class="btn-copy" id="btnCopyHash" onclick="copyHash()">Copy Hash</button>
                    </div>
                    <div class="hash-code" id="hashCode">----------------------------------------------------------------</div>
                </div>

                <details>
                    <summary>View Full Raw API Payload</summary>
                    <pre id="rawResponse">{}</pre>
                </details>
            </div>
        </main>

        <footer>
            Deepfake Detection System v1.0 | Built for InnoHACK 2
        </footer>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const dropzone = document.getElementById('dropzone');
        const uploadTitle = document.getElementById('uploadTitle');
        const uploadHint = document.getElementById('uploadHint');
        const previewContainer = document.getElementById('previewContainer');
        const imagePreview = document.getElementById('imagePreview');
        const videoPreview = document.getElementById('videoPreview');
        const analyzeBtn = document.getElementById('analyzeBtn');

        const loadingState = document.getElementById('loadingState');
        const resultsWrapper = document.getElementById('resultsWrapper');
        const errorCard = document.getElementById('errorCard');
        const errorMessage = document.getElementById('errorMessage');

        let selectedFile = null;

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.remove('dragover');
            }, false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            if (dt.files.length > 0) {
                handleFileSelect(dt.files[0]);
            }
        });

        function handleFileSelect(file) {
            selectedFile = file;
            uploadTitle.textContent = `Selected: ${file.name}`;
            uploadHint.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
            analyzeBtn.disabled = false;

            // Reset results & error
            resultsWrapper.style.display = 'none';
            errorCard.style.display = 'none';

            // Show preview
            const url = URL.createObjectURL(file);
            previewContainer.style.display = 'flex';

            if (file.type.startsWith('video/')) {
                imagePreview.style.display = 'none';
                videoPreview.style.display = 'block';
                videoPreview.src = url;
            } else {
                videoPreview.style.display = 'none';
                imagePreview.style.display = 'block';
                imagePreview.src = url;
            }
        }

        analyzeBtn.addEventListener('click', async () => {
            if (!selectedFile) return;

            // UI states
            analyzeBtn.disabled = true;
            loadingState.style.display = 'block';
            resultsWrapper.style.display = 'none';
            errorCard.style.display = 'none';

            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                loadingState.style.display = 'none';
                analyzeBtn.disabled = false;

                if (!response.ok || data.success === false) {
                    showError(data.error || 'Failed to analyze media file.');
                    return;
                }

                renderResults(data);

            } catch (err) {
                loadingState.style.display = 'none';
                analyzeBtn.disabled = false;
                showError('Network or server connection error: ' + err.message);
            }
        });

        function showError(msg) {
            errorMessage.textContent = msg;
            errorCard.style.display = 'block';
        }

        function renderResults(data) {
            resultsWrapper.style.display = 'block';

            const banner = document.getElementById('verdictBanner');
            const tag = document.getElementById('verdictTag');
            const title = document.getElementById('verdictTitle');

            const isManipulated = data.prediction === 'LIKELY MANIPULATED';
            
            banner.className = 'verdict-banner ' + (isManipulated ? 'manipulated' : 'authentic');
            tag.textContent = isManipulated ? '⚠️ FORENSIC WARNING' : '✅ AUTHENTICATED';
            title.textContent = data.prediction || 'UNKNOWN RESULT';

            const fakeProb = (data.fake_probability || 0) * 100;
            const realProb = (data.real_probability || 0) * 100;

            document.getElementById('barFake').style.width = fakeProb + '%';
            document.getElementById('barReal').style.width = realProb + '%';
            document.getElementById('fakeProbLabel').textContent = `Fake: ${fakeProb.toFixed(1)}%`;
            document.getElementById('realProbLabel').textContent = `Real: ${realProb.toFixed(1)}%`;

            document.getElementById('confidenceVal').textContent = `${((data.confidence || 0) * 100).toFixed(1)}%`;
            document.getElementById('faceVal').textContent = data.face_detected ? `${data.face_count} Detected` : 'Full Image';
            document.getElementById('timeVal').textContent = `${(data.processing_time_seconds || 0).toFixed(2)}s`;
            document.getElementById('sizeVal').textContent = `${(data.file_size_mb || 0).toFixed(2)} MB`;

            document.getElementById('hashCode').textContent = data.sha256 || 'N/A';
            document.getElementById('rawResponse').textContent = JSON.stringify(data, null, 2);
        }

        function copyHash() {
            const hashText = document.getElementById('hashCode').textContent;
            navigator.clipboard.writeText(hashText).then(() => {
                const btn = document.getElementById('btnCopyHash');
                btn.textContent = 'Copied!';
                setTimeout(() => { btn.textContent = 'Copy Hash'; }, 2000);
            });
        }
    </script>
</body>
</html>
"""
            self.wfile.write(html.encode('utf-8'))
        
        elif path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "service": "Deepfake Detection API",
                "version": "1.0",
                "model": "EfficientNet-B0"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": f"Not found: {path}"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_POST(self):
        """Handle POST requests."""
        path = urlparse(self.path).path
        
        if path == '/api/analyze':
            try:
                content_type = self.headers.get('Content-Type', '')
                
                if 'multipart/form-data' not in content_type:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {"error": "Content-Type must be multipart/form-data"}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return
                
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                
                files = parse_multipart(body, content_type)
                
                if not files:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {"error": "No file uploaded in request"}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return
                
                uploaded_file = files[0]
                filename = uploaded_file['filename']
                file_data = uploaded_file['data']
                
                # Create temporary file preserving extension
                ext = Path(filename).suffix
                if not ext:
                    ext = ".tmp"
                
                temp_filename = f"upload_{int(time.time())}_{os.urandom(4).hex()}{ext}"
                temp_path = os.path.join("/tmp", temp_filename)
                
                with open(temp_path, 'wb') as f:
                    f.write(file_data)
                
                try:
                    # Detect based on file extension
                    ext_lower = ext.lower()
                    if ext_lower in {'.mp4', '.mov', '.avi', '.mkv', '.webm'}:
                        result = detect_video(temp_path)
                    else:
                        result = detect_image(temp_path)
                    
                    # Attach original filename
                    result["filename"] = filename
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(result, default=str).encode('utf-8'))
                
                finally:
                    if Path(temp_path).exists():
                        try:
                            Path(temp_path).unlink()
                        except Exception:
                            pass
            
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": str(e), "type": type(e).__name__}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif path == '/api/test':
            try:
                test_image = Path("CATimg.png")
                if not test_image.exists():
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {"error": "Test image not found"}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return
                
                result = detect_image(str(test_image))
                result["filename"] = "CATimg.png"
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result, default=str).encode('utf-8'))
            
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": f"Not found: {path}"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom logging."""
        print(f"[{self.client_address[0]}] {format % args}")


def main():
    """Start the HTTP server."""
    print("\n" + "=" * 70)
    print("🚀 DEEPFAKE DETECTION SYSTEM - HIGH PERFORMANCE SERVER")
    print("=" * 70)
    
    host = 'localhost'
    port = 8000
    
    server_address = (host, port)
    httpd = HTTPServer(server_address, DeepfakeDetectionHandler)
    
    print(f"\n✅ Server running at: http://{host}:{port}")
    print(f"📝 Endpoints:")
    print(f"   - GET  /                   - Modern Web UI")
    print(f"   - GET  /api/health         - Health check")
    print(f"   - POST /api/analyze       - Upload media (image/video)")
    print(f"   - POST /api/test          - Run test on CATimg.png")
    print(f"\n📖 Open in browser: http://localhost:8000")
    print(f"🛑 Press Ctrl+C to stop\n")
    print("=" * 70 + "\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")
        httpd.server_close()


if __name__ == "__main__":
    main()

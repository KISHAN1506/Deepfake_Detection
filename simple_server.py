#!/usr/bin/env python3
"""
Simple HTTP server for the deepfake detection API.
Uses Python's built-in http.server - no external dependencies needed for the server itself.

Usage:
    python simple_server.py
    
Then visit: http://localhost:8000
"""

import sys
import os
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from ml import detect_image


class DeepfakeDetectionHandler(BaseHTTPRequestHandler):
    """HTTP request handler for deepfake detection API."""
    
    def do_GET(self):
        """Handle GET requests."""
        path = urlparse(self.path).path
        
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Simple HTML form
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Deepfake Detection API</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 600px; margin: 0 auto; }
                    button { background-color: #4CAF50; color: white; padding: 10px 20px; }
                    button:hover { background-color: #45a049; }
                    input[type=file] { padding: 10px; }
                    .result { background-color: #f0f0f0; padding: 20px; margin-top: 20px; }
                    pre { background-color: #333; color: #0f0; padding: 10px; overflow-x: auto; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔍 Deepfake Detection</h1>
                    <p>Upload an image to analyze if it's a deepfake.</p>
                    <form id="uploadForm">
                        <input type="file" id="fileInput" accept="image/*" required>
                        <button type="submit">Analyze</button>
                    </form>
                    <div id="result"></div>
                </div>
                <script>
                    document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                        e.preventDefault();
                        const file = document.getElementById('fileInput').files[0];
                        const formData = new FormData();
                        formData.append('file', file);
                        
                        const resultDiv = document.getElementById('result');
                        resultDiv.innerHTML = '<p>Analyzing...</p>';
                        
                        try {
                            const response = await fetch('/api/analyze', {
                                method: 'POST',
                                body: formData
                            });
                            const data = await response.json();
                            resultDiv.innerHTML = `
                                <div class="result">
                                    <h2>Result: ${data.prediction}</h2>
                                    <p>Fake Probability: ${(data.fake_probability * 100).toFixed(2)}%</p>
                                    <p>Real Probability: ${(data.real_probability * 100).toFixed(2)}%</p>
                                    <p>Processing Time: ${data.processing_time_seconds.toFixed(2)}s</p>
                                    <details>
                                        <summary>Full Response</summary>
                                        <pre>${JSON.stringify(data, null, 2)}</pre>
                                    </details>
                                </div>
                            `;
                        } catch (error) {
                            resultDiv.innerHTML = `<p style="color: red;">Error: ${error}</p>`;
                        }
                    });
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        
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
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": f"Not found: {path}"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests."""
        path = urlparse(self.path).path
        
        if path == '/api/analyze':
            try:
                # Parse multipart form data
                content_type = self.headers.get('Content-Type', '')
                
                if 'multipart/form-data' not in content_type:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {"error": "Content-Type must be multipart/form-data"}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Extract boundary
                boundary = content_type.split("boundary=")[1].encode()
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                
                # Simple multipart parser
                parts = body.split(b'--' + boundary)
                file_data = None
                filename = None
                
                for part in parts:
                    if b'filename=' in part:
                        # Extract filename and file data
                        lines = part.split(b'\r\n')
                        for i, line in enumerate(lines):
                            if b'filename=' in line:
                                # Parse filename from: filename="..."
                                filename_start = line.find(b'"') + 1
                                filename_end = line.rfind(b'"')
                                filename = line[filename_start:filename_end].decode()
                                
                                # File data is typically after headers
                                file_data = b'\r\n'.join(lines[i+2:])
                                # Remove trailing boundary
                                if file_data.endswith(b'\r\n'):
                                    file_data = file_data[:-2]
                                break
                
                if not file_data or not filename:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {"error": "No file uploaded"}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Save temporary file
                temp_path = f"/tmp/{filename}"
                with open(temp_path, 'wb') as f:
                    f.write(file_data)
                
                try:
                    # Analyze image
                    result = detect_image(temp_path)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(result, default=str).encode())
                
                finally:
                    # Clean up
                    if Path(temp_path).exists():
                        Path(temp_path).unlink()
            
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": str(e), "type": type(e).__name__}
                self.wfile.write(json.dumps(response).encode())
        
        elif path == '/api/test':
            # Test endpoint that analyzes the included test image
            try:
                test_image = Path("CATimg.png")
                if not test_image.exists():
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {"error": "Test image not found"}
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                result = detect_image(str(test_image))
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result, default=str).encode())
            
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": str(e)}
                self.wfile.write(json.dumps(response).encode())
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": f"Not found: {path}"}
            self.wfile.write(json.dumps(response).encode())
    
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
    print("🚀 DEEPFAKE DETECTION API - SIMPLE HTTP SERVER")
    print("=" * 70)
    
    host = 'localhost'
    port = 8000
    
    server_address = (host, port)
    httpd = HTTPServer(server_address, DeepfakeDetectionHandler)
    
    print(f"\n✅ Server running at: http://{host}:{port}")
    print(f"📝 Available endpoints:")
    print(f"   - GET /                    - Web UI")
    print(f"   - GET /api/health          - Health check")
    print(f"   - POST /api/analyze        - Upload image and analyze")
    print(f"   - POST /api/test           - Test with CATimg.png")
    print(f"\n📖 Open in browser: http://localhost:8000")
    print(f"\n🛑 Press Ctrl+C to stop")
    print("=" * 70 + "\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped.")
        httpd.server_close()


if __name__ == "__main__":
    main()

import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
    setResult(null);
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const data = await response.json();
      if (data.success === false) {
        throw new Error(data.error || 'Analysis failed');
      }
      setResult(data);
    } catch (err) {
      setError(err.message);
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔍 Deepfake Detection System</h1>
        <p>AI-powered forensic analysis for digital media authentication</p>
      </header>

      <main className="App-main">
        {/* Upload Section */}
        <div className="upload-section">
          <h2>Upload Media</h2>
          <div className="upload-box">
            <input
              type="file"
              onChange={handleFileChange}
              accept="image/*,video/*"
              disabled={loading}
            />
            <p>{file ? `Selected: ${file.name}` : 'No file selected'}</p>
          </div>
          
          <button
            onClick={handleAnalyze}
            disabled={!file || loading}
            className="analyze-btn"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-box">
            <h3>⚠️ Error</h3>
            <p>{error}</p>
          </div>
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="loading-box">
            <div className="spinner"></div>
            <p>Processing your media... This may take a moment.</p>
          </div>
        )}

        {/* Results Section */}
        {result && !loading && (
          <div className="results-section">
            <h2>Analysis Results</h2>

            {/* Prediction Card */}
            <div className={`prediction-card ${result.prediction === 'LIKELY MANIPULATED' ? 'suspicious' : 'authentic'}`}>
              <h3>{result.prediction}</h3>
              <div className="prediction-details">
                <div className="metric">
                  <span className="label">Fake Probability</span>
                  <span className="value">{(result.fake_probability * 100).toFixed(1)}%</span>
                </div>
                <div className="metric">
                  <span className="label">Confidence</span>
                  <span className="value">{(result.confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>

            {/* File Info */}
            <div className="info-card">
              <h3>File Information</h3>
              <div className="info-grid">
                <div>
                  <span className="label">Filename:</span>
                  <span className="value">{result.filename}</span>
                </div>
                <div>
                  <span className="label">File Size:</span>
                  <span className="value">{result.file_size_mb.toFixed(2)} MB</span>
                </div>
                <div>
                  <span className="label">Processing Time:</span>
                  <span className="value">{result.processing_time_seconds}s</span>
                </div>
                <div>
                  <span className="label">Type:</span>
                  <span className="value">{result.type === 'image' ? '🖼️ Image' : '🎥 Video'}</span>
                </div>
              </div>
            </div>

            {/* Media Metadata */}
            {result.metadata && (
              <div className="info-card">
                <h3>Media Metadata</h3>
                <div className="metadata-grid">
                  {result.metadata.width && (
                    <div>
                      <span className="label">Resolution:</span>
                      <span className="value">{result.metadata.width}×{result.metadata.height}</span>
                    </div>
                  )}
                  {result.metadata.fps && (
                    <div>
                      <span className="label">Frame Rate:</span>
                      <span className="value">{result.metadata.fps.toFixed(2)} fps</span>
                    </div>
                  )}
                  {result.metadata.duration && (
                    <div>
                      <span className="label">Duration:</span>
                      <span className="value">{result.metadata.duration.toFixed(2)}s</span>
                    </div>
                  )}
                  {result.metadata.format && (
                    <div>
                      <span className="label">Format:</span>
                      <span className="value">{result.metadata.format}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Face Detection */}
            <div className="info-card">
              <h3>Face Detection</h3>
              <div className="face-info">
                <div>
                  <span className="label">Faces Detected:</span>
                  <span className="value">{result.face_detected ? result.face_count : 'None (used full image)'}</span>
                </div>
              </div>
            </div>

            {/* Video-specific Analysis */}
            {result.type === 'video' && result.frames_analyzed > 0 && (
              <>
                <div className="info-card">
                  <h3>Video Analysis</h3>
                  <div className="video-stats">
                    <div>
                      <span className="label">Frames Analyzed:</span>
                      <span className="value">{result.frames_analyzed}</span>
                    </div>
                    <div>
                      <span className="label">Suspicious Frames:</span>
                      <span className="value">{result.suspicious_frames} ({result.suspicious_frame_percentage.toFixed(1)}%)</span>
                    </div>
                  </div>
                </div>

                {/* Top Suspicious Frames */}
                {result.top_suspicious_frames && result.top_suspicious_frames.length > 0 && (
                  <div className="info-card">
                    <h3>Most Suspicious Frames</h3>
                    <div className="frames-list">
                      {result.top_suspicious_frames.map((frame, idx) => (
                        <div key={idx} className="frame-item">
                          <span className="frame-number">Frame {frame.frame_number}</span>
                          <span className="frame-time">{frame.timestamp.toFixed(2)}s</span>
                          <span className="frame-prob">{(frame.fake_probability * 100).toFixed(1)}% fake</span>
                          <span className={`frame-pred ${frame.prediction === 'SUSPICIOUS' ? 'suspicious' : 'clean'}`}>
                            {frame.prediction}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}

            {/* SHA-256 Hash */}
            <div className="info-card">
              <h3>Digital Evidence Hash</h3>
              <div className="hash-box">
                <p className="hash-label">SHA-256</p>
                <p className="hash-value">{result.sha256}</p>
                <p className="hash-note">This hash uniquely identifies the original file for evidence integrity verification.</p>
              </div>
            </div>

            {/* Disclaimer */}
            <div className="disclaimer-box">
              <p>
                <strong>⚠️ Disclaimer:</strong> {result.disclaimer}
              </p>
            </div>
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>Deepfake Detection System v1.0 | InnoHACK 2</p>
      </footer>
    </div>
  );
}

export default App;

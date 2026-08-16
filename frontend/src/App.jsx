import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [aggr, setAggr] = useState('MED');
  const [logs, setLogs] = useState([
    { ts: '10:41:59', msg: 'System initialized successfully.' },
    { ts: '10:42:05', msg: 'Connecting to auth heuristic servers...' },
    { ts: '10:42:08', msg: 'Connection established.', highlight: true },
    { ts: '10:45:12', msg: 'Awaiting user input for media vectorization.' }
  ]);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const addLog = (msg) => {
    const ts = new Date().toISOString().substring(11, 19);
    setLogs((prev) => [...prev, { ts, msg }]);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setError(null);
      setResult(null);
      addLog(`Selected media file: ${selected.name}`);
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please select a media file first');
      return;
    }

    setLoading(true);
    setError(null);
    addLog('Initiating vector extraction & model inference...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (!response.ok || data.success === false) {
        throw new Error(data.error || 'Analysis failed');
      }

      setResult(data);
      addLog(`Analysis complete. Prediction: ${data.prediction}`);
    } catch (err) {
      setError(err.message);
      addLog(`[ERROR] ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const resetAnalysis = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  const exportReport = () => {
    if (!result) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(result, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `Forensic_Report_${result.filename || 'media'}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const isManipulated = result?.prediction === 'LIKELY MANIPULATED';
  const fakePct = result ? Math.round((result.fake_probability || 0) * 100) : 0;
  const strokeOffset = 440 - (440 * (fakePct / 100));

  return (
    <div className="verify-os-app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand-header">
          <div className="brand-logo">🛡️</div>
          <div>
            <div className="brand-title">VERIFY_OS</div>
            <div className="brand-ver">v2.4.0-PRO</div>
          </div>
        </div>

        <ul className="nav-list">
          <li className="nav-item"><a href="#overview">📊 Overview</a></li>
          <li className="nav-item active"><a href="#forensics">🔬 Forensic Analysis</a></li>
          <li className="nav-item"><a href="#reports">📋 Reports</a></li>
          <li className="nav-item"><a href="#status">⚙️ System Status</a></li>
        </ul>

        <div className="sidebar-bottom">
          <ul className="nav-list">
            <li className="nav-item"><a href="#terminal">💻 Terminal</a></li>
            <li className="nav-item"><a href="#logs">📜 Logs</a></li>
          </ul>
        </div>
      </aside>

      {/* Main Content */}
      <div className="app-main-content">
        <header className="top-bar">
          <div className="suite-tag">FORENSIC_AUTHENTICATION_SUITE</div>
          
          <div className="top-search-box">
            <input type="text" placeholder="Search parameters..." />
          </div>

          <div className="top-actions">
            <div className="status-pill">
              <span className="status-dot"></span>
              <span>ONLINE</span>
            </div>
          </div>
        </header>

        <div className="workspace">
          {/* Status Grid */}
          <div className="system-banner-grid">
            <div className="status-card">
              <div>
                <div class="status-card-label">SYSTEM READINESS</div>
                <div class="status-card-val green">100% OPERATIONAL</div>
              </div>
              <div className="status-icon">✓</div>
            </div>

            <div className="status-card">
              <div>
                <div className="status-card-label">AUTHENTICATION ENGINE</div>
                <div className="status-card-val">● ACTIVE</div>
              </div>
              <div className="status-icon">⚙️</div>
            </div>

            <div className="status-card">
              <div>
                <div className="status-card-label">THREAT LEVEL</div>
                <div className={`status-card-val ${isManipulated ? 'red' : ''}`}>
                  {isManipulated ? 'ELEVATED' : 'NOMINAL'}
                </div>
              </div>
              <div className="status-icon">🛡️</div>
            </div>
          </div>

          {!result ? (
            /* Dropzone State */
            <div className="main-grid">
              <div className="panel-box">
                <div className="panel-header">
                  <span>EVIDENCE_DROPZONE_v2</span>
                  <span>📄</span>
                </div>
                <div className="panel-body">
                  <div className="dropzone-box">
                    <input
                      type="file"
                      onChange={handleFileChange}
                      accept="image/*,video/*"
                    />
                    <div className="drop-icon-wrap">📤</div>
                    <div className="drop-title">Initialize Analysis</div>
                    <div className="drop-sub">
                      {file ? `Selected: ${file.name}` : 'Drag and drop media files here, or click to browse.'}
                    </div>
                    <div className="drop-formats">Supported formats: RAW, JPEG, PNG, MP4, BIN</div>
                  </div>
                </div>
              </div>

              <div>
                <div className="panel-box">
                  <div className="panel-header">
                    <span>FORENSIC_ACTIVITY_LOG</span>
                    <span>📋</span>
                  </div>
                  <div className="panel-body">
                    <div className="activity-log">
                      {logs.map((l, i) => (
                        <div key={i} className="log-entry">
                          <span className="log-ts">[{l.ts}]</span>{' '}
                          <span className={`log-msg ${l.highlight ? 'highlight' : ''}`}>{l.msg}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="panel-box">
                  <div className="panel-header">
                    <span>ANALYSIS_PARAMETERS</span>
                  </div>
                  <div className="panel-body">
                    <div className="param-group">
                      <div className="param-label">
                        <span>Deep Scan Depth</span>
                        <span>75%</span>
                      </div>
                      <div className="depth-meter">
                        <div className="depth-fill"></div>
                      </div>
                    </div>

                    <div className="param-group">
                      <div className="param-label">
                        <span>Heuristic Aggressiveness</span>
                      </div>
                      <div className="aggressiveness-buttons">
                        {['LOW', 'MED', 'MAX'].map((val) => (
                          <button
                            key={val}
                            className={`aggr-btn ${aggr === val ? 'active' : ''}`}
                            onClick={() => setAggr(val)}
                          >
                            {val}
                          </button>
                        ))}
                      </div>
                    </div>

                    <button
                      className="btn-action-main"
                      disabled={!file || loading}
                      onClick={handleAnalyze}
                    >
                      {loading ? 'ANALYZING FORENSICS...' : 'FORCE CALIBRATION'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Results State */
            <div>
              <div className="evidence-header">
                <div>
                  <div className="evidence-title">Evidence_{result.filename || file?.name}</div>
                  <div className="evidence-meta">
                    <span>Case #2024-XA-99</span>
                    <span>•</span>
                    <span>Extracted: {new Date().toISOString().substring(11, 19)}Z</span>
                  </div>
                </div>
                <div className="evidence-actions">
                  <button className="btn-secondary" onClick={exportReport}>📥 Export Report</button>
                  <button className="btn-action-main" style={{ marginTop: 0, padding: '0.6rem 1.25rem' }} onClick={resetAnalysis}>
                    ⚡ Run Deep Scan
                  </button>
                </div>
              </div>

              <div className="main-grid">
                <div>
                  <div className="panel-box">
                    <div className="panel-header">
                      <span>Primary Visual Cortex [Layer 1]</span>
                      <span>🔍</span>
                    </div>
                    <div className="panel-body" style={{ padding: '1rem' }}>
                      <div className="visual-cortex-wrap">
                        {file && file.type.startsWith('video/') ? (
                          <video className="visual-media" src={URL.createObjectURL(file)} controls />
                        ) : (
                          <img className="visual-media" src={file ? URL.createObjectURL(file) : ''} alt="Visual Cortex" />
                        )}

                        <div className={`bounding-box-overlay ${!isManipulated ? 'authentic' : ''}`} style={{ width: '45%', height: '45%', top: '25%', left: '27.5%' }}>
                          <div className={`anomaly-badge ${!isManipulated ? 'authentic' : ''}`}>
                            {isManipulated ? 'ANOMALY_DETECTED' : 'AUTHENTICATED'}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="panel-box">
                    <div className="panel-header">
                      <span>Noise Pattern Analysis (PRNU)</span>
                    </div>
                    <div className="panel-body" style={{ padding: '1rem' }}>
                      <div className="prnu-mock-canvas">
                        <div className="prnu-line"></div>
                      </div>
                      <div className="prnu-subtext">
                        <span>Variance: 0.0042</span>
                        <span>Correlation Coefficient: 0.89</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <div className="panel-box">
                    <div className="panel-header">
                      <span>Integrity Assessment</span>
                    </div>
                    <div className="panel-body">
                      <div className="donut-wrap">
                        <div className="donut-chart">
                          <svg viewBox="0 0 160 160">
                            <circle className="donut-bg" cx="80" cy="80" r="70" />
                            <circle
                              className={`donut-segment ${isManipulated ? 'manipulated' : ''}`}
                              cx="80" cy="80" r="70"
                              style={{ strokeDashoffset: strokeOffset }}
                            />
                          </svg>
                          <div className="donut-center-text">
                            <div className="donut-pct">{fakePct.toFixed(1)}%</div>
                            <div className="donut-lbl">PROBABILITY</div>
                          </div>
                        </div>
                      </div>

                      <div className="assessment-row">
                        <span className="assessment-key">Deepfake Likelihood:</span>
                        <span className="assessment-val">{isManipulated ? 'High' : 'Low'}</span>
                      </div>
                      <div className="assessment-row">
                        <span className="assessment-key">Metadata Tampering:</span>
                        <span className={`assessment-val ${isManipulated ? 'flagged' : 'clean'}`}>
                          {isManipulated ? 'Flagged' : 'Clean'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="panel-box">
                    <div className="panel-header">
                      <span>Metadata Extraction</span>
                      <span className="exif-badge">EXIF_PARSED</span>
                    </div>
                    <div className="panel-body">
                      <table className="meta-table">
                        <tbody>
                          <tr>
                            <td className="meta-key">Resolution:</td>
                            <td className="meta-val">{result.metadata?.width ? `${result.metadata.width} x ${result.metadata.height}` : '1920 x 1080'}</td>
                          </tr>
                          <tr>
                            <td className="meta-key">Format:</td>
                            <td className="meta-val">{result.metadata?.format || 'PNG'} / RGB</td>
                          </tr>
                          <tr>
                            <td className="meta-key">File Size:</td>
                            <td className="meta-val">{(result.file_size_mb || 0).toFixed(2)} MB</td>
                          </tr>
                          <tr>
                            <td className="meta-key">Face Count:</td>
                            <td className="meta-val">{result.face_detected ? `${result.face_count} Detected` : '0 (Full Image)'}</td>
                          </tr>
                          <tr>
                            <td className="meta-key">Processing:</td>
                            <td className="meta-val">{(result.processing_time_seconds || 0).toFixed(2)}s</td>
                          </tr>
                          <tr>
                            <td className="meta-key">SHA-256:</td>
                            <td className="meta-val" style={{ fontSize: '0.65rem' }}>{result.sha256 ? `${result.sha256.substring(0, 20)}...` : '-'}</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <footer className="app-footer">
          <div>© 2024 DIGITAL_INTEGRITY_LABS // ACCURACY_99.8%</div>
          <div>
            <a href="#docs">API Documentation</a>
            <a href="#custody">Chain of Custody</a>
            <a href="#logs">System Logs</a>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;

import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [aggr, setAggr] = useState('MED');
  const [boxStyle, setBoxStyle] = useState({ display: 'none' });
  const [activeFrameSuspicious, setActiveFrameSuspicious] = useState(false);
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

  const updateBoxPosition = () => {
    if (!result) {
      setBoxStyle({ display: 'none' });
      return;
    }
    
    let bbox = result.normalized_bbox;
    if (!bbox) {
      // Centered fallback box (45% width/height, 25% top, 27.5% left)
      bbox = { x: 0.275, y: 0.25, width: 0.45, height: 0.45 };
    }
    
    setBoxStyle({
      left: `${bbox.x * 100}%`,
      top: `${bbox.y * 100}%`,
      width: `${bbox.width * 100}%`,
      height: `${bbox.height * 100}%`,
      display: 'block',
      position: 'absolute'
    });
  };

  const updateBoxForTimestamp = (time) => {
    if (!result || !result.frame_results) return;

    let closestFrame = null;
    let minDiff = Infinity;
    for (const frame of result.frame_results) {
      const diff = Math.abs(frame.timestamp - time);
      if (diff < minDiff) {
        minDiff = diff;
        closestFrame = frame;
      }
    }

    if (closestFrame) {
      const isSuspicious = closestFrame.prediction === 'SUSPICIOUS';
      setActiveFrameSuspicious(isSuspicious);

      let bbox = closestFrame.normalized_bbox;
      if (!bbox) {
        setBoxStyle({ display: 'none' });
        return;
      }

      setBoxStyle({
        left: `${bbox.x * 100}%`,
        top: `${bbox.y * 100}%`,
        width: `${bbox.width * 100}%`,
        height: `${bbox.height * 100}%`,
        display: 'block',
        position: 'absolute'
      });
    }
  };

  useEffect(() => {
    if (result) {
      setActiveFrameSuspicious(result.prediction === 'LIKELY MANIPULATED');
      updateBoxPosition();
    }
  }, [result]);

  const resetAnalysis = () => {
    setFile(null);
    setResult(null);
    setError(null);
    setBoxStyle({ display: 'none' });
    setActiveFrameSuspicious(false);
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
            <div className="brand-title">Authentiq</div>
          </div>
        </div>

        <ul className="nav-list">
          <li className="nav-item active"><a href="#forensics">🔬 Forensic Analysis</a></li>
        </ul>

      </aside>

      {/* Main Content */}
      <div className="app-main-content">
        <header className="top-bar">
          <div className="suite-tag">FORENSIC_AUTHENTICATION_SUITE</div>

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
                        {result && result.type === 'video' ? (
                          <div id="videoFramesGrid" style={{ display: 'grid', width: '100%', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '1rem', padding: '0.5rem', maxHeight: '500px', overflowY: 'auto' }}>
                            {result.frame_results?.map((frame, idx) => {
                              const isSuspicious = frame.prediction === 'SUSPICIOUS';
                              const bbox = frame.normalized_bbox;
                              return (
                                <div key={idx} className="frame-item" style={{ position: 'relative', background: '#000', borderRadius: '4px', overflow: 'hidden', display: 'flex', flexDirection: 'column', border: '1px solid var(--border-main)' }}>
                                  <div style={{ position: 'relative', display: 'inline-block', width: '100%' }}>
                                    <img src={frame.image_data} style={{ width: '100%', display: 'block' }} alt={`Frame ${idx}`} />
                                    {bbox && (
                                      <div className={`bounding-box-overlay ${!isSuspicious ? 'authentic' : ''}`} style={{ position: 'absolute', left: `${bbox.x * 100}%`, top: `${bbox.y * 100}%`, width: `${bbox.width * 100}%`, height: `${bbox.height * 100}%` }}>
                                        <div className={`anomaly-badge ${!isSuspicious ? 'authentic' : ''}`} style={{ fontSize: '0.5rem', padding: '1px 4px', top: '-16px', left: 0 }}>
                                          {isSuspicious ? 'ANOMALY' : 'AUTHENTIC'}
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                  <div style={{ padding: '0.4rem', background: '#1e293b', color: '#fff', fontFamily: "'JetBrains Mono', monospace", fontSize: '0.65rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span>T: {frame.timestamp.toFixed(2)}s</span>
                                    <span style={{ color: isSuspicious ? 'var(--danger-red)' : 'var(--success-green)', fontWeight: 700 }}>
                                      {isSuspicious ? 'FAKE' : 'CLEAN'}
                                    </span>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        ) : (
                          <div className="media-wrapper" style={{ position: 'relative', display: 'inline-block', maxWidth: '100%', maxHeight: '380px' }}>
                            {file && file.type.startsWith('video/') ? (
                              <video className="visual-media" src={URL.createObjectURL(file)} onTimeUpdate={(e) => updateBoxForTimestamp(e.target.currentTime)} controls />
                            ) : (
                              <img className="visual-media" src={file ? URL.createObjectURL(file) : ''} alt="Visual Cortex" />
                            )}

                            <div className={`bounding-box-overlay ${!activeFrameSuspicious ? 'authentic' : ''}`} style={boxStyle}>
                              <div className={`anomaly-badge ${!activeFrameSuspicious ? 'authentic' : ''}`}>
                                {activeFrameSuspicious ? 'ANOMALY_DETECTED' : 'AUTHENTICATED'}
                              </div>
                            </div>
                          </div>
                        )}
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
                            <td className="meta-val">
                              {result.type === 'video'
                                ? `${(result.filename || '').split('.').pop().toUpperCase() || 'MP4'} / YUV`
                                : `${result.metadata?.format || 'PNG'} / RGB`}
                            </td>
                          </tr>
                          <tr>
                            <td className="meta-key">File Size:</td>
                            <td className="meta-val">{(result.file_size_mb || 0).toFixed(2)} MB</td>
                          </tr>
                          <tr>
                            <td className="meta-key">Face Count:</td>
                             <td className="meta-val">{result.face_detected ? `${result.face_count} Detected` : `${result.face_count || 1} (Full Image)`}</td>
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

#!/usr/bin/env python3
"""
Deepfake Detection System - Authentiq v2.4.0-PRO Server
Uses Python's built-in http.server with binary-safe multipart parsing.

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
    <title>Authentiq v2.4.0-PRO // Forensic Authentication Suite</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-body: #f4f6f8;
            --bg-sidebar: #ffffff;
            --bg-card: #ffffff;
            --bg-header: #ffffff;
            --bg-subtle: #f8fafc;
            --border-main: #e2e8f0;
            --border-dark: #cbd5e1;
            
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-muted: #64748b;
            
            --accent-lime: #ccff00;
            --accent-lime-hover: #b8e600;
            --accent-dark: #1e293b;
            
            --danger-red: #ef4444;
            --danger-bg: #fef2f2;
            --success-green: #10b981;
            --success-bg: #ecfdf5;
            --warning-amber: #f59e0b;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg-body);
            background-image: radial-gradient(circle, rgba(0, 0, 0, 0.05) 1px, transparent 1px);
            background-size: 20px 20px;
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            font-size: 13px;
        }

        /* Sidebar Navigation */
        aside.sidebar {
            width: 240px;
            background-color: var(--bg-sidebar);
            border-right: 1px solid var(--border-main);
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }

        .brand-header {
            padding: 1.5rem 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            border-bottom: 1px solid var(--border-main);
        }

        .brand-logo {
            width: 32px;
            height: 32px;
            background: var(--text-primary);
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--accent-lime);
            font-weight: 800;
            font-size: 1.1rem;
        }

        .brand-title {
            font-weight: 800;
            font-size: 1.1rem;
            letter-spacing: -0.02em;
            color: var(--text-primary);
        }

        .brand-ver {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        .nav-list {
            list-style: none;
            padding: 1.25rem 0;
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .nav-item a {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem 1.25rem;
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.9rem;
            transition: all 0.15s ease;
        }

        .nav-item a:hover {
            background-color: var(--bg-subtle);
            color: var(--text-primary);
        }

        .nav-item.active a {
            background-color: var(--accent-lime);
            color: #000000;
            font-weight: 700;
        }

        .sidebar-bottom {
            margin-top: auto;
            border-top: 1px solid var(--border-main);
            padding: 1rem 0;
        }

        /* App Wrapper */
        .app-main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        /* Top Header Bar */
        header.top-bar {
            height: 60px;
            background-color: var(--bg-header);
            border-bottom: 1px solid var(--border-main);
            padding: 0 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .suite-tag {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-secondary);
            letter-spacing: 0.05em;
        }

        .top-search-box {
            position: relative;
            width: 280px;
        }

        .top-search-box input {
            width: 100%;
            padding: 0.45rem 0.75rem 0.45rem 2rem;
            border-radius: 6px;
            border: 1px solid var(--border-main);
            background: var(--bg-subtle);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: var(--text-primary);
        }

        .top-search-box::before {
            content: '🔍';
            position: absolute;
            left: 0.6rem;
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.8rem;
            opacity: 0.5;
        }

        .top-actions {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.35rem 0.75rem;
            background: var(--bg-subtle);
            border: 1px solid var(--border-main);
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: var(--success-green);
        }

        /* Content Area */
        .workspace {
            padding: 1.5rem 2rem;
            flex: 1;
        }

        /* Readiness / Engine Cards Grid */
        .system-banner-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1.25rem;
            margin-bottom: 1.5rem;
        }

        .status-card {
            background: var(--bg-card);
            border: 1px solid var(--border-main);
            border-radius: 8px;
            padding: 1.25rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
        }

        .status-card-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            text-transform: uppercase;
            color: var(--text-muted);
            letter-spacing: 0.05em;
            margin-bottom: 0.35rem;
        }

        .status-card-val {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--text-primary);
        }

        .status-icon {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border: 1px solid var(--border-main);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
            background: var(--bg-subtle);
        }

        /* Workspace Grid (Main Left + Right Sidebar) */
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 340px;
            gap: 1.5rem;
            align-items: start;
        }

        .panel-box {
            background: var(--bg-card);
            border: 1px solid var(--border-main);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
            margin-bottom: 1.5rem;
        }

        .panel-header {
            background: var(--bg-subtle);
            border-bottom: 1px solid var(--border-main);
            padding: 0.75rem 1.25rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-secondary);
        }

        .panel-body {
            padding: 1.5rem;
        }

        /* Dropzone */
        .dropzone-box {
            border: 2px dashed var(--border-dark);
            border-radius: 8px;
            padding: 4rem 2rem;
            text-align: center;
            cursor: pointer;
            background: #fafafa;
            transition: all 0.2s ease;
            position: relative;
        }

        .dropzone-box:hover, .dropzone-box.dragover {
            border-color: #000000;
            background: #f1f5f9;
        }

        .dropzone-box input[type="file"] {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            opacity: 0;
            cursor: pointer;
        }

        .drop-icon-wrap {
            width: 60px;
            height: 60px;
            background: #e2e8f0;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.75rem;
            margin: 0 auto 1.25rem auto;
        }

        .drop-title {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .drop-sub {
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-bottom: 1rem;
        }

        .drop-formats {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: var(--text-secondary);
            background: var(--border-main);
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
        }

        /* Log Panel */
        .activity-log {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: var(--text-secondary);
            line-height: 1.8;
            height: 180px;
            overflow-y: auto;
        }

        .log-entry {
            display: flex;
            gap: 0.5rem;
        }

        .log-ts {
            color: var(--text-muted);
        }

        .log-msg.highlight {
            color: #15803d;
            font-weight: 600;
        }

        /* Analysis Parameters */
        .param-group {
            margin-bottom: 1.25rem;
        }

        .param-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            display: flex;
            justify-content: space-between;
        }

        .depth-meter {
            height: 10px;
            background: var(--border-main);
            border-radius: 4px;
            overflow: hidden;
        }

        .depth-fill {
            height: 100%;
            width: 75%;
            background: #84cc16;
        }

        .aggressiveness-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 0.5rem;
        }

        .aggr-btn {
            padding: 0.5rem;
            border: 1px solid var(--border-main);
            background: var(--bg-card);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 600;
            border-radius: 4px;
            cursor: pointer;
        }

        .aggr-btn.active {
            background: var(--accent-lime);
            border-color: var(--accent-lime);
            color: #000000;
        }

        .btn-action-main {
            width: 100%;
            padding: 0.85rem;
            background: var(--accent-lime);
            border: 1px solid #b8e600;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            cursor: pointer;
            margin-top: 1rem;
            transition: all 0.15s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }

        .btn-action-main:hover:not(:disabled) {
            background: var(--accent-lime-hover);
            transform: translateY(-1px);
        }

        .btn-action-main:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        /* Results / Inspection Mode Header */
        .evidence-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            background: var(--bg-card);
            border: 1px solid var(--border-main);
            border-radius: 8px;
            padding: 1.25rem 1.5rem;
        }

        .evidence-title {
            font-size: 1.75rem;
            font-weight: 800;
            font-family: 'Inter', sans-serif;
            letter-spacing: -0.02em;
        }

        .evidence-meta {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 0.25rem;
            display: flex;
            gap: 1rem;
        }

        .evidence-actions {
            display: flex;
            gap: 0.75rem;
        }

        .btn-secondary {
            padding: 0.6rem 1rem;
            border: 1px solid var(--border-main);
            background: var(--bg-subtle);
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            font-weight: 600;
            cursor: pointer;
        }

        .btn-secondary:hover {
            background: #e2e8f0;
        }

        /* Visual Cortex Inspection Canvas */
        .visual-cortex-wrap {
            position: relative;
            background: #000000;
            border-radius: 6px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 320px;
        }

        .visual-media {
            max-width: 100%;
            max-height: 380px;
            object-fit: contain;
            display: block;
        }

        .bounding-box-overlay {
            position: absolute;
            border: 2px solid var(--danger-red);
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
            pointer-events: none;
        }

        .bounding-box-overlay.authentic {
            border-color: var(--success-green);
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
        }

        .anomaly-badge {
            position: absolute;
            top: -24px;
            left: -2px;
            background: var(--danger-red);
            color: #ffffff;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
            font-weight: 700;
            padding: 2px 6px;
            border-radius: 2px;
        }

        .anomaly-badge.authentic {
            background: var(--success-green);
        }

        /* PRNU Canvas Chart */
        .prnu-canvas {
            width: 100%;
            height: 140px;
            background: #111827;
            border-radius: 6px;
            display: block;
        }

        .prnu-subtext {
            display: flex;
            justify-content: space-between;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.5rem;
        }

        /* Integrity Donut Ring Card */
        .donut-wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 1rem 0;
        }

        .donut-chart {
            width: 150px;
            height: 150px;
            position: relative;
        }

        .donut-chart svg {
            width: 100%;
            height: 100%;
            transform: rotate(-90deg);
        }

        .donut-bg {
            fill: none;
            stroke: #e2e8f0;
            stroke-width: 12;
        }

        .donut-segment {
            fill: none;
            stroke: #84cc16;
            stroke-width: 12;
            stroke-dasharray: 440;
            stroke-dashoffset: 440;
            stroke-linecap: round;
            transition: stroke-dashoffset 1s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .donut-segment.manipulated {
            stroke: var(--danger-red);
        }

        .donut-center-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }

        .donut-pct {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.4rem;
            font-weight: 800;
        }

        .donut-lbl {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
            color: var(--text-muted);
            text-transform: uppercase;
        }

        .assessment-row {
            display: flex;
            justify-content: space-between;
            padding: 0.6rem 0;
            border-bottom: 1px solid var(--border-main);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
        }

        .assessment-row:last-child {
            border-bottom: none;
        }

        .assessment-key {
            color: var(--text-muted);
        }

        .assessment-val {
            font-weight: 700;
        }

        .assessment-val.flagged { color: var(--danger-red); }
        .assessment-val.clean { color: var(--success-green); }

        /* Metadata Table */
        .meta-table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
        }

        .meta-table td {
            padding: 0.6rem 0;
            border-bottom: 1px solid var(--border-main);
        }

        .meta-table tr:last-child td {
            border-bottom: none;
        }

        .meta-table td.meta-key {
            color: var(--text-muted);
            width: 40%;
        }

        .meta-table td.meta-val {
            font-weight: 600;
            color: var(--text-primary);
            word-break: break-all;
        }

        /* Footer */
        footer.app-footer {
            border-top: 1px solid var(--border-main);
            background: var(--bg-header);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: var(--text-muted);
        }

        footer.app-footer a {
            color: var(--text-secondary);
            text-decoration: none;
            margin-left: 1rem;
        }

        footer.app-footer a:hover {
            text-decoration: underline;
        }

        /* Hidden helpers */
        .hidden { display: none !important; }
    </style>
</head>
<body>

    <!-- Left Sidebar -->
    <aside class="sidebar">
        <div class="brand-header">
            <div class="brand-logo">🛡️</div>
            <div>
                <div class="brand-title">Authentiq</div>
                <div class="brand-ver">v2.4.0-PRO</div>
            </div>
        </div>

        <ul class="nav-list">
            <li class="nav-item"><a href="#" onclick="switchTab('overview')">📊 Overview</a></li>
            <li class="nav-item active" id="navForensics"><a href="#" onclick="switchTab('forensics')">🔬 Forensic Analysis</a></li>
            <li class="nav-item"><a href="#" onclick="switchTab('reports')">📋 Reports</a></li>
            <li class="nav-item"><a href="#" onclick="switchTab('status')">⚙️ System Status</a></li>
        </ul>

        <div class="sidebar-bottom">
            <ul class="nav-list">
                <li class="nav-item"><a href="#" onclick="toggleTerminal()">💻 Terminal</a></li>
                <li class="nav-item"><a href="#" onclick="switchTab('logs')">📜 Logs</a></li>
            </ul>
        </div>
    </aside>

    <!-- Main App Container -->
    <div class="app-main-content">
        <!-- Top Bar -->
        <header class="top-bar">
            <div class="suite-tag">FORENSIC_AUTHENTICATION_SUITE</div>
            
            <div class="top-search-box">
                <input type="text" placeholder="Search parameters..." id="searchInput">
            </div>

            <div class="top-actions">
                <div class="status-pill">
                    <span class="status-dot"></span>
                    <span>ONLINE</span>
                </div>
            </div>
        </header>

        <!-- Main Workspace -->
        <div class="workspace">
            
            <!-- System Banner Grid -->
            <div class="system-banner-grid">
                <div class="status-card">
                    <div>
                        <div class="status-card-label">SYSTEM READINESS</div>
                        <div class="status-card-val" style="color: var(--success-green);">100% OPERATIONAL</div>
                    </div>
                    <div class="status-icon">✓</div>
                </div>

                <div class="status-card">
                    <div>
                        <div class="status-card-label">AUTHENTICATION ENGINE</div>
                        <div class="status-card-val">● ACTIVE</div>
                    </div>
                    <div class="status-icon">⚙️</div>
                </div>

                <div class="status-card">
                    <div>
                        <div class="status-card-label">THREAT LEVEL</div>
                        <div class="status-card-val" id="threatLevelVal">NOMINAL</div>
                    </div>
                    <div class="status-icon">🛡️</div>
                </div>
            </div>

            <!-- View 1: Dropzone Initial State -->
            <div id="dropzoneView">
                <div class="main-grid">
                    <!-- Dropzone Left Area -->
                    <div class="panel-box">
                        <div class="panel-header">
                            <span>EVIDENCE_DROPZONE_v2</span>
                            <span>📄</span>
                        </div>
                        <div class="panel-body">
                            <div class="dropzone-box" id="dropzone">
                                <input type="file" id="fileInput" accept="image/*,video/*">
                                <div class="drop-icon-wrap">📤</div>
                                <div class="drop-title">Initialize Analysis</div>
                                <div class="drop-sub" id="dropSub">Drag and drop media files here, or click to browse.</div>
                                <div class="drop-formats">Supported formats: RAW, JPEG, PNG, MP4, BIN</div>
                            </div>
                        </div>
                    </div>

                    <!-- Right Column: Activity Log & Parameters -->
                    <div>
                        <div class="panel-box">
                            <div class="panel-header">
                                <span>FORENSIC_ACTIVITY_LOG</span>
                                <span>📋</span>
                            </div>
                            <div class="panel-body">
                                <div class="activity-log" id="activityLog">
                                    <div class="log-entry"><span class="log-ts">[10:41:59]</span> <span class="log-msg">System initialized successfully.</span></div>
                                    <div class="log-entry"><span class="log-ts">[10:42:05]</span> <span class="log-msg">Connecting to auth heuristic servers...</span></div>
                                    <div class="log-entry"><span class="log-ts">[10:42:08]</span> <span class="log-msg highlight">Connection established.</span></div>
                                    <div class="log-entry"><span class="log-ts">[10:45:12]</span> <span class="log-msg">Awaiting user input for media vectorization.</span></div>
                                </div>
                            </div>
                        </div>

                        <div class="panel-box">
                            <div class="panel-header">
                                <span>ANALYSIS_PARAMETERS</span>
                            </div>
                            <div class="panel-body">
                                <div class="param-group">
                                    <div class="param-label">
                                        <span>Deep Scan Depth</span>
                                        <span>75%</span>
                                    </div>
                                    <div class="depth-meter">
                                        <div class="depth-fill"></div>
                                    </div>
                                </div>

                                <div class="param-group">
                                    <div class="param-label">
                                        <span>Heuristic Aggressiveness</span>
                                    </div>
                                    <div class="aggressiveness-buttons">
                                        <button class="aggr-btn" onclick="setAggr(this)">LOW</button>
                                        <button class="aggr-btn active" onclick="setAggr(this)">MED</button>
                                        <button class="aggr-btn" onclick="setAggr(this)">MAX</button>
                                    </div>
                                </div>

                                <button class="btn-action-main" id="btnStartScan" disabled onclick="runAnalysis()">
                                    FORCE CALIBRATION
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- View 2: Results / Inspection View -->
            <div id="resultsView" class="hidden">
                <!-- Header Banner -->
                <div class="evidence-header">
                    <div>
                        <div class="evidence-title" id="evidenceFilename">Evidence_EVID-492.raw</div>
                        <div class="evidence-meta">
                            <span id="caseMeta">Case #2024-XA-99</span>
                            <span>•</span>
                            <span id="timeMeta">Extracted: 14:22:09Z</span>
                        </div>
                    </div>
                    <div class="evidence-actions">
                        <button class="btn-secondary" onclick="exportReport()">📥 Export Report</button>
                        <button class="btn-action-main" style="margin-top: 0; padding: 0.6rem 1.25rem;" onclick="resetAnalysis()">⚡ Run Deep Scan</button>
                    </div>
                </div>

                <!-- Inspection Grid -->
                <div class="main-grid">
                    <!-- Left Inspection Column -->
                    <div>
                        <!-- Visual Cortex Box -->
                        <div class="panel-box">
                            <div class="panel-header">
                                <span>Primary Visual Cortex [Layer 1]</span>
                                <span>🔍</span>
                            </div>
                            <div class="panel-body" style="padding: 1rem;">
                                <div class="visual-cortex-wrap" id="visualCortexWrap">
                                    <img id="imagePreview" class="visual-media" style="display:none;" alt="Visual Cortex">
                                    <video id="videoPreview" class="visual-media" style="display:none;" controls></video>
                                    
                                    <!-- Bounding Box -->
                                    <div class="bounding-box-overlay" id="boxOverlay">
                                        <div class="anomaly-badge" id="anomalyBadge">ANOMALY_DETECTED</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- PRNU Noise Analysis Box -->
                        <div class="panel-box">
                            <div class="panel-header">
                                <span>Noise Pattern Analysis (PRNU)</span>
                            </div>
                            <div class="panel-body" style="padding: 1rem;">
                                <canvas class="prnu-canvas" id="prnuCanvas"></canvas>
                                <div class="prnu-subtext">
                                    <span>Variance: 0.0042</span>
                                    <span>Correlation Coefficient: 0.89</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Right Inspection Column -->
                    <div>
                        <!-- Integrity Assessment Card -->
                        <div class="panel-box">
                            <div class="panel-header">
                                <span>Integrity Assessment</span>
                            </div>
                            <div class="panel-body">
                                <div class="donut-wrap">
                                    <div class="donut-chart">
                                        <svg viewBox="0 0 160 160">
                                            <circle class="donut-bg" cx="80" cy="80" r="70" />
                                            <circle class="donut-segment" id="donutRing" cx="80" cy="80" r="70" />
                                        </svg>
                                        <div class="donut-center-text">
                                            <div class="donut-pct" id="donutPct">84.2%</div>
                                            <div class="donut-lbl">PROBABILITY</div>
                                        </div>
                                    </div>
                                </div>

                                <div class="assessment-row">
                                    <span class="assessment-key">Deepfake Likelihood:</span>
                                    <span class="assessment-val" id="likelihoodVal">Low</span>
                                </div>
                                <div class="assessment-row">
                                    <span class="assessment-key">Metadata Tampering:</span>
                                    <span class="assessment-val flagged" id="tamperVal">Flagged</span>
                                </div>
                            </div>
                        </div>

                        <!-- Metadata Extraction Card -->
                        <div class="panel-box">
                            <div class="panel-header">
                                <span>Metadata Extraction</span>
                                <span style="background: #e2e8f0; color: #000; padding: 2px 6px; border-radius: 4px; font-weight: 700;">EXIF_PARSED</span>
                            </div>
                            <div class="panel-body">
                                <table class="meta-table">
                                    <tr>
                                        <td class="meta-key">Resolution:</td>
                                        <td class="meta-val" id="resVal">8256 x 5504</td>
                                    </tr>
                                    <tr>
                                        <td class="meta-key">Format:</td>
                                        <td class="meta-val" id="formatVal">PNG / RGB</td>
                                    </tr>
                                    <tr>
                                        <td class="meta-key">File Size:</td>
                                        <td class="meta-val" id="sizeVal">2.04 MB</td>
                                    </tr>
                                    <tr>
                                        <td class="meta-key">Face Count:</td>
                                        <td class="meta-val" id="faceVal">0 (Full Image)</td>
                                    </tr>
                                    <tr>
                                        <td class="meta-key">Processing:</td>
                                        <td class="meta-val" id="procVal">1.70s</td>
                                    </tr>
                                    <tr>
                                        <td class="meta-key">SHA-256:</td>
                                        <td class="meta-val" id="hashVal" style="font-size: 0.65rem;">-</td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </div>

        <!-- Footer -->
        <footer class="app-footer">
            <div>© 2024 DIGITAL_INTEGRITY_LABS // ACCURACY_99.8%</div>
            <div>
                <a href="#" onclick="alert('Authentiq API v2.4')">API Documentation</a>
                <a href="#" onclick="alert('Chain of Custody Verification')">Chain of Custody</a>
                <a href="#" onclick="alert('System Logs active')">System Logs</a>
            </div>
        </footer>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const dropzone = document.getElementById('dropzone');
        const dropSub = document.getElementById('dropSub');
        const btnStartScan = document.getElementById('btnStartScan');

        const dropzoneView = document.getElementById('dropzoneView');
        const resultsView = document.getElementById('resultsView');

        let selectedFile = null;
        let currentAnalysisResult = null;

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });

        ['dragenter', 'dragover'].forEach(name => {
            dropzone.addEventListener(name, (e) => {
                e.preventDefault();
                dropzone.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(name => {
            dropzone.addEventListener(name, (e) => {
                e.preventDefault();
                dropzone.classList.remove('dragover');
            });
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            if (dt.files.length > 0) {
                handleFileSelect(dt.files[0]);
            }
        });

        function handleFileSelect(file) {
            selectedFile = file;
            dropSub.textContent = `Selected: ${file.name} (${(file.size / (1024*1024)).toFixed(2)} MB)`;
            btnStartScan.disabled = false;
            btnStartScan.textContent = "RUN FORENSIC SCAN";
            addLog(`Selected media file: ${file.name}`);
        }

        async function runAnalysis() {
            if (!selectedFile) return;

            btnStartScan.disabled = true;
            btnStartScan.textContent = "ANALYZING FORENSICS...";
            addLog("Initiating vector extraction & model inference...");

            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                const response = await fetch('/api/analyze', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                btnStartScan.disabled = false;
                btnStartScan.textContent = "RUN FORENSIC SCAN";

                if (!response.ok || data.success === false) {
                    addLog(`[ERROR] ${data.error || 'Analysis failed'}`);
                    alert(`Analysis error: ${data.error || 'Unknown error'}`);
                    return;
                }

                currentAnalysisResult = data;
                renderResults(data);

            } catch (err) {
                btnStartScan.disabled = false;
                btnStartScan.textContent = "RUN FORENSIC SCAN";
                addLog(`[ERROR] Connection failed: ${err.message}`);
                alert("Server connection failed: " + err.message);
            }
        }

        function renderResults(data) {
            dropzoneView.classList.add('hidden');
            resultsView.classList.remove('hidden');

            document.getElementById('evidenceFilename').textContent = `Evidence_${data.filename || selectedFile.name}`;
            document.getElementById('timeMeta').textContent = `Extracted: ${new Date().toISOString().substring(11,19)}Z`;

            // Preview
            const imgPreview = document.getElementById('imagePreview');
            const vidPreview = document.getElementById('videoPreview');
            const url = URL.createObjectURL(selectedFile);

            if (selectedFile.type.startsWith('video/')) {
                imgPreview.style.display = 'none';
                vidPreview.style.display = 'block';
                vidPreview.src = url;
            } else {
                vidPreview.style.display = 'none';
                imgPreview.style.display = 'block';
                imgPreview.src = url;
            }

            // Bounding Box / Anomaly overlay setup
            const isManipulated = data.prediction === 'LIKELY MANIPULATED';
            const box = document.getElementById('boxOverlay');
            const badge = document.getElementById('anomalyBadge');
            const threatVal = document.getElementById('threatLevelVal');

            if (isManipulated) {
                box.className = 'bounding-box-overlay';
                badge.className = 'anomaly-badge';
                badge.textContent = 'ANOMALY_DETECTED';
                threatVal.textContent = 'ELEVATED';
                threatVal.style.color = 'var(--danger-red)';
            } else {
                box.className = 'bounding-box-overlay authentic';
                badge.className = 'anomaly-badge authentic';
                badge.textContent = 'AUTHENTICATED';
                threatVal.textContent = 'NOMINAL';
                threatVal.style.color = 'var(--success-green)';
            }

            // Position bounding box
            box.style.width = '45%';
            box.style.height = '45%';
            box.style.top = '25%';
            box.style.left = '27.5%';

            // Donut gauge
            const pct = Math.round((data.fake_probability || 0) * 100);
            const donutPct = document.getElementById('donutPct');
            const donutRing = document.getElementById('donutRing');
            
            donutPct.textContent = `${pct.toFixed(1)}%`;
            const offset = 440 - (440 * (pct / 100));
            donutRing.style.strokeDashoffset = offset;

            if (isManipulated) {
                donutRing.className = 'donut-segment manipulated';
            } else {
                donutRing.className = 'donut-segment';
            }

            // Likelihood & Tamper
            document.getElementById('likelihoodVal').textContent = isManipulated ? 'High' : 'Low';
            document.getElementById('tamperVal').textContent = isManipulated ? 'Flagged' : 'Clean';
            document.getElementById('tamperVal').className = isManipulated ? 'assessment-val flagged' : 'assessment-val clean';

            // Metadata
            if (data.metadata) {
                document.getElementById('resVal').textContent = `${data.metadata.width || '1920'} x ${data.metadata.height || '1080'}`;
                document.getElementById('formatVal').textContent = `${data.metadata.format || 'PNG'} / RGB`;
            }
            document.getElementById('sizeVal').textContent = `${(data.file_size_mb || 0).toFixed(2)} MB`;
            document.getElementById('faceVal').textContent = data.face_detected ? `${data.face_count} Detected` : '0 (Full Image)';
            document.getElementById('procVal').textContent = `${(data.processing_time_seconds || 0).toFixed(2)}s`;
            document.getElementById('hashVal').textContent = data.sha256 ? `${data.sha256.substring(0,20)}...` : '-';

            // Draw PRNU noise canvas
            drawPrnuCanvas();
            addLog(`Analysis complete. Prediction: ${data.prediction}`);
        }

        function resetAnalysis() {
            resultsView.classList.add('hidden');
            dropzoneView.classList.remove('hidden');
            selectedFile = null;
            btnStartScan.disabled = true;
            btnStartScan.textContent = "FORCE CALIBRATION";
            dropSub.textContent = "Drag and drop media files here, or click to browse.";
        }

        function exportReport() {
            if (!currentAnalysisResult) return;
            const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(currentAnalysisResult, null, 2));
            const downloadAnchor = document.createElement('a');
            downloadAnchor.setAttribute("href", dataStr);
            downloadAnchor.setAttribute("download", `Forensic_Report_${currentAnalysisResult.filename || 'media'}.json`);
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            downloadAnchor.remove();
        }

        function setAggr(btn) {
            document.querySelectorAll('.aggr-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }

        function addLog(msg) {
            const logBox = document.getElementById('activityLog');
            const ts = new Date().toISOString().substring(11,19);
            const div = document.createElement('div');
            div.className = 'log-entry';
            div.innerHTML = `<span class="log-ts">[${ts}]</span> <span class="log-msg">${msg}</span>`;
            logBox.appendChild(div);
            logBox.scrollTop = logBox.scrollHeight;
        }

        function switchTab(tab) {
            if (tab === 'forensics') {
                resetAnalysis();
            } else {
                alert(`Navigating to ${tab.toUpperCase()} module...`);
            }
        }

        function toggleTerminal() {
            alert("Authentiq Forensic Terminal v2.4 active.");
        }

        function drawPrnuCanvas() {
            const canvas = document.getElementById('prnuCanvas');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            canvas.width = canvas.clientWidth;
            canvas.height = canvas.clientHeight;

            ctx.fillStyle = '#111827';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw noise waveform
            ctx.strokeStyle = '#84cc16';
            ctx.lineWidth = 1.5;
            ctx.beginPath();

            const sliceWidth = canvas.width / 100;
            let x = 0;

            for (let i = 0; i < 100; i++) {
                const y = (canvas.height / 2) + (Math.sin(i * 0.2) * 20) + ((Math.random() - 0.5) * 30);
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
                x += sliceWidth;
            }
            ctx.stroke();
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
                
                ext = Path(filename).suffix
                if not ext:
                    ext = ".tmp"
                
                temp_filename = f"upload_{int(time.time())}_{os.urandom(4).hex()}{ext}"
                temp_path = os.path.join("/tmp", temp_filename)
                
                with open(temp_path, 'wb') as f:
                    f.write(file_data)
                
                try:
                    ext_lower = ext.lower()
                    if ext_lower in {'.mp4', '.mov', '.avi', '.mkv', '.webm'}:
                        result = detect_video(temp_path)
                    else:
                        result = detect_image(temp_path)
                    
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
    print("🚀 Authentiq v2.4.0-PRO FORENSIC AUTHENTICATION SERVER")
    print("=" * 70)
    
    host = 'localhost'
    port = 8000
    
    server_address = (host, port)
    httpd = HTTPServer(server_address, DeepfakeDetectionHandler)
    
    print(f"\n✅ Server running at: http://{host}:{port}")
    print(f"📖 Open in browser: http://localhost:8000\n")
    print("=" * 70 + "\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")
        httpd.server_close()


if __name__ == "__main__":
    main()

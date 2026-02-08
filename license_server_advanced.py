"""
Advanced License Server - With rate limiting, logging, and admin features
Recommended for production use
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import secrets
import hashlib
from datetime import datetime, timedelta
import base64
import logging
from collections import defaultdict
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('license_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
LICENSES_FILE = "licenses.json"
OBFUSCATED_MOD_FILE = "obfuscated_mod.jar"
SERVER_SECRET = "your-secret-key-change-this"

# Rate limiting
RATE_LIMIT_REQUESTS = 10  # requests
RATE_LIMIT_WINDOW = 60    # seconds
rate_limit_storage = defaultdict(list)
rate_limit_lock = threading.Lock()

def is_rate_limited(ip: str) -> bool:
    """Check if IP has exceeded rate limit"""
    with rate_limit_lock:
        now = datetime.now()
        window_start = now - timedelta(seconds=RATE_LIMIT_WINDOW)
        
        # Clean old requests
        rate_limit_storage[ip] = [
            req_time for req_time in rate_limit_storage[ip]
            if req_time > window_start
        ]
        
        # Check limit
        if len(rate_limit_storage[ip]) >= RATE_LIMIT_REQUESTS:
            return True
        
        # Record this request
        rate_limit_storage[ip].append(now)
        return False

def load_licenses():
    """Load or create licenses database"""
    if os.path.exists(LICENSES_FILE):
        try:
            with open(LICENSES_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load licenses: {e}")
            return {}
    return {}

def save_licenses(licenses):
    """Save licenses to file with backup"""
    try:
        # Create backup
        if os.path.exists(LICENSES_FILE):
            backup_file = f"{LICENSES_FILE}.backup"
            with open(LICENSES_FILE, 'r') as f:
                backup_data = f.read()
            with open(backup_file, 'w') as f:
                f.write(backup_data)
        
        # Save new data
        with open(LICENSES_FILE, 'w') as f:
            json.dump(licenses, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save licenses: {e}")

def generate_license_key():
    """Generate cryptographically secure license key"""
    return secrets.token_hex(16).upper()

def get_client_ip() -> str:
    """Get real client IP (handles proxies)"""
    if request.environ.get('HTTP_CF_CONNECTING_IP'):
        return request.environ.get('HTTP_CF_CONNECTING_IP')
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ.get('HTTP_X_FORWARDED_FOR').split(',')[0]
    return request.remote_addr

@app.before_request
def check_rate_limit():
    """Check rate limiting before each request"""
    if request.path.startswith('/admin'):
        return  # Don't rate limit admin endpoints
    
    ip = get_client_ip()
    if is_rate_limited(ip):
        logger.warning(f"Rate limit exceeded for IP: {ip}")
        return jsonify({"error": "Rate limited"}), 429

@app.route('/auth/register', methods=['POST'])
def register_license():
    """Register new HWID and issue license"""
    try:
        data = request.json or {}
        hwid = data.get('hwid', '').strip()
        
        if not hwid or len(hwid) < 16:
            return jsonify({"success": False, "error": "Invalid HWID"}), 400
        
        licenses = load_licenses()
        ip = get_client_ip()
        
        # Check if already registered
        if hwid in licenses:
            license_info = licenses[hwid]
            if license_info.get('active'):
                logger.info(f"License re-issued to HWID: {hwid[:16]}... (IP: {ip})")
                return jsonify({
                    "success": True,
                    "license": license_info['license'],
                    "registered": True
                }), 200
        
        # Generate new license
        license_key = generate_license_key()
        
        licenses[hwid] = {
            "license": license_key,
            "active": True,
            "registered_at": datetime.now().isoformat(),
            "last_checked": datetime.now().isoformat(),
            "status": "active",
            "registrations": 1 if hwid not in licenses else licenses[hwid].get('registrations', 1) + 1
        }
        
        save_licenses(licenses)
        
        logger.info(f"New license registered - HWID: {hwid[:16]}... (IP: {ip})")
        
        return jsonify({
            "success": True,
            "license": license_key,
            "registered": False
        }), 200
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({"success": False, "error": "Internal error"}), 500

@app.route('/auth/verify', methods=['POST'])
def verify_license():
    """Verify license validity"""
    try:
        data = request.json or {}
        hwid = data.get('hwid', '').strip()
        license_key = data.get('license', '').strip()
        ip = get_client_ip()
        
        if not hwid or not license_key:
            return jsonify({"success": False, "authorized": False}), 400
        
        licenses = load_licenses()
        
        if hwid not in licenses:
            logger.warning(f"Unknown HWID verification attempt: {hwid[:16]}... (IP: {ip})")
            return jsonify({"success": True, "authorized": False, "reason": "not_registered"}), 200
        
        license_info = licenses[hwid]
        
        if license_info['license'] != license_key:
            logger.warning(f"Invalid license for HWID: {hwid[:16]}... (IP: {ip})")
            return jsonify({"success": True, "authorized": False, "reason": "invalid_license"}), 200
        
        if not license_info.get('active'):
            logger.warning(f"Inactive license for HWID: {hwid[:16]}... (IP: {ip})")
            return jsonify({"success": True, "authorized": False, "reason": "inactive"}), 200
        
        # Update last check
        license_info['last_checked'] = datetime.now().isoformat()
        save_licenses(licenses)
        
        logger.info(f"License verified - HWID: {hwid[:16]}... (IP: {ip})")
        
        return jsonify({
            "success": True,
            "authorized": True,
            "status": "active"
        }), 200
    
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        return jsonify({"success": False, "error": "Internal error"}), 500

@app.route('/auth/validate', methods=['POST'])
def validate_license():
    """Validate license - compatible with 4E vxenless pattern"""
    try:
        data = request.json or {}
        hwid = data.get('hwid', '').strip()
        license_key = data.get('license_key', '').strip()
        username = data.get('username', 'Player').strip()
        mode = data.get('mode', 'login')
        ip = get_client_ip()
        
        if not hwid or not license_key:
            logger.warning(f"Missing credentials from {ip}")
            return jsonify({"valid": False, "error": "Missing hwid or license_key"}), 400
        
        licenses = load_licenses()
        
        # Check if HWID exists
        if hwid not in licenses:
            logger.warning(f"Unknown HWID: {hwid[:16]}... from {username} ({ip})")
            return jsonify({"valid": False, "error": "Not registered"}), 200
        
        license_info = licenses[hwid]
        
        # Check license key matches
        if license_info.get('license') != license_key:
            logger.warning(f"Invalid license key for HWID {hwid[:16]}... from {username} ({ip})")
            return jsonify({"valid": False, "error": "Invalid license key"}), 200
        
        # Check if active
        if not license_info.get('active'):
            logger.warning(f"Inactive license for HWID {hwid[:16]}... from {username} ({ip})")
            return jsonify({"valid": False, "error": "License inactive"}), 200
        
        # Update activity
        license_info['last_checked'] = datetime.now().isoformat()
        license_info['last_user'] = username
        license_info['last_ip'] = ip
        save_licenses(licenses)
        
        logger.info(f"[{mode.upper()}] {username} authenticated from {ip}")
        
        return jsonify({
            "valid": True,
            "authenticated": True,
            "username": username,
            "hwid": hwid[:16] + "...",
            "timestamp": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"valid": False, "error": "Server error"}), 500

@app.route('/mod/download', methods=['POST'])
def download_mod():
    """Download obfuscated mod code"""
    try:
        data = request.json or {}
        hwid = data.get('hwid', '').strip()
        license_key = data.get('license', '').strip()
        ip = get_client_ip()
        
        if not hwid or not license_key:
            logger.warning(f"Missing credentials for mod download (IP: {ip})")
            return jsonify({"success": False, "error": "Missing credentials"}), 400
        
        licenses = load_licenses()
        
        # Verify authorization
        if (hwid not in licenses or 
            licenses[hwid]['license'] != license_key or 
            not licenses[hwid].get('active')):
            logger.warning(f"Unauthorized mod download attempt - HWID: {hwid[:16]}... (IP: {ip})")
            return jsonify({"success": False, "authorized": False}), 403
        
        if not os.path.exists(OBFUSCATED_MOD_FILE):
            logger.error(f"Mod file not found: {OBFUSCATED_MOD_FILE}")
            return jsonify({"success": False, "error": "Mod unavailable"}), 500
        
        # Read mod file
        with open(OBFUSCATED_MOD_FILE, 'rb') as f:
            mod_data = f.read()
        
        mod_base64 = base64.b64encode(mod_data).decode('utf-8')
        
        # Log download
        licenses[hwid]['last_download'] = datetime.now().isoformat()
        licenses[hwid]['downloads'] = licenses[hwid].get('downloads', 0) + 1
        save_licenses(licenses)
        
        logger.info(f"Mod downloaded - HWID: {hwid[:16]}... Size: {len(mod_data)} bytes (IP: {ip})")
        
        return jsonify({
            "success": True,
            "mod": mod_base64,
            "size": len(mod_data),
            "version": "1.0"
        }), 200
    
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({"success": False, "error": "Internal error"}), 500

@app.route('/admin/licenses', methods=['GET'])
def list_licenses():
    """List all registered licenses"""
    password = request.args.get('password', '')
    
    if password != SERVER_SECRET:
        logger.warning(f"Unauthorized admin access attempt from IP: {get_client_ip()}")
        return jsonify({"error": "Unauthorized"}), 403
    
    licenses = load_licenses()
    summary = {
        "total_licenses": len(licenses),
        "active": sum(1 for l in licenses.values() if l.get('active')),
        "inactive": sum(1 for l in licenses.values() if not l.get('active')),
        "licenses": {}
    }
    
    for hwid, info in licenses.items():
        summary["licenses"][hwid[:16] + "..."] = {
            "status": info.get('status'),
            "active": info.get('active'),
            "registered_at": info.get('registered_at'),
            "last_checked": info.get('last_checked'),
            "last_download": info.get('last_download'),
            "downloads": info.get('downloads', 0),
            "registrations": info.get('registrations', 1)
        }
    
    return jsonify(summary), 200

@app.route('/admin/stats', methods=['GET'])
def get_stats():
    """Get server statistics"""
    password = request.args.get('password', '')
    
    if password != SERVER_SECRET:
        return jsonify({"error": "Unauthorized"}), 403
    
    licenses = load_licenses()
    
    stats = {
        "timestamp": datetime.now().isoformat(),
        "total_licenses": len(licenses),
        "active_licenses": sum(1 for l in licenses.values() if l.get('active')),
        "total_downloads": sum(l.get('downloads', 0) for l in licenses.values()),
        "recent_activity": []
    }
    
    # Get 10 most recently checked licenses
    recent = sorted(
        [(hwid, info) for hwid, info in licenses.items()],
        key=lambda x: x[1].get('last_checked', ''),
        reverse=True
    )[:10]
    
    for hwid, info in recent:
        stats["recent_activity"].append({
            "hwid": hwid[:16] + "...",
            "last_checked": info.get('last_checked'),
            "status": info.get('status')
        })
    
    return jsonify(stats), 200

@app.route('/admin/revoke', methods=['POST'])
def revoke_license():
    """Revoke a license"""
    password = request.args.get('password', '')
    
    if password != SERVER_SECRET:
        logger.warning(f"Unauthorized revoke attempt from IP: {get_client_ip()}")
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json or {}
    hwid = data.get('hwid', '').strip()
    reason = data.get('reason', 'admin_revoke')
    
    licenses = load_licenses()
    
    if hwid not in licenses:
        return jsonify({"success": False, "error": "HWID not found"}), 404
    
    licenses[hwid]['active'] = False
    licenses[hwid]['status'] = 'revoked'
    licenses[hwid]['revoked_at'] = datetime.now().isoformat()
    licenses[hwid]['revoke_reason'] = reason
    
    save_licenses(licenses)
    
    logger.warning(f"License revoked - HWID: {hwid[:16]}... Reason: {reason}")
    
    return jsonify({"success": True, "message": "License revoked"}), 200

@app.route('/admin/reactivate', methods=['POST'])
def reactivate_license():
    """Reactivate a revoked license"""
    password = request.args.get('password', '')
    
    if password != SERVER_SECRET:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json or {}
    hwid = data.get('hwid', '').strip()
    
    licenses = load_licenses()
    
    if hwid not in licenses:
        return jsonify({"success": False, "error": "HWID not found"}), 404
    
    licenses[hwid]['active'] = True
    licenses[hwid]['status'] = 'active'
    del licenses[hwid]['revoked_at']
    del licenses[hwid]['revoke_reason']
    
    save_licenses(licenses)
    
    logger.info(f"License reactivated - HWID: {hwid[:16]}...")
    
    return jsonify({"success": True, "message": "License reactivated"}), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "server": "Advanced License Server v1.1",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("Advanced License Server Starting")
    logger.info("="*60)
    logger.info(f"Licenses database: {LICENSES_FILE}")
    logger.info(f"Mod file: {OBFUSCATED_MOD_FILE}")
    logger.info("IMPORTANT: Change SERVER_SECRET in production!")
    logger.info("="*60)
    
    # For production, use gunicorn instead:
    # gunicorn -w 4 -b 0.0.0.0:5000 license_server_advanced:app
    app.run(host='0.0.0.0', port=5000, debug=False)

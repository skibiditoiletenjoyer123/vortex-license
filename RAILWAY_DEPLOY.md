# Railway Deployment Guide

## Quick Deploy (5 minutes)

### 1. Create GitHub Account
- Go to https://github.com/signup
- Sign up with email

### 2. Initialize Git & Push to GitHub

```powershell
cd C:\Users\ten8\Desktop\vortex-license

# Initialize git
git init
git add .
git commit -m "Initial: Vortex License Server"

# Create new repo on GitHub
# Go to https://github.com/new
# Name it: vortex-license
# Make it PUBLIC

# Then run:
git remote add origin https://github.com/YOUR_USERNAME/vortex-license.git
git branch -M main
git push -u origin main
```

### 3. Deploy to Railway

1. Go to https://railway.app
2. Click "Start New Project"
3. Select "Deploy from GitHub"
4. Authorize GitHub
5. Select your `vortex-license` repository
6. Railway auto-detects Python + Procfile
7. It deploys automatically
8. Get your public URL from Railway dashboard

### 4. Get Your Server URL

After deploy, Railway gives you a URL like: `https://vortex-license-production.up.railway.app`

### 5. Update Java Client

In `VortexAuthClient.java`, change:
```java
private static final String AUTH_SERVER_URL = "https://your-railway-url.railway.app";
```

### 6. Test It

```bash
# Create a license
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"hwid":"abc123def456"}'

# Validate license
curl -X POST http://localhost:5000/auth/validate \
  -H "Content-Type: application/json" \
  -d '{"hwid":"abc123def456","license_key":"...","username":"Player","mode":"login"}'
```

## Features

- ✅ License registration
- ✅ HWID-based authentication  
- ✅ License validation with `/validate` endpoint
- ✅ Rate limiting (10 req/60s per IP)
- ✅ Logging to file & console
- ✅ Admin endpoints for license management
- ✅ Production-ready with Gunicorn

## Environment Variables (Optional - Railway sets these)

```
FLASK_ENV=production
PORT=5000
```

## Server Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/auth/register` | POST | Register new HWID |
| `/auth/verify` | POST | Verify license |
| `/auth/validate` | POST | Login/validate (4E compatible) |
| `/mod/download` | POST | Download obfuscated mod |
| `/admin/revoke` | POST | Revoke license |
| `/admin/reactivate` | POST | Reactivate license |
| `/admin/list` | GET | List all licenses |

## Database

Licenses stored in `licenses.json`:
```json
{
  "hwid_sha256": {
    "license": "ABC123...",
    "active": true,
    "registered_at": "2026-02-08T...",
    "last_checked": "2026-02-08T...",
    "last_user": "Player",
    "last_ip": "1.2.3.4"
  }
}
```

That's it! Your auth server is live on Railway.

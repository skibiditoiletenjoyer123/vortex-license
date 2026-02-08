# Vortex License Server

Production-ready, HWID-based authentication for Minecraft Fabric mods. Deploy to Railway in minutes. 4E vxenless pattern compatible.

## Features

- ✅ **HWID-based authentication** (SHA256 system hash)
- ✅ **License key validation** 
- ✅ **4E-compatible `/validate` endpoint**
- ✅ **Rate limiting** (10 req/60s per IP)
- ✅ **One-click Railway deploy**
- ✅ **Admin management** (revoke/reactivate)
- ✅ **File logging** (audit trail)

## Quick Start

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python license_server_advanced.py

# Test  (in another terminal)
python test_auth.py
```

### Deploy to Railway
See [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) (5-minute guide)

## Java Client

Use `VortexAuthClient.java` in your Minecraft mod:

```java
// Authenticate
VortexAuthClient.registerLicense("LICENSE_KEY", "PlayerName")
    .thenAccept(success -> {
        if (success) loadMod();
    });

// Update server URL after Railway deploy:
private static final String AUTH_SERVER_URL = "https://your-railway-url.railway.app";
```

## API Reference

### POST `/auth/register`
Register new HWID and get license key

### POST `/auth/validate`  
Validate license (4E compatible) - Request:
```json
{"hwid": "hash", "license_key": "key", "username": "name", "mode": "login"}
```
Response: `{"valid": true, "authenticated": true}`

### POST `/auth/verify`
Verify existing license

## Files

- `license_server_advanced.py` - Production server
- `VortexAuthClient.java` - Java client for Minecraft
- `test_auth.py` - Test suite
- `config py` - Configuration
- `requirements.txt` - Python dependencies
- `Procfile` - Railway deployment
- `RAILWAY_DEPLOY.md` - Deployment guide
4. Server verifies license
5. Server sends obfuscated mod code
6. Game launches with mod injected
7. License cached locally for offline use

## Security

- Each HWID gets unique license (can't share)
- Real mod code stored on server (not in JAR)
- License revocation works instantly
- Rate limiting prevents spam
- Full logging of all auth attempts

## Documentation

See `START_HERE.md` for quick setup guide.

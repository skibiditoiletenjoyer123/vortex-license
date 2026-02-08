# 🚀 START HERE

## Files on Your Desktop

All files are in: **C:\Users\ten8\Desktop\vortex-license**

### What You Have

```
vortex-license/
├── license_server_advanced.py  ← Run this on server
├── license_client.py           ← Players run this
├── config.py                   ← Edit this with your settings
├── requirements.txt            ← Install with pip
└── .gitignore                  ← For GitHub
```

---

## 3 Steps to Get Started

### Step 1: Test Locally (5 min)

```powershell
cd C:\Users\ten8\Desktop\vortex-license

# Install dependencies
pip install -r requirements.txt

# Start server in background
python license_server_advanced.py
# Should print: Advanced License Server Starting

# In another PowerShell window, test client
python license_client.py
# Should print: License registered, verified, etc
```

### Step 2: Push to GitHub (5 min)

```powershell
cd C:\Users\ten8\Desktop\vortex-license

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial: vortex license server and client"

# Go to https://github.com/new
# Create repo: vortex-license
# Copy the commands GitHub shows
# Paste them here (replace YOUR_USERNAME)

git remote add origin https://github.com/YOUR_USERNAME/vortex-license.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Railway (5 min)

1. Go to https://railway.app
2. Sign up with **GitHub**
3. Click **+ New Project** → **Deploy from GitHub repo**
4. Select **vortex-license**
5. Railway deploys automatically and gives you a URL like:
   ```
   https://vortex-license.railway.app
   ```

---

## Configure for Your Server

Edit `config.py`:

```python
# Change this line with your Railway URL:
SERVER_URL = "https://vortex-license.railway.app"

# Change this to a random secret:
SERVER_SECRET = "abc123def456xyz789xyz123"
```

Then test:
```bash
python license_client.py
```

---

## Important File Details

### license_server_advanced.py
- **What it does**: Runs the license server
- **When to run**: On Railway as your backend
- **What it creates**: `licenses.json` (stores all license data)

### license_client.py
- **What it does**: Client launcher for players
- **When to run**: Players run this to authenticate
- **What it creates**: `.license` (stores their license locally)

### config.py
- **What to edit**: SERVER_URL, SERVER_SECRET
- **Only file you need to change!**

### requirements.txt
- **What it is**: Python dependencies
- **Install with**: `pip install -r requirements.txt`

---

## Next: Create Obfuscated Mod JAR

Your mod JAR needs to be obfuscated (hidden code).

1. Obfuscate your mod JAR using ProGuard or YGuard
2. Name it: **obfuscated_mod.jar**
3. Place in: **C:\Users\ten8\Desktop\vortex-license\**
4. Push to GitHub

---

## Testing Checklist

- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Local server works: `python license_server_advanced.py`
- [ ] Client works: `python license_client.py`
- [ ] Git initialized: `git init`
- [ ] GitHub repo created and pushed
- [ ] Railway deployed successfully
- [ ] obfuscated_mod.jar placed in folder
- [ ] config.py updated with your Rails URL

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'flask'"**
→ Run: `pip install -r requirements.txt`

**"Cannot connect to license server"**
→ Make sure server is running first

**"License registration failed"**
→ Check SERVER_URL in config.py is correct

**"Git not found"**
→ Install Git from https://git-scm.com

---

**You're all set! Next: Push to GitHub → Deploy to Railway**

Questions? Check [FILE_SUMMARY.md](../shiii/FILE_SUMMARY.md) in the original folder.

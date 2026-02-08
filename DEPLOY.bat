@echo off
REM Quick deployment script for Vortex License Server
REM Prerequisites: git, github account, railway cli

setlocal enabledelayedexpansion

echo.
echo ============================================
echo Vortex License Server - Quick Deploy
echo ============================================
echo.

cd /d C:\Users\ten8\Desktop\vortex-license

echo [1/5] Checking git installation...
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git not installed. Download from https://git-scm.com/download/win
    exit /b 1
)
echo OK - Git found

echo.
echo [2/5] Initializing local repository...
if not exist ".git" (
    git init
    echo OK - Repository initialized
) else (
    echo OK - Repository exists
)

echo.
echo [3/5] Staging files for commit...
git add .
git commit -m "Vortex License Server - Railway deployment" --allow-empty
echo OK - Files staged

echo.
echo [4/5] GitHub Configuration
echo.
echo To push to GitHub:
echo 1. Create repo at https://github.com/new
echo 2. Name it: vortex-license
echo 3. Make it PUBLIC
echo.
echo Then run:
echo   git remote add origin https://github.com/YOUR_USERNAME/vortex-license.git
echo   git branch -M main
echo   git push -u origin main
echo.

echo.
echo [5/5] Railway Deployment
echo.
echo Once pushed to GitHub:
echo 1. Go to https://railway.app
echo 2. Click "Start New Project"
echo 3. Select "Deploy from GitHub"
echo 4. Connect vortex-license repository
echo 5. Railway auto-deploys with Procfile
echo.
echo Your server URL will be shown in Railway dashboard
echo.

echo.
echo ============================================
echo Next Steps:
echo ============================================
echo 1. Read RAILWAY_DEPLOY.md for full instructions
echo 2. Create GitHub account
echo 3. Create Railway account  
echo 4. Update VortexAuthClient.java AUTH_SERVER_URL
echo 5. Test endpoints with curl
echo.

pause

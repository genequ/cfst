@echo off
REM Specific Git Setup for genequ/Proxy.git repository
REM Run this AFTER installing Git from https://git-scm.com/downloads

echo ============================================
echo  GitHub Setup for genequ/Proxy.git
echo ============================================

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed or not in PATH
    echo.
    echo Please install Git first:
    echo 1. Go to https://git-scm.com/downloads
    echo 2. Download and install Git for Windows
    echo 3. Restart your command prompt
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

echo Git is installed: 
git --version

echo.
echo ============================================
echo  Step 1: Initialize Git Repository
echo ============================================

REM Change to script directory
cd /d "%~dp0"

REM Check if already a git repository
if exist ".git" (
    echo Git repository already initialized
    goto :config
)

git init
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize git repository
    pause
    exit /b 1
)
echo Git repository initialized successfully

:config
echo.
echo ============================================
echo  Step 2: Configure Git User
echo ============================================

echo Configuring Git user for genequ...
git config --global user.email "genequ@users.noreply.github.com"
git config --global user.name "genequ"

echo Git user configured: genequ <genequ@users.noreply.github.com>

echo.
echo ============================================
echo  Step 3: Add Your GitHub Repository
echo ============================================

echo Adding remote repository: https://github.com/genequ/Proxy.git
git remote add origin https://github.com/genequ/Proxy.git
if %errorlevel% neq 0 (
    echo WARNING: Failed to add remote repository (may already exist)
    echo You can check with: git remote -v
)

echo.
echo ============================================
echo  Step 4: First Commit
echo ============================================

echo Adding files to Git...
git add .

echo Creating initial commit...
git commit -m "Initial commit: Cloudflare Speed Test Automation"

echo.
echo ============================================
echo  Step 5: Push to Your Repository
echo ============================================

echo Attempting to push to https://github.com/genequ/Proxy.git
echo You will be prompted for your GitHub credentials

echo Trying 'main' branch...
git push -u origin main
if %errorlevel% neq 0 (
    echo Trying 'master' branch instead...
    git push -u origin master
)

echo.
echo ============================================
echo  Setup Complete!
echo ============================================

echo GitHub integration configured for genequ/Proxy.git!
echo.
echo Next steps:
echo 1. Test the automation: python cfst_scheduler.py --run-once
echo 2. Check https://github.com/genequ/Proxy.git for results
echo 3. The script will now automatically push results every 12 hours
echo.
echo For authentication issues:
echo - Use your GitHub username and Personal Access Token as password
echo - Or set up SSH keys for passwordless authentication
echo.
pause

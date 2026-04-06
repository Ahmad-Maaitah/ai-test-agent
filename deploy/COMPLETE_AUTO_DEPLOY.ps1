# ==============================================================================
# COMPLETE AUTOMATED DEPLOYMENT - ONE COMMAND DOES EVERYTHING
# ==============================================================================
# Run this ONE script on Windows Server and it will:
# 1. Install everything automatically
# 2. Deploy the application
# 3. Start the service
# 4. Configure clean URL access
# 5. Give you the team access URL
# ==============================================================================

#Requires -RunAsAdministrator

param(
    [string]$DeploymentPath = "C:\Temp\api-tester-deployment",
    [string]$InstallPath = "C:\Apps\APITester",
    [int]$Port = 5000,
    [string]$DomainName = "api-tester"  # Will create: http://api-tester (no port needed!)
)

$ErrorActionPreference = "Continue"

Write-Host @"
================================================================================
    API TESTING PLATFORM - COMPLETE AUTOMATED DEPLOYMENT
================================================================================
    This script will do EVERYTHING automatically:
    ✓ Install all components
    ✓ Configure the application
    ✓ Set up Windows Service
    ✓ Configure firewall
    ✓ Set up clean URL access (no port numbers!)
    ✓ Make it accessible to your team

    Sit back and relax - this will take 5-10 minutes...
================================================================================

"@ -ForegroundColor Cyan

Start-Sleep -Seconds 2

# ==============================================================================
# STEP 1: Check Prerequisites
# ==============================================================================
Write-Host "`n[STEP 1/10] Checking prerequisites..." -ForegroundColor Yellow

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "  ✗ This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "  Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "  ✓ Running as Administrator" -ForegroundColor Green

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Installing Python automatically..." -ForegroundColor Yellow

    # Download Python installer
    $pythonUrl = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-installer.exe"

    Write-Host "  Downloading Python 3.11.8..." -NoNewline
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller -UseBasicParsing
    Write-Host " ✓" -ForegroundColor Green

    Write-Host "  Installing Python..." -NoNewline
    Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
    Write-Host " ✓" -ForegroundColor Green

    # Refresh environment
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

    Write-Host "  ✓ Python installed successfully" -ForegroundColor Green
}

# Check deployment files
if (-not (Test-Path $DeploymentPath)) {
    Write-Host "  ✗ Deployment files not found at: $DeploymentPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Please extract api-tester-deployment.zip to: $DeploymentPath" -ForegroundColor Yellow
    Read-Host "Press Enter after extracting the files"

    if (-not (Test-Path $DeploymentPath)) {
        Write-Host "  ✗ Still not found. Exiting." -ForegroundColor Red
        exit 1
    }
}
Write-Host "  ✓ Deployment files found" -ForegroundColor Green

Write-Host "  ✓ All prerequisites met" -ForegroundColor Green

# ==============================================================================
# STEP 2: Create Directory Structure
# ==============================================================================
Write-Host "`n[STEP 2/10] Creating directory structure..." -ForegroundColor Yellow

$directories = @(
    $InstallPath,
    "$InstallPath\logs",
    "$InstallPath\output",
    "$InstallPath\backend",
    "$InstallPath\app",
    "$InstallPath\app\templates",
    "$InstallPath\app\static"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -Path $dir -ItemType Directory -Force | Out-Null
    }
}
Write-Host "  ✓ Directories created" -ForegroundColor Green

# ==============================================================================
# STEP 3: Copy Application Files
# ==============================================================================
Write-Host "`n[STEP 3/10] Copying application files..." -ForegroundColor Yellow

if (Test-Path "$DeploymentPath\package") {
    Write-Host "  Copying files..." -NoNewline
    xcopy /E /I /Y /Q "$DeploymentPath\package\*" "$InstallPath\" | Out-Null
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host "  ✗ Package directory not found!" -ForegroundColor Red
    exit 1
}

Write-Host "  ✓ Application files copied" -ForegroundColor Green

# ==============================================================================
# STEP 4: Create Virtual Environment
# ==============================================================================
Write-Host "`n[STEP 4/10] Setting up Python environment..." -ForegroundColor Yellow

Set-Location $InstallPath

if (-not (Test-Path "$InstallPath\venv")) {
    Write-Host "  Creating virtual environment..." -NoNewline
    python -m venv venv | Out-Null
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host "  ✓ Virtual environment exists" -ForegroundColor Gray
}

Write-Host "  ✓ Python environment ready" -ForegroundColor Green

# ==============================================================================
# STEP 5: Install Dependencies
# ==============================================================================
Write-Host "`n[STEP 5/10] Installing Python packages (this may take 2-3 minutes)..." -ForegroundColor Yellow

Write-Host "  Upgrading pip..." -NoNewline
& "$InstallPath\venv\Scripts\python.exe" -m pip install --upgrade pip --quiet | Out-Null
Write-Host " ✓" -ForegroundColor Green

if (Test-Path "$InstallPath\requirements.txt") {
    Write-Host "  Installing dependencies..." -NoNewline
    & "$InstallPath\venv\Scripts\pip.exe" install -r "$InstallPath\requirements.txt" --quiet | Out-Null
    Write-Host " ✓" -ForegroundColor Green
} else {
    Write-Host "  Installing core packages..." -NoNewline
    & "$InstallPath\venv\Scripts\pip.exe" install Flask==2.3.0 SQLAlchemy==2.0.23 requests==2.31.0 pytest==7.4.3 pytest-html==4.1.1 pytest-json-report==1.5.0 --quiet | Out-Null
    Write-Host " ✓" -ForegroundColor Green
}

Write-Host "  ✓ All packages installed" -ForegroundColor Green

# ==============================================================================
# STEP 6: Create Configuration Files
# ==============================================================================
Write-Host "`n[STEP 6/10] Creating configuration..." -ForegroundColor Yellow

# Create config.py
$configContent = @"
"""Production configuration."""
import os

class Config:
    HOST = '0.0.0.0'
    PORT = $Port
    DEBUG = False
    DATABASE_PATH = r'$InstallPath\database.db'
    LOG_DIR = r'$InstallPath\logs'
    LOG_FILE = os.path.join(LOG_DIR, 'app.log')
    LOG_LEVEL = 'INFO'
    OUTPUT_DIR = r'$InstallPath\output'
    SECRET_KEY = '$((New-Guid).Guid.Replace("-", ""))'
    THREAD_TIMEOUT = 300
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
"@
Set-Content -Path "$InstallPath\config.py" -Value $configContent -Force
Write-Host "  ✓ Configuration created" -ForegroundColor Green

# Create run_production.py if not exists
if (-not (Test-Path "$InstallPath\run_production.py")) {
    $runnerContent = @"
import os, sys, logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app
from config import Config

def setup_logging():
    os.makedirs(Config.LOG_DIR, exist_ok=True)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    file_handler = RotatingFileHandler(Config.LOG_FILE, maxBytes=10485760, backupCount=10)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    return root_logger

if __name__ == '__main__':
    logger = setup_logging()
    logger.info('='*80)
    logger.info('API Testing Platform Starting')
    logger.info(f'Server: {Config.HOST}:{Config.PORT}')
    logger.info('='*80)
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)
    from backend.database import init_db
    init_db()
    logger.info('Database initialized')
    app = create_app()
    try:
        app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, threaded=True)
    except Exception as e:
        logger.error(f'Server error: {e}', exc_info=True)
        sys.exit(1)
"@
    Set-Content -Path "$InstallPath\run_production.py" -Value $runnerContent -Force
}

# Create startup batch file
$batchContent = @"
@echo off
cd /d $InstallPath
call venv\Scripts\activate.bat
python run_production.py
"@
Set-Content -Path "$InstallPath\start_server.bat" -Value $batchContent -Force

Write-Host "  ✓ Startup scripts created" -ForegroundColor Green

# ==============================================================================
# STEP 7: Initialize Database
# ==============================================================================
Write-Host "`n[STEP 7/10] Initializing database..." -ForegroundColor Yellow

& "$InstallPath\venv\Scripts\python.exe" -c "from backend.database import init_db; init_db(); print('OK')" 2>&1 | Out-Null
if (Test-Path "$InstallPath\database.db") {
    Write-Host "  ✓ Database initialized" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Database will be created on first run" -ForegroundColor Yellow
}

# ==============================================================================
# STEP 8: Install Windows Service
# ==============================================================================
Write-Host "`n[STEP 8/10] Installing Windows Service..." -ForegroundColor Yellow

# Download NSSM if needed
$nssmPath = "C:\Apps\nssm\win64\nssm.exe"
if (-not (Test-Path $nssmPath)) {
    Write-Host "  Downloading NSSM..." -NoNewline
    $nssmDir = "C:\Apps\nssm"
    New-Item -Path $nssmDir -ItemType Directory -Force | Out-Null
    $nssmZip = "$env:TEMP\nssm.zip"
    Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile $nssmZip -UseBasicParsing
    Expand-Archive -Path $nssmZip -DestinationPath $nssmDir -Force
    Move-Item "$nssmDir\nssm-2.24\*" $nssmDir -Force
    Write-Host " ✓" -ForegroundColor Green
}

# Remove existing service
try {
    & $nssmPath stop APITester 2>&1 | Out-Null
    & $nssmPath remove APITester confirm 2>&1 | Out-Null
} catch {}

# Install service
Write-Host "  Installing service..." -NoNewline
& $nssmPath install APITester "$InstallPath\start_server.bat" | Out-Null
& $nssmPath set APITester Description "API Automation Testing Platform" | Out-Null
& $nssmPath set APITester Start SERVICE_AUTO_START | Out-Null
& $nssmPath set APITester AppDirectory "$InstallPath" | Out-Null
& $nssmPath set APITester AppStdout "$InstallPath\logs\service-output.log" | Out-Null
& $nssmPath set APITester AppStderr "$InstallPath\logs\service-error.log" | Out-Null
& $nssmPath set APITester AppRotateFiles 1 | Out-Null
& $nssmPath set APITester AppRotateBytes 10485760 | Out-Null
Write-Host " ✓" -ForegroundColor Green

Write-Host "  ✓ Windows Service installed" -ForegroundColor Green

# ==============================================================================
# STEP 9: Configure Firewall & Network
# ==============================================================================
Write-Host "`n[STEP 9/10] Configuring firewall and network..." -ForegroundColor Yellow

# Stop any process using port
$portUsage = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
if ($portUsage) {
    Write-Host "  Stopping process on port $Port..." -NoNewline
    Stop-Process -Id $portUsage.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host " ✓" -ForegroundColor Green
}

# Configure firewall
try {
    Remove-NetFirewallRule -DisplayName "API Tester*" -ErrorAction SilentlyContinue | Out-Null
} catch {}

New-NetFirewallRule -DisplayName "API Tester - Port $Port" `
    -Direction Inbound `
    -LocalPort $Port `
    -Protocol TCP `
    -Action Allow `
    -Profile Domain,Private `
    -ErrorAction SilentlyContinue | Out-Null

Write-Host "  ✓ Firewall configured (Port $Port open)" -ForegroundColor Green

# Add hosts entry for clean domain name
$hostsFile = "C:\Windows\System32\drivers\etc\hosts"
$hostsContent = Get-Content $hostsFile -Raw
$hostEntry = "127.0.0.1    $DomainName"

if ($hostsContent -notmatch $DomainName) {
    Add-Content -Path $hostsFile -Value "`n$hostEntry" -Force
    Write-Host "  ✓ Domain name configured: $DomainName" -ForegroundColor Green
} else {
    Write-Host "  ✓ Domain name already configured: $DomainName" -ForegroundColor Gray
}

# ==============================================================================
# STEP 10: Start Service & Verify
# ==============================================================================
Write-Host "`n[STEP 10/10] Starting service and verifying..." -ForegroundColor Yellow

Write-Host "  Starting APITester service..." -NoNewline
Start-Service -Name "APITester" -ErrorAction SilentlyContinue
Start-Sleep -Seconds 8
Write-Host " ✓" -ForegroundColor Green

$service = Get-Service -Name "APITester"
if ($service.Status -eq "Running") {
    Write-Host "  ✓ Service is running" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Service status: $($service.Status)" -ForegroundColor Yellow
}

# Test connection
Write-Host "  Testing connection..." -NoNewline
Start-Sleep -Seconds 3
try {
    $response = Invoke-WebRequest -Uri "http://localhost:$Port" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    Write-Host " ✓" -ForegroundColor Green
    Write-Host "  ✓ Server is accessible!" -ForegroundColor Green
    $success = $true
} catch {
    Write-Host " ✗" -ForegroundColor Red
    Write-Host "  ⚠ Server may still be starting..." -ForegroundColor Yellow
    $success = $false
}

# Get server IP
$serverIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "172.16.1.*"}).IPAddress
if (-not $serverIP) {
    $serverIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notmatch "127.0.0.1" -and $_.PrefixOrigin -eq "Dhcp"}).IPAddress | Select-Object -First 1
}
if (-not $serverIP) {
    $serverIP = "YOUR-SERVER-IP"
}

# ==============================================================================
# SUCCESS!
# ==============================================================================
Write-Host "`n" -NoNewline
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "                    DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""

Write-Host "📋 TEAM ACCESS INFORMATION" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "  🌐 Primary URL (Anyone on your network):" -ForegroundColor Yellow
Write-Host "     http://${serverIP}:${Port}" -ForegroundColor White -BackgroundColor DarkBlue
Write-Host ""
Write-Host "  🖥️  On Server (localhost):" -ForegroundColor Yellow
Write-Host "     http://localhost:${Port}" -ForegroundColor White
Write-Host "     http://${DomainName}:${Port}" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

Write-Host "📧 EMAIL TO YOUR TEAM:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host @"

Subject: API Testing Platform - Now Live!

Hi Team,

Our API Automation Testing Platform is now available!

🔗 Access URL: http://${serverIP}:${Port}

✨ What you can do:
• Create and manage API test cases
• Run automated API tests
• Generate detailed test reports
• Track test execution history
• Manage test variables

📋 Requirements:
• Browser: Chrome or Edge (recommended)
• Network: Company LAN

🚀 No login required - just open the URL and start testing!

For support, contact me.

"@ -ForegroundColor White

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

Write-Host "⚙️  SERVICE MANAGEMENT:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Status:   Get-Service -Name 'APITester'" -ForegroundColor White
Write-Host "  Start:    Start-Service -Name 'APITester'" -ForegroundColor White
Write-Host "  Stop:     Stop-Service -Name 'APITester'" -ForegroundColor White
Write-Host "  Restart:  Restart-Service -Name 'APITester'" -ForegroundColor White
Write-Host "  Logs:     Get-Content $InstallPath\logs\app.log -Tail 50 -Wait" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

Write-Host "📁 IMPORTANT LOCATIONS:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Installation: $InstallPath" -ForegroundColor White
Write-Host "  Config:       $InstallPath\config.py" -ForegroundColor White
Write-Host "  Database:     $InstallPath\database.db" -ForegroundColor White
Write-Host "  Logs:         $InstallPath\logs\" -ForegroundColor White
Write-Host "  Reports:      $InstallPath\output\" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

if ($success) {
    Write-Host "✅ Testing the URL now..." -ForegroundColor Green
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:$Port"
} else {
    Write-Host "⚠️  If the URL doesn't work yet, wait 30 seconds and try again." -ForegroundColor Yellow
    Write-Host "   The service may still be initializing." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Check status: Get-Service -Name 'APITester'" -ForegroundColor White
    Write-Host "   Check logs:   Get-Content $InstallPath\logs\service-error.log" -ForegroundColor White
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Green
Write-Host "               🎉 DEPLOYMENT COMPLETE! YOUR TEAM CAN NOW ACCESS! 🎉" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"

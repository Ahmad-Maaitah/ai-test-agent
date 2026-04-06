# ==============================================================================
# API Automation Testing Platform - Automated Windows Server Setup
# ==============================================================================
# Server: 172.16.1.4
# This script automates the entire installation process
# ==============================================================================

param(
    [string]$InstallPath = "C:\Apps\APITester",
    [int]$Port = 5000,
    [string]$ServerIP = "172.16.1.4"
)

# Requires Administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "This script must be run as Administrator"
    exit 1
}

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "API Automation Testing Platform - Automated Setup" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# ==============================================================================
# Step 1: Create Directory Structure
# ==============================================================================
Write-Host "[1/12] Creating directory structure..." -ForegroundColor Yellow

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
        Write-Host "  ✓ Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  ✓ Exists: $dir" -ForegroundColor Gray
    }
}

# ==============================================================================
# Step 2: Check Python Installation
# ==============================================================================
Write-Host "`n[2/12] Checking Python installation..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.9+ from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter after installing Python"
    exit 1
}

# ==============================================================================
# Step 3: Create Virtual Environment
# ==============================================================================
Write-Host "`n[3/12] Creating virtual environment..." -ForegroundColor Yellow

Set-Location $InstallPath

if (-not (Test-Path "$InstallPath\venv")) {
    python -m venv venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "  ✓ Virtual environment exists" -ForegroundColor Gray
}

# Activate virtual environment
& "$InstallPath\venv\Scripts\Activate.ps1"
Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green

# ==============================================================================
# Step 4: Install Python Dependencies
# ==============================================================================
Write-Host "`n[4/12] Installing Python dependencies..." -ForegroundColor Yellow

# Upgrade pip
python -m pip install --upgrade pip --quiet

# Install dependencies
$packages = @(
    "Flask==2.3.0",
    "SQLAlchemy==2.0.23",
    "requests==2.31.0",
    "pytest==7.4.3",
    "pytest-html==4.1.1",
    "pytest-json-report==1.5.0",
    "allure-pytest==2.13.2"
)

foreach ($package in $packages) {
    Write-Host "  Installing $package..." -NoNewline
    pip install $package --quiet
    Write-Host " ✓" -ForegroundColor Green
}

Write-Host "  ✓ All dependencies installed" -ForegroundColor Green

# ==============================================================================
# Step 5: Create Configuration File
# ==============================================================================
Write-Host "`n[5/12] Creating configuration files..." -ForegroundColor Yellow

$configContent = @"
"""Production configuration for Windows Server."""
import os

class Config:
    # Server Configuration
    HOST = '0.0.0.0'
    PORT = $Port
    DEBUG = False

    # Database
    DATABASE_PATH = r'$InstallPath\database.db'

    # Logging
    LOG_DIR = r'$InstallPath\logs'
    LOG_FILE = os.path.join(LOG_DIR, 'app.log')
    LOG_LEVEL = 'INFO'

    # Output/Reports
    OUTPUT_DIR = r'$InstallPath\output'

    # Security
    SECRET_KEY = '$((New-Guid).Guid.Replace("-", ""))'

    # Performance
    THREAD_TIMEOUT = 300
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
"@

Set-Content -Path "$InstallPath\config.py" -Value $configContent
Write-Host "  ✓ config.py created" -ForegroundColor Green

# ==============================================================================
# Step 6: Create Production Runner
# ==============================================================================
Write-Host "`n[6/12] Creating production runner..." -ForegroundColor Yellow

$runnerContent = @"
"""Production runner for API Testing Platform."""
import os
import sys
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config import Config

def setup_logging():
    os.makedirs(Config.LOG_DIR, exist_ok=True)

    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    file_handler = RotatingFileHandler(
        Config.LOG_FILE,
        maxBytes=10485760,
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger

if __name__ == '__main__':
    logger = setup_logging()
    logger.info('='*80)
    logger.info('Starting API Testing Platform - Production Mode')
    logger.info(f'Server: {Config.HOST}:{Config.PORT}')
    logger.info(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    logger.info('='*80)

    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

    from backend.database import init_db
    init_db()
    logger.info('Database initialized')

    app = create_app()

    try:
        logger.info('Server starting...')
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info('Server stopped by user')
    except Exception as e:
        logger.error(f'Server error: {e}', exc_info=True)
        sys.exit(1)
"@

Set-Content -Path "$InstallPath\run_production.py" -Value $runnerContent
Write-Host "  ✓ run_production.py created" -ForegroundColor Green

# ==============================================================================
# Step 7: Create Startup Batch File
# ==============================================================================
Write-Host "`n[7/12] Creating startup scripts..." -ForegroundColor Yellow

$batchContent = @"
@echo off
cd /d $InstallPath
call venv\Scripts\activate.bat
python run_production.py
"@

Set-Content -Path "$InstallPath\start_server.bat" -Value $batchContent
Write-Host "  ✓ start_server.bat created" -ForegroundColor Green

# ==============================================================================
# Step 8: Initialize Database
# ==============================================================================
Write-Host "`n[8/12] Initializing database..." -ForegroundColor Yellow

# Check if project files exist
if (Test-Path "$InstallPath\backend\database.py") {
    python -c "from backend.database import init_db; init_db(); print('Database initialized')"
    Write-Host "  ✓ Database initialized" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Waiting for project files to be copied..." -ForegroundColor Yellow
    Write-Host "  ! Database will be initialized when service starts" -ForegroundColor Yellow
}

# ==============================================================================
# Step 9: Configure Windows Firewall
# ==============================================================================
Write-Host "`n[9/12] Configuring Windows Firewall..." -ForegroundColor Yellow

# Remove old rules if they exist
try {
    Remove-NetFirewallRule -DisplayName "API Tester - Port $Port" -ErrorAction SilentlyContinue | Out-Null
} catch {}

# Create new rule
New-NetFirewallRule -DisplayName "API Tester - Port $Port" `
    -Direction Inbound `
    -LocalPort $Port `
    -Protocol TCP `
    -Action Allow `
    -Profile Domain,Private `
    -ErrorAction SilentlyContinue | Out-Null

Write-Host "  ✓ Firewall rule created for port $Port" -ForegroundColor Green

# ==============================================================================
# Step 10: Install and Configure NSSM Service
# ==============================================================================
Write-Host "`n[10/12] Installing Windows Service..." -ForegroundColor Yellow

# Check if NSSM exists
$nssmPath = "C:\Apps\nssm\win64\nssm.exe"

if (-not (Test-Path $nssmPath)) {
    Write-Host "  Downloading NSSM..." -NoNewline

    $nssmDir = "C:\Apps\nssm"
    New-Item -Path $nssmDir -ItemType Directory -Force | Out-Null

    $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $nssmZip = "$env:TEMP\nssm.zip"

    try {
        Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip -UseBasicParsing
        Expand-Archive -Path $nssmZip -DestinationPath $nssmDir -Force

        # Move files from nested directory
        Get-ChildItem "$nssmDir\nssm-*" | Get-ChildItem | Move-Item -Destination $nssmDir -Force

        Write-Host " ✓" -ForegroundColor Green
    } catch {
        Write-Host " ✗" -ForegroundColor Red
        Write-Host "  Please download NSSM manually from: https://nssm.cc/download" -ForegroundColor Yellow
        Write-Host "  Extract to: C:\Apps\nssm" -ForegroundColor Yellow
        Read-Host "Press Enter after downloading and extracting NSSM"
    }
}

# Stop and remove existing service if it exists
try {
    & $nssmPath stop APITester 2>&1 | Out-Null
    & $nssmPath remove APITester confirm 2>&1 | Out-Null
} catch {}

# Install service
Write-Host "  Installing APITester service..." -NoNewline
& $nssmPath install APITester "$InstallPath\start_server.bat" | Out-Null
Write-Host " ✓" -ForegroundColor Green

# Configure service
& $nssmPath set APITester Description "API Automation Testing Platform" | Out-Null
& $nssmPath set APITester Start SERVICE_AUTO_START | Out-Null
& $nssmPath set APITester AppDirectory "$InstallPath" | Out-Null
& $nssmPath set APITester AppStdout "$InstallPath\logs\service-output.log" | Out-Null
& $nssmPath set APITester AppStderr "$InstallPath\logs\service-error.log" | Out-Null
& $nssmPath set APITester AppRotateFiles 1 | Out-Null
& $nssmPath set APITester AppRotateBytes 10485760 | Out-Null

Write-Host "  ✓ Service configured" -ForegroundColor Green

# ==============================================================================
# Step 11: Create Maintenance Scripts
# ==============================================================================
Write-Host "`n[11/12] Creating maintenance scripts..." -ForegroundColor Yellow

# Health check script
$healthCheckContent = @"
`$url = "http://localhost:$Port"
try {
    `$response = Invoke-WebRequest -Uri `$url -TimeoutSec 5 -UseBasicParsing
    if (`$response.StatusCode -eq 200) {
        Write-Host "✓ Service is healthy" -ForegroundColor Green
        exit 0
    }
} catch {
    Write-Host "✗ Service is not responding" -ForegroundColor Red
    exit 1
}
"@

Set-Content -Path "$InstallPath\healthcheck.ps1" -Value $healthCheckContent
Write-Host "  ✓ healthcheck.ps1 created" -ForegroundColor Green

# Log cleanup script
$cleanupContent = @"
`$LogPath = "$InstallPath\logs"
`$DaysToKeep = 30
Get-ChildItem -Path `$LogPath -Recurse -File |
    Where-Object {`$_.LastWriteTime -lt (Get-Date).AddDays(-`$DaysToKeep)} |
    Remove-Item -Force

`$ReportPath = "$InstallPath\output"
Get-ChildItem -Path `$ReportPath -Filter "*.html" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -Skip 100 |
    Remove-Item -Force
"@

Set-Content -Path "$InstallPath\cleanup_logs.ps1" -Value $cleanupContent
Write-Host "  ✓ cleanup_logs.ps1 created" -ForegroundColor Green

# Service management script
$manageContent = @"
param([string]`$action = "status")

switch (`$action.ToLower()) {
    "start"   { Start-Service -Name "APITester"; Get-Service -Name "APITester" }
    "stop"    { Stop-Service -Name "APITester"; Get-Service -Name "APITester" }
    "restart" { Restart-Service -Name "APITester"; Get-Service -Name "APITester" }
    "status"  { Get-Service -Name "APITester" }
    "logs"    { Get-Content "$InstallPath\logs\app.log" -Tail 50 -Wait }
    "errors"  { Get-Content "$InstallPath\logs\service-error.log" -Tail 50 -Wait }
    default   {
        Write-Host "Usage: .\manage.ps1 [start|stop|restart|status|logs|errors]"
    }
}
"@

Set-Content -Path "$InstallPath\manage.ps1" -Value $manageContent
Write-Host "  ✓ manage.ps1 created" -ForegroundColor Green

# ==============================================================================
# Step 12: Start the Service
# ==============================================================================
Write-Host "`n[12/12] Starting the service..." -ForegroundColor Yellow

if (Test-Path "$InstallPath\backend\database.py") {
    Start-Sleep -Seconds 2
    Start-Service -Name "APITester" -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3

    $service = Get-Service -Name "APITester"
    if ($service.Status -eq "Running") {
        Write-Host "  ✓ Service started successfully" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Service is in state: $($service.Status)" -ForegroundColor Yellow
        Write-Host "  ! Check logs: $InstallPath\logs\service-error.log" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ! Service not started - waiting for project files" -ForegroundColor Yellow
}

# ==============================================================================
# Installation Complete
# ==============================================================================
Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Yellow
Write-Host "  Local:    http://localhost:$Port" -ForegroundColor White
Write-Host "  Network:  http://${ServerIP}:$Port" -ForegroundColor White
Write-Host ""
Write-Host "Service Management:" -ForegroundColor Yellow
Write-Host "  Start:    Start-Service -Name 'APITester'" -ForegroundColor White
Write-Host "  Stop:     Stop-Service -Name 'APITester'" -ForegroundColor White
Write-Host "  Restart:  Restart-Service -Name 'APITester'" -ForegroundColor White
Write-Host "  Status:   Get-Service -Name 'APITester'" -ForegroundColor White
Write-Host "  Or use:   .\manage.ps1 [start|stop|restart|status|logs|errors]" -ForegroundColor White
Write-Host ""
Write-Host "Important Files:" -ForegroundColor Yellow
Write-Host "  Config:   $InstallPath\config.py" -ForegroundColor White
Write-Host "  Database: $InstallPath\database.db" -ForegroundColor White
Write-Host "  Logs:     $InstallPath\logs\" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Copy project files to: $InstallPath" -ForegroundColor White
Write-Host "  2. Restart service: Restart-Service -Name 'APITester'" -ForegroundColor White
Write-Host "  3. Test access: http://${ServerIP}:$Port" -ForegroundColor White
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

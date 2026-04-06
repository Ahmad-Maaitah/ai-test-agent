# ==============================================================================
# API Tester - Quick Fix Script
# ==============================================================================
# This script will try to fix common issues and start the service
# ==============================================================================

param(
    [switch]$Force
)

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "API Testing Platform - Quick Fix" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$installPath = "C:\Apps\APITester"

# ==============================================================================
# Step 1: Stop existing service
# ==============================================================================
Write-Host "[Step 1] Stopping service..." -ForegroundColor Yellow

try {
    Stop-Service -Name "APITester" -Force -ErrorAction SilentlyContinue
    Write-Host "  ✓ Service stopped" -ForegroundColor Green
} catch {
    Write-Host "  - Service was not running" -ForegroundColor Gray
}

Start-Sleep -Seconds 2

# ==============================================================================
# Step 2: Check if port is in use
# ==============================================================================
Write-Host "`n[Step 2] Checking port 5000..." -ForegroundColor Yellow

$portUsage = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($portUsage) {
    Write-Host "  ⚠ Port 5000 is in use by process $($portUsage.OwningProcess)" -ForegroundColor Yellow

    if ($Force) {
        Write-Host "  Killing process..." -NoNewline
        Stop-Process -Id $portUsage.OwningProcess -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Write-Host " ✓" -ForegroundColor Green
    } else {
        Write-Host "  Run with -Force flag to kill the process" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✓ Port 5000 is available" -ForegroundColor Green
}

# ==============================================================================
# Step 3: Check installation
# ==============================================================================
Write-Host "`n[Step 3] Verifying installation..." -ForegroundColor Yellow

if (-not (Test-Path $installPath)) {
    Write-Host "  ✗ Installation directory not found: $installPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run the automated setup first:" -ForegroundColor Yellow
    Write-Host "  cd C:\Temp\api-tester-deployment" -ForegroundColor White
    Write-Host "  .\automated_setup.ps1" -ForegroundColor White
    exit 1
}

# Check critical files
$criticalFiles = @(
    "run_production.py",
    "backend\database.py",
    "app\routes.py"
)

$missingFiles = @()
foreach ($file in $criticalFiles) {
    if (-not (Test-Path "$installPath\$file")) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "  ✗ Missing files:" -ForegroundColor Red
    $missingFiles | ForEach-Object { Write-Host "    - $_" -ForegroundColor Red }
    Write-Host ""
    Write-Host "Please copy project files:" -ForegroundColor Yellow
    Write-Host "  xcopy /E /I /Y C:\Temp\api-tester-deployment\package\* C:\Apps\APITester\" -ForegroundColor White
    exit 1
}

Write-Host "  ✓ All critical files present" -ForegroundColor Green

# ==============================================================================
# Step 4: Initialize database
# ==============================================================================
Write-Host "`n[Step 4] Checking database..." -ForegroundColor Yellow

if (Test-Path "$installPath\database.db") {
    Write-Host "  ✓ Database exists" -ForegroundColor Green
} else {
    Write-Host "  Creating database..." -NoNewline
    Set-Location $installPath
    & "$installPath\venv\Scripts\python.exe" -c "from backend.database import init_db; init_db()" 2>&1 | Out-Null
    if (Test-Path "$installPath\database.db") {
        Write-Host " ✓" -ForegroundColor Green
    } else {
        Write-Host " ⚠" -ForegroundColor Yellow
    }
}

# ==============================================================================
# Step 5: Test manual startup
# ==============================================================================
Write-Host "`n[Step 5] Testing manual startup..." -ForegroundColor Yellow

Set-Location $installPath

# Start the server in background
$job = Start-Job -ScriptBlock {
    Set-Location $using:installPath
    & "$using:installPath\venv\Scripts\python.exe" run_production.py
}

Write-Host "  Starting server..." -NoNewline
Start-Sleep -Seconds 5
Write-Host " ✓" -ForegroundColor Green

# Test connection
Write-Host "  Testing connection..." -NoNewline
Start-Sleep -Seconds 2

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    Write-Host " ✓" -ForegroundColor Green
    Write-Host "  ✓ Server is working!" -ForegroundColor Green

    # Stop the test server
    Stop-Job -Job $job
    Remove-Job -Job $job
} catch {
    Write-Host " ✗" -ForegroundColor Red
    Write-Host "  ✗ Server failed to start" -ForegroundColor Red

    # Show error output
    $jobOutput = Receive-Job -Job $job
    if ($jobOutput) {
        Write-Host "`n  Error output:" -ForegroundColor Yellow
        $jobOutput | Select-Object -Last 10 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    }

    Stop-Job -Job $job -ErrorAction SilentlyContinue
    Remove-Job -Job $job -ErrorAction SilentlyContinue

    Write-Host "`n  Try running manually to see full errors:" -ForegroundColor Yellow
    Write-Host "    cd C:\Apps\APITester" -ForegroundColor White
    Write-Host "    .\venv\Scripts\activate" -ForegroundColor White
    Write-Host "    python run_production.py" -ForegroundColor White
    exit 1
}

# ==============================================================================
# Step 6: Configure firewall
# ==============================================================================
Write-Host "`n[Step 6] Configuring firewall..." -ForegroundColor Yellow

try {
    Remove-NetFirewallRule -DisplayName "API Tester - Port 5000" -ErrorAction SilentlyContinue | Out-Null
} catch {}

try {
    New-NetFirewallRule -DisplayName "API Tester - Port 5000" `
        -Direction Inbound `
        -LocalPort 5000 `
        -Protocol TCP `
        -Action Allow `
        -Profile Domain,Private `
        -ErrorAction Stop | Out-Null
    Write-Host "  ✓ Firewall rule created" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Could not create firewall rule (may require admin)" -ForegroundColor Yellow
}

# ==============================================================================
# Step 7: Start Windows Service
# ==============================================================================
Write-Host "`n[Step 7] Starting Windows Service..." -ForegroundColor Yellow

try {
    Start-Service -Name "APITester" -ErrorAction Stop
    Start-Sleep -Seconds 5

    $service = Get-Service -Name "APITester"
    if ($service.Status -eq "Running") {
        Write-Host "  ✓ Service started successfully" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Service status: $($service.Status)" -ForegroundColor Red
        Write-Host "    Check logs: C:\Apps\APITester\logs\service-error.log" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ Failed to start service: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "    Check logs: C:\Apps\APITester\logs\service-error.log" -ForegroundColor Yellow
}

# ==============================================================================
# Step 8: Final test
# ==============================================================================
Write-Host "`n[Step 8] Testing final connection..." -ForegroundColor Yellow

Start-Sleep -Seconds 3

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
    Write-Host "  ✓ SUCCESS! Server is accessible" -ForegroundColor Green

    # Get local IP
    $localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "172.16.1.*"}).IPAddress

    Write-Host "`n================================================================================" -ForegroundColor Cyan
    Write-Host "Server is running successfully!" -ForegroundColor Green
    Write-Host "================================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Yellow
    Write-Host "  Local:    http://localhost:5000" -ForegroundColor White
    if ($localIP) {
        Write-Host "  Network:  http://${localIP}:5000" -ForegroundColor White
    }
    Write-Host ""
    Write-Host "Service Management:" -ForegroundColor Yellow
    Write-Host "  Status:   Get-Service -Name 'APITester'" -ForegroundColor White
    Write-Host "  Restart:  Restart-Service -Name 'APITester'" -ForegroundColor White
    Write-Host "  Logs:     Get-Content C:\Apps\APITester\logs\app.log -Tail 50 -Wait" -ForegroundColor White
    Write-Host ""
    Write-Host "================================================================================" -ForegroundColor Cyan

} catch {
    Write-Host "  ✗ Still cannot connect: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "  1. Check service logs:" -ForegroundColor White
    Write-Host "     Get-Content C:\Apps\APITester\logs\service-error.log" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Try running manually:" -ForegroundColor White
    Write-Host "     cd C:\Apps\APITester" -ForegroundColor Gray
    Write-Host "     .\venv\Scripts\activate" -ForegroundColor Gray
    Write-Host "     python run_production.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  3. Check if port is blocked:" -ForegroundColor White
    Write-Host "     netstat -ano | findstr :5000" -ForegroundColor Gray
    Write-Host ""
}

Write-Host ""

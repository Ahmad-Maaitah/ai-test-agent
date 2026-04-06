# ==============================================================================
# API Tester - Diagnostic Script
# ==============================================================================
# Run this on Windows Server to diagnose connection issues
# ==============================================================================

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "API Testing Platform - Diagnostic Tool" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

$installPath = "C:\Apps\APITester"
$port = 5000
$issues = @()
$warnings = @()

# ==============================================================================
# Check 1: Installation Directory
# ==============================================================================
Write-Host "[1/10] Checking installation directory..." -ForegroundColor Yellow

if (Test-Path $installPath) {
    Write-Host "  ✓ Installation directory exists: $installPath" -ForegroundColor Green

    # Check for key files
    $keyFiles = @(
        "run_production.py",
        "config.py",
        "backend\database.py",
        "app\routes.py",
        "venv\Scripts\python.exe"
    )

    foreach ($file in $keyFiles) {
        $fullPath = Join-Path $installPath $file
        if (Test-Path $fullPath) {
            Write-Host "  ✓ Found: $file" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Missing: $file" -ForegroundColor Red
            $issues += "Missing file: $file"
        }
    }
} else {
    Write-Host "  ✗ Installation directory not found: $installPath" -ForegroundColor Red
    $issues += "Installation directory not found"
}

# ==============================================================================
# Check 2: Python Installation
# ==============================================================================
Write-Host "`n[2/10] Checking Python..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found in PATH" -ForegroundColor Red
    $issues += "Python not installed or not in PATH"
}

# Check virtual environment Python
if (Test-Path "$installPath\venv\Scripts\python.exe") {
    $venvVersion = & "$installPath\venv\Scripts\python.exe" --version 2>&1
    Write-Host "  ✓ Virtual environment Python: $venvVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Virtual environment Python not found" -ForegroundColor Red
    $issues += "Virtual environment not created properly"
}

# ==============================================================================
# Check 3: Windows Service
# ==============================================================================
Write-Host "`n[3/10] Checking Windows Service..." -ForegroundColor Yellow

try {
    $service = Get-Service -Name "APITester" -ErrorAction Stop
    Write-Host "  ✓ Service exists: $($service.Name)" -ForegroundColor Green
    Write-Host "  Status: $($service.Status)" -ForegroundColor $(if ($service.Status -eq "Running") { "Green" } else { "Red" })

    if ($service.Status -ne "Running") {
        $issues += "Service is not running (Status: $($service.Status))"
    }
} catch {
    Write-Host "  ✗ Service not found" -ForegroundColor Red
    $issues += "Windows Service 'APITester' not installed"
}

# ==============================================================================
# Check 4: Port Listening
# ==============================================================================
Write-Host "`n[4/10] Checking if port $port is listening..." -ForegroundColor Yellow

$listening = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($listening) {
    Write-Host "  ✓ Port $port is listening" -ForegroundColor Green
    Write-Host "  Process: $($listening.OwningProcess)" -ForegroundColor Gray

    # Get process name
    $process = Get-Process -Id $listening.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "  Process Name: $($process.Name)" -ForegroundColor Gray
    }
} else {
    Write-Host "  ✗ Port $port is NOT listening" -ForegroundColor Red
    $issues += "Service is not listening on port $port"
}

# ==============================================================================
# Check 5: Firewall Rules
# ==============================================================================
Write-Host "`n[5/10] Checking Windows Firewall..." -ForegroundColor Yellow

$firewallRule = Get-NetFirewallRule -DisplayName "API Tester*" -ErrorAction SilentlyContinue
if ($firewallRule) {
    Write-Host "  ✓ Firewall rule exists" -ForegroundColor Green
    foreach ($rule in $firewallRule) {
        Write-Host "  - $($rule.DisplayName): $($rule.Enabled)" -ForegroundColor Gray
    }
} else {
    Write-Host "  ⚠ No firewall rule found" -ForegroundColor Yellow
    $warnings += "Firewall rule may need to be created"
}

# ==============================================================================
# Check 6: Log Files
# ==============================================================================
Write-Host "`n[6/10] Checking log files..." -ForegroundColor Yellow

$logFiles = @(
    "$installPath\logs\app.log",
    "$installPath\logs\service-output.log",
    "$installPath\logs\service-error.log"
)

foreach ($logFile in $logFiles) {
    if (Test-Path $logFile) {
        $size = (Get-Item $logFile).Length
        Write-Host "  ✓ Found: $(Split-Path $logFile -Leaf) ($size bytes)" -ForegroundColor Green

        # Check for recent errors
        if ($logFile -match "error") {
            $lastLines = Get-Content $logFile -Tail 5 -ErrorAction SilentlyContinue
            if ($lastLines) {
                Write-Host "    Last error entries:" -ForegroundColor Yellow
                $lastLines | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
            }
        }
    } else {
        Write-Host "  - Not found: $(Split-Path $logFile -Leaf)" -ForegroundColor Gray
    }
}

# ==============================================================================
# Check 7: Database
# ==============================================================================
Write-Host "`n[7/10] Checking database..." -ForegroundColor Yellow

if (Test-Path "$installPath\database.db") {
    $dbSize = (Get-Item "$installPath\database.db").Length
    Write-Host "  ✓ Database exists ($dbSize bytes)" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Database not found (will be created on first run)" -ForegroundColor Yellow
    $warnings += "Database file not found"
}

# ==============================================================================
# Check 8: Test Local Connection
# ==============================================================================
Write-Host "`n[8/10] Testing local connection..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:$port" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    Write-Host "  ✓ Local connection successful (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Local connection failed: $($_.Exception.Message)" -ForegroundColor Red
    $issues += "Cannot connect to http://localhost:$port"
}

# ==============================================================================
# Check 9: Test Network Connection
# ==============================================================================
Write-Host "`n[9/10] Testing network connection..." -ForegroundColor Yellow

try {
    $localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "172.16.1.*"}).IPAddress
    if ($localIP) {
        Write-Host "  Server IP: $localIP" -ForegroundColor Gray

        try {
            $response = Invoke-WebRequest -Uri "http://${localIP}:$port" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            Write-Host "  ✓ Network connection successful (Status: $($response.StatusCode))" -ForegroundColor Green
        } catch {
            Write-Host "  ✗ Network connection failed: $($_.Exception.Message)" -ForegroundColor Red
            $issues += "Cannot connect via IP: http://${localIP}:$port"
        }
    } else {
        Write-Host "  ⚠ Could not determine server IP address" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ⚠ Could not test network connection" -ForegroundColor Yellow
}

# ==============================================================================
# Check 10: Dependencies
# ==============================================================================
Write-Host "`n[10/10] Checking Python dependencies..." -ForegroundColor Yellow

if (Test-Path "$installPath\venv\Scripts\pip.exe") {
    $packages = & "$installPath\venv\Scripts\pip.exe" list 2>&1

    $requiredPackages = @("Flask", "SQLAlchemy", "requests", "pytest")
    $missingPackages = @()

    foreach ($pkg in $requiredPackages) {
        if ($packages -match $pkg) {
            Write-Host "  ✓ $pkg installed" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $pkg not installed" -ForegroundColor Red
            $missingPackages += $pkg
        }
    }

    if ($missingPackages.Count -gt 0) {
        $issues += "Missing Python packages: $($missingPackages -join ', ')"
    }
} else {
    Write-Host "  ⚠ Cannot check dependencies - pip not found" -ForegroundColor Yellow
}

# ==============================================================================
# Summary
# ==============================================================================
Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host "Diagnostic Summary" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan

if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "`n✓ All checks passed! System appears healthy." -ForegroundColor Green
    Write-Host "`nAccess URL: http://localhost:$port" -ForegroundColor White
} else {
    if ($issues.Count -gt 0) {
        Write-Host "`n✗ Issues Found ($($issues.Count)):" -ForegroundColor Red
        $issues | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    }

    if ($warnings.Count -gt 0) {
        Write-Host "`n⚠ Warnings ($($warnings.Count)):" -ForegroundColor Yellow
        $warnings | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    }

    Write-Host "`n================================================================================" -ForegroundColor Cyan
    Write-Host "Recommended Actions" -ForegroundColor Yellow
    Write-Host "================================================================================" -ForegroundColor Cyan

    if ($issues -match "Installation directory not found") {
        Write-Host "`n1. Run the automated setup script:" -ForegroundColor White
        Write-Host "   cd C:\Temp\api-tester-deployment" -ForegroundColor Gray
        Write-Host "   .\automated_setup.ps1" -ForegroundColor Gray
    }

    if ($issues -match "Service is not running") {
        Write-Host "`n2. Try starting the service:" -ForegroundColor White
        Write-Host "   Start-Service -Name 'APITester'" -ForegroundColor Gray
        Write-Host "   Get-Service -Name 'APITester'" -ForegroundColor Gray
    }

    if ($issues -match "Service is not listening") {
        Write-Host "`n3. Check service error logs:" -ForegroundColor White
        Write-Host "   Get-Content C:\Apps\APITester\logs\service-error.log -Tail 50" -ForegroundColor Gray
        Write-Host "`n   Try running manually to see errors:" -ForegroundColor White
        Write-Host "   cd C:\Apps\APITester" -ForegroundColor Gray
        Write-Host "   .\venv\Scripts\activate" -ForegroundColor Gray
        Write-Host "   python run_production.py" -ForegroundColor Gray
    }

    if ($issues -match "Python not installed") {
        Write-Host "`n4. Install Python:" -ForegroundColor White
        Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Gray
        Write-Host "   Make sure to check 'Add Python to PATH'" -ForegroundColor Gray
    }

    if ($issues -match "Missing Python packages") {
        Write-Host "`n5. Install dependencies:" -ForegroundColor White
        Write-Host "   cd C:\Apps\APITester" -ForegroundColor Gray
        Write-Host "   .\venv\Scripts\activate" -ForegroundColor Gray
        Write-Host "   pip install -r requirements.txt" -ForegroundColor Gray
    }
}

Write-Host "`n================================================================================" -ForegroundColor Cyan
Write-Host ""

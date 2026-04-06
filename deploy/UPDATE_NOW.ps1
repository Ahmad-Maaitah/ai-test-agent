# ==============================================================================
# UPDATE SERVER NOW - Pull Latest Code from GitHub
# ==============================================================================
# Run this on Windows Server to get the UTF-8 fix
# ==============================================================================

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Updating API Testing Platform from GitHub" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitInstalled) {
    Write-Host "Git is not installed on this server." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Installing Git for Windows..." -ForegroundColor Yellow

    # Download Git installer
    $gitInstallerUrl = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"
    $gitInstallerPath = "$env:TEMP\Git-Installer.exe"

    Write-Host "Downloading Git installer..." -ForegroundColor Yellow
    try {
        Invoke-WebRequest -Uri $gitInstallerUrl -OutFile $gitInstallerPath
        Write-Host "Installing Git (this will take 1-2 minutes)..." -ForegroundColor Yellow
        Start-Process -FilePath $gitInstallerPath -ArgumentList "/VERYSILENT /NORESTART" -Wait

        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

        Write-Host "Git installed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "Failed to install Git automatically." -ForegroundColor Red
        Write-Host "Please download and install Git manually from: https://git-scm.com/download/win" -ForegroundColor Yellow
        Write-Host ""
        Read-Host "Press Enter after installing Git"
    }
}

Write-Host ""
Write-Host "[Step 1/5] Stopping server..." -ForegroundColor Yellow

# Try to stop the service if it exists
$service = Get-Service -Name "APITester" -ErrorAction SilentlyContinue
if ($service) {
    Stop-Service -Name "APITester" -Force
    Write-Host "  Service stopped" -ForegroundColor Green
} else {
    Write-Host "  (No service found - if server is running, please stop it with Ctrl+C)" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter when server is stopped"
}

Write-Host ""
Write-Host "[Step 2/5] Checking if git repository exists..." -ForegroundColor Yellow

cd C:\Apps\APITester

# Check if this is a git repository
$isGitRepo = Test-Path ".git"

if (-not $isGitRepo) {
    Write-Host "  Not a git repository yet. Initializing..." -ForegroundColor Yellow
    Write-Host ""

    # Initialize git repository
    git init

    # Add remote
    git remote add origin https://github.com/Ahmad-Maaitah/ai-test-agent.git

    # Fetch from remote
    Write-Host "  Fetching from GitHub..." -ForegroundColor Yellow
    git fetch origin main

    # Reset to match remote
    Write-Host "  Syncing with GitHub..." -ForegroundColor Yellow
    git reset --hard origin/main

    Write-Host "  Git repository initialized and synced!" -ForegroundColor Green
} else {
    Write-Host "  Git repository found!" -ForegroundColor Green
}

Write-Host ""
Write-Host "[Step 3/5] Pulling latest code from GitHub..." -ForegroundColor Yellow

# Pull latest changes
git pull origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Code updated successfully!" -ForegroundColor Green
} else {
    Write-Host "  Warning: Git pull had issues. Trying force update..." -ForegroundColor Yellow
    git fetch origin main
    git reset --hard origin/main
    Write-Host "  Force update complete!" -ForegroundColor Green
}

Write-Host ""
Write-Host "[Step 4/5] Checking UTF-8 fix..." -ForegroundColor Yellow

# Check if the fix is present
$utilsFile = "backend\utils.py"
$fixPresent = Select-String -Path $utilsFile -Pattern "encoding='utf-8'" -Quiet

if ($fixPresent) {
    Write-Host "  UTF-8 fix is present in the code!" -ForegroundColor Green
} else {
    Write-Host "  Warning: UTF-8 fix might not be in this version" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[Step 5/5] Starting server..." -ForegroundColor Yellow

# Try to start service first
if ($service) {
    Start-Service -Name "APITester"
    Write-Host "  Service started!" -ForegroundColor Green
} else {
    Write-Host "  Starting server manually..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Run this command to start the server:" -ForegroundColor White
    Write-Host "  .\venv\Scripts\python.exe main.py" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "UPDATE COMPLETE!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "UTF-8 Fix Applied:" -ForegroundColor White
Write-Host "  - HTML reports with special characters will now work correctly" -ForegroundColor Gray
Write-Host "  - The 'Unexpected token' error should be fixed" -ForegroundColor Gray
Write-Host ""
Write-Host "Server URL: http://172.16.1.4:5001" -ForegroundColor White
Write-Host ""
Write-Host "Test the fix by running an API test that generates a report!" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan

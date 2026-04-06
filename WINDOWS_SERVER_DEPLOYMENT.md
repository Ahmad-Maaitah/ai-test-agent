# Windows Server Deployment Guide
## API Automation Testing Platform - Production Setup

**Server Details:**
- IP Address: `172.16.1.4`
- Computer Name: `172.16.1.4`
- Username: `administrator`
- OS: Windows Server

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Server Setup](#initial-server-setup)
3. [Install Required Software](#install-required-software)
4. [Deploy the Application](#deploy-the-application)
5. [Configure the Application](#configure-the-application)
6. [Set Up Windows Service](#set-up-windows-service)
7. [Configure Firewall & Network](#configure-firewall--network)
8. [Security Configuration](#security-configuration)
9. [Access & Testing](#access--testing)
10. [Monitoring & Logs](#monitoring--logs)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools
- Python 3.9 or higher
- Git for Windows
- SQLite (included with Python)
- Text editor (Notepad++ or VS Code)
- Chrome or Edge browser

### Network Requirements
- Server accessible on LAN: `172.16.1.4`
- Port 5000 or 80 open for HTTP access
- Outbound internet access (for API testing)

---

## Initial Server Setup

### Step 1: Connect to the Server

**Option A: Remote Desktop (Recommended)**
```
1. Open Remote Desktop Connection (mstsc.exe)
2. Enter: 172.16.1.4
3. Username: administrator
4. Password: Amman@2026
5. Click Connect
```

**Option B: From Command Line**
```cmd
mstsc /v:172.16.1.4
```

### Step 2: Create Application Directory

Open PowerShell as Administrator and run:

```powershell
# Create application directory
New-Item -Path "C:\Apps" -ItemType Directory -Force
New-Item -Path "C:\Apps\APITester" -ItemType Directory -Force
New-Item -Path "C:\Apps\APITester\logs" -ItemType Directory -Force

# Navigate to the directory
cd C:\Apps\APITester
```

---

## Install Required Software

### Step 3: Install Python 3.11

1. **Download Python:**
   - Open Edge browser
   - Go to: https://www.python.org/downloads/windows/
   - Download "Windows installer (64-bit)" for Python 3.11.x

2. **Install Python:**
   ```
   - Run the installer
   - ✓ Check "Add Python to PATH"
   - ✓ Check "Install for all users"
   - Click "Install Now"
   - Wait for installation to complete
   ```

3. **Verify Installation:**
   ```powershell
   python --version
   # Should show: Python 3.11.x

   pip --version
   # Should show: pip 23.x.x
   ```

### Step 4: Install Git for Windows

1. **Download Git:**
   - Go to: https://git-scm.com/download/win
   - Download "64-bit Git for Windows Setup"

2. **Install Git:**
   ```
   - Run the installer
   - Use default settings
   - Click "Next" through all options
   - Click "Install"
   ```

3. **Verify Installation:**
   ```powershell
   git --version
   # Should show: git version 2.x.x
   ```

---

## Deploy the Application

### Step 5: Clone or Copy the Project

**Option A: Using Git (if repository is available)**
```powershell
cd C:\Apps\APITester
git clone https://github.com/your-org/api-testing-platform.git .
```

**Option B: Manual Copy from Your Mac**

On your Mac:
```bash
# Create a deployment package
cd "/Users/Admin/Documents/AI/New API testing/API -AI Testing"
tar -czf api-tester-deploy.tar.gz \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='*.pyc' \
  --exclude='output/*' \
  .

# Copy to Windows Server (using SCP or shared folder)
# Method 1: If you have SSH enabled on Windows
scp api-tester-deploy.tar.gz administrator@172.16.1.4:C:/Apps/APITester/

# Method 2: Use a shared folder or USB drive
```

On Windows Server:
```powershell
cd C:\Apps\APITester

# If you received a .tar.gz file, extract it using:
# Install 7-Zip first: https://www.7-zip.org/download.html
# Then extract with: 7z x api-tester-deploy.tar.gz
# Then extract again: 7z x api-tester-deploy.tar
```

**Option C: Create Files Manually**

If transferring is difficult, I can provide you with a PowerShell script to download all files directly.

### Step 6: Install Python Dependencies

```powershell
cd C:\Apps\APITester

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 7: Initialize the Database

```powershell
# Still in virtual environment
python -c "from backend.database import init_db; init_db(); print('Database initialized successfully')"

# Run migration script to populate from data.json (if needed)
python migrate_to_db.py
```

---

## Configure the Application

### Step 8: Create Production Configuration

Create a new file `config.py`:

```powershell
notepad C:\Apps\APITester\config.py
```

Add the following content:

```python
"""Production configuration for Windows Server."""
import os

class Config:
    # Server Configuration
    HOST = '0.0.0.0'  # Listen on all network interfaces
    PORT = 5000
    DEBUG = False

    # Database
    DATABASE_PATH = r'C:\Apps\APITester\database.db'

    # Logging
    LOG_DIR = r'C:\Apps\APITester\logs'
    LOG_FILE = os.path.join(LOG_DIR, 'app.log')
    LOG_LEVEL = 'INFO'

    # Output/Reports
    OUTPUT_DIR = r'C:\Apps\APITester\output'

    # Security
    SECRET_KEY = 'CHANGE-THIS-TO-RANDOM-SECRET-KEY-IN-PRODUCTION'

    # Performance
    THREAD_TIMEOUT = 300  # 5 minutes
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
```

### Step 9: Update app.py for Production

Create `run_production.py`:

```powershell
notepad C:\Apps\APITester\run_production.py
```

Add this content:

```python
"""Production runner for API Testing Platform."""
import os
import sys
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from config import Config

def setup_logging():
    """Configure production logging."""
    os.makedirs(Config.LOG_DIR, exist_ok=True)

    # Create formatters
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )

    # File handler with rotation
    file_handler = RotatingFileHandler(
        Config.LOG_FILE,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger

if __name__ == '__main__':
    # Setup logging
    logger = setup_logging()
    logger.info('='*80)
    logger.info('Starting API Testing Platform - Production Mode')
    logger.info(f'Server: {Config.HOST}:{Config.PORT}')
    logger.info(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    logger.info('='*80)

    # Ensure required directories exist
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

    # Initialize database
    from backend.database import init_db
    init_db()
    logger.info('Database initialized')

    # Create Flask app
    app = create_app()

    # Run server
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
```

### Step 10: Update app/__init__.py

Modify `app/__init__.py` to work with config:

```python
"""Flask application factory."""
from flask import Flask
import os

def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration
    if config:
        app.config.from_object(config)
    else:
        try:
            from config import Config
            app.config.from_object(Config)
        except ImportError:
            # Fallback to development config
            app.config['DEBUG'] = True

    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
```

---

## Set Up Windows Service

### Step 11: Install NSSM (Non-Sucking Service Manager)

```powershell
# Download NSSM
# Go to: https://nssm.cc/download
# Download nssm-2.24.zip

# Extract to C:\Apps\nssm
New-Item -Path "C:\Apps\nssm" -ItemType Directory -Force
# Extract the downloaded ZIP to C:\Apps\nssm

# Add to PATH (run in PowerShell as Admin)
[Environment]::SetEnvironmentVariable(
    "Path",
    $env:Path + ";C:\Apps\nssm\win64",
    [EnvironmentVariableTarget]::Machine
)

# Refresh environment
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")

# Verify installation
nssm --version
```

### Step 12: Create the Windows Service

```powershell
# Create a batch file to run the application
@"
@echo off
cd /d C:\Apps\APITester
call venv\Scripts\activate.bat
python run_production.py
"@ | Out-File -FilePath C:\Apps\APITester\start_server.bat -Encoding ASCII

# Install the service
nssm install APITester "C:\Apps\APITester\start_server.bat"

# Configure the service
nssm set APITester Description "API Automation Testing Platform"
nssm set APITester Start SERVICE_AUTO_START
nssm set APITester AppDirectory "C:\Apps\APITester"
nssm set APITester AppStdout "C:\Apps\APITester\logs\service-output.log"
nssm set APITester AppStderr "C:\Apps\APITester\logs\service-error.log"
nssm set APITester AppRotateFiles 1
nssm set APITester AppRotateBytes 10485760  # 10MB

# Start the service
nssm start APITester

# Check service status
nssm status APITester
```

**Alternative: Manual Service Management**

```powershell
# Start service
Start-Service -Name "APITester"

# Stop service
Stop-Service -Name "APITester"

# Restart service
Restart-Service -Name "APITester"

# Check service status
Get-Service -Name "APITester"
```

---

## Configure Firewall & Network

### Step 13: Open Firewall Ports

```powershell
# Allow port 5000 for API Testing Platform
New-NetFirewallRule -DisplayName "API Tester - Port 5000" `
    -Direction Inbound `
    -LocalPort 5000 `
    -Protocol TCP `
    -Action Allow `
    -Profile Domain,Private

# Optional: Also allow port 80 if using reverse proxy
New-NetFirewallRule -DisplayName "HTTP - Port 80" `
    -Direction Inbound `
    -LocalPort 80 `
    -Protocol TCP `
    -Action Allow `
    -Profile Domain,Private

# Verify firewall rules
Get-NetFirewallRule -DisplayName "API Tester*"
```

### Step 14: Test Local Access

```powershell
# Check if service is listening
netstat -ano | findstr :5000

# Test from localhost
Start-Process "http://localhost:5000"

# Or use curl
curl http://localhost:5000
```

### Step 15: Configure for Network Access

**Option A: Direct Access (Simple)**

Your team can access the application at:
```
http://172.16.1.4:5000
```

**Option B: Use Port 80 with URL Rewrite (Recommended)**

Install IIS as reverse proxy:

1. **Install IIS:**
```powershell
Install-WindowsFeature -name Web-Server -IncludeManagementTools
```

2. **Install URL Rewrite Module:**
   - Download from: https://www.iis.net/downloads/microsoft/url-rewrite
   - Install the module

3. **Install Application Request Routing (ARR):**
   - Download from: https://www.iis.net/downloads/microsoft/application-request-routing
   - Install ARR

4. **Configure Reverse Proxy:**

Create `C:\inetpub\wwwroot\web.config`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="ReverseProxyInboundRule1" stopProcessing="true">
                    <match url="(.*)" />
                    <action type="Rewrite" url="http://localhost:5000/{R:1}" />
                </rule>
            </rules>
        </rewrite>
    </system.webServer>
</configuration>
```

5. **Enable ARR Proxy:**
   - Open IIS Manager
   - Click on server name
   - Double-click "Application Request Routing Cache"
   - Click "Server Proxy Settings" in right panel
   - Check "Enable proxy"
   - Click "Apply"

Now your team can access at:
```
http://172.16.1.4
```

**Option C: Use DNS Name (Best Practice)**

If you have internal DNS:

1. Create DNS A record: `api-tester.yourcompany.local` → `172.16.1.4`
2. Access via: `http://api-tester.yourcompany.local`

---

## Security Configuration

### Step 16: Implement Security Best Practices

**1. Change Default Secret Key:**

```powershell
# Generate a random secret key
python -c "import secrets; print(secrets.token_hex(32))"
# Copy the output and update config.py SECRET_KEY
```

**2. Create Service Account (Recommended):**

```powershell
# Create dedicated service account
$Password = ConvertTo-SecureString "SecureP@ssw0rd123!" -AsPlainText -Force
New-LocalUser -Name "apitester_service" -Password $Password -Description "API Tester Service Account"

# Add to Users group (not Administrators)
Add-LocalGroupMember -Group "Users" -Member "apitester_service"

# Set folder permissions
icacls "C:\Apps\APITester" /grant "apitester_service:(OI)(CI)F" /T

# Update NSSM service to use this account
nssm set APITester ObjectName ".\apitester_service" "SecureP@ssw0rd123!"
```

**3. Enable HTTPS (Optional but Recommended):**

For production use, set up SSL certificate:
- Use self-signed certificate for internal use
- Use Let's Encrypt or company certificate for production

**4. Restrict Access by IP:**

```powershell
# Allow access only from specific IP range
New-NetFirewallRule -DisplayName "API Tester - Restricted Access" `
    -Direction Inbound `
    -LocalPort 5000 `
    -Protocol TCP `
    -Action Allow `
    -RemoteAddress 172.16.1.0/24
```

**5. Secure Credentials:**

Never store passwords in code. Use environment variables:

```powershell
# Set environment variables for the service
nssm set APITester AppEnvironmentExtra "DB_PASSWORD=SecurePassword"
```

---

## Access & Testing

### Step 17: Access URLs

**For Team Members:**

```
Internal LAN Access:
http://172.16.1.4:5000

OR (if using IIS reverse proxy):
http://172.16.1.4

OR (if using DNS):
http://api-tester.yourcompany.local
```

**Login/Authentication:**

Currently, the application doesn't have authentication. To add basic auth:

Create `auth_middleware.py`:

```python
from functools import wraps
from flask import request, Response

def check_auth(username, password):
    """Check if credentials are valid."""
    # CHANGE THESE IN PRODUCTION
    return username == 'admin' and password == 'Amman@2026'

def authenticate():
    """Send 401 response."""
    return Response(
        'Authentication required.', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    """Decorator for requiring authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
```

Then apply to routes in `app/routes.py`:

```python
from auth_middleware import requires_auth

@main_bp.route('/')
@requires_auth
def index():
    return render_template('index.html')
```

### Step 18: Team Access Instructions

**Send this to your team:**

```
API Automation Testing Platform - Access Guide

URL: http://172.16.1.4:5000

Login Credentials (if authentication is enabled):
- Username: admin
- Password: [provided separately]

Features:
1. Create and manage API test cases
2. Execute API tests with validation rules
3. Generate detailed HTML reports
4. Track test history and results
5. Manage test variables and environments

Getting Started:
1. Open the URL in your browser (Chrome/Edge recommended)
2. Log in with provided credentials
3. Click "Add API" to create your first test
4. Use "Run Selected" to execute tests
5. View reports in the Dashboard section

Support:
- Contact: [Your contact info]
- Documentation: Available in the Help section
```

---

## Monitoring & Logs

### Step 19: Log Locations

```
Application Logs:
C:\Apps\APITester\logs\app.log

Service Logs:
C:\Apps\APITester\logs\service-output.log
C:\Apps\APITester\logs\service-error.log

Test Reports:
C:\Apps\APITester\output\

Database:
C:\Apps\APITester\database.db
```

### Step 20: View Logs in Real-Time

```powershell
# View application log
Get-Content C:\Apps\APITester\logs\app.log -Tail 50 -Wait

# View service output
Get-Content C:\Apps\APITester\logs\service-output.log -Tail 50 -Wait

# View errors
Get-Content C:\Apps\APITester\logs\service-error.log -Tail 50 -Wait
```

### Step 21: Set Up Log Rotation

Logs are automatically rotated when they reach 10MB (configured in NSSM).

Manual cleanup script `cleanup_logs.ps1`:

```powershell
# Delete logs older than 30 days
$LogPath = "C:\Apps\APITester\logs"
$DaysToKeep = 30
Get-ChildItem -Path $LogPath -Recurse -File |
    Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-$DaysToKeep)} |
    Remove-Item -Force

# Delete old reports (keep last 100)
$ReportPath = "C:\Apps\APITester\output"
Get-ChildItem -Path $ReportPath -Filter "*.html" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -Skip 100 |
    Remove-Item -Force
```

Schedule this script to run weekly:

```powershell
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\Apps\APITester\cleanup_logs.ps1"
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2am
$Principal = New-ScheduledTaskPrincipal -UserID "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -Action $Action -Trigger $Trigger -Principal $Principal -TaskName "API Tester Log Cleanup"
```

---

## Troubleshooting

### Common Issues

**Issue 1: Service won't start**

```powershell
# Check service status
nssm status APITester

# View service logs
Get-Content C:\Apps\APITester\logs\service-error.log

# Check if Python is in PATH
python --version

# Restart service manually
cd C:\Apps\APITester
.\venv\Scripts\activate
python run_production.py

# Check for port conflicts
netstat -ano | findstr :5000
```

**Issue 2: Can't access from network**

```powershell
# Verify firewall rule
Get-NetFirewallRule -DisplayName "API Tester*"

# Test from server itself
curl http://localhost:5000

# Check if service is listening on all interfaces
netstat -ano | findstr :5000
# Should show 0.0.0.0:5000 or [::]:5000

# Verify Windows Firewall is not blocking
Get-NetFirewallProfile | Select-Object Name, Enabled
```

**Issue 3: Database errors**

```powershell
# Reinitialize database
cd C:\Apps\APITester
.\venv\Scripts\activate
python -c "from backend.database import init_db; init_db()"

# Check database file
dir database.db

# Backup database
Copy-Item database.db "database_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db"
```

**Issue 4: Module not found errors**

```powershell
# Reinstall dependencies
cd C:\Apps\APITester
.\venv\Scripts\activate
pip install -r requirements.txt --force-reinstall

# Verify all packages
pip list
```

**Issue 5: Performance issues**

```powershell
# Check system resources
Get-Process -Name python | Select-Object CPU, Memory, PM

# Increase worker threads in config.py
# Add to Config class:
WORKERS = 4

# Restart service
Restart-Service -Name "APITester"
```

### Health Check Script

Create `healthcheck.ps1`:

```powershell
$url = "http://localhost:5000"
$timeout = 5

try {
    $response = Invoke-WebRequest -Uri $url -TimeoutSec $timeout -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Service is healthy" -ForegroundColor Green
        exit 0
    } else {
        Write-Host "✗ Service returned status: $($response.StatusCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Service is not responding: $_" -ForegroundColor Red
    exit 1
}
```

Schedule health checks:

```powershell
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\Apps\APITester\healthcheck.ps1"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -Action $Action -Trigger $Trigger -TaskName "API Tester Health Check"
```

---

## Quick Start Checklist

- [ ] Remote desktop connected to 172.16.1.4
- [ ] Python 3.11 installed
- [ ] Git installed
- [ ] Project files copied to C:\Apps\APITester
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Database initialized
- [ ] config.py created
- [ ] run_production.py created
- [ ] NSSM installed
- [ ] Windows service created
- [ ] Service started successfully
- [ ] Firewall ports opened
- [ ] Local access verified (http://localhost:5000)
- [ ] Network access verified (http://172.16.1.4:5000)
- [ ] Team access instructions sent
- [ ] Logs configured and monitored

---

## Maintenance Tasks

### Daily
- [ ] Check service status
- [ ] Review error logs
- [ ] Verify team can access

### Weekly
- [ ] Review all logs
- [ ] Backup database
- [ ] Clean old reports (automated)

### Monthly
- [ ] Update dependencies (if needed)
- [ ] Review security settings
- [ ] Check disk space
- [ ] Update documentation

---

## Support & Contacts

**Server Information:**
- IP: 172.16.1.4
- Service Name: APITester
- Port: 5000

**Key Files:**
- App Directory: C:\Apps\APITester
- Config: C:\Apps\APITester\config.py
- Database: C:\Apps\APITester\database.db
- Logs: C:\Apps\APITester\logs\

**Emergency Procedures:**
```powershell
# Stop service
Stop-Service -Name "APITester"

# Start service
Start-Service -Name "APITester"

# Restart service
Restart-Service -Name "APITester"

# View logs
Get-Content C:\Apps\APITester\logs\app.log -Tail 100
```

---

## Final Access URL

**Primary Access:**
```
http://172.16.1.4:5000
```

**Alternative (if IIS configured):**
```
http://172.16.1.4
```

**With DNS (if configured):**
```
http://api-tester.yourcompany.local
```

---

*Last Updated: April 2026*
*Version: 1.0*

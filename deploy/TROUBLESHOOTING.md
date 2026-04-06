# Connection Refused - Troubleshooting Guide

## Problem: "This site can't be reached - 172.16.1.4 refused to connect"

This means the server is not running or not accessible. Follow these steps to diagnose and fix:

---

## Quick Fix (Try This First!)

On your Windows Server, open **PowerShell as Administrator** and run:

```powershell
cd C:\Apps\APITester
.\quick_fix.ps1
```

**OR** if that doesn't work:

```powershell
cd C:\Apps\APITester
.\quick_fix.ps1 -Force
```

This script will automatically:
- ✅ Stop any conflicting processes
- ✅ Check all files are in place
- ✅ Initialize the database
- ✅ Configure the firewall
- ✅ Start the service
- ✅ Test the connection

**If the quick fix works, you're done!** If not, continue below.

---

## Diagnostic Tool

Run this to see what's wrong:

```powershell
cd C:\Apps\APITester
.\diagnose.ps1
```

This will check:
- Installation files
- Python installation
- Windows Service status
- Port availability
- Firewall rules
- Log files
- Database
- Local and network connections
- Dependencies

---

## Common Issues & Solutions

### Issue 1: Service Not Installed

**Symptoms:**
- Error: "Service 'APITester' not found"

**Solution:**
```powershell
# Run the automated setup
cd C:\Temp\api-tester-deployment
.\automated_setup.ps1
```

---

### Issue 2: Service Won't Start

**Symptoms:**
- Service status shows "Stopped"
- Cannot start the service

**Solution:**

**Step 1:** Check error logs
```powershell
Get-Content C:\Apps\APITester\logs\service-error.log -Tail 50
```

**Step 2:** Try manual startup to see errors
```powershell
cd C:\Apps\APITester
.\venv\Scripts\activate
python run_production.py
```

Look for error messages like:
- `ModuleNotFoundError` → Missing Python packages
- `No module named 'backend'` → Missing project files
- `Permission denied` → File permission issues
- `Address already in use` → Port 5000 is blocked

---

### Issue 3: Missing Project Files

**Symptoms:**
- `No module named 'backend'`
- `No module named 'app'`
- Missing files in C:\Apps\APITester

**Solution:**
```powershell
# Copy project files
xcopy /E /I /Y C:\Temp\api-tester-deployment\package\* C:\Apps\APITester\

# Restart service
Restart-Service -Name "APITester"
```

---

### Issue 4: Port 5000 Already in Use

**Symptoms:**
- `Address already in use`
- `OSError: [WinError 10048]`

**Solution:**

**Option A:** Kill the process using port 5000
```powershell
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual number)
taskkill /F /PID <PID>

# Restart service
Restart-Service -Name "APITester"
```

**Option B:** Change to a different port
```powershell
# Edit config
notepad C:\Apps\APITester\config.py
# Change: PORT = 5000  →  PORT = 8080

# Update firewall
New-NetFirewallRule -DisplayName "API Tester - Port 8080" `
    -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow

# Restart service
Restart-Service -Name "APITester"

# Access on new port: http://172.16.1.4:8080
```

---

### Issue 5: Python Not Installed

**Symptoms:**
- `python is not recognized as an internal or external command`

**Solution:**

1. Download Python from: https://www.python.org/downloads/windows/
2. Install Python 3.11.x
3. ✅ **IMPORTANT:** Check "Add Python to PATH"
4. ✅ Check "Install for all users"
5. Restart PowerShell
6. Run: `python --version` to verify

Then run setup again:
```powershell
cd C:\Temp\api-tester-deployment
.\automated_setup.ps1
```

---

### Issue 6: Missing Python Packages

**Symptoms:**
- `ModuleNotFoundError: No module named 'flask'`
- `No module named 'sqlalchemy'`

**Solution:**
```powershell
cd C:\Apps\APITester
.\venv\Scripts\activate
pip install -r requirements.txt

# Restart service
Restart-Service -Name "APITester"
```

---

### Issue 7: Firewall Blocking Connection

**Symptoms:**
- Can access locally (`http://localhost:5000`) ✓
- Cannot access from network (`http://172.16.1.4:5000`) ✗

**Solution:**
```powershell
# Create firewall rule
New-NetFirewallRule -DisplayName "API Tester - Port 5000" `
    -Direction Inbound `
    -LocalPort 5000 `
    -Protocol TCP `
    -Action Allow `
    -Profile Domain,Private

# Verify rule
Get-NetFirewallRule -DisplayName "API Tester*"

# Test from another computer
Start-Process "http://172.16.1.4:5000"
```

---

### Issue 8: Database Initialization Failed

**Symptoms:**
- `sqlite3.DatabaseError`
- `OperationalError: unable to open database file`

**Solution:**
```powershell
cd C:\Apps\APITester
.\venv\Scripts\activate

# Reinitialize database
python -c "from backend.database import init_db; init_db()"

# Verify database exists
dir database.db

# Restart service
Restart-Service -Name "APITester"
```

---

## Step-by-Step Manual Startup

If automated scripts don't work, try starting manually:

### Step 1: Navigate to installation directory
```powershell
cd C:\Apps\APITester
```

### Step 2: Activate virtual environment
```powershell
.\venv\Scripts\activate
```

You should see `(venv)` in your prompt.

### Step 3: Run the server
```powershell
python run_production.py
```

### Step 4: Look for startup messages

**Good output:**
```
Starting API Testing Platform - Production Mode
Server: 0.0.0.0:5000
Database initialized
Server starting...
* Running on http://0.0.0.0:5000
```

**Bad output (errors):**
- Read the error message carefully
- Copy the error and search below for solution

### Step 5: Test in browser
Open browser: `http://localhost:5000`

### Step 6: If working, Ctrl+C to stop and install as service
```powershell
# Exit manual mode
# Press Ctrl+C

# Start as service
Start-Service -Name "APITester"
```

---

## Complete Reset (Nuclear Option)

If nothing works, start fresh:

```powershell
# Stop and remove service
Stop-Service -Name "APITester" -Force
nssm remove APITester confirm

# Delete installation
Remove-Item -Path C:\Apps\APITester -Recurse -Force

# Run setup again
cd C:\Temp\api-tester-deployment
.\automated_setup.ps1

# Copy files
xcopy /E /I /Y C:\Temp\api-tester-deployment\package\* C:\Apps\APITester\

# Start service
Start-Service -Name "APITester"
```

---

## Check Service Status

```powershell
# Service status
Get-Service -Name "APITester"

# Detailed status
Get-Service -Name "APITester" | Format-List *

# Service logs (live monitoring)
Get-Content C:\Apps\APITester\logs\app.log -Tail 50 -Wait

# Error logs
Get-Content C:\Apps\APITester\logs\service-error.log -Tail 50

# Output logs
Get-Content C:\Apps\APITester\logs\service-output.log -Tail 50
```

---

## Network Testing

Test if server is accessible:

### From Windows Server itself:
```powershell
# Test localhost
Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing

# Test IP
Invoke-WebRequest -Uri "http://172.16.1.4:5000" -UseBasicParsing

# Check if port is listening
netstat -ano | findstr :5000
```

### From another computer:
```powershell
# Test connection
Test-NetConnection -ComputerName 172.16.1.4 -Port 5000

# Or in browser
Start-Process "http://172.16.1.4:5000"
```

---

## Still Not Working?

### Collect diagnostic information:

```powershell
# Run diagnostic
cd C:\Apps\APITester
.\diagnose.ps1 > diagnostic_output.txt

# Check Python version
python --version > python_info.txt

# Check service
Get-Service -Name "APITester" | Format-List * > service_info.txt

# Check logs
Get-Content C:\Apps\APITester\logs\service-error.log -Tail 100 > error_log.txt

# Check port
netstat -ano | findstr :5000 > port_info.txt
```

Send these files for support:
- diagnostic_output.txt
- python_info.txt
- service_info.txt
- error_log.txt
- port_info.txt

---

## Quick Reference Commands

```powershell
# Check status
Get-Service -Name "APITester"

# Start
Start-Service -Name "APITester"

# Stop
Stop-Service -Name "APITester"

# Restart
Restart-Service -Name "APITester"

# View logs (live)
Get-Content C:\Apps\APITester\logs\app.log -Tail 50 -Wait

# Test connection
Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing

# Manual start (for debugging)
cd C:\Apps\APITester
.\venv\Scripts\activate
python run_production.py
```

---

## Success Checklist

You'll know it's working when:

- [✓] Service status shows "Running"
- [✓] Port 5000 is listening: `netstat -ano | findstr :5000` shows output
- [✓] `http://localhost:5000` opens in browser on server
- [✓] `http://172.16.1.4:5000` opens from other computers
- [✓] No errors in logs
- [✓] Can create and run API tests

---

**Need more help? Run the diagnostic tool:**
```powershell
cd C:\Apps\APITester
.\diagnose.ps1
```

This will tell you exactly what's wrong!

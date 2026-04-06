# Quick Start - Deploy to Windows Server 172.16.1.4

**This guide will do EVERYTHING for you automatically!**

---

## Part 1: On Your Mac (5 minutes)

### Step 1: Package the Project

```bash
cd "/Users/Admin/Documents/AI/New API testing/API -AI Testing/deploy"
chmod +x package_for_deployment.sh
./package_for_deployment.sh
```

**Result:** You'll have a file called `api-tester-deployment.zip`

### Step 2: Copy to Windows Server

**Option A: USB Drive**
1. Copy `api-tester-deployment.zip` to a USB drive
2. Plug USB into Windows Server
3. Copy file to `C:\Temp\` on Windows Server

**Option B: Network Share**
1. Open Finder
2. Go → Connect to Server
3. Enter: `smb://172.16.1.4`
4. Username: `administrator`, Password: `Amman@2026`
5. Copy `api-tester-deployment.zip` to a shared folder

**Option C: Direct Copy (if SSH enabled)**
```bash
scp api-tester-deployment.zip administrator@172.16.1.4:C:/Temp/
```

---

## Part 2: On Windows Server (10 minutes)

### Step 1: Connect to Server

1. Open **Remote Desktop Connection**
2. Computer: `172.16.1.4`
3. Username: `administrator`
4. Password: `Amman@2026`
5. Click **Connect**

### Step 2: Extract the Package

1. Open **File Explorer**
2. Navigate to where you copied the ZIP file (e.g., `C:\Temp\`)
3. Right-click `api-tester-deployment.zip`
4. Select **Extract All...**
5. Extract to: `C:\Temp\api-tester-deployment`
6. Click **Extract**

### Step 3: Install Python (if not already installed)

1. Open **Edge Browser**
2. Go to: `https://www.python.org/downloads/windows/`
3. Download **Python 3.11.x Windows installer (64-bit)**
4. Run the installer
5. ✅ Check **"Add Python to PATH"**
6. ✅ Check **"Install for all users"**
7. Click **Install Now**
8. Wait for installation to complete
9. Click **Close**

### Step 4: Run the Automated Setup

1. Navigate to: `C:\Temp\api-tester-deployment\`
2. Right-click on **automated_setup.ps1**
3. Select **"Run with PowerShell"**
   - If it says "execution policy", type `Y` and press Enter

**OR** run from PowerShell as Administrator:

```powershell
cd C:\Temp\api-tester-deployment
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\automated_setup.ps1
```

**The script will automatically:**
- ✅ Create all directories
- ✅ Set up Python virtual environment
- ✅ Install all dependencies
- ✅ Create configuration files
- ✅ Configure Windows Firewall
- ✅ Install Windows Service
- ✅ Create maintenance scripts

**Wait 5-10 minutes** for the script to complete.

### Step 5: Copy Project Files

After the automated setup completes:

```powershell
# Copy all project files to the installation directory
xcopy /E /I /Y C:\Temp\api-tester-deployment\package\* C:\Apps\APITester\
```

### Step 6: Start the Service

```powershell
Restart-Service -Name "APITester"
```

Wait 10 seconds, then check status:

```powershell
Get-Service -Name "APITester"
```

**Status should show:** `Running`

### Step 7: Test Access

Open **Edge Browser** and go to:

```
http://localhost:5000
```

**You should see the API Testing Platform!**

---

## Part 3: Give Access to Your Team

### Team Access URL

Share this URL with your team:

```
http://172.16.1.4:5000
```

### Team Access Instructions

Send this to your team:

```
API Testing Platform Access

URL: http://172.16.1.4:5000

Features:
- Create and manage API tests
- Run automated validations
- Generate detailed reports
- Track test history

Browser: Use Chrome or Edge
No login required (currently)

For support, contact: [Your name/email]
```

---

## Common Commands

### Check Service Status
```powershell
Get-Service -Name "APITester"
```

### Start Service
```powershell
Start-Service -Name "APITester"
```

### Stop Service
```powershell
Stop-Service -Name "APITester"
```

### Restart Service
```powershell
Restart-Service -Name "APITester"
```

### View Logs
```powershell
Get-Content C:\Apps\APITester\logs\app.log -Tail 50 -Wait
```

### View Errors
```powershell
Get-Content C:\Apps\APITester\logs\service-error.log -Tail 50
```

### Easy Management (Use the helper script)
```powershell
cd C:\Apps\APITester
.\manage.ps1 status    # Check status
.\manage.ps1 start     # Start service
.\manage.ps1 stop      # Stop service
.\manage.ps1 restart   # Restart service
.\manage.ps1 logs      # View logs (live)
.\manage.ps1 errors    # View errors
```

---

## Troubleshooting

### Problem: Can't access from network

**Solution:**
```powershell
# Check if service is running
Get-Service -Name "APITester"

# Check firewall
Get-NetFirewallRule -DisplayName "API Tester*"

# Test locally first
Start-Process "http://localhost:5000"
```

### Problem: Service won't start

**Solution:**
```powershell
# Check error logs
Get-Content C:\Apps\APITester\logs\service-error.log -Tail 50

# Try running manually
cd C:\Apps\APITester
.\venv\Scripts\activate
python run_production.py

# Look for error messages
```

### Problem: Python not found

**Solution:**
```powershell
# Check if Python is installed
python --version

# If not found, add to PATH or reinstall Python
# Make sure "Add Python to PATH" was checked during installation
```

### Problem: Port already in use

**Solution:**
```powershell
# Check what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual number)
taskkill /F /PID <PID>

# Or change port in config
notepad C:\Apps\APITester\config.py
# Change PORT = 5000 to PORT = 8080
# Update firewall rule for new port
```

---

## Important Files & Locations

```
Installation: C:\Apps\APITester\
Config:       C:\Apps\APITester\config.py
Database:     C:\Apps\APITester\database.db
Logs:         C:\Apps\APITester\logs\
Reports:      C:\Apps\APITester\output\
```

---

## Complete Summary

**What You Did:**
1. ✅ Packaged project on Mac
2. ✅ Copied to Windows Server
3. ✅ Ran automated setup
4. ✅ Started the service

**What Got Installed:**
- ✅ Python virtual environment
- ✅ All Python dependencies
- ✅ SQLite database
- ✅ Windows Service (auto-starts on boot)
- ✅ Firewall rules
- ✅ Logging system
- ✅ Maintenance scripts

**Access URLs:**
- Local: http://localhost:5000
- Network: http://172.16.1.4:5000

**Service Name:** APITester

**That's it! You're done!** 🎉

---

## Need Help?

If something goes wrong:

1. Check service status: `Get-Service -Name "APITester"`
2. Check error logs: `C:\Apps\APITester\logs\service-error.log`
3. Try running manually:
   ```powershell
   cd C:\Apps\APITester
   .\venv\Scripts\activate
   python run_production.py
   ```
4. Look at the detailed guide: `WINDOWS_SERVER_DEPLOYMENT.md`

---

**Last Updated:** April 2026

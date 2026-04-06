# Windows Server Deployment Guide

**OpenSooq API Automation Testing Platform**

Complete guide to deploy the API Automation Testing Platform on Windows Server.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Install Python](#install-python)
3. [Install Git](#install-git)
4. [Clone the Repository](#clone-the-repository)
5. [Install Dependencies](#install-dependencies)
6. [Database Setup](#database-setup)
7. [Start the Application](#start-the-application)
8. [Access from Network](#access-from-network)
9. [Troubleshooting](#troubleshooting)
10. [Production Deployment](#production-deployment)

---

## 1. Prerequisites

### System Requirements

- **Operating System**: Windows Server 2016+ or Windows 10/11
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Disk Space**: 500MB
- **Network**: Internet connection for initial setup

### Required Software

- Python 3.9 or higher
- Git (for repository management)
- Web browser (Chrome, Edge, Firefox)

---

## 2. Install Python

### Step 1: Download Python

1. Open your web browser
2. Go to: **https://www.python.org/downloads/**
3. Click **"Download Python 3.12.x"** (latest version)
4. Wait for download to complete

### Step 2: Install Python

1. **Run the installer** (`python-3.12.x-amd64.exe`)
2. **IMPORTANT**: ✅ Check **"Add Python to PATH"** at the bottom
3. Click **"Install Now"**
4. Wait for installation to complete
5. Click **"Close"**

### Step 3: Verify Installation

Open **Command Prompt** (cmd) and run:

```cmd
python --version
```

You should see: `Python 3.12.x`

If you see an error:
- Restart Command Prompt
- If still not working, add Python to PATH manually

---

## 3. Install Git

### Step 1: Download Git

1. Go to: **https://git-scm.com/download/win**
2. Download will start automatically
3. Wait for `Git-x.x.x-64-bit.exe` to download

### Step 2: Install Git

1. Run the installer
2. Use default settings (click **"Next"** through all screens)
3. Click **"Install"**
4. Click **"Finish"**

### Step 3: Verify Installation

Open **Command Prompt** and run:

```cmd
git --version
```

You should see: `git version 2.x.x.windows.x`

---

## 4. Clone the Repository

### Option A: From GitHub/GitLab (Recommended)

If you've pushed the code to GitHub/GitLab:

```cmd
cd C:\
git clone https://github.com/YOUR-USERNAME/API-Testing.git
cd API-Testing
```

Replace `YOUR-USERNAME` with your actual GitHub username.

### Option B: Transfer Files Directly

If you don't have Git repository:

1. Create folder: `C:\API-Testing\`
2. Copy all project files to this folder
3. Open Command Prompt:

```cmd
cd C:\API-Testing
```

---

## 5. Install Dependencies

### Step 1: Open Command Prompt as Administrator

1. Press **Windows Key**
2. Type: `cmd`
3. Right-click **"Command Prompt"**
4. Select **"Run as administrator"**

### Step 2: Navigate to Project Folder

```cmd
cd C:\API-Testing
```

### Step 3: Install Required Packages

```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- SQLAlchemy (database)
- requests (HTTP client)
- pytest (testing framework)

Wait for installation to complete (2-3 minutes).

---

## 6. Database Setup

The application uses **SQLite** database (file-based, no installation needed).

### If You Have Existing Data (data.json)

Run the migration script to convert JSON to SQLite:

```cmd
python migrate_to_db.py
```

You should see:
```
✅ Migration completed successfully!
📁 Database file created: database.db
```

### If Starting Fresh

The database will be created automatically when you start the app.

---

## 7. Start the Application

### Step 1: Start the Server

```cmd
python main.py
```

You should see:

```
==================================================
AI Test Agent
==================================================
Starting server at http://localhost:5001
Press Ctrl+C to stop
==================================================
```

### Step 2: Open the Application

Open your web browser and go to:

```
http://localhost:5001
```

You should see the OpenSooq API Testing Platform dashboard!

---

## 8. Access from Network

To allow other computers to access the application:

### Step 1: Find Your Server IP Address

In Command Prompt:

```cmd
ipconfig
```

Look for **"IPv4 Address"** (e.g., `192.168.1.100`)

### Step 2: Configure Windows Firewall

1. Open **Windows Defender Firewall**
2. Click **"Advanced settings"**
3. Click **"Inbound Rules"**
4. Click **"New Rule..."**
5. Select **"Port"** → Next
6. Enter port: `5001` → Next
7. Select **"Allow the connection"** → Next
8. Check all profiles → Next
9. Name: `API Testing Platform` → Finish

### Step 3: Share the Link

Share this URL with your team:

```
http://YOUR-SERVER-IP:5001
```

Example: `http://192.168.1.100:5001`

**Note**: Users must be on the same network.

---

## 9. Troubleshooting

### Problem: "Python is not recognized"

**Solution:**

1. Reinstall Python
2. Make sure to check **"Add Python to PATH"**
3. Restart Command Prompt

### Problem: "Port 5001 is already in use"

**Solution:**

```cmd
netstat -ano | findstr :5001
taskkill /PID <PID_NUMBER> /F
```

Replace `<PID_NUMBER>` with the number from the output.

### Problem: "ModuleNotFoundError: No module named 'flask'"

**Solution:**

```cmd
pip install -r requirements.txt
```

### Problem: "Database is locked"

**Solution:**

1. Close all applications accessing the database
2. Delete `database.db`
3. Run migration again: `python migrate_to_db.py`

### Problem: "Cannot access from other computers"

**Solution:**

1. Check Windows Firewall (see Section 8.2)
2. Verify server IP address with `ipconfig`
3. Make sure both computers are on same network
4. Try: `http://SERVER-IP:5001` not `localhost`

### Problem: "Module import errors"

**Solution:**

```cmd
pip uninstall flask sqlalchemy requests pytest
pip install -r requirements.txt
```

---

## 10. Production Deployment

For production environment (24/7 operation):

### Option A: Run as Windows Service (Recommended)

Use **NSSM** (Non-Sucking Service Manager):

1. Download NSSM: https://nssm.cc/download
2. Extract to `C:\nssm\`
3. Open Command Prompt as Administrator:

```cmd
cd C:\nssm\win64
nssm install APITestingService
```

4. In the GUI:
   - **Path**: `C:\Python312\python.exe`
   - **Startup directory**: `C:\API-Testing`
   - **Arguments**: `main.py`
   - Click **"Install service"**

5. Start the service:

```cmd
nssm start APITestingService
```

The application will now:
- Start automatically on Windows boot
- Restart automatically if it crashes
- Run in the background

### Option B: Use Production WSGI Server

Install Waitress (Windows-compatible WSGI server):

```cmd
pip install waitress
```

Create `production.py`:

```python
from waitress import serve
from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting production server on port 5001...")
    serve(app, host='0.0.0.0', port=5001, threads=4)
```

Run:

```cmd
python production.py
```

### Option C: Use IIS (Advanced)

1. Install **wfastcgi**:

```cmd
pip install wfastcgi
wfastcgi-enable
```

2. Configure IIS to host the Flask application
3. Create `web.config` file (search for Flask + IIS guides)

---

## 📊 Quick Reference Commands

### Start Application

```cmd
cd C:\API-Testing
python main.py
```

### Stop Application

Press `Ctrl+C` in the Command Prompt window

### Restart Application

1. Stop (Ctrl+C)
2. Start again (`python main.py`)

### Check Status

Open browser: `http://localhost:5001`

### View Database

Use **DB Browser for SQLite**:
- Download: https://sqlitebrowser.org/
- Open `C:\API-Testing\database.db`

### Backup Database

```cmd
copy database.db database_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.db
```

### Update Code (if using Git)

```cmd
cd C:\API-Testing
git pull
pip install -r requirements.txt
```

Then restart the application.

---

## 🔐 Security Notes

### For Production Deployment:

1. **Change Secret Key**:
   - Edit `app/__init__.py`
   - Set a random secret key

2. **Disable Debug Mode**:
   - Edit `main.py`
   - Change `debug=True` to `debug=False`

3. **Use HTTPS**:
   - Set up SSL certificate
   - Use reverse proxy (IIS, nginx)

4. **Restrict Access**:
   - Configure Windows Firewall
   - Use VPN for remote access
   - Add authentication if needed

5. **Regular Backups**:
   - Backup `database.db` daily
   - Store backups in secure location

---

## 📁 Project Structure

```
C:\API-Testing\
├── main.py                  # Application entry point
├── database.db             # SQLite database file
├── data.json.backup        # JSON backup (if migrated)
├── migrate_to_db.py        # Migration script
├── requirements.txt        # Python dependencies
├── app/
│   ├── __init__.py
│   ├── routes.py          # API endpoints
│   └── templates/
│       └── index.html     # Web interface
├── backend/
│   ├── database.py        # Database models
│   ├── db_helpers.py      # Database operations
│   ├── utils.py           # Helper functions
│   ├── runner.py          # Test execution
│   └── rules.py           # Validation rules
└── output/                # Generated reports
    └── report_*.html
```

---

## 🆘 Getting Help

### Contact Information

- **Project Documentation**: `TEAM_DOCUMENTATION.md`
- **Technical Issues**: Check `TROUBLESHOOTING.md`
- **GitHub Issues**: Create an issue in the repository

### Useful Resources

- **Python Documentation**: https://docs.python.org/3/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/

---

## ✅ Post-Deployment Checklist

- [ ] Python installed and in PATH
- [ ] Git installed (if using repository)
- [ ] Project files cloned/copied to `C:\API-Testing`
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database migrated (if had existing data)
- [ ] Application starts without errors
- [ ] Can access at `http://localhost:5001`
- [ ] Windows Firewall configured (port 5001)
- [ ] Tested access from another computer
- [ ] Production server configured (if needed)
- [ ] Backup strategy in place
- [ ] Team members can access the platform

---

**Questions?** Refer to `TEAM_DOCUMENTATION.md` for platform usage guide.

**OpenSooq API Automation Platform** - Deployed on Windows Server 🚀

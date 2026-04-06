# 🔄 How to Update Windows Server from GitHub

Your code is now on GitHub! The UTF-8 fix has been pushed.

---

## 📋 On Windows Server - Pull the Update

### Step 1: Stop the server

In PowerShell where server is running, press **Ctrl+C**

---

### Step 2: Pull latest code from GitHub

```powershell
cd C:\Apps\APITester
git pull origin main
```

---

### Step 3: Restart the server

```powershell
.\venv\Scripts\python.exe main.py
```

---

## ✅ Test the fix

The "Unexpected token '<'" error should now be fixed!

Try running an API test - it should work properly.

---

## 🚀 Future Updates (Every Time You Make Changes)

### On Mac:
```bash
cd "/Users/Admin/Documents/AI/New API testing/API -AI Testing"
# Make your changes
git add .
git commit -m "Description of what you changed"
git push origin main
```

### On Windows Server:
```powershell
# Stop server (Ctrl+C)
cd C:\Apps\APITester
git pull origin main
.\venv\Scripts\python.exe main.py
```

---

## 📦 Optional: Create Auto-Update Script

Save this as `C:\Apps\update.ps1`:

```powershell
Write-Host "Updating API Testing Platform..." -ForegroundColor Yellow
cd C:\Apps\APITester
git pull origin main
Write-Host "Update complete! Restart the server." -ForegroundColor Green
```

Then just run: `C:\Apps\update.ps1` to update!

---

## ✅ Your Current Fix

The UTF-8 encoding fix has been applied and pushed to GitHub.

**On Windows Server, run:**
```powershell
cd C:\Apps\APITester
git pull origin main
```

Then restart the server and test!

---

**Repository:** Already connected to your GitHub repo
**Branch:** main
**Latest Commit:** Fix UTF-8 encoding for Windows + Add database migration + Update deployment scripts

#!/bin/bash
# ==============================================================================
# REMOTE DEPLOYMENT - Deploy to Windows Server from Mac
# ==============================================================================
# This script will connect to your Windows Server and deploy everything
# ==============================================================================

SERVER_IP="172.16.1.4"
USERNAME="administrator"
PASSWORD="Amman@2026"
DEPLOYMENT_ZIP="/Users/Admin/Documents/AI/New API testing/API -AI Testing/deploy/api-tester-deployment.zip"

echo "================================================================================"
echo "Remote Deployment to Windows Server"
echo "================================================================================"
echo ""
echo "Target Server: $SERVER_IP"
echo "Username: $USERNAME"
echo ""

# Check if deployment package exists
if [ ! -f "$DEPLOYMENT_ZIP" ]; then
    echo "✗ Deployment package not found: $DEPLOYMENT_ZIP"
    exit 1
fi

echo "✓ Deployment package found"
echo ""

# ==============================================================================
# Step 1: Test connection
# ==============================================================================
echo "[Step 1/5] Testing connection to Windows Server..."

if ping -c 2 "$SERVER_IP" &> /dev/null; then
    echo "  ✓ Server is reachable"
else
    echo "  ✗ Cannot reach server at $SERVER_IP"
    echo "  Please check network connection"
    exit 1
fi

# ==============================================================================
# Step 2: Check if SMB is accessible
# ==============================================================================
echo ""
echo "[Step 2/5] Checking file sharing access..."

# Try to access Windows Admin share
if mount | grep -q "$SERVER_IP"; then
    echo "  ✓ Already connected to server"
else
    echo "  Attempting to connect to server file share..."

    # Create mount point
    MOUNT_POINT="/tmp/windows_server_$$"
    mkdir -p "$MOUNT_POINT"

    # Try to mount
    if mount -t smbfs "//${USERNAME}:${PASSWORD}@${SERVER_IP}/C$" "$MOUNT_POINT" 2>/dev/null; then
        echo "  ✓ Connected to server file share"
        SERVER_MOUNTED=true
    else
        echo "  ⚠ Cannot connect via file sharing"
        echo "  Will try alternative method..."
        SERVER_MOUNTED=false
        rmdir "$MOUNT_POINT" 2>/dev/null
    fi
fi

# ==============================================================================
# Step 3: Copy deployment package
# ==============================================================================
echo ""
echo "[Step 3/5] Copying deployment package to server..."

if [ "$SERVER_MOUNTED" = true ]; then
    # Copy via SMB
    echo "  Copying via file share..."
    mkdir -p "$MOUNT_POINT/Temp"
    cp "$DEPLOYMENT_ZIP" "$MOUNT_POINT/Temp/api-tester-deployment.zip"

    if [ $? -eq 0 ]; then
        echo "  ✓ Package copied successfully"
    else
        echo "  ✗ Failed to copy package"
        umount "$MOUNT_POINT" 2>/dev/null
        rmdir "$MOUNT_POINT" 2>/dev/null
        exit 1
    fi
else
    # Try SCP (if SSH is enabled)
    echo "  Trying to copy via SCP..."

    if command -v sshpass &> /dev/null; then
        sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$DEPLOYMENT_ZIP" "${USERNAME}@${SERVER_IP}:C:/Temp/api-tester-deployment.zip"

        if [ $? -eq 0 ]; then
            echo "  ✓ Package copied via SCP"
        else
            echo "  ✗ Failed to copy via SCP"
            echo ""
            echo "  Please copy the file manually:"
            echo "  File: $DEPLOYMENT_ZIP"
            echo "  Destination: \\\\${SERVER_IP}\\C$\\Temp\\"
            exit 1
        fi
    else
        echo "  ⚠ sshpass not installed"
        echo ""
        echo "  MANUAL STEP REQUIRED:"
        echo "  1. Copy this file to the server:"
        echo "     $DEPLOYMENT_ZIP"
        echo "  2. Destination: \\\\${SERVER_IP}\\C$\\Temp\\"
        echo ""
        read -p "  Press Enter after copying the file manually..."
    fi
fi

# ==============================================================================
# Step 4: Extract and deploy
# ==============================================================================
echo ""
echo "[Step 4/5] Extracting and deploying on server..."

if [ "$SERVER_MOUNTED" = true ]; then
    echo "  Extracting package..."

    # Create extraction directory
    mkdir -p "$MOUNT_POINT/Temp/api-tester-deployment"

    # Extract using unzip
    cd "$MOUNT_POINT/Temp"
    unzip -q "api-tester-deployment.zip" -d "api-tester-deployment"

    if [ $? -eq 0 ]; then
        echo "  ✓ Package extracted"
    else
        echo "  ✗ Failed to extract package"
        umount "$MOUNT_POINT" 2>/dev/null
        rmdir "$MOUNT_POINT" 2>/dev/null
        exit 1
    fi

    echo "  ✓ Files ready on server"
fi

# ==============================================================================
# Step 5: Run deployment script remotely
# ==============================================================================
echo ""
echo "[Step 5/5] Running deployment script on server..."

# Create PowerShell script to run remotely
REMOTE_SCRIPT="
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
cd C:\\Temp\\api-tester-deployment
.\\COMPLETE_AUTO_DEPLOY.ps1
"

if [ "$SERVER_MOUNTED" = true ]; then
    # Save script to server
    echo "$REMOTE_SCRIPT" > "$MOUNT_POINT/Temp/deploy_now.ps1"

    echo "  Script ready on server"
    echo ""
    echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  FINAL STEP - Run this on Windows Server:"
    echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  1. Connect to Windows Server (Remote Desktop)"
    echo "     Server: $SERVER_IP"
    echo "     User: $USERNAME"
    echo ""
    echo "  2. Open PowerShell as Administrator"
    echo ""
    echo "  3. Run this command:"
    echo "     C:\\Temp\\deploy_now.ps1"
    echo ""
    echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Cleanup
    sleep 2
    umount "$MOUNT_POINT" 2>/dev/null
    rmdir "$MOUNT_POINT" 2>/dev/null
else
    echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  FINAL STEP - Run on Windows Server:"
    echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  1. Connect via Remote Desktop to: $SERVER_IP"
    echo "  2. Open PowerShell as Administrator"
    echo "  3. Run these commands:"
    echo ""
    echo "     cd C:\\Temp\\api-tester-deployment"
    echo "     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"
    echo "     .\\COMPLETE_AUTO_DEPLOY.ps1"
    echo ""
    echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi

echo ""
echo "================================================================================"
echo "Remote deployment preparation complete!"
echo "================================================================================"
echo ""
echo "After running the deployment script, your team can access:"
echo "  http://${SERVER_IP}:5000"
echo ""
echo "================================================================================"

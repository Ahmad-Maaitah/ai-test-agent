#!/bin/bash
# ==============================================================================
# Package API Testing Platform for Windows Server Deployment
# ==============================================================================

echo "================================================================================"
echo "Packaging API Testing Platform for Deployment"
echo "================================================================================"
echo ""

# Set project directory
PROJECT_DIR="/Users/Admin/Documents/AI/New API testing/API -AI Testing"
DEPLOY_DIR="$PROJECT_DIR/deploy"
PACKAGE_NAME="api-tester-deployment"

cd "$PROJECT_DIR"

echo "[1/4] Cleaning up unnecessary files..."
# Remove cache and temporary files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type f -name ".DS_Store" -delete 2>/dev/null

echo "  ✓ Cleanup complete"

echo ""
echo "[2/4] Creating deployment package..."

# Create deployment package
mkdir -p "$DEPLOY_DIR/package"

# Copy application files
rsync -av --exclude='venv' \
         --exclude='__pycache__' \
         --exclude='.git' \
         --exclude='*.pyc' \
         --exclude='.DS_Store' \
         --exclude='output/*' \
         --exclude='*.log' \
         --exclude='deploy/package' \
         --exclude='database.db' \
         "$PROJECT_DIR/" "$DEPLOY_DIR/package/"

echo "  ✓ Files copied to package directory"

echo ""
echo "[3/4] Creating ZIP archive..."

cd "$DEPLOY_DIR"
zip -rq "$PACKAGE_NAME.zip" package/ automated_setup.ps1

echo "  ✓ ZIP archive created: $DEPLOY_DIR/$PACKAGE_NAME.zip"

echo ""
echo "[4/4] Package information..."

PACKAGE_SIZE=$(du -h "$DEPLOY_DIR/$PACKAGE_NAME.zip" | cut -f1)
echo "  Package size: $PACKAGE_SIZE"
echo "  Package location: $DEPLOY_DIR/$PACKAGE_NAME.zip"

echo ""
echo "================================================================================"
echo "Packaging Complete!"
echo "================================================================================"
echo ""
echo "Next steps:"
echo "1. Copy $PACKAGE_NAME.zip to your Windows Server"
echo "2. Extract the ZIP file on Windows Server"
echo "3. Run automated_setup.ps1 as Administrator"
echo ""
echo "Transfer methods:"
echo "  - USB drive"
echo "  - Shared network folder"
echo "  - SCP: scp $DEPLOY_DIR/$PACKAGE_NAME.zip administrator@172.16.1.4:C:/Temp/"
echo ""
echo "================================================================================"
echo ""

"""
Production server startup using Waitress (Windows-compatible)
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import init_db
from backend.db_helpers import initialize_protected_variables

# Initialize database
db_path = os.path.join(os.path.dirname(__file__), 'database.db')
if not os.path.exists(db_path):
    print("[*] Initializing database...")
    init_db()
    print("[+] Database initialized")
else:
    init_db()

# Initialize protected variables
print("[*] Initializing protected variables...")
initialize_protected_variables()
print("[+] Protected variables ready")

# Import app
from app import create_app
app = create_app()

print("=" * 50)
print("AI Test Agent - Production Server")
print("=" * 50)
print("Starting server at http://localhost:5001")
print("Press Ctrl+C to stop")
print("=" * 50)

# Use waitress for production
try:
    from waitress import serve
    print("[*] Using Waitress production server...")
    serve(app, host='0.0.0.0', port=5001, threads=6)
except ImportError:
    print("[!] Waitress not installed, using Flask dev server...")
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False, threaded=True)

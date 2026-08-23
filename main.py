"""
AI Test Agent - Entry Point

Run this file to start the Flask application.
"""

import os
import sys

# Logs echo request bodies in any language. On a console using a legacy code
# page an unencodable character raises UnicodeEncodeError mid-request, which
# aborts the API run instead of just the log line.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, 'reconfigure'):
        stream.reconfigure(encoding='utf-8', errors='replace')

from app import create_app
from backend.database import init_db
from backend.db_helpers import initialize_protected_variables, repair_folder_paths


# Initialize database
db_path = os.path.join(os.path.dirname(__file__), 'database.db')
if not os.path.exists(db_path):
    print("[*] Initializing database...")
    init_db()
    print("[+] Database initialized")
else:
    # Ensure database schema is up to date
    init_db()

# Initialize protected variables for dynamic text generation
print("[*] Initializing protected variables...")
initialize_protected_variables()
print("[+] Protected variables ready")

repaired_folders = repair_folder_paths()
if repaired_folders:
    print(f"[+] Repaired folder paths for {repaired_folders} section(s)")

app = create_app()


if __name__ == '__main__':
    print("=" * 50)
    print("AI Test Agent")
    print("=" * 50)
    print("Starting server at http://localhost:5001")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False, threaded=True)

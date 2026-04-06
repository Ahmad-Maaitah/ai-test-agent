"""
AI Test Agent - Entry Point

Run this file to start the Flask application.
"""

from app import create_app
from backend.database import init_db
import os


# Initialize database
db_path = os.path.join(os.path.dirname(__file__), 'database.db')
if not os.path.exists(db_path):
    print("📦 Initializing database...")
    init_db()
    print("✅ Database initialized")
else:
    # Ensure database schema is up to date
    init_db()

app = create_app()


if __name__ == '__main__':
    print("=" * 50)
    print("AI Test Agent")
    print("=" * 50)
    print("Starting server at http://localhost:5001")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5001, debug=True)

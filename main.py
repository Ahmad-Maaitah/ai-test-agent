"""
AI Test Agent - Entry Point

Run this file to start the Flask application.
"""

from app import create_app


app = create_app()


if __name__ == '__main__':
    print("=" * 50)
    print("AI Test Agent")
    print("=" * 50)
    print("Starting server at http://localhost:5001")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5001, debug=True)

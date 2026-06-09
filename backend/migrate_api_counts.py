"""
Database migration: Add apis_passed and apis_failed columns to reports table.
Run this once after updating the code.
"""

import sqlite3
import os


def migrate():
    """Add apis_passed and apis_failed columns to reports table."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database.db')

    if not os.path.exists(db_path):
        print("[!] Database not found. Will be created with new schema on first run.")
        return

    print("[*] Migrating database to add API-level counts...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(reports)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'apis_passed' in columns and 'apis_failed' in columns:
            print("[OK] Columns already exist - skipping migration")
            return

        # Add new columns
        if 'apis_passed' not in columns:
            print("  [+] Adding apis_passed column...")
            cursor.execute("ALTER TABLE reports ADD COLUMN apis_passed INTEGER DEFAULT 0")

        if 'apis_failed' not in columns:
            print("  [+] Adding apis_failed column...")
            cursor.execute("ALTER TABLE reports ADD COLUMN apis_failed INTEGER DEFAULT 0")

        conn.commit()
        print("[OK] Migration completed successfully!")

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == '__main__':
    migrate()

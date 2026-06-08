"""
Database migration script to add folder support to existing sections.

This script:
1. Adds new columns to sections table (parent_id, is_folder, path, depth)
2. Migrates existing sections to root-level folders
3. Creates indexes for performance
"""

import sqlite3
import os


def get_database_path():
    """Get path to database file."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'database.db')


def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    return column_name in columns


def migrate_to_folder_structure():
    """Migrate existing database to support folder hierarchy."""
    db_path = get_database_path()

    if not os.path.exists(db_path):
        print("⚠️  Database not found. Creating new database with folder support...")
        from backend.database import init_db
        init_db()
        print("✅ New database created with folder support")
        return

    print("🔄 Migrating database to add folder support...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if migration is needed
        if column_exists(cursor, 'sections', 'parent_id'):
            print("✅ Database already has folder support - skipping migration")
            return

        print("  📝 Adding new columns...")

        # Add parent_id column
        if not column_exists(cursor, 'sections', 'parent_id'):
            cursor.execute("ALTER TABLE sections ADD COLUMN parent_id VARCHAR(50)")
            print("    ✓ Added parent_id column")

        # Add is_folder column
        if not column_exists(cursor, 'sections', 'is_folder'):
            cursor.execute("ALTER TABLE sections ADD COLUMN is_folder BOOLEAN DEFAULT 1")
            print("    ✓ Added is_folder column")

        # Add path column
        if not column_exists(cursor, 'sections', 'path'):
            cursor.execute("ALTER TABLE sections ADD COLUMN path TEXT")
            print("    ✓ Added path column")

        # Add depth column
        if not column_exists(cursor, 'sections', 'depth'):
            cursor.execute("ALTER TABLE sections ADD COLUMN depth INTEGER DEFAULT 0")
            print("    ✓ Added depth column")

        print("  📝 Migrating existing sections to root-level folders...")

        # Update existing sections: set as root folders
        cursor.execute("""
            UPDATE sections
            SET
                is_folder = 1,
                depth = 0,
                path = '/' || id
            WHERE parent_id IS NULL
        """)

        rows_updated = cursor.rowcount
        print(f"    ✓ Migrated {rows_updated} sections to root-level folders")

        print("  📝 Creating indexes for performance...")

        # Create indexes
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sections_parent_id ON sections(parent_id)")
            print("    ✓ Created index on parent_id")
        except:
            pass

        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sections_path ON sections(path)")
            print("    ✓ Created index on path")
        except:
            pass

        # Add folder_id and folder_path to reports table if needed
        print("  📝 Updating reports table...")

        if not column_exists(cursor, 'reports', 'folder_id'):
            cursor.execute("ALTER TABLE reports ADD COLUMN folder_id VARCHAR(50)")
            print("    ✓ Added folder_id to reports")

        if not column_exists(cursor, 'reports', 'folder_path'):
            cursor.execute("ALTER TABLE reports ADD COLUMN folder_path TEXT")
            print("    ✓ Added folder_path to reports")

        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reports_folder_id ON reports(folder_id)")
            print("    ✓ Created index on reports.folder_id")
        except:
            pass

        # Commit changes
        conn.commit()
        print("✅ Migration completed successfully!")
        print(f"   Database: {db_path}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    migrate_to_folder_structure()

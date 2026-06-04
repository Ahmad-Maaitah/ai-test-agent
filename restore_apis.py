#!/usr/bin/env python3
"""
Restore APIs from database.db to data.json
Run this script to migrate all APIs from SQLite database to JSON file
"""

import sqlite3
import json
import os
import sys

def main():
    print("=" * 60)
    print("RESTORE APIs FROM DATABASE")
    print("=" * 60)
    print()

    # Check if files exist
    if not os.path.exists('database.db'):
        print("❌ ERROR: database.db not found!")
        print("   Make sure you're running this from the project directory.")
        return 1

    if not os.path.exists('data.json'):
        print("❌ ERROR: data.json not found!")
        return 1

    # Load current data.json
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    current_api_count = len(data.get('apis', []))
    print(f"Current data.json: {current_api_count} APIs")

    # Connect to database
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Check if apis table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='apis'")
    if not cursor.fetchone():
        print("❌ ERROR: No 'apis' table found in database.db")
        conn.close()
        return 1

    # Get all APIs
    cursor.execute("""
        SELECT id, name, section_id, curl, custom_rules, headers, body, method, url, created_at
        FROM apis
        ORDER BY created_at
    """)
    rows = cursor.fetchall()

    print(f"Found {len(rows)} APIs in database.db")
    print()

    if len(rows) == 0:
        print("⚠️  No APIs found in database.db - nothing to restore")
        conn.close()
        return 0

    # Ask for confirmation if data.json already has APIs
    if current_api_count > 0:
        print(f"⚠️  WARNING: data.json already has {current_api_count} APIs")
        response = input("Do you want to REPLACE them? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("❌ Cancelled by user")
            conn.close()
            return 0

    print()
    print("🔄 Migrating APIs...")
    print()

    # Convert to API objects
    apis = []
    for row in rows:
        api_id, name, section_id, curl, custom_rules_json, headers_json, body, method, url, created_at = row

        api = {
            'id': api_id,
            'name': name,
            'section_id': section_id,
            'curl': curl or '',
            'created_at': created_at
        }

        # Parse JSON fields
        if custom_rules_json:
            try:
                api['rules'] = json.loads(custom_rules_json)
            except:
                api['rules'] = []
        else:
            api['rules'] = []

        if headers_json:
            try:
                api['headers'] = json.loads(headers_json)
            except:
                api['headers'] = {}
        else:
            api['headers'] = {}

        if body:
            api['body'] = body
        if method:
            api['method'] = method
        if url:
            api['url'] = url

        apis.append(api)
        rules_count = len(api.get('rules', []))
        print(f"  ✅ {name} ({rules_count} rules)")

    # Update data.json
    data['apis'] = apis

    # Backup old data.json
    if current_api_count > 0:
        backup_file = 'data.json.backup'
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print()
        print(f"💾 Old data.json backed up to: {backup_file}")

    # Save new data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print()
    print("=" * 60)
    print(f"✅ SUCCESS! Restored {len(apis)} APIs to data.json")
    print(f"   Sections: {len(data.get('sections', []))}")
    print(f"   Variables: {len(data.get('variables', []))}")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Restart Flask server (Ctrl+C then 'python main.py')")
    print("2. Refresh browser to see all APIs")
    print()

    conn.close()
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

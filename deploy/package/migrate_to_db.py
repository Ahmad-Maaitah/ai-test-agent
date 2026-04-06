"""Migration script to convert data.json to SQLite database."""

import json
import os
from datetime import datetime
from backend.database import init_db, get_session, Section, API, Rule, Variable, Report, TestResult


def load_json_data():
    """Load existing data.json file."""
    data_file = os.path.join(os.path.dirname(__file__), 'data.json')

    if not os.path.exists(data_file):
        print(f"❌ data.json not found at: {data_file}")
        return None

    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded data.json successfully")
        return data
    except Exception as e:
        print(f"❌ Error loading data.json: {e}")
        return None


def migrate_sections(session, sections_data):
    """Migrate sections from JSON to database."""
    print(f"\n📂 Migrating {len(sections_data)} sections...")

    for idx, section_data in enumerate(sections_data):
        section = Section(
            id=section_data.get('id', f'section-{idx}'),
            name=section_data.get('name', 'Unnamed Section'),
            description=section_data.get('description', ''),
            order=section_data.get('order', idx)
        )
        session.add(section)
        print(f"  ✓ {section.name}")

    session.commit()
    print(f"✅ Migrated {len(sections_data)} sections")


def migrate_apis(session, sections_data):
    """Migrate APIs and their rules from JSON to database."""
    total_apis = 0
    total_rules = 0

    print(f"\n🔧 Migrating APIs and rules...")

    for section_data in sections_data:
        section_id = section_data.get('id')
        apis_data = section_data.get('apis', [])

        for idx, api_data in enumerate(apis_data):
            # Create API
            api = API(
                id=api_data.get('id', f'api-{section_id}-{idx}'),
                name=api_data.get('name', 'Unnamed API'),
                section_id=section_id,
                curl=api_data.get('curl'),
                method=api_data.get('method', 'GET'),
                url=api_data.get('url', ''),
                headers=api_data.get('headers', {}),
                body=api_data.get('data'),
                verify_ssl=api_data.get('verify_ssl', True),
                custom_rules=api_data.get('customRules', []),
                extract_rules=api_data.get('extractRules', []),
                last_status=api_data.get('lastStatus'),
                last_result=api_data.get('lastResult'),
                order=api_data.get('order', idx)
            )
            session.add(api)
            total_apis += 1

            # Create Rules for this API
            rules_data = api_data.get('rules', [])
            for rule_data in rules_data:
                rule = Rule(
                    api_id=api.id,
                    rule_type=rule_data.get('type', 'status_code'),
                    field_path=rule_data.get('field'),
                    expected_value=str(rule_data.get('expected')) if rule_data.get('expected') is not None else None,
                    operator=rule_data.get('operator'),
                    config=rule_data.get('config', {})
                )
                session.add(rule)
                total_rules += 1

            print(f"  ✓ {api.name} ({len(rules_data)} rules)")

    session.commit()
    print(f"✅ Migrated {total_apis} APIs with {total_rules} rules")


def migrate_variables(session, variables_data):
    """Migrate variables from JSON to database."""
    if not variables_data:
        print(f"\n📝 No variables to migrate")
        return

    print(f"\n📝 Migrating {len(variables_data)} variables...")

    for var_data in variables_data:
        source = var_data.get('source') if var_data.get('source') else {}

        variable = Variable(
            id=var_data.get('id', f'var-{var_data.get("name")}'),
            name=var_data.get('name'),
            value=str(var_data.get('value', '')),
            type=var_data.get('type', 'string'),
            description=var_data.get('description', ''),
            source_api_id=source.get('apiId') if source else None,
            source_field_path=source.get('fieldPath') if source else None
        )
        session.add(variable)
        print(f"  ✓ {variable.name}")

    session.commit()
    print(f"✅ Migrated {len(variables_data)} variables")


def migrate_reports(session, reports_data):
    """Migrate reports from JSON to database."""
    if not reports_data:
        print(f"\n📊 No reports to migrate")
        return

    print(f"\n📊 Migrating {len(reports_data)} reports...")

    for report_data in reports_data:
        report = Report(
            id=report_data.get('id', f'report-{datetime.now().timestamp()}'),
            module=report_data.get('module'),
            total_apis=report_data.get('total', 0),
            passed=report_data.get('passed', 0),
            failed=report_data.get('failed', 0),
            total_duration=report_data.get('duration', 0.0),
            html_path=report_data.get('htmlPath'),
            json_path=report_data.get('jsonPath'),
            status=report_data.get('status', 'completed'),
            error=report_data.get('error')
        )

        # Parse timestamp
        if 'timestamp' in report_data:
            try:
                report.created_at = datetime.fromisoformat(report_data['timestamp'].replace('Z', '+00:00'))
            except:
                pass

        session.add(report)
        print(f"  ✓ {report.id}")

    session.commit()
    print(f"✅ Migrated {len(reports_data)} reports")


def main():
    """Main migration function."""
    print("=" * 60)
    print("🔄 Starting Migration: data.json → SQLite Database")
    print("=" * 60)

    # Load JSON data
    data = load_json_data()
    if not data:
        print("❌ Migration aborted: Could not load data.json")
        return False

    # Initialize database
    print("\n🗄️  Initializing SQLite database...")
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

    # Get database session
    session = get_session()

    try:
        # Migrate data
        sections_data = data.get('sections', [])
        variables_data = data.get('variables', [])
        reports_data = data.get('reports', [])

        if sections_data:
            migrate_sections(session, sections_data)
            migrate_apis(session, sections_data)

        if variables_data:
            migrate_variables(session, variables_data)

        if reports_data:
            migrate_reports(session, reports_data)

        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print(f"\n📁 Database file created: database.db")
        print(f"📋 Backup your data.json file before deleting it")
        print(f"🚀 You can now start the application with: python3 main.py")

        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        return False

    finally:
        session.close()


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

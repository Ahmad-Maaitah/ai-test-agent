"""Database helper functions to replace JSON file operations."""

from typing import List, Dict, Optional, Any
from sqlalchemy.orm import joinedload
from backend.database import (
    get_session, close_session,
    Section, API, Rule, Variable, Report, TestResult
)
from datetime import datetime
import json


# =============================================================================
# Section Operations
# =============================================================================

def get_all_sections() -> List[Dict]:
    """Get all sections with their APIs."""
    session = get_session()
    try:
        sections = session.query(Section).order_by(Section.order).all()
        result = []

        for section in sections:
            apis = session.query(API).filter_by(section_id=section.id).order_by(API.order).all()

            section_dict = {
                'id': section.id,
                'name': section.name,
                'description': section.description,
                'order': section.order,
                'apis': []
            }

            for api in apis:
                rules = session.query(Rule).filter_by(api_id=api.id).all()

                api_dict = {
                    'id': api.id,
                    'name': api.name,
                    'curl': api.curl,
                    'method': api.method,
                    'url': api.url,
                    'headers': api.headers if api.headers else {},
                    'data': api.body,
                    'verify_ssl': api.verify_ssl,
                    'customRules': api.custom_rules if api.custom_rules else [],
                    'extractRules': api.extract_rules if api.extract_rules else [],
                    'lastStatus': api.last_status,
                    'lastResult': api.last_result,
                    'order': api.order,
                    'rules': []
                }

                for rule in rules:
                    rule_dict = {
                        'type': rule.rule_type,
                        'field': rule.field_path,
                        'expected': rule.expected_value,
                        'operator': rule.operator,
                        'config': rule.config if rule.config else {}
                    }
                    api_dict['rules'].append(rule_dict)

                section_dict['apis'].append(api_dict)

            result.append(section_dict)

        return result
    finally:
        close_session(session)


def create_section(name: str, description: str = '') -> Dict:
    """Create a new section."""
    session = get_session()
    try:
        # Get max order
        max_order = session.query(Section).count()

        section = Section(
            id=f'section-{datetime.now().timestamp()}',
            name=name,
            description=description,
            order=max_order
        )
        session.add(section)
        session.commit()

        return {
            'id': section.id,
            'name': section.name,
            'description': section.description,
            'order': section.order
        }
    finally:
        close_session(session)


def update_section(section_id: str, name: str = None, description: str = None) -> bool:
    """Update a section."""
    session = get_session()
    try:
        section = session.query(Section).filter_by(id=section_id).first()
        if not section:
            return False

        if name is not None:
            section.name = name
        if description is not None:
            section.description = description

        session.commit()
        return True
    finally:
        close_session(session)


def delete_section(section_id: str) -> bool:
    """Delete a section and all its APIs."""
    session = get_session()
    try:
        section = session.query(Section).filter_by(id=section_id).first()
        if not section:
            return False

        session.delete(section)
        session.commit()
        return True
    finally:
        close_session(session)


# =============================================================================
# API Operations
# =============================================================================

def get_api_by_id(api_id: str) -> Optional[Dict]:
    """Get a single API by ID."""
    session = get_session()
    try:
        api = session.query(API).filter_by(id=api_id).first()
        if not api:
            return None

        rules = session.query(Rule).filter_by(api_id=api.id).all()

        return {
            'id': api.id,
            'name': api.name,
            'section_id': api.section_id,
            'curl': api.curl,
            'method': api.method,
            'url': api.url,
            'headers': api.headers if api.headers else {},
            'data': api.body,
            'verify_ssl': api.verify_ssl,
            'customRules': api.custom_rules if api.custom_rules else [],
            'extractRules': api.extract_rules if api.extract_rules else [],
            'lastStatus': api.last_status,
            'lastResult': api.last_result,
            'order': api.order,
            'rules': [
                {
                    'type': r.rule_type,
                    'field': r.field_path,
                    'expected': r.expected_value,
                    'operator': r.operator,
                    'config': r.config if r.config else {}
                }
                for r in rules
            ]
        }
    finally:
        close_session(session)


def create_api(section_id: str, api_data: Dict) -> Dict:
    """Create a new API."""
    session = get_session()
    try:
        # Get max order for this section (count gives us the next order number, starting from 1)
        max_order = session.query(API).filter_by(section_id=section_id).count()

        api = API(
            id=api_data.get('id', f'api-{datetime.now().timestamp()}'),
            name=api_data.get('name'),
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
            order=max_order + 1  # Start from 1, not 0
        )
        session.add(api)
        session.flush()  # Get the API ID

        # Add rules
        for rule_data in api_data.get('rules', []):
            rule = Rule(
                api_id=api.id,
                rule_type=rule_data.get('type'),
                field_path=rule_data.get('field'),
                expected_value=str(rule_data.get('expected')) if rule_data.get('expected') is not None else None,
                operator=rule_data.get('operator'),
                config=rule_data.get('config', {})
            )
            session.add(rule)

        session.commit()

        return {'id': api.id, 'name': api.name}
    finally:
        close_session(session)


def normalize_api_orders(section_id: str, session=None) -> None:
    """Normalize API orders in a section to be sequential (1, 2, 3, ...).

    Args:
        section_id: The section ID to normalize
        session: Optional existing session. If None, creates new session.
    """
    should_close = False
    if session is None:
        session = get_session()
        should_close = True

    try:
        # Get all APIs in section ordered by current order
        apis = session.query(API).filter_by(section_id=section_id).order_by(API.order).all()

        # Renumber sequentially starting from 1
        for idx, api in enumerate(apis, start=1):
            api.order = idx

        if should_close:
            session.commit()
    finally:
        if should_close:
            close_session(session)


def update_api(api_id: str, api_data: Dict) -> bool:
    """Update an existing API."""
    session = get_session()
    try:
        api = session.query(API).filter_by(id=api_id).first()
        if not api:
            return False

        # Store section_id for normalization
        section_id = api.section_id
        order_changed = False

        # Update API fields
        api.name = api_data.get('name', api.name)
        api.curl = api_data.get('curl', api.curl)
        api.method = api_data.get('method', api.method)
        api.url = api_data.get('url', api.url)
        api.headers = api_data.get('headers', api.headers)
        api.body = api_data.get('data', api.body)
        api.verify_ssl = api_data.get('verify_ssl', api.verify_ssl)
        api.custom_rules = api_data.get('customRules', api.custom_rules)
        api.extract_rules = api_data.get('extractRules', api.extract_rules)

        # Handle order update
        if 'order' in api_data:
            new_order = int(api_data['order'])
            if api.order != new_order:
                api.order = new_order
                order_changed = True

        # Update last status and result if provided
        if 'lastStatus' in api_data:
            api.last_status = api_data['lastStatus']
        if 'lastResult' in api_data:
            api.last_result = api_data['lastResult']
        api.updated_at = datetime.utcnow()

        # Delete old rules
        session.query(Rule).filter_by(api_id=api_id).delete()

        # Add new rules
        for rule_data in api_data.get('rules', []):
            rule = Rule(
                api_id=api.id,
                rule_type=rule_data.get('type'),
                field_path=rule_data.get('field'),
                expected_value=str(rule_data.get('expected')) if rule_data.get('expected') is not None else None,
                operator=rule_data.get('operator'),
                config=rule_data.get('config', {})
            )
            session.add(rule)

        session.commit()

        # If order changed, normalize all orders in the section
        if order_changed:
            normalize_api_orders(section_id, session)
            session.commit()

        return True
    finally:
        close_session(session)


def delete_api(api_id: str) -> bool:
    """Delete an API and its rules."""
    session = get_session()
    try:
        api = session.query(API).filter_by(id=api_id).first()
        if not api:
            return False

        section_id = api.section_id
        session.delete(api)
        session.commit()

        # Normalize orders in the section after deletion
        normalize_api_orders(section_id, session)
        session.commit()
        return True
    finally:
        close_session(session)


# =============================================================================
# Variable Operations
# =============================================================================

def get_all_variables() -> List[Dict]:
    """Get all variables."""
    session = get_session()
    try:
        variables = session.query(Variable).all()
        return [
            {
                'id': v.id,
                'name': v.name,
                'value': v.value,
                'type': v.type,
                'description': v.description,
                'source': {
                    'apiId': v.source_api_id,
                    'fieldPath': v.source_field_path
                } if v.source_api_id or v.source_field_path else None,
                'createdAt': v.created_at.isoformat() if v.created_at else None
            }
            for v in variables
        ]
    finally:
        close_session(session)


def create_variable(var_data: Dict) -> Dict:
    """Create a new variable."""
    session = get_session()
    try:
        source = var_data.get('source') if var_data.get('source') else {}

        variable = Variable(
            id=var_data.get('id', f'var-{datetime.now().timestamp()}'),
            name=var_data['name'],
            value=str(var_data.get('value', '')),
            type=var_data.get('type', 'string'),
            description=var_data.get('description', ''),
            source_api_id=source.get('apiId') if source else None,
            source_field_path=source.get('fieldPath') if source else None
        )
        session.add(variable)
        session.commit()

        return {
            'id': variable.id,
            'name': variable.name,
            'value': variable.value,
            'type': variable.type
        }
    finally:
        close_session(session)


def update_variable(var_id: str, var_data: Dict) -> bool:
    """Update a variable."""
    session = get_session()
    try:
        variable = session.query(Variable).filter_by(id=var_id).first()
        if not variable:
            return False

        variable.name = var_data.get('name', variable.name)
        variable.value = str(var_data.get('value', variable.value))
        variable.type = var_data.get('type', variable.type)
        variable.description = var_data.get('description', variable.description)
        variable.updated_at = datetime.utcnow()

        source = var_data.get('source')
        if source:
            variable.source_api_id = source.get('apiId')
            variable.source_field_path = source.get('fieldPath')

        session.commit()
        return True
    finally:
        close_session(session)


def delete_variable(var_id: str) -> bool:
    """Delete a variable. Protected variables cannot be deleted."""
    # List of protected variable names that cannot be deleted
    PROTECTED_VARIABLES = ['postTitle', 'postDescription']

    session = get_session()
    try:
        variable = session.query(Variable).filter_by(id=var_id).first()
        if not variable:
            return False

        # Check if this is a protected variable
        if variable.name in PROTECTED_VARIABLES:
            print(f"⚠️  Cannot delete protected variable: {variable.name}")
            return False

        session.delete(variable)
        session.commit()
        return True
    finally:
        close_session(session)


def update_variable_value(var_name: str, value: Any) -> bool:
    """Update only the value of a variable by name."""
    session = get_session()
    try:
        variable = session.query(Variable).filter_by(name=var_name).first()
        if not variable:
            return False

        variable.value = str(value)

        # Update type based on value
        if isinstance(value, bool):
            variable.type = 'boolean'
        elif isinstance(value, (int, float)):
            variable.type = 'number'
        elif isinstance(value, str):
            variable.type = 'string'
        elif isinstance(value, (list, dict)):
            variable.type = 'object'

        variable.updated_at = datetime.utcnow()
        session.commit()
        return True
    finally:
        close_session(session)


# =============================================================================
# Report Operations
# =============================================================================

def get_all_reports(limit: int = None) -> List[Dict]:
    """Get all reports, optionally limited."""
    session = get_session()
    try:
        query = session.query(Report).order_by(Report.created_at.desc())

        if limit:
            query = query.limit(limit)

        reports = query.all()

        return [
            {
                'id': r.id,
                'module': r.module,
                'totalApis': r.total_apis,  # Number of APIs
                'total': r.total_rules if hasattr(r, 'total_rules') and r.total_rules else r.total_apis,  # Rules count
                'totalRules': r.total_rules if hasattr(r, 'total_rules') else 0,
                'passed': r.passed,
                'failed': r.failed,
                'duration': r.total_duration,
                'timestamp': r.created_at.isoformat() if r.created_at else None,
                'date': r.created_at.isoformat() if r.created_at else None,  # Frontend compatibility
                'htmlPath': r.html_path,
                'jsonPath': r.json_path,
                'status': r.status,
                'error': r.error
            }
            for r in reports
        ]
    finally:
        close_session(session)


def get_report_by_id(report_id: str) -> Optional[Dict]:
    """Get a single report by ID."""
    session = get_session()
    try:
        report = session.query(Report).filter_by(id=report_id).first()
        if not report:
            return None

        return {
            'id': report.id,
            'module': report.module,
            'totalApis': report.total_apis,  # Number of APIs
            'total': report.total_rules if hasattr(report, 'total_rules') and report.total_rules else report.total_apis,
            'totalRules': report.total_rules if hasattr(report, 'total_rules') else 0,
            'passed': report.passed,
            'failed': report.failed,
            'duration': report.total_duration,
            'timestamp': report.created_at.isoformat() if report.created_at else None,
            'date': report.created_at.isoformat() if report.created_at else None,  # Frontend compatibility
            'htmlPath': report.html_path,
            'jsonPath': report.json_path,
            'status': report.status,
            'error': report.error,
            'results': []  # Empty array for frontend compatibility
        }
    finally:
        close_session(session)


def create_report(report_data: Dict) -> Dict:
    """Create a new report."""
    session = get_session()
    try:
        report = Report(
            id=report_data.get('id', f'report-{datetime.now().timestamp()}'),
            module=report_data.get('module'),
            total_apis=report_data.get('total_apis', 0),
            total_rules=report_data.get('total_rules', report_data.get('total', 0)),
            passed=report_data.get('passed', 0),
            failed=report_data.get('failed', 0),
            total_duration=report_data.get('duration', 0.0),
            html_path=report_data.get('htmlPath'),
            json_path=report_data.get('jsonPath'),
            status=report_data.get('status', 'completed'),
            error=report_data.get('error')
        )
        session.add(report)
        session.commit()

        return {'id': report.id}
    finally:
        close_session(session)


def delete_report(report_id: str) -> bool:
    """Delete a report."""
    session = get_session()
    try:
        report = session.query(Report).filter_by(id=report_id).first()
        if not report:
            return False

        session.delete(report)
        session.commit()
        return True
    finally:
        close_session(session)


# =============================================================================
# Protected Variables Initialization
# =============================================================================

def initialize_protected_variables():
    """
    Initialize protected variables for dynamic text generation.
    These variables cannot be deleted and auto-generate values when used.
    """
    PROTECTED_VARIABLES = [
        {
            'id': 'var-protected-postTitle',
            'name': 'postTitle',
            'value': '',
            'type': 'generator',
            'description': 'Auto-generates 20-character random title. Protected variable.'
        },
        {
            'id': 'var-protected-postDescription',
            'name': 'postDescription',
            'value': '',
            'type': 'generator',
            'description': 'Auto-generates 20-character random description. Protected variable.'
        }
    ]

    session = get_session()
    try:
        for var_data in PROTECTED_VARIABLES:
            # Check if variable already exists
            existing = session.query(Variable).filter_by(name=var_data['name']).first()
            if not existing:
                variable = Variable(
                    id=var_data['id'],
                    name=var_data['name'],
                    value=var_data['value'],
                    type=var_data['type'],
                    description=var_data['description']
                )
                session.add(variable)
                print(f"✅ Created protected variable: {var_data['name']}")

        session.commit()
    except Exception as e:
        print(f"⚠️  Error initializing protected variables: {e}")
        session.rollback()
    finally:
        close_session(session)


# =============================================================================
# Folder Management Operations
# =============================================================================

def get_folder_tree() -> List[Dict]:
    """
    Get complete folder hierarchy with nested structure.
    Returns tree structure suitable for frontend rendering.
    """
    session = get_session()
    try:
        # Get all sections ordered by depth and order
        all_sections = session.query(Section).order_by(Section.depth, Section.order).all()

        # Build dictionary for quick lookup
        sections_dict = {}
        root_sections = []

        for section in all_sections:
            section_dict = {
                'id': section.id,
                'name': section.name,
                'description': section.description or '',
                'parent_id': section.parent_id,
                'is_folder': section.is_folder if hasattr(section, 'is_folder') else True,
                'path': section.path if hasattr(section, 'path') else f'/{section.id}',
                'depth': section.depth if hasattr(section, 'depth') else 0,
                'order': section.order,
                'children': [],  # Nested folders
                'apis': []  # APIs in this folder
            }

            sections_dict[section.id] = section_dict

            if section.parent_id is None:
                root_sections.append(section_dict)

        # Build parent-child relationships
        for section in all_sections:
            if section.parent_id and section.parent_id in sections_dict:
                sections_dict[section.parent_id]['children'].append(sections_dict[section.id])

        # Attach APIs to their folders
        apis = session.query(API).order_by(API.order).all()
        for api in apis:
            if api.section_id in sections_dict:
                api_dict = {
                    'id': api.id,
                    'name': api.name,
                    'curl': api.curl,
                    'method': api.method,
                    'url': api.url,
                    'order': api.order,
                    'lastStatus': api.last_status,
                    'lastResult': api.last_result
                }
                sections_dict[api.section_id]['apis'].append(api_dict)

        return root_sections
    finally:
        close_session(session)


def create_folder(name: str, parent_id: str = None, description: str = '') -> Dict:
    """Create a new folder (section with nesting support)."""
    session = get_session()
    try:
        # Calculate depth and path
        depth = 0
        path = ''

        if parent_id:
            parent = session.query(Section).filter_by(id=parent_id).first()
            if not parent:
                raise ValueError('Parent folder not found')
            depth = (parent.depth if hasattr(parent, 'depth') else 0) + 1
            parent_path = parent.path if hasattr(parent, 'path') else f'/{parent.id}'
            path = parent_path
        else:
            path = '/'

        # Get max order at this level
        if parent_id:
            max_order = session.query(Section).filter_by(parent_id=parent_id).count()
        else:
            max_order = session.query(Section).filter_by(parent_id=None).count()

        import time
        folder_id = f'folder-{int(time.time() * 1000)}'
        path = f"{path}/{folder_id}"

        folder = Section(
            id=folder_id,
            name=name,
            description=description,
            parent_id=parent_id,
            is_folder=True,
            path=path,
            depth=depth,
            order=max_order
        )

        session.add(folder)
        session.commit()

        return {
            'id': folder.id,
            'name': folder.name,
            'description': folder.description,
            'parent_id': folder.parent_id,
            'depth': folder.depth,
            'order': folder.order,
            'path': folder.path
        }
    finally:
        close_session(session)


def move_folder(folder_id: str, new_parent_id: str = None) -> bool:
    """
    Move a folder to a new parent (supports drag-and-drop).
    Updates path and depth for all descendants.
    """
    session = get_session()
    try:
        folder = session.query(Section).filter_by(id=folder_id).first()
        if not folder:
            return False

        # Prevent moving folder into its own descendants
        if new_parent_id:
            new_parent = session.query(Section).filter_by(id=new_parent_id).first()
            if not new_parent:
                return False

            # Check if new_parent is a descendant of folder
            folder_path = folder.path if hasattr(folder, 'path') else f'/{folder.id}'
            new_parent_path = new_parent.path if hasattr(new_parent, 'path') else f'/{new_parent.id}'

            if new_parent_path.startswith(folder_path):
                raise ValueError('Cannot move folder into its own descendant')

        # Calculate new depth and path
        old_depth = folder.depth if hasattr(folder, 'depth') else 0
        old_path = folder.path if hasattr(folder, 'path') else f'/{folder.id}'

        if new_parent_id:
            new_parent = session.query(Section).filter_by(id=new_parent_id).first()
            new_depth = (new_parent.depth if hasattr(new_parent, 'depth') else 0) + 1
            new_parent_path = new_parent.path if hasattr(new_parent, 'path') else f'/{new_parent.id}'
            new_path = f"{new_parent_path}/{folder.id}"
        else:
            new_depth = 0
            new_path = f"/{folder.id}"

        depth_diff = new_depth - old_depth

        # Update folder
        folder.parent_id = new_parent_id
        folder.depth = new_depth
        folder.path = new_path

        # Update all descendants (recursive path update)
        descendants = session.query(Section).filter(
            Section.path.like(f"{old_path}/%")
        ).all()

        for desc in descendants:
            # Update depth
            desc.depth = (desc.depth if hasattr(desc, 'depth') else 0) + depth_diff
            # Update path
            old_desc_path = desc.path if hasattr(desc, 'path') else f'/{desc.id}'
            desc.path = old_desc_path.replace(old_path, new_path, 1)

        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error moving folder: {e}")
        raise
    finally:
        close_session(session)


def copy_folder(folder_id: str, new_parent_id: str = None, include_apis: bool = True) -> Dict:
    """
    Copy/duplicate a folder with all its contents.
    Recursively copies subfolders and APIs.
    """
    session = get_session()
    try:
        original = session.query(Section).filter_by(id=folder_id).first()
        if not original:
            raise ValueError('Folder not found')

        # Create new folder
        new_folder = create_folder(
            name=f"{original.name} (Copy)",
            parent_id=new_parent_id or original.parent_id,
            description=original.description or ''
        )

        if include_apis:
            # Copy APIs
            apis = session.query(API).filter_by(section_id=folder_id).all()
            for api in apis:
                import time
                new_api_id = f'api-{int(time.time() * 1000000)}'

                new_api = API(
                    id=new_api_id,
                    name=api.name,
                    section_id=new_folder['id'],
                    curl=api.curl,
                    method=api.method,
                    url=api.url,
                    headers=api.headers,
                    body=api.body,
                    verify_ssl=api.verify_ssl,
                    custom_rules=api.custom_rules,
                    extract_rules=api.extract_rules,
                    last_status=api.last_status,
                    last_result=api.last_result,
                    order=api.order
                )
                session.add(new_api)

            session.commit()

        # Recursively copy child folders
        children = session.query(Section).filter_by(parent_id=folder_id).all()
        for child in children:
            copy_folder(child.id, new_folder['id'], include_apis)

        return new_folder
    except Exception as e:
        session.rollback()
        print(f"Error copying folder: {e}")
        raise
    finally:
        close_session(session)


def get_folder_statistics(folder_id: str, recursive: bool = True) -> Dict:
    """
    Get statistics for a folder (for reporting).

    Returns:
        {
            'folder_id': str,
            'folder_name': str,
            'total_apis': int,
            'total_subfolders': int,
            'depth': int,
            'api_ids': List[str],  # For running all APIs in folder
            'folder_path': str
        }
    """
    session = get_session()
    try:
        folder = session.query(Section).filter_by(id=folder_id).first()
        if not folder:
            return None

        folder_path = folder.path if hasattr(folder, 'path') else f'/{folder.id}'

        stats = {
            'folder_id': folder_id,
            'folder_name': folder.name,
            'folder_path': folder_path,
            'depth': folder.depth if hasattr(folder, 'depth') else 0,
            'total_apis': 0,
            'total_subfolders': 0,
            'api_ids': []
        }

        if recursive:
            # Get all descendants using path
            descendants = session.query(Section).filter(
                Section.path.like(f"{folder_path}/%")
            ).all()

            stats['total_subfolders'] = len(descendants)

            # Get APIs from this folder and all descendants
            folder_ids = [folder.id] + [d.id for d in descendants]
            apis = session.query(API).filter(API.section_id.in_(folder_ids)).all()
            stats['total_apis'] = len(apis)
            stats['api_ids'] = [api.id for api in apis]
        else:
            # Only direct children
            apis = session.query(API).filter_by(section_id=folder_id).all()
            subfolders = session.query(Section).filter_by(parent_id=folder_id).count()

            stats['total_apis'] = len(apis)
            stats['total_subfolders'] = subfolders
            stats['api_ids'] = [api.id for api in apis]

        return stats
    finally:
        close_session(session)


def get_folder_path_name(folder_id: str) -> str:
    """
    Get human-readable folder path (e.g., "Add Post / Cars For Sale / Create Listing").
    """
    session = get_session()
    try:
        folder = session.query(Section).filter_by(id=folder_id).first()
        if not folder:
            return ""

        path_parts = []
        current = folder

        while current:
            path_parts.insert(0, current.name)
            if current.parent_id:
                current = session.query(Section).filter_by(id=current.parent_id).first()
            else:
                break

        return " / ".join(path_parts)
    finally:
        close_session(session)

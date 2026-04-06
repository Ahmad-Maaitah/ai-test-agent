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
        # Get max order for this section
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
            order=max_order
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


def update_api(api_id: str, api_data: Dict) -> bool:
    """Update an existing API."""
    session = get_session()
    try:
        api = session.query(API).filter_by(id=api_id).first()
        if not api:
            return False

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

        session.delete(api)
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
    """Delete a variable."""
    session = get_session()
    try:
        variable = session.query(Variable).filter_by(id=var_id).first()
        if not variable:
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

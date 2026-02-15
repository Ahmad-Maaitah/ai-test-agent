"""Flask routes for the AI Test Agent Web UI."""

import os
import json
import uuid
import re
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, send_from_directory

from backend.runner import run_test_pipeline, generate_allure_report
from backend.report import generate_run_html_report


main_bp = Blueprint('main', __name__)


# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
DATA_FILE = os.path.join(BASE_DIR, 'data.json')


def load_data():
    """Load data from JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"sections": [], "reports": []}


def save_data(data):
    """Save data to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def generate_id():
    """Generate unique ID."""
    return str(uuid.uuid4())[:8]


# =============================================================================
# Pages
# =============================================================================

@main_bp.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@main_bp.route('/output/<path:filename>')
def serve_report(filename):
    """Serve generated reports from the output directory."""
    return send_from_directory(OUTPUT_DIR, filename)


# =============================================================================
# Sections API
# =============================================================================

@main_bp.route('/api/sections', methods=['GET'])
def get_sections():
    """Get all sections with their APIs."""
    data = load_data()
    return jsonify({
        'success': True,
        'sections': data.get('sections', [])
    })


@main_bp.route('/api/sections', methods=['POST'])
def create_section():
    """Create a new section."""
    req_data = request.get_json()
    name = req_data.get('name', '').strip()

    if not name:
        return jsonify({'success': False, 'error': 'Section name is required'}), 400

    data = load_data()

    # Check duplicate name
    for section in data['sections']:
        if section['name'].lower() == name.lower():
            return jsonify({'success': False, 'error': 'Section name already exists'}), 400

    # Get max order
    max_order = max([s.get('order', 0) for s in data['sections']], default=0)

    new_section = {
        'id': f'section-{generate_id()}',
        'name': name,
        'order': max_order + 1,
        'apis': []
    }

    data['sections'].append(new_section)
    save_data(data)

    return jsonify({'success': True, 'section': new_section})


@main_bp.route('/api/sections/<section_id>', methods=['PUT'])
def update_section(section_id):
    """Update section name."""
    req_data = request.get_json()
    name = req_data.get('name', '').strip()

    if not name:
        return jsonify({'success': False, 'error': 'Section name is required'}), 400

    data = load_data()

    for section in data['sections']:
        if section['id'] == section_id:
            section['name'] = name
            save_data(data)
            return jsonify({'success': True, 'section': section})

    return jsonify({'success': False, 'error': 'Section not found'}), 404


@main_bp.route('/api/sections/<section_id>', methods=['DELETE'])
def delete_section(section_id):
    """Delete a section."""
    data = load_data()

    for i, section in enumerate(data['sections']):
        if section['id'] == section_id:
            del data['sections'][i]
            save_data(data)
            return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Section not found'}), 404


@main_bp.route('/api/sections/reorder', methods=['POST'])
def reorder_sections():
    """Reorder sections."""
    req_data = request.get_json()
    section_ids = req_data.get('sectionIds', [])

    data = load_data()

    # Create order map
    order_map = {sid: idx + 1 for idx, sid in enumerate(section_ids)}

    for section in data['sections']:
        if section['id'] in order_map:
            section['order'] = order_map[section['id']]

    # Sort by order
    data['sections'].sort(key=lambda x: x.get('order', 0))
    save_data(data)

    return jsonify({'success': True})


# =============================================================================
# APIs within Sections
# =============================================================================

@main_bp.route('/api/sections/<section_id>/apis', methods=['POST'])
def create_api(section_id):
    """Create a new API in a section."""
    req_data = request.get_json()
    name = req_data.get('name', '').strip()
    curl = req_data.get('curl', '').strip()
    custom_rules = req_data.get('customRules', [])
    extract_rules = req_data.get('extractRules', [])

    if not name:
        return jsonify({'success': False, 'error': 'API name is required'}), 400
    if not curl:
        return jsonify({'success': False, 'error': 'cURL command is required'}), 400

    data = load_data()

    for section in data['sections']:
        if section['id'] == section_id:
            # Check duplicate name in section
            for api in section['apis']:
                if api['name'].lower() == name.lower():
                    return jsonify({'success': False, 'error': 'API name already exists in this section'}), 400

            max_order = max([a.get('order', 0) for a in section['apis']], default=0)

            new_api = {
                'id': f'api-{generate_id()}',
                'name': name,
                'curl': curl,
                'order': max_order + 1,
                'lastStatus': None,
                'lastResult': None,
                'customRules': custom_rules,
                'extractRules': extract_rules
            }

            section['apis'].append(new_api)
            save_data(data)

            return jsonify({'success': True, 'api': new_api})

    return jsonify({'success': False, 'error': 'Section not found'}), 404


@main_bp.route('/api/apis/<api_id>', methods=['PUT'])
def update_api(api_id):
    """Update an API."""
    req_data = request.get_json()
    name = req_data.get('name', '').strip()
    curl = req_data.get('curl', '').strip()
    custom_rules = req_data.get('customRules')
    extract_rules = req_data.get('extractRules')

    data = load_data()

    for section in data['sections']:
        for api in section['apis']:
            if api['id'] == api_id:
                if name:
                    api['name'] = name
                if curl:
                    api['curl'] = curl
                if custom_rules is not None:
                    api['customRules'] = custom_rules
                if extract_rules is not None:
                    api['extractRules'] = extract_rules
                save_data(data)
                return jsonify({'success': True, 'api': api})

    return jsonify({'success': False, 'error': 'API not found'}), 404


@main_bp.route('/api/apis/<api_id>', methods=['DELETE'])
def delete_api(api_id):
    """Delete an API."""
    data = load_data()

    for section in data['sections']:
        for i, api in enumerate(section['apis']):
            if api['id'] == api_id:
                del section['apis'][i]
                save_data(data)
                return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'API not found'}), 404


@main_bp.route('/api/apis/<api_id>/move', methods=['POST'])
def move_api(api_id):
    """Move API to another section."""
    req_data = request.get_json()
    target_section_id = req_data.get('targetSectionId')

    data = load_data()

    # Find and remove API from current section
    api_to_move = None
    for section in data['sections']:
        for i, api in enumerate(section['apis']):
            if api['id'] == api_id:
                api_to_move = section['apis'].pop(i)
                break
        if api_to_move:
            break

    if not api_to_move:
        return jsonify({'success': False, 'error': 'API not found'}), 404

    # Add to target section
    for section in data['sections']:
        if section['id'] == target_section_id:
            max_order = max([a.get('order', 0) for a in section['apis']], default=0)
            api_to_move['order'] = max_order + 1
            section['apis'].append(api_to_move)
            save_data(data)
            return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Target section not found'}), 404


@main_bp.route('/api/sections/<section_id>/apis/reorder', methods=['POST'])
def reorder_apis(section_id):
    """Reorder APIs within a section."""
    req_data = request.get_json()
    api_ids = req_data.get('apiIds', [])

    data = load_data()

    for section in data['sections']:
        if section['id'] == section_id:
            order_map = {aid: idx + 1 for idx, aid in enumerate(api_ids)}
            for api in section['apis']:
                if api['id'] in order_map:
                    api['order'] = order_map[api['id']]
            section['apis'].sort(key=lambda x: x.get('order', 0))
            save_data(data)
            return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Section not found'}), 404


# =============================================================================
# Run APIs
# =============================================================================

@main_bp.route('/api/run', methods=['POST'])
def run_apis():
    """Run selected APIs and generate report."""
    req_data = request.get_json()
    api_ids = req_data.get('apiIds', [])

    if not api_ids:
        return jsonify({'success': False, 'error': 'No APIs selected'}), 400

    data = load_data()

    # Find APIs to run
    apis_to_run = []
    for section in data['sections']:
        for api in section['apis']:
            if api['id'] in api_ids:
                apis_to_run.append({
                    'api': api,
                    'section': section['name']
                })

    if not apis_to_run:
        return jsonify({'success': False, 'error': 'No valid APIs found'}), 400

    # Run each API
    run_id = f'run-{generate_id()}'
    run_date = datetime.now().isoformat()
    results = []

    # Get saved variables for replacement
    saved_variables = {v['name']: v['value'] for v in data.get('variables', [])}

    for item in apis_to_run:
        api = item['api']
        section_name = item['section']

        # Replace variables in cURL command
        curl_command = api['curl']
        def replace_var(match):
            var_name = match.group(1)
            if var_name in saved_variables:
                return str(saved_variables[var_name])
            return match.group(0)  # Keep original if not found
        curl_command = re.sub(r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}', replace_var, curl_command)

        start_time = datetime.now()
        # Pass custom rules to runner if available
        custom_rules = api.get('customRules', [])
        test_result = run_test_pipeline(curl_command, api_name=api['name'], custom_rules=custom_rules)
        end_time = datetime.now()
        execution_time = int((end_time - start_time).total_seconds() * 1000)

        # Auto-update saved variables if response contains matching fields
        response_json = test_result.get('response_json')
        if response_json is not None:
            from backend.flow_context import get_nested_value
            variables_updated = False

            for var in data.get('variables', []):
                source = var.get('source', {})
                field_path = source.get('fieldPath', '')
                if field_path:
                    new_value = get_nested_value(response_json, field_path)
                    if new_value is not None and new_value != var.get('value'):
                        var['value'] = new_value
                        # Update type based on new value
                        if isinstance(new_value, bool):
                            var['type'] = 'boolean'
                        elif isinstance(new_value, (int, float)):
                            var['type'] = 'number'
                        elif isinstance(new_value, str):
                            var['type'] = 'string'
                        elif isinstance(new_value, (list, dict)):
                            var['type'] = 'object'
                        variables_updated = True

            if variables_updated:
                save_data(data)

        # Determine overall result based on rule_type
        structural_pass = all(
            r['result'] == 'PASS'
            for r in test_result.get('rule_results', [])
            if r.get('rule_type') == 'structural'
        )
        functional_pass = all(
            r['result'] == 'PASS'
            for r in test_result.get('rule_results', [])
            if r.get('rule_type') == 'functional'
        )

        overall_result = 'PASS' if (structural_pass and functional_pass) else 'FAIL'

        # Get status code directly from test result (set by runner)
        status_code = test_result.get('status_code')
        error_message = None

        # Fallback: try to get from rule results for legacy compatibility
        if status_code is None:
            for r in test_result.get('rule_results', []):
                if r['rule_name'] == 'Status Code Rule':
                    if r['reason']:
                        match = re.search(r'got (\d+)', r['reason'])
                        if match:
                            status_code = int(match.group(1))
                    else:
                        status_code = 200

        # Collect error messages from failed rules
        for r in test_result.get('rule_results', []):
            if r['result'] == 'FAIL' and r['reason']:
                error_message = r['reason']
                break

        result_entry = {
            'apiId': api['id'],
            'apiName': api['name'],
            'section': section_name,
            'statusCode': status_code,
            'result': overall_result,
            'structuralResult': 'PASS' if structural_pass else 'FAIL',
            'functionalResult': 'PASS' if functional_pass else 'FAIL',
            'executionTime': f'{execution_time}ms',
            'errorMessage': error_message,
            'ruleResults': test_result.get('rule_results', []),
            'reportPaths': test_result.get('report_paths', {})
        }

        results.append(result_entry)

        # Update API last status
        api['lastStatus'] = status_code
        api['lastResult'] = overall_result

    # Generate combined HTML report for this run
    run_report_filename = f'run_report_{run_id}.html'
    run_report_path = os.path.join(OUTPUT_DIR, run_report_filename)
    generate_run_html_report(
        run_id=run_id,
        run_date=run_date,
        results=results,
        report_path=run_report_path
    )

    # Save report
    report = {
        'runId': run_id,
        'date': run_date,
        'totalApis': len(results),
        'passed': sum(1 for r in results if r['result'] == 'PASS'),
        'failed': sum(1 for r in results if r['result'] == 'FAIL'),
        'results': results,
        'htmlReport': run_report_filename
    }

    data['reports'].insert(0, report)  # Add to beginning

    # Keep only last 50 reports
    data['reports'] = data['reports'][:50]

    save_data(data)

    return jsonify({
        'success': True,
        'report': report
    })


@main_bp.route('/api/run-single', methods=['POST'])
def run_single_api():
    """Run a single API test (for Add API flow)."""
    req_data = request.get_json()
    curl = req_data.get('curl', '').strip()
    custom_rules = req_data.get('customRules', [])

    if not curl:
        return jsonify({'success': False, 'error': 'cURL command is required'}), 400

    test_result = run_test_pipeline(curl, custom_rules=custom_rules)

    return jsonify({
        'success': True,
        'result': test_result
    })


@main_bp.route('/api/run-flow', methods=['POST'])
def run_flow():
    """
    Run APIs as a flow with dynamic runtime context.

    Creates a fresh ExecutionContext for each flow run.
    Variables extracted from responses are injected into subsequent API calls.
    Context is discarded after flow completes - no persistence.

    Request body:
    {
        "apiIds": ["api-1", "api-2", ...]  // APIs to run in order
    }

    Returns:
    {
        "success": bool,
        "results": [...],  // Results for each step
        "executionContext": {...},  // Final extracted variables
        "errors": [...]
    }
    """
    from backend.runner import run_flow_pipeline

    req_data = request.get_json()
    api_ids = req_data.get('apiIds', [])

    if not api_ids:
        return jsonify({'success': False, 'error': 'No APIs selected'}), 400

    data = load_data()

    # Build flow steps in the order specified by apiIds
    flow_steps = []
    for api_id in api_ids:
        found = False
        for section in data['sections']:
            for api in section['apis']:
                if api['id'] == api_id:
                    flow_steps.append({
                        'id': api['id'],
                        'name': api['name'],
                        'curl': api['curl'],
                        'customRules': api.get('customRules', []),
                        'extractRules': api.get('extractRules', [])
                    })
                    found = True
                    break
            if found:
                break

    if not flow_steps:
        return jsonify({'success': False, 'error': 'No valid APIs found'}), 400

    # Execute the flow with dynamic runtime context
    result = run_flow_pipeline(flow_steps)

    return jsonify(result)


# =============================================================================
# Reports API
# =============================================================================

@main_bp.route('/api/reports', methods=['GET'])
def get_reports():
    """Get all reports with optional filters."""
    data = load_data()

    section_filter = request.args.get('section')
    result_filter = request.args.get('result')
    api_filter = request.args.get('api')

    reports = data.get('reports', [])

    # Apply filters to results within reports
    if section_filter or result_filter or api_filter:
        filtered_reports = []
        for report in reports:
            filtered_results = report['results']

            if section_filter:
                filtered_results = [r for r in filtered_results if r['section'] == section_filter]
            if result_filter:
                filtered_results = [r for r in filtered_results if r['result'] == result_filter]
            if api_filter:
                filtered_results = [r for r in filtered_results if api_filter.lower() in r['apiName'].lower()]

            if filtered_results:
                filtered_report = report.copy()
                filtered_report['results'] = filtered_results
                filtered_reports.append(filtered_report)

        reports = filtered_reports

    return jsonify({
        'success': True,
        'reports': reports
    })


@main_bp.route('/api/reports/<run_id>', methods=['GET'])
def get_report(run_id):
    """Get a specific report by run ID."""
    data = load_data()

    for report in data.get('reports', []):
        if report['runId'] == run_id:
            return jsonify({
                'success': True,
                'report': report
            })

    return jsonify({'success': False, 'error': 'Report not found'}), 404


@main_bp.route('/api/reports/<run_id>/export', methods=['GET'])
def export_report(run_id):
    """Export report as JSON."""
    data = load_data()

    for report in data.get('reports', []):
        if report['runId'] == run_id:
            return jsonify(report)

    return jsonify({'error': 'Report not found'}), 404


@main_bp.route('/api/reports/<run_id>', methods=['DELETE'])
def delete_report(run_id):
    """Delete a report."""
    data = load_data()

    for i, report in enumerate(data.get('reports', [])):
        if report['runId'] == run_id:
            del data['reports'][i]
            save_data(data)
            return jsonify({'success': True})

    return jsonify({'success': False, 'error': 'Report not found'}), 404


@main_bp.route('/api/reports/<run_id>/rerun-failed', methods=['POST'])
def rerun_failed(run_id):
    """Re-run failed APIs from a report."""
    data = load_data()

    for report in data.get('reports', []):
        if report['runId'] == run_id:
            failed_api_ids = [r['apiId'] for r in report['results'] if r['result'] == 'FAIL']
            if not failed_api_ids:
                return jsonify({'success': False, 'error': 'No failed APIs to re-run'}), 400

            # Trigger run with failed APIs
            return run_apis()  # Will use request body

    return jsonify({'success': False, 'error': 'Report not found'}), 404


# =============================================================================
# Allure Reports
# =============================================================================

@main_bp.route('/api/allure/generate', methods=['POST'])
def generate_allure():
    """Generate Allure report from collected results."""
    allure_results = os.path.join(OUTPUT_DIR, 'allure-results')
    allure_report = os.path.join(OUTPUT_DIR, 'allure-report')

    if not os.path.exists(allure_results):
        return jsonify({'success': False, 'error': 'No Allure results found'}), 404

    success = generate_allure_report(allure_results, allure_report)

    if success:
        return jsonify({
            'success': True,
            'message': 'Allure report generated',
            'reportUrl': '/allure-report/index.html'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to generate Allure report. Make sure Allure is installed.'
        }), 500


@main_bp.route('/allure-report/<path:filename>')
def serve_allure_report(filename):
    """Serve Allure report files."""
    allure_report = os.path.join(OUTPUT_DIR, 'allure-report')
    return send_from_directory(allure_report, filename)


# =============================================================================
# Variables API
# =============================================================================

@main_bp.route('/api/variables', methods=['GET'])
def get_variables():
    """Get all saved variables."""
    data = load_data()
    return jsonify({
        'success': True,
        'variables': data.get('variables', [])
    })


@main_bp.route('/api/variables', methods=['POST'])
def create_variable():
    """Create a new variable."""
    req_data = request.get_json()

    if not req_data.get('name'):
        return jsonify({'success': False, 'error': 'Variable name is required'}), 400
    if 'value' not in req_data:
        return jsonify({'success': False, 'error': 'Variable value is required'}), 400

    data = load_data()
    if 'variables' not in data:
        data['variables'] = []

    # Check for duplicate name
    for var in data['variables']:
        if var['name'] == req_data['name']:
            return jsonify({'success': False, 'error': 'Variable with this name already exists'}), 400

    new_var = {
        'id': f'var-{generate_id()}',
        'name': req_data['name'],
        'value': req_data['value'],
        'type': req_data.get('type', 'string'),
        'description': req_data.get('description', ''),
        'source': req_data.get('source'),
        'createdAt': datetime.now().isoformat()
    }
    data['variables'].append(new_var)
    save_data(data)
    return jsonify({'success': True, 'variable': new_var})


@main_bp.route('/api/variables/<var_id>', methods=['PUT'])
def update_variable(var_id):
    """Update a variable."""
    req_data = request.get_json()
    data = load_data()
    variables = data.get('variables', [])

    for var in variables:
        if var['id'] == var_id:
            # Check for duplicate name if name is being changed
            new_name = req_data.get('name', var['name'])
            if new_name != var['name']:
                for other_var in variables:
                    if other_var['id'] != var_id and other_var['name'] == new_name:
                        return jsonify({'success': False, 'error': 'Variable with this name already exists'}), 400

            var['name'] = new_name
            var['value'] = req_data.get('value', var['value'])
            var['type'] = req_data.get('type', var.get('type', 'string'))
            var['description'] = req_data.get('description', var.get('description', ''))
            save_data(data)
            return jsonify({'success': True, 'variable': var})

    return jsonify({'success': False, 'error': 'Variable not found'}), 404


@main_bp.route('/api/variables/<var_id>', methods=['DELETE'])
def delete_variable(var_id):
    """Delete a variable."""
    data = load_data()
    variables = data.get('variables', [])
    original_count = len(variables)
    data['variables'] = [v for v in variables if v['id'] != var_id]

    if len(data['variables']) == original_count:
        return jsonify({'success': False, 'error': 'Variable not found'}), 404

    save_data(data)
    return jsonify({'success': True})


# =============================================================================
# Dynamic Rules API
# =============================================================================

@main_bp.route('/api/execute-curl', methods=['POST'])
def execute_curl():
    """
    Execute cURL and return response with extracted fields.
    Used when user enters cURL to show available fields for rule selection.
    """
    import time
    import requests
    from backend.utils import parse_curl
    from backend.dynamic_rules import extract_response_fields

    req_data = request.get_json()
    curl = req_data.get('curl', '').strip()

    if not curl:
        return jsonify({'success': False, 'error': 'cURL command is required'}), 400

    try:
        # Parse cURL
        parsed_curl = parse_curl(curl)

        # Execute request
        start_time = time.time()
        response = requests.request(
            method=parsed_curl['method'],
            url=parsed_curl['url'],
            headers=parsed_curl.get('headers', {}),
            data=parsed_curl.get('data'),
            verify=parsed_curl.get('verify_ssl', False),
            timeout=30
        )
        response_time_ms = (time.time() - start_time) * 1000

        # Parse response
        try:
            response_json = response.json()
            fields = extract_response_fields(response_json)
        except Exception:
            response_json = None
            fields = []

        # Auto-update saved variables if response contains matching fields
        updated_variables = []
        if response_json is not None:
            from backend.flow_context import get_nested_value
            data = load_data()
            variables_updated = False

            for var in data.get('variables', []):
                source = var.get('source', {})
                field_path = source.get('fieldPath', '')
                if field_path:
                    # Get value from response using the saved field path
                    new_value = get_nested_value(response_json, field_path)
                    if new_value is not None and new_value != var.get('value'):
                        var['value'] = new_value
                        # Update type based on new value
                        if isinstance(new_value, bool):
                            var['type'] = 'boolean'
                        elif isinstance(new_value, int):
                            var['type'] = 'number'
                        elif isinstance(new_value, float):
                            var['type'] = 'number'
                        elif isinstance(new_value, str):
                            var['type'] = 'string'
                        elif isinstance(new_value, (list, dict)):
                            var['type'] = 'object'
                        updated_variables.append({
                            'name': var['name'],
                            'oldValue': var.get('value'),
                            'newValue': new_value
                        })
                        variables_updated = True

            if variables_updated:
                save_data(data)

        return jsonify({
            'success': True,
            'status_code': response.status_code,
            'response_time_ms': int(response_time_ms),
            'response': response_json,
            'response_text': response.text[:5000] if response_json is None else None,
            'fields': fields,
            'updatedVariables': updated_variables
        })

    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Request timed out (30s limit)'}), 408
    except requests.exceptions.ConnectionError as e:
        error_msg = str(e)
        if 'label empty or too long' in error_msg:
            return jsonify({'success': False, 'error': 'Invalid URL: The hostname in your cURL is malformed. Please check the URL.'}), 400
        return jsonify({'success': False, 'error': 'Connection failed: Unable to reach the server. Check the URL and try again.'}), 502
    except ValueError as e:
        error_msg = str(e)
        if 'label empty or too long' in error_msg or 'Failed to parse' in error_msg:
            return jsonify({'success': False, 'error': 'Invalid URL: The hostname in your cURL is malformed. Please check the URL.'}), 400
        return jsonify({'success': False, 'error': f'Invalid cURL: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500


@main_bp.route('/api/rule-types', methods=['GET'])
def get_rule_types():
    """Get all available rule types with their configuration schemas."""
    from backend.dynamic_rules import get_rule_types

    return jsonify({
        'success': True,
        'ruleTypes': get_rule_types()
    })


@main_bp.route('/api/validate-rules', methods=['POST'])
def validate_rules():
    """Validate a set of rules before saving."""
    from backend.dynamic_rules import validate_rule_config

    req_data = request.get_json()
    rules = req_data.get('rules', [])
    available_fields = req_data.get('fields', [])

    results = []
    all_valid = True

    for rule in rules:
        is_valid, error = validate_rule_config(rule, available_fields)
        results.append({
            'ruleId': rule.get('id'),
            'valid': is_valid,
            'error': error
        })
        if not is_valid:
            all_valid = False

    return jsonify({
        'success': True,
        'allValid': all_valid,
        'results': results
    })


@main_bp.route('/api/test-rules', methods=['POST'])
def test_rules():
    """Test rules against provided response (without re-executing cURL)."""
    from backend.dynamic_rules import apply_dynamic_rules

    req_data = request.get_json()
    rules = req_data.get('rules', [])
    response_json = req_data.get('responseJson')
    status_code = req_data.get('statusCode', 200)
    response_time_ms = req_data.get('responseTimeMs', 0)

    if not rules:
        return jsonify({'success': False, 'error': 'At least one rule is required'}), 400

    if response_json is None:
        return jsonify({'success': False, 'error': 'Response data is required. Execute the cURL first.'}), 400

    try:
        # Apply rules against the provided response
        results = apply_dynamic_rules(rules, response_json, response_time_ms, status_code)

        return jsonify({
            'success': True,
            'status_code': status_code,
            'response_time_ms': int(response_time_ms),
            'results': results
        })

    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Request timed out (30s limit)'}), 408
    except requests.exceptions.ConnectionError as e:
        error_msg = str(e)
        if 'label empty or too long' in error_msg:
            return jsonify({'success': False, 'error': 'Invalid URL: The hostname in your cURL is malformed. Please check the URL.'}), 400
        return jsonify({'success': False, 'error': 'Connection failed: Unable to reach the server. Check the URL and try again.'}), 502
    except ValueError as e:
        error_msg = str(e)
        if 'label empty or too long' in error_msg or 'Failed to parse' in error_msg:
            return jsonify({'success': False, 'error': 'Invalid URL: The hostname in your cURL is malformed. Please check the URL.'}), 400
        return jsonify({'success': False, 'error': f'Invalid cURL: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error: {str(e)}'}), 500

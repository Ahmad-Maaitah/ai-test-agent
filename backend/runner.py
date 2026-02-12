"""
Main orchestration pipeline for the AI Test Agent.

Handles the complete flow:
1. Parse cURL command
2. Execute API request
3. Apply validation rules
4. Generate pytest file
5. Run pytest
6. Generate reports
"""

import os
import subprocess
import sys
import time
import requests
from typing import Optional, List

from backend.utils import (
    parse_curl,
    generate_unique_id,
    get_test_file_path,
    get_report_paths,
    write_file
)
from backend.rules import apply_rules
from backend.report import save_execution_metadata, generate_json_report, generate_html_report


# Default timeout for API requests (30 seconds)
DEFAULT_TIMEOUT = 30


def execute_api_request(parsed_curl: dict, timeout: int = DEFAULT_TIMEOUT) -> requests.Response:
    """
    Execute an API request based on parsed cURL data.

    Args:
        parsed_curl: Dictionary with method, url, headers, data, verify_ssl
        timeout: Request timeout in seconds

    Returns:
        requests.Response object
    """
    response = requests.request(
        method=parsed_curl['method'],
        url=parsed_curl['url'],
        headers=parsed_curl.get('headers', {}),
        data=parsed_curl.get('data'),
        verify=parsed_curl.get('verify_ssl', False),  # Default to False for testing flexibility
        timeout=timeout
    )
    return response


def generate_pytest_code(
    unique_id: str,
    parsed_curl: dict,
    rule_results: list
) -> str:
    """
    Generate pytest code dynamically based on the API request and rule results.

    Args:
        unique_id: Unique identifier for this test run
        parsed_curl: Parsed cURL components
        rule_results: Results from rule validation

    Returns:
        Generated pytest code as a string
    """
    # Escape strings for Python code
    method = parsed_curl['method']
    url = parsed_curl['url']
    headers = repr(parsed_curl.get('headers', {}))
    data = repr(parsed_curl.get('data'))
    verify_ssl = parsed_curl.get('verify_ssl', False)

    test_code = f'''"""
Auto-generated pytest file for API testing.
Execution ID: {unique_id}
URL: {url}
Method: {method}
"""

import pytest
import requests


# API Request Configuration
API_CONFIG = {{
    'method': '{method}',
    'url': '{url}',
    'headers': {headers},
    'data': {data},
    'verify': {verify_ssl},
    'timeout': {DEFAULT_TIMEOUT}
}}


@pytest.fixture(scope='module')
def api_response():
    """Execute the API request and return the response."""
    response = requests.request(
        method=API_CONFIG['method'],
        url=API_CONFIG['url'],
        headers=API_CONFIG['headers'],
        data=API_CONFIG['data'],
        verify=API_CONFIG['verify'],
        timeout=API_CONFIG['timeout']
    )
    return response


class TestAPIValidation:
    """Test class for API validation rules."""

    def test_status_code_rule(self, api_response):
        """PASS if status code is in 2xx range."""
        status_code = api_response.status_code
        assert 200 <= status_code < 300, f"Expected 2xx status code, got {{status_code}}"

    def test_response_exists_rule(self, api_response):
        """PASS if response body is not empty and has no error field."""
        content = api_response.text
        assert content and len(content.strip()) > 0, "Response body is empty"
        try:
            data = api_response.json()
            if isinstance(data, dict):
                if 'error' in data:
                    pytest.fail(f"Response contains error: {{data['error']}}")
                if 'message' in data and api_response.status_code >= 400:
                    pytest.fail(f"Response contains error message: {{data['message']}}")
        except Exception:
            pass

    def test_valid_json_rule(self, api_response):
        """PASS if response body is valid JSON and has no error field."""
        try:
            data = api_response.json()
            if isinstance(data, dict):
                if 'error' in data:
                    pytest.fail(f"Response contains error: {{data['error']}}")
                if 'message' in data and api_response.status_code >= 400:
                    pytest.fail(f"Response contains error message: {{data['message']}}")
        except Exception as e:
            pytest.fail(f"Response is not valid JSON: {{e}}")

    def test_no_error_field_rule(self, api_response):
        """PASS if response JSON does not contain an error field."""
        try:
            data = api_response.json()
            if isinstance(data, dict):
                if 'error' in data:
                    pytest.fail(f"Response contains error: {{data['error']}}")
                if 'message' in data and api_response.status_code >= 400:
                    pytest.fail(f"Response contains error message: {{data['message']}}")
        except Exception:
            pass  # Let valid_json_rule handle JSON errors
'''

    return test_code


def run_pytest(test_file_path: str, report_paths: dict) -> tuple:
    """
    Run pytest on the generated test file with Allure reporting.

    Args:
        test_file_path: Path to the pytest file
        report_paths: Dictionary with html, json, and allure report paths

    Returns:
        Tuple of (return_code, stdout, stderr)
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(report_paths['html']), exist_ok=True)

    # Allure results directory
    allure_results_dir = report_paths.get('allure_results', os.path.join(os.path.dirname(report_paths['html']), 'allure-results'))
    os.makedirs(allure_results_dir, exist_ok=True)

    # Build pytest command with Allure
    pytest_args = [
        sys.executable, '-m', 'pytest',
        test_file_path,
        '-v',
        f'--html={report_paths["html"]}',
        '--self-contained-html',
        f'--json-report',
        f'--json-report-file={report_paths["json"]}',
        f'--alluredir={allure_results_dir}',
    ]

    # Run pytest
    result = subprocess.run(
        pytest_args,
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )

    return result.returncode, result.stdout, result.stderr


def generate_allure_report(allure_results_dir: str, allure_report_dir: str) -> bool:
    """
    Generate Allure HTML report from results.

    Args:
        allure_results_dir: Path to allure results directory
        allure_report_dir: Path to generate allure HTML report

    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(allure_report_dir, exist_ok=True)
        result = subprocess.run(
            ['allure', 'generate', allure_results_dir, '-o', allure_report_dir, '--clean'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        # Allure command not found
        return False
    except Exception:
        return False


def run_test_pipeline(curl_command: str, api_name: str = "API Test", custom_rules: List[dict] = None) -> dict:
    """
    Execute the complete test pipeline.

    Args:
        curl_command: The cURL command to test
        api_name: Name of the API being tested
        custom_rules: Optional list of custom rule configurations

    Returns:
        Dictionary with execution results
    """
    unique_id = generate_unique_id()
    test_file_path = get_test_file_path(unique_id)
    report_paths = get_report_paths(unique_id)

    result = {
        'success': False,
        'execution_id': unique_id,
        'rule_results': [],
        'report_paths': {
            'html': None,
            'json': None
        },
        'error': None,
        'status_code': None,
        'response_time_ms': None
    }

    try:
        # Step 1: Parse cURL command
        parsed_curl = parse_curl(curl_command)

        # Step 2: Execute API request
        start_time = time.time()
        response = execute_api_request(parsed_curl)
        response_time = time.time() - start_time
        response_time_ms = response_time * 1000

        # Step 3: Apply validation rules
        if custom_rules and len(custom_rules) > 0:
            # Use dynamic rules engine for custom rules
            from backend.dynamic_rules import apply_dynamic_rules
            try:
                response_json = response.json()
            except Exception:
                response_json = None
            rule_results = apply_dynamic_rules(custom_rules, response_json, response_time_ms, response.status_code)
        else:
            # Fall back to legacy hardcoded rules
            rule_results = apply_rules(response)
        result['rule_results'] = rule_results

        # Step 4: Generate pytest file
        test_code = generate_pytest_code(unique_id, parsed_curl, rule_results)
        write_file(test_file_path, test_code)

        # Step 5: Run pytest and generate reports
        return_code, stdout, stderr = run_pytest(test_file_path, report_paths)

        # Step 6: Generate custom HTML report with API name
        generate_html_report(
            unique_id=unique_id,
            api_name=api_name,
            curl_command=curl_command,
            rule_results=rule_results,
            report_path=report_paths['html'],
            api_response_status=response.status_code,
            execution_time=f"{response_time:.2f}s"
        )

        # Step 7: Generate backup JSON report if pytest-json-report failed
        if not os.path.exists(report_paths['json']):
            generate_json_report(
                unique_id,
                rule_results,
                report_paths['json'],
                curl_command,
                response.status_code
            )

        # Set report paths in result
        result['report_paths'] = {
            'html': os.path.basename(report_paths['html']),
            'json': os.path.basename(report_paths['json'])
        }

        # Save execution metadata
        save_execution_metadata(
            unique_id=unique_id,
            curl_command=curl_command,
            parsed_curl=parsed_curl,
            rule_results=rule_results,
            test_file_path=test_file_path,
            report_paths=report_paths,
            api_response_status=response.status_code,
            api_response_time=response_time
        )

        result['success'] = True
        result['status_code'] = response.status_code
        result['response_time_ms'] = response_time_ms

    except requests.exceptions.Timeout:
        result['error'] = f'API request timed out after {DEFAULT_TIMEOUT} seconds'
        result['rule_results'] = [
            {'rule_name': 'Status Code Rule', 'result': 'FAIL', 'reason': 'Request timed out'},
            {'rule_name': 'Response Exists Rule', 'result': 'FAIL', 'reason': 'Request timed out'},
            {'rule_name': 'Valid JSON Rule', 'result': 'FAIL', 'reason': 'Request timed out'},
            {'rule_name': 'No Error Field Rule', 'result': 'FAIL', 'reason': 'Request timed out'},
        ]

    except requests.exceptions.ConnectionError as e:
        error_msg = str(e)
        if 'label empty or too long' in error_msg:
            result['error'] = 'Invalid URL: The hostname in your cURL is malformed. Please check the URL.'
        else:
            result['error'] = 'Connection failed: Unable to reach the server. Check the URL and try again.'
        result['rule_results'] = [
            {'rule_name': 'Status Code Rule', 'result': 'FAIL', 'reason': 'Connection failed'},
            {'rule_name': 'Response Exists Rule', 'result': 'FAIL', 'reason': 'Connection failed'},
            {'rule_name': 'Valid JSON Rule', 'result': 'FAIL', 'reason': 'Connection failed'},
            {'rule_name': 'No Error Field Rule', 'result': 'FAIL', 'reason': 'Connection failed'},
        ]

    except ValueError as e:
        error_msg = str(e)
        if 'label empty or too long' in error_msg or 'Failed to parse' in error_msg:
            result['error'] = 'Invalid URL: The hostname in your cURL is malformed. Please check the URL.'
        else:
            result['error'] = f'Invalid cURL command: {str(e)}'

    except Exception as e:
        result['error'] = f'Unexpected error: {str(e)}'

    return result

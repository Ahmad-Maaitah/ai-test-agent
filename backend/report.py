"""
Report generation for test results.

Handles creation of execution metadata and provides paths for pytest-generated reports.
"""

import json
import os
from datetime import datetime
from typing import Optional

from backend.utils import get_metadata_path, write_file


def save_execution_metadata(
    unique_id: str,
    curl_command: str,
    parsed_curl: dict,
    rule_results: list,
    test_file_path: str,
    report_paths: dict,
    api_response_status: Optional[int] = None,
    api_response_time: Optional[float] = None,
    error: Optional[str] = None
) -> str:
    """
    Save execution metadata to a JSON file.

    Args:
        unique_id: Unique identifier for this execution
        curl_command: Original cURL command
        parsed_curl: Parsed cURL components
        rule_results: Results from rule validation
        test_file_path: Path to generated pytest file
        report_paths: Paths to HTML and JSON reports
        api_response_status: HTTP status code from API
        api_response_time: Response time in seconds
        error: Error message if execution failed

    Returns:
        Path to the metadata file
    """
    metadata = {
        'execution_id': unique_id,
        'timestamp': datetime.now().isoformat(),
        'curl_command': curl_command,
        'parsed_curl': {
            'method': parsed_curl.get('method'),
            'url': parsed_curl.get('url'),
            'headers': parsed_curl.get('headers', {}),
            'has_body': parsed_curl.get('data') is not None
        },
        'api_response': {
            'status_code': api_response_status,
            'response_time_seconds': api_response_time
        },
        'rule_results': rule_results,
        'generated_files': {
            'test_file': test_file_path,
            'html_report': report_paths.get('html'),
            'json_report': report_paths.get('json')
        },
        'error': error
    }

    metadata_path = get_metadata_path(unique_id)
    write_file(metadata_path, json.dumps(metadata, indent=2))

    return metadata_path


def generate_json_report(
    unique_id: str,
    rule_results: list,
    report_path: str,
    curl_command: str,
    api_response_status: Optional[int] = None
) -> None:
    """
    Generate a standalone JSON report (backup if pytest-json-report fails).

    Args:
        unique_id: Unique identifier for this execution
        rule_results: Results from rule validation
        report_path: Path to save the JSON report
        curl_command: Original cURL command
        api_response_status: HTTP status code from API
    """
    report = {
        'execution_id': unique_id,
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_rules': len(rule_results),
            'passed': sum(1 for r in rule_results if r['result'] == 'PASS'),
            'failed': sum(1 for r in rule_results if r['result'] == 'FAIL')
        },
        'curl_command': curl_command,
        'api_status_code': api_response_status,
        'results': rule_results
    }

    write_file(report_path, json.dumps(report, indent=2))


def get_relative_report_path(absolute_path: str) -> str:
    """
    Convert absolute report path to relative path for serving via Flask.

    Args:
        absolute_path: Absolute path to the report file

    Returns:
        Relative path from output directory
    """
    return os.path.basename(absolute_path)

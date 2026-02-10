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


def generate_html_report(
    unique_id: str,
    api_name: str,
    curl_command: str,
    rule_results: list,
    report_path: str,
    api_response_status: Optional[int] = None,
    execution_time: Optional[str] = None
) -> None:
    """
    Generate a custom HTML report with API name and test results.

    Args:
        unique_id: Unique identifier for this execution
        api_name: Name of the API being tested
        curl_command: Original cURL command
        rule_results: Results from rule validation
        report_path: Path to save the HTML report
        api_response_status: HTTP status code from API
        execution_time: Execution time string
    """
    passed = sum(1 for r in rule_results if r['result'] == 'PASS')
    failed = sum(1 for r in rule_results if r['result'] == 'FAIL')
    total = len(rule_results)
    overall_result = 'PASS' if failed == 0 else 'FAIL'

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {api_name}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1a1a2e, #16213e); color: white; padding: 25px; border-radius: 10px 10px 0 0; }}
        .header h1 {{ font-size: 1.5rem; margin-bottom: 5px; }}
        .header .subtitle {{ color: rgba(255,255,255,0.7); font-size: 0.9rem; }}
        .summary {{ background: white; padding: 20px; display: flex; gap: 30px; border-bottom: 1px solid #eee; }}
        .summary-item {{ text-align: center; }}
        .summary-value {{ font-size: 2rem; font-weight: 700; }}
        .summary-value.pass {{ color: #27ae60; }}
        .summary-value.fail {{ color: #e74c3c; }}
        .summary-label {{ font-size: 0.85rem; color: #7f8c8d; }}
        .info {{ background: white; padding: 20px; border-bottom: 1px solid #eee; }}
        .info-row {{ display: flex; margin-bottom: 10px; }}
        .info-label {{ width: 120px; font-weight: 600; color: #2c3e50; }}
        .info-value {{ flex: 1; color: #333; font-family: monospace; word-break: break-all; }}
        .results {{ background: white; padding: 20px; border-radius: 0 0 10px 10px; }}
        .results h2 {{ margin-bottom: 15px; color: #2c3e50; font-size: 1.1rem; }}
        .test-case {{ padding: 15px; border-left: 4px solid #27ae60; margin-bottom: 10px; background: #f8f9fa; border-radius: 0 6px 6px 0; }}
        .test-case.fail {{ border-left-color: #e74c3c; background: #fff5f5; }}
        .test-case-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }}
        .test-case-icon {{ font-size: 18px; }}
        .test-case.pass .test-case-icon {{ color: #27ae60; }}
        .test-case.fail .test-case-icon {{ color: #e74c3c; }}
        .test-case-name {{ font-weight: 600; color: #2c3e50; }}
        .test-case-type {{ font-size: 11px; background: #7f8c8d; color: white; padding: 2px 8px; border-radius: 10px; }}
        .test-case-details {{ margin-left: 28px; font-size: 0.9rem; }}
        .test-case-row {{ margin-bottom: 5px; }}
        .test-case-row span {{ display: inline-block; }}
        .label {{ color: #7f8c8d; width: 80px; }}
        .expected {{ color: #27ae60; }}
        .actual {{ color: #e65100; }}
        .actual.fail {{ color: #e74c3c; font-weight: 600; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-weight: 600; font-size: 0.85rem; }}
        .badge.pass {{ background: #d4edda; color: #155724; }}
        .badge.fail {{ background: #f8d7da; color: #721c24; }}
        .footer {{ text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.85rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{api_name}</h1>
            <div class="subtitle">Test Report - {unique_id}</div>
        </div>

        <div class="summary">
            <div class="summary-item">
                <div class="summary-value {overall_result.lower()}">{overall_result}</div>
                <div class="summary-label">Overall Result</div>
            </div>
            <div class="summary-item">
                <div class="summary-value pass">{passed}</div>
                <div class="summary-label">Passed</div>
            </div>
            <div class="summary-item">
                <div class="summary-value fail">{failed}</div>
                <div class="summary-label">Failed</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{total}</div>
                <div class="summary-label">Total Tests</div>
            </div>
        </div>

        <div class="info">
            <div class="info-row">
                <span class="info-label">Status Code:</span>
                <span class="info-value">{api_response_status or '-'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Execution Time:</span>
                <span class="info-value">{execution_time or '-'}</span>
            </div>
            <div class="info-row">
                <span class="info-label">cURL:</span>
                <span class="info-value">{curl_command[:200]}{'...' if len(curl_command) > 200 else ''}</span>
            </div>
        </div>

        <div class="results">
            <h2>Test Cases</h2>
            {''.join([f"""
            <div class="test-case {r['result'].lower()}">
                <div class="test-case-header">
                    <span class="test-case-icon">{'✓' if r['result'] == 'PASS' else '✗'}</span>
                    <span class="test-case-name">{r['rule_name']}</span>
                    <span class="test-case-type">{r.get('rule_type', '')}</span>
                    <span class="badge {r['result'].lower()}">{r['result']}</span>
                </div>
                <div class="test-case-details">
                    <div class="test-case-row">
                        <span class="label">Expected:</span>
                        <span class="expected">{r.get('expected', '-')}</span>
                    </div>
                    <div class="test-case-row">
                        <span class="label">Actual:</span>
                        <span class="actual {'' if r['result'] == 'PASS' else 'fail'}">{r.get('actual', '-')}</span>
                    </div>
                </div>
            </div>
            """ for r in rule_results])}
        </div>

        <div class="footer">
            Generated by AI Test Agent for API | OpenSooq<br>
            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>'''

    write_file(report_path, html)

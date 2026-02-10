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
                    <span class="test-case-name">{r['rule_name']}{f" ({r.get('field', '')})" if r.get('field') else ''}</span>
                    <span class="test-case-type">{r.get('rule_type', '')}</span>
                    <span class="badge {r['result'].lower()}">{r['result']}</span>
                </div>
                <div class="test-case-details">
                    {f'<div class="test-case-row"><span class="label">Field:</span><span style="color: #8e44ad; font-family: monospace;">{r.get("field", "")}</span></div>' if r.get('field') else ''}
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


def generate_run_html_report(
    run_id: str,
    run_date: str,
    results: list,
    report_path: str
) -> None:
    """
    Generate a comprehensive HTML report for all APIs in a test run.

    Args:
        run_id: Unique identifier for this run
        run_date: Date/time of the run
        results: List of API test results grouped by module
        report_path: Path to save the HTML report
    """
    # Group results by module
    modules = {}
    for r in results:
        module = r.get('section', 'Unknown')
        if module not in modules:
            modules[module] = []
        modules[module].append(r)

    total_apis = len(results)
    total_passed = sum(1 for r in results if r['result'] == 'PASS')
    total_failed = sum(1 for r in results if r['result'] == 'FAIL')
    overall_result = 'PASS' if total_failed == 0 else 'FAIL'

    # Build modules HTML
    modules_html = ""
    for module_name, apis in modules.items():
        module_passed = sum(1 for a in apis if a['result'] == 'PASS')
        module_failed = sum(1 for a in apis if a['result'] == 'FAIL')
        module_result = 'pass' if module_failed == 0 else 'fail'

        apis_html = ""
        for api in apis:
            rule_results = api.get('ruleResults', [])
            api_passed = sum(1 for r in rule_results if r['result'] == 'PASS')
            api_failed = sum(1 for r in rule_results if r['result'] == 'FAIL')

            # Build test cases HTML
            tests_html = ""
            for rule in rule_results:
                result_class = rule['result'].lower()
                icon = '✓' if rule['result'] == 'PASS' else '✗'
                field_display = f" <span style='color: #8e44ad; font-size: 0.85rem;'>({rule.get('field', '')})</span>" if rule.get('field') else ''
                field_row = f'''<div class="detail-row"><span class="detail-label">Field:</span><span class="detail-value" style="color: #8e44ad; font-family: monospace;">{rule.get('field', '')}</span></div>''' if rule.get('field') else ''
                tests_html += f'''
                <div class="test-item {result_class}">
                    <div class="test-header">
                        <span class="test-icon">{icon}</span>
                        <span class="test-name">{rule.get('rule_name', '')}{field_display}</span>
                        <span class="test-type">{rule.get('rule_type', '')}</span>
                    </div>
                    <div class="test-details">
                        {field_row}
                        <div class="detail-row">
                            <span class="detail-label">Expected:</span>
                            <span class="detail-value expected">{rule.get('expected', '-')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Actual:</span>
                            <span class="detail-value actual {result_class}">{rule.get('actual', '-')}</span>
                        </div>
                    </div>
                </div>'''

            api_result_class = api['result'].lower()
            api_icon = '✓' if api['result'] == 'PASS' else '✗'

            apis_html += f'''
            <div class="api-card {api_result_class}">
                <div class="api-header">
                    <div class="api-info">
                        <span class="api-icon {api_result_class}">{api_icon}</span>
                        <h4 class="api-name">{api.get('apiName', 'Unknown API')}</h4>
                        <span class="api-badge {api_result_class}">{api['result']}</span>
                    </div>
                    <div class="api-meta">
                        <span class="meta-item"><strong>Status:</strong> {api.get('statusCode', '-')}</span>
                        <span class="meta-item"><strong>Time:</strong> {api.get('executionTime', '-')}</span>
                        <span class="meta-item tests"><strong>Tests:</strong> <span class="pass-count">{api_passed}</span> / <span class="fail-count">{api_failed}</span></span>
                    </div>
                </div>
                <div class="api-tests">
                    <h5 class="tests-title">Test Cases</h5>
                    {tests_html}
                </div>
            </div>'''

        modules_html += f'''
        <div class="module-section">
            <div class="module-header {module_result}" onclick="toggleModule(this)">
                <div class="module-left">
                    <span class="toggle-icon">▼</span>
                    <h3 class="module-name">{module_name}</h3>
                </div>
                <div class="module-stats">
                    <span class="stat pass">{module_passed} passed</span>
                    <span class="stat fail">{module_failed} failed</span>
                    <span class="api-count">{len(apis)} APIs</span>
                </div>
            </div>
            <div class="module-apis">
                {apis_html}
            </div>
        </div>'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {run_id}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            min-height: 100vh;
            padding: 30px;
        }}
        .container {{ max-width: 1100px; margin: 0 auto; }}

        /* Header */
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: white;
            padding: 30px 35px;
            border-radius: 16px 16px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header-left h1 {{ font-size: 1.8rem; margin-bottom: 8px; font-weight: 600; }}
        .header-left .subtitle {{ color: rgba(255,255,255,0.7); font-size: 0.9rem; }}
        .header-badge {{
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            padding: 8px 16px;
            border-radius: 25px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}

        /* Summary Cards */
        .summary {{
            background: white;
            padding: 25px 35px;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            border-bottom: 1px solid #eee;
        }}
        .summary-card {{
            text-align: center;
            padding: 20px;
            border-radius: 12px;
            background: #f8f9fa;
        }}
        .summary-card.result {{ background: linear-gradient(135deg, #1a1a2e, #16213e); color: white; }}
        .summary-card.result.fail {{ background: linear-gradient(135deg, #c0392b, #e74c3c); }}
        .summary-value {{ font-size: 2.5rem; font-weight: 700; line-height: 1.2; }}
        .summary-value.pass {{ color: #27ae60; }}
        .summary-value.fail {{ color: #e74c3c; }}
        .summary-label {{ font-size: 0.85rem; color: #7f8c8d; margin-top: 5px; font-weight: 500; }}
        .summary-card.result .summary-label {{ color: rgba(255,255,255,0.8); }}

        /* Content */
        .content {{ background: white; padding: 30px 35px; border-radius: 0 0 16px 16px; }}
        .content-title {{
            font-size: 1.3rem;
            color: #2c3e50;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 2px solid #eee;
        }}

        /* Module Section */
        .module-section {{ margin-bottom: 20px; }}
        .module-header {{
            background: linear-gradient(135deg, #27ae60, #2ecc71);
            color: white;
            padding: 16px 20px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            user-select: none;
            transition: all 0.2s ease;
        }}
        .module-header:hover {{ opacity: 0.95; transform: translateY(-1px); }}
        .module-header.fail {{ background: linear-gradient(135deg, #c0392b, #e74c3c); }}
        .module-header.expanded {{ border-radius: 10px 10px 0 0; }}
        .module-left {{ display: flex; align-items: center; gap: 12px; }}
        .toggle-icon {{
            font-size: 0.9rem;
            transition: transform 0.3s ease;
            display: inline-block;
        }}
        .module-header.collapsed .toggle-icon {{ transform: rotate(-90deg); }}
        .module-name {{ font-size: 1.1rem; font-weight: 600; }}
        .module-stats {{ display: flex; gap: 12px; align-items: center; }}
        .module-stats .stat {{
            background: rgba(255,255,255,0.2);
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.85rem;
        }}
        .module-stats .api-count {{
            background: rgba(255,255,255,0.3);
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        .module-apis {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 0 0 10px 10px;
            border: 1px solid #e0e0e0;
            border-top: none;
            max-height: 2000px;
            overflow: hidden;
            transition: max-height 0.4s ease, padding 0.4s ease, opacity 0.3s ease;
        }}
        .module-apis.collapsed {{
            max-height: 0;
            padding: 0 20px;
            opacity: 0;
        }}

        /* API Card */
        .api-card {{
            background: white;
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            overflow: hidden;
            border-left: 4px solid #27ae60;
        }}
        .api-card.fail {{ border-left-color: #e74c3c; }}
        .api-card:last-child {{ margin-bottom: 0; }}

        .api-header {{
            padding: 18px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #f0f0f0;
        }}
        .api-info {{ display: flex; align-items: center; gap: 12px; }}
        .api-icon {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            font-weight: bold;
        }}
        .api-icon.pass {{ background: #d4edda; color: #27ae60; }}
        .api-icon.fail {{ background: #f8d7da; color: #e74c3c; }}
        .api-name {{ font-size: 1.05rem; font-weight: 600; color: #2c3e50; }}
        .api-badge {{
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .api-badge.pass {{ background: #d4edda; color: #155724; }}
        .api-badge.fail {{ background: #f8d7da; color: #721c24; }}

        .api-meta {{ display: flex; gap: 20px; font-size: 0.9rem; color: #666; }}
        .meta-item strong {{ color: #2c3e50; }}
        .pass-count {{ color: #27ae60; font-weight: 600; }}
        .fail-count {{ color: #e74c3c; font-weight: 600; }}

        /* Test Cases */
        .api-tests {{ padding: 15px 20px; background: #fafbfc; }}
        .tests-title {{
            font-size: 0.9rem;
            color: #7f8c8d;
            margin-bottom: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .test-item {{
            background: white;
            padding: 12px 15px;
            border-radius: 8px;
            margin-bottom: 8px;
            border-left: 3px solid #27ae60;
        }}
        .test-item.fail {{ border-left-color: #e74c3c; background: #fff9f9; }}
        .test-item:last-child {{ margin-bottom: 0; }}

        .test-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }}
        .test-icon {{ font-size: 14px; }}
        .test-item.pass .test-icon {{ color: #27ae60; }}
        .test-item.fail .test-icon {{ color: #e74c3c; }}
        .test-name {{ font-weight: 600; color: #2c3e50; font-size: 0.95rem; }}
        .test-type {{
            font-size: 0.7rem;
            background: #e0e0e0;
            color: #666;
            padding: 2px 8px;
            border-radius: 10px;
            text-transform: uppercase;
        }}

        .test-details {{ margin-left: 24px; }}
        .detail-row {{
            display: flex;
            gap: 10px;
            margin-bottom: 4px;
            font-size: 0.85rem;
        }}
        .detail-label {{ color: #7f8c8d; min-width: 70px; }}
        .detail-value.expected {{ color: #27ae60; }}
        .detail-value.actual.pass {{ color: #2980b9; }}
        .detail-value.actual.fail {{ color: #e74c3c; font-weight: 600; }}

        /* Footer */
        .footer {{
            text-align: center;
            padding: 25px;
            color: #7f8c8d;
            font-size: 0.85rem;
        }}
        .footer a {{ color: #3498db; text-decoration: none; }}

        /* Print styles */
        @media print {{
            body {{ background: white; padding: 0; }}
            .container {{ max-width: 100%; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-left">
                <h1>API Test Report</h1>
                <div class="subtitle">Run ID: {run_id} | {run_date}</div>
            </div>
            <div class="header-badge">OpenSooq</div>
        </div>

        <div class="summary">
            <div class="summary-card result {overall_result.lower()}">
                <div class="summary-value">{overall_result}</div>
                <div class="summary-label">Overall Result</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{total_apis}</div>
                <div class="summary-label">Total APIs</div>
            </div>
            <div class="summary-card">
                <div class="summary-value pass">{total_passed}</div>
                <div class="summary-label">Passed</div>
            </div>
            <div class="summary-card">
                <div class="summary-value fail">{total_failed}</div>
                <div class="summary-label">Failed</div>
            </div>
        </div>

        <div class="content">
            <h2 class="content-title">Test Results by Module</h2>
            {modules_html}
        </div>

        <div class="footer">
            Generated by <strong>AI Test Agent for API</strong> | OpenSooq<br>
            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>

    <script>
        function toggleModule(header) {{
            const moduleSection = header.parentElement;
            const apis = moduleSection.querySelector('.module-apis');

            if (header.classList.contains('collapsed')) {{
                header.classList.remove('collapsed');
                header.classList.add('expanded');
                apis.classList.remove('collapsed');
            }} else {{
                header.classList.add('collapsed');
                header.classList.remove('expanded');
                apis.classList.add('collapsed');
            }}
        }}

        // Initialize all modules as expanded
        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelectorAll('.module-header').forEach(function(header) {{
                header.classList.add('expanded');
            }});
        }});
    </script>
</body>
</html>'''

    write_file(report_path, html)

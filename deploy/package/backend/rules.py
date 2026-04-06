"""
Validation rules for API responses.

Each rule is an independent function with the signature:
    input: response (requests.Response object)
    output: dict with keys: rule_name, result (PASS/FAIL), reason (if FAIL), expected, actual

To add a new rule:
1. Create a new function following the same signature
2. Add it to the RULES list at the bottom
"""

import json
from typing import Any


def status_code_rule(response: Any) -> dict:
    """
    PASS if status code is in 2xx range.
    Functional rule - checks if the API returned success status.
    """
    status_code = response.status_code

    result = {
        'rule_name': 'Status Code Rule',
        'rule_type': 'functional',
        'result': 'PASS' if 200 <= status_code < 300 else 'FAIL',
        'reason': None if 200 <= status_code < 300 else f'Expected 2xx status code, got {status_code}',
        'expected': '200-299 (2xx)',
        'actual': str(status_code)
    }

    return result


def response_exists_rule(response: Any) -> dict:
    """
    PASS if response body is not empty.
    Structural rule - checks if response structure is valid.
    """
    content = response.text
    content_length = len(content.strip()) if content else 0
    is_pass = content_length > 0

    result = {
        'rule_name': 'Response Exists Rule',
        'rule_type': 'structural',
        'result': 'PASS' if is_pass else 'FAIL',
        'reason': None if is_pass else 'Response body is empty',
        'expected': 'Non-empty response body',
        'actual': f'{content_length} characters' if is_pass else 'Empty response'
    }

    return result


def valid_json_rule(response: Any) -> dict:
    """
    PASS if response body is valid JSON.
    Structural rule - checks if response is properly formatted JSON.
    """
    result = {
        'rule_name': 'Valid JSON Rule',
        'rule_type': 'structural',
        'result': 'FAIL',
        'reason': None,
        'expected': 'Valid JSON format',
        'actual': ''
    }

    try:
        data = response.json()
        result['result'] = 'PASS'
        if isinstance(data, dict):
            result['actual'] = f'JSON Object with {len(data)} keys'
        elif isinstance(data, list):
            result['actual'] = f'JSON Array with {len(data)} items'
        else:
            result['actual'] = f'JSON {type(data).__name__}'
    except (json.JSONDecodeError, ValueError) as e:
        result['reason'] = f'Response is not valid JSON: {str(e)}'
        result['actual'] = 'Invalid JSON'

    return result


def no_error_field_rule(response: Any) -> dict:
    """
    PASS if response JSON does not contain an 'error' or 'message' field (for error responses).
    Functional rule - detects error responses like {"error": "Bad Authentication"}
    """
    result = {
        'rule_name': 'No Error Field Rule',
        'rule_type': 'functional',
        'result': 'PASS',
        'reason': None,
        'expected': 'No error/message fields in response',
        'actual': 'No error fields found'
    }

    try:
        data = response.json()
        if isinstance(data, dict):
            if 'error' in data:
                result['result'] = 'FAIL'
                result['reason'] = f'Response contains error: {data["error"]}'
                result['actual'] = f'error: "{data["error"]}"'
            elif 'message' in data and response.status_code >= 400:
                result['result'] = 'FAIL'
                result['reason'] = f'Response contains error message: {data["message"]}'
                result['actual'] = f'message: "{data["message"]}"'
    except (json.JSONDecodeError, ValueError):
        pass

    return result


# =============================================================================
# RULES REGISTRY
# =============================================================================

RULES = [
    status_code_rule,
    response_exists_rule,
    valid_json_rule,
    no_error_field_rule,
]


def apply_rules(response: Any) -> list:
    """
    Apply all registered rules to a response.

    Args:
        response: requests.Response object

    Returns:
        List of rule results with expected/actual values
    """
    results = []
    for rule in RULES:
        try:
            result = rule(response)
            results.append(result)
        except Exception as e:
            results.append({
                'rule_name': rule.__name__,
                'rule_type': 'unknown',
                'result': 'FAIL',
                'reason': f'Rule execution error: {str(e)}',
                'expected': 'Rule to execute successfully',
                'actual': f'Error: {str(e)}'
            })
    return results

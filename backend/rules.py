"""
Validation rules for API responses.

Each rule is an independent function with the signature:
    input: response (requests.Response object)
    output: dict with keys: rule_name, result (PASS/FAIL), reason (if FAIL)

To add a new rule:
1. Create a new function following the same signature
2. Add it to the RULES list at the bottom
"""

import json
from typing import Any


def status_code_rule(response: Any) -> dict:
    """
    PASS if status code is in 2xx range.
    """
    result = {
        'rule_name': 'Status Code Rule',
        'result': 'FAIL',
        'reason': None
    }

    status_code = response.status_code

    if 200 <= status_code < 300:
        result['result'] = 'PASS'
    else:
        result['reason'] = f'Expected 2xx status code, got {status_code}'

    return result


def response_exists_rule(response: Any) -> dict:
    """
    PASS if response body is not empty and does not contain an error field.
    """
    result = {
        'rule_name': 'Response Exists Rule',
        'result': 'FAIL',
        'reason': None
    }

    content = response.text

    if not content or len(content.strip()) == 0:
        result['reason'] = 'Response body is empty'
        return result

    # Check if response contains error/message field
    try:
        data = response.json()
        if isinstance(data, dict):
            if 'error' in data:
                result['reason'] = f'Response contains error: {data["error"]}'
                return result
            if 'message' in data and response.status_code >= 400:
                result['reason'] = f'Response contains error message: {data["message"]}'
                return result
    except (json.JSONDecodeError, ValueError):
        pass

    result['result'] = 'PASS'
    return result


def valid_json_rule(response: Any) -> dict:
    """
    PASS if response body is valid JSON and does not contain an error field.
    """
    result = {
        'rule_name': 'Valid JSON Rule',
        'result': 'FAIL',
        'reason': None
    }

    try:
        data = response.json()
        # Check if response contains error/message field
        if isinstance(data, dict):
            if 'error' in data:
                result['reason'] = f'Response contains error: {data["error"]}'
                return result
            if 'message' in data and response.status_code >= 400:
                result['reason'] = f'Response contains error message: {data["message"]}'
                return result
        result['result'] = 'PASS'
    except (json.JSONDecodeError, ValueError) as e:
        result['reason'] = f'Response is not valid JSON: {str(e)}'

    return result


def no_error_field_rule(response: Any) -> dict:
    """
    PASS if response JSON does not contain an 'error' or 'message' field (for error responses).
    Detects error responses like {"error": "Bad Authentication"} or {"message": "Requires authentication"}
    """
    result = {
        'rule_name': 'No Error Field Rule',
        'result': 'PASS',
        'reason': None
    }

    try:
        data = response.json()
        if isinstance(data, dict):
            if 'error' in data:
                result['result'] = 'FAIL'
                result['reason'] = f'Response contains error: {data["error"]}'
            elif 'message' in data and response.status_code >= 400:
                result['result'] = 'FAIL'
                result['reason'] = f'Response contains error message: {data["message"]}'
    except (json.JSONDecodeError, ValueError):
        pass

    return result


# =============================================================================
# RULES REGISTRY
# =============================================================================
# Add new rules to this list. Each rule function must follow the signature:
#   input: response (requests.Response object)
#   output: dict with keys: rule_name, result (PASS/FAIL), reason (if FAIL)
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
        List of rule results
    """
    results = []
    for rule in RULES:
        try:
            result = rule(response)
            results.append(result)
        except Exception as e:
            results.append({
                'rule_name': rule.__name__,
                'result': 'FAIL',
                'reason': f'Rule execution error: {str(e)}'
            })
    return results

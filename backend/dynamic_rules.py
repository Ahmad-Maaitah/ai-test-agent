"""
Dynamic Rules Engine for configurable API test cases.

Supports user-defined rules with the following types:
- status_code: Check HTTP status code
- success_flag: Check boolean success field
- field_exists: Verify field presence
- field_not_null: Check field is not null/empty
- field_type: Validate field data type
- response_time: Check response within threshold
- custom_expression: Evaluate custom comparison expressions
"""

import re
from typing import Any, Dict, List, Optional, Tuple


# Rule type definitions with metadata
RULE_TYPES = {
    "status_code": {
        "name": "Status Code (e.g., 200, 404, 500)",
        "description": "Verify HTTP status code equals expected value",
        "example": "Check if API returns 200 OK",
        "requiresField": False,
        "ruleType": "functional",
        "configFields": [
            {"name": "expectedStatus", "type": "number", "label": "Expected Status Code", "default": 200}
        ]
    },
    "response_time": {
        "name": "Response Time (e.g., < 2000ms)",
        "description": "Verify API response time is within acceptable threshold",
        "example": "Ensure response completes within 2 seconds",
        "requiresField": False,
        "ruleType": "performance",
        "configFields": [
            {"name": "maxMs", "type": "number", "label": "Max Response Time (ms)", "default": 2000}
        ]
    },
    "field_exists": {
        "name": "Field Exists (e.g., data.id exists)",
        "description": "Verify that a specific field exists in the response",
        "example": "Check if 'data.user.email' field is present",
        "requiresField": True,
        "ruleType": "structural",
        "configFields": []
    },
    "field_not_null": {
        "name": "Field Not Null (e.g., data.id != null)",
        "description": "Check that a field has a value (not null/empty)",
        "example": "Ensure 'data.token' is not empty",
        "requiresField": True,
        "ruleType": "structural",
        "configFields": []
    },
    "field_type": {
        "name": "Field Type (e.g., data.count is number)",
        "description": "Validate the data type of a field value",
        "example": "Verify 'data.items' is an array",
        "requiresField": True,
        "ruleType": "structural",
        "configFields": [
            {
                "name": "expectedType",
                "type": "select",
                "label": "Expected Type",
                "options": ["string", "number", "boolean", "array", "object"],
                "default": "string"
            }
        ]
    },
    "success_flag": {
        "name": "Boolean Check (e.g., success == true)",
        "description": "Check if a boolean field matches expected true/false",
        "example": "Verify 'data.isActive' equals true",
        "requiresField": True,
        "ruleType": "functional",
        "configFields": [
            {"name": "expectedValue", "type": "boolean", "label": "Expected Value", "default": True}
        ]
    },
    "custom_expression": {
        "name": "Custom Compare (e.g., data.status == 'active')",
        "description": "Compare field value using operators: equals, contains, greater_than, etc.",
        "example": "Check if 'data.role' contains 'admin'",
        "requiresField": True,
        "ruleType": "functional",
        "configFields": [
            {
                "name": "operator",
                "type": "select",
                "label": "Operator",
                "options": ["equals", "not_equals", "contains", "greater_than", "less_than", "regex"],
                "default": "equals"
            },
            {"name": "expectedValue", "type": "text", "label": "Expected Value", "default": ""}
        ]
    }
}


def get_nested_field(data: Any, field_path: str) -> Tuple[Any, bool]:
    """
    Get value from nested field path (e.g., "data.countries.0.name").

    Args:
        data: The JSON data to traverse
        field_path: Dot-separated path (e.g., "data.items.0.id")

    Returns:
        Tuple of (value, found: bool)
    """
    if not field_path or data is None:
        return None, False

    parts = field_path.split('.')
    current = data

    for part in parts:
        if current is None:
            return None, False

        # Handle array index
        if part.isdigit():
            index = int(part)
            if isinstance(current, list) and 0 <= index < len(current):
                current = current[index]
            else:
                return None, False
        # Handle dictionary key
        elif isinstance(current, dict):
            if part in current:
                current = current[part]
            else:
                return None, False
        else:
            return None, False

    return current, True


def get_type_name(value: Any) -> str:
    """Get the JSON type name for a value."""
    if value is None:
        return "null"
    elif isinstance(value, bool):
        return "boolean"
    elif isinstance(value, int) or isinstance(value, float):
        return "number"
    elif isinstance(value, str):
        return "string"
    elif isinstance(value, list):
        return "array"
    elif isinstance(value, dict):
        return "object"
    else:
        return type(value).__name__


def evaluate_rule(rule: Dict, response: Any, response_time_ms: float, status_code: int) -> Dict:
    """
    Evaluate a single rule against the response.

    Args:
        rule: Rule configuration dict
        response: Parsed JSON response body
        response_time_ms: Response time in milliseconds
        status_code: HTTP status code

    Returns:
        Rule result with pass/fail, expected, actual
    """
    rule_type = rule.get('type')
    field = rule.get('field')
    config = rule.get('config', {})

    result = {
        'rule_id': rule.get('id'),
        'rule_name': RULE_TYPES.get(rule_type, {}).get('name', rule_type),
        'rule_type': RULE_TYPES.get(rule_type, {}).get('ruleType', 'functional'),
        'field': field,
        'result': 'FAIL',
        'reason': None,
        'expected': '',
        'actual': ''
    }

    try:
        if rule_type == 'status_code':
            expected_status = config.get('expectedStatus', 200)
            result['expected'] = str(expected_status)
            result['actual'] = str(status_code)

            if status_code == expected_status:
                result['result'] = 'PASS'
            else:
                result['reason'] = f"Expected status {expected_status}, got {status_code}"

        elif rule_type == 'success_flag':
            expected_value = config.get('expectedValue', True)
            value, found = get_nested_field(response, field)

            result['expected'] = str(expected_value).lower()
            result['actual'] = str(value).lower() if found else 'field not found'

            if not found:
                result['reason'] = f"Field '{field}' not found"
            elif value == expected_value:
                result['result'] = 'PASS'
            else:
                result['reason'] = f"Expected {expected_value}, got {value}"

        elif rule_type == 'field_exists':
            value, found = get_nested_field(response, field)

            result['expected'] = f"'{field}' exists"
            if found:
                result['result'] = 'PASS'
                # Show actual value (truncated if too long)
                if value is None:
                    result['actual'] = 'Found (null)'
                elif isinstance(value, str):
                    display_val = value[:50] + '...' if len(value) > 50 else value
                    result['actual'] = f'Found: "{display_val}"'
                elif isinstance(value, (dict, list)):
                    result['actual'] = f'Found: {get_type_name(value)} ({len(value)} items)'
                else:
                    result['actual'] = f'Found: {value}'
            else:
                result['actual'] = 'Not found'
                result['reason'] = f"Field '{field}' does not exist"

        elif rule_type == 'field_not_null':
            value, found = get_nested_field(response, field)

            result['expected'] = 'Not null/empty'

            if not found:
                result['actual'] = 'Field not found'
                result['reason'] = f"Field '{field}' does not exist"
            elif value is None:
                result['actual'] = 'null'
                result['reason'] = f"Field '{field}' is null"
            elif isinstance(value, str) and len(value.strip()) == 0:
                result['actual'] = 'empty string'
                result['reason'] = f"Field '{field}' is empty"
            elif isinstance(value, (list, dict)) and len(value) == 0:
                result['actual'] = 'empty ' + get_type_name(value)
                result['reason'] = f"Field '{field}' is empty"
            else:
                result['result'] = 'PASS'
                if isinstance(value, str):
                    result['actual'] = f'"{value[:50]}{"..." if len(value) > 50 else ""}"'
                else:
                    result['actual'] = f'{get_type_name(value)} with value'

        elif rule_type == 'field_type':
            expected_type = config.get('expectedType', 'string')
            value, found = get_nested_field(response, field)

            result['expected'] = expected_type

            if not found:
                result['actual'] = 'Field not found'
                result['reason'] = f"Field '{field}' does not exist"
            else:
                actual_type = get_type_name(value)
                result['actual'] = actual_type

                if actual_type == expected_type:
                    result['result'] = 'PASS'
                else:
                    result['reason'] = f"Expected {expected_type}, got {actual_type}"

        elif rule_type == 'response_time':
            max_ms = config.get('maxMs', 2000)

            result['expected'] = f'<= {max_ms}ms'
            result['actual'] = f'{int(response_time_ms)}ms'

            if response_time_ms <= max_ms:
                result['result'] = 'PASS'
            else:
                result['reason'] = f"Response time {int(response_time_ms)}ms exceeds {max_ms}ms"

        elif rule_type == 'custom_expression':
            operator = config.get('operator', 'equals')
            expected_value = config.get('expectedValue', '')
            # Strip surrounding quotes if user added them
            if expected_value.startswith('"') and expected_value.endswith('"'):
                expected_value = expected_value[1:-1]
            elif expected_value.startswith("'") and expected_value.endswith("'"):
                expected_value = expected_value[1:-1]
            value, found = get_nested_field(response, field)

            result['expected'] = f'{operator} "{expected_value}"'

            if not found:
                result['actual'] = 'Field not found'
                result['reason'] = f"Field '{field}' does not exist"
            else:
                actual_str = str(value) if value is not None else 'null'
                result['actual'] = actual_str[:100]

                passed = False

                if operator == 'equals':
                    passed = str(value) == expected_value
                elif operator == 'not_equals':
                    passed = str(value) != expected_value
                elif operator == 'contains':
                    passed = expected_value in str(value)
                elif operator == 'greater_than':
                    try:
                        passed = float(value) > float(expected_value)
                    except (ValueError, TypeError):
                        result['reason'] = "Cannot compare non-numeric values"
                elif operator == 'less_than':
                    try:
                        passed = float(value) < float(expected_value)
                    except (ValueError, TypeError):
                        result['reason'] = "Cannot compare non-numeric values"
                elif operator == 'regex':
                    try:
                        passed = bool(re.search(expected_value, str(value)))
                    except re.error as e:
                        result['reason'] = f"Invalid regex: {e}"

                if passed:
                    result['result'] = 'PASS'
                elif not result['reason']:
                    result['reason'] = f"Value '{actual_str[:50]}' does not match {operator} '{expected_value}'"

        else:
            result['reason'] = f"Unknown rule type: {rule_type}"
            result['expected'] = 'Valid rule'
            result['actual'] = 'Unknown rule type'

    except Exception as e:
        result['reason'] = f"Rule evaluation error: {str(e)}"
        result['expected'] = 'Successful evaluation'
        result['actual'] = f'Error: {str(e)}'

    return result


def apply_dynamic_rules(rules: List[Dict], response: Any, response_time_ms: float, status_code: int) -> List[Dict]:
    """
    Apply all custom rules to a response.

    Args:
        rules: List of rule configurations
        response: Parsed JSON response body
        response_time_ms: Response time in milliseconds
        status_code: HTTP status code

    Returns:
        List of rule results
    """
    results = []

    for rule in rules:
        if rule.get('enabled', True):
            result = evaluate_rule(rule, response, response_time_ms, status_code)
            results.append(result)

    return results


def extract_response_fields(data: Any, prefix: str = "", max_depth: int = 5) -> List[str]:
    """
    Recursively extract all field paths from JSON response.

    Args:
        data: JSON data to extract fields from
        prefix: Current field path prefix
        max_depth: Maximum nesting depth to prevent infinite recursion

    Returns:
        List of field paths (e.g., ["id", "data.name", "items.0.id"])
    """
    fields = []

    if max_depth <= 0:
        return fields

    if isinstance(data, dict):
        for key, value in data.items():
            field_path = f"{prefix}.{key}" if prefix else key
            fields.append(field_path)

            # Recurse into nested structures
            if isinstance(value, (dict, list)):
                fields.extend(extract_response_fields(value, field_path, max_depth - 1))

    elif isinstance(data, list) and len(data) > 0:
        # Only show first item as example for arrays
        first_item = data[0]
        field_path = f"{prefix}.0" if prefix else "0"

        if isinstance(first_item, (dict, list)):
            fields.extend(extract_response_fields(first_item, field_path, max_depth - 1))
        else:
            fields.append(field_path)

    return fields


def validate_rule_config(rule: Dict, available_fields: List[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate rule configuration before saving.

    Args:
        rule: Rule configuration to validate
        available_fields: List of available field paths (for field validation)

    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
    """
    rule_type = rule.get('type')

    if not rule_type:
        return False, "Rule type is required"

    if rule_type not in RULE_TYPES:
        return False, f"Unknown rule type: {rule_type}"

    type_config = RULE_TYPES[rule_type]

    # Check if field is required
    if type_config['requiresField']:
        field = rule.get('field')
        if not field:
            return False, f"Field is required for {type_config['name']}"

        # Optionally validate field exists in response
        if available_fields and field not in available_fields:
            return False, f"Field '{field}' not found in response"

    # Validate config fields
    config = rule.get('config', {})

    for field_def in type_config['configFields']:
        field_name = field_def['name']
        field_type = field_def['type']

        value = config.get(field_name)

        # Check if required config is present
        if value is None and 'default' not in field_def:
            return False, f"Configuration '{field_name}' is required"

        # Type validation
        if value is not None:
            if field_type == 'number':
                try:
                    float(value)
                except (ValueError, TypeError):
                    return False, f"'{field_name}' must be a number"

            elif field_type == 'boolean':
                if not isinstance(value, bool):
                    return False, f"'{field_name}' must be a boolean"

            elif field_type == 'select':
                options = field_def.get('options', [])
                if value not in options:
                    return False, f"'{field_name}' must be one of: {', '.join(options)}"

    return True, None


def get_rule_types() -> Dict:
    """Get all available rule types with their configurations."""
    return RULE_TYPES

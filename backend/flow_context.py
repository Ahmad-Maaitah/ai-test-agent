"""
Dynamic Runtime Execution Context for API Flow Engine.

This module provides runtime variable management that exists ONLY during
a single flow execution. No persistence, no global state.

Key features:
- Fresh context per flow run
- Variable injection using {{variableName}} syntax
- Value extraction from JSON responses using dot notation
- Automatic cleanup after flow completes
"""

import re
from typing import Any, Dict, List, Optional


class ExecutionContext:
    """
    Runtime context that exists only during a single flow execution.

    This is NOT stored in database or globally. It's created fresh
    for each flow run and discarded after completion.
    """

    def __init__(self):
        self._variables: Dict[str, Any] = {}

    def set(self, name: str, value: Any) -> None:
        """Store a variable in the execution context."""
        self._variables[name] = value

    def get(self, name: str, default: Any = None) -> Any:
        """Get a variable from the execution context."""
        return self._variables.get(name, default)

    def has(self, name: str) -> bool:
        """Check if variable exists in context."""
        return name in self._variables

    def all(self) -> Dict[str, Any]:
        """Get all variables (returns a copy)."""
        return self._variables.copy()

    def update(self, values: Dict[str, Any]) -> None:
        """Merge multiple values into context."""
        self._variables.update(values)

    def clear(self) -> None:
        """Clear all variables."""
        self._variables.clear()

    def __repr__(self) -> str:
        return f"ExecutionContext({self._variables})"


def inject_variables(text: str, context: ExecutionContext) -> str:
    """
    Replace all {{variableName}} placeholders with context values.

    Args:
        text: The text containing {{variable}} placeholders
        context: The execution context with variable values

    Returns:
        Text with all variables replaced

    Raises:
        ValueError: If a variable is not found in context
    """
    pattern = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}'

    def replacer(match):
        var_name = match.group(1)
        if not context.has(var_name):
            raise ValueError(f"Variable '{var_name}' not found in execution context")
        value = context.get(var_name)
        # Convert to string, handling different types
        if isinstance(value, str):
            return value
        elif isinstance(value, (dict, list)):
            import json
            return json.dumps(value)
        else:
            return str(value)

    return re.sub(pattern, replacer, text)


def extract_from_response(
    response_json: Any,
    extract_rules: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Extract values from response using dot-notation paths.

    Args:
        response_json: The JSON response to extract from
        extract_rules: List of extraction rules

    extract_rules format:
    [
        {"path": "data.workflow_id", "variable": "workflowId"},
        {"path": "data.draft.id", "variable": "draftId"},
        {"path": "items.0.name", "variable": "firstName"}
    ]

    Returns:
        Dictionary of extracted {variableName: value}
    """
    extracted = {}

    for rule in extract_rules:
        path = rule.get('path', '')
        var_name = rule.get('variable', '')

        if not path or not var_name:
            continue

        value = get_nested_value(response_json, path)
        if value is not None:
            extracted[var_name] = value

    return extracted


def get_nested_value(data: Any, path: str) -> Any:
    """
    Get nested value using dot notation.

    Supports:
    - Object properties: data.user.id
    - Array indices: items.0.name
    - Mixed: response.data.users.0.email

    Args:
        data: The data structure to traverse
        path: Dot-notation path like "data.user.id"

    Returns:
        The value at the path, or None if not found
    """
    if data is None:
        return None

    keys = path.split('.')
    current = data

    for key in keys:
        if current is None:
            return None

        # Handle array index
        if isinstance(current, list):
            try:
                index = int(key)
                current = current[index] if 0 <= index < len(current) else None
            except (ValueError, IndexError):
                return None
        # Handle dict key
        elif isinstance(current, dict):
            current = current.get(key)
        else:
            return None

    return current


def validate_variables_in_text(text: str, context: ExecutionContext) -> Dict:
    """
    Check if all variables in text exist in context.

    Args:
        text: Text containing {{variable}} placeholders
        context: The execution context to check against

    Returns:
        {"valid": bool, "missing": [list of missing variable names]}
    """
    pattern = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}'
    matches = re.findall(pattern, text)
    missing = [var for var in matches if not context.has(var)]
    return {"valid": len(missing) == 0, "missing": missing}


def find_variables_in_text(text: str) -> List[str]:
    """
    Find all variable names used in text.

    Args:
        text: Text containing {{variable}} placeholders

    Returns:
        List of unique variable names found
    """
    pattern = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}'
    matches = re.findall(pattern, text)
    return list(set(matches))

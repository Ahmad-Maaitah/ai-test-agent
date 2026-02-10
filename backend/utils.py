"""Utility functions for the AI Test Agent."""

import shlex
import re
import os
import hashlib
from datetime import datetime
from typing import Optional


def parse_curl(curl_command: str) -> dict:
    """
    Parse a cURL command into its components.

    Returns:
        dict with keys: method, url, headers, data, verify_ssl
    """
    result = {
        'method': 'GET',
        'url': None,
        'headers': {},
        'data': None,
        'verify_ssl': True
    }

    # Clean up the command
    curl_command = curl_command.strip()

    # Handle line continuations (backslash at end of line)
    curl_command = re.sub(r'\\\s*\n\s*', ' ', curl_command)

    # Remove 'curl' prefix if present
    if curl_command.lower().startswith('curl'):
        curl_command = curl_command[4:].strip()

    try:
        tokens = shlex.split(curl_command)
    except ValueError as e:
        raise ValueError(f"Failed to parse cURL command: {e}")

    i = 0
    while i < len(tokens):
        token = tokens[i]

        # HTTP Method
        if token in ('-X', '--request'):
            if i + 1 < len(tokens):
                result['method'] = tokens[i + 1].upper()
                i += 2
                continue

        # Headers
        elif token in ('-H', '--header'):
            if i + 1 < len(tokens):
                header = tokens[i + 1]
                if ':' in header:
                    key, value = header.split(':', 1)
                    result['headers'][key.strip()] = value.strip()
                i += 2
                continue

        # Data/Body
        elif token in ('-d', '--data', '--data-raw', '--data-binary'):
            if i + 1 < len(tokens):
                result['data'] = tokens[i + 1]
                # If data is provided and method is GET, change to POST
                if result['method'] == 'GET':
                    result['method'] = 'POST'
                i += 2
                continue

        # JSON data shorthand
        elif token == '--json':
            if i + 1 < len(tokens):
                result['data'] = tokens[i + 1]
                result['headers']['Content-Type'] = 'application/json'
                if result['method'] == 'GET':
                    result['method'] = 'POST'
                i += 2
                continue

        # Insecure (skip SSL verification)
        elif token in ('-k', '--insecure'):
            result['verify_ssl'] = False
            i += 1
            continue

        # Skip common flags we don't need
        elif token in ('-v', '--verbose', '-s', '--silent', '-S', '--show-error',
                       '-L', '--location', '-i', '--include', '-o', '--output',
                       '-w', '--write-out', '-c', '--cookie-jar', '-b', '--cookie'):
            # Some of these take arguments, some don't
            if token in ('-o', '--output', '-w', '--write-out', '-c', '--cookie-jar', '-b', '--cookie'):
                i += 2  # Skip the argument too
            else:
                i += 1
            continue

        # User agent
        elif token in ('-A', '--user-agent'):
            if i + 1 < len(tokens):
                result['headers']['User-Agent'] = tokens[i + 1]
                i += 2
                continue

        # URL (anything that looks like a URL or doesn't start with -)
        elif not token.startswith('-'):
            # Check if it looks like a URL
            if token.startswith(('http://', 'https://')) or '.' in token:
                result['url'] = token
                # Add protocol if missing
                if not result['url'].startswith(('http://', 'https://')):
                    result['url'] = 'https://' + result['url']
            i += 1
            continue

        i += 1

    if not result['url']:
        raise ValueError("No URL found in cURL command")

    return result


def generate_unique_id() -> str:
    """Generate a unique identifier for this test run."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    hash_suffix = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
    return f"{timestamp}_{hash_suffix}"


def get_test_file_path(unique_id: str) -> str:
    """Get the path for a generated test file."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'tests', f'test_api_{unique_id}.py')


def get_report_paths(unique_id: str) -> dict:
    """Get paths for HTML and JSON reports."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, 'output')

    return {
        'html': os.path.join(output_dir, f'report_{unique_id}.html'),
        'json': os.path.join(output_dir, f'report_{unique_id}.json'),
        'allure_results': os.path.join(output_dir, 'allure-results', unique_id),
        'allure_report': os.path.join(output_dir, 'allure-report', unique_id)
    }


def get_metadata_path(unique_id: str) -> str:
    """Get path for execution metadata file."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    metadata_dir = os.path.join(base_dir, 'output', 'metadata')
    os.makedirs(metadata_dir, exist_ok=True)
    return os.path.join(metadata_dir, f'execution_{unique_id}.json')


def write_file(path: str, content: str) -> None:
    """Write content to a file, creating directories if needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

"""
Auto-generated pytest file for API testing.
Execution ID: 20260209_144831_38186034
URL: https://jsonplaceholder.typicode.com/posts/1
Method: GET
"""

import pytest
import requests


# API Request Configuration
API_CONFIG = {
    'method': 'GET',
    'url': 'https://jsonplaceholder.typicode.com/posts/1',
    'headers': {},
    'data': None,
    'verify': True,
    'timeout': 30
}


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
        assert 200 <= status_code < 300, f"Expected 2xx status code, got {status_code}"

    def test_response_exists_rule(self, api_response):
        """PASS if response body is not empty."""
        content = api_response.text
        assert content and len(content.strip()) > 0, "Response body is empty"

    def test_valid_json_rule(self, api_response):
        """PASS if response body is valid JSON."""
        try:
            api_response.json()
        except Exception as e:
            pytest.fail(f"Response is not valid JSON: {e}")

    def test_no_error_field_rule(self, api_response):
        """PASS if response JSON does not contain an 'error' field."""
        try:
            data = api_response.json()
            if isinstance(data, dict) and 'error' in data:
                pytest.fail(f"Response contains error: {data['error']}")
        except Exception:
            pass  # Let valid_json_rule handle JSON errors

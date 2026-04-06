"""
Auto-generated pytest file for API testing.
Execution ID: 20260406_102618_269a48ba
URL: https://api.opensooq.com/v2.1/cities?expand=neighborhoods
Method: GET
"""

import pytest
import requests


# API Request Configuration
API_CONFIG = {
    'method': 'GET',
    'url': 'https://api.opensooq.com/v2.1/cities?expand=neighborhoods',
    'headers': {'country': 'jo', 'source': 'ios', 'x-access-token': 'a9d85bf9942cf90b64793dfe5aad7564dfc104b7', 'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdDAiOjE3NDcwNTM1NDUsImF1ZCI6ImRlc2t0b3AiLCJzdWIiOjE0NDQyMDY0LCJybmQiOiIzNzEyMTMxNSIsImV4cCI6MTc0NzI5NjEyM30.8CxffCKPHffoLZtvJp1SAoWcvPFcYzBH5LAPLt205aY'},
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
        """PASS if response body is not empty and has no error field."""
        content = api_response.text
        assert content and len(content.strip()) > 0, "Response body is empty"
        try:
            data = api_response.json()
            if isinstance(data, dict):
                if 'error' in data:
                    pytest.fail(f"Response contains error: {data['error']}")
                if 'message' in data and api_response.status_code >= 400:
                    pytest.fail(f"Response contains error message: {data['message']}")
        except Exception:
            pass

    def test_valid_json_rule(self, api_response):
        """PASS if response body is valid JSON and has no error field."""
        try:
            data = api_response.json()
            if isinstance(data, dict):
                if 'error' in data:
                    pytest.fail(f"Response contains error: {data['error']}")
                if 'message' in data and api_response.status_code >= 400:
                    pytest.fail(f"Response contains error message: {data['message']}")
        except Exception as e:
            pytest.fail(f"Response is not valid JSON: {e}")

    def test_no_error_field_rule(self, api_response):
        """PASS if response JSON does not contain an error field."""
        try:
            data = api_response.json()
            if isinstance(data, dict):
                if 'error' in data:
                    pytest.fail(f"Response contains error: {data['error']}")
                if 'message' in data and api_response.status_code >= 400:
                    pytest.fail(f"Response contains error message: {data['message']}")
        except Exception:
            pass  # Let valid_json_rule handle JSON errors

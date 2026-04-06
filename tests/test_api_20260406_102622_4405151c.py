"""
Auto-generated pytest file for API testing.
Execution ID: 20260406_102622_4405151c
URL: https://opensooq.com/api//home/v2/full?source=opensooq&medium=app_open&campaign=direct_app_open&abBucket=3
Method: GET
"""

import pytest
import requests


# API Request Configuration
API_CONFIG = {
    'method': 'GET',
    'url': 'https://opensooq.com/api//home/v2/full?source=opensooq&medium=app_open&campaign=direct_app_open&abBucket=3',
    'headers': {'release-version': 'pwa-prod-7.2.03-build-2435', 'ConnectionType': 'WiFi', 'source': 'ios', 'Accept-Language': 'ar', 'country': 'jo', 'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdDAiOjE3NDY5NTIzNzEsImF1ZCI6ImRlc2t0b3AiLCJzdWIiOjcxMDA3NDkyLCJybmQiOiIwMzExNDIiLCJleHAiOjE3NDY5NjQzNzB9.SibGNiSF9UmDdD9kEx0njndV0WWb_jYtYqreHR5uqy4'},
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

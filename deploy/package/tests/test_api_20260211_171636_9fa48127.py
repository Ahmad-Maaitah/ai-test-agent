"""
Auto-generated pytest file for API testing.
Execution ID: 20260211_171636_9fa48127
URL: https://api.opensooq.com/vertical/forms/v1/add-post/normal/1?source=opensooq&medium=app_open&campaign=direct_app_open&expand=remaining_edit_counter%2Cmedia
Method: GET
"""

import pytest
import requests


# API Request Configuration
API_CONFIG = {
    'method': 'GET',
    'url': 'https://api.opensooq.com/vertical/forms/v1/add-post/normal/1?source=opensooq&medium=app_open&campaign=direct_app_open&expand=remaining_edit_counter%2Cmedia',
    'headers': {'latency_ms': '1535', 'abBucket': '3', 'Accept-Language': 'en', 'ConnectionType': 'WiFi', 'Device-Language': 'ar', 'source': 'ios', 'always-200': '1', 'release-version': '11.2.00.15', 'Accept-Encoding': 'br;q=1.0, gzip;q=0.9, deflate;q=0.8', 'currency': 'JOD', 'device_language': 'ar', 'X-Tracking-UUID': '_46F5383F-B17E-45B3-8E22-9937D0D5565C', 'display-mode': 'normal', 'country': 'jo', 'device_timezone': 'UTC+03:00', 'version': '4', 'X-JWT-Try-Counter': '1', 'session-id': 'EE971F6F-584D-44FA-8EC9-EBFD512E6DF6', 'device-model': 'iPhone11,8', 'User-Agent': 'OpenSooq/11.2.00.15_qa_stag/v2.1/3 (com.opensooq.App; build:20241231215200; iOS 14.4.0) Alamofire/5.4.1', 'rm': '0', 'screen_resolution': '414x896', 'Authorization': 'Basic MDc4NTU2OTM0MjphaG1hZDEyMw=='},
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

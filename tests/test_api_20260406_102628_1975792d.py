"""
Auto-generated pytest file for API testing.
Execution ID: 20260406_102628_1975792d
URL: https://opensooq.com/api//taxonomy-api/v8?Action_screen_name=search&medium=app_open&source=opensooq&campaign=direct_app_open
Method: POST
"""

import pytest
import requests


# API Request Configuration
API_CONFIG = {
    'method': 'POST',
    'url': 'https://opensooq.com/api//taxonomy-api/v8?Action_screen_name=search&medium=app_open&source=opensooq&campaign=direct_app_open',
    'headers': {'currency': 'JOD', 'Accept': 'application/json', 'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdDAiOjE3NDIyMDAwMjksImF1ZCI6ImRlc2t0b3AiLCJzdWIiOjcxMDA3NDkyLCJybmQiOiI0MTQ3OTMiLCJleHAiOjE3NDIyMDA0OTN9.dqwJDFa6WktAOs_YPusalVVoXEHODccWp2rd4l3OVBs', 'abBucket': '1', 'release-version': '11.1.00.06', 'Device-Language': 'en', 'country': 'jo', 'source': 'ios', 'device_timezone': 'UTC+03:00', 'always-200': '1', 'session-id': '9A2078A0-CEB1-4C5B-8DB5-78CE8C0B988B', 'appVersion': 'pwa-prod-7.2.03-build-2435', 'Accept-Charset': 'UTF-8', 'rm': '0', 'latency_ms': '527', 'ConnectionType': 'WiFi', 'version': '4', 'X-Tracking-UUID': '_4992B0EA-9E15-4B93-A83C-D8482CC303D6', 'User-Agent': 'OpenSooq/11.1.00.06_qa_stag/v2.1/1 (com.opensooq.App; build:20241128111310; iOS 14.6.0) Alamofire/5.4.1', 'Content-Type': 'application/json', 'device-model': 'iPhone11,6', 'display-mode': 'normal', 'screen_resolution': '414x896', 'Accept-Language': 'en'},
    'data': '{\n    "vertical_link" : "Property", "filters" :{\n        "clone_vertical_link\\/Property": [\n            1\n        ]\n    },\n\n"sort_code":"",\n"selected_cell_type":"GridCell",\n"filters_val":{\n\n},\n\n"member_ids":[\n\n],\n"page":1\n}',
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

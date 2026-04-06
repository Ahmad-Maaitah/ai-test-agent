"""
Auto-generated pytest file for API testing.
Execution ID: 20260402_155242_fab7e1b1
URL: https://api.opensooq.com/v2.1/members/66983508?NO-NULL=1&source=opensooq&medium=app_open&campaign=direct_app_open&expand=postCount%2ClimitAccountReport%2CfollowersCount%2Cviews%2CfollowingsCount%2Crating%2CmemberDetails%2Cmembership_type%2Cbundle_count%2Cwallet_amount%2CisShopProfileCompleted%2Ccv%2CwalletInfo
Method: GET
"""

import pytest
import requests


# API Request Configuration
API_CONFIG = {
    'method': 'GET',
    'url': 'https://api.opensooq.com/v2.1/members/66983508?NO-NULL=1&source=opensooq&medium=app_open&campaign=direct_app_open&expand=postCount%2ClimitAccountReport%2CfollowersCount%2Cviews%2CfollowingsCount%2Crating%2CmemberDetails%2Cmembership_type%2Cbundle_count%2Cwallet_amount%2CisShopProfileCompleted%2Ccv%2CwalletInfo',
    'headers': {'device_language': 'en', 'session-id': '8670D21E-9DA8-45CC-AA47-F1C5ECD59EAC', 'Device-Language': 'en', 'currency': 'jo', 'User-Agent': 'OpenSooq/10.9.01.04_qa_stag/v2.1/3 (com.opensooq.App; build:20241006171549; iOS 15.8.2) Alamofire/5.4.1', 'latency_ms': '727', 'screen_resolution': '414x736', 'X-JWT-Try-Counter': '1', 'Accept-Language': 'ar', 'country': 'jo', 'ConnectionType': 'WiFi', 'release-version': '10.9.01.04', 'device_timezone': 'UTC+03:00', 'Accept-Encoding': 'br;q=1.0, gzip;q=0.9, deflate;q=0.8', 'version': '4', 'device-model': 'iPhone8,2', 'abBucket': '3', 'rm': '0', 'source': 'web', 'display-mode': 'normal', 'always-200': '1', 'Authorization': 'Basic MDc4NTU2OTM0MjphaG1hZDEyMw=='},
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

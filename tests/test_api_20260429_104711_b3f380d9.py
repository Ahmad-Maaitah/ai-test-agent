"""
Auto-generated pytest file for API testing.
Execution ID: 20260429_104711_b3f380d9
URL: https://api.sooqtest.com/vertical/forms/v1/add-post/normal/1?expand=remaining_edit_counter,media,post.overLimitType,post.isOverLimit&cMedium=web_open&cName=direct_web_open&cSource=opensooq&abBucket=3
Method: GET
"""

import pytest
import requests


# API Request Configuration
API_CONFIG = {
    'method': 'GET',
    'url': 'https://api.sooqtest.com/vertical/forms/v1/add-post/normal/1?expand=remaining_edit_counter,media,post.overLimitType,post.isOverLimit&cMedium=web_open&cName=direct_web_open&cSource=opensooq&abBucket=3',
    'headers': {'abbucket': '3', 'accept': 'application/json, text/plain, */*', 'accept-language': 'ar', 'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdDAiOjE3Nzc0NDU5ODUsImF1ZCI6ImRlc2t0b3AiLCJzdWIiOjgxMjg1MzMwLCJybmQiOiIxNDgxNDAzIiwiZXhwIjoxNzc3NDQ5MDcyfQ.OOAU--g08nXBIW9KA3UCG_HFhqCAVppGyOnRg5Y4xuw', 'country': 'jo', 'enforce-language': 'ar', 'origin': 'https://add.opensooq.com', 'priority': 'u=1, i', 'referer': 'https://add.opensooq.com/', 'release-version': '11.3.0', 'sec-ch-ua': '', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'session-id': 'a7c5695d-ea9a-4db0-9343-21d8eb78bbef', 'source': 'desktop', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36', 'x-tracking-uuid': 'a7c5695d-ea9a-4db0-9343-21d8eb78bbef'},
    'data': None,
    'verify': True,
    'timeout': 30
}


@pytest.fixture(scope='module')
def api_response():
    """Execute the API request and return the response."""
    request_params = {
        'method': API_CONFIG['method'],
        'url': API_CONFIG['url'],
        'headers': API_CONFIG['headers'],
        'verify': API_CONFIG['verify'],
        'timeout': API_CONFIG['timeout']
    }

    # Add json or data parameter if present
    if 'json' in API_CONFIG and API_CONFIG['json']:
        request_params['json'] = API_CONFIG['json']
    elif 'data' in API_CONFIG and API_CONFIG['data']:
        request_params['data'] = API_CONFIG['data']

    response = requests.request(**request_params)
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

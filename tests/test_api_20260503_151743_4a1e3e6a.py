"""
Auto-generated pytest file for API testing.
Execution ID: 20260503_151743_4a1e3e6a
URL: https://my.opensooq.com/api/taxonomy-api/v3/favorites-listings?cSource=opensooq&cName=direct_web_open&cMedium=web_open&abBucket=2
Method: POST
"""

import pytest
import requests


# API Request Configuration
API_CONFIG = {
    'method': 'POST',
    'url': 'https://my.opensooq.com/api/taxonomy-api/v3/favorites-listings?cSource=opensooq&cName=direct_web_open&cMedium=web_open&abBucket=2',
    'headers': {'abbucket': '2', 'accept': 'application/json, text/plain, */*', 'accept-language': 'ar', 'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdDAiOjE3NzY3NzUwODcsImF1ZCI6ImRlc2t0b3AiLCJzdWIiOjc2NDE1ODk3LCJybmQiOiIzNTA3MyIsImV4cCI6MTc3NzM4MjE4Mn0.ZHomadRCX8R6KjRX2sqPsgLcbIkSOXbsZcNOsHaBPIE', 'cache-control': 'no-cache', 'content-type': 'application/json', 'country': 'jo', 'enforce-language': 'ar', 'origin': 'https://my.opensooq.com', 'pragma': 'no-cache', 'priority': 'u=1, i', 'referer': 'https://my.opensooq.com/listings/demand/favorite-listings?v=2026-04-28&cSource=opensooq&cMedium=none&cName=direct_web_open', 'sec-ch-ua': '', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin', 'session-id': '76415897', 'source': 'desktop', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36'},
    'json': {'page': 1},
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

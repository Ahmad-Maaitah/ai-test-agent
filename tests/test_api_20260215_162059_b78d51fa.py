"""
Auto-generated pytest file for API testing.
Execution ID: 20260215_162059_b78d51fa
URL: https://api.opensooq.com/vertical/forms/v1/add-post/normal/post_mediaStepIdentifier/401100?expand=remaining_edit_counter,media,post.overLimitType,post.isOverLimit&cMedium=web_open&cName=direct_web_open&cSource=opensooq&abBucket=3
Method: POST
"""

import pytest
import requests


# API Request Configuration
API_CONFIG = {
    'method': 'POST',
    'url': 'https://api.opensooq.com/vertical/forms/v1/add-post/normal/post_mediaStepIdentifier/401100?expand=remaining_edit_counter,media,post.overLimitType,post.isOverLimit&cMedium=web_open&cName=direct_web_open&cSource=opensooq&abBucket=3',
    'headers': {'abbucket': '3', 'accept': 'application/json, text/plain, */*', 'accept-language': 'ar', 'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdDAiOjE3NzA1OTQwMDcsImF1ZCI6ImRlc2t0b3AiLCJzdWIiOjgwNjE0MDAxLCJybmQiOiIzMzE1NzUiLCJleHAiOjE3NzExNDkwNzh9.bpu9g1uk0wONHxbNP1e52APS0v4WxhSrzDscGRS8zDU', 'content-type': 'application/x-www-form-urlencoded', 'country': 'jo', 'enforce-language': 'ar', 'origin': 'https://add.opensooq.com', 'priority': 'u=1, i', 'referer': 'https://add.opensooq.com/', 'release-version': '11.3.0', 'sec-ch-ua': '', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-site', 'session-id': 'a7c5695d-ea9a-4db0-9343-21d8eb78bbef', 'source': 'desktop', 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36', 'x-tracking-uuid': 'a7c5695d-ea9a-4db0-9343-21d8eb78bbef'},
    'data': 'undefined=1&draftId=9840714c-1c76-4bd3-b8f4-2377a1b7ae47&workflowId=401100&currentStep=post_mediaStepIdentifier&categoriesSub=7107&time_spent_ms=363325&categoriesMain=7105&payloadPassCps={&postMedia=0',
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

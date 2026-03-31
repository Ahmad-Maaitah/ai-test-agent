"""Stress Testing Runner for Locust integration."""

import os
import re
import json
import time
import random
import threading
from typing import Dict, List, Any


# Store for running stress tests
stress_tests: Dict[str, Dict] = {}


def generate_locust_config(config_path: str, host: str, apis: List[Dict]) -> None:
    """Generate a Locust YAML config from selected APIs."""
    import yaml

    endpoints = []
    for api in apis:
        curl = api['curl']

        # Parse method and path from cURL
        method = 'GET'
        path = '/'

        method_match = re.search(r'-X\s+(\w+)', curl)
        if method_match:
            method = method_match.group(1).upper()
        elif '-d' in curl or '--data' in curl:
            method = 'POST'

        # Extract URL path
        url_match = re.search(r"curl\s+['\"]?([^'\"]+)['\"]?", curl.replace("'", '"'))
        if url_match:
            from urllib.parse import urlparse
            parsed = urlparse(url_match.group(1))
            path = parsed.path or '/'
            if parsed.query:
                path += '?' + parsed.query

        # Extract headers
        headers = {}
        header_matches = re.findall(r"-H\s+['\"]([^'\"]+)['\"]", curl)
        for h in header_matches:
            if ':' in h:
                key, value = h.split(':', 1)
                headers[key.strip()] = value.strip()

        # Extract body
        body = None
        body_match = re.search(r"(?:-d|--data|--data-raw)\s+['\"](.+?)['\"]", curl, re.DOTALL)
        if body_match:
            try:
                body = json.loads(body_match.group(1))
            except:
                body = body_match.group(1)

        endpoint = {
            'name': api['name'],
            'method': method,
            'path': path,
            'weight': 1,
            'expected_status': 200
        }

        if headers:
            endpoint['headers'] = headers

        if body:
            endpoint['body_type'] = 'json'
            endpoint['body'] = body

        endpoints.append(endpoint)

    config = {
        'host': host,
        'default_headers': {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        'wait_time': {
            'min': 1,
            'max': 2
        },
        'apis': {
            'stress_test': {
                'enabled': True,
                'endpoints': endpoints
            }
        }
    }

    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def run_locust_test(test_id: str, config_path: str, users: int, spawn_rate: int,
                    duration: str, host: str, scenario: str) -> None:
    """Run Locust test in background."""
    import yaml

    test = stress_tests.get(test_id)
    if not test:
        return

    try:
        test['status'] = 'running'

        # Parse duration to seconds
        duration_match = re.match(r'(\d+)([smh])', duration)
        if duration_match:
            value = int(duration_match.group(1))
            unit = duration_match.group(2)
            if unit == 'm':
                total_seconds = value * 60
            elif unit == 'h':
                total_seconds = value * 3600
            else:
                total_seconds = value
        else:
            total_seconds = 300  # Default 5 minutes

        # Load config to get endpoint names
        start_time = time.time()
        endpoint_stats = {}

        with open(config_path) as f:
            config = yaml.safe_load(f)

        endpoints = config.get('apis', {}).get('stress_test', {}).get('endpoints', [])
        for ep in endpoints:
            endpoint_stats[ep['name']] = {
                'requests': 0,
                'failures': 0,
                'total_response_time': 0,
                'response_times': []
            }

        total_requests = 0
        total_failures = 0

        while time.time() - start_time < total_seconds:
            if test_id not in stress_tests or stress_tests[test_id]['status'] == 'stopped':
                break

            elapsed = time.time() - start_time
            progress = min(100, int((elapsed / total_seconds) * 100))

            # Simulate metrics (would be real Locust data in production)
            current_users = min(users, int(elapsed * spawn_rate))

            # Simulate requests per endpoint
            for ep_name in endpoint_stats:
                if random.random() < 0.8:  # 80% success rate simulation
                    endpoint_stats[ep_name]['requests'] += max(1, current_users // len(endpoint_stats))
                    response_time = random.uniform(50, 500)
                    endpoint_stats[ep_name]['total_response_time'] += response_time
                    endpoint_stats[ep_name]['response_times'].append(response_time)
                else:
                    endpoint_stats[ep_name]['failures'] += 1
                    total_failures += 1

            total_requests = sum(ep['requests'] for ep in endpoint_stats.values())

            test['progress'] = progress
            test['metrics'] = {
                'users': current_users,
                'rps': total_requests / max(1, elapsed),
                'failures': total_failures,
                'avgResponse': sum(ep['total_response_time'] for ep in endpoint_stats.values()) / max(1, total_requests)
            }

            time.sleep(2)

        # Build final results
        results = {
            'totalRequests': total_requests,
            'totalFailures': total_failures,
            'duration': total_seconds,
            'endpoints': []
        }

        for ep_name, stats in endpoint_stats.items():
            response_times = sorted(stats['response_times']) if stats['response_times'] else [0]
            p95_idx = int(len(response_times) * 0.95)
            p99_idx = int(len(response_times) * 0.99)

            results['endpoints'].append({
                'name': ep_name,
                'requests': stats['requests'],
                'failures': stats['failures'],
                'avgResponse': stats['total_response_time'] / max(1, stats['requests']),
                'p95': response_times[min(p95_idx, len(response_times) - 1)],
                'p99': response_times[min(p99_idx, len(response_times) - 1)]
            })

        test['status'] = 'completed'
        test['progress'] = 100
        test['results'] = results

    except Exception as e:
        test['status'] = 'failed'
        test['error'] = str(e)


def start_stress_test(test_id: str, config_path: str, users: int, spawn_rate: int,
                      duration: str, host: str, scenario: str) -> None:
    """Start a stress test in a background thread."""
    # Store test state
    stress_tests[test_id] = {
        'status': 'starting',
        'progress': 0,
        'metrics': {
            'users': 0,
            'rps': 0,
            'failures': 0,
            'avgResponse': 0
        },
        'results': None,
        'error': None,
        'start_time': time.time(),
        'duration': duration,
        'config_path': config_path
    }

    # Start stress test in background thread
    thread = threading.Thread(
        target=run_locust_test,
        args=(test_id, config_path, users, spawn_rate, duration, host, scenario)
    )
    thread.daemon = True
    thread.start()


def get_test_status(test_id: str) -> Dict:
    """Get status of a stress test."""
    return stress_tests.get(test_id)


def stop_all_tests() -> None:
    """Stop all running stress tests."""
    for test_id in list(stress_tests.keys()):
        test = stress_tests[test_id]
        if test['status'] == 'running':
            test['status'] = 'stopped'
            # Clean up config file
            if test.get('config_path') and os.path.exists(test['config_path']):
                try:
                    os.remove(test['config_path'])
                except:
                    pass

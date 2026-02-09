"""Flask routes for the AI Test Agent Web UI."""

import os
import json
from flask import Blueprint, render_template, request, jsonify, send_from_directory

from backend.runner import run_test_pipeline


main_bp = Blueprint('main', __name__)


# Get the output directory path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
SAVED_APIS_FILE = os.path.join(BASE_DIR, 'saved_apis.json')


def load_saved_apis():
    """Load saved APIs from JSON file."""
    if os.path.exists(SAVED_APIS_FILE):
        with open(SAVED_APIS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_apis_to_file(apis):
    """Save APIs to JSON file."""
    with open(SAVED_APIS_FILE, 'w') as f:
        json.dump(apis, f, indent=2)


@main_bp.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@main_bp.route('/run-test', methods=['POST'])
def run_test():
    """
    Execute the test pipeline with the provided cURL command.

    Expected JSON body:
        { "curl": "curl command here" }

    Returns:
        JSON with rule results and report links
    """
    data = request.get_json()

    if not data or 'curl' not in data:
        return jsonify({
            'success': False,
            'error': 'No cURL command provided'
        }), 400

    curl_command = data['curl'].strip()

    if not curl_command:
        return jsonify({
            'success': False,
            'error': 'cURL command is empty'
        }), 400

    # Run the test pipeline
    result = run_test_pipeline(curl_command)

    return jsonify(result)


@main_bp.route('/output/<path:filename>')
def serve_report(filename):
    """Serve generated reports from the output directory."""
    return send_from_directory(OUTPUT_DIR, filename)


# =============================================================================
# Saved APIs Endpoints
# =============================================================================

@main_bp.route('/api/saved-apis', methods=['GET'])
def get_saved_apis():
    """Get all saved APIs."""
    apis = load_saved_apis()
    return jsonify({
        'success': True,
        'apis': apis,
        'count': len(apis)
    })


@main_bp.route('/api/saved-apis', methods=['POST'])
def save_api():
    """
    Save a new API.

    Expected JSON body:
        { "name": "API Name", "curl": "curl command" }
    """
    data = request.get_json()

    if not data or 'name' not in data or 'curl' not in data:
        return jsonify({
            'success': False,
            'error': 'API name and curl command are required'
        }), 400

    api_name = data['name'].strip()
    api_curl = data['curl'].strip()

    if not api_name:
        return jsonify({
            'success': False,
            'error': 'API name is required'
        }), 400

    if not api_curl:
        return jsonify({
            'success': False,
            'error': 'cURL command is required'
        }), 400

    apis = load_saved_apis()

    # Check duplicate API Name
    if api_name in apis:
        return jsonify({
            'success': False,
            'error': f'API Name "{api_name}" already exists'
        }), 400

    # Check duplicate API Code
    for existing_name, existing_curl in apis.items():
        if existing_curl == api_curl:
            return jsonify({
                'success': False,
                'error': f'This API code already exists as "{existing_name}"'
            }), 400

    # Save the API
    apis[api_name] = api_curl
    save_apis_to_file(apis)

    return jsonify({
        'success': True,
        'message': f'API "{api_name}" saved successfully'
    })


@main_bp.route('/api/saved-apis/<api_name>', methods=['DELETE'])
def delete_api(api_name):
    """Delete a saved API by name."""
    apis = load_saved_apis()

    if api_name not in apis:
        return jsonify({
            'success': False,
            'error': f'API "{api_name}" not found'
        }), 404

    del apis[api_name]
    save_apis_to_file(apis)

    return jsonify({
        'success': True,
        'message': f'API "{api_name}" deleted successfully'
    })

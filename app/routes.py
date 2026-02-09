"""Flask routes for the AI Test Agent Web UI."""

import os
from flask import Blueprint, render_template, request, jsonify, send_from_directory

from backend.runner import run_test_pipeline


main_bp = Blueprint('main', __name__)


# Get the output directory path
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')


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

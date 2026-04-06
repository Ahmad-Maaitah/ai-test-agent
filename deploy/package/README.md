# AI Test Agent MVP

A fully functional AI Test Agent that automatically generates and executes pytest code from cURL commands.

## Features

- Input a cURL command via Web UI
- Automatically parse cURL into HTTP components
- Generate pytest code dynamically
- Execute 3 validation rules on API responses
- Generate HTML and JSON reports
- Display PASS/FAIL results in the Web UI

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python main.py
```

### 3. Open the Web UI

Navigate to: http://localhost:5000

### 4. Test an API

Enter a cURL command and click "Run Test". Example:

```bash
curl https://jsonplaceholder.typicode.com/posts/1
```

## Validation Rules

| Rule | Description |
|------|-------------|
| Status Code Rule | PASS if status code is 2xx |
| Response Exists Rule | PASS if response body is not empty |
| Valid JSON Rule | PASS if response body is valid JSON |

## Adding New Rules

1. Open `backend/rules.py`
2. Create a new function:

```python
def my_new_rule(response) -> dict:
    """Description of rule."""
    result = {
        'rule_name': 'My New Rule',
        'result': 'FAIL',
        'reason': None
    }

    # Your validation logic here
    if some_condition:
        result['result'] = 'PASS'
    else:
        result['reason'] = 'Explanation of failure'

    return result
```

3. Add to the RULES list:

```python
RULES = [
    status_code_rule,
    response_exists_rule,
    valid_json_rule,
    my_new_rule,  # Add here
]
```

No other changes required.

## Project Structure

```
project_root/
├── app/
│   ├── templates/      # HTML templates
│   │   └── index.html  # Main UI
│   ├── static/         # CSS/JS (if needed)
│   ├── routes.py       # Flask routes
│   └── __init__.py
├── backend/
│   ├── rules.py        # Validation rule functions
│   ├── runner.py       # Pipeline orchestration
│   ├── report.py       # Report generation
│   ├── utils.py        # cURL parser, helpers
│   └── __init__.py
├── tests/              # Dynamically generated pytest files
├── output/             # HTML & JSON reports
│   └── metadata/       # Execution metadata
├── main.py             # Entry point
├── requirements.txt    # Dependencies
└── README.md
```

## Example cURL Commands

Basic GET:
```bash
curl https://jsonplaceholder.typicode.com/posts/1
```

With headers:
```bash
curl https://api.example.com/data -H "Authorization: Bearer token123"
```

POST with JSON:
```bash
curl -X POST https://jsonplaceholder.typicode.com/posts \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "body": "Content", "userId": 1}'
```

## Configuration

- **Timeout**: 30 seconds (configurable in `backend/runner.py`)
- **SSL Verification**: Disabled by default for testing flexibility
- **Port**: 5000 (configurable in `main.py`)

## Output Files

After each test run:

- `tests/test_api_{timestamp}_{hash}.py` - Generated pytest file
- `output/report_{timestamp}_{hash}.html` - HTML report
- `output/report_{timestamp}_{hash}.json` - JSON report
- `output/metadata/execution_{timestamp}_{hash}.json` - Execution metadata

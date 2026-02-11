# AI Test Agent for API - Project Documentation

> **Single Source of Truth** for the API Testing Automation Platform
> Last Updated: 2026-02-11

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Functional Requirements](#3-functional-requirements)
4. [Business Rules](#4-business-rules)
5. [Validation Rules Engine](#5-validation-rules-engine)
6. [API Handling Logic](#6-api-handling-logic)
7. [Automation & Testing Rules](#7-automation--testing-rules)
8. [Edge Cases & Limitations](#8-edge-cases--limitations)
9. [Data Structures Reference](#9-data-structures-reference)
10. [API Endpoints Reference](#10-api-endpoints-reference)
11. [Future Enhancement Notes](#11-future-enhancement-notes)

---

## 1. Project Overview

### 1.1 Goal

**AI Test Agent for API** is a web-based platform for automated API testing and validation. It enables QA engineers and developers to:

- Input cURL commands and automatically parse them
- Execute HTTP requests against any API endpoint
- Define custom validation rules per API
- Run batch tests across multiple APIs
- Generate comprehensive HTML/JSON reports
- Track test history and results over time

### 1.2 Key Features

| Feature | Description |
|---------|-------------|
| **cURL Parser** | Automatically extracts method, URL, headers, and body from cURL commands |
| **Dynamic Rules Engine** | 7 configurable rule types for response validation |
| **Test-Before-Save** | Rules must pass validation before being saved |
| **Module Organization** | Group APIs into logical sections (modules) |
| **Drag-and-Drop** | Reorder modules and APIs visually |
| **Batch Execution** | Run multiple APIs at once with combined reports |
| **Report Generation** | Professional HTML reports with pass/fail details |
| **Allure Integration** | Generate Allure test reports (optional) |
| **Field Discovery** | Automatically extract response fields for rule creation |

### 1.3 Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.x, Flask 3.0+ |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| HTTP Client | Python `requests` library |
| Testing | pytest, pytest-html, pytest-json-report |
| Reporting | Custom HTML generator, Allure CLI (optional) |
| Data Storage | JSON file (data.json) |

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Browser                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   index.html (SPA)                       │    │
│  │  ┌─────────┐  ┌─────────────┐  ┌─────────────────────┐  │    │
│  │  │ Saved   │  │ Create API  │  │     Reports         │  │    │
│  │  │ APIs    │  │ (3-column)  │  │     History         │  │    │
│  │  └─────────┘  └─────────────┘  └─────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Flask Backend                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    routes.py                             │    │
│  │         (API Endpoints - 20+ routes)                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│        ┌─────────────────────┼─────────────────────┐            │
│        ▼                     ▼                     ▼            │
│  ┌───────────┐       ┌─────────────┐       ┌────────────┐       │
│  │  utils.py │       │  runner.py  │       │ report.py  │       │
│  │  - cURL   │       │  - Execute  │       │ - HTML     │       │
│  │    parser │       │    pipeline │       │ - JSON     │       │
│  └───────────┘       └─────────────┘       └────────────┘       │
│                              │                                   │
│                    ┌─────────┴─────────┐                        │
│                    ▼                   ▼                        │
│              ┌───────────┐      ┌───────────────┐               │
│              │ rules.py  │      │dynamic_rules.py│              │
│              │ (legacy)  │      │ (configurable) │              │
│              └───────────┘      └───────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      File System                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  data.json   │  │   tests/     │  │      output/         │   │
│  │  (sections,  │  │  (pytest     │  │  (reports, metadata, │   │
│  │   apis,      │  │   files)     │  │   allure-results)    │   │
│  │   reports)   │  │              │  │                      │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Directory Structure

```
API -AI Testing/
├── app/                          # Flask application
│   ├── __init__.py              # App factory
│   ├── routes.py                # API endpoints (746 lines)
│   └── templates/
│       └── index.html           # Web UI (4100+ lines)
│
├── backend/                     # Core business logic
│   ├── utils.py                 # cURL parser, utilities
│   ├── rules.py                 # Legacy validation rules
│   ├── dynamic_rules.py         # Configurable rule engine
│   ├── runner.py                # Test execution pipeline
│   └── report.py                # Report generation
│
├── tests/                       # Auto-generated pytest files
├── output/                      # Generated reports
│   ├── allure-results/          # Allure test data
│   ├── allure-report/           # Allure HTML reports
│   ├── metadata/                # Execution metadata
│   └── *.html, *.json           # Test reports
│
├── data.json                    # Persistent storage
├── main.py                      # Entry point
└── requirements.txt             # Dependencies
```

### 2.3 Data Flow

```
User Input (cURL)
       │
       ▼
┌──────────────────┐
│  Parse cURL      │  utils.parse_curl()
│  Extract: URL,   │
│  method, headers │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Execute HTTP    │  runner.execute_api_request()
│  Request         │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Apply Rules     │  dynamic_rules.apply_dynamic_rules()
│  - Status code   │  OR rules.apply_rules()
│  - Field checks  │
│  - Response time │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Generate Report │  report.generate_html_report()
│  - HTML          │  report.generate_json_report()
│  - JSON          │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Save Results    │  data.json (reports array)
│  Update API      │
│  lastStatus      │
└──────────────────┘
```

---

## 3. Functional Requirements

### 3.1 Module (Section) Management

| Requirement | Description |
|-------------|-------------|
| FR-1.1 | User can create modules with unique names |
| FR-1.2 | User can rename existing modules |
| FR-1.3 | User can delete modules (cascades to all APIs) |
| FR-1.4 | User can reorder modules via drag-and-drop |
| FR-1.5 | Modules display count of contained APIs |

### 3.2 API Management

| Requirement | Description |
|-------------|-------------|
| FR-2.1 | User can create APIs by pasting cURL commands |
| FR-2.2 | User can assign APIs to modules |
| FR-2.3 | User can edit API name and cURL command |
| FR-2.4 | User can move APIs between modules |
| FR-2.5 | User can delete APIs |
| FR-2.6 | User can reorder APIs within a module |
| FR-2.7 | APIs display last test status (PASS/FAIL) and HTTP code |

### 3.3 Rule Management

| Requirement | Description |
|-------------|-------------|
| FR-3.1 | User can add custom validation rules to APIs |
| FR-3.2 | Rules must be tested and pass before saving |
| FR-3.3 | User can enable/disable individual rules |
| FR-3.4 | User can delete rules from APIs |
| FR-3.5 | System provides 7 rule types with examples |
| FR-3.6 | User can search/filter response fields for rule creation |

### 3.4 Test Execution

| Requirement | Description |
|-------------|-------------|
| FR-4.1 | User can execute single API for testing rules |
| FR-4.2 | User can select multiple APIs for batch execution |
| FR-4.3 | System shows real-time execution progress |
| FR-4.4 | Results update API lastStatus/lastResult |
| FR-4.5 | System generates combined report for batch runs |

### 3.5 Reporting

| Requirement | Description |
|-------------|-------------|
| FR-5.1 | System generates HTML reports for each test run |
| FR-5.2 | Reports show pass/fail per rule with expected/actual |
| FR-5.3 | User can view historical reports |
| FR-5.4 | User can filter reports by module, result, or API |
| FR-5.5 | User can delete old reports |
| FR-5.6 | User can re-run failed APIs from a report |
| FR-5.7 | Reports are grouped by module with collapsible sections |

---

## 4. Business Rules

### 4.1 Naming Conventions

| Rule | Description |
|------|-------------|
| BR-1.1 | Module names must be unique (case-insensitive) |
| BR-1.2 | API names must be unique within a module |
| BR-1.3 | cURL commands should be unique across all APIs (warning only) |

### 4.2 Test Execution Rules

| Rule | Description |
|------|-------------|
| BR-2.1 | **Test-Before-Save**: New rules must pass test before being added |
| BR-2.2 | APIs without custom rules use legacy 4-rule validation |
| BR-2.3 | APIs with custom rules only use those custom rules |
| BR-2.4 | API requests have 30-second timeout |
| BR-2.5 | HTTP errors (connection, timeout) mark API as FAIL |

### 4.3 Result Calculation

| Rule | Description |
|------|-------------|
| BR-3.1 | **Overall Result** = All rules must PASS |
| BR-3.2 | **Structural Result** = All structural rules must PASS |
| BR-3.3 | **Functional Result** = All functional rules must PASS |
| BR-3.4 | One failing rule = entire API marked as FAIL |

### 4.4 Report Retention

| Rule | Description |
|------|-------------|
| BR-4.1 | Maximum 50 reports stored in data.json |
| BR-4.2 | Old reports auto-removed when limit exceeded |
| BR-4.3 | Report HTML files persist in output/ directory |

---

## 5. Validation Rules Engine

### 5.1 Rule Types Overview

| Type | Name | Category | Requires Field | Description |
|------|------|----------|----------------|-------------|
| `status_code` | Status Code (e.g., 200, 404, 500) | functional | No | Check HTTP status code equals expected |
| `response_time` | Response Time (e.g., < 2000ms) | performance | No | Check response time within threshold |
| `field_exists` | Field Exists (e.g., data.id exists) | structural | Yes | Verify field present in response |
| `field_not_null` | Field Not Null (e.g., data.id != null) | structural | Yes | Check field has non-empty value |
| `field_type` | Field Type (e.g., data.count is number) | structural | Yes | Validate field data type |
| `success_flag` | Boolean Check (e.g., success == true) | functional | Yes | Check boolean field value |
| `custom_expression` | Custom Compare (e.g., data.status == 'active') | functional | Yes | Custom comparison with operators |

### 5.2 Rule Configuration Schema

```json
{
  "id": "rule-{uuid}",
  "type": "status_code|response_time|field_exists|field_not_null|field_type|success_flag|custom_expression",
  "field": "path.to.field",
  "enabled": true,
  "config": {
    // Type-specific configuration
  }
}
```

### 5.3 Rule Type Details

#### 5.3.1 Status Code
```json
{
  "type": "status_code",
  "config": {
    "expectedStatus": 200
  }
}
```
- **Pass**: Response status code equals expected
- **Fail**: Status code mismatch

#### 5.3.2 Response Time
```json
{
  "type": "response_time",
  "config": {
    "maxMs": 2000
  }
}
```
- **Pass**: Response time ≤ maxMs
- **Fail**: Response time exceeds threshold

#### 5.3.3 Field Exists
```json
{
  "type": "field_exists",
  "field": "data.user.email"
}
```
- **Pass**: Field path exists in response
- **Fail**: Field not found

#### 5.3.4 Field Not Null
```json
{
  "type": "field_not_null",
  "field": "data.token"
}
```
- **Pass**: Field exists AND is not null/empty
- **Fail**: Field missing, null, or empty string/array/object

#### 5.3.5 Field Type
```json
{
  "type": "field_type",
  "field": "data.items",
  "config": {
    "expectedType": "array"
  }
}
```
- **Options**: string, number, boolean, array, object
- **Pass**: Field type matches expected
- **Fail**: Type mismatch

#### 5.3.6 Success Flag (Boolean Check)
```json
{
  "type": "success_flag",
  "field": "data.isActive",
  "config": {
    "expectedValue": true
  }
}
```
- **Pass**: Boolean field equals expected value
- **Fail**: Value mismatch or field not found

#### 5.3.7 Custom Expression
```json
{
  "type": "custom_expression",
  "field": "data.role",
  "config": {
    "operator": "contains",
    "expectedValue": "admin"
  }
}
```
- **Operators**:
  - `equals`: Exact string match
  - `not_equals`: String does not match
  - `contains`: Substring match
  - `greater_than`: Numeric comparison (>)
  - `less_than`: Numeric comparison (<)
  - `regex`: Regular expression match

### 5.4 Field Path Notation

Fields are accessed using dot notation with array index support:

| Path | Description |
|------|-------------|
| `id` | Root-level field |
| `data.user` | Nested object field |
| `data.users.0.name` | First array element's name |
| `result.items.0.details.id` | Deep nested path |

### 5.5 Legacy Rules (No Custom Rules)

When an API has no custom rules, these 4 rules apply:

1. **Status Code Rule** (functional)
   - Pass: 200-299 status code

2. **Response Exists Rule** (structural)
   - Pass: Non-empty response body

3. **Valid JSON Rule** (structural)
   - Pass: Response is valid JSON

4. **No Error Field Rule** (functional)
   - Pass: No 'error' or 'message' fields (on 4xx/5xx)

---

## 6. API Handling Logic

### 6.1 cURL Parsing

The `utils.parse_curl()` function extracts:

| Component | cURL Flag | Example |
|-----------|-----------|---------|
| Method | `-X`, `--request` | `-X POST` |
| URL | (positional) | `'https://api.example.com'` |
| Headers | `-H`, `--header` | `-H 'Authorization: Bearer xxx'` |
| Body | `-d`, `--data`, `--data-raw` | `-d '{"key":"value"}'` |
| JSON Body | `--json` | `--json '{"key":"value"}'` |
| SSL Verify | `-k`, `--insecure` | `-k` (disables SSL verification) |
| User Agent | `-A`, `--user-agent` | `-A 'MyApp/1.0'` |

### 6.2 Request Execution

```python
# Configuration
timeout = 30  # seconds
verify_ssl = True  # unless -k flag

# Execution
response = requests.request(
    method=parsed['method'],
    url=parsed['url'],
    headers=parsed['headers'],
    data=parsed['data'],
    timeout=timeout,
    verify=parsed['verify_ssl']
)
```

### 6.3 Response Processing

1. **Capture timing**: Record response time in milliseconds
2. **Parse JSON**: Attempt to parse response body as JSON
3. **Extract fields**: Recursively extract all field paths (max depth: 5)
4. **Apply rules**: Evaluate each rule against response
5. **Generate results**: Create rule result objects with pass/fail

### 6.4 Error Handling

| Error Type | Behavior |
|------------|----------|
| Connection Error | FAIL with "Connection error" message |
| Timeout | FAIL with "Request timed out" message |
| Invalid JSON | Rule "valid_json" fails, others may still run |
| SSL Error | FAIL with SSL error details |
| HTTP 4xx/5xx | Captured; rules determine pass/fail |

---

## 7. Automation & Testing Rules

### 7.1 Test Pipeline

```
run_test_pipeline(curl_command, api_name, custom_rules)
    │
    ├── 1. Parse cURL command
    │
    ├── 2. Execute HTTP request (30s timeout)
    │
    ├── 3. Apply validation rules
    │       ├── Custom rules (if defined)
    │       └── Legacy rules (if no custom)
    │
    ├── 4. Generate pytest code
    │
    ├── 5. Run pytest with plugins
    │       ├── pytest-html
    │       ├── pytest-json-report
    │       └── allure (if available)
    │
    ├── 6. Generate HTML report
    │
    ├── 7. Generate JSON report
    │
    ├── 8. Save execution metadata
    │
    └── 9. Return results
```

### 7.2 Generated Pytest Structure

```python
# tests/test_api_{timestamp}_{hash}.py

API_CONFIG = {
    'url': 'https://...',
    'method': 'GET',
    'headers': {...},
    'data': {...}
}

@pytest.fixture
def api_response():
    response = requests.request(...)
    return response

class TestAPIValidation:
    def test_status_code(self, api_response):
        assert 200 <= api_response.status_code < 300

    def test_response_exists(self, api_response):
        assert len(api_response.text) > 0

    def test_valid_json(self, api_response):
        api_response.json()  # Raises if invalid

    def test_no_error_field(self, api_response):
        # Check for error fields
```

### 7.3 Report Generation

#### HTML Report Features
- Professional gradient header
- Summary cards (total, passed, failed)
- API info section (name, status, time)
- Rule results table with icons
- Expected vs Actual comparison
- Color-coded pass/fail

#### Run Report Features (Batch)
- Module grouping
- Collapsible sections
- Per-module statistics
- Individual API cards
- Toggle all expand/collapse

---

## 8. Edge Cases & Limitations

### 8.1 Known Limitations

| Limitation | Description | Workaround |
|------------|-------------|------------|
| No Authentication UI | Cannot configure OAuth flows in UI | Include auth tokens in cURL headers |
| Single File Storage | data.json can grow large | Periodic cleanup of old reports |
| No Parallel Execution | APIs run sequentially | Expected behavior for consistency |
| 30s Timeout Fixed | Cannot configure per-API timeout | Modify runner.py if needed |
| Max Field Depth: 5 | Deep nested fields may not extract | Manually type field path |
| No Variables | Cannot use environment variables | Hardcode values in cURL |

### 8.2 Edge Cases Handled

| Case | Behavior |
|------|----------|
| Empty cURL | Error: "No URL found in cURL command" |
| Invalid JSON response | `valid_json` rule fails, others continue |
| Missing field in rule | Rule fails with "Field not found" |
| Null field value | `field_not_null` fails, `field_exists` passes |
| Empty array/object | `field_not_null` fails |
| Non-numeric comparison | `greater_than`/`less_than` fails gracefully |
| Invalid regex | Rule fails with "Invalid regex" message |
| Network unreachable | API marked FAIL with connection error |
| SSL certificate error | Fails unless `-k` flag used |

### 8.3 Browser Compatibility

- **Tested**: Chrome, Firefox, Safari (modern versions)
- **Not Tested**: Internet Explorer, Edge Legacy
- **Requirements**: JavaScript enabled, modern CSS support

### 8.4 Concurrency Considerations

- **Single User Design**: No multi-user conflict handling
- **File Locking**: No file locking on data.json
- **Race Conditions**: Possible if multiple tabs modify data

---

## 9. Data Structures Reference

### 9.1 Section (Module)

```json
{
  "id": "section-{8-char-uuid}",
  "name": "Module Name",
  "order": 1,
  "apis": [/* API objects */]
}
```

### 9.2 API

```json
{
  "id": "api-{8-char-uuid}",
  "name": "API Display Name",
  "curl": "curl --location 'https://...' --header '...'",
  "order": 1,
  "lastStatus": 200,
  "lastResult": "PASS",
  "customRules": [/* Rule objects */]
}
```

### 9.3 Rule

```json
{
  "id": "rule-{9-char-uuid}",
  "type": "field_exists",
  "field": "data.user.id",
  "enabled": true,
  "config": {},
  "testResult": {
    "result": "PASS",
    "expected": "'data.user.id' exists",
    "actual": "Found: \"12345\""
  }
}
```

### 9.4 Report

```json
{
  "runId": "run-{8-char-uuid}",
  "date": "2026-02-11T12:00:00.000000",
  "totalApis": 5,
  "passed": 4,
  "failed": 1,
  "htmlReport": "run_report_run-xxx.html",
  "results": [/* API Result objects */]
}
```

### 9.5 API Result

```json
{
  "apiId": "api-xxx",
  "apiName": "API Name",
  "section": "Module Name",
  "statusCode": 200,
  "result": "PASS",
  "structuralResult": "PASS",
  "functionalResult": "PASS",
  "executionTime": "523ms",
  "errorMessage": null,
  "ruleResults": [/* Rule Result objects */],
  "reportPaths": {
    "html": "report_xxx.html",
    "json": "report_xxx.json"
  }
}
```

### 9.6 Rule Result

```json
{
  "rule_id": "rule-xxx",
  "rule_name": "Field Exists (e.g., data.id exists)",
  "rule_type": "structural",
  "field": "data.user.id",
  "result": "PASS",
  "reason": null,
  "expected": "'data.user.id' exists",
  "actual": "Found: \"12345\""
}
```

---

## 10. API Endpoints Reference

### 10.1 Section Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sections` | Get all sections with APIs |
| POST | `/api/sections` | Create new section |
| PUT | `/api/sections/<id>` | Update section name |
| DELETE | `/api/sections/<id>` | Delete section and APIs |
| POST | `/api/sections/reorder` | Reorder sections |

### 10.2 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sections/<id>/apis` | Create API in section |
| PUT | `/api/apis/<id>` | Update API |
| DELETE | `/api/apis/<id>` | Delete API |
| POST | `/api/apis/<id>/move` | Move API to section |
| POST | `/api/sections/<id>/apis/reorder` | Reorder APIs |

### 10.3 Test Execution Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/run` | Execute selected APIs |
| POST | `/api/run-single` | Test single API |
| POST | `/api/execute-curl` | Parse and execute cURL |
| POST | `/api/test-rules` | Test rules without saving |
| POST | `/api/validate-rules` | Validate rule config |

### 10.4 Rule Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rule-types` | Get rule type definitions |

### 10.5 Report Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports` | Get all reports (with filters) |
| GET | `/api/reports/<id>` | Get report by ID |
| GET | `/api/reports/<id>/export` | Export report as JSON |
| DELETE | `/api/reports/<id>` | Delete report |
| POST | `/api/reports/<id>/rerun-failed` | Re-run failed APIs |

### 10.6 Static File Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main web UI |
| GET | `/output/<filename>` | Serve report files |
| GET | `/allure-report/<filename>` | Serve Allure reports |

---

## 11. Future Enhancement Notes

### 11.1 High Priority

| Enhancement | Description |
|-------------|-------------|
| **Environment Variables** | Support `{{VAR}}` syntax in cURL commands |
| **Authentication Profiles** | Store and reuse OAuth/API key configs |
| **Scheduled Runs** | Cron-like scheduling for automated testing |
| **Email Notifications** | Send alerts on test failures |
| **Database Storage** | Migrate from JSON to SQLite/PostgreSQL |

### 11.2 Medium Priority

| Enhancement | Description |
|-------------|-------------|
| **Import/Export** | Bulk import APIs from Postman/Swagger |
| **Team Collaboration** | Multi-user support with permissions |
| **API Chaining** | Use response from one API in another |
| **Response Assertions** | JSON schema validation |
| **Performance Trends** | Track response time over multiple runs |

### 11.3 Low Priority

| Enhancement | Description |
|-------------|-------------|
| **Dark Mode** | UI theme toggle |
| **Keyboard Shortcuts** | Power user navigation |
| **API Versioning** | Track changes to API definitions |
| **Mock Server** | Generate mock responses for testing |
| **CI/CD Integration** | GitHub Actions / Jenkins plugins |

### 11.4 Technical Debt

| Item | Description |
|------|-------------|
| **Code Splitting** | Split index.html into components |
| **TypeScript** | Add type safety to frontend |
| **Unit Tests** | Add pytest tests for backend modules |
| **API Documentation** | Generate OpenAPI/Swagger spec |
| **Error Logging** | Structured logging with levels |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-11 | AI Assistant | Initial documentation |

---

*This document serves as the single source of truth for the AI Test Agent for API project. Update this document when making significant changes to the system.*

# API Automation Testing Platform - Team Documentation

**OpenSooq API Testing & Validation Platform**

---

## 📋 What is This Project?

**API Automation Testing Platform** is a comprehensive web-based tool for automated API testing and validation. It helps QA engineers and developers:

- **Test APIs automatically** - No manual work needed
- **Validate responses** - Check status codes, response times, data fields
- **Organize tests** - Group APIs into modules/sections
- **Generate reports** - Professional HTML reports with pass/fail details
- **Track history** - See all past test results
- **Save time** - Run multiple APIs in one click

Think of it as **Postman + Automated Testing + Reports** all in one platform.

---

## 🎯 Key Benefits

| Benefit | Description |
|---------|-------------|
| **Zero Coding Required** | Just paste cURL commands and add validation rules |
| **Instant Testing** | Test APIs with one click |
| **Smart Validation** | 7 types of validation rules (status, response time, fields, etc.) |
| **Batch Execution** | Run all APIs in a module at once |
| **Beautiful Reports** | Professional HTML reports with graphs and statistics |
| **Test History** | Track all test results over time |

---

## 🏗️ Project Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Web Interface (SPA)                    │
│              http://localhost:5001                       │
│  ┌──────────┐  ┌───────────┐  ┌─────────┐  ┌─────────┐ │
│  │Dashboard │  │ Saved     │  │ Create  │  │Reports  │ │
│  │          │  │ APIs      │  │ API     │  │         │ │
│  └──────────┘  └───────────┘  └─────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  Flask Backend (Python)                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │              API Routes Handler                   │   │
│  │  • Parse cURL commands                           │   │
│  │  • Execute HTTP requests                         │   │
│  │  • Validate responses                            │   │
│  │  • Generate test reports                         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  Your API Endpoints                      │
│              (OpenSooq Backend APIs)                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Reports & Test Results                      │
│  • HTML Reports (output/report_*.html)                  │
│  • JSON Reports (pytest format)                         │
│  • Allure Reports (optional)                            │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### Starting the Platform

```bash
cd "/Users/Admin/Documents/AI/New API testing/API -AI Testing"
python3 main.py
```

✅ Platform will be available at: **http://localhost:5001**

---

## 📊 Main Features

### 1. Dashboard
**What you see:**
- Total APIs count
- Recent test results
- Quick stats
- Latest report preview

**Use it for:** Quick overview of your testing status

---

### 2. Saved APIs
**What you can do:**
- View all saved APIs organized by sections/modules
- Run individual APIs
- Run entire sections
- Edit existing APIs
- Delete APIs
- Drag & drop to reorder

**Best for:** Managing and organizing your API tests

---

### 3. Create API
**This is where the magic happens!**

#### Three-Column Layout:

**Left Column: Request Builder**
1. **Paste cURL command** (or build manually)
2. **Name your API** (e.g., "Login API - Valid User")
3. **Select section/module**
4. **Execute** to test the request

**Middle Column: Rules Builder**
1. **Add validation rules** (7 types available)
2. **Test rules** against actual response
3. **See live validation** (✓ Pass / ✗ Fail)
4. **Auto-discover fields** from response

**Right Column: Response Viewer**
1. **See API response** in real-time
2. **Response time & status**
3. **Available fields** for validation
4. **Search fields** easily

---

### 4. Reports
**What you get:**
- List of all test reports
- Filter by module or result (Pass/Fail)
- View detailed HTML reports
- Open Allure reports

**Report includes:**
- Test summary (total, passed, failed)
- Response times
- Individual API results
- Error details
- Timestamps

---

### 5. Variables
**Manage reusable variables:**

**Example use cases:**
- Store auth tokens: `{{authToken}}`
- Save user IDs: `{{userId}}`
- Reuse common values: `{{baseUrl}}`

**How to use:**
1. Add variable with `{{variableName}}` syntax
2. Use in any API request
3. Update once, applies everywhere

---

## 🧪 Validation Rules Explained

### 1. Status Code ✅
**What it does:** Checks HTTP status code

**Example:**
- Expected: `200`
- Use for: Verify successful response

---

### 2. Response Time ⏱️
**What it does:** Checks API speed

**Example:**
- Expected: `< 2000ms`
- Use for: Performance validation

---

### 3. Field Exists 🔍
**What it does:** Verify field is present in response

**Example:**
- Field: `data.user.id`
- Use for: Structure validation

---

### 4. Field Not Null ❌
**What it does:** Ensure field has a value

**Example:**
- Field: `data.user.name`
- Use for: Data completeness

---

### 5. Field Type 🏷️
**What it does:** Validate data type

**Example:**
- Field: `data.count` = `number`
- Use for: Type safety checks

---

### 6. Boolean Check ✔️
**What it does:** Check true/false fields

**Example:**
- Field: `success` = `true`
- Use for: Success flags

---

### 7. Custom Expression 🔧
**What it does:** Custom comparisons

**Example:**
- `data.status == 'active'`
- `data.count > 10`
- Use for: Complex validations

---

## 📝 How to Create Your First Test

### Step-by-Step Guide

#### Step 1: Get Your cURL Command
From browser DevTools or Postman, copy the cURL command:

```bash
curl 'https://api.opensooq.com/v1/users/login' \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@opensooq.com","password":"pass123"}'
```

#### Step 2: Open Create API Page
1. Go to http://localhost:5001
2. Click **"Create API"** tab

#### Step 3: Paste cURL
1. Paste cURL in the text area
2. Click **"Parse cURL"**
3. ✅ Request details auto-filled

#### Step 4: Name Your API
1. Enter name: "Login API - Valid User"
2. Select section: "Authentication"

#### Step 5: Test the Request
1. Click **"Execute Request"**
2. ✅ See response in right panel

#### Step 6: Add Validation Rules
1. Click **"+ Add Rule"**
2. Select rule type: **Status Code**
3. Expected value: `200`
4. Click **"Test Rule"**
5. ✅ Rule passes!

#### Step 7: Add More Rules (Optional)
- Response time < 2000ms
- Field `data.token` exists
- Field `success` = true

#### Step 8: Validate All Rules
1. Click **"Test All Rules"**
2. ✅ All rules pass!

#### Step 9: Save API
1. Click **"Save API"**
2. ✅ API saved to your section

#### Step 10: Run Anytime
1. Go to **"Saved APIs"** tab
2. Click **"Run"** next to your API
3. ✅ Instant test results!

---

## 🎯 Common Use Cases

### Use Case 1: Daily Smoke Tests
**Scenario:** Test critical APIs every morning

**Steps:**
1. Create "Critical APIs" section
2. Add all critical endpoints
3. Click **"Run Section"**
4. Review generated report
5. Share with team

---

### Use Case 2: Regression Testing
**Scenario:** Ensure no APIs broke after deployment

**Steps:**
1. Run all APIs: Click **"Run All"**
2. Check report for failures
3. Fix any broken APIs
4. Re-run until all pass

---

### Use Case 3: API Documentation
**Scenario:** Document expected API behavior

**Steps:**
1. Create API with validation rules
2. Rules serve as documentation
3. Future tests verify behavior matches

---

### Use Case 4: New Feature Validation
**Scenario:** Test new API endpoint

**Steps:**
1. Get cURL from development
2. Create test API
3. Add validation rules
4. Run after each code change
5. Ensure consistent behavior

---

## 📊 Understanding Reports

### HTML Report Sections

#### 1. Summary
- **Total APIs tested**
- **Passed count** (green)
- **Failed count** (red)
- **Total duration**

#### 2. Individual Results
For each API:
- Name and module
- Status (✓ Pass / ✗ Fail)
- Response time
- Status code
- Rule validations
- Error messages (if failed)

#### 3. Statistics
- Average response time
- Success rate percentage
- Slowest APIs
- Failed APIs list

---

## 🛠️ Best Practices

### ✅ DO

1. **Organize by modules** - Group related APIs together
2. **Use descriptive names** - "Login - Valid Credentials" not "Test1"
3. **Add multiple rules** - More validation = better quality
4. **Test before saving** - Always validate rules first
5. **Review reports** - Check test results regularly
6. **Use variables** - For auth tokens, IDs, etc.
7. **Document expected behavior** - Rules serve as documentation

### ❌ DON'T

1. **Don't skip validation** - Always add at least basic rules
2. **Don't save without testing** - Platform enforces this anyway
3. **Don't use hardcoded values** - Use variables for dynamic data
4. **Don't ignore failures** - Investigate and fix
5. **Don't delete sections with APIs** - Move APIs first

---

## 🎓 Tips & Tricks

### Tip 1: Quick Field Discovery
After executing request:
1. Look at right panel **"Available Fields"**
2. Click any field to copy path
3. Use in validation rules

### Tip 2: Reuse Common Rules
Common rule combinations:
- Status 200 + Response time < 2000ms
- Field exists + Field not null
- Boolean check + Status code

### Tip 3: Batch Testing
Test entire modules:
1. Go to **"Saved APIs"**
2. Click section name
3. Click **"Run Section"**
4. Get one report for all APIs

### Tip 4: Variable Usage
Store extracted values:
```
{{authToken}}     - From login response
{{userId}}        - From user creation
{{orderId}}       - From order creation
```

Use in subsequent requests:
```
Authorization: Bearer {{authToken}}
/users/{{userId}}/orders
```

---

## 🔧 Troubleshooting

### Problem: "API not saving"
**Reason:** Rules must pass validation first
**Solution:** Click "Test All Rules" and ensure all pass

### Problem: "CORS error"
**Reason:** API doesn't allow browser requests
**Solution:** This is expected - the backend handles it

### Problem: "Connection refused"
**Reason:** Target API is down
**Solution:** Check API is running and accessible

### Problem: "Can't parse cURL"
**Reason:** Invalid cURL format
**Solution:** Get cURL directly from browser DevTools

### Problem: "Rule always fails"
**Reason:** Response structure doesn't match
**Solution:** Check actual response, adjust field path

---

## 📚 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + E` | Execute request |
| `Ctrl + S` | Save API (after validation) |
| `Ctrl + T` | Test all rules |

---

## 🎯 Success Criteria

### Quality Checklist for APIs

- [ ] API has descriptive name
- [ ] Assigned to correct section/module
- [ ] Has at least 3 validation rules
- [ ] Status code rule added
- [ ] Response time rule added (< 2000ms)
- [ ] Critical fields validated
- [ ] All rules pass before saving
- [ ] Tested at least once after saving

---

## 📊 Sample Validation Rules

### Example 1: Login API
```
✓ Status Code = 200
✓ Response Time < 1500ms
✓ Field Exists: data.token
✓ Field Not Null: data.token
✓ Field Exists: data.user.id
✓ Boolean Check: success = true
```

### Example 2: Get Users API
```
✓ Status Code = 200
✓ Response Time < 2000ms
✓ Field Exists: data.users
✓ Field Type: data.users = array
✓ Field Exists: data.total
✓ Field Type: data.total = number
```

### Example 3: Create Order API
```
✓ Status Code = 201
✓ Response Time < 3000ms
✓ Field Exists: data.orderId
✓ Field Not Null: data.orderId
✓ Custom Expression: data.status == 'pending'
✓ Field Type: data.total = number
```

---

## 🆘 Getting Help

### Team Contacts
- **QA Team Lead**: [Contact]
- **Backend Team**: [Contact]
- **DevOps**: [Contact]

### Resources
- **Project Documentation**: `PROJECT_DOCUMENTATION.md`
- **API Reference**: See Reports section
- **Flask Documentation**: https://flask.palletsprojects.com/

---

## 📋 Quick Reference

### File Locations

```
Project Root: /Users/Admin/Documents/AI/New API testing/API -AI Testing/

├── main.py                 # Start the application
├── data.json              # All saved APIs and sections
├── app/
│   ├── templates/
│   │   └── index.html     # Web interface
│   └── routes.py          # API endpoints
├── backend/
│   ├── runner.py          # Test execution
│   ├── rules.py           # Validation rules
│   └── report.py          # Report generation
└── output/                # Generated reports
    └── report_*.html      # Test reports
```

### Common Commands

```bash
# Start the platform
python3 main.py

# Access web interface
http://localhost:5001

# View reports
open output/report_*.html

# Check data
cat data.json
```

---

## 🚀 Workflow Example

### Complete Testing Workflow

#### Morning Routine (5 minutes)
1. Open platform: http://localhost:5001
2. Go to "Saved APIs"
3. Click "Run All APIs"
4. Review report
5. Note any failures

#### Adding New API (10 minutes)
1. Get cURL from DevTools
2. Go to "Create API" tab
3. Paste cURL, parse it
4. Add API name and section
5. Execute to test
6. Add validation rules (at least 3)
7. Test all rules
8. Save API

#### Weekly Review (15 minutes)
1. Go to "Reports" tab
2. Review last 10 reports
3. Check for trends
4. Note slow APIs
5. Update validation rules if needed

---

## 🎓 Training Plan

### Week 1: Basics
- [ ] Understand what the platform does
- [ ] Create first API from cURL
- [ ] Add basic validation rules
- [ ] Run individual API test
- [ ] View generated report

### Week 2: Intermediate
- [ ] Organize APIs into sections
- [ ] Use all 7 rule types
- [ ] Run batch tests (section)
- [ ] Use variables
- [ ] Interpret reports effectively

### Week 3: Advanced
- [ ] Create complex validation rules
- [ ] Chain API calls with variables
- [ ] Run complete regression tests
- [ ] Share reports with team
- [ ] Optimize slow APIs

---

## 📈 Metrics to Track

| Metric | What to Track | Goal |
|--------|---------------|------|
| **Test Coverage** | Number of APIs tested | > 80% of endpoints |
| **Success Rate** | % of passing tests | > 95% |
| **Response Time** | Average API response | < 1000ms |
| **Test Frequency** | How often tests run | Daily minimum |
| **Failed Tests** | Number of failures | < 5% |

---

## 🔐 Security Best Practices

### Important Rules

1. **Never commit credentials** to data.json
2. **Use environment variables** for sensitive data
3. **Don't test production** without approval
4. **Limit API access** to authorized users only
5. **Review data.json** before sharing

### Variable Security

```bash
# Good: Use variables for sensitive data
Authorization: Bearer {{authToken}}

# Bad: Hardcoded credentials
Authorization: Bearer abc123xyz456
```

---

## ✨ Platform Features

### Built-in Features

✅ **Auto cURL Parser** - Paste and parse instantly
✅ **Live Request Execution** - Test before saving
✅ **7 Validation Rule Types** - Complete coverage
✅ **Field Auto-Discovery** - Extract from responses
✅ **Drag & Drop Reordering** - Organize easily
✅ **Batch Execution** - Run multiple APIs
✅ **HTML Reports** - Professional output
✅ **Test History** - Track all results
✅ **Variable Management** - Reusable values
✅ **Section Organization** - Modular structure

---

## 🎯 Next Steps

1. **Open the platform** (http://localhost:5001)
2. **Explore the dashboard**
3. **Create your first test API**
4. **Add validation rules**
5. **Run the test**
6. **Review the report**
7. **Share with your team**

---

**Questions?** Check PROJECT_DOCUMENTATION.md or contact the QA team.

**OpenSooq API Automation Platform** - Testing Made Simple 🚀

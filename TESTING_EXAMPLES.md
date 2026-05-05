# Testing Examples - Real Use Cases

Complete examples showing how to use all testing tools for the Luxury Travel Agent.

## 🚀 Example 1: Quick Development Testing

Test your changes during development:

```bash
# Install dependencies (first time only)
pip install -r requirements.txt

# Run all tests quickly (< 1 second)
pytest

# Output:
# ============================== 43 passed in 0.67s ==============================
```

## 🔍 Example 2: Check Code Coverage

Ensure your code changes maintain high coverage:

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# View the report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# Terminal output shows:
# Name          Stmts  Miss  Cover  Missing
# ────────────────────────────────────────
# src/flights.py   22    2    91%   26-29
# src/hotels.py    26    3    88%   26-29
# TOTAL           292   19    93%
```

## ⚡ Example 3: Performance Testing

Verify all operations meet performance targets:

```bash
# Run performance benchmarks
pytest tests/test_performance.py -v

# Output:
# test_flight_search_performance PASSED      [ 20%]
# test_hotel_search_performance PASSED       [ 40%]
# test_cpp_calculation_performance PASSED    [ 60%]
# test_ranking_performance PASSED            [ 80%]
# test_database_query_performance PASSED     [100%]
```

## 🧪 Example 4: API Integration Testing

Test all API endpoints:

```bash
# Terminal 1: Start Flask server
python -m src.app
# Output: Running on http://localhost:5000

# Terminal 2: Run integration tests
pytest tests/test_integration.py -v

# Output:
# test_index_page_loads PASSED           [ 7%]
# test_health_endpoint PASSED            [14%]
# test_deals_analyze_success PASSED      [21%]
# test_flight_search_endpoint PASSED     [35%]
# test_hotel_search_endpoint PASSED      [50%]
# test_save_deal_success PASSED          [64%]
# test_404_endpoint PASSED               [100%]
# ============================== 13 passed in 0.89s ==============================
```

## 📊 Example 5: Load Testing - Interactive Web UI

Simulate real user traffic with visual dashboard:

```bash
# Terminal 1: Start Flask server
python -m src.app

# Terminal 2: Start Locust load test
locust -f locustfile.py --host=http://localhost:5000

# Output:
# [2026-05-05 12:00:00] Starting web interface at http://0.0.0.0:8089
# [2026-05-05 12:00:00] Starting Locust 2.16.1
```

**In browser, visit: http://localhost:8089**

**Set parameters:**
- Number of users: 50
- Spawn rate: 5 users/sec
- Duration: 5 minutes

**Visual metrics:**
- Real-time request throughput
- Response time graph
- Success/failure rates
- Requests per endpoint

## 🔥 Example 6: Load Testing - Heavy Stress Test

Automated heavy load test (500 concurrent users):

```bash
# Terminal 1: Start Flask server
python -m src.app

# Terminal 2: Run heavy load test
locust -f locustfile.py \
  --host=http://localhost:5000 \
  --users 500 \
  --spawn-rate 50 \
  --run-time 300s \
  --headless

# Output:
# Type     Name                     # reqs    # fails |    Avg     Min     Max  Median
# ─────────────────────────────────────────────────────────────────────────────────
# POST     /api/deals/analyze        15000        0 |      8       1      45       7
# GET      /api/flights/search       10000        0 |      5       0      22       4
# GET      /api/hotels/search        10000        0 |      5       0      20       4
# POST     /api/deals/save            5000        0 |      3       0      12       3
# GET      /api/health               5000        0 |      2       0       8       2
# ─────────────────────────────────────────────────────────────────────────────────
# Total                             45000        0 |      6       0      45       5
#
# Total Request Rate: 150 req/s
# Total Response Rate: 150 req/s
# Average Response Time: 6ms
# Min Response Time: 0ms
# Max Response Time: 45ms
# 99th percentile: 15ms
```

## 📈 Example 7: Spike Test (Sudden Traffic)

Test how the system handles sudden traffic spikes:

```bash
locust -f locustfile.py \
  --host=http://localhost:5000 \
  --users 1000 \
  --spawn-rate 100 \
  --run-time 60s \
  --headless

# Simulates:
# - 100 new users joining every second
# - Total of 1000 concurrent users in 10 seconds
# - Running for 60 seconds total

# Expected results:
# ✅ Should handle spike without degradation
# ✅ Response times should stay <100ms
# ✅ 0% failure rate
```

## 🔧 Example 8: Specific Test Execution

Run individual test suites:

```bash
# Run only flight tests
pytest tests/test_flights.py -v

# Run only hotel tests
pytest tests/test_hotels.py -v

# Run only database tests
pytest tests/test_database.py -v

# Run only agent tests
pytest tests/test_agent.py -v

# Run only a specific test
pytest tests/test_flights.py::TestFlightSearchEngine::test_calculate_cpp -v
```

## 🎯 Example 9: Parallel Testing

Speed up tests by running them in parallel:

```bash
# Run with 4 workers (4x faster)
pytest -n 4

# Output:
# ============================== 43 passed in 0.17s ==============================
# (Much faster than 0.67s serial)

# Use more workers for even faster execution
pytest -n auto  # Uses number of CPU cores
```

## 📋 Example 10: Verbose Testing with Details

Get maximum detail about test execution:

```bash
# Show print statements
pytest -s

# Show very verbose output
pytest -vv

# Show test timing
pytest --durations=10

# Show slowest 10 tests:
# test_chat_endpoint_no_api_key 0.05s
# test_integration.py::test_deals_analyze_cpp_values 0.04s
# test_agent.py::test_build_system_prompt 0.03s
```

## 🐛 Example 11: Debug Failed Tests

When a test fails, get maximum debugging info:

```bash
# Stop at first failure
pytest -x

# Show full traceback
pytest -vv --tb=long

# Drop into Python debugger on failure
pytest --pdb

# Show print statements and failure details
pytest -s -vv --tb=short
```

## ✅ Example 12: Before Committing Checklist

Run this before pushing code:

```bash
#!/bin/bash
echo "🧪 Running tests..."
pytest || exit 1

echo "📊 Checking coverage..."
pytest --cov=src --cov-report=term-missing || exit 1

echo "⚡ Checking performance..."
pytest tests/test_performance.py || exit 1

echo "✅ All checks passed! Ready to commit."
```

## 🚀 Example 13: CI/CD Pipeline Commands

Commands for continuous integration:

```bash
# Full test suite with all reporting
pytest \
  --cov=src \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term-missing \
  --timeout=10 \
  -v \
  --tb=short

# Can be used in GitHub Actions, GitLab CI, Jenkins, etc.
```

## 📊 Example 14: Test Report Generation

Generate test reports for stakeholders:

```bash
# Generate JUnit XML report (for CI/CD tools)
pytest --junit-xml=test-results.xml

# Generate coverage XML (for CI tools)
pytest --cov=src --cov-report=xml

# Generate HTML report with all details
pytest --cov=src --cov-report=html --html=report.html

# View reports
open htmlcov/index.html      # Coverage
open report.html              # Test results
```

## 🎪 Example 15: Continuous Testing During Development

Auto-rerun tests when files change:

```bash
# Install pytest-watch (not in requirements.txt)
pip install pytest-watch

# Run tests automatically on file changes
ptw

# Run specific tests on changes
ptw tests/test_flights.py

# Output:
# [watch] Waiting for file changes...
# [watch] Running tests...
# ============================== 43 passed in 0.67s ==============================
# [watch] Waiting for file changes...
```

## 📈 Example 16: Load Test with Custom Scenarios

Extend Locust for custom user behavior:

```python
# In locustfile.py, add custom tasks:
class PowerUser(HttpUser):
    wait_time = between(0.5, 1)
    
    @task(5)
    def search_multiple_times(self):
        for i in range(5):
            self.client.get(f"/api/flights/search?origin=ORD&destination=MIA")
    
    @task(2)
    def save_all_deals(self):
        for deal_id in ["FL001", "FL002", "FL003"]:
            self.client.post("/api/deals/save", json={
                "user_id": "user123",
                "deal_type": "flight",
                "deal_id": deal_id
            })
```

Then run: `locust -f locustfile.py --host=http://localhost:5000`

---

## 🎯 Testing Cheat Sheet

```bash
# Most common commands
pytest                              # Run all tests
pytest -v                           # Verbose output
pytest -s                           # Show print statements
pytest --cov=src                    # With coverage
pytest -n 4                         # Parallel execution
pytest -x                           # Stop at first failure
pytest -k "test_flight"             # Run matching tests
pytest tests/test_flights.py        # Run specific file

# Performance & Load Testing
pytest tests/test_performance.py -v # Run benchmarks
locust -f locustfile.py --host=...  # Load test UI
locust -f locustfile.py --users 100 # Headless load test
```

## 📞 Questions?

Refer to:
- `TESTING.md` - Comprehensive guide
- `TEST_QUICK_START.md` - Quick reference
- Individual test files - Test documentation

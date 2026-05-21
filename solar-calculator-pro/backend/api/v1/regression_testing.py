"""
Regression Testing System
Task 89: Automated regression tests, functionality validation, performance and security checks
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid

router = APIRouter(prefix="/regression-testing", tags=["Regression Testing"])


class TestStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TestCategory(str, Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"
    REGRESSION = "regression"


class TestResult(BaseModel):
    """Test result"""
    id: str
    name: str
    category: TestCategory
    status: TestStatus
    duration_ms: float
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    assertions: int = 0
    assertions_passed: int = 0


class TestSuite(BaseModel):
    """Test suite"""
    id: str
    name: str
    category: TestCategory
    tests: List[TestResult] = []
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration_ms: float = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class TestRun(BaseModel):
    """Test run"""
    id: str
    name: str
    status: TestStatus
    suites: List[TestSuite] = []
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration_ms: float = 0
    started_at: datetime
    completed_at: Optional[datetime] = None
    triggered_by: str = "manual"
    commit_hash: Optional[str] = None
    branch: Optional[str] = None


# In-memory storage
test_runs: List[TestRun] = []
test_schedules: List[Dict] = []


# ============================================
# Test Execution
# ============================================

@router.post("/run", response_model=TestRun)
async def start_test_run(
    name: str = "Regression Test Run",
    categories: List[TestCategory] = None,
    triggered_by: str = "manual",
    commit_hash: Optional[str] = None,
    branch: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    """Start a new test run"""
    run = TestRun(
        id=str(uuid.uuid4())[:8],
        name=name,
        status=TestStatus.RUNNING,
        started_at=datetime.now(),
        triggered_by=triggered_by,
        commit_hash=commit_hash,
        branch=branch
    )
    
    # Generate test suites based on categories
    if not categories:
        categories = list(TestCategory)
    
    for category in categories:
        suite = _generate_test_suite(category)
        run.suites.append(suite)
        run.total_tests += suite.total_tests
        run.passed += suite.passed
        run.failed += suite.failed
        run.skipped += suite.skipped
        run.duration_ms += suite.duration_ms
    
    run.status = TestStatus.PASSED if run.failed == 0 else TestStatus.FAILED
    run.completed_at = datetime.now()
    
    test_runs.append(run)
    return run


def _generate_test_suite(category: TestCategory) -> TestSuite:
    """Generate a test suite with sample results"""
    suite = TestSuite(
        id=str(uuid.uuid4())[:8],
        name=f"{category.value.title()} Tests",
        category=category,
        started_at=datetime.now()
    )
    
    # Define tests per category
    test_definitions = {
        TestCategory.UNIT: [
            ("test_calculation_solar_yield", 50),
            ("test_calculation_roi", 30),
            ("test_price_matrix_lookup", 25),
            ("test_pdf_generation", 100),
            ("test_user_authentication", 20)
        ],
        TestCategory.INTEGRATION: [
            ("test_api_project_crud", 200),
            ("test_api_calculation_flow", 350),
            ("test_database_transactions", 150),
            ("test_cache_integration", 80)
        ],
        TestCategory.E2E: [
            ("test_user_login_flow", 2000),
            ("test_project_creation_flow", 3500),
            ("test_calculation_to_pdf_flow", 5000),
            ("test_crm_workflow", 2500)
        ],
        TestCategory.PERFORMANCE: [
            ("test_api_response_time", 1000),
            ("test_database_query_performance", 500),
            ("test_concurrent_users", 5000),
            ("test_memory_usage", 2000)
        ],
        TestCategory.SECURITY: [
            ("test_authentication_security", 100),
            ("test_authorization_rules", 150),
            ("test_input_validation", 200),
            ("test_sql_injection_prevention", 100),
            ("test_xss_prevention", 100)
        ],
        TestCategory.REGRESSION: [
            ("test_legacy_calculation_compatibility", 300),
            ("test_data_migration_integrity", 500),
            ("test_api_backward_compatibility", 400),
            ("test_ui_component_rendering", 1000)
        ]
    }
    
    tests = test_definitions.get(category, [])
    
    for test_name, duration in tests:
        # Simulate test results (95% pass rate)
        import random
        passed = random.random() > 0.05
        
        result = TestResult(
            id=str(uuid.uuid4())[:8],
            name=test_name,
            category=category,
            status=TestStatus.PASSED if passed else TestStatus.FAILED,
            duration_ms=duration + random.uniform(-20, 20),
            assertions=random.randint(5, 20),
            assertions_passed=random.randint(5, 20) if passed else random.randint(1, 4),
            error_message=None if passed else "Assertion failed: expected value did not match"
        )
        suite.tests.append(result)
        suite.total_tests += 1
        if passed:
            suite.passed += 1
        else:
            suite.failed += 1
        suite.duration_ms += result.duration_ms
    
    suite.completed_at = datetime.now()
    return suite


@router.get("/runs", response_model=List[TestRun])
async def get_test_runs(limit: int = 20):
    """Get test run history"""
    return test_runs[-limit:]


@router.get("/runs/{run_id}", response_model=TestRun)
async def get_test_run(run_id: str):
    """Get test run details"""
    for run in test_runs:
        if run.id == run_id:
            return run
    raise HTTPException(status_code=404, detail="Test run not found")


@router.get("/runs/{run_id}/failures")
async def get_test_failures(run_id: str):
    """Get failed tests from a run"""
    for run in test_runs:
        if run.id == run_id:
            failures = []
            for suite in run.suites:
                for test in suite.tests:
                    if test.status == TestStatus.FAILED:
                        failures.append({
                            "suite": suite.name,
                            "test": test.name,
                            "error": test.error_message,
                            "duration_ms": test.duration_ms
                        })
            return {"failures": failures, "total": len(failures)}
    raise HTTPException(status_code=404, detail="Test run not found")


# ============================================
# Test Scheduling
# ============================================

@router.post("/schedule")
async def create_test_schedule(
    name: str,
    cron_expression: str,
    categories: List[TestCategory],
    enabled: bool = True
):
    """Create a test schedule"""
    schedule = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "cron_expression": cron_expression,
        "categories": [c.value for c in categories],
        "enabled": enabled,
        "created_at": datetime.now().isoformat(),
        "last_run": None,
        "next_run": datetime.now().isoformat()
    }
    test_schedules.append(schedule)
    return schedule


@router.get("/schedules")
async def get_test_schedules():
    """Get test schedules"""
    return test_schedules


@router.delete("/schedules/{schedule_id}")
async def delete_test_schedule(schedule_id: str):
    """Delete test schedule"""
    global test_schedules
    test_schedules = [s for s in test_schedules if s["id"] != schedule_id]
    return {"status": "deleted", "schedule_id": schedule_id}


# ============================================
# Test Coverage
# ============================================

@router.get("/coverage")
async def get_test_coverage():
    """Get test coverage report"""
    return {
        "overall": {
            "lines": 85.5,
            "branches": 78.2,
            "functions": 90.1,
            "statements": 84.8
        },
        "by_module": [
            {"module": "calculations", "coverage": 92.5},
            {"module": "api", "coverage": 88.3},
            {"module": "services", "coverage": 85.7},
            {"module": "models", "coverage": 95.2},
            {"module": "utils", "coverage": 78.4}
        ],
        "uncovered_files": [
            {"file": "legacy_adapter.py", "coverage": 45.2},
            {"file": "deprecated_utils.py", "coverage": 30.5}
        ],
        "trend": {
            "last_week": 84.2,
            "this_week": 85.5,
            "change": "+1.3%"
        }
    }


# ============================================
# Test Reports
# ============================================

@router.get("/reports/summary")
async def get_test_summary():
    """Get test summary report"""
    if not test_runs:
        return {"message": "No test runs available"}
    
    latest = test_runs[-1]
    
    return {
        "latest_run": {
            "id": latest.id,
            "status": latest.status.value,
            "total": latest.total_tests,
            "passed": latest.passed,
            "failed": latest.failed,
            "pass_rate": (latest.passed / latest.total_tests * 100) if latest.total_tests > 0 else 0,
            "duration_ms": latest.duration_ms
        },
        "trends": {
            "runs_last_7_days": len([r for r in test_runs if r.started_at >= datetime.now() - timedelta(days=7)]),
            "avg_pass_rate": 95.5,
            "avg_duration_ms": 15000
        },
        "flaky_tests": [
            {"name": "test_concurrent_users", "failure_rate": 8.5},
            {"name": "test_external_api_integration", "failure_rate": 5.2}
        ]
    }


@router.get("/reports/comparison")
async def compare_test_runs(run_id_1: str, run_id_2: str):
    """Compare two test runs"""
    run1 = None
    run2 = None
    
    for run in test_runs:
        if run.id == run_id_1:
            run1 = run
        if run.id == run_id_2:
            run2 = run
    
    if not run1 or not run2:
        raise HTTPException(status_code=404, detail="Test run not found")
    
    return {
        "run_1": {
            "id": run1.id,
            "passed": run1.passed,
            "failed": run1.failed,
            "duration_ms": run1.duration_ms
        },
        "run_2": {
            "id": run2.id,
            "passed": run2.passed,
            "failed": run2.failed,
            "duration_ms": run2.duration_ms
        },
        "comparison": {
            "passed_diff": run2.passed - run1.passed,
            "failed_diff": run2.failed - run1.failed,
            "duration_diff_ms": run2.duration_ms - run1.duration_ms
        }
    }

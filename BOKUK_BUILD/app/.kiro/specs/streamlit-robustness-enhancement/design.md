# Design Document

## Overview

This design document outlines the architecture for transforming the existing Streamlit application into a maximally robust, production-ready system. The design builds upon the existing foundation while implementing comprehensive enhancements for state management, data persistence, job processing, caching, security, and operational excellence.

The core architectural principle is **"Zero Data Loss, Zero UI Jumps"** - every user interaction must be preserved and the interface must remain stable and responsive under all conditions.

## Architecture

### Architectural Principles for "Keine Sprünge, Keine Verluste"

The core architectural principle is **"Zero Data Loss, Zero UI Jumps"** with the following implementation strategies:

1. **Widget State Management**
   - Every Widget-Write spiegelt in st.session_state and sofort in DB (debounced)
   - Einheitliche key= für alle Widgets with controlled wrappers (s_text, s_select, etc.)
   - Jeder on_change schreibt in session_state und spiegelt per debounce in DB

2. **Navigation System**
   - Navigation über Router.current_page in session_state
   - Seiten sind Container, nicht neue Routen (container swap)
   - Keine Browser-Back-Logik, alles über eigenen Router

3. **Caching Strategy**
   - Teure Berechnungen hinter st.cache_data/st.cache_resource mit expliziten Keys
   - Cache-Bust nach Writes für consistency
   - get_or_compute(key, fn, ttl) pattern

4. **Job Processing**
   - Lange Jobs entkoppelt via apscheduler/rq
   - UI zeigt stabilen Status, keine Spinners, nur Fortschrittsbalken
   - JobResult-Table für persistence

5. **UI Stability**
   - Platzhalter-Container behalten Position
   - Kein Neuaufbau der Sidebar
   - Keine dynamischen Insertions oberhalb der Scroll-Position
   - Formulare als "controlled forms" mit "Save", "Apply", "Reset"

6. **Performance Targets**
   - 95% der Interaktionen lösen höchstens 50ms Recompute im Haupt-Container aus
   - Keine impliziten on_change-Recomputes

### High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Streamlit UI]
        Router[Navigation Router]
        Forms[Form Manager]
        Widgets[Controlled Widgets]
    end
    
    subgraph "Application Layer"
        Session[Session Manager]
        Cache[Cache System]
        Jobs[Job Manager]
        Events[Event System]
    end
    
    subgraph "Domain Layer"
        Models[Domain Models]
        Services[Business Services]
        Validators[Validation Engine]
    end
    
    subgraph "Infrastructure Layer"
        DB[(Database)]
        Storage[(Object Storage)]
        Queue[Job Queue]
        Metrics[Metrics Store]
    end
    
    subgraph "Operations Layer"
        CLI[CLI Tools]
        Backup[Backup System]
        Monitor[Monitoring]
        Deploy[Deployment]
    end
    
    UI --> Router
    UI --> Forms
    UI --> Widgets
    Router --> Session
    Forms --> Session
    Widgets --> Session
    Session --> Cache
    Session --> Jobs
    Jobs --> Queue
    Cache --> DB
    Models --> DB
    Services --> Models
    CLI --> DB
    CLI --> Backup
    Monitor --> Metrics
```

### Core Components

#### 1. Enhanced Session Management

- **UserSession**: Comprehensive session state with navigation history, form states, permissions
- **SessionPersistence**: Automatic persistence to database with debouncing
- **SessionRecovery**: Restore complete session state after browser refresh
- **MultiUser**: Support for concurrent user sessions with isolation

#### 2. Container-Based Navigation

- **Router**: Client-side routing without page reloads
- **PageContainer**: Stable containers that swap content without layout shifts
- **NavigationState**: Persistent navigation history with back/forward support
- **PermissionGuards**: Route-level access control

#### 3. Controlled Widget System

- **WidgetState**: Centralized state management for all form inputs
- **AutoPersistence**: Immediate session_state updates with debounced DB writes
- **ValidationEngine**: Real-time validation with error state management
- **UndoRedo**: Complete undo/redo stack for all form operations

#### 4. Intelligent Caching

- **MultiLayerCache**: Memory + Streamlit + Database caching layers
- **TaggedInvalidation**: Smart cache invalidation by tags and dependencies
- **CacheWarming**: Proactive cache population for critical data
- **PerformanceMonitoring**: Cache hit rates and performance metrics

#### 5. Background Job System

- **JobQueue**: Asynchronous job processing with priority queues
- **ProgressTracking**: Real-time progress updates without UI blocking
- **JobPersistence**: Durable job state across application restarts
- **RetryLogic**: Exponential backoff with configurable retry policies

## Components and Interfaces

### Core Classes

#### AppConfig

```python
@dataclass
class AppConfig:
    """Enhanced application configuration with all required settings"""
    # Environment
    env: str  # dev/stage/prod
    debug: bool
    mode: str  # offline/online
    theme: str  # auto/light/dark
    compute: str  # fast/accurate
    
    # Database
    database: DatabaseConfig
    
    # Caching
    cache: CacheConfig
    
    # Jobs
    jobs: JobConfig
    
    # Security
    security: SecurityConfig
    
    # Features
    features: Dict[str, bool]
    
    # Performance
    performance: PerformanceConfig
    
    # Paths
    backup_path: str
    log_path: str
    
    @classmethod
    def load_config(cls) -> 'AppConfig':
        """Load configuration from environment and files"""
        pass
```

#### UserSession

```python
@dataclass
class UserSession:
    """Enhanced user session with complete state management"""
    session_id: str
    user_id: Optional[str]
    
    # Navigation
    current_page: str
    page_params: Dict[str, Any]
    navigation_history: List[NavigationEntry]
    
    # Forms
    form_states: Dict[str, FormState]
    dirty_forms: Set[str]
    form_snapshots: Dict[str, List[FormSnapshot]]
    
    # Cache
    cache_keys: Set[str]
    cache_dependencies: Dict[str, Set[str]]
    
    # Permissions
    roles: Set[str]
    permissions: Set[str]
    
    # Preferences
    theme: str
    language: str
    timezone: str
    
    # Metrics
    page_views: Dict[str, int]
    interaction_count: int
    session_duration: timedelta
```

#### Router

```python
class Router:
    """Enhanced navigation router with container-based page swapping"""
    
    def __init__(self):
        self.routes: Dict[str, Route] = {}
        self.middleware: List[Middleware] = []
        self.guards: List[RouteGuard] = []
        self.current_page: str = "home"
        self.params: Dict[str, Any] = {}
        self.history: List[NavigationEntry] = []
    
    def navigate(self, to: str, params: Dict[str, Any] = None, replace: bool = False) -> None:
        """Navigate to page via container swap, no browser navigation"""
        pass
    
    def go_back(self) -> bool:
        """Handle browser back via internal router"""
        pass
    
    def go_forward(self) -> bool:
        """Handle browser forward via internal router"""
        pass
    
    def register_route(self, name: str, page_class: Type[Page], **options) -> None
    def register_middleware(self, middleware: Middleware) -> None
    def register_guard(self, guard: RouteGuard) -> None
    def render_navigation(self) -> None
    def render_current_page(self) -> None
    
    @property
    def current_route(self) -> str:
        """Get current route from session_state"""
        return st.session_state.get('router_current_page', 'home')
```

#### FormState

```python
@dataclass
class FormState:
    """Enhanced form state with undo/redo"""
    form_id: str
    data: Dict[str, Any]
    
    # Validation
    errors: Dict[str, List[str]]
    warnings: Dict[str, List[str]]
    validation_schema: Optional[Dict[str, Any]]
    
    # History
    snapshots: List[FormSnapshot]
    current_snapshot_index: int
    max_snapshots: int
    
    # Persistence
    is_dirty: bool
    last_saved: Optional[datetime]
    auto_save: bool
    save_debounce_ms: int
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    version: int
```

#### Job & JobResult

```python
@dataclass
class Job:
    """Enhanced job definition for background processing"""
    id: str
    name: str
    function: Callable
    args: tuple
    kwargs: Dict[str, Any]
    
    # Scheduling
    priority: int
    scheduled_at: Optional[datetime]
    timeout: Optional[int]
    
    # Retry
    retry_count: int
    max_retries: int
    retry_delay: int
    
    # Dependencies
    depends_on: List[str]
    tags: Set[str]
    
    # Metadata
    created_by: str
    created_at: datetime
    metadata: Dict[str, Any]

@dataclass
class JobResult:
    """Job execution result stored in JobResult-Table"""
    id: str
    job_id: str
    status: JobStatus  # PENDING, RUNNING, COMPLETED, FAILED, CANCELLED
    result: Optional[Any]
    error: Optional[str]
    progress: float  # 0.0 to 1.0
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for database storage"""
        pass
```

#### Repository Pattern

```python
class Repository(Generic[T]):
    """Enhanced repository with audit logging"""
    
    def __init__(self, model_class: Type[T], db_manager: DatabaseManager):
        self.model_class = model_class
        self.db_manager = db_manager
        self.audit_logger = AuditLogger()
    
    def create(self, **kwargs) -> T
    def get_by_id(self, entity_id: Any) -> Optional[T]
    def update(self, entity_id: Any, **kwargs) -> Optional[T]
    def delete(self, entity_id: Any, soft: bool = True) -> bool
    def find_by(self, **criteria) -> List[T]
    def paginate(self, page: int, size: int, **filters) -> PaginatedResult[T]
    def bulk_create(self, entities: List[Dict[str, Any]]) -> List[T]
    def bulk_update(self, updates: List[Dict[str, Any]]) -> int
```

### Data Models

#### Core Classes

```python
@dataclass
class CacheKeys:
    """Centralized cache key management"""
    USER_SESSION = "user_session_{user_id}"
    FORM_DATA = "form_data_{form_id}_{user_id}"
    JOB_RESULT = "job_result_{job_id}"
    COMPUTED_DATA = "computed_{function_name}_{hash}"
    
    @staticmethod
    def user_session(user_id: str) -> str:
        return f"user_session_{user_id}"
    
    @staticmethod
    def form_data(form_id: str, user_id: str) -> str:
        return f"form_data_{form_id}_{user_id}"

@dataclass
class DB:
    """Database connection and management"""
    connection: Connection
    engine: Engine
    session_factory: sessionmaker
    
    def get_session(self) -> Session:
        """Get database session"""
        pass
    
    def health_check(self) -> bool:
        """Check database health"""
        pass

@dataclass
class Event:
    """System event for tracking and auditing"""
    id: str
    type: str
    source: str
    data: Dict[str, Any]
    timestamp: datetime
    user_id: Optional[str]
    session_id: Optional[str]
    correlation_id: str

@dataclass
class Metrics:
    """Application metrics collection"""
    request_count: int
    response_time_avg: float
    error_rate: float
    active_sessions: int
    job_queue_size: int
    cache_hit_rate: float
    memory_usage: float
    
    def to_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        pass

class UnitOfWork:
    """Unit of Work pattern for transaction management"""
    
    def __init__(self, db: DB):
        self.db = db
        self.session: Optional[Session] = None
        self._repositories: Dict[str, Any] = {}
    
    def __enter__(self):
        self.session = self.db.get_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()
    
    def commit(self):
        self.session.commit()
    
    def rollback(self):
        self.session.rollback()

class Page:
    """Base page class for modular page implementation"""
    
    def __init__(self, router: Router, session: UserSession):
        self.router = router
        self.session = session
        self.title: str = ""
        self.permissions: Set[str] = set()
    
    def render(self) -> None:
        """Render page content"""
        pass
    
    def on_event(self, event: Event) -> None:
        """Handle page events"""
        pass
    
    def can_access(self, user: User) -> bool:
        """Check if user can access this page"""
        return self.permissions.issubset(user.permissions)
```

#### Domain Models

```python
@dataclass
class User:
    """User domain model"""
    id: str
    email: str
    name: str
    roles: Set[str]
    permissions: Set[str]
    preferences: UserPreferences
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

@dataclass
class FormData:
    """Form data model"""
    id: str
    form_id: str
    user_id: str
    data: Dict[str, Any]
    version: int
    created_at: datetime
    updated_at: datetime

@dataclass
class AuditLog:
    """Audit log model for all system changes"""
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    timestamp: datetime
    ip_address: str
    user_agent: str
    correlation_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for database storage"""
        pass
```

### Core Functions

#### Application Lifecycle

```python
def init_app() -> None:
    """Initialize application with all components"""
    config = load_config()
    bootstrap_session()
    migrate()
    # Initialize all systems

def load_config() -> AppConfig:
    """Load configuration from environment and files"""
    pass

def bootstrap_session() -> UserSession:
    """Initialize or restore user session"""
    pass

def navigate(to: str, params: Dict[str, Any] = None) -> None:
    """Navigate to page via Router"""
    pass
```

#### Data Persistence

```python
def persist_input(key: str, val: Any) -> None:
    """Immediately persist input to session_state and debounce to DB"""
    st.session_state[key] = val
    # Trigger debounced DB write

def save_form(form_id: str, data: Dict[str, Any]) -> FormData:
    """Save form data with transaction"""
    pass

def get_or_compute(key: str, fn: Callable, ttl: int = 3600) -> Any:
    """Get from cache or compute and cache"""
    pass
```

#### Job Management

```python
def enqueue(job: Job) -> str:
    """Enqueue job for background processing"""
    pass

def poll(job_id: str) -> Optional[JobResult]:
    """Poll job status and results"""
    pass

def cancel(job_id: str) -> bool:
    """Cancel running job"""
    pass
```

#### Database Operations

```python
def get_conn() -> Connection:
    """Get database connection"""
    pass

def run_tx(fn: Callable) -> Any:
    """Run function in transaction with UnitOfWork"""
    pass

def migrate() -> None:
    """Run pending database migrations"""
    pass
```

#### Backup & Recovery

```python
def snapshot_db() -> str:
    """Create database snapshot"""
    pass

def restore(snapshot_id: str) -> bool:
    """Restore from snapshot"""
    pass
```

#### Telemetry

```python
def track(event: str, props: Dict[str, Any]) -> None:
    """Track user event"""
    pass

def log_error(err: Exception, ctx: Dict[str, Any]) -> None:
    """Log error with context"""
    pass
```

### Controlled Widget System

#### Widget Wrappers

```python
def s_text(key: str, label: str = None, **kwargs) -> str:
    """Controlled text input with auto-persistence"""
    value = st.text_input(label or key, key=key, **kwargs)
    persist_input(key, value)
    return value

def s_select(key: str, options: List[Any], label: str = None, **kwargs) -> Any:
    """Controlled selectbox with auto-persistence"""
    value = st.selectbox(label or key, options, key=key, **kwargs)
    persist_input(key, value)
    return value

def s_number(key: str, label: str = None, **kwargs) -> float:
    """Controlled number input with auto-persistence"""
    value = st.number_input(label or key, key=key, **kwargs)
    persist_input(key, value)
    return value

def s_checkbox(key: str, label: str = None, **kwargs) -> bool:
    """Controlled checkbox with auto-persistence"""
    value = st.checkbox(label or key, key=key, **kwargs)
    persist_input(key, value)
    return value

def s_date(key: str, label: str = None, **kwargs) -> date:
    """Controlled date input with auto-persistence"""
    value = st.date_input(label or key, key=key, **kwargs)
    persist_input(key, value)
    return value

def s_file(key: str, label: str = None, **kwargs) -> Any:
    """Controlled file uploader with auto-persistence"""
    value = st.file_uploader(label or key, key=key, **kwargs)
    persist_input(key, value)
    return value

def s_multiselect(key: str, options: List[Any], label: str = None, **kwargs) -> List[Any]:
    """Controlled multiselect with auto-persistence"""
    value = st.multiselect(label or key, options, key=key, **kwargs)
    persist_input(key, value)
    return value

def s_slider(key: str, min_value: float, max_value: float, label: str = None, **kwargs) -> float:
    """Controlled slider with auto-persistence"""
    value = st.slider(label or key, min_value, max_value, key=key, **kwargs)
    persist_input(key, value)
    return value
```

### Service Layer

#### Business Services

```python
class UserService:
    """User management service"""
    
    def __init__(self, user_repo: Repository[User], audit_service: AuditService):
        self.user_repo = user_repo
        self.audit_service = audit_service
    
    def authenticate(self, email: str, password: str) -> Optional[User]
    def create_user(self, user_data: Dict[str, Any]) -> User
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> User
    def delete_user(self, user_id: str) -> bool
    def get_user_permissions(self, user_id: str) -> Set[str]

class FormService:
    """Form management service"""
    
    def save_form(self, form_id: str, user_id: str, data: Dict[str, Any]) -> FormData
    def load_form(self, form_id: str, user_id: str) -> Optional[FormData]
    def validate_form(self, form_id: str, data: Dict[str, Any]) -> ValidationResult
    def create_snapshot(self, form_id: str, user_id: str, description: str) -> FormSnapshot
    def restore_snapshot(self, snapshot_id: str) -> FormData

class JobService:
    """Job management service"""
    
    def enqueue_job(self, job: Job) -> str
    def get_job_status(self, job_id: str) -> Optional[JobResult]
    def cancel_job(self, job_id: str) -> bool
    def retry_job(self, job_id: str) -> str
    def get_user_jobs(self, user_id: str) -> List[JobResult]
```

## Error Handling

### Error Hierarchy

```python
class AppError(Exception):
    """Base application error"""
    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(message)

class ValidationError(AppError):
    """Validation error"""
    pass

class PermissionError(AppError):
    """Permission denied error"""
    pass

class JobError(AppError):
    """Job execution error"""
    pass

class CacheError(AppError):
    """Cache operation error"""
    pass
```

### Error Handling Strategy

1. **Graceful Degradation**: UI remains functional even when backend services fail
2. **User-Friendly Messages**: Technical errors are translated to user-friendly messages
3. **Automatic Recovery**: Transient errors trigger automatic retry with exponential backoff
4. **Error Boundaries**: Errors are contained to prevent cascade failures
5. **Comprehensive Logging**: All errors are logged with full context for debugging

## Testing Strategy

### Test Pyramid

#### Unit Tests (70%)

- **Pure Functions**: All computation functions with property-based testing
- **Domain Models**: Validation, business rules, state transitions
- **Services**: Business logic with mocked dependencies
- **Utilities**: Helper functions and data transformations

#### Integration Tests (20%)

- **Database**: Repository operations with real database
- **Cache**: Cache operations and invalidation logic
- **Jobs**: Job execution and state management
- **API**: External service integrations

#### End-to-End Tests (10%)

- **User Workflows**: Complete user journeys using Playwright
- **Cross-Browser**: Testing on Chrome, Firefox, Safari
- **Performance**: Load testing and response time validation
- **Accessibility**: WCAG compliance testing

### Test Infrastructure

```python
class TestFixtures:
    """Test data fixtures"""
    
    @pytest.fixture
    def test_user(self) -> User:
        return User(
            id="test_user_1",
            email="test@example.com",
            name="Test User",
            roles={"user"},
            permissions={"read", "write"}
        )
    
    @pytest.fixture
    def test_session(self, test_user: User) -> UserSession:
        return UserSession(
            session_id="test_session_1",
            user_id=test_user.id,
            current_page="home"
        )
    
    @pytest.fixture
    def test_db(self) -> DatabaseManager:
        # In-memory test database
        return DatabaseManager(url="sqlite:///:memory:")

class TestHelpers:
    """Test helper functions"""
    
    @staticmethod
    def create_test_form_data(form_id: str, **data) -> Dict[str, Any]:
        return {"form_id": form_id, "data": data, "created_at": datetime.now()}
    
    @staticmethod
    def simulate_user_input(widget_key: str, value: Any) -> None:
        # Simulate user input for testing
        pass
```

### Performance Testing

- **Load Testing**: Simulate 100+ concurrent users
- **Stress Testing**: Test system limits and recovery
- **Memory Profiling**: Detect memory leaks and optimization opportunities
- **Database Performance**: Query optimization and indexing validation

## Security Architecture

### Authentication & Authorization

```python
class SecurityManager:
    """Centralized security management"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.session_store = SessionStore()
        self.permission_engine = PermissionEngine()
    
    def authenticate_user(self, credentials: Dict[str, str]) -> Optional[User]
    def authorize_action(self, user: User, action: str, resource: str) -> bool
    def create_session(self, user: User) -> UserSession
    def validate_session(self, session_id: str) -> Optional[UserSession]
    def revoke_session(self, session_id: str) -> bool
```

### Data Protection

- **PII Masking**: Automatic masking of sensitive data in logs and debug output
- **Encryption**: Sensitive data encrypted at rest and in transit
- **Access Logging**: All data access logged for audit trails
- **Data Retention**: Automatic cleanup of expired data

### Security Headers

```python
SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'",
    "Referrer-Policy": "strict-origin-when-cross-origin"
}
```

## Deployment Architecture

### Environment Configuration

```yaml
# Development
environment: dev
database_url: "duckdb:///dev.db"
debug: true
cache_ttl: 60
job_workers: 2

# Staging
environment: staging
database_url: "postgresql://user:pass@staging-db/app"
debug: false
cache_ttl: 300
job_workers: 4

# Production
environment: prod
database_url: "postgresql://user:pass@prod-db/app"
debug: false
cache_ttl: 3600
job_workers: 8
```

### Infrastructure Components

- **Reverse Proxy**: Nginx/Caddy for TLS termination and load balancing
- **Database**: PostgreSQL with read replicas for production
- **Object Storage**: S3-compatible storage for file uploads
- **Monitoring**: Prometheus + Grafana for metrics and alerting
- **Logging**: Structured JSON logs with centralized collection

### Deployment Pipeline

1. **Code Quality**: Linting, type checking, security scanning
2. **Testing**: Unit, integration, and E2E test suites
3. **Build**: Docker image creation with dependency caching
4. **Deploy**: Blue-green deployment with health checks
5. **Monitor**: Automated rollback on failure detection

## Migration Strategy

### Database Migrations

```python
class MigrationManager:
    """Database migration management"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.alembic_config = self._setup_alembic()
    
    def run_migrations(self) -> None:
        """Run pending migrations"""
        command.upgrade(self.alembic_config, "head")
    
    def create_migration(self, message: str) -> str:
        """Create new migration"""
        return command.revision(self.alembic_config, message=message, autogenerate=True)
    
    def rollback_migration(self, revision: str) -> None:
        """Rollback to specific revision"""
        command.downgrade(self.alembic_config, revision)
```

### Zero-Downtime Deployment

1. **Database Migrations**: Forward-compatible schema changes
2. **Feature Flags**: Gradual feature rollout with instant rollback
3. **Blue-Green Deployment**: Parallel environment switching
4. **Health Checks**: Automated validation before traffic switching
5. **Rollback Strategy**: Instant rollback on failure detection

## Monitoring and Observability

### Metrics Collection

```python
class MetricsCollector:
    """Application metrics collection"""
    
    def __init__(self):
        self.request_counter = Counter('app_requests_total', ['method', 'endpoint', 'status'])
        self.request_duration = Histogram('app_request_duration_seconds', ['endpoint'])
        self.active_sessions = Gauge('app_active_sessions')
        self.job_queue_size = Gauge('app_job_queue_size')
        self.cache_hit_rate = Gauge('app_cache_hit_rate')
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        self.request_counter.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(endpoint=endpoint).observe(duration)
    
    def update_active_sessions(self, count: int):
        self.active_sessions.set(count)
```

### Health Checks

```python
class HealthChecker:
    """System health monitoring"""
    
    def __init__(self, db_manager: DatabaseManager, cache: CacheManager, job_manager: JobManager):
        self.db_manager = db_manager
        self.cache = cache
        self.job_manager = job_manager
    
    def check_database(self) -> HealthStatus:
        """Check database connectivity"""
        try:
            self.db_manager.health_check()
            return HealthStatus.HEALTHY
        except Exception as e:
            return HealthStatus.UNHEALTHY(str(e))
    
    def check_cache(self) -> HealthStatus:
        """Check cache system"""
        # Implementation
        pass
    
    def check_jobs(self) -> HealthStatus:
        """Check job system"""
        # Implementation
        pass
    
    def overall_health(self) -> Dict[str, HealthStatus]:
        """Get overall system health"""
        return {
            "database": self.check_database(),
            "cache": self.check_cache(),
            "jobs": self.check_jobs(),
        }
```

### Alerting Rules

- **Response Time**: Alert if 95th percentile > 2 seconds
- **Error Rate**: Alert if error rate > 5% over 5 minutes
- **Database**: Alert if connection pool exhausted
- **Jobs**: Alert if job queue size > 1000
- **Memory**: Alert if memory usage > 80%
- **Disk**: Alert if disk usage > 90%

This comprehensive design provides the foundation for a maximally robust Streamlit application that meets all the specified requirements while maintaining high performance, security, and operational excellence.

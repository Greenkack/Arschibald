# Robuste Streamlit App - Projektstruktur

```
streamlit_app/
├── app.py                          # Haupteinstiegspunkt
├── pyproject.toml                  # Dependencies & Config
├── .env.example                    # Environment Template
├── README.md
├── ARCHITECTURE.md
├── OPERATIONS.md
├── BACKUP_RESTORE.md
├── MIGRATIONS.md
├── TESTING.md
├── SECURITY.md
│
├── cli/                           # CLI Commands
│   ├── __init__.py
│   ├── main.py                    # Typer CLI
│   ├── app_commands.py
│   ├── db_commands.py
│   ├── backup_commands.py
│   └── test_commands.py
│
├── core/                          # Kernlogik
│   ├── __init__.py
│   ├── config.py                  # AppConfig
│   ├── session.py                 # UserSession
│   ├── router.py                  # Router
│   ├── database.py                # DB, Repository, UnitOfWork
│   ├── cache.py                   # Caching
│   ├── jobs.py                    # Job System
│   ├── audit.py                   # AuditLog
│   ├── metrics.py                 # Metrics
│   └── compute/                   # Rechenkern
│       ├── __init__.py
│       ├── schemas.py             # Pydantic Schemas
│       ├── calculations.py        # Reine Funktionen
│       └── formulas.py
│
├── models/                        # Domain Models
│   ├── __init__.py
│   ├── base.py                    # Base Model
│   ├── user.py
│   ├── form_state.py
│   ├── job.py
│   └── audit.py
│
├── pages/                         # UI Pages
│   ├── __init__.py
│   ├── base.py                    # Page Base Class
│   ├── home.py
│   ├── settings.py
│   ├── form_demo.py
│   ├── job_demo.py
│   └── import_export.py
│
├── widgets/                       # Controlled Widgets
│   ├── __init__.py
│   ├── base.py                    # Widget Base
│   ├── inputs.py                  # s_text, s_select, etc.
│   └── forms.py                   # FormState Manager
│
├── repositories/                  # Data Access
│   ├── __init__.py
│   ├── base.py                    # Repository<T>
│   ├── user_repository.py
│   ├── form_repository.py
│   └── job_repository.py
│
├── services/                      # Business Logic
│   ├── __init__.py
│   ├── auth_service.py
│   ├── backup_service.py
│   └── integration_service.py
│
├── migrations/                    # Alembic
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── tests/                         # Test Suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   └── property/                  # Hypothesis Tests
│
├── static/                        # Assets
│   ├── css/
│   ├── js/
│   └── images/
│
└── docker/                       # Deployment
    ├── Dockerfile
    ├── docker-compose.yml
    └── nginx.conf
```

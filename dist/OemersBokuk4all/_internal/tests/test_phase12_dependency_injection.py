"""
Tests für Phase 12: Dependency Injection
=========================================

Test-Coverage für:
- DI Container (core/dependency_injection.py)
- Service Registration
- Service Resolution
- Lifetime Management (SINGLETON, SCOPED, TRANSIENT)
- Circular Dependency Detection
- Decorators (@injectable, @singleton, @scoped, @transient)

Ausführen:
    pytest tests/test_phase12_dependency_injection.py -v
"""

import pytest
import threading
from unittest.mock import Mock, MagicMock
from typing import Optional

# Import der zu testenden Module
try:
    from core.dependency_injection import (
        DIContainer,
        ServiceLifetime,
        ServiceDescriptor,
        CircularDependencyError,
        ServiceNotFoundError,
        injectable,
        singleton,
        scoped,
        transient
    )
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    pytest.skip(f"Dependency Injection nicht verfügbar: {e}", allow_module_level=True)


# ============================================================================
# TEST SERVICES
# ============================================================================

class IRepository:
    """Interface für Repository (ABC)."""
    def get_data(self):
        raise NotImplementedError


class MockRepository(IRepository):
    """Mock-Repository-Implementierung."""
    def __init__(self):
        self.data = ["item1", "item2"]
    
    def get_data(self):
        return self.data


class Logger:
    """Einfacher Logger-Service."""
    def __init__(self):
        self.logs = []
    
    def log(self, message: str):
        self.logs.append(message)


class Config:
    """Config-Service."""
    def __init__(self):
        self.settings = {"debug": True}
    
    def get(self, key: str):
        return self.settings.get(key)


class DatabaseConnection:
    """Database-Connection-Service mit Dependency."""
    def __init__(self, config: Config):
        self.config = config
        self.connected = True


class UserService:
    """User-Service mit mehreren Dependencies."""
    def __init__(self, repo: IRepository, logger: Logger):
        self.repo = repo
        self.logger = logger
        self.logger.log("UserService initialized")
    
    def get_users(self):
        return self.repo.get_data()


class ServiceA:
    """Service A für Circular-Dependency-Tests."""
    def __init__(self, b: 'ServiceB'):
        self.b = b


class ServiceB:
    """Service B für Circular-Dependency-Tests."""
    def __init__(self, a: ServiceA):
        self.a = a


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def container():
    """Frischer DI-Container."""
    return DIContainer()


@pytest.fixture
def configured_container():
    """Container mit registrierten Sample-Services."""
    container = DIContainer()
    container.register(Logger, Logger, ServiceLifetime.SINGLETON)
    container.register(Config, Config, ServiceLifetime.SINGLETON)
    container.register(IRepository, MockRepository, ServiceLifetime.SCOPED)
    container.register(UserService, UserService, ServiceLifetime.TRANSIENT)
    return container


# ============================================================================
# TEST CLASS: DI Container
# ============================================================================

class TestDIContainer:
    """Tests für DI-Container-Basis-Funktionalität."""
    
    def test_create_container(self):
        """Test: Container erstellen."""
        container = DIContainer()
        assert container is not None
        assert len(container.get_registered_services()) == 0
    
    def test_register_service_type(self, container):
        """Test: Service via Typ registrieren."""
        container.register(Logger, Logger, ServiceLifetime.SINGLETON)
        
        services = container.get_registered_services()
        assert Logger in services
        assert services[Logger].lifetime == ServiceLifetime.SINGLETON
    
    def test_register_service_factory(self, container):
        """Test: Service via Factory registrieren."""
        def create_logger():
            return Logger()
        
        container.register(Logger, create_logger, ServiceLifetime.SINGLETON)
        
        logger = container.resolve(Logger)
        assert isinstance(logger, Logger)
    
    def test_register_instance(self, container):
        """Test: Service-Instanz registrieren."""
        logger = Logger()
        logger.log("Test")
        
        container.register_instance(Logger, logger)
        
        resolved = container.resolve(Logger)
        assert resolved is logger
        assert "Test" in resolved.logs
    
    def test_resolve_unregistered_service(self, container):
        """Test: Nicht-registrierten Service auflösen."""
        with pytest.raises(ServiceNotFoundError):
            container.resolve(Logger)
    
    def test_register_with_interface(self, container):
        """Test: Interface -> Implementation registrieren."""
        container.register(IRepository, MockRepository, ServiceLifetime.SCOPED)
        
        repo = container.resolve(IRepository)
        assert isinstance(repo, MockRepository)
        assert repo.get_data() == ["item1", "item2"]
    
    def test_get_stats(self, container):
        """Test: Container-Statistiken abrufen."""
        container.register(Logger, Logger, ServiceLifetime.SINGLETON)
        container.register(Config, Config, ServiceLifetime.SCOPED)
        container.register(UserService, UserService, ServiceLifetime.TRANSIENT)
        
        stats = container.get_stats()
        
        assert stats['total_registered'] == 3
        assert stats['singletons'] == 1
        assert stats['scoped'] == 1
        assert stats['transient'] == 1
    
    def test_clear_container(self, container):
        """Test: Container leeren."""
        container.register(Logger, Logger, ServiceLifetime.SINGLETON)
        container.register(Config, Config, ServiceLifetime.SINGLETON)
        
        container.clear()
        
        assert len(container.get_registered_services()) == 0


# ============================================================================
# TEST CLASS: Service Registration
# ============================================================================

class TestServiceRegistration:
    """Tests für Service-Registrierung."""
    
    def test_register_singleton(self, container):
        """Test: SINGLETON-Service registrieren."""
        container.register(Logger, Logger, ServiceLifetime.SINGLETON)
        
        logger1 = container.resolve(Logger)
        logger2 = container.resolve(Logger)
        
        # Gleiche Instanz
        assert logger1 is logger2
    
    def test_register_scoped(self, container):
        """Test: SCOPED-Service registrieren."""
        container.register(Config, Config, ServiceLifetime.SCOPED)
        
        # In gleichem Scope: gleiche Instanz
        with container.create_scope() as scope:
            config1 = scope.resolve(Config)
            config2 = scope.resolve(Config)
            assert config1 is config2
        
        # In verschiedenen Scopes: verschiedene Instanzen
        with container.create_scope() as scope1:
            config_a = scope1.resolve(Config)
        
        with container.create_scope() as scope2:
            config_b = scope2.resolve(Config)
        
        assert config_a is not config_b
    
    def test_register_transient(self, container):
        """Test: TRANSIENT-Service registrieren."""
        container.register(Logger, Logger, ServiceLifetime.TRANSIENT)
        
        logger1 = container.resolve(Logger)
        logger2 = container.resolve(Logger)
        
        # Verschiedene Instanzen
        assert logger1 is not logger2
    
    def test_update_registration(self, container):
        """Test: Bestehende Registrierung updaten."""
        container.register(Logger, Logger, ServiceLifetime.TRANSIENT)
        
        logger1 = container.resolve(Logger)
        logger2 = container.resolve(Logger)
        assert logger1 is not logger2  # TRANSIENT
        
        # Update zu SINGLETON
        container.register(Logger, Logger, ServiceLifetime.SINGLETON)
        
        logger3 = container.resolve(Logger)
        logger4 = container.resolve(Logger)
        assert logger3 is logger4  # SINGLETON
    
    def test_register_multiple_services(self, container):
        """Test: Mehrere Services registrieren."""
        services = [
            (Logger, Logger, ServiceLifetime.SINGLETON),
            (Config, Config, ServiceLifetime.SINGLETON),
            (IRepository, MockRepository, ServiceLifetime.SCOPED),
        ]
        
        for service_type, implementation, lifetime in services:
            container.register(service_type, implementation, lifetime)
        
        assert len(container.get_registered_services()) == 3
    
    def test_register_with_dependencies(self, container):
        """Test: Service mit Dependencies registrieren."""
        container.register(Config, Config, ServiceLifetime.SINGLETON)
        container.register(DatabaseConnection, DatabaseConnection, ServiceLifetime.SCOPED)
        
        with container.create_scope() as scope:
            db = scope.resolve(DatabaseConnection)
            assert isinstance(db.config, Config)


# ============================================================================
# TEST CLASS: Service Resolution
# ============================================================================

class TestServiceResolution:
    """Tests für Service-Auflösung."""
    
    def test_resolve_simple_service(self, container):
        """Test: Einfachen Service auflösen."""
        container.register(Logger, Logger, ServiceLifetime.SINGLETON)
        
        logger = container.resolve(Logger)
        
        assert isinstance(logger, Logger)
        assert logger.logs == []
    
    def test_resolve_with_dependencies(self, configured_container):
        """Test: Service mit Dependencies auflösen."""
        user_service = configured_container.resolve(UserService)
        
        assert isinstance(user_service, UserService)
        assert isinstance(user_service.repo, MockRepository)
        assert isinstance(user_service.logger, Logger)
        assert "UserService initialized" in user_service.logger.logs
    
    def test_auto_wiring(self, container):
        """Test: Automatisches Dependency-Injection (Auto-Wiring)."""
        container.register(Logger, Logger, ServiceLifetime.SINGLETON)
        container.register(IRepository, MockRepository, ServiceLifetime.SCOPED)
        container.register(UserService, UserService, ServiceLifetime.TRANSIENT)
        
        user_service = container.resolve(UserService)
        
        # Dependencies wurden automatisch injiziert
        assert user_service.repo is not None
        assert user_service.logger is not None
    
    def test_resolve_nested_dependencies(self, container):
        """Test: Verschachtelte Dependencies auflösen."""
        # Config -> DatabaseConnection -> Service
        container.register(Config, Config, ServiceLifetime.SINGLETON)
        container.register(DatabaseConnection, DatabaseConnection, ServiceLifetime.SCOPED)
        
        class ServiceWithDB:
            def __init__(self, db: DatabaseConnection):
                self.db = db
        
        container.register(ServiceWithDB, ServiceWithDB, ServiceLifetime.TRANSIENT)
        
        service = container.resolve(ServiceWithDB)
        
        assert isinstance(service.db, DatabaseConnection)
        assert isinstance(service.db.config, Config)
    
    def test_resolve_optional_dependency(self, container):
        """Test: Optional Dependency auflösen."""
        class ServiceWithOptional:
            def __init__(self, logger: Optional[Logger] = None):
                self.logger = logger
        
        container.register(ServiceWithOptional, ServiceWithOptional, ServiceLifetime.TRANSIENT)
        
        service = container.resolve(ServiceWithOptional)
        
        # Ohne registrierten Logger sollte None sein
        assert service.logger is None
    
    def test_resolve_from_scoped_container(self, container):
        """Test: Service aus Scoped-Container auflösen."""
        container.register(Config, Config, ServiceLifetime.SCOPED)
        
        with container.create_scope() as scope:
            config = scope.resolve(Config)
            assert isinstance(config, Config)
    
    def test_resolve_performance(self, configured_container):
        """Test: Resolution-Performance."""
        import time
        
        start = time.time()
        
        for _ in range(1000):
            user_service = configured_container.resolve(UserService)
        
        duration = time.time() - start
        
        # 1000 Resolutions sollten <1 Sekunde dauern
        assert duration < 1.0


# ============================================================================
# TEST CLASS: Lifetime Management
# ============================================================================

class TestLifetimeManagement:
    """Tests für Service-Lifetime-Management."""
    
    def test_singleton_lifetime(self, container):
        """Test: SINGLETON Lifetime."""
        container.register(Logger, Logger, ServiceLifetime.SINGLETON)
        
        logger1 = container.resolve(Logger)
        logger1.log("Test 1")
        
        logger2 = container.resolve(Logger)
        
        # Gleiche Instanz
        assert logger1 is logger2
        # State wird geteilt
        assert "Test 1" in logger2.logs
    
    def test_scoped_lifetime_within_scope(self, container):
        """Test: SCOPED Lifetime innerhalb Scope."""
        container.register(Config, Config, ServiceLifetime.SCOPED)
        
        with container.create_scope() as scope:
            config1 = scope.resolve(Config)
            config1.settings['test'] = 123
            
            config2 = scope.resolve(Config)
            
            # Gleiche Instanz innerhalb Scope
            assert config1 is config2
            assert config2.settings['test'] == 123
    
    def test_scoped_lifetime_across_scopes(self, container):
        """Test: SCOPED Lifetime über Scopes hinweg."""
        container.register(Config, Config, ServiceLifetime.SCOPED)
        
        with container.create_scope() as scope1:
            config1 = scope1.resolve(Config)
            config1.settings['test'] = 123
        
        with container.create_scope() as scope2:
            config2 = scope2.resolve(Config)
            
            # Verschiedene Instanzen über Scopes
            assert config1 is not config2
            # State wird NICHT geteilt
            assert 'test' not in config2.settings
    
    def test_transient_lifetime(self, container):
        """Test: TRANSIENT Lifetime."""
        container.register(Logger, Logger, ServiceLifetime.TRANSIENT)
        
        logger1 = container.resolve(Logger)
        logger1.log("Test 1")
        
        logger2 = container.resolve(Logger)
        logger2.log("Test 2")
        
        # Verschiedene Instanzen
        assert logger1 is not logger2
        # State wird NICHT geteilt
        assert "Test 1" not in logger2.logs
        assert "Test 2" not in logger1.logs
    
    def test_mixed_lifetimes(self, container):
        """Test: Gemischte Lifetimes."""
        # SINGLETON Logger
        container.register(Logger, Logger, ServiceLifetime.SINGLETON)
        
        # TRANSIENT Service mit SINGLETON Dependency
        class TransientService:
            def __init__(self, logger: Logger):
                self.logger = logger
        
        container.register(TransientService, TransientService, ServiceLifetime.TRANSIENT)
        
        service1 = container.resolve(TransientService)
        service2 = container.resolve(TransientService)
        
        # Services sind verschieden (TRANSIENT)
        assert service1 is not service2
        # Aber Logger ist gleich (SINGLETON)
        assert service1.logger is service2.logger
    
    def test_scope_disposal(self, container):
        """Test: Scope-Disposal."""
        container.register(Config, Config, ServiceLifetime.SCOPED)
        
        with container.create_scope() as scope:
            config = scope.resolve(Config)
            assert config is not None
        
        # Nach Scope sollte Service disposed sein
        stats = container.get_stats()
        assert stats['active_scopes'] == 0


# ============================================================================
# TEST CLASS: Circular Dependencies
# ============================================================================

class TestCircularDependencies:
    """Tests für Circular-Dependency-Detection."""
    
    def test_detect_circular_dependency(self, container):
        """Test: Zirkuläre Dependency erkennen."""
        container.register(ServiceA, ServiceA, ServiceLifetime.TRANSIENT)
        container.register(ServiceB, ServiceB, ServiceLifetime.TRANSIENT)
        
        with pytest.raises(CircularDependencyError) as exc_info:
            container.resolve(ServiceA)
        
        # Error-Message sollte Pfad enthalten
        assert "ServiceA" in str(exc_info.value)
        assert "ServiceB" in str(exc_info.value)
    
    def test_no_false_positive_circular(self, container):
        """Test: Keine False-Positive bei echten Dependencies."""
        # A -> B, B -> C (kein Zyklus!)
        class ServiceC:
            pass
        
        class ServiceB:
            def __init__(self, c: ServiceC):
                self.c = c
        
        class ServiceA:
            def __init__(self, b: ServiceB):
                self.b = b
        
        container.register(ServiceC, ServiceC, ServiceLifetime.SINGLETON)
        container.register(ServiceB, ServiceB, ServiceLifetime.SINGLETON)
        container.register(ServiceA, ServiceA, ServiceLifetime.SINGLETON)
        
        # Sollte NICHT fehlschlagen
        service_a = container.resolve(ServiceA)
        assert isinstance(service_a.b.c, ServiceC)
    
    def test_circular_dependency_path(self, container):
        """Test: Circular-Dependency-Pfad korrekt."""
        container.register(ServiceA, ServiceA, ServiceLifetime.TRANSIENT)
        container.register(ServiceB, ServiceB, ServiceLifetime.TRANSIENT)
        
        try:
            container.resolve(ServiceA)
        except CircularDependencyError as e:
            # Pfad sollte A -> B -> A sein
            path = e.path
            assert path == ['ServiceA', 'ServiceB', 'ServiceA']


# ============================================================================
# TEST CLASS: Decorators
# ============================================================================

class TestDecorators:
    """Tests für Service-Decorators."""
    
    def test_injectable_decorator(self, container):
        """Test: @injectable Decorator."""
        @injectable()
        class TestService:
            pass
        
        container.register(TestService, TestService, ServiceLifetime.TRANSIENT)
        
        service = container.resolve(TestService)
        assert isinstance(service, TestService)
    
    def test_singleton_decorator(self, container):
        """Test: @singleton Decorator."""
        @singleton()
        class SingletonService:
            pass
        
        container.register(SingletonService, SingletonService, ServiceLifetime.SINGLETON)
        
        s1 = container.resolve(SingletonService)
        s2 = container.resolve(SingletonService)
        
        assert s1 is s2
    
    def test_scoped_decorator(self, container):
        """Test: @scoped Decorator."""
        @scoped()
        class ScopedService:
            pass
        
        container.register(ScopedService, ScopedService, ServiceLifetime.SCOPED)
        
        with container.create_scope() as scope:
            s1 = scope.resolve(ScopedService)
            s2 = scope.resolve(ScopedService)
            assert s1 is s2
    
    def test_transient_decorator(self, container):
        """Test: @transient Decorator."""
        @transient()
        class TransientService:
            pass
        
        container.register(TransientService, TransientService, ServiceLifetime.TRANSIENT)
        
        s1 = container.resolve(TransientService)
        s2 = container.resolve(TransientService)
        
        assert s1 is not s2


# ============================================================================
# TEST CLASS: Integration Tests
# ============================================================================

class TestIntegration:
    """Integration-Tests."""
    
    def test_complex_dependency_graph(self, container):
        """Test: Komplexer Dependency-Graph."""
        # Logger (SINGLETON)
        container.register(Logger, Logger, ServiceLifetime.SINGLETON)
        
        # Config (SINGLETON)
        container.register(Config, Config, ServiceLifetime.SINGLETON)
        
        # DatabaseConnection (SCOPED) <- Config
        container.register(DatabaseConnection, DatabaseConnection, ServiceLifetime.SCOPED)
        
        # Repository (SCOPED) <- DatabaseConnection (implizit)
        class Repository:
            def __init__(self, db: DatabaseConnection):
                self.db = db
        
        container.register(IRepository, Repository, ServiceLifetime.SCOPED)
        
        # UserService (TRANSIENT) <- Repository, Logger
        container.register(UserService, UserService, ServiceLifetime.TRANSIENT)
        
        # Auflösen
        with container.create_scope() as scope:
            user_service = scope.resolve(UserService)
            
            assert isinstance(user_service.logger, Logger)
            assert isinstance(user_service.repo, Repository)
            assert isinstance(user_service.repo.db, DatabaseConnection)
            assert isinstance(user_service.repo.db.config, Config)
    
    def test_thread_safety(self, container):
        """Test: Thread-Safety."""
        container.register(Logger, Logger, ServiceLifetime.SINGLETON)
        
        results = []
        
        def resolve_logger():
            logger = container.resolve(Logger)
            results.append(logger)
        
        threads = [threading.Thread(target=resolve_logger) for _ in range(10)]
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Alle sollten gleiche SINGLETON-Instanz haben
        assert len(results) == 10
        assert all(r is results[0] for r in results)


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

@pytest.mark.parametrize("lifetime,expected_same", [
    (ServiceLifetime.SINGLETON, True),
    (ServiceLifetime.SCOPED, False),   # Über Scopes hinweg
    (ServiceLifetime.TRANSIENT, False),
])
def test_parametrized_lifetimes(container, lifetime, expected_same):
    """Parametrized Test: Service-Lifetimes."""
    container.register(Logger, Logger, lifetime)
    
    if lifetime == ServiceLifetime.SCOPED:
        # SCOPED: Verschiedene Scopes = verschiedene Instanzen
        with container.create_scope() as scope1:
            l1 = scope1.resolve(Logger)
        with container.create_scope() as scope2:
            l2 = scope2.resolve(Logger)
    else:
        # SINGLETON/TRANSIENT: Direkte Resolution
        l1 = container.resolve(Logger)
        l2 = container.resolve(Logger)
    
    if expected_same:
        assert l1 is l2
    else:
        assert l1 is not l2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

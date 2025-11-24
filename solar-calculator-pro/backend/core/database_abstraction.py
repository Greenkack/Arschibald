"""
Database Abstraction Layer
Provides unified interface for SQLite, PostgreSQL, and MySQL databases.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from enum import Enum
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import StaticPool, QueuePool
import logging

logger = logging.getLogger(__name__)


class DatabaseType(str, Enum):
    """Supported database types"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


class DatabaseConfig:
    """Database configuration"""
    
    def __init__(
        self,
        db_type: DatabaseType,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        sqlite_path: Optional[str] = None,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False
    ):
        self.db_type = db_type
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.sqlite_path = sqlite_path
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.echo = echo
    
    def get_connection_string(self) -> str:
        """Generate database connection string"""
        if self.db_type == DatabaseType.SQLITE:
            if not self.sqlite_path:
                raise ValueError("SQLite path is required for SQLite database")
            return f"sqlite:///{self.sqlite_path}"
        
        elif self.db_type == DatabaseType.POSTGRESQL:
            if not all([self.host, self.database, self.username, self.password]):
                raise ValueError("Host, database, username, and password are required for PostgreSQL")
            port = self.port or 5432
            return f"postgresql://{self.username}:{self.password}@{self.host}:{port}/{self.database}"
        
        elif self.db_type == DatabaseType.MYSQL:
            if not all([self.host, self.database, self.username, self.password]):
                raise ValueError("Host, database, username, and password are required for MySQL")
            port = self.port or 3306
            return f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{port}/{self.database}"
        
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")


class DatabaseAdapter(ABC):
    """Abstract base class for database adapters"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self.Base = declarative_base()
    
    @abstractmethod
    def connect(self) -> None:
        """Establish database connection"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection"""
        pass
    
    @abstractmethod
    def create_tables(self) -> None:
        """Create all tables"""
        pass
    
    @abstractmethod
    def drop_tables(self) -> None:
        """Drop all tables"""
        pass
    
    @abstractmethod
    def get_session(self) -> Session:
        """Get database session"""
        pass
    
    @abstractmethod
    def execute_raw_sql(self, sql: str, params: Optional[Dict] = None) -> Any:
        """Execute raw SQL query"""
        pass
    
    @abstractmethod
    def backup(self, backup_path: str) -> bool:
        """Backup database"""
        pass
    
    @abstractmethod
    def restore(self, backup_path: str) -> bool:
        """Restore database from backup"""
        pass


class SQLiteAdapter(DatabaseAdapter):
    """SQLite database adapter"""
    
    def connect(self) -> None:
        """Establish SQLite connection"""
        try:
            connection_string = self.config.get_connection_string()
            
            # SQLite-specific configuration
            self.engine = create_engine(
                connection_string,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=self.config.echo
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Connected to SQLite database: {self.config.sqlite_path}")
        
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close SQLite connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Disconnected from SQLite database")
    
    def create_tables(self) -> None:
        """Create all tables in SQLite"""
        self.Base.metadata.create_all(bind=self.engine)
        logger.info("Created all tables in SQLite")
    
    def drop_tables(self) -> None:
        """Drop all tables in SQLite"""
        self.Base.metadata.drop_all(bind=self.engine)
        logger.info("Dropped all tables in SQLite")
    
    def get_session(self) -> Session:
        """Get SQLite session"""
        return self.SessionLocal()
    
    def execute_raw_sql(self, sql: str, params: Optional[Dict] = None) -> Any:
        """Execute raw SQL in SQLite"""
        with self.engine.connect() as connection:
            result = connection.execute(sql, params or {})
            return result.fetchall()
    
    def backup(self, backup_path: str) -> bool:
        """Backup SQLite database"""
        import shutil
        try:
            shutil.copy2(self.config.sqlite_path, backup_path)
            logger.info(f"SQLite database backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup SQLite database: {e}")
            return False
    
    def restore(self, backup_path: str) -> bool:
        """Restore SQLite database from backup"""
        import shutil
        try:
            shutil.copy2(backup_path, self.config.sqlite_path)
            logger.info(f"SQLite database restored from: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore SQLite database: {e}")
            return False


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL database adapter"""
    
    def connect(self) -> None:
        """Establish PostgreSQL connection"""
        try:
            connection_string = self.config.get_connection_string()
            
            # PostgreSQL-specific configuration
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                echo=self.config.echo
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Connected to PostgreSQL database: {self.config.database}")
        
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close PostgreSQL connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Disconnected from PostgreSQL database")
    
    def create_tables(self) -> None:
        """Create all tables in PostgreSQL"""
        self.Base.metadata.create_all(bind=self.engine)
        logger.info("Created all tables in PostgreSQL")
    
    def drop_tables(self) -> None:
        """Drop all tables in PostgreSQL"""
        self.Base.metadata.drop_all(bind=self.engine)
        logger.info("Dropped all tables in PostgreSQL")
    
    def get_session(self) -> Session:
        """Get PostgreSQL session"""
        return self.SessionLocal()
    
    def execute_raw_sql(self, sql: str, params: Optional[Dict] = None) -> Any:
        """Execute raw SQL in PostgreSQL"""
        with self.engine.connect() as connection:
            result = connection.execute(sql, params or {})
            return result.fetchall()
    
    def backup(self, backup_path: str) -> bool:
        """Backup PostgreSQL database using pg_dump"""
        import subprocess
        try:
            cmd = [
                "pg_dump",
                "-h", self.config.host,
                "-p", str(self.config.port or 5432),
                "-U", self.config.username,
                "-d", self.config.database,
                "-f", backup_path
            ]
            
            env = {"PGPASSWORD": self.config.password}
            subprocess.run(cmd, env=env, check=True)
            
            logger.info(f"PostgreSQL database backed up to: {backup_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to backup PostgreSQL database: {e}")
            return False
    
    def restore(self, backup_path: str) -> bool:
        """Restore PostgreSQL database using psql"""
        import subprocess
        try:
            cmd = [
                "psql",
                "-h", self.config.host,
                "-p", str(self.config.port or 5432),
                "-U", self.config.username,
                "-d", self.config.database,
                "-f", backup_path
            ]
            
            env = {"PGPASSWORD": self.config.password}
            subprocess.run(cmd, env=env, check=True)
            
            logger.info(f"PostgreSQL database restored from: {backup_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to restore PostgreSQL database: {e}")
            return False


class MySQLAdapter(DatabaseAdapter):
    """MySQL database adapter"""
    
    def connect(self) -> None:
        """Establish MySQL connection"""
        try:
            connection_string = self.config.get_connection_string()
            
            # MySQL-specific configuration
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                echo=self.config.echo
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info(f"Connected to MySQL database: {self.config.database}")
        
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close MySQL connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Disconnected from MySQL database")
    
    def create_tables(self) -> None:
        """Create all tables in MySQL"""
        self.Base.metadata.create_all(bind=self.engine)
        logger.info("Created all tables in MySQL")
    
    def drop_tables(self) -> None:
        """Drop all tables in MySQL"""
        self.Base.metadata.drop_all(bind=self.engine)
        logger.info("Dropped all tables in MySQL")
    
    def get_session(self) -> Session:
        """Get MySQL session"""
        return self.SessionLocal()
    
    def execute_raw_sql(self, sql: str, params: Optional[Dict] = None) -> Any:
        """Execute raw SQL in MySQL"""
        with self.engine.connect() as connection:
            result = connection.execute(sql, params or {})
            return result.fetchall()
    
    def backup(self, backup_path: str) -> bool:
        """Backup MySQL database using mysqldump"""
        import subprocess
        try:
            cmd = [
                "mysqldump",
                "-h", self.config.host,
                "-P", str(self.config.port or 3306),
                "-u", self.config.username,
                f"-p{self.config.password}",
                self.config.database,
                "--result-file", backup_path
            ]
            
            subprocess.run(cmd, check=True)
            
            logger.info(f"MySQL database backed up to: {backup_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to backup MySQL database: {e}")
            return False
    
    def restore(self, backup_path: str) -> bool:
        """Restore MySQL database from backup"""
        import subprocess
        try:
            cmd = [
                "mysql",
                "-h", self.config.host,
                "-P", str(self.config.port or 3306),
                "-u", self.config.username,
                f"-p{self.config.password}",
                self.config.database
            ]
            
            with open(backup_path, 'r') as f:
                subprocess.run(cmd, stdin=f, check=True)
            
            logger.info(f"MySQL database restored from: {backup_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to restore MySQL database: {e}")
            return False


class DatabaseFactory:
    """Factory for creating database adapters"""
    
    @staticmethod
    def create_adapter(config: DatabaseConfig) -> DatabaseAdapter:
        """Create appropriate database adapter based on configuration"""
        if config.db_type == DatabaseType.SQLITE:
            return SQLiteAdapter(config)
        elif config.db_type == DatabaseType.POSTGRESQL:
            return PostgreSQLAdapter(config)
        elif config.db_type == DatabaseType.MYSQL:
            return MySQLAdapter(config)
        else:
            raise ValueError(f"Unsupported database type: {config.db_type}")


class DatabaseManager:
    """Unified database manager"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.adapter = DatabaseFactory.create_adapter(config)
        self._connected = False
    
    def connect(self) -> None:
        """Connect to database"""
        if not self._connected:
            self.adapter.connect()
            self._connected = True
    
    def disconnect(self) -> None:
        """Disconnect from database"""
        if self._connected:
            self.adapter.disconnect()
            self._connected = False
    
    def get_session(self) -> Session:
        """Get database session"""
        if not self._connected:
            self.connect()
        return self.adapter.get_session()
    
    def create_tables(self) -> None:
        """Create all tables"""
        if not self._connected:
            self.connect()
        self.adapter.create_tables()
    
    def drop_tables(self) -> None:
        """Drop all tables"""
        if not self._connected:
            self.connect()
        self.adapter.drop_tables()
    
    def execute_raw_sql(self, sql: str, params: Optional[Dict] = None) -> Any:
        """Execute raw SQL"""
        if not self._connected:
            self.connect()
        return self.adapter.execute_raw_sql(sql, params)
    
    def backup(self, backup_path: str) -> bool:
        """Backup database"""
        return self.adapter.backup(backup_path)
    
    def restore(self, backup_path: str) -> bool:
        """Restore database"""
        return self.adapter.restore(backup_path)
    
    def get_database_type(self) -> DatabaseType:
        """Get current database type"""
        return self.config.db_type
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()

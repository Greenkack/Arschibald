"""
Database Production Setup
Task 77: Production database configuration, backups, replication, and monitoring
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio


class ReplicationType(str, Enum):
    STREAMING = "streaming"
    LOGICAL = "logical"
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"


class BackupType(str, Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    WAL = "wal"


class BackupStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DatabaseConnectionConfig(BaseModel):
    """Database connection configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "solar_calculator"
    username: str = "solar_app"
    password: str = ""
    ssl_mode: str = "require"
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    ssl_root_cert: Optional[str] = None


class ConnectionPoolConfig(BaseModel):
    """Connection pool configuration"""
    min_size: int = 5
    max_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 1800
    pool_pre_ping: bool = True
    echo: bool = False


class ReplicationConfig(BaseModel):
    """Database replication configuration"""
    enabled: bool = True
    type: ReplicationType = ReplicationType.STREAMING
    primary_host: str = "primary.db.local"
    replica_hosts: List[str] = ["replica1.db.local", "replica2.db.local"]
    replication_user: str = "replicator"
    replication_password: str = ""
    synchronous_commit: bool = True
    max_wal_senders: int = 10
    wal_keep_size: str = "1GB"
    hot_standby: bool = True
    hot_standby_feedback: bool = True


class BackupConfig(BaseModel):
    """Backup configuration"""
    enabled: bool = True
    backup_directory: str = "/var/backups/postgresql"
    retention_days: int = 30
    full_backup_schedule: str = "0 2 * * 0"  # Weekly on Sunday at 2 AM
    incremental_backup_schedule: str = "0 2 * * 1-6"  # Daily except Sunday
    wal_archive_enabled: bool = True
    wal_archive_directory: str = "/var/backups/postgresql/wal"
    compression_enabled: bool = True
    compression_level: int = 6
    encryption_enabled: bool = True
    encryption_key_path: str = "/etc/postgresql/backup.key"
    parallel_jobs: int = 4
    s3_enabled: bool = False
    s3_bucket: Optional[str] = None
    s3_region: Optional[str] = None


class MonitoringConfig(BaseModel):
    """Database monitoring configuration"""
    enabled: bool = True
    metrics_port: int = 9187
    slow_query_threshold_ms: int = 1000
    log_min_duration_statement: int = 500
    log_checkpoints: bool = True
    log_connections: bool = True
    log_disconnections: bool = True
    log_lock_waits: bool = True
    track_activities: bool = True
    track_counts: bool = True
    track_io_timing: bool = True
    track_functions: str = "all"


class PerformanceConfig(BaseModel):
    """Database performance configuration"""
    shared_buffers: str = "4GB"
    effective_cache_size: str = "12GB"
    maintenance_work_mem: str = "1GB"
    work_mem: str = "256MB"
    max_connections: int = 200
    max_parallel_workers_per_gather: int = 4
    max_parallel_workers: int = 8
    max_parallel_maintenance_workers: int = 4
    random_page_cost: float = 1.1
    effective_io_concurrency: int = 200
    checkpoint_completion_target: float = 0.9
    wal_buffers: str = "64MB"
    default_statistics_target: int = 100


class DatabaseProductionConfig(BaseModel):
    """Complete database production configuration"""
    connection: DatabaseConnectionConfig = DatabaseConnectionConfig()
    pool: ConnectionPoolConfig = ConnectionPoolConfig()
    replication: ReplicationConfig = ReplicationConfig()
    backup: BackupConfig = BackupConfig()
    monitoring: MonitoringConfig = MonitoringConfig()
    performance: PerformanceConfig = PerformanceConfig()


class BackupJob(BaseModel):
    """Backup job information"""
    id: str
    type: BackupType
    status: BackupStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    size_bytes: int = 0
    duration_seconds: float = 0
    error_message: Optional[str] = None
    backup_path: Optional[str] = None


class ReplicaStatus(BaseModel):
    """Replica status information"""
    host: str
    status: str
    lag_bytes: int
    lag_seconds: float
    last_replay_timestamp: Optional[datetime] = None
    is_streaming: bool
    sync_state: str


class DatabaseHealth(BaseModel):
    """Database health information"""
    status: str
    connections_active: int
    connections_idle: int
    connections_total: int
    connections_max: int
    database_size_gb: float
    cache_hit_ratio: float
    transaction_rate: float
    deadlocks: int
    conflicts: int
    temp_files: int
    temp_bytes: int


# In-memory storage for demo
backup_jobs: List[BackupJob] = []
replica_statuses: Dict[str, ReplicaStatus] = {}


class DatabaseManager:
    """Database management operations"""
    
    def __init__(self, config: DatabaseProductionConfig):
        self.config = config
    
    async def get_health(self) -> DatabaseHealth:
        """Get database health status"""
        # In production, this would query actual database
        return DatabaseHealth(
            status="healthy",
            connections_active=15,
            connections_idle=5,
            connections_total=20,
            connections_max=self.config.performance.max_connections,
            database_size_gb=25.5,
            cache_hit_ratio=0.985,
            transaction_rate=150.5,
            deadlocks=0,
            conflicts=0,
            temp_files=2,
            temp_bytes=1024 * 1024 * 50
        )
    
    async def get_replica_status(self) -> List[ReplicaStatus]:
        """Get replication status"""
        statuses = []
        for host in self.config.replication.replica_hosts:
            statuses.append(ReplicaStatus(
                host=host,
                status="streaming",
                lag_bytes=1024,
                lag_seconds=0.5,
                last_replay_timestamp=datetime.now(),
                is_streaming=True,
                sync_state="async"
            ))
        return statuses
    
    async def create_backup(self, backup_type: BackupType) -> BackupJob:
        """Create a new backup"""
        job = BackupJob(
            id=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type=backup_type,
            status=BackupStatus.RUNNING,
            started_at=datetime.now()
        )
        backup_jobs.append(job)
        
        # Simulate backup completion
        await asyncio.sleep(0.1)
        job.status = BackupStatus.COMPLETED
        job.completed_at = datetime.now()
        job.size_bytes = 1024 * 1024 * 500  # 500 MB
        job.duration_seconds = 120.5
        job.backup_path = f"{self.config.backup.backup_directory}/{job.id}.tar.gz"
        
        return job
    
    async def restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """Restore from backup"""
        job = None
        for b in backup_jobs:
            if b.id == backup_id:
                job = b
                break
        
        if not job:
            return {"status": "error", "message": "Backup not found"}
        
        return {
            "status": "success",
            "message": f"Restored from backup {backup_id}",
            "restored_at": datetime.now().isoformat()
        }
    
    async def get_slow_queries(self, limit: int = 10) -> List[Dict]:
        """Get slow queries"""
        return [
            {
                "query": "SELECT * FROM calculations WHERE created_at > $1",
                "calls": 150,
                "total_time_ms": 5000,
                "mean_time_ms": 33.3,
                "rows": 10000
            },
            {
                "query": "UPDATE projects SET status = $1 WHERE id = $2",
                "calls": 50,
                "total_time_ms": 2500,
                "mean_time_ms": 50.0,
                "rows": 50
            }
        ]
    
    async def get_table_stats(self) -> List[Dict]:
        """Get table statistics"""
        return [
            {
                "table": "projects",
                "rows": 50000,
                "size_mb": 250,
                "index_size_mb": 50,
                "dead_tuples": 100,
                "last_vacuum": datetime.now() - timedelta(hours=2),
                "last_analyze": datetime.now() - timedelta(hours=1)
            },
            {
                "table": "calculations",
                "rows": 200000,
                "size_mb": 1000,
                "index_size_mb": 200,
                "dead_tuples": 500,
                "last_vacuum": datetime.now() - timedelta(hours=3),
                "last_analyze": datetime.now() - timedelta(hours=2)
            }
        ]
    
    async def vacuum_analyze(self, table: Optional[str] = None) -> Dict:
        """Run VACUUM ANALYZE"""
        return {
            "status": "success",
            "table": table or "all tables",
            "started_at": datetime.now().isoformat(),
            "message": "VACUUM ANALYZE completed"
        }
    
    async def reindex(self, table: Optional[str] = None) -> Dict:
        """Reindex tables"""
        return {
            "status": "success",
            "table": table or "all tables",
            "started_at": datetime.now().isoformat(),
            "message": "REINDEX completed"
        }


# PostgreSQL configuration template
POSTGRESQL_CONF_TEMPLATE = """
# PostgreSQL Production Configuration
# Generated for Solar Calculator Pro

#------------------------------------------------------------------------------
# CONNECTIONS AND AUTHENTICATION
#------------------------------------------------------------------------------
listen_addresses = '*'
port = {port}
max_connections = {max_connections}
superuser_reserved_connections = 3

#------------------------------------------------------------------------------
# RESOURCE USAGE
#------------------------------------------------------------------------------
shared_buffers = {shared_buffers}
huge_pages = try
work_mem = {work_mem}
maintenance_work_mem = {maintenance_work_mem}
effective_cache_size = {effective_cache_size}

#------------------------------------------------------------------------------
# WRITE AHEAD LOG
#------------------------------------------------------------------------------
wal_level = replica
fsync = on
synchronous_commit = on
wal_buffers = {wal_buffers}
checkpoint_completion_target = {checkpoint_completion_target}
max_wal_size = 4GB
min_wal_size = 1GB
archive_mode = on
archive_command = 'cp %p {wal_archive_directory}/%f'

#------------------------------------------------------------------------------
# REPLICATION
#------------------------------------------------------------------------------
max_wal_senders = {max_wal_senders}
wal_keep_size = {wal_keep_size}
hot_standby = {hot_standby}
hot_standby_feedback = {hot_standby_feedback}

#------------------------------------------------------------------------------
# QUERY TUNING
#------------------------------------------------------------------------------
random_page_cost = {random_page_cost}
effective_io_concurrency = {effective_io_concurrency}
default_statistics_target = {default_statistics_target}

#------------------------------------------------------------------------------
# PARALLEL QUERY
#------------------------------------------------------------------------------
max_parallel_workers_per_gather = {max_parallel_workers_per_gather}
max_parallel_workers = {max_parallel_workers}
max_parallel_maintenance_workers = {max_parallel_maintenance_workers}

#------------------------------------------------------------------------------
# LOGGING
#------------------------------------------------------------------------------
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = {log_min_duration_statement}
log_checkpoints = {log_checkpoints}
log_connections = {log_connections}
log_disconnections = {log_disconnections}
log_lock_waits = {log_lock_waits}
log_statement = 'ddl'
log_temp_files = 0

#------------------------------------------------------------------------------
# STATISTICS
#------------------------------------------------------------------------------
track_activities = {track_activities}
track_counts = {track_counts}
track_io_timing = {track_io_timing}
track_functions = {track_functions}

#------------------------------------------------------------------------------
# AUTOVACUUM
#------------------------------------------------------------------------------
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min
autovacuum_vacuum_threshold = 50
autovacuum_analyze_threshold = 50
autovacuum_vacuum_scale_factor = 0.1
autovacuum_analyze_scale_factor = 0.05
"""


def generate_postgresql_conf(config: DatabaseProductionConfig) -> str:
    """Generate PostgreSQL configuration"""
    return POSTGRESQL_CONF_TEMPLATE.format(
        port=config.connection.port,
        max_connections=config.performance.max_connections,
        shared_buffers=config.performance.shared_buffers,
        work_mem=config.performance.work_mem,
        maintenance_work_mem=config.performance.maintenance_work_mem,
        effective_cache_size=config.performance.effective_cache_size,
        wal_buffers=config.performance.wal_buffers,
        checkpoint_completion_target=config.performance.checkpoint_completion_target,
        wal_archive_directory=config.backup.wal_archive_directory,
        max_wal_senders=config.replication.max_wal_senders,
        wal_keep_size=config.replication.wal_keep_size,
        hot_standby="on" if config.replication.hot_standby else "off",
        hot_standby_feedback="on" if config.replication.hot_standby_feedback else "off",
        random_page_cost=config.performance.random_page_cost,
        effective_io_concurrency=config.performance.effective_io_concurrency,
        default_statistics_target=config.performance.default_statistics_target,
        max_parallel_workers_per_gather=config.performance.max_parallel_workers_per_gather,
        max_parallel_workers=config.performance.max_parallel_workers,
        max_parallel_maintenance_workers=config.performance.max_parallel_maintenance_workers,
        log_min_duration_statement=config.monitoring.log_min_duration_statement,
        log_checkpoints="on" if config.monitoring.log_checkpoints else "off",
        log_connections="on" if config.monitoring.log_connections else "off",
        log_disconnections="on" if config.monitoring.log_disconnections else "off",
        log_lock_waits="on" if config.monitoring.log_lock_waits else "off",
        track_activities="on" if config.monitoring.track_activities else "off",
        track_counts="on" if config.monitoring.track_counts else "off",
        track_io_timing="on" if config.monitoring.track_io_timing else "off",
        track_functions=config.monitoring.track_functions
    )


# pg_hba.conf template
PG_HBA_CONF_TEMPLATE = """
# PostgreSQL Client Authentication Configuration
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections
local   all             all                                     peer
local   all             postgres                                peer

# IPv4 local connections
host    all             all             127.0.0.1/32            scram-sha-256

# IPv4 remote connections (application)
hostssl solar_calculator solar_app      10.0.0.0/8              scram-sha-256
hostssl solar_calculator solar_app      172.16.0.0/12           scram-sha-256
hostssl solar_calculator solar_app      192.168.0.0/16          scram-sha-256

# Replication connections
hostssl replication     replicator      10.0.0.0/8              scram-sha-256

# Monitoring connections
hostssl all             monitoring      10.0.0.0/8              scram-sha-256

# Reject all other connections
host    all             all             0.0.0.0/0               reject
"""


def generate_pg_hba_conf() -> str:
    """Generate pg_hba.conf"""
    return PG_HBA_CONF_TEMPLATE


# Backup script template
BACKUP_SCRIPT_TEMPLATE = """#!/bin/bash
# PostgreSQL Backup Script
# Generated for Solar Calculator Pro

set -e

# Configuration
BACKUP_DIR="{backup_directory}"
RETENTION_DAYS={retention_days}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
LOG_FILE="$BACKUP_DIR/backup_$TIMESTAMP.log"

# Database connection
export PGHOST="{host}"
export PGPORT={port}
export PGDATABASE="{database}"
export PGUSER="{username}"

echo "Starting backup at $(date)" | tee -a $LOG_FILE

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

# Perform backup
pg_dump --format=custom --compress={compression_level} --jobs={parallel_jobs} \\
    --file=$BACKUP_FILE 2>> $LOG_FILE

# Verify backup
pg_restore --list $BACKUP_FILE > /dev/null 2>> $LOG_FILE

# Get backup size
BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
echo "Backup completed: $BACKUP_FILE ($BACKUP_SIZE)" | tee -a $LOG_FILE

# Cleanup old backups
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete
echo "Cleaned up backups older than $RETENTION_DAYS days" | tee -a $LOG_FILE

# Upload to S3 if enabled
{s3_upload}

echo "Backup finished at $(date)" | tee -a $LOG_FILE
"""


def generate_backup_script(config: DatabaseProductionConfig) -> str:
    """Generate backup script"""
    s3_upload = ""
    if config.backup.s3_enabled and config.backup.s3_bucket:
        s3_upload = f"""
# Upload to S3
aws s3 cp $BACKUP_FILE s3://{config.backup.s3_bucket}/backups/
echo "Uploaded to S3: s3://{config.backup.s3_bucket}/backups/" | tee -a $LOG_FILE
"""
    
    return BACKUP_SCRIPT_TEMPLATE.format(
        backup_directory=config.backup.backup_directory,
        retention_days=config.backup.retention_days,
        host=config.connection.host,
        port=config.connection.port,
        database=config.connection.database,
        username=config.connection.username,
        compression_level=config.backup.compression_level,
        parallel_jobs=config.backup.parallel_jobs,
        s3_upload=s3_upload
    )

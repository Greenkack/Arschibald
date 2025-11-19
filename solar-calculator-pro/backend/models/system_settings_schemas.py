"""
System Settings Schemas

Pydantic models for system settings API requests and responses
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class LogLevel(str, Enum):
    """Log level enumeration"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class BackupFrequency(str, Enum):
    """Backup frequency enumeration"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class EmailProvider(str, Enum):
    """Email provider enumeration"""
    SMTP = "smtp"
    SENDGRID = "sendgrid"
    MAILGUN = "mailgun"
    AWS_SES = "aws_ses"


# General Settings
class GeneralSettingsUpdate(BaseModel):
    """General settings update request"""
    app_name: Optional[str] = Field(None, min_length=1, max_length=100)
    app_description: Optional[str] = Field(None, max_length=500)
    default_language: Optional[str] = Field(None, pattern="^[a-z]{2}-[A-Z]{2}$")
    default_currency: Optional[str] = Field(None, pattern="^[A-Z]{3}$")
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    time_format: Optional[str] = None
    items_per_page: Optional[int] = Field(None, ge=10, le=100)
    session_timeout: Optional[int] = Field(None, ge=5, le=1440)  # minutes
    enable_analytics: Optional[bool] = None
    enable_telemetry: Optional[bool] = None
    maintenance_mode: Optional[bool] = None


class GeneralSettingsResponse(BaseModel):
    """General settings response"""
    app_name: str
    app_description: str
    default_language: str
    default_currency: str
    timezone: str
    date_format: str
    time_format: str
    items_per_page: int
    session_timeout: int
    enable_analytics: bool
    enable_telemetry: bool
    maintenance_mode: bool
    updated_at: datetime


# Email Configuration
class EmailSettingsUpdate(BaseModel):
    """Email settings update request"""
    provider: Optional[EmailProvider] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = Field(None, ge=1, le=65535)
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: Optional[bool] = None
    smtp_use_ssl: Optional[bool] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None
    reply_to_email: Optional[EmailStr] = None
    api_key: Optional[str] = None  # For SendGrid, Mailgun, etc.
    api_secret: Optional[str] = None
    region: Optional[str] = None  # For AWS SES
    test_email: Optional[EmailStr] = None


class EmailSettingsResponse(BaseModel):
    """Email settings response"""
    provider: EmailProvider
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_use_tls: bool
    smtp_use_ssl: bool
    from_email: str
    from_name: str
    reply_to_email: Optional[str] = None
    region: Optional[str] = None
    is_configured: bool
    last_test_at: Optional[datetime] = None
    last_test_success: Optional[bool] = None
    updated_at: datetime


class EmailTestRequest(BaseModel):
    """Email test request"""
    to_email: EmailStr
    subject: Optional[str] = "Test Email from Solar Calculator Pro"
    body: Optional[str] = "This is a test email to verify email configuration."


class EmailTestResponse(BaseModel):
    """Email test response"""
    success: bool
    message: str
    sent_at: datetime


# Backup Settings
class BackupSettingsUpdate(BaseModel):
    """Backup settings update request"""
    enabled: Optional[bool] = None
    frequency: Optional[BackupFrequency] = None
    retention_days: Optional[int] = Field(None, ge=1, le=365)
    backup_location: Optional[str] = None
    include_database: Optional[bool] = None
    include_files: Optional[bool] = None
    include_logs: Optional[bool] = None
    compress_backups: Optional[bool] = None
    encrypt_backups: Optional[bool] = None
    encryption_key: Optional[str] = None
    max_backup_size_mb: Optional[int] = Field(None, ge=100, le=10000)
    notification_email: Optional[EmailStr] = None


class BackupSettingsResponse(BaseModel):
    """Backup settings response"""
    enabled: bool
    frequency: BackupFrequency
    retention_days: int
    backup_location: str
    include_database: bool
    include_files: bool
    include_logs: bool
    compress_backups: bool
    encrypt_backups: bool
    max_backup_size_mb: int
    notification_email: Optional[str] = None
    last_backup_at: Optional[datetime] = None
    last_backup_success: Optional[bool] = None
    last_backup_size_mb: Optional[float] = None
    next_backup_at: Optional[datetime] = None
    total_backups: int
    updated_at: datetime


class BackupNowRequest(BaseModel):
    """Manual backup request"""
    include_database: bool = True
    include_files: bool = True
    include_logs: bool = False
    description: Optional[str] = None


class BackupInfo(BaseModel):
    """Backup information"""
    id: int
    filename: str
    created_at: datetime
    size_mb: float
    description: Optional[str] = None
    includes_database: bool
    includes_files: bool
    includes_logs: bool
    is_compressed: bool
    is_encrypted: bool


class BackupListResponse(BaseModel):
    """Backup list response"""
    backups: List[BackupInfo]
    total: int
    total_size_mb: float


# Logging Configuration
class LoggingSettingsUpdate(BaseModel):
    """Logging settings update request"""
    log_level: Optional[LogLevel] = None
    log_to_file: Optional[bool] = None
    log_to_console: Optional[bool] = None
    log_file_path: Optional[str] = None
    max_log_file_size_mb: Optional[int] = Field(None, ge=1, le=1000)
    log_file_retention_days: Optional[int] = Field(None, ge=1, le=365)
    log_rotation_enabled: Optional[bool] = None
    log_format: Optional[str] = None
    log_api_requests: Optional[bool] = None
    log_database_queries: Optional[bool] = None
    log_errors_only: Optional[bool] = None
    enable_debug_mode: Optional[bool] = None


class LoggingSettingsResponse(BaseModel):
    """Logging settings response"""
    log_level: LogLevel
    log_to_file: bool
    log_to_console: bool
    log_file_path: str
    max_log_file_size_mb: int
    log_file_retention_days: int
    log_rotation_enabled: bool
    log_format: str
    log_api_requests: bool
    log_database_queries: bool
    log_errors_only: bool
    enable_debug_mode: bool
    current_log_size_mb: float
    total_log_files: int
    updated_at: datetime


class LogFileInfo(BaseModel):
    """Log file information"""
    filename: str
    size_mb: float
    created_at: datetime
    modified_at: datetime
    lines: int


class LogFilesResponse(BaseModel):
    """Log files list response"""
    log_files: List[LogFileInfo]
    total_size_mb: float


# System Information
class SystemInfoResponse(BaseModel):
    """System information response"""
    # Application Info
    app_version: str
    app_build: str
    app_environment: str
    
    # System Info
    os_name: str
    os_version: str
    python_version: str
    node_version: Optional[str] = None
    
    # Hardware Info
    cpu_count: int
    cpu_percent: float
    memory_total_gb: float
    memory_used_gb: float
    memory_percent: float
    disk_total_gb: float
    disk_used_gb: float
    disk_percent: float
    
    # Database Info
    database_type: str
    database_size_mb: float
    database_tables: int
    database_records: int
    
    # Performance Info
    uptime_seconds: int
    requests_total: int
    requests_per_minute: float
    average_response_time_ms: float
    
    # Status
    status: str
    health_checks: Dict[str, bool]
    
    # Timestamps
    server_time: datetime
    last_restart: datetime


class SystemHealthResponse(BaseModel):
    """System health check response"""
    status: str  # "healthy", "degraded", "unhealthy"
    checks: Dict[str, Dict[str, Any]]
    timestamp: datetime


class SystemStatsResponse(BaseModel):
    """System statistics response"""
    users_total: int
    users_active: int
    projects_total: int
    calculations_today: int
    calculations_total: int
    pdfs_generated_today: int
    pdfs_generated_total: int
    storage_used_mb: float
    api_calls_today: int
    errors_today: int


# Combined Settings Response
class AllSettingsResponse(BaseModel):
    """All settings combined response"""
    general: GeneralSettingsResponse
    email: EmailSettingsResponse
    backup: BackupSettingsResponse
    logging: LoggingSettingsResponse
    system_info: SystemInfoResponse

"""
System Settings Service

Business logic for system settings management
"""

import os
import platform
import psutil
import json
import shutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..models.system_settings_schemas import (
    GeneralSettingsUpdate, GeneralSettingsResponse,
    EmailSettingsUpdate, EmailSettingsResponse, EmailTestRequest, EmailTestResponse,
    BackupSettingsUpdate, BackupSettingsResponse, BackupNowRequest, BackupInfo, BackupListResponse,
    LoggingSettingsUpdate, LoggingSettingsResponse, LogFileInfo, LogFilesResponse,
    SystemInfoResponse, SystemHealthResponse, SystemStatsResponse,
    LogLevel, BackupFrequency, EmailProvider
)

logger = logging.getLogger(__name__)


class SystemSettingsService:
    """Service for managing system settings"""
    
    def __init__(self):
        self.settings_dir = Path("config")
        self.settings_dir.mkdir(exist_ok=True)
        self.settings_file = self.settings_dir / "system_settings.json"
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize settings if not exists
        if not self.settings_file.exists():
            self._initialize_default_settings()
    
    def _initialize_default_settings(self):
        """Initialize default settings"""
        default_settings = {
            "general": {
                "app_name": "Solar Calculator Pro",
                "app_description": "Professional Solar and Heat Pump Calculator",
                "default_language": "de-DE",
                "default_currency": "EUR",
                "timezone": "Europe/Berlin",
                "date_format": "DD.MM.YYYY",
                "time_format": "HH:mm",
                "items_per_page": 25,
                "session_timeout": 60,
                "enable_analytics": False,
                "enable_telemetry": False,
                "maintenance_mode": False,
                "updated_at": datetime.now().isoformat()
            },
            "email": {
                "provider": "smtp",
                "smtp_host": "localhost",
                "smtp_port": 587,
                "smtp_username": "",
                "smtp_password": "",
                "smtp_use_tls": True,
                "smtp_use_ssl": False,
                "from_email": "noreply@solarcalculator.local",
                "from_name": "Solar Calculator Pro",
                "reply_to_email": None,
                "api_key": None,
                "api_secret": None,
                "region": None,
                "is_configured": False,
                "last_test_at": None,
                "last_test_success": None,
                "updated_at": datetime.now().isoformat()
            },
            "backup": {
                "enabled": True,
                "frequency": "daily",
                "retention_days": 30,
                "backup_location": str(self.backup_dir),
                "include_database": True,
                "include_files": True,
                "include_logs": False,
                "compress_backups": True,
                "encrypt_backups": False,
                "encryption_key": None,
                "max_backup_size_mb": 1000,
                "notification_email": None,
                "last_backup_at": None,
                "last_backup_success": None,
                "last_backup_size_mb": None,
                "next_backup_at": None,
                "total_backups": 0,
                "updated_at": datetime.now().isoformat()
            },
            "logging": {
                "log_level": "INFO",
                "log_to_file": True,
                "log_to_console": True,
                "log_file_path": str(self.log_dir / "app.log"),
                "max_log_file_size_mb": 100,
                "log_file_retention_days": 30,
                "log_rotation_enabled": True,
                "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "log_api_requests": True,
                "log_database_queries": False,
                "log_errors_only": False,
                "enable_debug_mode": False,
                "current_log_size_mb": 0.0,
                "total_log_files": 0,
                "updated_at": datetime.now().isoformat()
            }
        }
        
        with open(self.settings_file, 'w') as f:
            json.dump(default_settings, f, indent=2)
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        with open(self.settings_file, 'r') as f:
            return json.load(f)
    
    def _save_settings(self, settings: Dict[str, Any]):
        """Save settings to file"""
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
    
    # General Settings
    def get_general_settings(self) -> GeneralSettingsResponse:
        """Get general settings"""
        settings = self._load_settings()
        general = settings["general"]
        return GeneralSettingsResponse(
            **{k: v for k, v in general.items() if k != 'updated_at'},
            updated_at=datetime.fromisoformat(general["updated_at"])
        )
    
    def update_general_settings(self, update: GeneralSettingsUpdate) -> GeneralSettingsResponse:
        """Update general settings"""
        settings = self._load_settings()
        general = settings["general"]
        
        # Update only provided fields
        update_data = update.dict(exclude_unset=True)
        general.update(update_data)
        general["updated_at"] = datetime.now().isoformat()
        
        settings["general"] = general
        self._save_settings(settings)
        
        logger.info(f"General settings updated: {list(update_data.keys())}")
        return self.get_general_settings()
    
    # Email Settings
    def get_email_settings(self) -> EmailSettingsResponse:
        """Get email settings (without sensitive data)"""
        settings = self._load_settings()
        email = settings["email"]
        
        # Don't expose passwords and API keys
        safe_email = {k: v for k, v in email.items() 
                     if k not in ['smtp_password', 'api_key', 'api_secret']}
        
        return EmailSettingsResponse(
            **{k: v for k, v in safe_email.items() if k not in ['updated_at', 'last_test_at']},
            updated_at=datetime.fromisoformat(email["updated_at"]),
            last_test_at=datetime.fromisoformat(email["last_test_at"]) if email.get("last_test_at") else None
        )
    
    def update_email_settings(self, update: EmailSettingsUpdate) -> EmailSettingsResponse:
        """Update email settings"""
        settings = self._load_settings()
        email = settings["email"]
        
        # Update only provided fields
        update_data = update.dict(exclude_unset=True)
        email.update(update_data)
        email["updated_at"] = datetime.now().isoformat()
        email["is_configured"] = bool(email.get("smtp_host") or email.get("api_key"))
        
        settings["email"] = email
        self._save_settings(settings)
        
        logger.info(f"Email settings updated: {list(update_data.keys())}")
        return self.get_email_settings()
    
    def test_email(self, request: EmailTestRequest) -> EmailTestResponse:
        """Test email configuration"""
        settings = self._load_settings()
        email = settings["email"]
        
        try:
            if email["provider"] == "smtp":
                # Test SMTP connection
                msg = MIMEMultipart()
                msg['From'] = f"{email['from_name']} <{email['from_email']}>"
                msg['To'] = request.to_email
                msg['Subject'] = request.subject
                msg.attach(MIMEText(request.body, 'plain'))
                
                if email["smtp_use_ssl"]:
                    server = smtplib.SMTP_SSL(email["smtp_host"], email["smtp_port"])
                else:
                    server = smtplib.SMTP(email["smtp_host"], email["smtp_port"])
                    if email["smtp_use_tls"]:
                        server.starttls()
                
                if email.get("smtp_username") and email.get("smtp_password"):
                    server.login(email["smtp_username"], email["smtp_password"])
                
                server.send_message(msg)
                server.quit()
                
                # Update last test info
                email["last_test_at"] = datetime.now().isoformat()
                email["last_test_success"] = True
                settings["email"] = email
                self._save_settings(settings)
                
                logger.info(f"Test email sent successfully to {request.to_email}")
                return EmailTestResponse(
                    success=True,
                    message="Test email sent successfully",
                    sent_at=datetime.now()
                )
            else:
                return EmailTestResponse(
                    success=False,
                    message=f"Email provider '{email['provider']}' not yet implemented",
                    sent_at=datetime.now()
                )
        
        except Exception as e:
            # Update last test info
            email["last_test_at"] = datetime.now().isoformat()
            email["last_test_success"] = False
            settings["email"] = email
            self._save_settings(settings)
            
            logger.error(f"Failed to send test email: {str(e)}")
            return EmailTestResponse(
                success=False,
                message=f"Failed to send email: {str(e)}",
                sent_at=datetime.now()
            )
    
    # Backup Settings
    def get_backup_settings(self) -> BackupSettingsResponse:
        """Get backup settings"""
        settings = self._load_settings()
        backup = settings["backup"]
        
        # Calculate next backup time
        if backup["enabled"] and backup.get("last_backup_at"):
            last_backup = datetime.fromisoformat(backup["last_backup_at"])
            frequency = backup["frequency"]
            if frequency == "hourly":
                next_backup = last_backup + timedelta(hours=1)
            elif frequency == "daily":
                next_backup = last_backup + timedelta(days=1)
            elif frequency == "weekly":
                next_backup = last_backup + timedelta(weeks=1)
            else:  # monthly
                next_backup = last_backup + timedelta(days=30)
            backup["next_backup_at"] = next_backup.isoformat()
        
        return BackupSettingsResponse(
            **{k: v for k, v in backup.items() if k not in ['updated_at', 'last_backup_at', 'next_backup_at', 'encryption_key']},
            updated_at=datetime.fromisoformat(backup["updated_at"]),
            last_backup_at=datetime.fromisoformat(backup["last_backup_at"]) if backup.get("last_backup_at") else None,
            next_backup_at=datetime.fromisoformat(backup["next_backup_at"]) if backup.get("next_backup_at") else None
        )
    
    def update_backup_settings(self, update: BackupSettingsUpdate) -> BackupSettingsResponse:
        """Update backup settings"""
        settings = self._load_settings()
        backup = settings["backup"]
        
        # Update only provided fields
        update_data = update.dict(exclude_unset=True)
        backup.update(update_data)
        backup["updated_at"] = datetime.now().isoformat()
        
        settings["backup"] = backup
        self._save_settings(settings)
        
        logger.info(f"Backup settings updated: {list(update_data.keys())}")
        return self.get_backup_settings()
    
    def create_backup(self, request: BackupNowRequest) -> BackupInfo:
        """Create a manual backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        total_size = 0
        
        try:
            # Backup database
            if request.include_database:
                db_path = Path("product_database.db")
                if db_path.exists():
                    shutil.copy2(db_path, backup_path / "database.db")
                    total_size += db_path.stat().st_size
            
            # Backup files
            if request.include_files:
                files_to_backup = ["config", "uploads"]
                for folder in files_to_backup:
                    folder_path = Path(folder)
                    if folder_path.exists():
                        shutil.copytree(folder_path, backup_path / folder, dirs_exist_ok=True)
                        total_size += sum(f.stat().st_size for f in folder_path.rglob('*') if f.is_file())
            
            # Backup logs
            if request.include_logs:
                if self.log_dir.exists():
                    shutil.copytree(self.log_dir, backup_path / "logs", dirs_exist_ok=True)
                    total_size += sum(f.stat().st_size for f in self.log_dir.rglob('*') if f.is_file())
            
            # Compress if needed
            settings = self._load_settings()
            if settings["backup"]["compress_backups"]:
                shutil.make_archive(str(backup_path), 'zip', backup_path)
                shutil.rmtree(backup_path)
                backup_file = f"{backup_name}.zip"
                total_size = (self.backup_dir / backup_file).stat().st_size
            else:
                backup_file = backup_name
            
            # Update backup settings
            backup_settings = settings["backup"]
            backup_settings["last_backup_at"] = datetime.now().isoformat()
            backup_settings["last_backup_success"] = True
            backup_settings["last_backup_size_mb"] = total_size / (1024 * 1024)
            backup_settings["total_backups"] = backup_settings.get("total_backups", 0) + 1
            settings["backup"] = backup_settings
            self._save_settings(settings)
            
            logger.info(f"Backup created successfully: {backup_file}")
            
            return BackupInfo(
                id=backup_settings["total_backups"],
                filename=backup_file,
                created_at=datetime.now(),
                size_mb=total_size / (1024 * 1024),
                description=request.description,
                includes_database=request.include_database,
                includes_files=request.include_files,
                includes_logs=request.include_logs,
                is_compressed=settings["backup"]["compress_backups"],
                is_encrypted=settings["backup"]["encrypt_backups"]
            )
        
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            raise
    
    def list_backups(self) -> BackupListResponse:
        """List all backups"""
        backups = []
        total_size = 0
        
        for backup_file in self.backup_dir.iterdir():
            if backup_file.is_file() or backup_file.is_dir():
                size = backup_file.stat().st_size if backup_file.is_file() else sum(
                    f.stat().st_size for f in backup_file.rglob('*') if f.is_file()
                )
                size_mb = size / (1024 * 1024)
                total_size += size_mb
                
                backups.append(BackupInfo(
                    id=len(backups) + 1,
                    filename=backup_file.name,
                    created_at=datetime.fromtimestamp(backup_file.stat().st_ctime),
                    size_mb=size_mb,
                    description=None,
                    includes_database=True,
                    includes_files=True,
                    includes_logs=False,
                    is_compressed=backup_file.suffix == '.zip',
                    is_encrypted=False
                ))
        
        backups.sort(key=lambda x: x.created_at, reverse=True)
        
        return BackupListResponse(
            backups=backups,
            total=len(backups),
            total_size_mb=total_size
        )
    
    # Logging Settings
    def get_logging_settings(self) -> LoggingSettingsResponse:
        """Get logging settings"""
        settings = self._load_settings()
        logging_settings = settings["logging"]
        
        # Calculate current log size
        log_file = Path(logging_settings["log_file_path"])
        current_size = log_file.stat().st_size / (1024 * 1024) if log_file.exists() else 0
        
        # Count log files
        log_files = list(self.log_dir.glob("*.log*"))
        
        logging_settings["current_log_size_mb"] = current_size
        logging_settings["total_log_files"] = len(log_files)
        
        return LoggingSettingsResponse(
            **{k: v for k, v in logging_settings.items() if k != 'updated_at'},
            updated_at=datetime.fromisoformat(logging_settings["updated_at"])
        )
    
    def update_logging_settings(self, update: LoggingSettingsUpdate) -> LoggingSettingsResponse:
        """Update logging settings"""
        settings = self._load_settings()
        logging_settings = settings["logging"]
        
        # Update only provided fields
        update_data = update.dict(exclude_unset=True)
        logging_settings.update(update_data)
        logging_settings["updated_at"] = datetime.now().isoformat()
        
        settings["logging"] = logging_settings
        self._save_settings(settings)
        
        # Apply logging configuration
        if "log_level" in update_data:
            logging.getLogger().setLevel(getattr(logging, update_data["log_level"]))
        
        logger.info(f"Logging settings updated: {list(update_data.keys())}")
        return self.get_logging_settings()
    
    def list_log_files(self) -> LogFilesResponse:
        """List all log files"""
        log_files = []
        total_size = 0
        
        for log_file in self.log_dir.glob("*.log*"):
            if log_file.is_file():
                size_mb = log_file.stat().st_size / (1024 * 1024)
                total_size += size_mb
                
                # Count lines
                try:
                    with open(log_file, 'r') as f:
                        lines = sum(1 for _ in f)
                except:
                    lines = 0
                
                log_files.append(LogFileInfo(
                    filename=log_file.name,
                    size_mb=size_mb,
                    created_at=datetime.fromtimestamp(log_file.stat().st_ctime),
                    modified_at=datetime.fromtimestamp(log_file.stat().st_mtime),
                    lines=lines
                ))
        
        log_files.sort(key=lambda x: x.modified_at, reverse=True)
        
        return LogFilesResponse(
            log_files=log_files,
            total_size_mb=total_size
        )
    
    # System Information
    def get_system_info(self) -> SystemInfoResponse:
        """Get system information"""
        import sys
        
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Database info
        db_path = Path("product_database.db")
        db_size = db_path.stat().st_size / (1024 * 1024) if db_path.exists() else 0
        
        # Uptime
        boot_time = psutil.boot_time()
        uptime = int(datetime.now().timestamp() - boot_time)
        
        return SystemInfoResponse(
            # Application Info
            app_version="1.0.0",
            app_build="20240101",
            app_environment=os.getenv("ENVIRONMENT", "production"),
            
            # System Info
            os_name=platform.system(),
            os_version=platform.version(),
            python_version=sys.version.split()[0],
            node_version=None,
            
            # Hardware Info
            cpu_count=psutil.cpu_count(),
            cpu_percent=cpu_percent,
            memory_total_gb=memory.total / (1024**3),
            memory_used_gb=memory.used / (1024**3),
            memory_percent=memory.percent,
            disk_total_gb=disk.total / (1024**3),
            disk_used_gb=disk.used / (1024**3),
            disk_percent=disk.percent,
            
            # Database Info
            database_type="SQLite",
            database_size_mb=db_size,
            database_tables=0,
            database_records=0,
            
            # Performance Info
            uptime_seconds=uptime,
            requests_total=0,
            requests_per_minute=0.0,
            average_response_time_ms=0.0,
            
            # Status
            status="healthy",
            health_checks={
                "database": True,
                "filesystem": True,
                "memory": memory.percent < 90,
                "disk": disk.percent < 90
            },
            
            # Timestamps
            server_time=datetime.now(),
            last_restart=datetime.fromtimestamp(boot_time)
        )
    
    def get_system_health(self) -> SystemHealthResponse:
        """Get system health status"""
        checks = {}
        
        # Database check
        db_path = Path("product_database.db")
        checks["database"] = {
            "status": "healthy" if db_path.exists() else "unhealthy",
            "message": "Database accessible" if db_path.exists() else "Database not found"
        }
        
        # Filesystem check
        disk = psutil.disk_usage('/')
        checks["filesystem"] = {
            "status": "healthy" if disk.percent < 90 else "degraded",
            "message": f"Disk usage: {disk.percent}%"
        }
        
        # Memory check
        memory = psutil.virtual_memory()
        checks["memory"] = {
            "status": "healthy" if memory.percent < 90 else "degraded",
            "message": f"Memory usage: {memory.percent}%"
        }
        
        # Determine overall status
        statuses = [check["status"] for check in checks.values()]
        if all(s == "healthy" for s in statuses):
            overall_status = "healthy"
        elif any(s == "unhealthy" for s in statuses):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"
        
        return SystemHealthResponse(
            status=overall_status,
            checks=checks,
            timestamp=datetime.now()
        )
    
    def get_system_stats(self) -> SystemStatsResponse:
        """Get system statistics"""
        # This would normally query the database
        # For now, return mock data
        return SystemStatsResponse(
            users_total=10,
            users_active=5,
            projects_total=50,
            calculations_today=25,
            calculations_total=500,
            pdfs_generated_today=10,
            pdfs_generated_total=200,
            storage_used_mb=150.5,
            api_calls_today=1000,
            errors_today=5
        )

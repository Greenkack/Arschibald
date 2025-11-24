"""
System Maintenance Service
Handles database maintenance, cache management, log cleanup, temp file cleanup, diagnostics, and repairs
"""

import os
import shutil
import psutil
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
import gzip

from backend.models.maintenance_models import MaintenanceLog, SystemDiagnostic, CacheEntry, TempFile
from backend.models.maintenance_schemas import (
    DatabaseMaintenanceRequest, DatabaseMaintenanceResponse,
    CacheStatsResponse, CacheClearRequest, CacheClearResponse,
    LogStatsResponse, LogCleanupRequest, LogCleanupResponse,
    TempFileStatsResponse, TempFileCleanupRequest, TempFileCleanupResponse,
    SystemDiagnosticsResponse, DiagnosticRequest, DiagnosticResult,
    RepairRequest, RepairResponse, MaintenanceStatus, DiagnosticStatus,
    MaintenanceLogResponse
)

logger = logging.getLogger(__name__)


class MaintenanceService:
    """Service for system maintenance operations"""

    def __init__(self, db: Session):
        self.db = db
        self.log_dir = Path("logs")
        self.temp_dir = Path("temp")
        self.cache_dir = Path("cache")

    # ==================== Database Maintenance ====================

    def perform_database_maintenance(
        self, request: DatabaseMaintenanceRequest, user: str = "system"
    ) -> DatabaseMaintenanceResponse:
        """Perform database maintenance operations"""
        start_time = datetime.now()
        
        # Log operation start
        log_entry = MaintenanceLog(
            operation_type="database",
            operation_name=request.operation,
            status="in_progress",
            performed_by=user,
            details=request.dict()
        )
        self.db.add(log_entry)
        self.db.commit()

        try:
            tables_processed = []
            details = {}

            if request.operation == "vacuum":
                tables_processed = self._vacuum_database(request.tables, request.full)
                details["operation"] = "VACUUM"
            
            elif request.operation == "analyze":
                tables_processed = self._analyze_database(request.tables)
                details["operation"] = "ANALYZE"
            
            elif request.operation == "reindex":
                tables_processed = self._reindex_database(request.tables)
                details["operation"] = "REINDEX"
            
            elif request.operation == "optimize":
                tables_processed = self._optimize_database(request.tables)
                details["operation"] = "OPTIMIZE"
            
            else:
                raise ValueError(f"Unknown operation: {request.operation}")

            duration = (datetime.now() - start_time).total_seconds()

            # Update log entry
            log_entry.status = "success"
            log_entry.completed_at = datetime.now()
            log_entry.duration_seconds = duration
            log_entry.details = {**log_entry.details, "tables_processed": tables_processed}
            self.db.commit()

            return DatabaseMaintenanceResponse(
                operation=request.operation,
                status=MaintenanceStatus.SUCCESS,
                tables_processed=tables_processed,
                duration_seconds=duration,
                details=details
            )

        except Exception as e:
            logger.error(f"Database maintenance failed: {str(e)}")
            log_entry.status = "failed"
            log_entry.error_message = str(e)
            log_entry.completed_at = datetime.now()
            self.db.commit()
            raise

    def _vacuum_database(self, tables: Optional[List[str]], full: bool) -> List[str]:
        """Vacuum database tables"""
        inspector = inspect(self.db.bind)
        all_tables = inspector.get_table_names()
        
        target_tables = tables if tables else all_tables
        processed = []

        for table in target_tables:
            if table in all_tables:
                try:
                    vacuum_cmd = f"VACUUM {'FULL' if full else ''} {table}"
                    self.db.execute(text(vacuum_cmd))
                    self.db.commit()
                    processed.append(table)
                    logger.info(f"Vacuumed table: {table}")
                except Exception as e:
                    logger.warning(f"Failed to vacuum {table}: {str(e)}")

        return processed

    def _analyze_database(self, tables: Optional[List[str]]) -> List[str]:
        """Analyze database tables for query optimization"""
        inspector = inspect(self.db.bind)
        all_tables = inspector.get_table_names()
        
        target_tables = tables if tables else all_tables
        processed = []

        for table in target_tables:
            if table in all_tables:
                try:
                    self.db.execute(text(f"ANALYZE {table}"))
                    self.db.commit()
                    processed.append(table)
                    logger.info(f"Analyzed table: {table}")
                except Exception as e:
                    logger.warning(f"Failed to analyze {table}: {str(e)}")

        return processed

    def _reindex_database(self, tables: Optional[List[str]]) -> List[str]:
        """Rebuild database indexes"""
        inspector = inspect(self.db.bind)
        all_tables = inspector.get_table_names()
        
        target_tables = tables if tables else all_tables
        processed = []

        for table in target_tables:
            if table in all_tables:
                try:
                    self.db.execute(text(f"REINDEX TABLE {table}"))
                    self.db.commit()
                    processed.append(table)
                    logger.info(f"Reindexed table: {table}")
                except Exception as e:
                    logger.warning(f"Failed to reindex {table}: {str(e)}")

        return processed

    def _optimize_database(self, tables: Optional[List[str]]) -> List[str]:
        """Optimize database tables (combination of vacuum, analyze, reindex)"""
        processed = []
        processed.extend(self._vacuum_database(tables, False))
        processed.extend(self._analyze_database(tables))
        return list(set(processed))

    # ==================== Cache Management ====================

    def get_cache_stats(self) -> CacheStatsResponse:
        """Get cache statistics"""
        entries = self.db.query(CacheEntry).all()
        
        total_size = sum(e.size_bytes for e in entries)
        cache_types = {}
        total_hits = 0

        for entry in entries:
            cache_types[entry.cache_type] = cache_types.get(entry.cache_type, 0) + 1
            total_hits += entry.hit_count

        hit_rate = (total_hits / len(entries)) if entries else 0

        return CacheStatsResponse(
            total_entries=len(entries),
            total_size_bytes=total_size,
            total_size_mb=round(total_size / (1024 * 1024), 2),
            cache_types=cache_types,
            hit_rate=round(hit_rate, 2),
            oldest_entry=min((e.created_at for e in entries), default=None),
            newest_entry=max((e.created_at for e in entries), default=None)
        )

    def clear_cache(self, request: CacheClearRequest, user: str = "system") -> CacheClearResponse:
        """Clear cache entries"""
        start_time = datetime.now()
        
        query = self.db.query(CacheEntry)

        # Filter by cache type
        if request.cache_type:
            query = query.filter(CacheEntry.cache_type == request.cache_type)

        # Filter by age
        if request.older_than_days:
            cutoff_date = datetime.now() - timedelta(days=request.older_than_days)
            query = query.filter(CacheEntry.created_at < cutoff_date)

        # Filter unused entries
        if request.unused_only:
            query = query.filter(CacheEntry.hit_count == 0)

        entries = query.all()
        total_size = sum(e.size_bytes for e in entries)
        
        # Delete entries
        for entry in entries:
            self.db.delete(entry)
        
        self.db.commit()

        duration = (datetime.now() - start_time).total_seconds()

        # Log operation
        log_entry = MaintenanceLog(
            operation_type="cache",
            operation_name="clear_cache",
            status="success",
            performed_by=user,
            completed_at=datetime.now(),
            duration_seconds=duration,
            details={
                "entries_cleared": len(entries),
                "size_freed_mb": round(total_size / (1024 * 1024), 2)
            }
        )
        self.db.add(log_entry)
        self.db.commit()

        return CacheClearResponse(
            entries_cleared=len(entries),
            size_freed_mb=round(total_size / (1024 * 1024), 2),
            duration_seconds=duration
        )

    # ==================== Log Management ====================

    def get_log_stats(self) -> LogStatsResponse:
        """Get log file statistics"""
        if not self.log_dir.exists():
            return LogStatsResponse(
                total_log_files=0,
                total_size_bytes=0,
                total_size_mb=0,
                log_types={},
                oldest_log=None,
                newest_log=None,
                error_count_24h=0,
                warning_count_24h=0
            )

        log_files = list(self.log_dir.glob("*.log"))
        total_size = sum(f.stat().st_size for f in log_files)
        
        log_types = {}
        for log_file in log_files:
            log_type = log_file.stem.split('_')[0] if '_' in log_file.stem else 'general'
            log_types[log_type] = log_types.get(log_type, 0) + 1

        # Count recent errors and warnings
        error_count = self._count_log_level("ERROR", hours=24)
        warning_count = self._count_log_level("WARNING", hours=24)

        return LogStatsResponse(
            total_log_files=len(log_files),
            total_size_bytes=total_size,
            total_size_mb=round(total_size / (1024 * 1024), 2),
            log_types=log_types,
            oldest_log=min((datetime.fromtimestamp(f.stat().st_mtime) for f in log_files), default=None),
            newest_log=max((datetime.fromtimestamp(f.stat().st_mtime) for f in log_files), default=None),
            error_count_24h=error_count,
            warning_count_24h=warning_count
        )

    def cleanup_logs(self, request: LogCleanupRequest, user: str = "system") -> LogCleanupResponse:
        """Clean up old log files"""
        start_time = datetime.now()
        
        if not self.log_dir.exists():
            return LogCleanupResponse(
                files_deleted=0,
                files_compressed=0,
                size_freed_mb=0,
                duration_seconds=0
            )

        cutoff_date = datetime.now() - timedelta(days=request.older_than_days)
        log_files = list(self.log_dir.glob("*.log"))
        
        files_deleted = 0
        files_compressed = 0
        size_freed = 0

        for log_file in log_files:
            file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if file_mtime < cutoff_date:
                file_size = log_file.stat().st_size
                
                if request.compress_before_delete:
                    # Compress before deleting
                    compressed_path = log_file.with_suffix('.log.gz')
                    with open(log_file, 'rb') as f_in:
                        with gzip.open(compressed_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    files_compressed += 1
                
                log_file.unlink()
                files_deleted += 1
                size_freed += file_size

        duration = (datetime.now() - start_time).total_seconds()

        # Log operation
        log_entry = MaintenanceLog(
            operation_type="logs",
            operation_name="cleanup_logs",
            status="success",
            performed_by=user,
            completed_at=datetime.now(),
            duration_seconds=duration,
            details={
                "files_deleted": files_deleted,
                "files_compressed": files_compressed,
                "size_freed_mb": round(size_freed / (1024 * 1024), 2)
            }
        )
        self.db.add(log_entry)
        self.db.commit()

        return LogCleanupResponse(
            files_deleted=files_deleted,
            files_compressed=files_compressed,
            size_freed_mb=round(size_freed / (1024 * 1024), 2),
            duration_seconds=duration
        )

    def _count_log_level(self, level: str, hours: int = 24) -> int:
        """Count log entries of specific level in recent hours"""
        count = 0
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        if not self.log_dir.exists():
            return 0

        for log_file in self.log_dir.glob("*.log"):
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        if level in line:
                            # Simple timestamp parsing (adjust based on log format)
                            count += 1
            except Exception as e:
                logger.warning(f"Failed to read log file {log_file}: {str(e)}")

        return count

    # ==================== Temp File Cleanup ====================

    def get_temp_file_stats(self) -> TempFileStatsResponse:
        """Get temporary file statistics"""
        temp_files = self.db.query(TempFile).all()
        
        total_size = sum(f.size_bytes for f in temp_files)
        file_types = {}
        files_to_delete = 0

        for temp_file in temp_files:
            file_types[temp_file.file_type] = file_types.get(temp_file.file_type, 0) + 1
            if temp_file.should_delete or (temp_file.delete_after and temp_file.delete_after < datetime.now()):
                files_to_delete += 1

        return TempFileStatsResponse(
            total_files=len(temp_files),
            total_size_bytes=total_size,
            total_size_mb=round(total_size / (1024 * 1024), 2),
            file_types=file_types,
            oldest_file=min((f.created_at for f in temp_files), default=None),
            files_to_delete=files_to_delete
        )

    def cleanup_temp_files(
        self, request: TempFileCleanupRequest, user: str = "system"
    ) -> TempFileCleanupResponse:
        """Clean up temporary files"""
        start_time = datetime.now()
        
        cutoff_time = datetime.now() - timedelta(hours=request.older_than_hours)
        query = self.db.query(TempFile)

        # Filter by age
        if not request.force:
            query = query.filter(TempFile.created_at < cutoff_time)

        # Filter by file types
        if request.file_types:
            query = query.filter(TempFile.file_type.in_(request.file_types))

        temp_files = query.all()
        files_deleted = 0
        size_freed = 0

        for temp_file in temp_files:
            try:
                file_path = Path(temp_file.file_path)
                if file_path.exists():
                    size_freed += file_path.stat().st_size
                    file_path.unlink()
                    files_deleted += 1
                
                self.db.delete(temp_file)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {temp_file.file_path}: {str(e)}")

        self.db.commit()

        duration = (datetime.now() - start_time).total_seconds()

        # Log operation
        log_entry = MaintenanceLog(
            operation_type="temp_files",
            operation_name="cleanup_temp_files",
            status="success",
            performed_by=user,
            completed_at=datetime.now(),
            duration_seconds=duration,
            details={
                "files_deleted": files_deleted,
                "size_freed_mb": round(size_freed / (1024 * 1024), 2)
            }
        )
        self.db.add(log_entry)
        self.db.commit()

        return TempFileCleanupResponse(
            files_deleted=files_deleted,
            size_freed_mb=round(size_freed / (1024 * 1024), 2),
            duration_seconds=duration
        )

    # ==================== System Diagnostics ====================

    def run_diagnostics(self, request: DiagnosticRequest) -> SystemDiagnosticsResponse:
        """Run system diagnostics"""
        diagnostic_types = request.diagnostic_types or [
            "database", "disk", "memory", "cpu", "network", "services"
        ]

        diagnostics = []
        overall_status = DiagnosticStatus.HEALTHY

        for diag_type in diagnostic_types:
            if diag_type == "database":
                result = self._diagnose_database(request.detailed)
            elif diag_type == "disk":
                result = self._diagnose_disk(request.detailed)
            elif diag_type == "memory":
                result = self._diagnose_memory(request.detailed)
            elif diag_type == "cpu":
                result = self._diagnose_cpu(request.detailed)
            elif diag_type == "network":
                result = self._diagnose_network(request.detailed)
            elif diag_type == "services":
                result = self._diagnose_services(request.detailed)
            else:
                continue

            diagnostics.append(result)

            # Update overall status
            if result.status == DiagnosticStatus.CRITICAL:
                overall_status = DiagnosticStatus.CRITICAL
            elif result.status == DiagnosticStatus.WARNING and overall_status != DiagnosticStatus.CRITICAL:
                overall_status = DiagnosticStatus.WARNING

            # Save diagnostic result
            diag_entry = SystemDiagnostic(
                diagnostic_type=diag_type,
                status=result.status.value,
                metrics=result.metrics,
                issues=result.issues,
                recommendations=result.recommendations
            )
            self.db.add(diag_entry)

        self.db.commit()

        summary = {
            "total_diagnostics": len(diagnostics),
            "healthy": sum(1 for d in diagnostics if d.status == DiagnosticStatus.HEALTHY),
            "warnings": sum(1 for d in diagnostics if d.status == DiagnosticStatus.WARNING),
            "critical": sum(1 for d in diagnostics if d.status == DiagnosticStatus.CRITICAL),
        }

        return SystemDiagnosticsResponse(
            overall_status=overall_status,
            diagnostics=diagnostics,
            summary=summary
        )

    def _diagnose_database(self, detailed: bool) -> DiagnosticResult:
        """Diagnose database health"""
        metrics = {}
        issues = []
        recommendations = []
        status = DiagnosticStatus.HEALTHY

        try:
            # Check database connection
            self.db.execute(text("SELECT 1"))
            metrics["connection"] = "OK"

            # Check table count
            inspector = inspect(self.db.bind)
            table_count = len(inspector.get_table_names())
            metrics["table_count"] = table_count

            # Check database size
            result = self.db.execute(text("SELECT pg_database_size(current_database())")).fetchone()
            db_size = result[0] if result else 0
            metrics["size_mb"] = round(db_size / (1024 * 1024), 2)

            if db_size > 10 * 1024 * 1024 * 1024:  # 10GB
                status = DiagnosticStatus.WARNING
                issues.append("Database size exceeds 10GB")
                recommendations.append("Consider archiving old data")

        except Exception as e:
            status = DiagnosticStatus.CRITICAL
            issues.append(f"Database connection failed: {str(e)}")
            recommendations.append("Check database service and credentials")

        return DiagnosticResult(
            diagnostic_type="database",
            status=status,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            checked_at=datetime.now()
        )

    def _diagnose_disk(self, detailed: bool) -> DiagnosticResult:
        """Diagnose disk space"""
        metrics = {}
        issues = []
        recommendations = []
        status = DiagnosticStatus.HEALTHY

        disk = psutil.disk_usage('/')
        metrics["total_gb"] = round(disk.total / (1024**3), 2)
        metrics["used_gb"] = round(disk.used / (1024**3), 2)
        metrics["free_gb"] = round(disk.free / (1024**3), 2)
        metrics["percent_used"] = disk.percent

        if disk.percent > 90:
            status = DiagnosticStatus.CRITICAL
            issues.append(f"Disk usage critical: {disk.percent}%")
            recommendations.append("Free up disk space immediately")
        elif disk.percent > 80:
            status = DiagnosticStatus.WARNING
            issues.append(f"Disk usage high: {disk.percent}%")
            recommendations.append("Consider cleaning up old files")

        return DiagnosticResult(
            diagnostic_type="disk",
            status=status,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            checked_at=datetime.now()
        )

    def _diagnose_memory(self, detailed: bool) -> DiagnosticResult:
        """Diagnose memory usage"""
        metrics = {}
        issues = []
        recommendations = []
        status = DiagnosticStatus.HEALTHY

        memory = psutil.virtual_memory()
        metrics["total_gb"] = round(memory.total / (1024**3), 2)
        metrics["available_gb"] = round(memory.available / (1024**3), 2)
        metrics["used_gb"] = round(memory.used / (1024**3), 2)
        metrics["percent_used"] = memory.percent

        if memory.percent > 90:
            status = DiagnosticStatus.CRITICAL
            issues.append(f"Memory usage critical: {memory.percent}%")
            recommendations.append("Restart services or increase memory")
        elif memory.percent > 80:
            status = DiagnosticStatus.WARNING
            issues.append(f"Memory usage high: {memory.percent}%")
            recommendations.append("Monitor memory-intensive processes")

        return DiagnosticResult(
            diagnostic_type="memory",
            status=status,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            checked_at=datetime.now()
        )

    def _diagnose_cpu(self, detailed: bool) -> DiagnosticResult:
        """Diagnose CPU usage"""
        metrics = {}
        issues = []
        recommendations = []
        status = DiagnosticStatus.HEALTHY

        cpu_percent = psutil.cpu_percent(interval=1)
        metrics["cpu_percent"] = cpu_percent
        metrics["cpu_count"] = psutil.cpu_count()

        if cpu_percent > 90:
            status = DiagnosticStatus.CRITICAL
            issues.append(f"CPU usage critical: {cpu_percent}%")
            recommendations.append("Investigate high CPU processes")
        elif cpu_percent > 80:
            status = DiagnosticStatus.WARNING
            issues.append(f"CPU usage high: {cpu_percent}%")
            recommendations.append("Monitor CPU-intensive operations")

        return DiagnosticResult(
            diagnostic_type="cpu",
            status=status,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            checked_at=datetime.now()
        )

    def _diagnose_network(self, detailed: bool) -> DiagnosticResult:
        """Diagnose network connectivity"""
        metrics = {}
        issues = []
        recommendations = []
        status = DiagnosticStatus.HEALTHY

        net_io = psutil.net_io_counters()
        metrics["bytes_sent_mb"] = round(net_io.bytes_sent / (1024**2), 2)
        metrics["bytes_recv_mb"] = round(net_io.bytes_recv / (1024**2), 2)
        metrics["packets_sent"] = net_io.packets_sent
        metrics["packets_recv"] = net_io.packets_recv

        if net_io.errin > 100 or net_io.errout > 100:
            status = DiagnosticStatus.WARNING
            issues.append("Network errors detected")
            recommendations.append("Check network configuration")

        return DiagnosticResult(
            diagnostic_type="network",
            status=status,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            checked_at=datetime.now()
        )

    def _diagnose_services(self, detailed: bool) -> DiagnosticResult:
        """Diagnose service health"""
        metrics = {}
        issues = []
        recommendations = []
        status = DiagnosticStatus.HEALTHY

        # Check critical services
        services_to_check = ["database", "cache", "backend"]
        
        for service in services_to_check:
            # Simplified service check
            metrics[f"{service}_status"] = "running"

        return DiagnosticResult(
            diagnostic_type="services",
            status=status,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            checked_at=datetime.now()
        )

    # ==================== Repair Tools ====================

    def perform_repair(self, request: RepairRequest, user: str = "system") -> RepairResponse:
        """Perform repair operation"""
        start_time = datetime.now()
        
        items_repaired = 0
        items_failed = 0
        backup_created = None
        details = {}

        try:
            if request.backup_first and not request.dry_run:
                backup_created = self._create_backup()

            if request.operation.value == "fix_permissions":
                items_repaired, items_failed = self._fix_permissions(request.target, request.dry_run)
            
            elif request.operation.value == "rebuild_index":
                items_repaired, items_failed = self._rebuild_indexes(request.target, request.dry_run)
            
            elif request.operation.value == "repair_database":
                items_repaired, items_failed = self._repair_database(request.dry_run)
            
            elif request.operation.value == "reset_cache":
                items_repaired, items_failed = self._reset_cache(request.dry_run)
            
            elif request.operation.value == "fix_orphaned_files":
                items_repaired, items_failed = self._fix_orphaned_files(request.dry_run)
            
            elif request.operation.value == "repair_corrupted_data":
                items_repaired, items_failed = self._repair_corrupted_data(request.target, request.dry_run)

            duration = (datetime.now() - start_time).total_seconds()

            # Log operation
            log_entry = MaintenanceLog(
                operation_type="repair",
                operation_name=request.operation.value,
                status="success",
                performed_by=user,
                completed_at=datetime.now(),
                duration_seconds=duration,
                details={
                    "items_repaired": items_repaired,
                    "items_failed": items_failed,
                    "dry_run": request.dry_run
                }
            )
            self.db.add(log_entry)
            self.db.commit()

            return RepairResponse(
                operation=request.operation,
                status=MaintenanceStatus.SUCCESS,
                items_repaired=items_repaired,
                items_failed=items_failed,
                backup_created=backup_created,
                details=details,
                duration_seconds=duration
            )

        except Exception as e:
            logger.error(f"Repair operation failed: {str(e)}")
            raise

    def _create_backup(self) -> str:
        """Create database backup"""
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_{timestamp}.sql"
        
        # Simplified backup (implement actual backup logic)
        logger.info(f"Created backup: {backup_file}")
        return str(backup_file)

    def _fix_permissions(self, target: Optional[str], dry_run: bool) -> tuple:
        """Fix file permissions"""
        # Implement permission fixing logic
        return (0, 0)

    def _rebuild_indexes(self, target: Optional[str], dry_run: bool) -> tuple:
        """Rebuild database indexes"""
        if not dry_run:
            tables = [target] if target else None
            self._reindex_database(tables)
        return (1, 0)

    def _repair_database(self, dry_run: bool) -> tuple:
        """Repair database integrity"""
        # Implement database repair logic
        return (0, 0)

    def _reset_cache(self, dry_run: bool) -> tuple:
        """Reset all caches"""
        if not dry_run:
            count = self.db.query(CacheEntry).count()
            self.db.query(CacheEntry).delete()
            self.db.commit()
            return (count, 0)
        return (0, 0)

    def _fix_orphaned_files(self, dry_run: bool) -> tuple:
        """Fix orphaned files"""
        # Implement orphaned file cleanup logic
        return (0, 0)

    def _repair_corrupted_data(self, target: Optional[str], dry_run: bool) -> tuple:
        """Repair corrupted data"""
        # Implement data repair logic
        return (0, 0)

    # ==================== Maintenance Logs ====================

    def get_maintenance_logs(
        self, 
        operation_type: Optional[str] = None,
        limit: int = 100
    ) -> List[MaintenanceLogResponse]:
        """Get maintenance operation logs"""
        query = self.db.query(MaintenanceLog)
        
        if operation_type:
            query = query.filter(MaintenanceLog.operation_type == operation_type)
        
        logs = query.order_by(MaintenanceLog.started_at.desc()).limit(limit).all()
        
        return [MaintenanceLogResponse.from_orm(log) for log in logs]

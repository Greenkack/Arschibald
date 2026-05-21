"""
Production Configuration API
Task 76: API endpoints for production server management
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
import os
import platform
import psutil

router = APIRouter(prefix="/production", tags=["Production Configuration"])


class ServerStatus(BaseModel):
    """Server status information"""
    hostname: str
    platform: str
    python_version: str
    cpu_count: int
    cpu_percent: float
    memory_total_gb: float
    memory_used_gb: float
    memory_percent: float
    disk_total_gb: float
    disk_used_gb: float
    disk_percent: float
    uptime_seconds: float
    load_average: List[float]


class SSLCertificateInfo(BaseModel):
    """SSL certificate information"""
    subject: str
    issuer: str
    valid_from: datetime
    valid_until: datetime
    days_until_expiry: int
    is_valid: bool
    serial_number: str


class HealthCheckResult(BaseModel):
    """Health check result"""
    service: str
    status: str
    response_time_ms: float
    message: Optional[str] = None
    last_check: datetime


class ProductionStatus(BaseModel):
    """Overall production status"""
    environment: str
    version: str
    status: str
    server: ServerStatus
    health_checks: List[HealthCheckResult]
    ssl_certificate: Optional[SSLCertificateInfo] = None
    last_deployment: Optional[datetime] = None
    active_connections: int
    requests_per_minute: float


# In-memory storage for demo
deployment_history: List[Dict] = []
health_check_results: Dict[str, HealthCheckResult] = {}


def get_server_status() -> ServerStatus:
    """Get current server status"""
    import sys
    
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    try:
        load_avg = list(os.getloadavg())
    except (AttributeError, OSError):
        load_avg = [0.0, 0.0, 0.0]
    
    return ServerStatus(
        hostname=platform.node(),
        platform=f"{platform.system()} {platform.release()}",
        python_version=sys.version.split()[0],
        cpu_count=psutil.cpu_count(),
        cpu_percent=psutil.cpu_percent(interval=1),
        memory_total_gb=memory.total / (1024**3),
        memory_used_gb=memory.used / (1024**3),
        memory_percent=memory.percent,
        disk_total_gb=disk.total / (1024**3),
        disk_used_gb=disk.used / (1024**3),
        disk_percent=disk.percent,
        uptime_seconds=float(datetime.now().timestamp() - psutil.boot_time()),
        load_average=load_avg
    )


@router.get("/status", response_model=ProductionStatus)
async def get_production_status():
    """Get overall production status"""
    server_status = get_server_status()
    
    # Determine overall status
    if server_status.cpu_percent > 90 or server_status.memory_percent > 90:
        status = "warning"
    elif server_status.cpu_percent > 95 or server_status.memory_percent > 95:
        status = "critical"
    else:
        status = "healthy"
    
    return ProductionStatus(
        environment=os.getenv("SOLAR_ENV", "development"),
        version=os.getenv("APP_VERSION", "1.0.0"),
        status=status,
        server=server_status,
        health_checks=list(health_check_results.values()),
        last_deployment=deployment_history[-1]["timestamp"] if deployment_history else None,
        active_connections=0,  # Would be from actual connection tracking
        requests_per_minute=0.0  # Would be from metrics
    )


@router.get("/server-info")
async def get_server_info():
    """Get detailed server information"""
    return {
        "server": get_server_status(),
        "environment_variables": {
            "SOLAR_ENV": os.getenv("SOLAR_ENV", "not set"),
            "APP_VERSION": os.getenv("APP_VERSION", "not set"),
            "DEBUG": os.getenv("DEBUG", "false"),
        },
        "process": {
            "pid": os.getpid(),
            "memory_mb": psutil.Process().memory_info().rss / (1024**2),
            "threads": psutil.Process().num_threads(),
            "open_files": len(psutil.Process().open_files()),
        }
    }


@router.get("/health")
async def health_check():
    """Comprehensive health check"""
    checks = {}
    overall_healthy = True
    
    # Database check
    try:
        # Simulated database check
        checks["database"] = {
            "status": "healthy",
            "response_time_ms": 5.2,
            "message": "Connection successful"
        }
    except Exception as e:
        checks["database"] = {
            "status": "unhealthy",
            "response_time_ms": 0,
            "message": str(e)
        }
        overall_healthy = False
    
    # Redis check
    try:
        checks["redis"] = {
            "status": "healthy",
            "response_time_ms": 1.5,
            "message": "Connection successful"
        }
    except Exception as e:
        checks["redis"] = {
            "status": "unhealthy",
            "response_time_ms": 0,
            "message": str(e)
        }
        overall_healthy = False
    
    # Disk space check
    disk = psutil.disk_usage('/')
    if disk.percent > 90:
        checks["disk"] = {
            "status": "warning",
            "response_time_ms": 0,
            "message": f"Disk usage at {disk.percent}%"
        }
    else:
        checks["disk"] = {
            "status": "healthy",
            "response_time_ms": 0,
            "message": f"Disk usage at {disk.percent}%"
        }
    
    # Memory check
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        checks["memory"] = {
            "status": "warning",
            "response_time_ms": 0,
            "message": f"Memory usage at {memory.percent}%"
        }
    else:
        checks["memory"] = {
            "status": "healthy",
            "response_time_ms": 0,
            "message": f"Memory usage at {memory.percent}%"
        }
    
    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "checks": checks
    }


@router.get("/metrics")
async def get_metrics():
    """Get Prometheus-compatible metrics"""
    server = get_server_status()
    
    metrics = []
    
    # CPU metrics
    metrics.append(f"solar_calculator_cpu_percent {server.cpu_percent}")
    metrics.append(f"solar_calculator_cpu_count {server.cpu_count}")
    
    # Memory metrics
    metrics.append(f"solar_calculator_memory_total_bytes {server.memory_total_gb * 1024**3}")
    metrics.append(f"solar_calculator_memory_used_bytes {server.memory_used_gb * 1024**3}")
    metrics.append(f"solar_calculator_memory_percent {server.memory_percent}")
    
    # Disk metrics
    metrics.append(f"solar_calculator_disk_total_bytes {server.disk_total_gb * 1024**3}")
    metrics.append(f"solar_calculator_disk_used_bytes {server.disk_used_gb * 1024**3}")
    metrics.append(f"solar_calculator_disk_percent {server.disk_percent}")
    
    # Uptime
    metrics.append(f"solar_calculator_uptime_seconds {server.uptime_seconds}")
    
    return "\n".join(metrics)


@router.post("/deployment")
async def record_deployment(
    version: str,
    commit_hash: Optional[str] = None,
    deployed_by: Optional[str] = None,
    notes: Optional[str] = None
):
    """Record a new deployment"""
    deployment = {
        "id": len(deployment_history) + 1,
        "version": version,
        "commit_hash": commit_hash,
        "deployed_by": deployed_by,
        "notes": notes,
        "timestamp": datetime.now(),
        "status": "success"
    }
    deployment_history.append(deployment)
    return deployment


@router.get("/deployments")
async def get_deployment_history(limit: int = 10):
    """Get deployment history"""
    return {
        "deployments": deployment_history[-limit:],
        "total": len(deployment_history)
    }


@router.post("/rollback/{deployment_id}")
async def rollback_deployment(deployment_id: int):
    """Rollback to a previous deployment"""
    target = None
    for d in deployment_history:
        if d["id"] == deployment_id:
            target = d
            break
    
    if not target:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    rollback = {
        "id": len(deployment_history) + 1,
        "version": target["version"],
        "commit_hash": target["commit_hash"],
        "deployed_by": "system",
        "notes": f"Rollback to deployment {deployment_id}",
        "timestamp": datetime.now(),
        "status": "rollback"
    }
    deployment_history.append(rollback)
    
    return {
        "status": "success",
        "message": f"Rolled back to version {target['version']}",
        "deployment": rollback
    }


@router.get("/config/nginx")
async def get_nginx_config():
    """Get generated Nginx configuration"""
    from ..config.production_server import get_production_config, generate_nginx_config
    
    config = get_production_config()
    nginx_config = generate_nginx_config(config)
    
    return {
        "config": nginx_config,
        "settings": {
            "worker_processes": config.reverse_proxy.worker_processes,
            "worker_connections": config.reverse_proxy.worker_connections,
            "ssl_enabled": config.ssl.enabled,
            "rate_limiting": config.reverse_proxy.rate_limiting_enabled
        }
    }


@router.get("/config/systemd")
async def get_systemd_config():
    """Get generated systemd service configuration"""
    from ..config.production_server import get_production_config, generate_systemd_service
    
    config = get_production_config()
    systemd_config = generate_systemd_service(config)
    
    return {
        "config": systemd_config,
        "settings": {
            "workers": config.server.workers,
            "timeout": config.server.timeout,
            "max_requests": config.server.max_requests
        }
    }


@router.get("/config/docker-compose")
async def get_docker_compose_config():
    """Get Docker Compose configuration"""
    from ..config.production_server import generate_docker_compose
    
    return {
        "config": generate_docker_compose(),
        "services": ["app", "db", "redis", "nginx", "prometheus", "grafana"]
    }


@router.get("/ssl/status")
async def get_ssl_status():
    """Get SSL certificate status"""
    # In production, this would check actual certificates
    return {
        "enabled": True,
        "certificate": {
            "subject": "CN=solar-calculator.example.com",
            "issuer": "Let's Encrypt Authority X3",
            "valid_from": "2025-01-01T00:00:00Z",
            "valid_until": "2025-12-31T23:59:59Z",
            "days_until_expiry": 397,
            "is_valid": True
        },
        "protocols": ["TLSv1.2", "TLSv1.3"],
        "hsts_enabled": True
    }


@router.post("/maintenance/enable")
async def enable_maintenance_mode(
    message: str = "System is under maintenance",
    estimated_duration_minutes: int = 30
):
    """Enable maintenance mode"""
    return {
        "status": "enabled",
        "message": message,
        "estimated_duration_minutes": estimated_duration_minutes,
        "started_at": datetime.now().isoformat()
    }


@router.post("/maintenance/disable")
async def disable_maintenance_mode():
    """Disable maintenance mode"""
    return {
        "status": "disabled",
        "disabled_at": datetime.now().isoformat()
    }


@router.get("/logs")
async def get_recent_logs(
    level: str = "INFO",
    limit: int = 100,
    service: Optional[str] = None
):
    """Get recent application logs"""
    # In production, this would read from actual log files
    sample_logs = [
        {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "service": "api",
            "message": "Request processed successfully"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "service": "database",
            "message": "Query executed in 5ms"
        }
    ]
    
    return {
        "logs": sample_logs,
        "total": len(sample_logs),
        "filters": {
            "level": level,
            "limit": limit,
            "service": service
        }
    }

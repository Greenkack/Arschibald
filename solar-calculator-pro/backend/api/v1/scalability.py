"""
Scalability Improvements System
Task 85: Horizontal scaling, resource optimization, load balancing, capacity monitoring
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid

router = APIRouter(prefix="/scalability", tags=["Scalability"])


class ScalingPolicy(str, Enum):
    MANUAL = "manual"
    AUTO_CPU = "auto_cpu"
    AUTO_MEMORY = "auto_memory"
    AUTO_REQUESTS = "auto_requests"
    SCHEDULED = "scheduled"


class InstanceStatus(str, Enum):
    RUNNING = "running"
    STARTING = "starting"
    STOPPING = "stopping"
    STOPPED = "stopped"
    UNHEALTHY = "unhealthy"


class ServiceType(str, Enum):
    API = "api"
    WORKER = "worker"
    SCHEDULER = "scheduler"
    CACHE = "cache"
    DATABASE = "database"


class Instance(BaseModel):
    """Service instance"""
    id: str
    service: ServiceType
    status: InstanceStatus
    host: str
    port: int
    cpu_percent: float
    memory_percent: float
    requests_per_second: float
    started_at: datetime
    health_check_url: str


class ScalingRule(BaseModel):
    """Auto-scaling rule"""
    id: str
    service: ServiceType
    policy: ScalingPolicy
    min_instances: int
    max_instances: int
    scale_up_threshold: float
    scale_down_threshold: float
    cooldown_seconds: int
    enabled: bool = True


class CapacityPlan(BaseModel):
    """Capacity planning"""
    id: str
    name: str
    target_users: int
    target_requests_per_second: int
    recommended_api_instances: int
    recommended_worker_instances: int
    recommended_cache_size_gb: int
    recommended_db_connections: int
    estimated_cost_monthly: float


# In-memory storage
instances: List[Instance] = []
scaling_rules: List[ScalingRule] = []
capacity_plans: List[CapacityPlan] = []
scaling_events: List[Dict] = []

# Initialize default instances
default_instances = [
    Instance(
        id="api-1",
        service=ServiceType.API,
        status=InstanceStatus.RUNNING,
        host="10.0.1.1",
        port=8000,
        cpu_percent=45.0,
        memory_percent=60.0,
        requests_per_second=100,
        started_at=datetime.now() - timedelta(hours=24),
        health_check_url="http://10.0.1.1:8000/health"
    ),
    Instance(
        id="api-2",
        service=ServiceType.API,
        status=InstanceStatus.RUNNING,
        host="10.0.1.2",
        port=8000,
        cpu_percent=50.0,
        memory_percent=55.0,
        requests_per_second=95,
        started_at=datetime.now() - timedelta(hours=24),
        health_check_url="http://10.0.1.2:8000/health"
    ),
    Instance(
        id="worker-1",
        service=ServiceType.WORKER,
        status=InstanceStatus.RUNNING,
        host="10.0.2.1",
        port=8001,
        cpu_percent=70.0,
        memory_percent=65.0,
        requests_per_second=0,
        started_at=datetime.now() - timedelta(hours=24),
        health_check_url="http://10.0.2.1:8001/health"
    )
]
instances.extend(default_instances)

# Initialize default scaling rules
default_rules = [
    ScalingRule(
        id="api-autoscale",
        service=ServiceType.API,
        policy=ScalingPolicy.AUTO_CPU,
        min_instances=2,
        max_instances=10,
        scale_up_threshold=70.0,
        scale_down_threshold=30.0,
        cooldown_seconds=300
    ),
    ScalingRule(
        id="worker-autoscale",
        service=ServiceType.WORKER,
        policy=ScalingPolicy.AUTO_MEMORY,
        min_instances=1,
        max_instances=5,
        scale_up_threshold=80.0,
        scale_down_threshold=40.0,
        cooldown_seconds=300
    )
]
scaling_rules.extend(default_rules)


# ============================================
# Instance Management
# ============================================

@router.get("/instances", response_model=List[Instance])
async def get_instances(service: Optional[ServiceType] = None):
    """Get all instances"""
    if service:
        return [i for i in instances if i.service == service]
    return instances


@router.get("/instances/{instance_id}", response_model=Instance)
async def get_instance(instance_id: str):
    """Get instance details"""
    for instance in instances:
        if instance.id == instance_id:
            return instance
    raise HTTPException(status_code=404, detail="Instance not found")


@router.post("/instances/scale-up")
async def scale_up(service: ServiceType, count: int = 1):
    """Scale up service instances"""
    new_instances = []
    for i in range(count):
        instance = Instance(
            id=f"{service.value}-{uuid.uuid4().hex[:6]}",
            service=service,
            status=InstanceStatus.STARTING,
            host=f"10.0.{len(instances)+1}.{i+1}",
            port=8000,
            cpu_percent=0,
            memory_percent=0,
            requests_per_second=0,
            started_at=datetime.now(),
            health_check_url=f"http://10.0.{len(instances)+1}.{i+1}:8000/health"
        )
        instances.append(instance)
        new_instances.append(instance)
        
        # Simulate startup
        instance.status = InstanceStatus.RUNNING
    
    scaling_events.append({
        "type": "scale_up",
        "service": service.value,
        "count": count,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "status": "success",
        "instances_created": count,
        "new_instances": [i.dict() for i in new_instances]
    }


@router.post("/instances/scale-down")
async def scale_down(service: ServiceType, count: int = 1):
    """Scale down service instances"""
    global instances
    service_instances = [i for i in instances if i.service == service and i.status == InstanceStatus.RUNNING]
    
    if len(service_instances) <= count:
        raise HTTPException(status_code=400, detail="Cannot scale down below minimum instances")
    
    removed = []
    for i in range(min(count, len(service_instances))):
        instance = service_instances[-(i+1)]
        instance.status = InstanceStatus.STOPPED
        removed.append(instance.id)
    
    instances = [i for i in instances if i.id not in removed]
    
    scaling_events.append({
        "type": "scale_down",
        "service": service.value,
        "count": count,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "status": "success",
        "instances_removed": count,
        "removed_ids": removed
    }


# ============================================
# Auto-Scaling Rules
# ============================================

@router.get("/scaling-rules", response_model=List[ScalingRule])
async def get_scaling_rules():
    """Get auto-scaling rules"""
    return scaling_rules


@router.post("/scaling-rules", response_model=ScalingRule)
async def create_scaling_rule(rule: ScalingRule):
    """Create auto-scaling rule"""
    rule.id = f"rule-{uuid.uuid4().hex[:6]}"
    scaling_rules.append(rule)
    return rule


@router.put("/scaling-rules/{rule_id}")
async def update_scaling_rule(
    rule_id: str,
    min_instances: Optional[int] = None,
    max_instances: Optional[int] = None,
    scale_up_threshold: Optional[float] = None,
    scale_down_threshold: Optional[float] = None,
    enabled: Optional[bool] = None
):
    """Update auto-scaling rule"""
    for rule in scaling_rules:
        if rule.id == rule_id:
            if min_instances is not None:
                rule.min_instances = min_instances
            if max_instances is not None:
                rule.max_instances = max_instances
            if scale_up_threshold is not None:
                rule.scale_up_threshold = scale_up_threshold
            if scale_down_threshold is not None:
                rule.scale_down_threshold = scale_down_threshold
            if enabled is not None:
                rule.enabled = enabled
            return rule
    raise HTTPException(status_code=404, detail="Rule not found")


@router.delete("/scaling-rules/{rule_id}")
async def delete_scaling_rule(rule_id: str):
    """Delete auto-scaling rule"""
    global scaling_rules
    scaling_rules = [r for r in scaling_rules if r.id != rule_id]
    return {"status": "deleted", "rule_id": rule_id}


# ============================================
# Resource Optimization
# ============================================

@router.get("/resources/usage")
async def get_resource_usage():
    """Get resource usage across all instances"""
    api_instances = [i for i in instances if i.service == ServiceType.API]
    worker_instances = [i for i in instances if i.service == ServiceType.WORKER]
    
    return {
        "timestamp": datetime.now().isoformat(),
        "api": {
            "instances": len(api_instances),
            "avg_cpu_percent": sum(i.cpu_percent for i in api_instances) / len(api_instances) if api_instances else 0,
            "avg_memory_percent": sum(i.memory_percent for i in api_instances) / len(api_instances) if api_instances else 0,
            "total_rps": sum(i.requests_per_second for i in api_instances)
        },
        "worker": {
            "instances": len(worker_instances),
            "avg_cpu_percent": sum(i.cpu_percent for i in worker_instances) / len(worker_instances) if worker_instances else 0,
            "avg_memory_percent": sum(i.memory_percent for i in worker_instances) / len(worker_instances) if worker_instances else 0
        },
        "database": {
            "connections_used": 45,
            "connections_max": 100,
            "cpu_percent": 35,
            "memory_percent": 60,
            "disk_percent": 45
        },
        "cache": {
            "memory_used_mb": 512,
            "memory_max_mb": 1024,
            "connections": 50,
            "hit_rate": 0.92
        }
    }


@router.get("/resources/recommendations")
async def get_resource_recommendations():
    """Get resource optimization recommendations"""
    return {
        "recommendations": [
            {
                "category": "compute",
                "recommendation": "Consider scaling down API instances during off-peak hours",
                "current": "4 instances",
                "suggested": "2 instances (off-peak)",
                "savings": "50% compute cost during off-peak"
            },
            {
                "category": "database",
                "recommendation": "Increase connection pool size",
                "current": "100 connections",
                "suggested": "150 connections",
                "reason": "Connection pool utilization at 90%"
            },
            {
                "category": "cache",
                "recommendation": "Increase cache memory",
                "current": "1 GB",
                "suggested": "2 GB",
                "reason": "High eviction rate detected"
            },
            {
                "category": "storage",
                "recommendation": "Enable compression for old data",
                "current": "No compression",
                "suggested": "Enable zstd compression",
                "savings": "40% storage reduction"
            }
        ]
    }


# ============================================
# Capacity Planning
# ============================================

@router.get("/capacity/current")
async def get_current_capacity():
    """Get current capacity metrics"""
    return {
        "timestamp": datetime.now().isoformat(),
        "current_load": {
            "active_users": 150,
            "requests_per_second": 250,
            "concurrent_connections": 500
        },
        "capacity": {
            "max_users": 500,
            "max_rps": 1000,
            "max_connections": 2000
        },
        "utilization": {
            "users_percent": 30,
            "rps_percent": 25,
            "connections_percent": 25
        },
        "headroom": {
            "users": 350,
            "rps": 750,
            "connections": 1500
        }
    }


@router.post("/capacity/plan")
async def create_capacity_plan(
    target_users: int,
    target_rps: int,
    growth_percent: float = 20
):
    """Create capacity plan"""
    # Calculate requirements with growth buffer
    buffer = 1 + (growth_percent / 100)
    
    plan = CapacityPlan(
        id=f"plan-{uuid.uuid4().hex[:6]}",
        name=f"Capacity Plan for {target_users} users",
        target_users=target_users,
        target_requests_per_second=target_rps,
        recommended_api_instances=max(2, int((target_rps / 200) * buffer)),
        recommended_worker_instances=max(1, int((target_users / 500) * buffer)),
        recommended_cache_size_gb=max(1, int((target_users / 100) * buffer)),
        recommended_db_connections=max(50, int((target_rps / 10) * buffer)),
        estimated_cost_monthly=target_users * 0.5 + target_rps * 0.1
    )
    capacity_plans.append(plan)
    
    return plan


@router.get("/capacity/plans", response_model=List[CapacityPlan])
async def get_capacity_plans():
    """Get capacity plans"""
    return capacity_plans


# ============================================
# Scaling Events and History
# ============================================

@router.get("/events")
async def get_scaling_events(limit: int = 50):
    """Get scaling events history"""
    return {
        "events": scaling_events[-limit:],
        "total": len(scaling_events)
    }


@router.get("/status")
async def get_scalability_status():
    """Get overall scalability status"""
    api_instances = [i for i in instances if i.service == ServiceType.API and i.status == InstanceStatus.RUNNING]
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": {
                "instances": len(api_instances),
                "status": "healthy",
                "auto_scaling": "enabled"
            },
            "worker": {
                "instances": len([i for i in instances if i.service == ServiceType.WORKER]),
                "status": "healthy",
                "auto_scaling": "enabled"
            }
        },
        "scaling_rules_active": len([r for r in scaling_rules if r.enabled]),
        "recent_events": scaling_events[-5:],
        "capacity_utilization": 30
    }

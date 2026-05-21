"""
Load Balancing System
Task 191: Request distribution, health checks, failover, and session affinity
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import hashlib
import random


router = APIRouter(prefix="/loadbalancer", tags=["Load Balancing"])


class ServerStatus(str, Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"
    OFFLINE = "offline"


class LoadBalancingStrategy(str, Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    IP_HASH = "ip_hash"
    RANDOM = "random"


class BackendServer(BaseModel):
    id: str
    host: str
    port: int
    weight: int = 1
    status: ServerStatus = ServerStatus.HEALTHY
    active_connections: int = 0
    total_requests: int = 0
    failed_requests: int = 0
    last_health_check: Optional[datetime] = None
    response_time_ms: float = 0


class HealthCheckConfig(BaseModel):
    interval_seconds: int = 30
    timeout_seconds: int = 5
    unhealthy_threshold: int = 3
    healthy_threshold: int = 2
    path: str = "/health"


class LoadBalancer:
    def __init__(self):
        self.servers: Dict[str, BackendServer] = {}
        self.strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
        self.current_index: int = 0
        self.health_config = HealthCheckConfig()
        self.session_map: Dict[str, str] = {}  # session_id -> server_id
        
    def add_server(self, server: BackendServer):
        self.servers[server.id] = server
        
    def remove_server(self, server_id: str):
        if server_id in self.servers:
            del self.servers[server_id]
            
    def get_healthy_servers(self) -> List[BackendServer]:
        return [s for s in self.servers.values() if s.status == ServerStatus.HEALTHY]
        
    def select_server(self, client_ip: str = None, session_id: str = None) -> Optional[BackendServer]:
        # Check session affinity first
        if session_id and session_id in self.session_map:
            server_id = self.session_map[session_id]
            if server_id in self.servers and self.servers[server_id].status == ServerStatus.HEALTHY:
                return self.servers[server_id]
                
        healthy = self.get_healthy_servers()
        if not healthy:
            return None
            
        server = None
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            server = healthy[self.current_index % len(healthy)]
            self.current_index += 1
        elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            server = min(healthy, key=lambda s: s.active_connections)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED:
            total_weight = sum(s.weight for s in healthy)
            r = random.randint(1, total_weight)
            for s in healthy:
                r -= s.weight
                if r <= 0:
                    server = s
                    break
        elif self.strategy == LoadBalancingStrategy.IP_HASH and client_ip:
            idx = int(hashlib.md5(client_ip.encode()).hexdigest(), 16) % len(healthy)
            server = healthy[idx]
        else:
            server = random.choice(healthy)
            
        if server and session_id:
            self.session_map[session_id] = server.id
        return server
        
    def record_request(self, server_id: str, success: bool, response_time_ms: float):
        if server_id in self.servers:
            server = self.servers[server_id]
            server.total_requests += 1
            if not success:
                server.failed_requests += 1
            server.response_time_ms = (server.response_time_ms * 0.9) + (response_time_ms * 0.1)
            
    async def health_check(self, server: BackendServer) -> bool:
        # Simulated health check
        server.last_health_check = datetime.now()
        return server.status != ServerStatus.OFFLINE
        
    def get_stats(self) -> Dict:
        healthy = len(self.get_healthy_servers())
        total = len(self.servers)
        return {
            "total_servers": total,
            "healthy_servers": healthy,
            "strategy": self.strategy.value,
            "active_sessions": len(self.session_map),
            "servers": [{"id": s.id, "status": s.status.value, "connections": s.active_connections,
                        "requests": s.total_requests, "errors": s.failed_requests} for s in self.servers.values()]
        }


# Global load balancer
lb = LoadBalancer()

# Add default servers
lb.add_server(BackendServer(id="server1", host="localhost", port=8001, weight=2))
lb.add_server(BackendServer(id="server2", host="localhost", port=8002, weight=1))
lb.add_server(BackendServer(id="server3", host="localhost", port=8003, weight=1))


@router.get("/servers")
async def list_servers():
    return {"servers": list(lb.servers.values())}


@router.post("/servers")
async def add_server(server: BackendServer):
    lb.add_server(server)
    return {"status": "added", "server": server}


@router.delete("/servers/{server_id}")
async def remove_server(server_id: str):
    lb.remove_server(server_id)
    return {"status": "removed"}


@router.put("/servers/{server_id}/status")
async def update_server_status(server_id: str, status: ServerStatus):
    if server_id not in lb.servers:
        raise HTTPException(status_code=404, detail="Server not found")
    lb.servers[server_id].status = status
    return {"status": "updated"}


@router.get("/select")
async def select_server(client_ip: Optional[str] = None, session_id: Optional[str] = None):
    server = lb.select_server(client_ip, session_id)
    if not server:
        raise HTTPException(status_code=503, detail="No healthy servers available")
    return {"server": server}


@router.put("/strategy")
async def set_strategy(strategy: LoadBalancingStrategy):
    lb.strategy = strategy
    return {"status": "updated", "strategy": strategy.value}


@router.get("/stats")
async def get_stats():
    return lb.get_stats()


@router.get("/health")
async def health_check():
    healthy = lb.get_healthy_servers()
    return {"status": "healthy" if healthy else "unhealthy", "healthy_count": len(healthy), "total_count": len(lb.servers)}


@router.post("/health-check/run")
async def run_health_checks():
    results = {}
    for server in lb.servers.values():
        results[server.id] = await lb.health_check(server)
    return {"results": results}
